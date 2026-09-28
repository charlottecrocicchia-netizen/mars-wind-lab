"""Analytic and consistency checks for the discriminating-test modules.

These verify implementations against exact cases. They do not validate any
geological interpretation of Mars.
"""
import numpy as np
import pytest

from marswind.agetransfer import epoch_features, skill, age_features
from marswind.amplitude import required_magnetization, coherence_penalty, window_statistics
from marswind.crusthistory import (heat_production_w_kg, HistoryParameters, run_history, acquisition_ages, coherent_fractions,
                                   coherent_fraction, cooling_duration_myr, isotherm_depth_km, profile_within_envelope, sample_parameters)
from marswind.recording import cylinder_axis_operator

sh = pytest.importorskip('pyshtools')
from marswind.crustinversion import relief_potential, shell_potential, minimum_amplitude_filter, invert_moho, rereference, weighted_mean, grid_value  # noqa: E402


def test_relief_potential_matches_linear_and_reference():
    mass, d, lmax, gl = 6.4171e23, 3.39e6, 12, 63
    c = np.zeros((2, gl+1, gl+1)); c[0, 0, 0] = d; c[0, 3, 2] = 1000.; c[1, 5, 1] = 500.
    grid = sh.expand.MakeGridDH(c, sampling=2, lmax=gl)
    mine = relief_potential(grid-d, 3000., d, mass, lmax, 1)
    assert mine[0, 3, 2] == pytest.approx(4*np.pi*d**2*3000.*1000./(mass*7), rel=1e-9)
    c[0, 3, 2] = 20000.; grid = sh.expand.MakeGridDH(c, sampling=2, lmax=gl)
    mine = relief_potential(grid-d, 3000., d, mass, lmax, 5)
    ref, _ = sh.gravmag.CilmPlusDH(grid, 5, mass, 3000., lmax=lmax)
    big = np.abs(ref) > 1e-14
    assert np.max(np.abs(mine-ref)[big]/np.abs(ref)[big]) < 1e-4


def test_lateral_density_is_linear():
    mass, d, lmax, gl = 6.4171e23, 3.39e6, 8, 31
    c = np.zeros((2, gl+1, gl+1)); c[0, 0, 0] = d; c[0, 2, 1] = 5000.
    grid = sh.expand.MakeGridDH(c, sampling=2, lmax=gl)
    rho = np.where(np.arange(grid.shape[0])[:, None] < grid.shape[0]//2, 2600., 2900.)*np.ones_like(grid)
    split = relief_potential(grid-d, rho, d, mass, lmax, 3)
    north = relief_potential(np.where(rho == 2600., grid-d, 0.), 2600., d, mass, lmax, 3)
    south = relief_potential(np.where(rho == 2900., grid-d, 0.), 2900., d, mass, lmax, 3)
    assert np.allclose(split, north+south, atol=1e-16)


def test_filter_matches_reference():
    for l in [1, 5, 50, 90]:
        assert minimum_amplitude_filter(l, 50, 3396e3, 3340e3) == pytest.approx(sh.gravmag.DownContFilterMA(l, 50, 3396e3, 3340e3), abs=1e-12)
    assert minimum_amplitude_filter(0, 50, 3396e3, 3340e3) == 1.0


def test_inversion_recovers_synthetic_relief():
    mass, d, r0, lmax, gl = 6.4171e23, 3.34e6, 3.396e6, 10, 79
    truth = np.zeros((2, gl+1, gl+1)); truth[0, 0, 0] = d; truth[0, 1, 0] = -8000.; truth[0, 3, 2] = 6000.; truth[1, 7, 4] = 3000.
    grid = sh.expand.MakeGridDH(truth, sampling=2, lmax=gl)
    forward = rereference(relief_potential(grid-d, 482., d, mass, lmax, 5), d, r0)
    recovered, info = invert_moho(forward, r0, np.full(grid.shape, 2900.), 3382., d, mass, lmax, 5, filter_half_degree=200, iterations=100, tolerance_m=1e-3)
    rc = sh.expand.SHExpandDH(recovered-d, sampling=2, lmax_calc=lmax)
    assert info['converged']
    assert rc[0, 1, 0] == pytest.approx(-8000., abs=5.)
    assert rc[0, 3, 2] == pytest.approx(6000., abs=5.)
    assert rc[1, 7, 4] == pytest.approx(3000., abs=5.)


def test_filter_is_applied_to_the_converged_solution():
    """Audit control: a pure degree-50 relief must come back with gain 0.5, not 1."""
    mass, d, r0, lmax, gl = 6.4171e23, 3.34e6, 3.396e6, 50, 63
    truth = np.zeros((2, gl+1, gl+1)); truth[0, 50, 0] = 10.
    grid = sh.expand.MakeGridDH(truth, sampling=2, lmax=gl)
    ba = rereference(relief_potential(grid, 482., d, mass, lmax, 1), d, r0)
    recovered, info = invert_moho(ba, r0, np.full(grid.shape, 2900.), 3382., d, mass, lmax, 1, filter_half_degree=50, iterations=100, tolerance_m=1e-6)
    rc = sh.expand.SHExpandDH(recovered-d, sampling=2, lmax_calc=lmax)
    assert info['converged'] and rc[0, 50, 0]/10 == pytest.approx(0.5, abs=1e-3)


def test_shell_potential_matches_analytic_integral_and_decomposition():
    """Audit control: the laterally variable reference shell has exterior gravity."""
    mass, d, R, r0, lmax, gl = 6.4171e23, 3340e3, 3390e3, 3396e3, 20, 63
    coeff = np.zeros((2, gl+1, gl+1)); coeff[0, 0, 0] = 2800.; coeff[0, 3, 1] = 100.
    density = sh.expand.MakeGridDH(coeff, sampling=2, lmax=gl)
    exact = 4*np.pi*100.*(R**6-d**6)/(mass*7*6*r0**3)
    shell = shell_potential(density, d, R, mass, lmax, r0)
    assert shell[0, 3, 1] == pytest.approx(exact, rel=1e-9)
    assert abs(shell[1, 3, 1]) < 1e-12*exact and abs(shell[0, 5, 2]) < 1e-12*exact
    uniform = shell_potential(np.full(density.shape, 2800.), d, R, mass, lmax, r0)
    assert np.max(np.abs(uniform[:, 1:, :])) < 1e-12*exact
    hs = np.zeros((2, gl+1, gl+1)); hs[0, 4, 2] = 3000.; hs_grid = sh.expand.MakeGridDH(hs, sampling=2, lmax=gl)
    whole = rereference(relief_potential(R-d+hs_grid, density, d, mass, lmax, 8), d, r0)
    split = shell_potential(density, d, R, mass, lmax, r0)+rereference(relief_potential(hs_grid, density, R, mass, lmax, 8), R, r0)
    assert np.max(np.abs(whole-split)[:, 1:, :]) < 1e-9*np.max(np.abs(whole[:, 1:, :]))


def test_grid_helpers():
    g = np.arange(8*16, dtype=float).reshape(8, 16)
    assert grid_value(g, 90, 0) == 0.
    assert weighted_mean(np.ones((8, 16)), np.ones((8, 16), bool)) == pytest.approx(1.0)


def test_epoch_features():
    assert epoch_features('eNh')['rank'] == 1 and epoch_features('eNh')['noachian'] == 1
    assert epoch_features('HNb')['rank'] == pytest.approx((2+4.5)/2) and epoch_features('HNb')['mixed'] == 1
    assert epoch_features('lApc')['rank'] == 8 and epoch_features('lApc')['amazonian'] == 1
    assert epoch_features('AHv')['hesperian'] == 1 and epoch_features('AHv')['amazonian'] == 1
    with pytest.raises(ValueError):
        epoch_features('xyz')
    assert age_features(['eNh', 'lAv']).shape == (2, 5)


def test_skill_definition():
    y = np.array([1., 2., 3.]); w = np.ones(3)
    assert skill(y, y, w, 2.) == 1.0
    assert skill(y, np.full(3, 2.), w, 2.) == 0.0
    assert skill(y, np.zeros(3), w, 2.) < 0


def test_heat_production_decays_toward_present():
    now = heat_production_w_kg(0., 3000., 0.7, 0.19)
    early = heat_production_w_kg(4.5, 3000., 0.7, 0.19)
    assert 3 < early/now < 10
    # a chondritic-like rock today: order 1e-11 W/kg
    assert 1e-12 < heat_production_w_kg(0., 300., 0.056, 0.016) < 1e-10


def test_basal_flux_meets_both_endpoints():
    """Audit control: the present-day flux must equal the declared value at the present day."""
    p = HistoryParameters(40, 3, .7, 4500, .27, 15, 60, 3, 220)
    assert p.basal_flux_w_m2(0.)*1000 == pytest.approx(60.)
    assert p.basal_flux_w_m2(4500.)*1000 == pytest.approx(15.)
    assert 15 < p.basal_flux_w_m2(2000.)*1000 < 60
    with pytest.raises(ValueError):
        run_history(HistoryParameters(40.5, 3, .7, 4500, .27, 15, 60, 3, 220), step_myr=10., cell_km=1.)


def test_poisson_reversals_cancel_less_than_periodic_ones():
    """Audit control: equal chrons cancel far more efficiently than random ones."""
    p = HistoryParameters(thickness_km=40, conductivity=3., th_ppm=0.7, k_over_th=4500, u_over_th=0.27,
                          basal_flux_now_mw=15, basal_flux_early_mw=60, basal_decay_gyr=1.5, surface_temperature_k=220)
    h = run_history(p, step_myr=10., cell_km=2.)
    periodic, known = coherent_fractions(h, 15, (703.15, 853.15), 1.0, 16, 'periodic')
    poisson, _ = coherent_fractions(h, 15, (703.15, 853.15), 1.0, 64, 'poisson', seed=5)
    duration = cooling_duration_myr(h, 15, (703.15, 853.15))
    assert np.median(periodic) < np.median(poisson) < 0.2
    # random telegraph averaged over the cooling time: rms about sqrt(chron/duration)
    assert np.sqrt(np.mean(poisson**2)) == pytest.approx(np.sqrt(1.0/duration), rel=0.6)


def test_history_cools_and_records_in_order():
    p = HistoryParameters(thickness_km=40, conductivity=3., th_ppm=0.7, k_over_th=4500, u_over_th=0.27,
                          basal_flux_now_mw=15, basal_flux_early_mw=60, basal_decay_gyr=1.5, surface_temperature_k=220)
    h = run_history(p, step_myr=10., cell_km=2.)
    assert np.all(np.diff(h.temperature_k[:, 20]) <= 1e-9)  # monotonic cooling at 40 km
    ages, status = acquisition_ages(h, [598.15, 853.15])
    deep = ages[15]  # 30 km
    assert status[15].tolist() == [1, 1]
    assert deep[1] > deep[0]  # magnetite Curie point is crossed before the cooler pyrrhotite point
    duration = cooling_duration_myr(h, 15, (703.15, 853.15))
    assert duration is not None and duration > 0
    steady, known = coherent_fraction(h, 15, (703.15, 853.15), 1e6)
    assert known == pytest.approx(1.0, abs=1e-9) and steady == pytest.approx(1.0, abs=1e-6)
    fast, _ = coherent_fraction(h, 15, (703.15, 853.15), 1.0)
    assert fast < 0.05


def test_isotherm_and_envelope():
    depth = np.arange(0, 41000., 1000.); temperature = 220+10*depth/1000
    assert isotherm_depth_km(depth, temperature, 320.) == pytest.approx(10.)
    assert isotherm_depth_km(depth, temperature, 5000.) is None
    ok, values = profile_within_envelope(depth, temperature, [10, 20], [300, 400], [340, 440], 0.)
    assert ok and values.tolist() == [320., 420.]
    assert not profile_within_envelope(depth, temperature, [10], [400], [440], 0.)[0]


def test_sampling_respects_ranges():
    samples = sample_parameters(50, {'a': (0, 1), 'b': (10, 20)}, seed=3)
    assert len(samples) == 50 and all(0 <= s['a'] <= 1 and 10 <= s['b'] <= 20 for s in samples)


def test_required_magnetization_inverts_operator():
    op = cylinder_axis_operator(100., [10.], [30.], [150.])[0, 0]
    assert required_magnetization(5*op, 100., 10., 30., 150.) == pytest.approx(5.)
    assert coherence_penalty(2., 0.5) == pytest.approx(4.)
    with pytest.raises(ValueError):
        coherence_penalty(1., 0.)


def test_window_statistics_constant_field():
    lat = np.arange(-89.5, 90); lon = np.arange(.5, 360)
    st = window_statistics(np.full((180, 360), 7.), lat, lon, 10., 20., 10.)
    assert st['rms'] == pytest.approx(7.) and st['max'] == 7. and st['cells'] > 100


def test_saved_outputs_match_their_manifest():
    import hashlib, json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]/'research/discriminating'
    manifest = json.loads((root/'manifest.json').read_text())
    assert not manifest['quick'], 'The committed outputs must come from a full build'
    for name, digest in manifest['outputs_sha256'].items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest() == digest, name
    protocol = json.loads((root/'protocol.json').read_text())
    crust = json.loads((root/'crust_inversion.json').read_text())
    assert {s['id'] for s in crust['scenarios']} == {s['id'] for s in protocol['crust_inversion']['scenarios']}
    assert crust['benchmark_relative_difference_vs_pyshtools'] < 1e-8
    assert crust['validation_equal_2900']['weighted_rms_difference_km'] < 6
    assert all(abs(s['insight_km']-39) < 0.05 and s['converged'] for s in crust['scenarios'])
    thermal = json.loads((root/'thermal_ensemble.json').read_text())
    assert all(h['accepted'] >= 20 for h in thermal['hemispheres'].values())
    surface = json.loads((root/'surface_check.json').read_text())['sites']['Zhurong']
    assert abs(surface['prediction_at_reference_sphere_degree_134_total_nt']-surface['published_downward_continuation_total_nt']) < 5
