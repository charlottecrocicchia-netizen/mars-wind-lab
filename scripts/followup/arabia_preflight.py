"""Run declared Arabia Terra geometry and support checks, without magnetic outcomes.

Usage: python scripts/followup/arabia_preflight.py
Only existing authorized atlas/boundary inputs and the saved attributed USGS
outline are used. No network request or magnetic-field evaluation is made.
"""
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy
import pyshtools
import shapely
from shapely.geometry import shape
from scipy.spatial.distance import cdist
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'arabia-preflight-v1'
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from marswind.agetransfer import epoch_features
from marswind.spatial_matching import (unit_vectors, polyline_distance_km,
    caliper_match, block_labels, pair_block_components, standardized_balance)

OUT = ROOT/'research/followup/arabia'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe(value):
    if isinstance(value, dict): return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)): return [safe(v) for v in value]
    if isinstance(value, (float, np.floating)): return float(value) if np.isfinite(value) else None
    if isinstance(value, (bool, np.bool_)): return bool(value)
    if isinstance(value, np.integer): return int(value)
    return value


def save(name, value):
    (OUT/name).write_text(json.dumps(safe(value), indent=2, allow_nan=False)+'\n')


def write_csv(name, rows, fields=None):
    with (OUT/name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(safe(rows))


def inputs(protocol):
    for file_key, hash_key in [('atlas_file', 'atlas_sha256'), ('boundary_file', 'boundary_sha256')]:
        assert sha(ROOT/protocol[file_key]) == protocol[hash_key], f'Changed declared input: {file_key}'
    assert sha(OUT/protocol['polygon_file']) == protocol['polygon_sha256']
    atlas = json.loads((ROOT/protocol['atlas_file']).read_text())
    # Deliberately discard all magnetic values before any extraction or selection.
    atlas.pop('magnetic_nT', None)
    lat, lon = np.asarray(atlas['latitude']), np.asarray(atlas['longitude'])
    la, lo = np.meshgrid(lat, lon, indexing='ij')
    grid = np.asarray(atlas['geology']['grid'])
    valid = (np.abs(la) <= 75) & (grid >= 0)
    boundary = np.loadtxt(ROOT/protocol['boundary_file'])
    mask = pyshtools.backends.shtools.Curve2Mask(180, boundary[:, [1, 0]], 0, sampling=2, extend=True)
    south = mask[np.ix_((90-lat).astype(int), lon.astype(int))].astype(bool)[valid]
    la, lo = la[valid], lo[valid]
    signed_lon = (lo+180) % 360-180
    polygon = shape(json.loads((OUT/protocol['polygon_file']).read_text())['geometry'])
    assert len(polygon.geoms) == 1
    ring = np.asarray(polygon.geoms[0].exterior.coords)
    inside = shapely.contains_xy(polygon, signed_lon, la)
    boundary_distance = polyline_distance_km(la, lo, boundary, protocol['radius_km'])
    edge_distance = polyline_distance_km(la, lo, ring, protocol['radius_km'])
    units = {u['Unit']: u for u in atlas['geology']['units']}
    codes = np.array([atlas['geology']['codes'][i] for i in grid[valid]])
    features = [epoch_features(c) for c in codes]
    ranks = np.array([r['rank'] for r in features])
    pure_noachian = np.array([r['noachian'] == 1 and r['mixed'] == 0 for r in features])
    weights = np.cos(np.deg2rad(la))
    p = protocol['eligibility']
    common = (pure_noachian & south & (la >= p['latitude_bounds_deg'][0]) &
              (la <= p['latitude_bounds_deg'][1]) & (boundary_distance <= p['maximum_boundary_distance_km']))
    treatment = common & inside
    control = common & ~inside & (edge_distance >= p['control_polygon_guard_km'])
    elevation = np.asarray(atlas['topography_km'], float)[valid]
    thickness = {int(k): np.asarray(v, float)[valid] for k, v in atlas['crust_km'].items()}
    assert np.all(np.isfinite(elevation)) and all(np.all(np.isfinite(h)) for h in thickness.values())
    row, column = np.where(valid)
    cell_ids = np.array([f'r{r:02d}c{c:03d}' for r, c in zip(row, column)])
    cells = []
    for i, identifier in enumerate(cell_ids):
        cells.append({'cell_id': identifier, 'latitude_deg': la[i], 'longitude_east_deg': lo[i],
            'unit': codes[i], 'epoch_rank': ranks[i], 'unit_group': units[codes[i]]['UnitGroup'],
            'south_of_boundary': south[i], 'inside_arabia_footprint': inside[i],
            'boundary_distance_km': boundary_distance[i], 'arabia_edge_distance_km': edge_distance[i],
            'elevation_km': elevation[i], **{f'thickness_{k}_km': h[i] for k, h in thickness.items()},
            'candidate_arabia': treatment[i], 'candidate_control': control[i]})
    north_early = ~south & (ranks == 1)
    assert north_early.sum() == protocol['northern_cell_reproduction']['expected_count']
    write_csv('northern_early_noachian_cells.csv', [c for c, keep in zip(cells, north_early) if keep])
    write_csv('covariates_and_masks.csv', cells)
    # A finer mask changes geometric sampling only; no covariates are interpolated.
    glat, glon = np.arange(-89.75, 90, .5), np.arange(-179.75, 180, .5)
    gy, gx = np.meshgrid(glat, glon, indexing='ij')
    geometry_mask = shapely.contains_xy(polygon, gx, gy)
    np.savez_compressed(OUT/'geometry_mask_0p5.npz', latitude_deg=glat, longitude_deg=glon, named_footprint=geometry_mask)
    return dict(cells=cells, ids=cell_ids, la=la, lo=lo, ranks=ranks, weights=weights,
        inside=inside, north_early=north_early, south=south, boundary=boundary, ring=ring,
        boundary_distance=boundary_distance, treatment=treatment, control=control,
        elevation=elevation, thickness=thickness, topography=np.asarray(atlas['topography_km']),
        latitude=lat, longitude=lon, geometry_mask_count=int(geometry_mask.sum()))


def block_diagnostics(data, ti, ci, protocol, setting):
    rows, allocations = [], []
    if not len(ti): return rows, allocations
    radius = protocol['radius_km']
    points = unit_vectors(np.r_[data['la'][ti], data['la'][ci]], np.r_[data['lo'][ti], data['lo'][ci]])
    distances = 2*radius*np.arcsin(np.clip(cdist(points, points)/2, 0, 1))
    for size in protocol['blocks']['nominal_sizes_km']:
        for offset in protocol['blocks']['grid_offsets_fraction']:
            a = block_labels(data['la'][ti], data['lo'][ti], size, offset, radius)
            b = block_labels(data['la'][ci], data['lo'][ci], size, offset, radius)
            components = pair_block_components(a, b)
            labels, counts = np.unique(components, return_counts=True)
            memberships = np.r_[components, components]
            cross = memberships[:, None] != memberships[None, :]
            minimum = float(np.min(distances[cross])) if cross.any() else None
            enough = len(labels) >= protocol['blocks']['minimum_components_screen']
            separated = minimum is not None and minimum >= protocol['blocks']['minimum_between_component_distance_km_screen']
            rows.append({'setting': setting, 'nominal_block_km': size, 'offset_fraction': offset,
                'pairs': len(ti), 'target_blocks': len(set(a)), 'control_blocks': len(set(b)),
                'pair_graph_components': len(labels), 'largest_component_pairs': int(max(counts)),
                'minimum_between_component_distance_km': minimum,
                'component_count_screen_pass': enough, 'separation_screen_pass': separated,
                'geometry_screen_pass': enough and separated, 'exchangeability_established': False})
            for t, c, ba, bb, component in zip(ti, ci, a, b, components):
                allocations.append({'setting': setting, 'nominal_block_km': size, 'offset_fraction': offset,
                    'target_id': data['ids'][t], 'control_id': data['ids'][c],
                    'target_block': ba, 'control_block': bb, 'component': component})
    return rows, allocations


def match_all(data, protocol):
    t, c = np.where(data['treatment'])[0], np.where(data['control'])[0]
    assert len(t) and len(c), 'Empty declared comparison pool; do not change the mask to force matches'
    match_rows, pairs, blocks, allocations = [], [], [], []
    primary_pair = None
    feature_names = list(protocol['matching']['primary_calipers'])
    wa, wb = data['weights'][t], data['weights'][c]
    for density in protocol['matching']['density_scenarios_kg_m3']:
        features = np.column_stack([data['elevation'], data['thickness'][density], data['boundary_distance'], data['la']])
        a, b = features[t], features[c]
        for multiplier in protocol['matching']['sensitivity_caliper_multipliers']:
            scales = np.array(list(protocol['matching']['primary_calipers'].values()))*multiplier
            ia, ib, cost = caliper_match(a, b, data['ranks'][t], data['ranks'][c], scales)
            pre, post = standardized_balance(a, b, wa, wb, ia, ib)
            setting = f'rho{density}_caliper{multiplier:g}'
            coverage = float(wa[ia].sum()/wa.sum())
            balance = float(np.max(np.abs(post))) if len(ia) else None
            match_rows.append({'setting': setting, 'density_kg_m3': density, 'caliper_multiplier': multiplier,
                'target_candidates': len(t), 'control_candidates': len(c), 'matched_pairs': len(ia),
                'target_area_fraction_matched': coverage, 'maximum_absolute_post_smd': balance,
                'coverage_gate_pass': coverage >= protocol['decision_gates']['minimum_target_coverage_fraction'],
                'balance_gate_pass': balance is not None and balance <= protocol['decision_gates']['maximum_absolute_standardized_mean_difference'],
                **{f'{name}_smd_before': v for name, v in zip(feature_names, pre)},
                **{f'{name}_smd_after': v for name, v in zip(feature_names, post)}})
            ti, ci = t[ia], c[ib]
            if density == protocol['matching']['primary_density_kg_m3'] and multiplier == 1:
                primary_pair = (ti, ci)
            for ai, bi, value in zip(ti, ci, cost):
                pairs.append({'setting': setting, 'target_id': data['ids'][ai], 'control_id': data['ids'][bi],
                    'epoch_rank': data['ranks'][ai], 'squared_scaled_cost': value,
                    **{f'{name}_difference': v for name, v in zip(feature_names, features[ai]-features[bi])},
                    'pair_target_area_weight': data['weights'][ai]})
            diagnostic, allocation = block_diagnostics(data, ti, ci, protocol, setting)
            blocks.extend(diagnostic); allocations.extend(allocation)
    write_csv('matching_diagnostics.csv', match_rows)
    write_csv('matched_pairs.csv', pairs, ['setting', 'target_id', 'control_id', 'epoch_rank', 'squared_scaled_cost',
        *[f'{name}_difference' for name in feature_names], 'pair_target_area_weight'])
    write_csv('block_diagnostics.csv', blocks)
    write_csv('pair_block_allocations.csv', allocations)
    return match_rows, blocks, primary_pair


def figures(data, pair):
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), layout='constrained')
    la, lo = data['la'], (data['lo']+180) % 360-180
    boundary = data['boundary'].copy(); boundary[:, 0] = (boundary[:, 0]+180) % 360-180
    breaks = np.where(np.abs(np.diff(boundary[:, 0])) > 180)[0]+1
    for ax in axes:
        for j, part in enumerate(np.split(boundary, breaks)):
            ax.plot(part[:, 0], part[:, 1], color='#526475', lw=1, label='Dichotomy boundary' if j == 0 else None)
        ax.plot(data['ring'][:, 0], data['ring'][:, 1], color='#077f8c', lw=1.5, label='Approximate Arabia footprint')
        sel = data['north_early']
        ax.scatter(lo[sel], la[sel], color='#c35427', marker='*', s=70, edgecolor='white', linewidth=.3, label='Early Noachian cells north of boundary', zorder=5)
        ax.set_xlabel('East longitude (°)'); ax.set_ylabel('Planetocentric latitude (°)')
        ax.grid(alpha=.18)
    axes[0].set(xlim=(-180, 180), ylim=(-30, 75), title='Where are the 23 Early Noachian cells north of the boundary?')
    axes[0].legend(loc='lower right', fontsize=8)
    axes[1].set(xlim=(-50, 80), ylim=(-25, 60), title='Declared footprint and near-boundary comparison pools · no magnetic field shown')
    for mask, color, label in [(data['treatment'], '#118983', 'Eligible Arabia cells'), (data['control'], '#647bba', 'Eligible controls')]:
        axes[1].scatter(lo[mask], la[mask], s=10, c=color, alpha=.6, label=label)
    ti, ci = pair
    axes[1].scatter(lo[ti], la[ti], s=28, facecolors='none', edgecolors='#123d3b', linewidth=.6, label='Matched Arabia cells, primary setting')
    axes[1].legend(loc='lower right', fontsize=8)
    fig.savefig(OUT/'geometry.png', dpi=180)
    fig.savefig(OUT/'geometry.svg', metadata={'Date': None})
    plt.close(fig)


def report(data, match_rows, blocks, protocol):
    primary = next(r for r in match_rows if r['density_kg_m3'] == 2900 and r['caliper_multiplier'] == 1)
    pb = [r for r in blocks if r['setting'] == primary['setting']]
    north = data['north_early']
    summary = {'status': 'Preflight completed; observed-field test not run',
        'outcomes_used': False, 'inference': 'No magnetic contrast, p-value or verdict on archive mechanisms.',
        'northern_early_noachian': {'cells': int(north.sum()), 'inside_declared_arabia': int((north & data['inside']).sum()),
            'distance_to_boundary_min_median_max_km': np.quantile(data['boundary_distance'][north], [0, .5, 1]),
            'near_boundary_counts': {str(d): int(np.sum(data['boundary_distance'][north] <= d)) for d in protocol['northern_cell_reproduction']['near_boundary_bands_km']}},
        'native_covariate_grid_deg': 2, 'geometry_only_mask_grid_deg': .5,
        'geometry_mask_samples': data['geometry_mask_count'], 'primary_matching': primary,
        'primary_block_diagnostics': pb, 'all_matching_settings': match_rows,
        'exchangeability': 'Not established. Connected pairs share blocks; unmeasured regional structure remains possible. Geometry screens cannot establish a null distribution.',
        'null_calibration_run': False,
        'gates': {'primary_overlap_pass': primary['coverage_gate_pass'] and primary['balance_gate_pass'],
            'primary_any_block_geometry_pass': any(b['geometry_screen_pass'] for b in pb),
            'observed_field_test_allowed_by_this_preflight': False}}
    save('summary.json', summary)
    n = summary['northern_early_noachian']; dist = n['distance_to_boundary_min_median_max_km']
    lines = ['# Arabia Terra: geometry and support preflight', '',
        '**Status: executed prerequisite checks; no observed magnetic outcomes used.**', '',
        '## What the checks found', '',
        f'- All **{n["cells"]}** northern Early Noachian cells from Test 1 were recovered; **{n["inside_declared_arabia"]}** fall inside the declared Arabia footprint.',
        f'- Their distances from the supplied dichotomy polyline range from **{dist[0]:.1f} to {dist[2]:.1f} km**, with a median of **{dist[1]:.1f} km**. Counts within 50/100/160 km are **{n["near_boundary_counts"]["50"]}/{n["near_boundary_counts"]["100"]}/{n["near_boundary_counts"]["160"]}**.',
        f'- The declared pools contain **{primary["target_candidates"]} Arabia cells** and **{primary["control_candidates"]} controls**. The primary matching retains **{primary["matched_pairs"]} pairs**, representing **{100*primary["target_area_fraction_matched"]:.1f}%** of eligible Arabia area.',
        f'- Maximum absolute standardized covariate imbalance after matching is **{primary["maximum_absolute_post_smd"]:.3f}**, against the declared screening threshold of 0.1.', '',
        '![Geometry and declared comparison pools](followup/arabia/geometry.png)', '',
        '## Why this is a preflight, not a magnetic result', '',
        'The analysis discards the magnetic arrays before extracting any covariate. Global associations and earlier results were already known; this is procedural non-use of outcomes for the present matching, not a historically blind discovery. It neither estimates a magnetic deficit nor decides whether the archive hypothesis is correct.', '',
        '## Region and input resolution', '',
        'The [USGS Gazetteer footprint](https://planetarynames.wr.usgs.gov/Feature/336), saved as `arabia_polygon.geojson`, is an approximate extent of a named feature. It is not a mapped geological contact. The detailed geometry (`wkt-25452`) on that page was selected before matching; its alternate rectangular extent was not substituted. Credit: USGS / IAU; USGS-produced numerical information is used under its [public-domain policy](https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits).', '',
        'The covariates are the existing native **2° atlas**: USGS SIM 3292 geological unit, MOLA elevation, Wieczorek crustal-thickness scenarios and the Andrews-Hanna boundary distributed with that archive. The 0.5° output contains a footprint mask only. It supplies no additional geological or magnetic resolution. The approximately 160 km surface resolution of [Langlais et al. (2019)](https://doi.org/10.1029/2018JE005854) motivates dependence checks but is not a measured correlation length for this comparison.', '',
        'Boundary distances use sampled great-circle segments with at most 5 km spacing (distance overestimate no more than 2.5 km from sampling). This is separate from uncertainty in the geological boundary itself. Polygon inclusion follows the supplied longitude/latitude outline; approximate edge distances use the spherical-segment convention.', '',
        '## Declared comparison', '',
        'Both groups are pure Noachian units south of the dichotomy boundary, within 500 km of it and between 30°S and 55°N. Controls lie outside Arabia and at least 300 km from its outline. Thus the comparison conditions on boundary side; the 23 northern cells are a separate diagnostic, not the Arabia treatment group.', '',
        'Matching is without replacement and exact in epoch rank. Primary calipers are 1 km in elevation, 5 km in thickness, 150 km in boundary distance and 10° in latitude. Assignment first maximizes pair count, then minimizes squared caliper-scaled distance. The 2,600–2,900 kg/m³ atlas density scenarios and half/double calipers are declared sensitivities. Pair differences use the target cell’s area weight on both members, and balance uses the pooled unmatched standard deviation.', '',
        '| Density (kg/m³) | Caliper multiplier | Pairs | Arabia area retained | Max. absolute SMD | Coverage + balance pass |',
        '| --- | --- | --- | --- | --- | --- |']
    for r in match_rows:
        lines.append(f'| {r["density_kg_m3"]} | {r["caliper_multiplier"]:g} | {r["matched_pairs"]} | {r["target_area_fraction_matched"]:.1%} | {r["maximum_absolute_post_smd"]:.3f} | {r["coverage_gate_pass"] and r["balance_gate_pass"]} |')
    lines += ['', 'The 50% area-coverage and 0.1 imbalance thresholds are declared feasibility screens, not universal statistical criteria. Changing a caliper changes which population can be compared. All twelve declared variants fail at least one of these screens. This finding concerns the chosen pools and matching design; it does not prove that every possible Arabia comparison is infeasible.', '',
        '## Can the blocks be exchanged?', '',
        'A block shared by several pairs couples those pairs. Connecting all pairs through shared target or control blocks reveals the candidate joint sign-flip units. This diagnoses one source of dependence; components are not automatically independent, and swapping regional labels is not justified merely by matching measured covariates.', '',
        '| Nominal block size (km) | Grid offset | Target/control blocks | Connected components | Largest component (pairs) | Closest components (km) | Geometry screen |',
        '| --- | --- | --- | --- | --- | --- | --- |']
    for b in pb:
        distance = b['minimum_between_component_distance_km']
        lines.append(f'| {b["nominal_block_km"]} | {b["offset_fraction"]:g} | {b["target_blocks"]}/{b["control_blocks"]} | {b["pair_graph_components"]} | {b["largest_component_pairs"]} | {distance:.1f} | {b["geometry_screen_pass"]} |' if distance is not None else f'| {b["nominal_block_km"]} | {b["offset_fraction"]:g} | {b["target_blocks"]}/{b["control_blocks"]} | {b["pair_graph_components"]} | {b["largest_component_pairs"]} | Not applicable | {b["geometry_screen_pass"]} |')
    lines += ['', 'The declared geometry screen asks for at least eight components and 160 km between sampled cells in different components. It does not prove exchangeability, stationarity, identical noise or independence of the underlying source footprints. The scientific target is still spatially structured and regional covariates remain unmeasured.', '',
        '**No permutation p-value is reported.** The primary overlap and block screens are reported above. A supported design and synthetic-null calibration are required before an observed-field test. Naively treating grid cells or pairs sharing a block as independent would inflate the apparent sample size.', '',
        '## Reproduce and inspect', '',
        '```bash', 'python scripts/followup/arabia_preflight.py', 'python -m pytest -q tests/test_spatial_matching.py', '```', '',
        'The run is offline and writes only this follow-up directory and its report. Its inputs, protocol, numerical source code and outputs are hashed in [the manifest](followup/arabia/manifest.json). Source attribution and reuse terms for the existing atlas remain in [the input manifest](data/manifest.json). The six-test outputs are not rebuilt or overwritten.', '',
        '- [Frozen preflight protocol](followup/arabia/protocol.json)',
        '- [23 northern-cell coordinates](followup/arabia/northern_early_noachian_cells.csv)',
        '- [Covariates and eligibility masks](followup/arabia/covariates_and_masks.csv)',
        '- [Matching diagnostics](followup/arabia/matching_diagnostics.csv)',
        '- [Matched pairs](followup/arabia/matched_pairs.csv)',
        '- [All block diagnostics](followup/arabia/block_diagnostics.csv)',
        '- [Pair/block allocation ledger](followup/arabia/pair_block_allocations.csv)',
        '- [Polygon GeoJSON](followup/arabia/arabia_polygon.geojson)',
        '- [Geometry-only 0.5° mask](followup/arabia/geometry_mask_0p5.npz)',
        '- [Machine-readable summary](followup/arabia/summary.json)', '']
    (ROOT/'research/ARABIA_PREFLIGHT.md').write_text('\n'.join(lines))
    return summary


def main():
    protocol = json.loads((OUT/'protocol.json').read_text())
    data = inputs(protocol)
    matched, blocks, primary_pair = match_all(data, protocol)
    figures(data, primary_pair)
    summary = report(data, matched, blocks, protocol)
    files = [p for p in OUT.iterdir() if p.is_file() and p.name != 'manifest.json']
    save('manifest.json', {'generated_by': 'scripts/followup/arabia_preflight.py',
        'magnetic_outcomes_used': False,
        'input_sha256': {protocol['atlas_file']: sha(ROOT/protocol['atlas_file']), protocol['boundary_file']: sha(ROOT/protocol['boundary_file'])},
        'code_sha256': {str(p.relative_to(ROOT)): sha(p) for p in [Path(__file__).resolve(), ROOT/'src/marswind/spatial_matching.py', ROOT/'src/marswind/agetransfer.py']},
        'outputs_sha256': {p.name: sha(p) for p in sorted(files)},
        'report_sha256': sha(ROOT/'research/ARABIA_PREFLIGHT.md'),
        'software': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__, 'pyshtools': pyshtools.__version__, 'shapely': shapely.__version__}})
    print(json.dumps(safe({k: summary[k] for k in ['northern_early_noachian', 'primary_matching', 'primary_block_diagnostics', 'gates']}), indent=2))


if __name__ == '__main__':
    main()
