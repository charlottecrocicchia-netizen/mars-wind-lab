"""Reproduce the six discriminating tests offline from permitted local inputs.

Usage: python scripts/discriminating/build.py [--quick]
Inputs: research/data/atlas.json and depths.json (2° snapshot), the local
Langlais (2019) coefficients, the local Thiriet (2018) present-day profiles,
the Wieczorek (2022) archive boundary and one validation grid, plus the GMM-3
gravity and MOLA shape coefficients cached by pyshtools from NASA PDS / Zenodo.
Outputs are written to research/discriminating/. --quick shrinks the thermal
ensemble and the inversion scenarios for a fast smoke test.
"""
import csv, hashlib, json, platform, sys, time
from pathlib import Path

import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'mars-discriminating-tests-v1'
import matplotlib.pyplot as plt
import pyshtools as sh
from pyshtools.datasets import Mars

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from marswind.crustinversion import relief_potential, shell_potential, rereference, invert_moho, weighted_mean as dh_mean, grid_value, area_weights, G
from marswind.agetransfer import epoch_features, location_features, structure_features, age_features, skill, by_class_summary
from marswind.research_checks import ridge_predict, longitude_folds
from marswind.crusthistory import (HistoryParameters, run_history, profile_within_envelope, isotherm_depth_km,
                                   acquisition_ages, coherent_fractions, cooling_duration_myr, sample_parameters, START_AGE_GA)
from marswind.amplitude import required_magnetization, window_statistics, magnetic_vector, coherence_penalty

RAW = ROOT/'data/observations/raw'
OUT = ROOT/'research/discriminating'
OUT.mkdir(exist_ok=True)
QUICK = '--quick' in sys.argv
SEED = 20260928

PROTOCOL = {
    'version': '1.1', 'declared': '2026-09-28', 'revised_after_audit': '2026-09-28 (research/DISCRIMINATING_AUDIT.md)',
    'preregistration': 'Declared in this repository before the runs; not externally timestamped or preregistered.',
    'crust_inversion': {
        'gravity_model': 'GMM-3 (Genova et al., 2016), NASA PDS gmm3_120_sha.tab via pyshtools datasets',
        'shape_model': 'MOLA shape coefficients (Wieczorek 2024 Zenodo 10820719) via pyshtools datasets',
        'lmax': 90, 'finite_amplitude_order': 7, 'grid_lmax': 719, 'filter': 'minimum amplitude, 0.5 at degree 50',
        'degree_2_zonal': 'Bouguer C20 set to zero: the hydrostatic flattening is not compensated at the crust-mantle interface',
        'mass_convention': 'Crust = laterally variable-density shell between the mean Moho radius and the mean surface radius (shell_potential, recomputed at every trial Moho radius) + surface relief with crust density + Moho relief with contrast mantle − crust. Regularised fixed-point inversion: the minimum-amplitude filter multiplies the whole linear solution at every iteration; convergence (largest relief change < 1 m) is recorded.',
        'insight_anchor_km': 39.0, 'insight_lat_lon': [4.502, 135.623],
        'boundary': 'Andrews-Hanna et al. (2008) polyline distributed with the Wieczorek (2022) archive',
        'scenarios': [
            {'id': 'equal_2900', 'north': 2900, 'south': 2900, 'mantle': 3382, 'label': 'Equal density 2,900 (archive validation case)'},
            {'id': 'goossens_sabaka', 'north': 2622, 'south': 2492, 'mantle': 3382, 'label': 'Goossens & Sabaka (2026) north 2,622 / south 2,492'},
            {'id': 'kim_south_lighter', 'north': 2900, 'south': 2700, 'mantle': 3382, 'label': 'South lighter by 200 (Kim et al. 2023 bound)'},
            {'id': 'kim_south_denser', 'north': 2700, 'south': 2900, 'mantle': 3382, 'label': 'South denser by 200 (Kim et al. 2023 bound)'},
            {'id': 'goossens_sabaka_mantle_3500', 'north': 2622, 'south': 2492, 'mantle': 3500, 'label': 'Goossens & Sabaka densities, mantle 3,500'},
            {'id': 'equal_2900_mantle_3500', 'north': 2900, 'south': 2900, 'mantle': 3500, 'label': 'Equal density 2,900, mantle 3,500'}],
        'validation_grid': 'Mars-thick-Khan2022-39-2900-2900.dat from the Wieczorek (2022) archive'},
    'age_transfer': {
        'target': 'log(1 + |B| / 1 nT) from Langlais et al. (2019) at 150 and 400 km on 2° centres, |lat| <= 75°',
        'densities': [2600, 2700, 2800, 2900], 'ridge_alpha': 0.01, 'random_folds': 6, 'wedges': 6, 'buffer_deg': 10, 'wedge_offsets_deg': [0, 30],
        'longitude_shift_controls_deg': [60, 120, 180],
        'epoch_ranks': 'eN 1, mN 2, lN 3, eH 4, lH 5, eA 6, mA 7, lA 8; undivided and two-period codes average their classes',
        'age_features': 'ordinal rank, declared approximate class-centre age in Ga (eN 4.1 … lA 0.3), and Noachian/Hesperian/Amazonian indicators; the model age_ordinal drops the class-centre age as a sensitivity run',
        'interpretation': 'skill compares predictor sets out of region; it does not establish causation or the fraction of the dichotomy due to resurfacing'},
    'thermal_ensemble': {
        'samples_per_hemisphere': 300 if QUICK else 5000, 'seed': SEED, 'duration_myr': 4500, 'step_myr': 2.5, 'cell_km': 1.0,
        'thickness_resolution': 'sampled thickness rounded to whole kilometres so depth indices are exact physical depths',
        'basal_flux_convention': 'basal_flux_now_mw is the flux at the present day and basal_flux_early_mw at 4.5 Ga; the exponential decay is normalised to meet both endpoints',
        'acquisition_bookkeeping': 'cooled_before_X fractions count only depths that were hotter than the threshold at some time and last cooled through it before X; material always below the threshold is reported separately as an unresolved earlier record',
        'ranges': {'common': {'conductivity': [2.0, 3.5], 'th_ppm': [0.3, 1.5], 'k_over_th': [3000, 6000], 'u_over_th': [0.22, 0.32],
                              'basal_flux_now_mw': [5, 30], 'basal_flux_early_mw': [30, 120], 'basal_decay_gyr': [0.5, 3.0], 'surface_temperature_k': [205, 235]},
                   'North': {'thickness_km': [30, 55]}, 'South': {'thickness_km': [40, 85]}},
        'density': 2900, 'heat_capacity': 1000,
        'initial_state': 'steady state of the initial sources; rejected if any temperature exceeds the declared 1,500 K solidus gate',
        'present_day_envelope': 'Thiriet et al. (2018) Min/Max/BestModel present-day profiles, tolerance 30 K',
        'check_depths_km': {'North': [5, 10, 15, 20, 25], 'South': [5, 10, 20, 30, 35]},
        'noachian_te_gate_south': 'depth of a 650, 750 or 850 K isotherm at 3.9 Ga within 5–35 km (compiled Noachian elastic thicknesses in the Thiriet archive)',
        'carriers_k': {'pyrrhotite': 598.15, 'magnetite': 853.15, 'hematite': 943.15},
        'blocking_band_below_curie_k': 150,
        'dynamo_end_ages_ga': [4.1, 3.7],
        'chron_durations_myr': [0.67, 2, 5, 10, 20, 50, 100, 200, 500, 1000], 'coherence_depths_km': [10, 20, 30, 40, 50], 'phases': 16, 'poisson_realizations': 64,
        'reversal_models': 'periodic chrons of equal duration (16 phases) and Poisson chrons of the same mean duration (64 seeds); distributions are reported, the periodic case is the most efficient cancellation'},
    'amplitude': {'window_radius_deg': 10, 'altitude_km': 150, 'geometries': ['thin10_centered', 'thick20_centered', 'surface_to_depth'],
                  'capacity_levels_a_m': [1, 5, 20], 'capacity_note': 'Declared comparison levels, not material limits: 1 A/m, 5 A/m (Parker 2003 minimum for a 50 km layer), 20 A/m',
                  'geometry_note': 'Cylinder-equivalent magnetization: the window RMS field is matched by the on-axis field of one uniform vertical cylinder of the fitted cap radius. This is a declared scenario, not a demonstrated lower bound; the source model of Gong & Wieczorek is a stochastic ensemble of thin caps'},
    'surface': {'sites': {'Zhurong': {'lat': 25.066, 'lon': 109.926, 'observed_total_range_nt': [5.2, 39.8], 'observed_horizontal_mean_nt': 11.2, 'observed_horizontal_sd_nt': 10.9,
                                       'published_downward_continuation_total_nt': 81, 'published_downward_continuation_horizontal_nt': 55, 'source': 'Du et al. (2023)'},
                          'InSight': {'lat': 4.502, 'lon': 135.623, 'observed_total_nt': 2000, 'source': 'Johnson et al. (2020) as quoted in Mittelholz & Johnson (2022): ~2000 nT'}},
                'truncations': [134, 110, 90]}}


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def clean(x):
    if isinstance(x, dict): return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [clean(v) for v in x]
    if isinstance(x, np.ndarray): return clean(x.tolist())
    if isinstance(x, (float, np.floating)): return round(float(x), 6) if np.isfinite(x) else None
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, np.bool_): return bool(x)
    return x
def save(name, obj):
    (OUT/name).write_text(json.dumps(clean(obj), ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n'); print('saved', name, flush=True)
def csv_save(name, rows):
    with (OUT/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(clean(rows))
def q(a, probs=(.05, .5, .95)): return [float(x) for x in np.nanquantile(np.asarray(a, float), probs)]


# ---------------------------------------------------------------- Test 6: crust
def crust_inversion():
    p = PROTOCOL['crust_inversion']; L, N, GL = p['lmax'], p['finite_amplitude_order'], p['grid_lmax']
    grav = Mars.GMM3(lmax=L); mass = grav.gm/G; r0 = grav.r0
    shape = Mars.MOLA_shape(lmax=GL); c = shape.coeffs.copy(); c[:, L+1:, :] = 0
    surface = sh.expand.MakeGridDH(c, sampling=2, lmax=GL); rm = float(c[0, 0, 0])
    boundary = np.loadtxt(RAW/'crustal_models/selected/dichotomy_coordinates-JAH-0-360.txt')
    south = sh.backends.shtools.Curve2Mask(surface.shape[0], boundary[:, [1, 0]], 0, sampling=2, extend=False).astype(bool)
    obs = grav.pad(L).coeffs.copy(); obs[0, 0, 0] = 0
    lat_i, lon_i = p['insight_lat_lon']
    # constant-density benchmark of the finite-amplitude expansion against pyshtools
    mine = relief_potential(surface-rm, 2900., rm, mass, L, N); ref, _ = sh.gravmag.CilmPlusDH(surface, N, mass, 2900., lmax=L)
    benchmark = float(np.max(np.abs(mine-ref)[:, 1:, :])/np.max(np.abs(ref[:, 1:, :])))
    if benchmark > 1e-8: raise RuntimeError('Finite-amplitude expansion disagrees with the reference implementation')

    def run(rho_n, rho_s, rho_m):
        rho = np.where(south, rho_s, rho_n).astype(float)
        topo = rereference(relief_potential(surface-rm, rho, rm, mass, L, N), rm, r0)
        def f(d):
            # The reference shell between the trial mean Moho radius and the mean surface carries
            # gravity when the crust density varies laterally; it is recomputed for every trial d.
            ba = obs-topo-shell_potential(rho, d, rm, mass, L, r0); ba[0, 0, 0] = 0; ba[0, 2, 0] = 0
            moho, info = invert_moho(ba, r0, rho, rho_m, d, mass, L, N, filter_half_degree=50, iterations=100, tolerance_m=1.0)
            return (grid_value(surface, lat_i, lon_i)-grid_value(moho, lat_i, lon_i))/1000-p['insight_anchor_km'], moho, info
        d0 = rm-50e3; f0, moho, info = f(d0); d1 = d0-f0*1000; f1, moho, info = f(d1)
        for _ in range(8):
            if abs(f1) < 0.01: break
            d2 = d1-f1*(d1-d0)/(f1-f0); d0, f0 = d1, f1; d1 = d2; f1, moho, info = f(d1)
        if not info['converged']: raise RuntimeError('Crustal inversion did not converge')
        thick = (surface-moho)/1000
        w = area_weights(surface.shape[0])
        return thick, {'north_mean_km': dh_mean(thick, ~south), 'south_mean_km': dh_mean(thick, south), 'global_mean_km': dh_mean(thick, np.ones_like(south)),
                       'south_minus_north_km': dh_mean(thick, south)-dh_mean(thick, ~south), 'min_km': float(thick.min()), 'max_km': float(thick.max()),
                       'insight_km': grid_value(thick, lat_i, lon_i), 'negative_area_fraction': float(np.average((thick < 0).mean(axis=1), weights=w)),
                       'mean_moho_radius_km': d1/1000, **info}
    rows = []; grids = {}
    scenarios = p['scenarios'][:2] if QUICK else p['scenarios']
    for sc in scenarios:
        t = time.time(); thick, summary = run(sc['north'], sc['south'], sc['mantle'])
        summary.update(sc, seconds=round(time.time()-t, 1)); rows.append(summary); print(' ', sc['id'], {k: round(v, 2) for k, v in summary.items() if isinstance(v, float)}, flush=True)
        rows_idx = np.round((90-np.arange(-89, 90, 2))*surface.shape[0]/180).astype(int) % surface.shape[0]
        cols_idx = np.round(np.arange(1, 360, 2)*(2*surface.shape[0])/360).astype(int) % (2*surface.shape[0])
        grids[sc['id']] = np.round(thick[np.ix_(rows_idx[::-1], cols_idx)], 2)  # south-first rows to match atlas latitude order
        if sc['id'] == 'equal_2900':
            arch = np.loadtxt(RAW/'crustal_models/selected/Mars-thick-Khan2022-39-2900-2900.dat')
            lat_nodes = 90-np.arange(721)*0.25; lon_nodes = np.arange(1441)*0.25
            i = np.round((90-lat_nodes)*surface.shape[0]/180).astype(int) % surface.shape[0]; j = np.round(lon_nodes*(2*surface.shape[0])/360).astype(int) % (2*surface.shape[0])
            diff = thick[np.ix_(i, j)]-arch; w = np.cos(np.deg2rad(lat_nodes))[:, None]*np.ones((1, 1441))
            validation = {'archive_north_mean_km': 42.9221, 'archive_south_mean_km': 66.1801, 'archive_global_mean_km': 56.6888, 'archive_min_km': 5.5782, 'archive_max_km': 116.821,
                          'weighted_mean_difference_km': float(np.sum(diff*w)/np.sum(w)), 'weighted_rms_difference_km': float(np.sqrt(np.sum(diff**2*w)/np.sum(w))),
                          'max_abs_difference_km': float(np.abs(diff).max()), 'note': 'The archive uses the depth-dependent Khan2022 mantle density and its own hydrostatic treatment; agreement within a few km validates the implementation, not identity.'}
    result = {'scope': 'Crustal thickness inversions with laterally variable crust density (shell + relief decomposition, regularised fixed-point inversion), anchored to 39 km at InSight. Densities are declared scenarios; no scenario is a fitted best model.',
              'benchmark_relative_difference_vs_pyshtools': benchmark, 'validation_equal_2900': validation, 'scenarios': rows,
              'south_area_fraction_unweighted': float(south.mean()), 'grid_note': '2° cell-centre thickness (km), latitude −89..89 then longitude 1..359, for display only'}
    save('crust_inversion.json', result | {'grids_2deg': {k: v.tolist() for k, v in grids.items()}}); csv_save('crust_inversion.csv', rows)
    return result


# --------------------------------------------------------------- Test 1: age
def age_transfer():
    p = PROTOCOL['age_transfer']; A = json.loads((ROOT/'research/data/atlas.json').read_text())
    lat = np.array(A['latitude']); lon = np.array(A['longitude']); LA, LO = np.meshgrid(lat, lon, indexing='ij')
    codes = A['geology']['codes']; grid = np.array(A['geology']['grid']); units = {u['Unit']: u for u in A['geology']['units']}
    groups = sorted({u['UnitGroup'] for u in A['geology']['units']})
    boundary = np.loadtxt(RAW/'crustal_models/selected/dichotomy_coordinates-JAH-0-360.txt')
    dhmask = sh.backends.shtools.Curve2Mask(180, boundary[:, [1, 0]], 0, sampling=2, extend=True)
    south = dhmask[np.ix_((90-lat).astype(int), lon.astype(int))].astype(bool)
    R = np.array(A['topography_km']); valid = (np.abs(LA) <= 75) & (grid >= 0)
    la, lo, w = LA[valid], LO[valid], np.cos(np.deg2rad(LA[valid])); s_mask = south[valid]
    code_cells = [codes[i] for i in grid[valid]]; gidx = [groups.index(units[c]['UnitGroup']) for c in code_cells]
    F_loc = location_features(la, lo); F_age = age_features(code_cells)
    rng = np.random.default_rng(SEED); fold = rng.integers(0, p['random_folds'], len(la))
    random_splits = [(fold != k, fold == k) for k in range(p['random_folds'])]
    def evaluate(X, y, splits):
        pred = np.full(len(y), np.nan); base = np.full(len(y), np.nan)
        for train, test in splits:
            pred[test] = ridge_predict(X[train], y[train], w[train], X[test], p['ridge_alpha']); base[test] = np.average(y[train], weights=w[train])
        ok = np.isfinite(pred); num = np.sum(w[ok]*(y[ok]-pred[ok])**2); den = np.sum(w[ok]*(y[ok]-base[ok])**2)
        return float(1-num/den), float(np.sqrt(num/np.sum(w[ok])))
    rows = []; classes = []
    for alt in ['150', '400']:
        B = np.array(A['magnetic_nT'][alt]); y = np.log1p(B[valid])
        for density in p['densities']:
            H = np.array(A['crust_km'][str(density)])
            F_struct = structure_features(R[valid], H[valid], gidx, len(groups))
            F_hemi = s_mask.astype(float)[:, None]
            F_age_ordinal = F_age[:, [0, 2, 3, 4]]
            models = {'mean': np.zeros((len(y), 0)), 'hemisphere': F_hemi, 'location': F_loc, 'structure': F_struct, 'age': F_age, 'age_ordinal': F_age_ordinal,
                      'hemisphere+age': np.column_stack([F_hemi, F_age]), 'hemisphere+structure': np.column_stack([F_hemi, F_struct]),
                      'structure+age': np.column_stack([F_struct, F_age]), 'location+age': np.column_stack([F_loc, F_age]),
                      'location+structure': np.column_stack([F_loc, F_struct]), 'all': np.column_stack([F_loc, F_struct, F_age])}
            for name, X in models.items():
                for split_name, splits in [('random', random_splits)]+[(f'regional_{o}', list(longitude_folds(lo, p['wedges'], p['buffer_deg'], o))) for o in p['wedge_offsets_deg']]:
                    sk, rmse = evaluate(X, y, splits)
                    rows.append({'altitude_km': int(alt), 'density_kg_m3': density, 'model': name, 'split': split_name, 'skill_over_training_mean': sk, 'weighted_rmse_log1p_nt': rmse})
            if density == 2900:
                for shift in p['longitude_shift_controls_deg']:
                    Bs = np.roll(B, shift//2, axis=1); ys = np.log1p(Bs[valid])
                    for name in ['age', 'structure', 'location', 'hemisphere']:
                        sk, rmse = evaluate(models[name], ys, list(longitude_folds(lo, p['wedges'], p['buffer_deg'], 0)))
                        rows.append({'altitude_km': int(alt), 'density_kg_m3': density, 'model': name, 'split': f'regional_0_target_shifted_{shift}', 'skill_over_training_mean': sk, 'weighted_rmse_log1p_nt': rmse})
        ranks = F_age[:, 0]
        for row in by_class_summary(y, w, ranks, {'north_of_boundary': ~s_mask, 'south_of_boundary': s_mask, 'all': np.ones(len(y), bool)}):
            row.update(altitude_km=int(alt), mean_field_nt=float(np.expm1(row['weighted_mean']))); classes.append(row)
    result = {'scope': 'Fixed ridge baselines with training-only scaling; wedge hold-out with 10° buffers; grid cells are correlated model samples, not independent observations. Skill measures out-of-region predictability, not cause.',
              'cells': int(valid.sum()), 'skills': rows, 'field_by_epoch_class': classes,
              'rank_labels': {'1': 'Early Noachian', '2': 'Middle Noachian / undivided Noachian', '3': 'Late Noachian', '3.25': 'Hesperian–Noachian', '4': 'Early Hesperian', '4.5': 'undivided Hesperian / Amazonian–Noachian', '5': 'Late Hesperian', '5.75': 'Amazonian–Hesperian', '6': 'Early Amazonian', '7': 'Middle / undivided Amazonian', '8': 'Late Amazonian'}}
    save('age_transfer.json', result); csv_save('age_transfer_skills.csv', rows); csv_save('age_transfer_classes.csv', classes)
    return result


# ------------------------------------------------------ Tests 2 & 4: thermal
def thermal_ensemble(window_fields):
    p = PROTOCOL['thermal_ensemble']; carriers = p['carriers_k']; band = p['blocking_band_below_curie_k']
    def envelope(hemi):
        out = {}
        for kind in ['Min', 'Max', 'BestModel']:
            r = np.loadtxt(RAW/f'thermal_profiles/{hemi}_radius_{kind}.csv'); T = np.loadtxt(RAW/f'thermal_profiles/{hemi}_TemperatureProfile_{kind}.csv')
            d = r.max()-r; i = np.argsort(d); out[kind] = (d[i], T[i])
        return out
    depths_gw = json.loads((ROOT/'research/data/depths.json').read_text())
    result = {'scope': 'Fixed-thickness conductive crust columns with decaying radiogenic heating and basal flux, cooling from 4.5 Ga. Accepted histories match the published present-day envelope; they are not fitted regional histories and omit crustal growth, intrusions, impacts and fluids.',
              'hemispheres': {}}
    ages_rows = []; coherence_rows = []; window_rows = []
    for hemi in ['North', 'South']:
        env = envelope(hemi); check = p['check_depths_km'][hemi]
        lo = np.minimum(np.interp(check, *env['Min']), np.interp(check, *env['Max'])); hi = np.maximum(np.interp(check, *env['Min']), np.interp(check, *env['Max']))
        ranges = {k: tuple(v) for k, v in (p['ranges']['common'] | p['ranges'][hemi]).items()}
        samples = sample_parameters(p['samples_per_hemisphere'], ranges, SEED+(hemi == 'South'))
        accepted = []; rejected = {'solidus': 0, 'envelope': 0, 'noachian_te': 0}
        t0 = time.time()
        for s in samples:
            s['thickness_km'] = float(round(s['thickness_km']/p['cell_km'])*p['cell_km'])
            par = HistoryParameters(**s, density=p['density'], heat_capacity=p['heat_capacity'], duration_myr=p['duration_myr'])
            h = run_history(par, p['duration_myr'], p['step_myr'], p['cell_km'])
            if h.temperature_k[0].max() > 1500: rejected['solidus'] += 1; continue
            ok, _ = profile_within_envelope(h.depth_m, h.temperature_k[-1], check, lo, hi, 30.)
            if not ok: rejected['envelope'] += 1; continue
            i39 = int(np.argmin(abs(h.time_myr-600)))
            te = {T: isotherm_depth_km(h.depth_m, h.temperature_k[i39], T) for T in (650, 750, 850)}
            te_ok = {str(T): bool(v is not None and 5 <= v <= 35) for T, v in te.items()}
            if hemi == 'South' and not any(te_ok.values()): rejected['noachian_te'] += 1; continue
            accepted.append((s, h, te_ok))
        print(f'  {hemi}: {len(accepted)} accepted of {len(samples)} in {time.time()-t0:.0f} s; rejected {rejected}', flush=True)
        if not accepted: raise RuntimeError(f'No accepted history for {hemi}')
        hmin = min(len(h.depth_m) for _, h, _ in accepted)
        depth_km = np.arange(hmin)*p['cell_km']
        thresholds = np.array(list(carriers.values()))
        ages = np.full((len(accepted), hmin, len(thresholds)), np.nan)
        for n, (_, h, _) in enumerate(accepted):
            a, status = acquisition_ages(h, thresholds); ages[n] = a[:hmin]
            ages[n][status[:hmin] == 0] = np.inf   # never hotter than the threshold: an earlier record is possible at any age
            ages[n][status[:hmin] == 2] = -np.inf  # still hotter than the threshold today
        for zi, z in enumerate(depth_km):
            row = {'hemisphere': hemi, 'depth_km': float(z)}
            for ci, name in enumerate(carriers):
                col = ages[:, zi, ci]; finite = np.isfinite(col)
                row[f'{name}_age_q05_ga'], row[f'{name}_age_q50_ga'], row[f'{name}_age_q95_ga'] = (q(col[finite]) if finite.any() else [None]*3)
                row[f'{name}_always_below_fraction'] = float(np.mean(col == np.inf)); row[f'{name}_still_above_fraction'] = float(np.mean(col == -np.inf))
                for end in p['dynamo_end_ages_ga']:
                    row[f'{name}_cooled_before_{end}_ga_fraction'] = float(np.mean(finite & (col >= end)))
                    row[f'{name}_cooled_after_{end}_ga_fraction'] = float(np.mean(finite & (col < end)))
            ages_rows.append(row)
        # cooling durations and coherence at selected depths: periodic and Poisson reversals
        for z in p['coherence_depths_km']:
            zi = int(round(z/p['cell_km']))
            if zi >= hmin: continue
            for name, Tc in carriers.items():
                bandk = (Tc-band, Tc); durations = []; frac = {(kind, c): [] for kind in ('periodic', 'poisson') for c in p['chron_durations_myr']}
                for k, (_, h, _) in enumerate(accepted[: (60 if QUICK else 200)]):
                    dur = cooling_duration_myr(h, zi, bandk)
                    if dur is None: continue
                    durations.append(dur)
                    for c in p['chron_durations_myr']:
                        frac[('periodic', c)].extend(coherent_fractions(h, zi, bandk, c, p['phases'], 'periodic')[0].tolist())
                        frac[('poisson', c)].extend(coherent_fractions(h, zi, bandk, c, p['poisson_realizations'], 'poisson', seed=SEED+1000*k)[0].tolist())
                if not durations: continue
                rowc = {'hemisphere': hemi, 'depth_km': z, 'carrier': name, 'histories': len(durations), 'cooling_duration_q05_q50_q95_myr': q(durations)}
                for kind in ('periodic', 'poisson'):
                    medians = []
                    for c in p['chron_durations_myr']:
                        vals = np.array(frac[(kind, c)], float); vals = vals[np.isfinite(vals)]
                        rowc[f'{kind}_retained_median_chron_{c}_myr'] = float(np.median(vals)); rowc[f'{kind}_retained_q95_chron_{c}_myr'] = float(np.quantile(vals, .95))
                        rowc[f'{kind}_retained_rms_chron_{c}_myr'] = float(np.sqrt(np.mean(vals**2))); medians.append(float(np.median(vals)))
                    half = [c for c, m in zip(p['chron_durations_myr'], medians) if m >= .5]
                    rowc[f'{kind}_shortest_tested_chron_with_half_retention_myr'] = half[0] if half else None
                coherence_rows.append(rowc)
        # Gong & Wieczorek windows: is the equivalent depth cooled through each carrier before the dynamo ends?
        for win in depths_gw:
            if not win['usable'] or win['region'] != hemi: continue
            zi = int(round(win['depth_km']/p['cell_km']))
            row = {'hemisphere': hemi, 'lat': win['lat'], 'lon': win['lon'], 'depth_km': win['depth_km'], 'within_ensemble_columns': zi < hmin,
                   'rms_field_150km_nt': window_fields[(win['lat'], win['lon'])]}
            for ci, name in enumerate(carriers):
                col = ages[:, min(zi, hmin-1), ci]; finite = np.isfinite(col)
                row[f'{name}_always_below_fraction'] = float(np.mean(col == np.inf)) if zi < hmin else None
                for end in p['dynamo_end_ages_ga']:
                    row[f'{name}_cooled_before_{end}_ga_fraction'] = float(np.mean(finite & (col >= end))) if zi < hmin else None
            window_rows.append(row)
        params = {k: q([s[k] for s, _, _ in accepted]) for k in ranges}
        curie_now = {name: q([isotherm_depth_km(h.depth_m, h.temperature_k[-1], Tc) or h.depth_m[-1]/1000 for _, h, _ in accepted]) for name, Tc in carriers.items()}
        result['hemispheres'][hemi] = {'samples': len(samples), 'accepted': len(accepted), 'rejected': rejected, 'accepted_parameter_quantiles_q05_q50_q95': params,
                                       'present_day_curie_depth_quantiles_km': curie_now, 'noachian_te_gate_pass_by_isotherm': {T: float(np.mean([a[2][T] for a in accepted])) for T in ('650', '750', '850')},
                                       'common_depth_range_km': [0, float(depth_km[-1])]}
    win_summary = []
    subsets = {'all_usable': lambda r: True, 'deep_ge_30km': lambda r: r['depth_km'] >= 30, 'strong_rms_ge_100nT': lambda r: r['rms_field_150km_nt'] >= 100,
               'strong_and_deep': lambda r: r['depth_km'] >= 30 and r['rms_field_150km_nt'] >= 100}
    for hemi in ['North', 'South']:
        for subset, keep in subsets.items():
            sel = [r for r in window_rows if r['hemisphere'] == hemi and r['within_ensemble_columns'] and keep(r)]
            for name in carriers:
                for end in p['dynamo_end_ages_ga']:
                    vals = [r[f'{name}_cooled_before_{end}_ga_fraction'] for r in sel]
                    win_summary.append({'hemisphere': hemi, 'subset': subset, 'carrier': name, 'dynamo_end_ga': end, 'windows': len(vals),
                                        'windows_majority_cooled_before_end': int(np.sum(np.array(vals) >= .5)) if vals else 0,
                                        'median_fraction_of_histories_cooled_before_end': float(np.median(vals)) if vals else None})
    result['window_summary'] = win_summary
    save('thermal_ensemble.json', result); csv_save('thermal_acquisition_ages.csv', ages_rows); csv_save('thermal_coherence.csv', coherence_rows); csv_save('thermal_source_windows.csv', window_rows)
    return result, ages_rows, coherence_rows


# ------------------------------------------------ Tests 3 & 5: amplitude, surface
def load_langlais(lmax):
    return sh.SHMagCoeffs.from_file(str(RAW/'magnetic_field/Langlais2019.sh.gz'), lmax=lmax, skip=4, r0=3393.5e3, header=False, file_units='nT', units='nT', encoding='utf-8')


def field_grid():
    """|B| of the degree-134 model at the amplitude altitude on a 1° grid, plus window RMS values."""
    p = PROTOCOL['amplitude']; model = load_langlais(134)
    lat = np.arange(-89.5, 90, 1.); lon = np.arange(0.5, 360, 1.); LA, LO = np.meshgrid(lat, lon, indexing='ij')
    v = model.expand(lat=LA.ravel(), lon=LO.ravel(), r=np.full(LA.size, (3393.5+p['altitude_km'])*1000)); B = np.linalg.norm(v, axis=1).reshape(LA.shape)
    depths = json.loads((ROOT/'research/data/depths.json').read_text())
    stats = {(d['lat'], d['lon']): window_statistics(B, lat, lon, d['lat'], d['lon'], p['window_radius_deg']) for d in depths if d['usable']}
    return B, lat, lon, depths, stats


def amplitude_and_surface(coherence_rows, grid):
    p = PROTOCOL['amplitude']; ps = PROTOCOL['surface']; load = load_langlais
    B, lat, lon, depths, stats = grid
    coh = {(r['hemisphere'], r['depth_km']): r for r in coherence_rows if r['carrier'] == 'magnetite'}
    rows = []
    for d in depths:
        if not d['usable']: continue
        st = stats[(d['lat'], d['lon'])]; dep = d['depth_km']; R = d['source_cap_radius_km']
        geoms = {'thin10_centered': (max(0., dep-5), max(0., dep-5)+10), 'thick20_centered': (max(0., dep-10), max(0., dep-10)+20), 'surface_to_depth': (0., max(dep, 1.))}
        row = {'region': d['region'], 'lat': d['lat'], 'lon': d['lon'], 'depth_km': dep, 'cap_radius_km': R, 'rms_field_150km_nt': st['rms'], 'max_field_150km_nt': st['max']}
        for k, (a, b) in geoms.items(): row[f'required_{k}_a_m'] = required_magnetization(st['rms'], R, a, b, p['altitude_km'])
        nearest = min([z for (h, z) in coh if h == d['region']], key=lambda z: abs(z-dep), default=None)
        if nearest is not None:
            c = coh[(d['region'], nearest)]
            for kind in ('poisson', 'periodic'):
                for chron in [0.67, 100, 1000]:
                    f = c.get(f'{kind}_retained_median_chron_{chron}_myr')
                    row[f'required_thick20_after_{kind}_cancellation_chron_{chron}_myr_a_m'] = float(coherence_penalty(row['required_thick20_centered_a_m'], max(f, 1e-6))) if f is not None and np.isfinite(f) else None
            row['coherence_reference_depth_km'] = nearest
        rows.append(row)
    summary = []
    for region in ['North', 'South']:
        sel = [r for r in rows if r['region'] == region]
        for k in p['geometries']:
            vals = np.array([r[f'required_{k}_a_m'] for r in sel])
            summary.append({'region': region, 'geometry': k, 'windows': len(vals), 'required_q10_q50_q90_a_m': q(vals, (.1, .5, .9)), 'max_a_m': float(vals.max()),
                            **{f'fraction_above_{c}_a_m': float(np.mean(vals > c)) for c in p['capacity_levels_a_m']}})
        for kind in ('poisson', 'periodic'):
            for chron in [0.67, 100, 1000]:
                vals = np.array([r.get(f'required_thick20_after_{kind}_cancellation_chron_{chron}_myr_a_m') for r in sel], dtype=float)
                if np.isfinite(vals).any():
                    summary.append({'region': region, 'geometry': f'thick20_centered_after_{kind}_cancellation_chron_{chron}_myr', 'windows': int(np.isfinite(vals).sum()), 'required_q10_q50_q90_a_m': q(vals[np.isfinite(vals)], (.1, .5, .9)), 'max_a_m': float(np.nanmax(vals)),
                                    **{f'fraction_above_{c}_a_m': float(np.nanmean(vals > c)) for c in p['capacity_levels_a_m']}})
    amp = {'scope': 'Cylinder-equivalent magnetization: the on-axis field of one uniform vertical cylinder of the fitted cap radius is matched to the area-weighted RMS field within 10° of each usable Gong & Wieczorek window at 150 km. This is a declared geometry scenario, not a demonstrated lower bound. Cancellation penalties divide by the median retained fraction (Poisson or periodic reversals) of the conductive histories at the nearest tested depth.',
           'summary': summary}
    save('amplitude.json', amp); csv_save('amplitude_windows.csv', rows)
    # surface truth
    shape = Mars.MOLA_shape(lmax=90); sites = {}
    for name, site in ps['sites'].items():
        r_site = float(shape.expand(lat=site['lat'], lon=site['lon']))/1000
        preds = []
        for lmax in ps['truncations']:
            m = load(lmax)
            for label, r in [('local_surface', r_site), ('reference_sphere_3393.5', 3393.5), ('surface_plus_5km', r_site+5)]:
                preds.append({'lmax': lmax, 'radius_km': r, 'radius_label': label, **magnetic_vector(m, site['lat'], site['lon'], r)})
        full = next(x for x in preds if x['lmax'] == 134 and x['radius_label'] == 'reference_sphere_3393.5')
        sites[name] = {**site, 'mola_radius_km': r_site, 'predictions': preds, 'prediction_at_reference_sphere_degree_134_total_nt': full['total_nt'], 'prediction_at_reference_sphere_degree_134_horizontal_nt': full['horizontal_nt']}
        if name == 'Zhurong':
            sites[name]['ratio_predicted_over_observed_total'] = [full['total_nt']/site['observed_total_range_nt'][1], full['total_nt']/site['observed_total_range_nt'][0]]
            sites[name]['ratio_predicted_over_observed_horizontal_mean'] = full['horizontal_nt']/site['observed_horizontal_mean_nt']
        else:
            sites[name]['ratio_observed_over_predicted_total'] = site['observed_total_nt']/full['total_nt']
    surface = {'scope': 'Downward continuation of the degree-134 Langlais et al. (2019) model to two surface sites with published rover/lander measurements. The amplification factor at the surface makes truncation and radius choices matter; both are tabulated.', 'sites': sites}
    save('surface_check.json', surface)
    return amp, rows, surface


# ------------------------------------------------------------------ figures
def figures(crust, age, thermal, ages_rows, coherence_rows, amp_rows, surface):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
    def finish(fig, name):
        fig.savefig(OUT/f'{name}.png', dpi=170); fig.savefig(OUT/f'{name}.svg', metadata={'Date': None}); plt.close(fig)
        svg = OUT/f'{name}.svg'; svg.write_text('\n'.join(l.rstrip() for l in svg.read_text().splitlines())+'\n')
    # crust
    fig, ax = plt.subplots(figsize=(8, 3.6), layout='constrained'); sc = crust['scenarios']; x = np.arange(len(sc))
    ax.bar(x-.2, [s['north_mean_km'] for s in sc], .4, label='North of boundary', color='#486282'); ax.bar(x+.2, [s['south_mean_km'] for s in sc], .4, label='South of boundary', color='#b64f30')
    for i, s in enumerate(sc): ax.text(i, max(s['north_mean_km'], s['south_mean_km'])+1, f"Δ {s['south_minus_north_km']:.1f} km\nmin {s['min_km']:.1f}", ha='center', fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels([f"N {s['north']}\nS {s['south']}\nmantle {s['mantle']}" for s in sc], fontsize=7); ax.set_ylabel('Mean crustal thickness (km)'); ax.legend(fontsize=8)
    ax.set_title('Test 6 · Crustal thickness with declared density scenarios, anchored to 39 km at InSight'); finish(fig, 'crust_inversion')
    # age
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8), layout='constrained')
    cls = [c for c in age['field_by_epoch_class'] if c['altitude_km'] == 150]
    for region, color, marker in [('north_of_boundary', '#486282', 'o'), ('south_of_boundary', '#b64f30', 's')]:
        pts = sorted([c for c in cls if c['region'] == region and c['rank'] in (1, 2, 3, 4, 5, 6, 7, 8)], key=lambda c: c['rank'])
        ax[0].plot([c['rank'] for c in pts], [c['mean_field_nt'] for c in pts], marker=marker, color=color, label=region.replace('_', ' '))
        for c in pts: ax[0].annotate(str(c['cells']), (c['rank'], c['mean_field_nt']), textcoords='offset points', xytext=(0, 5), ha='center', fontsize=6, color=color)
    ax[0].set_yscale('log'); ax[0].set_xticks(range(1, 9)); ax[0].set_xticklabels(['eN', 'mN', 'lN', 'eH', 'lH', 'eA', 'mA', 'lA']); ax[0].set_ylabel('Area-weighted mean |B| at 150 km (nT)'); ax[0].set_xlabel('Surface epoch of the mapped unit'); ax[0].legend(fontsize=8)
    ax[0].set_title('Field by surface epoch, both sides of the boundary (numbers: 2° cells)')
    sk = [s for s in age['skills'] if s['altitude_km'] == 150 and s['density_kg_m3'] == 2900 and 'shifted' not in s['split']]
    names = ['hemisphere', 'location', 'structure', 'age', 'hemisphere+age', 'structure+age', 'all']; xs = np.arange(len(names))
    for k, (split, color) in enumerate([('random', '#9aa0a6'), ('regional_0', '#b64f30'), ('regional_30', '#e0a070')]):
        ax[1].bar(xs+(k-1)*.27, [next(s['skill_over_training_mean'] for s in sk if s['model'] == n and s['split'] == split) for n in names], .27, label=split.replace('_', ' '), color=color)
    ax[1].axhline(0, color='k', lw=.6); ax[1].set_xticks(xs); ax[1].set_xticklabels(names, rotation=20, fontsize=8); ax[1].set_ylabel('Out-of-fold skill'); ax[1].legend(fontsize=8); ax[1].set_title('Test 1 · Predictive skill, 150 km, crust density 2,900')
    finish(fig, 'age_transfer')
    # thermal acquisition ages
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), layout='constrained', sharey=True)
    for a, hemi in zip(ax, ['North', 'South']):
        rows = [r for r in ages_rows if r['hemisphere'] == hemi]; z = [r['depth_km'] for r in rows]
        for name, color in [('pyrrhotite', '#c9a227'), ('magnetite', '#b64f30'), ('hematite', '#6b2940')]:
            med = np.array([r[f'{name}_age_q50_ga'] if r[f'{name}_age_q50_ga'] is not None else np.nan for r in rows], float)
            lo = np.array([r[f'{name}_age_q05_ga'] if r[f'{name}_age_q05_ga'] is not None else np.nan for r in rows], float); hi = np.array([r[f'{name}_age_q95_ga'] if r[f'{name}_age_q95_ga'] is not None else np.nan for r in rows], float)
            a.plot(med, z, color=color, label=f'{name}: age of last cooling through its Curie point'); a.fill_betweenx(z, lo, hi, color=color, alpha=.18)
        a.axvspan(3.7, 4.5, color='#dfe7f0', alpha=.6); a.axvspan(4.1, 4.5, color='#c5d3e3', alpha=.6); a.text(4.48, 2, 'dynamo\n≥4.1 Ga', fontsize=7, ha='right'); a.text(3.72, 2, '≥3.7 Ga', fontsize=7)
        a.set_xlim(4.5, 0); a.set_ylim(max(z), 0); a.set_xlabel('Age (Ga)'); a.set_title(f'{hemi}: {thermal["hemispheres"][hemi]["accepted"]} accepted conductive histories')
    ax[0].set_ylabel('Depth (km)'); ax[1].legend(fontsize=7, loc='lower left')
    fig.suptitle('Test 2 · When does each depth last cool through a carrier Curie temperature? (median and 5–95% of accepted histories)'); finish(fig, 'thermal_acquisition')
    # coherence
    fig, ax = plt.subplots(figsize=(8, 3.8), layout='constrained'); chrons = PROTOCOL['thermal_ensemble']['chron_durations_myr']
    for r in [r for r in coherence_rows if r['carrier'] == 'magnetite' and r['hemisphere'] == 'South']:
        line, = ax.plot(chrons, [r[f'poisson_retained_median_chron_{c}_myr'] for c in chrons], marker='o', label=f"{r['depth_km']:.0f} km · Poisson reversals · cooling through band {r['cooling_duration_q05_q50_q95_myr'][1]:.0f} Myr")
        ax.plot(chrons, [r[f'periodic_retained_median_chron_{c}_myr'] for c in chrons], marker='x', ls=':', color=line.get_color(), label=f"{r['depth_km']:.0f} km · periodic reversals")
    ax.axvline(1/1.5, color='k', ls=':', lw=.8); ax.text(1/1.5*1.1, .9, 'Steele et al. 2024:\n≥1.5 reversals/Myr\ndemagnetize large basins', fontsize=7); ax.axhline(.5, color='gray', lw=.6)
    ax.set_xscale('log'); ax.set_xlabel('Chron duration (Myr)'); ax.set_ylabel('Median retained fraction of a steady record'); ax.set_ylim(0, 1.02); ax.legend(fontsize=7)
    ax.set_title('Test 4 · Retained fraction of a steady record after reversals during slow conductive cooling\n(southern histories, magnetite 430–580 °C band; medians over histories and realisations)'); finish(fig, 'thermal_coherence')
    # amplitude
    fig, ax = plt.subplots(figsize=(8, 3.8), layout='constrained')
    for region, color in [('North', '#486282'), ('South', '#b64f30')]:
        vals = np.array([r['required_thick20_centered_a_m'] for r in amp_rows if r['region'] == region]); vals = vals[vals > 0]
        ax.hist(np.log10(vals), bins=np.linspace(-2, 3, 26), alpha=.6, color=color, label=f'{region}: {len(vals)} windows')
    for c, lab in [(1, '1 A/m'), (5, '5 A/m · Parker (2003) minimum'), (20, '20 A/m')]: ax.axvline(np.log10(c), color='k', ls='--', lw=.7); ax.text(np.log10(c), ax.get_ylim()[1]*.9, lab, rotation=90, fontsize=7, va='top', ha='right')
    ax.set_xlabel('log10 cylinder-equivalent magnetization (A/m), 20 km layer centred on the equivalent depth, before any cancellation'); ax.set_ylabel('Windows'); ax.legend(fontsize=8)
    ax.set_title('Test 3 · Cylinder-equivalent magnetization behind each usable source-depth window'); finish(fig, 'amplitude_budget')
    # surface
    fig, ax = plt.subplots(figsize=(7, 3.4), layout='constrained'); s = surface['sites']
    obs = [np.mean(s['Zhurong']['observed_total_range_nt']), s['InSight']['observed_total_nt']]; pred = [s['Zhurong']['prediction_at_reference_sphere_degree_134_total_nt'], s['InSight']['prediction_at_reference_sphere_degree_134_total_nt']]
    x = np.arange(2); ax.bar(x-.2, obs, .4, color='#2f6f5e', label='Measured on the ground'); ax.bar(x+.2, pred, .4, color='#9aa0a6', label='Orbital model continued to the surface (degree 134)')
    ax.errorbar([-.2], [obs[0]], yerr=[[obs[0]-s['Zhurong']['observed_total_range_nt'][0]], [s['Zhurong']['observed_total_range_nt'][1]-obs[0]]], fmt='none', color='k', capsize=3)
    ax.set_yscale('log'); ax.set_xticks(x); ax.set_xticklabels(['Zhurong · Utopia Planitia', 'InSight · Elysium Planitia']); ax.set_ylabel('|B| at the surface (nT)'); ax.legend(fontsize=8)
    ax.set_title('Test 5 · The two sites where the orbital model has been checked on the ground'); finish(fig, 'surface_check')


def main():
    t0 = time.time(); print('Discriminating tests build', 'quick' if QUICK else 'full', flush=True)
    save('protocol.json', PROTOCOL)
    print('Test 6: crust inversion', flush=True); crust = crust_inversion()
    print('Test 1: age transfer', flush=True); age = age_transfer()
    grid = field_grid()
    print('Tests 2 & 4: thermal ensemble', flush=True); thermal, ages_rows, coherence_rows = thermal_ensemble({k: v['rms'] for k, v in grid[4].items()})
    print('Tests 3 & 5: amplitude and surface', flush=True); amp, amp_rows, surface = amplitude_and_surface(coherence_rows, grid)
    figures(crust, age, thermal, ages_rows, coherence_rows, amp_rows, surface)
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in [ROOT/'research/data/atlas.json', ROOT/'research/data/depths.json', RAW/'magnetic_field/Langlais2019.sh.gz',
              RAW/'crustal_models/selected/dichotomy_coordinates-JAH-0-360.txt', RAW/'crustal_models/selected/Mars-thick-Khan2022-39-2900-2900.dat']+
              [RAW/f'thermal_profiles/{h}_{k}_{v}.csv' for h in ['North', 'South'] for k in ['radius', 'TemperatureProfile'] for v in ['Min', 'Max', 'BestModel']]}
    outputs = {p.name: sha(p) for p in sorted(OUT.iterdir()) if p.name != 'manifest.json'}
    save('manifest.json', {'generated_by': 'scripts/discriminating/build.py', 'quick': QUICK, 'seconds': round(time.time()-t0), 'inputs_sha256': inputs,
                           'code_sha256': {n: sha(ROOT/f'src/marswind/{n}.py') for n in ['crustinversion', 'agetransfer', 'crusthistory', 'amplitude', 'recording', 'thermal', 'research_checks']} | {'builder': sha(Path(__file__))},
                           'outputs_sha256': outputs, 'software': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__, 'pyshtools': sh.__version__, 'matplotlib': matplotlib.__version__},
                           'external_cached_inputs': 'GMM-3 gravity (NASA PDS) and MOLA shape (Zenodo 10820719) are fetched and checksummed by pyshtools into its cache; they are not redistributed here.'})
    print('done in', round(time.time()-t0), 's')


if __name__ == '__main__':
    main()
