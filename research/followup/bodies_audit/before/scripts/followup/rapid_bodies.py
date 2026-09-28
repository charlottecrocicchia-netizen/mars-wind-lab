"""Rapidly cooled bodies under a reversing dynamo: frozen protocol, then evaluation.

Usage: python scripts/followup/rapid_bodies.py
No external data is read: the calculation is a declared physical scenario
(slab cooling, blocking band, reversal statistics) whose purpose is to turn the
Test 4 tension into a bound on the thickness of magnetized bodies. Outputs go
to research/followup/bodies/ and the report to research/RAPID_BODIES.md.
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
matplotlib.rcParams['svg.hashsalt'] = 'rapid-bodies-v1'
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from marswind.rapid_bodies import body_kernels, body_retention, stack_coherence, max_thickness_for_retention

OUT = ROOT/'research/followup/bodies'
OUT.mkdir(parents=True, exist_ok=True)
SEED = 20260928

PROTOCOL = {
    'declared_utc': datetime.now(timezone.utc).isoformat(),
    'question': 'How thick can an igneous body be and still record a coherent thermoremanence under a frequently reversing dynamo, and what does a stack of such bodies retain?',
    'physics': 'Exact conductive cooling of an infinite slab in an infinite host (Carslaw & Jaeger 1959 §2.4), no latent heat, uniform diffusivity. Acquisition on cooling through a uniform blocking band; linear recording; retained fraction = |signed record| / known acquired fraction, as in Tests 2 and 4.',
    'diffusivity_m2_s': 1e-6, 'emplacement_temperature_c': 1200,
    'host_temperatures_c': [100, 300, 400], 'host_note': 'Host temperatures span shallow crust to the depth where the accepted conductive histories reach about 400 °C; the host must be below the band.',
    'thicknesses_m': [30, 100, 300, 1000, 3000, 10000, 30000],
    'blocking_bands_c': {'magnetite_430_580': [430, 580], 'pyrrhotite_175_325': [175, 325]},
    'chron_durations_myr': [0.67, 2, 5, 20, 100], 'periodic_phases': 16, 'poisson_realizations': 128,
    'retention_threshold': 0.5,
    'stack': {'bodies': [1, 3, 10, 30, 100], 'emplacement_spans_myr': [0.1, 1, 10, 100], 'chron_myr': 0.67, 'realizations': 400,
              'note': 'Equal bodies, random emplacement times within the span, polarity = field sign at emplacement, each body fully coherent (thin-body limit).'},
    'decision_rule': 'For each host temperature, band and chron, report the largest declared thickness whose median Poisson retention is at least 0.5. Report the stack coherence distribution. No thickness is asserted for Mars; the output is an inequality conditional on the declared physics.',
    'positions': 32, 'time_points': 400}


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
def q(a, probs=(.05, .5, .95)): return [float(x) for x in np.nanquantile(np.asarray(a, float), probs)]


def main():
    save('protocol.json', PROTOCOL); p = PROTOCOL; started = datetime.now(timezone.utc).isoformat()
    rows = []; bounds = []
    for band_name, (lo, hi) in p['blocking_bands_c'].items():
        band = (lo+273.15, hi+273.15)
        for host in p['host_temperatures_c']:
            if host >= lo: continue
            medians = {c: [] for c in p['chron_durations_myr']}
            for h in p['thicknesses_m']:
                kernels, cooling = body_kernels(h, p['emplacement_temperature_c']+273.15, host+273.15, p['diffusivity_m2_s'], band, p['positions'], p['time_points'])
                for c in p['chron_durations_myr']:
                    per, known = body_retention(kernels, 'periodic', c, p['periodic_phases'])
                    poi, _ = body_retention(kernels, 'poisson', c, p['poisson_realizations'], seed=SEED)
                    rows.append({'band': band_name, 'host_c': host, 'thickness_m': h, 'midplane_cooling_through_band_myr': cooling, 'known_fraction': known, 'chron_myr': c,
                                 'poisson_q05': q(poi)[0], 'poisson_median': q(poi)[1], 'poisson_q95': q(poi)[2], 'poisson_rms': float(np.sqrt(np.mean(poi**2))),
                                 'periodic_median': q(per)[1], 'periodic_q95': q(per)[2]})
                    medians[c].append(q(poi)[1])
            for c in p['chron_durations_myr']:
                bounds.append({'band': band_name, 'host_c': host, 'chron_myr': c, 'max_thickness_m_with_median_retention_ge_0.5': max_thickness_for_retention(p['thicknesses_m'], medians[c], p['retention_threshold']),
                               'medians_by_thickness': dict(zip(map(str, p['thicknesses_m']), medians[c]))})
    csv_save('retention.csv', rows); save('thickness_bounds.json', bounds)
    stack = []
    for n in p['stack']['bodies']:
        for span in p['stack']['emplacement_spans_myr']:
            vals = stack_coherence(n, span, p['stack']['chron_myr'], p['stack']['realizations'], seed=SEED)
            stack.append({'bodies': n, 'emplacement_span_myr': span, 'chron_myr': p['stack']['chron_myr'], 'coherence_q05': q(vals)[0], 'coherence_median': q(vals)[1], 'coherence_q95': q(vals)[2],
                          'coherence_rms': float(np.sqrt(np.mean(vals**2))), 'reference_one_over_sqrt_n': 1/np.sqrt(n)})
    csv_save('stack.csv', stack)
    summary = {'field_evaluation_started_utc': started, 'bounds': bounds, 'stack': stack,
               'scope': 'Declared slab and stack scenarios; inequalities conditional on the stated physics. No Martian body thickness or emplacement history is inferred.'}
    save('summary.json', summary)
    figure(rows, stack)
    save('manifest.json', {'generated_utc': datetime.now(timezone.utc).isoformat(), 'code_sha256': {'src/marswind/rapid_bodies.py': sha(ROOT/'src/marswind/rapid_bodies.py'), 'src/marswind/recording.py': sha(ROOT/'src/marswind/recording.py'), 'scripts/followup/rapid_bodies.py': sha(Path(__file__))},
                           'outputs_sha256': {x.name: sha(x) for x in sorted(OUT.iterdir()) if x.name != 'manifest.json'},
                           'software': {'python': platform.python_version(), 'numpy': np.__version__, 'matplotlib': matplotlib.__version__}})
    report(rows, bounds, stack)
    for b in bounds:
        if b['band'] == 'magnetite_430_580': print(b['host_c'], b['chron_myr'], b['max_thickness_m_with_median_retention_ge_0.5'])


def figure(rows, stack):
    p = PROTOCOL
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.2), layout='constrained')
    sel = [r for r in rows if r['band'] == 'magnetite_430_580' and r['host_c'] == 300]
    for c in p['chron_durations_myr']:
        rr = [r for r in sel if r['chron_myr'] == c]
        line, = ax[0].plot([r['thickness_m']/1000 for r in rr], [r['poisson_median'] for r in rr], marker='o', label=f'Poisson, mean chron {c} Myr')
        ax[0].fill_between([r['thickness_m']/1000 for r in rr], [r['poisson_q05'] for r in rr], [r['poisson_q95'] for r in rr], color=line.get_color(), alpha=.12)
    ax[0].axhline(.5, color='gray', lw=.7); ax[0].set_xscale('log'); ax[0].set_xlabel('Body thickness (km)'); ax[0].set_ylabel('Retained fraction of a steady record'); ax[0].set_ylim(0, 1.02)
    ax[0].set_title('One body, 1,200 °C into a 300 °C host, magnetite band 430–580 °C', fontsize=9); ax[0].legend(fontsize=7)
    for span in p['stack']['emplacement_spans_myr']:
        ss = [s for s in stack if s['emplacement_span_myr'] == span]
        ax[1].plot([s['bodies'] for s in ss], [s['coherence_rms'] for s in ss], marker='s', label=f'emplacement span {span} Myr')
    ns = np.array(p['stack']['bodies']); ax[1].plot(ns, 1/np.sqrt(ns), 'k:', label='1/√N')
    ax[1].set_xscale('log'); ax[1].set_yscale('log'); ax[1].set_xlabel('Number of thin bodies'); ax[1].set_ylabel('RMS net coherence of the stack'); ax[1].legend(fontsize=7)
    ax[1].set_title('Stacks of fully coherent bodies, polarity set at emplacement, mean chron 0.67 Myr', fontsize=9)
    fig.suptitle('Rapid cooling protects a body from cancellation; a stack built across many chrons cancels anyway', fontsize=11)
    fig.savefig(OUT/'bodies.png', dpi=170); fig.savefig(OUT/'bodies.svg', metadata={'Date': None}); plt.close(fig)
    svg = OUT/'bodies.svg'; svg.write_text('\n'.join(l.rstrip() for l in svg.read_text().splitlines())+'\n')


def report(rows, bounds, stack):
    p = PROTOCOL
    def fmt_h(v): return '—' if v is None else (f'{v/1000:g} km' if v >= 1000 else f'{v:g} m')
    bound_rows = '\n'.join(f"| {b['band'].replace('_', ' ')} | {b['host_c']} | {b['chron_myr']} | {fmt_h(b['max_thickness_m_with_median_retention_ge_0.5'])} |" for b in bounds)
    sel = [r for r in rows if r['band'] == 'magnetite_430_580' and r['host_c'] == 300 and r['chron_myr'] == 0.67]
    ret_rows = '\n'.join(f"| {fmt_h(r['thickness_m'])} | {r['midplane_cooling_through_band_myr']:.4g} | {r['poisson_median']*100:.1f}% | {r['poisson_q05']*100:.1f}–{r['poisson_q95']*100:.1f}% | {r['periodic_median']*100:.2f}% |" for r in sel)
    stack_rows = '\n'.join(f"| {s['bodies']} | {s['emplacement_span_myr']} | {s['coherence_median']:.2f} | {s['coherence_rms']:.2f} | {s['reference_one_over_sqrt_n']:.2f} |" for s in stack)
    md = f'''# Rapidly cooled bodies under a reversing dynamo

**Status: declared-scenario calculation completed. Verdict: adds a constraint. Rapid cooling protects a single body from cancellation; a stack assembled over many chrons cancels anyway.** [Protocol](followup/bodies/protocol.json) · [Retention table](followup/bodies/retention.csv) · [Thickness bounds](followup/bodies/thickness_bounds.json) · [Stack table](followup/bodies/stack.csv) · [Manifest](followup/bodies/manifest.json)

## Why

Test 4 found that crust cooling conductively over hundreds of millions of years keeps about 2% of a steady record under randomly timed reversals every 0.67 Myr. The natural escape is a source that cooled within one chron: a sill, dyke or lava unit. This calculation asks how thick such a body can be, and whether many such bodies can add up to a strong coherent source. It is a declared physical scenario, not an inference about a particular Martian region.

## How

An infinite slab of thickness h at {p['emplacement_temperature_c']} °C is emplaced into a host at {', '.join(str(t) for t in p['host_temperatures_c'])} °C; it cools by conduction with diffusivity {p['diffusivity_m2_s']:g} m²/s and no latent heat (exact solution, Carslaw &amp; Jaeger 1959). Each of {p['positions']} positions across the half-slab acquires remanence while cooling through a uniform blocking band, {p['blocking_bands_c']['magnetite_430_580'][0]}–{p['blocking_bands_c']['magnetite_430_580'][1]} °C for magnetite and {p['blocking_bands_c']['pyrrhotite_175_325'][0]}–{p['blocking_bands_c']['pyrrhotite_175_325'][1]} °C for pyrrhotite. The body's kernel is integrated against periodic reversals ({p['periodic_phases']} phases) and Poisson reversals ({p['poisson_realizations']} seeds) with mean chrons of {', '.join(str(c) for c in p['chron_durations_myr'])} Myr; the retained fraction of a steady record is reported. A stack of N fully coherent bodies emplaced at random times within a span records the field sign at each emplacement (mean chron {p['stack']['chron_myr']} Myr, {p['stack']['realizations']} realizations). The protocol was saved before evaluation; it is a local declaration, not external preregistration.

## Result

### One body

Magnetite band, host at 300 °C, mean chron 0.67 Myr:

| Thickness | Mid-plane cooling through the band (Myr) | Poisson retention, median | Poisson 5–95% | Periodic retention, median |
| --- | ---: | ---: | ---: | ---: |
{ret_rows}

Largest declared thickness with median Poisson retention ≥ 50%:

| Band | Host (°C) | Mean chron (Myr) | Maximum thickness |
| --- | ---: | ---: | ---: |
{bound_rows}

### A stack of bodies

Mean chron 0.67 Myr, each body fully coherent:

| Bodies | Emplacement span (Myr) | Net coherence, median | Net coherence, RMS | 1/√N |
| ---: | ---: | ---: | ---: | ---: |
{stack_rows}

![Retention of one body against thickness, and net coherence of stacks](followup/bodies/bodies.png)

## Reading

Cooling time scales with the square of thickness, so a body a few kilometres thick cools through its blocking band in well under a chron of 0.67 Myr and keeps almost all of its record, while a body of ten kilometres or more approaches the conductive-crust regime of Test 4. Rapid cooling is therefore a real escape from cancellation, but only body by body. When a magnetized crust is built from many bodies emplaced over an interval longer than a chron, their polarities are set by the field at each emplacement and the stack cancels like 1/√N: a hundred sills emplaced under a dynamo reversing every 0.67 Myr retain (RMS) about a quarter of their summed magnetization when built over 10 Myr and about an eighth over 100 Myr, because emplacements closer than a chron share a polarity. A stack is coherent only if it was emplaced within a single chron or under a long-lived polarity.

The tension of Test 4 is thus sharpened rather than resolved. Under a frequently reversing dynamo, a strong coherent source over tens of kilometres of crust requires either emplacement of most of its volume within one chron, or a period of stable polarity long enough to cover its construction, or a magnetization per body so high that a tenth of it still meets the budget of Test 3. Each of these is a statement about the dynamo's reversal history at the time the southern crust was built, which is what the follow-up on reversal statistics (protocol 1) would have to address.

## Limits

No latent heat, no host cooling with depth, no chemical remanence, no shock, uniform blocking band, infinite slab geometry, no forward field at orbital altitude. The stack model assumes independent random emplacement times and equal bodies. The thicknesses and chrons are declared scenarios. Ogawa &amp; Manga (2007) and earlier dyke-source models treat related geometries; their results were not reproduced and no novelty is claimed.

## Reproduce

```bash
python scripts/followup/rapid_bodies.py
python -m pytest -q tests/test_rapid_bodies.py
python scripts/research/render_docs.py
```
'''
    (ROOT/'research/RAPID_BODIES.md').write_text(md)


if __name__ == '__main__':
    main()
