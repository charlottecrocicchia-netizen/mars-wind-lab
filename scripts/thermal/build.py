"""Reproduce the small thermal experiment offline from its synthetic protocol."""
import csv
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
import numpy as np
import scipy

from marswind.thermal import Column, HeatPulse, eigenmode_benchmark, solve, steady_temperature

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/thermal"
PROTOCOL = json.loads((OUT / "protocol.json").read_text())


def run_case(column, step, case):
    q, h = PROTOCOL['basal_flux'], PROTOCOL['heat_production']
    return solve(column, PROTOCOL['duration_myr'], step,
                 lambda t: q['asymptote_w_m2'] + (q['initial_w_m2']-q['asymptote_w_m2'])*np.exp(-t/q['decay_time_myr']),
                 lambda t: h['initial_w_m3']*2**(-t/h['effective_half_life_myr']),
                 steady_temperature(column, q['initial_w_m2'], h['initial_w_m3']),
                 tuple(HeatPulse(**p) for p in case['pulses']),
                 pulse_step_myr=PROTOCOL['pulse_step_myr']*step/PROTOCOL['step_myr'],
                 pulse_window_myr=PROTOCOL['pulse_window_myr'])


def classify(temperature, future_peak, threshold):
    # No likelihood: 0 avoids this gate, 1 is excluded later, 2 is too hot now.
    return np.where(temperature >= threshold, 2, np.where(future_peak >= threshold, 1, 0)).astype(np.uint8)


def main():
    column = Column(**PROTOCOL['column'])
    step = PROTOCOL['step_myr']
    steady = steady_temperature(column, .03, 4e-8)
    steady_run = solve(column, 100., step, lambda t: .03, lambda t: 4e-8, steady)
    validation = {
        'scope': 'Numerical verification against exact solutions and a finer grid; not geological validation',
        'steady_max_error_k': float(np.max(np.abs(steady_run.temperature_k-steady))),
        'transient_initial_anomaly_k': 100.,
        'transient_max_error_k': eigenmode_benchmark(column.cells, step),
        'transient_time_refinement': [
            {'step_myr': dt, 'max_error_k': eigenmode_benchmark(400, dt)} for dt in [.5, .25, .125]
        ],
        'refined_cells': column.cells*2,
        'refined_step_myr': step/2,
        'refined_pulse_step_myr': PROTOCOL['pulse_step_myr']/2,
        'scenario_comparisons': [],
    }
    results = {'schema_version': 1, 'language': 'en', 'protocol': PROTOCOL,
               'validation': validation, 'scenarios': [],
               'gate_codes': {'0': 'Ordering threshold never reached from this time onward; survival unresolved',
                              '1': 'Below threshold now, but reaches it later; older component thermally excluded',
                              '2': 'At or above ordering threshold at this time'},
               'provenance': {
                   'sha256': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [
                       'src/marswind/thermal.py', 'scripts/thermal/build.py',
                       'research/thermal/protocol.json', 'tests/test_thermal.py']},
                   'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__, 'matplotlib': matplotlib.__version__},
                   'command': 'python scripts/thermal/build.py',
                   'downloads_required': False,
                   'display_sampling': '10 Myr normally, 0.125 Myr within 5 Myr of each pulse, 1 Myr for the next 95 Myr; all depth nodes. Future peaks computed at every integration step before thinning.'}}
    profile_rows, window_rows = [], []
    for case in PROTOCOL['scenarios']:
        history = run_case(column, step, case)
        future = history.future_peak_k()
        refined = run_case(replace(column, cells=column.cells*2), step/2, case)
        matching = np.searchsorted(refined.time_myr, history.time_myr)
        np.testing.assert_array_equal(refined.time_myr[matching], history.time_myr)
        validation['scenario_comparisons'].append({
            'id': case['id'],
            'max_temperature_difference_k': float(np.max(np.abs(history.temperature_k-refined.temperature_k[matching, ::2]))),
            'max_future_peak_difference_k': float(np.max(np.abs(future-refined.future_peak_k()[matching, ::2]))),
            'interpretation': 'Deterministic numerical difference, not a geological uncertainty interval'})
        del refined
        display_times = set(np.arange(0, PROTOCOL['duration_myr']+10, 10.))
        for pulse in case['pulses']:
            event = pulse['time_myr']
            display_times.update(np.arange(max(0, event-5), min(PROTOCOL['duration_myr'], event+5)+step, step))
            display_times.update(np.arange(event, min(PROTOCOL['duration_myr'], event+100)+1, 1.))
        display_times = np.array(sorted(display_times))
        indices = np.searchsorted(history.time_myr, display_times)
        np.testing.assert_array_equal(history.time_myr[indices], display_times)
        gates = {g['id']: classify(history.temperature_k[indices], future[indices], g['temperature_k']).tolist()
                 for g in PROTOCOL['ordering_thresholds']}
        results['scenarios'].append({
            'id': case['id'], 'label': case['label'], 'time_myr': history.time_myr[indices].tolist(),
            'depth_km': (history.depth_m/1000).tolist(),
            'temperature_k': np.round(history.temperature_k[indices], 3).tolist(),
            'future_peak_k': np.round(future[indices], 3).tolist(), 'gates': gates,
            'pulses': history.pulses,
            'maximum_temperature_k': float(history.temperature_k.max()),
            'minimum_temperature_k': float(history.temperature_k.min()),
        })
        for time in [0., 500., 1000., 1100., 4000.]:
            i = np.searchsorted(history.time_myr, time)
            for j, depth in enumerate(history.depth_m/1000):
                profile_rows.append([case['id'], time, depth, round(history.temperature_k[i, j], 6), round(future[i, j], 6)])
        for gate in PROTOCOL['ordering_thresholds']:
            for depth in [5., 15., 25., 35., 45.]:
                j = round(depth*1000/(column.thickness_m/column.cells))
                allowed = np.flatnonzero(future[:, j] < gate['temperature_k'])
                first = float(history.time_myr[allowed[0]]) if len(allowed) else None
                window_rows.append([case['id'], gate['id'], depth, first,
                                    'No later ordering-temperature crossing; acquisition and survival remain unresolved'])
    print(json.dumps(validation, indent=2))
    if validation['steady_max_error_k'] > 1e-7 or validation['transient_max_error_k'] > .08:
        raise RuntimeError('Analytic validation tolerance exceeded')
    if max(v['max_temperature_difference_k'] for v in validation['scenario_comparisons']) > 2.:
        raise RuntimeError('Refinement difference exceeds the 2 K display tolerance; refine the protocol')
    (OUT/'results.json').write_text(json.dumps(results, separators=(',', ':'), allow_nan=False)+'\n')
    for name, header, rows in [
        ('profiles.csv', ['scenario','elapsed_time_myr','depth_km','temperature_k','future_peak_k'], profile_rows),
        ('windows.csv', ['scenario','ordering_endmember','depth_km','earliest_sampled_compatible_time_myr','qualification'], window_rows)
    ]:
        with (OUT/name).open('w', newline='') as f:
            writer = csv.writer(f, lineterminator='\n'); writer.writerow(header); writer.writerows(rows)
    figure(results)
    print('Saved project-generated results and figures to research/thermal; no downloads.')


def figure(results):
    plt.rcParams.update({'font.size': 10, 'svg.hashsalt': 'mars-thermal-experiment'})
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 9), layout='constrained', sharex=True, sharey=True)
    colors = ListedColormap(['#5eaca4', '#d7825b', '#454c58'])
    for col, case in enumerate(results['scenarios']):
        t, z = np.array(case['time_myr'])/1000, case['depth_km']
        thermal = axes[0, col].pcolormesh(t, z, np.array(case['temperature_k']).T-273.15, shading='nearest', cmap='magma', vmin=-55, vmax=725, rasterized=True)
        axes[0, col].contour(t, z, np.array(case['temperature_k']).T, levels=[853.15], colors=['white'], linewidths=.8)
        gate = axes[1, col].pcolormesh(t, z, np.array(case['gates']['magnetite']).T, shading='nearest', cmap=colors, norm=BoundaryNorm([-.5,.5,1.5,2.5], 3), rasterized=True)
        axes[0, col].set_title(case['label'], weight='bold')
        if case['pulses']:
            inset = axes[0, col].inset_axes([.56, .14, .39, .37])
            inset.pcolormesh(np.array(case['time_myr']), z, np.array(case['temperature_k']).T-273.15,
                            shading='nearest', cmap='magma', vmin=-55, vmax=725, rasterized=True)
            inset.contour(np.array(case['time_myr']), z, np.array(case['temperature_k']).T,
                          levels=[853.15], colors=['white'], linewidths=.7)
            inset.set(xlim=(999, 1003), ylim=(35, 15), xticks=[1000,1002], yticks=[15,25,35])
            inset.tick_params(labelsize=8, colors='white')
            inset.set_title('Pulse detail · depth 15–35 km', fontsize=8, color='white')
            inset.set_xlabel('Elapsed time (Myr)', fontsize=8, color='white')
            for spine in inset.spines.values():
                spine.set_edgecolor('white')
        axes[1, col].set_xlabel('Candidate recording time (Gyr elapsed)')
        for row in [0, 1]:
            axes[row, col].set_ylim(50, 0)
            axes[row, col].set_xlim(0, 4)
            if case['pulses']:
                axes[row, col].axvline(1., color='#2f2f2f', ls='--', lw=.8)
    for row in [0, 1]:
        axes[row, 0].set_ylabel('Depth below surface (km)')
    fig.colorbar(thermal, ax=axes[0, :], label='Temperature (°C); white line = 580 °C', shrink=.85)
    bar = fig.colorbar(gate, ax=axes[1, :], ticks=[0,1,2], shrink=.85)
    bar.ax.set_yticklabels(['No crossing*', 'Later crossing', 'Too hot now'])
    fig.suptitle('A thermal history can exclude an ancient magnetic record\nControlled 1-D experiment · no Martian region fitted', fontsize=16, weight='bold')
    fig.supxlabel('Bottom panels: ordering-temperature gate at 580 °C (magnetite endmember).\n*No crossing permits further testing; it does not demonstrate acquisition or survival.\nTime is elapsed model time, not a measured Martian age. Dashed line: imposed heat pulse.', fontsize=10)
    fig.savefig(OUT/'thermal_history.png', dpi=180, metadata={'Software':'Mars dichotomy research — original numerical experiment'})
    fig.savefig(OUT/'thermal_history.svg', metadata={'Date': None, 'Creator': 'Mars dichotomy research'})
    svg = OUT/'thermal_history.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)


if __name__ == '__main__':
    main()
