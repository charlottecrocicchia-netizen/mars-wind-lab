"""Run the frozen synthetic prerequisite, without fitting any Mars field map."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'reversal-identifiability-v1'
import matplotlib.pyplot as plt
import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from marswind.rapid_bodies import body_kernels
from marswind.reversal_identifiability import (
    PiecewiseClock, warp_kernel, poisson_hazard_events, record_explicit_events,
    radial_dipole_operator, flip_probability, fit_dated_signs, profile_unknown_spacing,
)

OUT = ROOT/'research/followup/reversal'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clean(value):
    if isinstance(value, dict): return {k: clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)): return [clean(v) for v in value]
    if isinstance(value, (bool, np.bool_)): return bool(value)
    if isinstance(value, (int, np.integer)): return int(value)
    if isinstance(value, (float, np.floating)): return float(value) if np.isfinite(value) else None
    return value


def save(name, value):
    (OUT/name).write_text(json.dumps(clean(value), indent=2, allow_nan=False)+'\n')


def csv_save(name, rows):
    with (OUT/name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(clean(rows))


def cartesian(lat, lon, radius_m):
    lat, lon = np.deg2rad(lat), np.deg2rad(lon)
    return radius_m*np.column_stack([np.cos(lat)*np.cos(lon), np.cos(lat)*np.sin(lon), np.sin(lat)])


def counterexample(p):
    clock = PiecewiseClock(p['switch_time_myr'], *p['rates_per_myr'], p['constant_rate_per_myr'])
    rng = np.random.default_rng(p['seed'])
    sources, kernels, pushed = [], [], []
    for i in range(p['sources']):
        h = float(rng.choice(p['cooling_thicknesses_m']))
        age = float(rng.uniform(*p['emplacement_ranges_myr'][i//(p['sources']//2)]))
        local, _ = body_kernels(h, p['emplacement_c']+273.15, p['host_c']+273.15,
                               p['diffusivity_m2_s'], np.array(p['blocking_band_c'])+273.15,
                               p['positions'], p['time_points'])
        kernel = {key: np.concatenate([k[key] for k in local]) for key in ('start', 'end', 'weight')}
        kernel['start'] += age
        kernel['end'] += age
        kernel['weight'] /= len(local)
        mapped = warp_kernel(kernel, clock)
        if kernel['end'].max() > p['activity_window_myr'][1]:
            raise ValueError('Declared continuously active example does not cover the full kernel')
        kernels.append(kernel)
        pushed.append(mapped)
        entirely_early = kernel['end'].max() < clock.switch_myr
        entirely_late = kernel['start'].min() > clock.switch_myr
        if not (entirely_early or entirely_late):
            raise ValueError('This example requires each cooling body to lie within one rate segment')
        slope = (clock.early_rate if entirely_early else clock.late_rate)/clock.reference_rate
        sources.append({'source': i, 'latitude': float(rng.uniform(-60, 60)), 'longitude': float(rng.uniform(0, 360)),
                        'depth_km': 20., 'emplacement_myr': age, 'thickness_m': h,
                        'warped_emplacement_myr': float(clock.warp(age)), 'warped_effective_thickness_m': h*np.sqrt(slope),
                        'acquired_mass': float(kernel['weight'].sum()), 'clock_slope': slope})
    csv_save('sources.csv', sources)
    source_xyz = cartesian([s['latitude'] for s in sources], [s['longitude'] for s in sources], (3389.5-20)*1000)
    lon, lat = np.meshgrid(np.arange(0, 360, p['observation_longitudes_step_deg']), p['observation_latitudes'])
    operators = {height: radial_dipole_operator(source_xyz, cartesian(lat.ravel(), lon.ravel(), (3389.5+height)*1000))
                 for height in p['altitudes_km']}
    checks, records, first_maps = [], [], []
    source_max_error = 0.
    for run in range(p['realizations']):
        path_rng = np.random.default_rng(np.random.SeedSequence([p['seed'], 1, run]))
        events_h = poisson_hazard_events(float(clock.hazard(p['activity_window_myr'][1])), path_rng)
        events_t = clock.inverse_hazard(events_h)
        events_u = events_h/clock.reference_rate
        a = np.array([record_explicit_events(k, events_t, p['activity_window_myr'], 1-2*(run % 2)) for k in kernels])
        b = np.array([record_explicit_events(k, events_u, clock.warp(p['activity_window_myr']), 1-2*(run % 2)) for k in pushed])
        source_max_error = max(source_max_error, float(np.max(np.abs(a-b))))
        for i, (v, w) in enumerate(zip(a, b)):
            records.append({'realization': run, 'source': i, 'changing_rate_record': v, 'constant_rate_warped_record': w})
        for height, operator in operators.items():
            ba, bb = operator@a*p['moment_scale_a_m2'], operator@b*p['moment_scale_a_m2']
            signal_norm = np.linalg.norm(ba)
            for noise in p['noise_nT']:
                noise_rng = np.random.default_rng(np.random.SeedSequence([p['seed'], 2, run, int(height), int(noise)]))
                shared = noise_rng.normal(0, noise, len(ba))
                noisy_a, noisy_b = ba+shared, bb+shared
                checks.append({'realization': run, 'altitude_km': height, 'noise_nt': noise,
                               'signal_relative_l2_error': np.linalg.norm(ba-bb)/signal_norm,
                               'signal_max_abs_error_nt': float(np.max(np.abs(ba-bb))),
                               'paired_noisy_max_abs_error_nt': float(np.max(np.abs(noisy_a-noisy_b))),
                               'signal_rms_nt': float(np.sqrt(np.mean(ba**2)))})
                if run == 0:
                    for j in range(len(ba)):
                        first_maps.append({'latitude': lat.ravel()[j], 'longitude': lon.ravel()[j], 'altitude_km': height,
                                           'noise_nt': noise, 'changing_nt': noisy_a[j], 'constant_warped_nt': noisy_b[j]})
    csv_save('record_checks.csv', records)
    csv_save('map_checks.csv', checks)
    csv_save('example_maps.csv', first_maps)
    maximum = max(row['signal_relative_l2_error'] for row in checks)
    return {'global_identifiability_fails_in_declared_class': maximum <= 1e-10,
            'max_relative_map_error': maximum, 'max_absolute_map_error_nt': max(r['signal_max_abs_error_nt'] for r in checks),
            'max_absolute_record_error': source_max_error, 'realizations': p['realizations'],
            'changing_activity_window_myr': p['activity_window_myr'],
            'constant_activity_window_myr': clock.warp(p['activity_window_myr'])}, first_maps


def dated_control(p):
    summaries, calibration, profile_rows, arrays = [], [], [], {}
    for ni, n in enumerate(p['intervals_per_segment']):
        quantiles = []
        for ri, rate in enumerate(p['rates_null_per_myr']):
            rng = np.random.default_rng(np.random.SeedSequence([p['seed_calibration'], ni, ri]))
            counts = rng.binomial(n, flip_probability(rate, p['spacing_myr']), (p['calibration_draws_per_null'], 2))
            lr = fit_dated_signs(counts, n, p['spacing_myr'])['lr']
            cutoff = float(np.quantile(lr, 1-p['alpha']))
            quantiles.append(cutoff)
            calibration.append({'intervals_per_segment': n, 'null_rate': rate, 'lr_q95': cutoff})
            arrays[f'calibration_n{n}_r{ri}_counts'] = counts
        threshold = max(quantiles)
        cases = [('constant', [r, r]) for r in p['rates_null_per_myr']]
        cases += [('change', rates) for rates in p['rates_change_per_myr']]
        for ci, (truth, rates) in enumerate(cases):
            rng = np.random.default_rng(np.random.SeedSequence([p['seed_heldout'], ni, ci]))
            counts = rng.binomial(n, flip_probability(rates, p['spacing_myr']), (p['heldout_draws_per_case'], 2))
            fit = fit_dated_signs(counts, n, p['spacing_myr'])
            detected = fit['lr'] > threshold
            arrays[f'heldout_n{n}_c{ci}_counts'] = counts
            row = {'intervals_per_segment': n, 'truth': truth, 'rate_early': rates[0], 'rate_late': rates[1],
                   'lr_threshold': threshold, 'draws': len(counts), 'called_change': int(detected.sum()),
                   'called_constant': int((~detected).sum()), 'fraction_called_change': float(detected.mean())}
            for j, segment in enumerate(['early', 'late']):
                for label, val in zip(['q05', 'median', 'q95'], np.quantile(fit['rates'][:, j], [.05, .5, .95])):
                    row[f'fitted_{segment}_rate_{label}'] = val
                row[f'{segment}_infinite_mle_count'] = int(np.isinf(fit['rates'][:, j]).sum())
            summaries.append(row)
            if n == 1000 and rates == [.15, 1.5]:
                profile = profile_unknown_spacing(counts, n)
                for draw in range(len(counts)):
                    profile_rows.append({'draw': draw, 'early_count': counts[draw, 0], 'late_count': counts[draw, 1],
                                         'ridge_inside_clock_bounds': profile['feasible'][draw],
                                         'common_rate': profile['common_rate'][draw], 'spacing_early_myr': profile['spacings'][draw, 0],
                                         'spacing_late_myr': profile['spacings'][draw, 1],
                                         'll_change': fit['ll_change'][draw], 'll_constant_unknown_clock': profile['ll_profile'][draw]})
    csv_save('classification.csv', summaries)
    csv_save('calibration.csv', calibration)
    csv_save('unknown_clock_profile.csv', profile_rows)
    np.savez_compressed(OUT/'trial_counts.npz', **arrays)
    main = next(row for row in summaries if row['intervals_per_segment'] == 1000 and row['rate_early'] == .15 and row['rate_late'] == 1.5)
    max_fp = max(row['fraction_called_change'] for row in summaries if row['intervals_per_segment'] == 1000 and row['truth'] == 'constant')
    return {'primary_power': main['fraction_called_change'], 'primary_max_false_positive': max_fp,
            'positive_control_passes': main['fraction_called_change'] >= .8 and max_fp <= .075,
            'profile_equivalent_draws': sum(r['ridge_inside_clock_bounds'] for r in profile_rows),
            'profile_total_draws': len(profile_rows)}, summaries


def figure(maps, classifications):
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), layout='constrained')
    rr = [r for r in maps if r['altitude_km'] == 150 and r['noise_nt'] == 0]
    lon, lat = [r['longitude'] for r in rr], [r['latitude'] for r in rr]
    value = np.array([r['changing_nt'] for r in rr])
    image = axes[0, 0].scatter(lon, lat, c=value, cmap='RdBu_r', vmin=-max(abs(value)), vmax=max(abs(value)), marker='s', s=25)
    fig.colorbar(image, ax=axes[0, 0], label='Synthetic radial field (nT)')
    axes[0, 0].set(title='Two histories, one map · 150 km', xlabel='Longitude (°)', ylabel='Latitude (°)')
    axes[0, 1].scatter(value, [r['constant_warped_nt'] for r in rr], s=10, color='#167d8d')
    axes[0, 1].plot([min(value), max(value)], [min(value), max(value)], 'k:', lw=1)
    axes[0, 1].set(title='Equality before adding noise', xlabel='Changing rate, original clocks (nT)', ylabel='Constant rate, transformed clocks (nT)')
    for n, color in [(100, '#bd662f'), (1000, '#167d8d')]:
        alt = [r for r in classifications if r['intervals_per_segment'] == n and r['truth'] == 'change']
        axes[1, 0].plot(range(len(alt)), [r['fraction_called_change'] for r in alt], 'o-', color=color, label=f'{n} dated intervals / segment')
        null = [r for r in classifications if r['intervals_per_segment'] == n and r['truth'] == 'constant']
        axes[1, 1].plot([r['rate_early'] for r in null], [r['fraction_called_change'] for r in null], 'o-', color=color, label=f'n = {n}')
    axes[1, 0].set_xticks(range(4), ['0.15 → 1.5', '1.5 → 0.15', '0.5 → 1.5', '1 → 1.5'])
    axes[1, 0].set(title='Known acquisition clocks: held-out power', ylabel='Fraction called a rate change', xlabel='True rates (reversals / Myr)', ylim=(0, 1.04))
    axes[1, 0].legend(fontsize=8)
    axes[1, 1].axhline(.05, color='gray', ls=':', label='Nominal 5%')
    axes[1, 1].set(title='Held-out false positives', xlabel='True constant rate (reversals / Myr)', ylabel='Fraction called a rate change', ylim=(0, .10))
    axes[1, 1].legend(fontsize=8)
    fig.suptitle('Synthetic prerequisite only — no Martian reversal chronology inferred', fontsize=13)
    fig.savefig(OUT/'identifiability.png', dpi=180)
    fig.savefig(OUT/'identifiability.svg', metadata={'Date': None})
    plt.close(fig)


def report(s, rows):
    c, d = s['counterexample'], s['dated_control']
    table = '\n'.join(f"| {r['intervals_per_segment']} | {r['rate_early']:g} → {r['rate_late']:g} | {r['fraction_called_change']:.1%} | {r['fitted_early_rate_median']:.3f} / {r['fitted_late_rate_median']:.3f} |" for r in rows if r['truth'] == 'change')
    text = f'''# Reversal histories and acquisition clocks

**Synthetic prerequisite · 28 September 2026.** The declared flexible recording model fails global identifiability: distinct reversal histories can produce the same source moments and orbital observations. A separate positive control succeeds when acquisition times are known. No observed Mars magnetic map is fitted, and no transition age or preferred dynamo history is inferred.

## Why

[Slow cooling](DISCRIMINATING_TESTS.md) and [rapid bodies](RAPID_BODIES.md) show that reversal statistics and recording duration jointly determine cancellation. Before interpreting a coherent magnetic patch as a long chron, we must test whether recording histories can mimic a rate change. The earlier [proposal](NEXT_TEST_PROTOCOLS.md) required this gate before any map interpretation. The [machine protocol](followup/reversal/protocol.json) was saved before these numerical trials; the analytic time-change argument and the preceding body results were already known. This is an internal protocol, not an external preregistration.

## How

We compare rates of 0.15 then 1.5 reversals/Myr, changing at elapsed time 100 Myr, with a constant 1.5 reversals/Myr. Both families permit the same nuisance class: positive piecewise-affine acquisition clocks with slopes 0.1–10, moment scales 0.5–2 and activity windows transformed with the clock. The main example uses unit moment scale and a continuously active window. Geometry is fixed between the two descriptions.

Let H(t) be integrated reversal rate and set u(t) = H(t)/1.5. Unit-rate Poisson arrivals in H generate one shared path. The constant-rate path at u(t) has exactly the same sign as the changing-rate path at t. Moving each acquisition interval to the u clock and preserving its mass therefore gives **the same signed remanence for every realization**. Intervals crossing the rate break are split before transformation. The field's active window is transformed too: 0–200 Myr becomes 0–110 Myr. This is a comparison of distinct physical histories when absolute acquisition ages and the activity duration are unknown, not a change of coordinates with externally fixed dates silently discarded.

The construction is a direct application of the established time-rescaling property of Poisson processes; see [Brown et al. (2002), author-hosted manuscript](https://www.stat.cmu.edu/~kass/papers/rescaling.pdf), introduction and theorem. The implementation and acquisition-integral derivation here are original. We use a finite-horizon coupling, not a goodness-of-fit test on censored interarrival times. No novelty is claimed.

The numerical check uses 24 bodies with slab acquisition kernels (1, 3 or 10 km effective thickness; 300 °C host; 430–580 °C blocking band), 128 shared field realizations, and 264 radial observations at each of 150 and 400 km. Within the early segment, shrinking time by 0.1 is also the conductive time scale of a slab thinner by √0.1: 3 km becomes 0.949 km. Each example kernel lies wholly within one segment. The orbital operator consists of z-directed point dipoles at 20 km depth, with 10¹⁴ A m² reference moments. It is a linear synthetic basis: thermal thickness, finite source geometry, density and moment are **not** jointly constrained by a physical body inversion.

## Result

Across all {c['realizations']} realizations, the largest signed-record difference is {c['max_absolute_record_error']:.2e}. The largest relative map difference is {c['max_relative_map_error']:.2e}; the largest absolute difference is {c['max_absolute_map_error_nt']:.2e} nT. This passes the declared equality tolerance of 10⁻¹⁰. Adding the same 0, 1 or 5 nT Gaussian noise to each equivalent pair preserves equality of their observation laws. Shared noise is a coupling demonstration; it does not claim that two independent noisy observations would be pixel-identical. These noise levels are scenarios, not Langlais coefficient uncertainties.

![Synthetic map equality and independently calibrated dated-sign controls](followup/reversal/identifiability.png)

### Positive control: independently known acquisition times

We simulate instantaneous, noiseless polarity samples at a known 0.1 Myr spacing, in two segments whose boundary is known. The sign-change probability is p = (1 − exp(−2λΔt))/2, allowing unobserved even numbers of reversals. A binomial likelihood fits either one shared rate or two rates, with the same probability bounds. The cutoff is calibrated using 4,000 simulations at each of five null rates, taking the largest 95th percentile; classification uses a strict exceedance. Separate seeds supply 4,000 held-out trials per case.

| Intervals per segment | True rates, /Myr | Held-out detection | Median fitted early / late rate |
|---:|---:|---:|---:|
{table}

For the declared primary case (1,000 intervals per segment, 0.15 → 1.5/Myr), power is **{d['primary_power']:.1%}**, and the largest held-out false-positive fraction over the null grid is **{d['primary_max_false_positive']:.1%}**. The positive control {'passes' if d['positive_control_passes'] else 'fails'} its rule. These are simulation frequencies under ideal dated sampling, not performance estimates for available Mars maps. Sampling uncertainty for a 5% frequency with 4,000 trials is about 0.35 percentage points (one standard error).

### Releasing the clock restores the ambiguity

The dated-sign likelihood depends on λΔt. A constant rate of 1.5/Myr sampled with early spacing 0.01 Myr and late spacing 0.1 Myr has exactly the same probabilities as the primary changing-rate case sampled at 0.1 Myr throughout. We also profile the held-out primary counts: allowing each spacing to lie in 0.01–1 Myr, a common-rate ridge attains the two-rate maximum likelihood in **{d['profile_equivalent_draws']} of {d['profile_total_draws']} trials**. The [profile table](followup/reversal/unknown_clock_profile.csv) records rates, spacings and both likelihoods. A row outside the feasible ridge would be marked unresolved by this analytic profiling step. No arbitrary classifier is assigned a chance-level score.

## Verdict

**The gate to observed-map inference is closed for this nuisance class.** A counterexample disproves global uniqueness in that class, even before orbital smoothing or noise. Fitting correlation lengths or connected-sign areas cannot distinguish this pair: the entire synthetic fields agree. This does not show that all rate changes are indistinguishable in every physical model, or that existing public evidence can never help.

The dated positive control shows what removes this particular degeneracy: acquisition times constrained independently of the magnetic fit. Source ages, cooling rates, geometry, material budgets and independently fixed dynamo activity windows can restrict admissible time changes. A more restrictive coupled physical model would need its own declared recovery test. The original broader programme's observed-map stage and any transition dating are not executed.

## Limits

- The example allows flexible piecewise recording clocks; the result is conditional on that class. The simple conductive rescaling within each segment does not establish a physically admissible three-dimensional Martian crust with all other observations matched.
- Dipole geometry, common global-z orientation and reference moments are synthetic. No geologic-age map, measured correlation length, Langlais coefficient uncertainty or real source-direction inversion enters this calculation.
- The positive control knows the break, has perfectly dated instantaneous signs, and assumes Poisson increments. Uncertain ages, overlapping acquisition, unknown change dates and non-Poisson reversals require additional tests.
- The reported Monte Carlo trials verify the implementation; the pathwise change-of-time identity is the reason the equivalence holds. Model ambiguity is not evidence for either actual Mars history.

## Reproduce

```sh
python scripts/followup/reversal_identifiability.py
python -m pytest -q tests/test_reversal_identifiability.py
python scripts/research/render_docs.py
python scripts/research/render_site.py
```

The builder checks the frozen input hashes and never rewrites the protocol. [Source ledger](followup/reversal/sources.json), [source geometries](followup/reversal/sources.csv), [record checks](followup/reversal/record_checks.csv), [map checks](followup/reversal/map_checks.csv), [classification and rate recovery](followup/reversal/classification.csv), [calibration](followup/reversal/calibration.csv), [all trial counts](followup/reversal/trial_counts.npz), [summary](followup/reversal/summary.json) and [manifest](followup/reversal/manifest.json) are saved. No new external dataset or implementation was incorporated.
'''
    (ROOT/'research/REVERSAL_IDENTIFIABILITY.md').write_text(text)


def main():
    p = json.loads((OUT/'protocol.json').read_text())
    for path, expected in p['input_sha256'].items():
        if sha(ROOT/path) != expected:
            raise ValueError(f'Frozen input changed: {path}')
    started = datetime.now(timezone.utc).isoformat()
    counter, maps = counterexample(p['counterexample'])
    dated, rows = dated_control(p['known_clock_positive_control'])
    summary = {'evaluation_started_utc': started, 'counterexample': counter, 'dated_control': dated,
               'observed_mars_fit_executed': False,
               'scope': 'Synthetic prerequisite; failure of global identifiability only in the declared nuisance class.'}
    save('summary.json', summary)
    save('sources.json', {'external_data_incorporated': False, 'external_code_copied': False, 'references': [
        {'title': 'Brown et al. (2002), The Time-Rescaling Theorem and Its Application to Neural Spike Train Data Analysis',
         'doi': '10.1162/08997660252741149', 'url': 'https://www.stat.cmu.edu/~kass/papers/rescaling.pdf',
         'consulted': 'Introduction and theorem in author-hosted manuscript; method only, no source data/code incorporated. The manuscript header has a 2001 draft date; publication is 2002.'},
        {'title': 'Project slab cooling and recording kernels', 'path': 'src/marswind/rapid_bodies.py',
         'consulted': 'Existing project implementation; analytic thermal scaling checked; no new external thermal solver.'}]})
    figure(maps, rows)
    report(summary, rows)
    save('manifest.json', {'generated_utc': datetime.now(timezone.utc).isoformat(),
                           'protocol_sha256': sha(OUT/'protocol.json'), 'frozen_input_sha256': p['input_sha256'],
                           'code_sha256': {path: sha(ROOT/path) for path in ['src/marswind/reversal_identifiability.py', 'scripts/followup/reversal_identifiability.py', 'tests/test_reversal_identifiability.py']},
                           'outputs_sha256': {f.name: sha(f) for f in sorted(OUT.iterdir()) if f.is_file() and f.name != 'manifest.json'},
                           'report_sha256': sha(ROOT/'research/REVERSAL_IDENTIFIABILITY.md'),
                           'software': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__, 'matplotlib': matplotlib.__version__}})
    print(json.dumps(clean(summary), indent=2))


if __name__ == '__main__':
    main()
