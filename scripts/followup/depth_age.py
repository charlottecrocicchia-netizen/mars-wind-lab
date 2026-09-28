"""Equivalent source depth against surface age: frozen protocol, then evaluation.

Usage: python scripts/followup/depth_age.py
Inputs are the committed 2° atlas (geology), the usable Gong & Wieczorek
source-depth windows and the window field statistics already saved by the
six-test build. The protocol and the prediction are written before any depth
or field value is read. Outputs go to research/followup/depth_age/ and the
report to research/DEPTH_AGE.md.
"""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'depth-age-v1'
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from marswind.agetransfer import epoch_features
from marswind.depth_age import surface_summary, spearman, wedge_labels, block_bootstrap_spearman, binned_means

OUT = ROOT/'research/followup/depth_age'
OUT.mkdir(parents=True, exist_ok=True)

PROTOCOL = {
    'declared_utc': datetime.now(timezone.utc).isoformat(),
    'question': 'Within each hemisphere, does the equivalent magnetic source depth of Gong & Wieczorek (2021) vary with the age of the overlying surface?',
    'prediction_declared_before_evaluation': {
        'resurfacing_archive': 'If northern sources are weak because young surfaces removed, buried or reheated the shallow record, the surviving northern sources should sit deeper where the surface is younger: a negative rank correlation between depth and the Noachian area fraction within the north.',
        'borealis_excavation': 'If northern strong material was excavated early (Gong & Wieczorek interpretation), northern depths are shallow regardless of surface age: no dependence within the north.',
        'south': 'No directional prediction is declared for the south; its correlation is reported as a comparison.'},
    'inputs': {'depths': 'research/data/depths.json, usable windows only (nonnegative best fit with published bounds)',
               'field': 'research/discriminating/amplitude_windows.csv, RMS |B| at 150 km within 10° (already saved)',
               'geology': 'research/data/atlas.json, USGS SIM 3292 unit at 2° centres, epoch rank and Noachian indicator from marswind.agetransfer'},
    'surface_radii_deg': [10, 20], 'unassigned_fraction_max': 0.25,
    'depth_variants': ['best', 'lower_1sigma', 'upper_1sigma'],
    'correlation': 'Spearman rank correlation; interval from a block bootstrap over 6 longitude wedges of 60° (offsets 0° and 30°), 2000 draws, seed 20260928. Windows are 10° apart with 20° radii and are not independent; the wedge is the resampling unit.',
    'decision_rule': 'An association is reported only if the sign of rho is the same for all three depth variants, both radii and both wedge offsets, and the 5–95% block interval excludes zero in the primary case (best depth, 10°, offset 0). Otherwise the result is reported as no supported dependence. Association is not causation and surface age is not source age.',
    'noachian_bins': [0, .25, .5, .75, 1.0001]}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clean(x):
    if isinstance(x, dict): return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, np.ndarray)): return [clean(v) for v in x]
    if isinstance(x, (bool, np.bool_)): return bool(x)
    if isinstance(x, (int, np.integer)): return int(x)
    if isinstance(x, (float, np.floating)): return float(x) if np.isfinite(x) else None
    return x
def save(name, data): (OUT/name).write_text(json.dumps(clean(data), indent=2, allow_nan=False)+'\n')
def csv_save(name, rows):
    with (OUT/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(clean(rows))


def main():
    save('protocol.json', PROTOCOL)
    atlas = json.loads((ROOT/'research/data/atlas.json').read_text())
    lat = np.array(atlas['latitude'], float); lon = np.array(atlas['longitude'], float)
    LA, LO = np.meshgrid(lat, lon, indexing='ij')
    codes = atlas['geology']['codes']; grid = np.array(atlas['geology']['grid'])
    feats = [epoch_features(c) for c in codes]
    rank_grid = np.where(grid >= 0, np.array([f['rank'] for f in feats])[np.clip(grid, 0, None)], np.nan)
    noach_grid = np.where(grid >= 0, np.array([f['noachian'] for f in feats])[np.clip(grid, 0, None)], np.nan)
    started = datetime.now(timezone.utc).isoformat()
    depths = [d for d in json.loads((ROOT/'research/data/depths.json').read_text()) if d['usable']]
    field = {(round(r['lat'], 3), round(r['lon'], 3)): float(r['rms_field_150km_nt']) for r in csv.DictReader((ROOT/'research/discriminating/amplitude_windows.csv').open())
             for r in [{**r, 'lat': float(r['lat']), 'lon': float(r['lon'])}]}
    rows = []
    for d in depths:
        row = {'region': d['region'], 'lat': d['lat'], 'lon': d['lon'], 'depth_best_km': d['depth_km'], 'depth_lower_km': d['lower_km'], 'depth_upper_km': d['upper_km'],
               'rms_field_150km_nt': field[(round(d['lat'], 3), round(d['lon'], 3))]}
        for r in PROTOCOL['surface_radii_deg']:
            s = surface_summary(LA, LO, rank_grid, noach_grid, d['lat'], d['lon'], r)
            row.update({f'noachian_fraction_{r}deg': s['noachian_fraction'], f'mean_rank_{r}deg': s['mean_rank'], f'unassigned_fraction_{r}deg': s['unassigned_fraction']})
        rows.append(row)
    csv_save('windows.csv', rows)
    results = []
    for hemi in ['North', 'South']:
        sel = [r for r in rows if r['region'] == hemi]
        lons = np.array([r['lon'] for r in sel])
        for radius in PROTOCOL['surface_radii_deg']:
            keep = np.array([r[f'unassigned_fraction_{radius}deg'] <= PROTOCOL['unassigned_fraction_max'] for r in sel])
            for covariate in [f'noachian_fraction_{radius}deg', f'mean_rank_{radius}deg']:
                x = np.array([r[covariate] for r in sel])[keep]
                for variant, key in [('best', 'depth_best_km'), ('lower_1sigma', 'depth_lower_km'), ('upper_1sigma', 'depth_upper_km')]:
                    y = np.array([r[key] for r in sel])[keep]
                    for offset in [0., 30.]:
                        boot = block_bootstrap_spearman(x, y, wedge_labels(lons[keep], 6, offset), draws=2000, seed=20260928)
                        results.append({'hemisphere': hemi, 'radius_deg': radius, 'covariate': covariate.rsplit('_', 1)[0], 'depth_variant': variant, 'wedge_offset_deg': offset,
                                        'windows': int(keep.sum()), **boot})
        # field strength against depth for context (Gong & Wieczorek: strongest anomalies are deep)
        y = np.array([r['depth_best_km'] for r in sel]); f = np.log1p(np.array([r['rms_field_150km_nt'] for r in sel]))
        boot = block_bootstrap_spearman(f, y, wedge_labels(lons, 6, 0.), draws=2000, seed=20260928)
        results.append({'hemisphere': hemi, 'radius_deg': 10, 'covariate': 'log_rms_field_150km', 'depth_variant': 'best', 'wedge_offset_deg': 0., 'windows': len(sel), **boot})
    csv_save('correlations.csv', results)
    bins = []
    for hemi in ['North', 'South']:
        sel = [r for r in rows if r['region'] == hemi and r['unassigned_fraction_10deg'] <= PROTOCOL['unassigned_fraction_max']]
        for b in binned_means([r['noachian_fraction_10deg'] for r in sel], [r['depth_best_km'] for r in sel], PROTOCOL['noachian_bins']):
            bins.append({'hemisphere': hemi, **b})
    csv_save('depth_by_noachian_fraction.csv', bins)
    # decision per hemisphere for the Noachian-fraction covariate
    decisions = {}
    for hemi in ['North', 'South']:
        cases = [r for r in results if r['hemisphere'] == hemi and r['covariate'] == 'noachian_fraction']
        primary = next(r for r in cases if r['radius_deg'] == 10 and r['depth_variant'] == 'best' and r['wedge_offset_deg'] == 0.)
        signs = {np.sign(r['rho']) for r in cases if np.isfinite(r['rho'])}
        consistent = len(signs) == 1
        excludes_zero = (primary['q05'] > 0) or (primary['q95'] < 0)
        decisions[hemi] = {'primary_rho': primary['rho'], 'primary_interval_q05_q95': [primary['q05'], primary['q95']], 'blocks': primary['blocks'],
                           'sign_consistent_across_12_cases': consistent, 'primary_interval_excludes_zero': excludes_zero,
                           'verdict': 'association reported' if consistent and excludes_zero else 'no supported dependence',
                           'rho_range_across_cases': [min(r['rho'] for r in cases), max(r['rho'] for r in cases)]}
    summary = {'field_evaluation_started_utc': started, 'windows_total': len(rows), 'windows_by_hemisphere': {h: sum(r['region'] == h for r in rows) for h in ['North', 'South']},
               'decisions': decisions, 'correlations': results, 'bins': bins,
               'scope': 'Rank correlations between equivalent thin-layer depth and surface-age summaries of the 2° geological map inside each window; block bootstrap over longitude wedges. Describes association in one dataset; does not date sources or establish a mechanism.'}
    save('summary.json', summary)
    figure(rows, bins, decisions)
    save('manifest.json', {'generated_utc': datetime.now(timezone.utc).isoformat(), 'inputs_sha256': {p: sha(ROOT/p) for p in ['research/data/atlas.json', 'research/data/depths.json', 'research/discriminating/amplitude_windows.csv']},
                           'code_sha256': {'src/marswind/depth_age.py': sha(ROOT/'src/marswind/depth_age.py'), 'src/marswind/agetransfer.py': sha(ROOT/'src/marswind/agetransfer.py'), 'scripts/followup/depth_age.py': sha(Path(__file__))},
                           'outputs_sha256': {p.name: sha(p) for p in sorted(OUT.iterdir()) if p.name != 'manifest.json'},
                           'software': {'python': platform.python_version(), 'numpy': np.__version__, 'matplotlib': matplotlib.__version__}})
    report(summary, rows)
    print(json.dumps(clean(decisions), indent=1))


def figure(rows, bins, decisions):
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), layout='constrained', sharey=True)
    for a, hemi, color in zip(ax, ['North', 'South'], ['#486282', '#b64f30']):
        sel = [r for r in rows if r['region'] == hemi and r['unassigned_fraction_10deg'] <= PROTOCOL['unassigned_fraction_max']]
        x = np.array([r['noachian_fraction_10deg'] for r in sel]); y = np.array([r['depth_best_km'] for r in sel])
        lo = np.array([r['depth_lower_km'] for r in sel]); hi = np.array([r['depth_upper_km'] for r in sel])
        a.errorbar(x, y, yerr=[np.clip(y-lo, 0, None), np.clip(hi-y, 0, None)], fmt='o', ms=4, color=color, ecolor=color, elinewidth=.5, alpha=.6, label=f'{len(sel)} usable windows')
        bh = [b for b in bins if b['hemisphere'] == hemi and b['median'] is not None]
        a.step([b['low'] for b in bh]+[bh[-1]['high']], [b['median'] for b in bh]+[bh[-1]['median']], where='post', color='k', lw=1.5, label='median depth per Noachian-fraction bin')
        d = decisions[hemi]
        a.set_title(f"{hemi}: Spearman ρ = {d['primary_rho']:+.2f} [{d['primary_interval_q05_q95'][0]:+.2f}, {d['primary_interval_q05_q95'][1]:+.2f}], {d['blocks']} wedges · {d['verdict']}", fontsize=9)
        a.set_xlabel('Noachian area fraction within 10° of the window centre'); a.set_xlim(-.02, 1.02); a.legend(fontsize=7, loc='lower left')
    ax[0].set_ylabel('Equivalent source depth (km, 1σ bounds)'); ax[0].invert_yaxis()
    fig.suptitle('Equivalent source depth (Gong & Wieczorek 2021) against surface age of the overlying map units', fontsize=11)
    fig.savefig(OUT/'depth_age.png', dpi=170); fig.savefig(OUT/'depth_age.svg', metadata={'Date': None}); plt.close(fig)
    svg = OUT/'depth_age.svg'; svg.write_text('\n'.join(l.rstrip() for l in svg.read_text().splitlines())+'\n')


def report(summary, rows):
    d = summary['decisions']; c = summary['correlations']
    def table(hemi):
        sel = [r for r in c if r['hemisphere'] == hemi and r['covariate'] in ('noachian_fraction', 'mean_rank') and r['wedge_offset_deg'] == 0.]
        return '\n'.join(f"| {r['covariate'].replace('_', ' ')} | {r['radius_deg']}° | {r['depth_variant'].replace('_', ' ')} | {r['windows']} | {r['rho']:+.2f} | [{r['q05']:+.2f}, {r['q95']:+.2f}] |" for r in sel)
    fld = {r['hemisphere']: r for r in c if r['covariate'] == 'log_rms_field_150km'}
    bins = summary['bins']
    def bintable(hemi):
        return '\n'.join(f"| {b['low']:.2f}–{min(b['high'], 1):.2f} | {b['count']} | {b['median']:.0f} | {b['mean']:.0f} |" if b['median'] is not None else f"| {b['low']:.2f}–{min(b['high'], 1):.2f} | 0 | — | — |" for b in bins if b['hemisphere'] == hemi)
    md = f'''# Source depth against surface age

**Status: calculation completed · {summary['windows_total']} usable source-depth windows ({summary['windows_by_hemisphere']['North']} north, {summary['windows_by_hemisphere']['South']} south).** [Protocol](followup/depth_age/protocol.json) · [Per-window table](followup/depth_age/windows.csv) · [All correlations](followup/depth_age/correlations.csv) · [Manifest](followup/depth_age/manifest.json)

## Why

Gong & Wieczorek (2021) report equivalent source depths of about 9 km in the north and 32 km in the south and read this as excavation of northern material by the Borealis impact. A resurfacing-archive explanation of the weak north makes a different prediction: where young surfaces removed, buried or reheated the shallow record, the surviving northern sources should be deeper, so depth should increase as the Noachian fraction of the overlying surface decreases. The prediction and the decision rule were written into the protocol before any depth or field value was read.

## How

For each usable window (nonnegative best fit with published 1σ bounds) the area-weighted Noachian fraction and mean epoch rank of the USGS SIM 3292 units are computed within 10° and 20° of the window centre on the 2° atlas. Windows with more than 25% unassigned area are dropped. The rank correlation between depth (best fit, lower and upper 1σ bound) and each surface summary is computed per hemisphere. Because windows are 10° apart with 20° radii, the interval comes from a block bootstrap over six 60° longitude wedges (offsets 0° and 30°), 2,000 draws. Twelve cases per hemisphere and covariate; an association is reported only if all twelve share a sign and the primary interval excludes zero.

## Result

| Hemisphere | Primary ρ (depth vs Noachian fraction, 10°, best depth) | 5–95% block interval | Wedges | Sign consistent across 12 cases | Verdict |
| --- | ---: | --- | ---: | --- | --- |
| North | {d['North']['primary_rho']:+.2f} | [{d['North']['primary_interval_q05_q95'][0]:+.2f}, {d['North']['primary_interval_q05_q95'][1]:+.2f}] | {d['North']['blocks']} | {d['North']['sign_consistent_across_12_cases']} | {d['North']['verdict']} |
| South | {d['South']['primary_rho']:+.2f} | [{d['South']['primary_interval_q05_q95'][0]:+.2f}, {d['South']['primary_interval_q05_q95'][1]:+.2f}] | {d['South']['blocks']} | {d['South']['sign_consistent_across_12_cases']} | {d['South']['verdict']} |

Median equivalent depth by Noachian fraction within 10°:

| North: Noachian fraction | Windows | Median depth (km) | Mean depth (km) |
| --- | ---: | ---: | ---: |
{bintable('North')}

| South: Noachian fraction | Windows | Median depth (km) | Mean depth (km) |
| --- | ---: | ---: | ---: |
{bintable('South')}

All declared cases at offset 0° (offset 30° is in the CSV):

| North | Radius | Depth variant | Windows | ρ | 5–95% |
| --- | --- | --- | ---: | ---: | --- |
{table('North')}

| South | Radius | Depth variant | Windows | ρ | 5–95% |
| --- | --- | --- | ---: | ---: | --- |
{table('South')}

For context, depth against log RMS field at 150 km: north ρ = {fld['North']['rho']:+.2f} [{fld['North']['q05']:+.2f}, {fld['North']['q95']:+.2f}], south ρ = {fld['South']['rho']:+.2f} [{fld['South']['q05']:+.2f}, {fld['South']['q95']:+.2f}]. Gong & Wieczorek's statement that the strongest anomalies are associated with deep sources can be checked against these values.

![Depth against Noachian fraction](followup/depth_age/depth_age.png)

## Reading

The verdict follows the declared rule. A reported association would mean that, within one hemisphere, windows over younger surfaces have systematically different equivalent depths; it would not date the sources, identify a mechanism, or separate resurfacing from lateral variations in crustal structure. No supported dependence would mean that this dataset cannot distinguish the two declared predictions at the 60° wedge scale. Six wedges is a coarse resampling unit; the intervals are correspondingly wide and should be read as such.

## Limits

Equivalent thin-layer depths are model quantities from one field model, with 1σ bounds that often span tens of kilometres. The 2° map units summarise surface age coarsely and mixed-period units are averaged. Windows overlap heavily; the wedge bootstrap addresses one scale of dependence only. No p-value is computed.

## Reproduce

```bash
python scripts/followup/depth_age.py
python -m pytest -q tests/test_depth_age.py
python scripts/research/render_docs.py
```
'''
    (ROOT/'research/DEPTH_AGE.md').write_text(md)


if __name__ == '__main__':
    main()
