"""Rapidly cooled bodies under a reversing dynamo: frozen protocol, then evaluation.

Usage: python scripts/followup/rapid_bodies.py
No external data is read: the calculation is a declared physical scenario
(slab cooling, blocking band, reversal statistics) whose purpose is to test
retention at declared body thicknesses and emplacement spans. Outputs go
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
from marswind.rapid_bodies import body_kernels, body_retention, stack_coherence, max_thickness_for_retention, midplane_crossing_times, expected_stack_rms

OUT = ROOT/'research/followup/bodies'
OUT.mkdir(parents=True, exist_ok=True)
SEED = 20260928

PROTOCOL = json.loads((OUT/'protocol.json').read_text())


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
    p = PROTOCOL; started = datetime.now(timezone.utc).isoformat()
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
                    rows.append({'band': band_name, 'host_c': host, 'thickness_m': h, 'midplane_cooling_through_band_myr': cooling, **midplane_crossing_times(h, p['emplacement_temperature_c']+273.15, host+273.15, p['diffusivity_m2_s'], band), 'known_fraction': known, 'chron_myr': c,
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
                          'coherence_rms': float(np.sqrt(np.mean(vals**2))), 'reference_one_over_sqrt_n': 1/np.sqrt(n), 'analytic_coherence_rms': expected_stack_rms(n,span,p['stack']['chron_myr'])})
    csv_save('stack.csv', stack)
    summary = {'field_evaluation_started_utc': started, 'bounds': bounds, 'stack': stack,
               'scope': 'Declared slab and stack scenarios; inequalities conditional on the stated physics. No Martian body thickness or emplacement history is inferred.'}
    save('summary.json', summary)
    figure(rows, stack)
    save('manifest.json', {'generated_utc': datetime.now(timezone.utc).isoformat(), 'code_sha256': {'src/marswind/rapid_bodies.py': sha(ROOT/'src/marswind/rapid_bodies.py'), 'src/marswind/recording.py': sha(ROOT/'src/marswind/recording.py'), 'scripts/followup/rapid_bodies.py': sha(Path(__file__))},
                           'outputs_sha256': {x.name: sha(x) for x in sorted(OUT.iterdir()) if x.is_file() and x.name != 'manifest.json'},
                           'software': {'python': platform.python_version(), 'numpy': np.__version__, 'matplotlib': matplotlib.__version__}})
    report(rows, bounds, stack)
    manifest = json.loads((OUT/'manifest.json').read_text())
    manifest['report_sha256'] = sha(ROOT/'research/RAPID_BODIES.md')
    save('manifest.json', manifest)
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
    fig.suptitle('Single-body retention and correlated-polarity stacks · declared scenarios', fontsize=11)
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

**Status: declared-scenario calculation completed. Verdict: adds a constraint. Rapid cooling can protect one body; stack cancellation depends on the shared field and emplacement span.** [Protocol](followup/bodies/protocol.json) · [Retention table](followup/bodies/retention.csv) · [Thickness bounds](followup/bodies/thickness_bounds.json) · [Stack table](followup/bodies/stack.csv) · [Manifest](followup/bodies/manifest.json)

## Why

Test 4 found that crust cooling conductively over hundreds of millions of years keeps about 2% of a steady record under randomly timed reversals every 0.67 Myr. The natural escape is a source that cooled within one chron: a sill, dyke or lava unit. This calculation asks how thick such a body can be, and whether many such bodies can add up to a strong coherent source. It is a declared physical scenario, not an inference about a particular Martian region.

## How

An infinite planar slab of thickness h at {p['emplacement_temperature_c']} °C is emplaced into a host at {', '.join(str(t) for t in p['host_temperatures_c'])} °C; it cools by conduction with diffusivity {p['diffusivity_m2_s']:g} m²/s and no latent heat (analytic heat-kernel solution; recording kernels use piecewise-linear temperature interpolation). Each of {p['positions']} positions across the half-slab acquires remanence while cooling through a uniform blocking band, {p['blocking_bands_c']['magnetite_430_580'][0]}–{p['blocking_bands_c']['magnetite_430_580'][1]} °C for magnetite and {p['blocking_bands_c']['pyrrhotite_175_325'][0]}–{p['blocking_bands_c']['pyrrhotite_175_325'][1]} °C for pyrrhotite. The body's kernel is integrated against periodic reversals ({p['periodic_phases']} phases) and Poisson reversals ({p['poisson_realizations']} seeds) with mean chrons of {', '.join(str(c) for c in p['chron_durations_myr'])} Myr; the retained fraction of a steady record is reported. A stack of N fully coherent bodies emplaced at random times within a span records the field sign at each emplacement (mean chron {p['stack']['chron_myr']} Myr, {p['stack']['realizations']} realizations). The protocol was saved before evaluation; it is a local declaration, not external preregistration.

## Result

### One body

Magnetite band, host at 300 °C, mean chron 0.67 Myr:

| Thickness | Mid-plane cooling through the band (Myr) | Poisson retention, median | Poisson 5–95% | Periodic retention, median |
| --- | ---: | ---: | ---: | ---: |
{ret_rows}

Largest declared thickness with median Poisson retention ≥ 50%:

| Band | Host (°C) | Mean chron (Myr) | Largest passing tested thickness |
| --- | ---: | ---: | ---: |
{bound_rows}

### A stack of bodies

Mean chron 0.67 Myr, each body fully coherent:

| Bodies | Emplacement span (Myr) | Net coherence, median | Net coherence, RMS | 1/√N |
| ---: | ---: | ---: | ---: | ---: |
{stack_rows}

![Retention of one body against thickness, and net coherence of stacks](followup/bodies/bodies.png)

## Reading

The 3 km body in the primary case crosses the mid-plane blocking band in **0.853 Myr**, longer than a 0.67 Myr mean chron, and retains **76%** at the simulated median. The 1 km body crosses in 0.0948 Myr. These are scenario results, not universal thickness cutoffs. Each tabulated thickness limit is the largest **tested** value meeting the median criterion; a passing 30 km case only reaches the top of the tested grid. The continuous threshold and its Monte Carlo uncertainty were not estimated.

The bodies share one telegraph field, so independent emplacement times do not imply independent polarities. For N equal instantaneous recorders distributed uniformly over a span T, let x = 2T/τ, with mean chron τ. The telegraph correlation is derived in the [KTH stochastic-process notes, section 12.5.3](https://www.math.kth.se/matstat/gru/sf2940/lectnotemat5.pdf) (the relevant derivation was consulted; no code or data copied). Directly integrating E[S(t)S(s)] = exp(−2|t−s|/τ) over the two independent uniform emplacement times gives:

```text
A = 2 * (x - 1 + exp(-x)) / x²
RMS² = 1/N + (1 - 1/N)*A
```

The limit 1/√N applies when the correlation term is negligible, approximately **T ≫ Nτ**, not merely T ≫ τ. At fixed span, increasing N leaves a nonzero correlation floor. For N = 100 and τ = 0.67 Myr the analytic RMS is **0.272 at 10 Myr** and **0.129 at 100 Myr**, consistent with the simulation. The corresponding simulated medians are 0.20 and 0.08; RMS and median must not be interchanged. Favorable stochastic histories can retain a record across multiple chrons, so single-chron emplacement is not a necessary condition for every realization.

This is a retention calculation for equal sources, not an orbital-field inversion for a crustal stack. Source geometry, volume, carrier efficiency, emplacement history and reversal history remain coupled. None of these results alone requires a change in the dynamo rate or makes reversal inference the only possible next calculation. The subsequent [synthetic identifiability prerequisite](REVERSAL_IDENTIFIABILITY.md) tests one explicit rate–recording ambiguity before any observed-map inference.

### Corrections following the implementation review

The initial cooling column reported elapsed time from emplacement to a sampled point near the lower band boundary. It now reports the analytic difference between both crossing times; both absolute crossing times are saved in the CSV. Retention kernels and their simulated fractions are unchanged. The stack CSV now includes the exact correlated-field RMS for comparison. The original protocol timestamp is preserved when rebuilding. Earlier files and hashes are retained under `followup/bodies_audit/before/`. The original Carslaw & Jaeger section number has not been independently checked; the formula is verified against the heat-kernel expression and analytic inversion instead.

## Limits

No latent heat, no host cooling with depth, no chemical remanence, no shock, uniform blocking band, infinite slab geometry, no forward field at orbital altitude. The stack model assumes independent random emplacement times and equal bodies, whose polarities are correlated through one shared field. It uses the instantaneous-recording limit; finite cooling and mutual reheating within a stack are not coupled. The thicknesses and chrons are declared scenarios. Ogawa &amp; Manga (2007) and earlier dyke-source models treat related geometries; their results were not reproduced and no novelty is claimed.

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
