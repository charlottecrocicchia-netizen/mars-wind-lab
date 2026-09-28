"""Execute the frozen boundary-transect test from authorized local inputs.

Geometry and a synthetic-null calibration are saved before evaluating the
observed magnetic model. No numerical output from an earlier test is replaced.
"""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import pyshtools as sh
import shapely
from shapely.geometry import Polygon, GeometryCollection, LineString
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'boundary-walk-v1'
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from marswind.agetransfer import epoch_features
from marswind.spatial_matching import unit_vectors
from marswind.boundary_walk import (ClosedCurve, advance, lat_lon, block_operator,
    sign_patterns, reference_tails, synthetic_calibration)

OUT = ROOT/'research/followup/boundary_walk'
RAW = ROOT/'data/observations/raw'


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clean(x):
    if isinstance(x, dict): return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (tuple, list, np.ndarray)): return [clean(v) for v in x]
    if isinstance(x, (bool, np.bool_)): return bool(x)
    if isinstance(x, (int, np.integer)): return int(x)
    if isinstance(x, (float, np.floating)): return float(x) if np.isfinite(x) else None
    return x


def save(name, data):
    (OUT/name).write_text(json.dumps(clean(data), indent=2, allow_nan=False)+'\n')


def csv_save(name, rows):
    with (OUT/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader(); w.writerows(clean(rows))


def geology_classifier():
    """Interpret polygon rings with even/odd inclusion; reject multiple hits."""
    raw = json.loads((RAW/'geology/units.json').read_text())
    assert raw['spatialReference']['wkid'] == 104971
    polygons, codes = [], []
    for feature in raw['features']:
        geom = GeometryCollection()
        for ring in feature['geometry']['rings']:
            geom = shapely.symmetric_difference(geom, shapely.make_valid(Polygon(ring)))
        polygons.append(geom); codes.append(feature['attributes']['Unit'])
    tree = shapely.STRtree(polygons)
    def classify(vectors):
        lat, lon = lat_lon(vectors)
        points = shapely.points(((lon+180) % 360-180).ravel(), lat.ravel())
        pairs = tree.query(points, predicate='within')
        hits = np.bincount(pairs[0], minlength=len(points))
        values = np.full(len(points), '', dtype='<U12')
        for point, feature in pairs.T:
            if hits[point] == 1: values[point] = codes[feature]
        return values.reshape(lat.shape)
    return classify


def geology_flags(codes):
    ranks = np.full(codes.shape, np.nan)
    pure = np.zeros(codes.shape, bool)
    for code in np.unique(codes):
        if not code: continue
        features = epoch_features(code)
        ranks[codes == code] = features['rank']
        pure[codes == code] = features['noachian'] == 1 and features['mixed'] == 0
    return pure, ranks


def geometry(protocol):
    coords = np.loadtxt(RAW/'crustal_models/selected/dichotomy_coordinates-JAH-0-360.txt')
    curve = ClosedCurve(coords, protocol['radius_for_geodesics_km'])
    mask = sh.backends.shtools.Curve2Mask(720, coords[:, [1, 0]], 0, sampling=2, extend=True).astype(bool)
    def south(vectors):
        lat, lon = lat_lon(vectors)
        return mask[np.clip(np.rint((90-lat)*4).astype(int), 0, 720), np.rint(lon*4).astype(int) % 1440]
    n = curve.normals(protocol['tangent_half_window_km'])
    plus = south(advance(curve.points, n, protocol['orientation_probe_km']))
    minus = south(advance(curve.points, n, -protocol['orientation_probe_km']))
    oriented = plus != minus
    n[~plus & minus] *= -1
    centers, endpoints, center_south, flags = [], [], [], []
    for shift in protocol['line_shifts_south_km']:
        center = advance(curve.points, n, shift)
        if shift:
            lat, lon = lat_lon(center)
            shifted = ClosedCurve(np.column_stack((lon, lat)), curve.radius_km)
            normal = shifted.normals(protocol['tangent_half_window_km'])
            angle = shift/curve.radius_km
            transported = -np.sin(angle)*curve.points+np.cos(angle)*n
            normal[np.sum(normal*transported, axis=1) < 0] *= -1
        else:
            normal = n
        lat, lon = lat_lon(center)
        unwrapped = np.rad2deg(np.unwrap(np.deg2rad(lon)))
        simple = LineString(np.column_stack((unwrapped, lat))).is_simple
        centers.append(center); center_south.append(south(center))
        flags.append({'shift_south_km': shift, 'unwrapped_polyline_is_simple': simple,
            'centers_south_of_true_boundary': int(south(center).sum())})
        pairs = []
        for distance in protocol['offset_distances_km']:
            pairs.append(np.stack((advance(center, normal, -distance), advance(center, normal, distance)), axis=1))
        endpoints.append(pairs)
    points = np.asarray(endpoints)
    centers = np.asarray(centers)
    true_south = south(points)
    print('Classifying authorized USGS polygons...', flush=True)
    classify = geology_classifier()
    codes = classify(points); center_codes = classify(centers)
    pure, ranks = geology_flags(codes); center_pure, _ = geology_flags(center_codes)
    broad = pure[..., 0] & pure[..., 1] & oriented[None, None, :]
    broad[0] &= ~true_south[0, ..., 0] & true_south[0, ..., 1]
    for li in [1, 2]:
        broad[li] &= (true_south[li, ..., 0] & true_south[li, ..., 1] &
                      np.asarray(center_south)[li][None, :] & center_pure[li][None, :])
    strict = broad & (ranks[..., 0] == ranks[..., 1])
    rows = []
    lat, lon = lat_lon(points)
    for li, shift in enumerate(protocol['line_shifts_south_km']):
        flags[li]['centers_pure_noachian'] = int(center_pure[li].sum())
        for di, distance in enumerate(protocol['offset_distances_km']):
            for i in range(len(curve.points)):
                rows.append({'station': i, 'arc_km': curve.arc[i], 'arc_weight_km': curve.weights[i],
                    'shift_south_km': shift, 'distance_each_side_km': distance,
                    'north_latitude': lat[li, di, i, 0], 'north_longitude': lon[li, di, i, 0],
                    'south_latitude': lat[li, di, i, 1], 'south_longitude': lon[li, di, i, 1],
                    'north_unit': codes[li, di, i, 0], 'south_unit': codes[li, di, i, 1],
                    'north_epoch_rank': ranks[li, di, i, 0], 'south_epoch_rank': ranks[li, di, i, 1],
                    'center_unit': center_codes[li, i], 'north_endpoint_south_of_true_boundary': true_south[li, di, i, 0],
                    'south_endpoint_south_of_true_boundary': true_south[li, di, i, 1],
                    'orientation_probe_resolved': oriented[i], 'both_pure_noachian_eligible': broad[li, di, i],
                    'same_epoch_rank_eligible': strict[li, di, i]})
    csv_save('geometry_and_eligibility.csv', rows)
    np.savez_compressed(OUT/'geometry.npz', points=points, centers=centers, broad=broad, strict=strict,
        arc_km=curve.arc, arc_weights=curve.weights, codes=codes)
    save('geometry_summary.json', {'protocol_sha256': sha(OUT/'protocol.json'),
        'unique_stations': len(curve.points), 'supplied_rows': len(coords), 'curve_length_km': curve.length,
        'orientation_probes_resolved': int(oriented.sum()), 'lines': flags,
        'eligible_counts_both_noachian': broad.sum(axis=2), 'eligible_counts_same_epoch': strict.sum(axis=2),
        'geometry_csv_sha256': sha(OUT/'geometry_and_eligibility.csv'),
        'saved_before_field_evaluation_utc': datetime.now(timezone.utc).isoformat()})
    print('Geometry frozen:', {'stations': len(curve.points), 'length_km': round(curve.length), 'broad_counts': broad.sum(axis=2).tolist()}, flush=True)
    return curve, points, centers, broad, strict, flags


def designs(curve, broad, strict, protocol):
    result = []
    for selection, masks in zip(protocol['selections'], [broad, strict]):
        for di, distance in enumerate(protocol['offset_distances_km']):
            common = np.all(masks[:, di], axis=0)
            for block_offset in protocol['blocks']['offset_fractions']:
                comparisons = [(f'line_{shift}', [li], [1], masks[li, di]) for li, shift in enumerate(protocol['line_shifts_south_km'])]
                comparisons += [(f'real_minus_{shift}', [0, li], [1, -1], common) for li, shift in enumerate(protocol['line_shifts_south_km']) if shift]
                for name, lines, signs, eligible in comparisons:
                    matrix, ids, support, width = block_operator(curve, eligible,
                        protocol['blocks']['nominal_length_km'], block_offset, protocol['blocks']['minimum_retained_arc_weight_km'])
                    result.append({'name': name, 'selection': selection, 'distance_km': distance,
                        'block_offset': block_offset, 'lines': lines, 'signs': signs, 'di': di,
                        'eligible': eligible, 'matrix': matrix, 'block_ids': ids,
                        'support': support, 'block_width': width})
    return result


def design_key(d):
    return f'{d["name"]}_{d["selection"]}_d{d["distance_km"]}_offset{d["block_offset"]:g}'


def null_checks(design_list, points, protocol):
    results = {}
    p = protocol['synthetic_null']
    for d in design_list:
        if d['selection'] != protocol['primary_selection'] or d['distance_km'] != 200 or d['block_offset'] != 0 or d['name'] not in ['line_0', 'real_minus_500', 'real_minus_1000']:
            continue
        key = design_key(d); blocks = len(d['matrix'])
        if blocks < protocol['blocks']['minimum_blocks_for_calibration']:
            results[key] = {'blocks': blocks, 'ran': False, 'gate_pass': False, 'reason': 'Fewer than eight retained blocks', 'nulls': []}
            continue
        locations, operators = [], []
        for li, sign in zip(d['lines'], d['signs']):
            locations.append(points[li, d['di']].reshape(-1, 3))
            op = np.empty((blocks, len(d['eligible'])*2))
            op[:, 0::2] = -sign*d['matrix']; op[:, 1::2] = sign*d['matrix']
            operators.append(op)
        nulls = synthetic_calibration(np.concatenate(operators, axis=1), np.vstack(locations),
            p['correlation_lengths_km'], protocol['radius_for_geodesics_km'], p['features'],
            p['realizations_per_length'], protocol['sign_flips']['seed'])
        passed = all(n['false_positive_rate_at_005'] <= p['maximum_empirical_false_positive_rate'] for n in nulls)
        results[key] = {'blocks': blocks, 'ran': True, 'gate_pass': passed, 'nulls': nulls}
        print('Synthetic null:', key, [n['false_positive_rate_at_005'] for n in nulls], flush=True)
    save('synthetic_null.json', {'protocol_sha256': sha(OUT/'protocol.json'),
        'saved_before_field_evaluation_utc': datetime.now(timezone.utc).isoformat(), 'cases': results})
    return results


def evaluate(points, broad, design_list, nulls, curve, protocol):
    model = sh.SHMagCoeffs.from_file(str(RAW/'magnetic_field/Langlais2019.sh.gz'), lmax=134,
        skip=4, r0=protocol['magnetic_reference_radius_km']*1000, header=False,
        file_units='nT', units='nT', encoding='utf-8')
    rows, blocks, field_rows = [], [], []
    for altitude in protocol['altitudes_km']:
        fields = np.full(points.shape[:-1], np.nan)
        select = np.repeat(broad[..., None], 2, axis=-1)
        positions = points[select]
        lat, lon = lat_lon(positions)
        vectors = model.expand(lat=lat, lon=lon, r=np.full(len(lat), (protocol['magnetic_reference_radius_km']+altitude)*1000))
        fields[select] = np.linalg.norm(vectors, axis=1)
        assert np.all(np.isfinite(fields[select]))
        print('Evaluated selected magnetic points:', altitude, len(lat), flush=True)
        for li, shift in enumerate(protocol['line_shifts_south_km']):
            for di, distance in enumerate(protocol['offset_distances_km']):
                for i in np.where(broad[li, di])[0]:
                    field_rows.append({'altitude_km': altitude, 'shift_south_km': shift,
                        'distance_each_side_km': distance, 'station': i,
                        'north_field_nt': fields[li, di, i, 0], 'south_field_nt': fields[li, di, i, 1],
                        'delta_log1p_nt': np.log1p(fields[li, di, i, 1])-np.log1p(fields[li, di, i, 0])})
        for d in design_list:
            delta = np.zeros(len(curve.points))
            for li, sign in zip(d['lines'], d['signs']):
                contribution = np.log1p(fields[li, d['di'], :, 1])-np.log1p(fields[li, d['di'], :, 0])
                delta += sign*np.where(d['eligible'], contribution, 0)
            values = d['matrix'] @ delta
            if len(values):
                signs, exact = sign_patterns(len(values), protocol['sign_flips']['seed'], protocol['sign_flips']['draws'], protocol['sign_flips']['exact_if_blocks_at_most'])
                reference = float(reference_tails(values, signs, exact)[0])
            else:
                reference = None
            key = design_key(d)
            calibration = nulls.get(key)
            row = {'altitude_km': altitude, 'comparison': d['name'], 'selection': d['selection'],
                'distance_each_side_km': d['distance_km'], 'block_offset_fraction': d['block_offset'],
                'eligible_pairs': int(d['eligible'].sum()), 'retained_arc_weight_km': float(curve.weights[d['eligible']].sum()),
                'pairs_in_retained_blocks': int(np.any(d['matrix'] > 0, axis=0).sum()),
                'arc_weight_in_retained_blocks_km': float(d['support'].sum()),
                'retained_blocks': len(values), 'block_width_km': d['block_width'],
                'equal_block_mean_delta_log1p': float(values.mean()) if len(values) else None,
                'arc_weighted_delta_log1p': float(np.average(delta[d['eligible']], weights=curve.weights[d['eligible']])) if d['eligible'].any() else None,
                'positive_blocks': int(np.sum(values > 0)), 'reference_sign_flip_tail': reference,
                'primary_synthetic_null_gate_pass': bool(calibration and calibration['gate_pass']),
                'real_data_exchangeability_established': False}
            rows.append(row)
            for block_id, weight, value in zip(d['block_ids'], d['support'], values):
                blocks.append({'altitude_km': altitude, 'design': key, 'block': block_id,
                    'represented_arc_weight_km': weight, 'delta_log1p': value})
    csv_save('contrasts.csv', rows); csv_save('block_contrasts.csv', blocks); csv_save('selected_field_values.csv', field_rows)
    return rows, blocks


def regional_23(protocol):
    atlas = json.loads((ROOT/'research/data/atlas.json').read_text())
    cells = list(csv.DictReader((ROOT/'research/followup/arabia/northern_early_noachian_cells.csv').open()))
    lat = np.array([float(c['latitude_deg']) for c in cells]); lon = np.array([float(c['longitude_east_deg']) for c in cells])
    weights = np.cos(np.deg2rad(lat))
    indices = [(int(c['cell_id'][1:3]), int(c['cell_id'][4:])) for c in cells]
    boundary = np.loadtxt(RAW/'crustal_models/selected/dichotomy_coordinates-JAH-0-360.txt')
    south = sh.backends.shtools.Curve2Mask(180, boundary[:, [1, 0]], 0, sampling=2, extend=True)
    ay, ax = np.meshgrid(atlas['latitude'], atlas['longitude'], indexing='ij')
    atlas_south = south[np.ix_((90-np.array(atlas['latitude'])).astype(int), np.array(atlas['longitude']).astype(int))].astype(bool)
    strong = atlas_south & (np.asarray(atlas['magnetic_nT']['150']) >= 100)
    chord, _ = cKDTree(unit_vectors(ay[strong], ax[strong])).query(unit_vectors(lat, lon))
    distances = 2*protocol['radius_for_geodesics_km']*np.arcsin(np.clip(chord/2, 0, 1))
    labels = np.full(len(cells), '', dtype='<U30')
    for name, box in protocol['regional_23']['regions'].items():
        selected = (lat >= box['latitude'][0]) & (lat <= box['latitude'][1]) & (lon >= box['longitude'][0]) & (lon <= box['longitude'][1])
        assert np.all(labels[selected] == '')
        labels[selected] = name
    assert np.all(labels != '') and len(cells) == 23
    summaries, individual = [], []
    for altitude in protocol['altitudes_km']:
        grid = np.asarray(atlas['magnetic_nT'][str(altitude)])
        values = np.array([grid[i, j] for i, j in indices])
        logs = np.log1p(values); total = np.sum(weights*logs)
        for name in [*protocol['regional_23']['regions'], 'All_23']:
            mask = labels == name if name != 'All_23' else np.ones(len(cells), bool)
            summaries.append({'region': name, 'altitude_km': altitude, 'cells': int(mask.sum()),
                'arithmetic_mean_nt': np.average(values[mask], weights=weights[mask]),
                'back_transformed_log_mean_nt': np.expm1(np.average(logs[mask], weights=weights[mask])),
                'fraction_of_total_weighted_log_signal': np.sum(weights[mask]*logs[mask])/total,
                'distance_to_southern_100nt_atlas_cells_min_km': distances[mask].min(),
                'distance_to_southern_100nt_atlas_cells_median_km': np.median(distances[mask])})
        for i, cell in enumerate(cells):
            individual.append({'cell_id': cell['cell_id'], 'region': labels[i], 'latitude': lat[i], 'longitude': lon[i],
                'altitude_km': altitude, 'field_nt': values[i], 'area_weight': weights[i],
                'distance_to_southern_100nt_atlas_cell_km': distances[i]})
    csv_save('regional_23_summary.csv', summaries); csv_save('regional_23_cells.csv', individual)
    return summaries


def figures(curve, centers, broad, contrast_rows, block_rows, protocol):
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), layout='constrained')
    for li, shift in enumerate(protocol['line_shifts_south_km']):
        lat, lon = lat_lon(centers[li]); lon = (lon+180) % 360-180
        cuts = np.where(np.abs(np.diff(lon)) > 180)[0]+1
        color = ['#1c5276', '#d97730', '#36947b'][li]
        for j, ids in enumerate(np.split(np.arange(len(lon)), cuts)):
            axes[0].plot(lon[ids], lat[ids], color=color, lw=1, label=f'{shift} km shift' if j == 0 else None)
        selected = broad[li, 0]
        axes[0].scatter(lon[selected], lat[selected], color=color, s=5)
    axes[0].set(xlim=(-180, 180), xlabel='East longitude (°)', ylabel='Latitude (°)',
        title='Boundary and shifted controls · dots: eligible pairs at ±200 km')
    axes[0].legend(fontsize=9); axes[0].grid(alpha=.2)
    for name, color in zip(['line_0', 'real_minus_500', 'real_minus_1000'], ['#1c5276', '#d97730', '#36947b']):
        key = f'{name}_both_pure_noachian_d200_offset0'
        rows = [r for r in block_rows if r['design'] == key and r['altitude_km'] == 150]
        if rows:
            axes[1].scatter([r['block'] for r in rows], [r['delta_log1p'] for r in rows], color=color, label=name.replace('_', ' '), s=35)
    axes[1].text(.5, .94, 'Common-station control differences: no admissible blocks',
        transform=axes[1].transAxes, ha='center', va='top', fontsize=10)
    axes[1].axhline(0, color='grey', lw=.8)
    axes[1].set(xlabel='Block along the original closed boundary', ylabel='Block contrast in log(1 + |B| / nT)',
        title='Primary contrasts at 150 km · control differences use common stations')
    axes[1].legend(fontsize=9); axes[1].grid(alpha=.2)
    fig.savefig(OUT/'boundary_walk.png', dpi=180); fig.savefig(OUT/'boundary_walk.svg', metadata={'Date': None}); plt.close(fig)


def main():
    protocol = json.loads((OUT/'protocol.json').read_text())
    for name, wanted in protocol['input_sha256'].items():
        assert sha(ROOT/name) == wanted, f'Declared input changed: {name}'
    curve, points, centers, broad, strict, flags = geometry(protocol)
    design_list = designs(curve, broad, strict, protocol)
    nulls = null_checks(design_list, points, protocol)
    # No observed magnetic array or coefficient has been read above this line.
    started = datetime.now(timezone.utc).isoformat()
    rows, blocks = evaluate(points, broad, design_list, nulls, curve, protocol)
    regions = regional_23(protocol)
    figures(curve, centers, broad, rows, blocks, protocol)
    primary = [r for r in rows if r['selection'] == 'both_pure_noachian' and r['distance_each_side_km'] == 200 and r['altitude_km'] == 150 and r['block_offset_fraction'] == 0]
    save('summary.json', {'status': 'Executed conditional boundary contrasts and negative-control checks',
        'field_evaluation_started_utc': started, 'curve_length_km': curve.length,
        'unique_stations': len(curve.points), 'primary': primary, 'synthetic_null': nulls,
        'geometry_flags': flags, 'regional_23': regions,
        'limits': 'No attribution to an ancient field asymmetry or archive mechanism follows from the step alone. Shifted controls are negative controls, not automatically draws from a calibrated null.'})
    save('manifest.json', {'generated_by': 'scripts/followup/boundary_walk.py',
        'input_sha256': protocol['input_sha256'], 'protocol_sha256': sha(OUT/'protocol.json'),
        'code_sha256': {str(p.relative_to(ROOT)): sha(p) for p in [Path(__file__).resolve(), ROOT/'src/marswind/boundary_walk.py', ROOT/'src/marswind/agetransfer.py', ROOT/'src/marswind/spatial_matching.py']},
        'outputs_sha256': {p.name: sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'manifest.json'},
        'software': {'python': platform.python_version(), 'numpy': np.__version__, 'pyshtools': sh.__version__, 'shapely': shapely.__version__}})
    print(json.dumps(clean({'primary': primary, 'regions_150': [r for r in regions if r['altitude_km'] == 150]}), indent=2))


if __name__ == '__main__': main()
