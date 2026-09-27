"""Analytic physical limits, conservation and non-identifiability controls."""
import numpy as np
import pytest
from marswind.dichotomy_physics import (column_support, layered_density,
    thermal_susceptibility, modal_power_share, rigidity, flexure,
    boundary_proxy, arai_example)


def test_equal_pressure_columns_and_dense_layer_mass_balance():
    rm, rn, rs, hn, hs = 3500., 2900., 2600., 30., 60.
    dh = column_support(hs, rs, rm)-column_support(hn, rn, rm)
    # Direct integrated overburden mass at a common level 150 km below north.
    assert rs*hs+rm*(150+dh-hs) == pytest.approx(rn*hn+rm*(150-hn))
    rho = layered_density(50, 14, 2700, 3400)
    assert rho*50 == pytest.approx(36*2700+14*3400)
    assert rho > 2700
    assert layered_density(50, 0, 2700, 3400, .1) == pytest.approx(2430)
    assert column_support(40, rm, rm) == 0


def test_spherical_poisson_shell_against_exact_degree_zero_and_refinement():
    b = 1-100/3390
    exact = (.5-1.5*b*b+b**3)/3
    errors = [abs(thermal_susceptibility(0, cells=n)-exact) for n in [50, 100, 200]]
    assert errors[1] < errors[0]/3.5
    assert errors[2] < errors[1]/3.5
    assert errors[-1]/exact < 2e-6
    values = [thermal_susceptibility(l) for l in [0, 1, 2, 10, 40]]
    assert np.all(np.diff(values) < 0) and min(values) > 0
    assert thermal_susceptibility(2, cells=800) == pytest.approx(values[2], rel=2e-6)


@pytest.mark.parametrize('degree', [1, 3, 10, 40])
def test_nonzero_harmonics_against_closed_form_shell_solution(degree):
    # u = A*x^l + B*x^(-l-1) + C*x^2. This independently checks the
    # angular term and the basal Neumann condition (l=2 is resonant).
    b = 1-200/3390
    c = 1/(degree*(degree+1)-6)
    a, d = np.linalg.solve([[1, 1],
        [degree*b**(degree-1), -(degree+1)*b**(-degree-2)]], [-c, -2*c*b])
    exact = a*b**degree+d*b**(-degree-1)+c*b*b
    assert thermal_susceptibility(degree, lid_km=200, cells=800) == pytest.approx(exact, rel=3e-7)


def test_modal_power_zero_growth_and_growth_degeneracy():
    power = np.array([3., 5., 7.])
    np.testing.assert_allclose(modal_power_share([1, .9, .8], 0, power), power/power.sum())
    np.testing.assert_allclose(modal_power_share([1, 1, 1], 1000, power), power/power.sum())
    assert modal_power_share([1, .5, .1], 10, power)[0] > .999


def test_elastic_sinusoid_exact_transfer_and_local_compensation():
    n, dx = 512, 10000.
    x = np.arange(n)*dx
    k = 2*np.pi*8/(n*dx)
    load = 1200*np.cos(k*x)
    expected = load*2900*3.71/(rigidity(30)*k**4+3500*3.71)
    np.testing.assert_allclose(flexure(load, dx, 30, padding=0), expected, atol=1e-11)
    np.testing.assert_allclose(flexure(load, dx, 0), load*2900/3500, atol=1e-11)
    np.testing.assert_allclose(flexure(np.ones(n)*1000, dx, 60, padding=0), 1000*2900/3500)


def test_isolated_load_mass_balance_padding_and_sign():
    x = np.arange(-2000, 2001, 10.)
    load = 1000*np.exp(-.5*(x/100)**2)
    w = flexure(load, 10000, 30)
    assert w.sum()*3500 == pytest.approx(load.sum()*2900, rel=1e-5)
    np.testing.assert_allclose(w, flexure(load, 10000, 30, padding=4), atol=1e-8)
    np.testing.assert_allclose(flexure(-load, 10000, 30), -w, atol=1e-10)


def test_boundary_recovery_and_nonunique_loading_histories():
    x = np.arange(-1500, 1501, 10.)
    original = -2*np.tanh(x/80)
    load = 1500*np.exp(-.5*((x-150)/100)**2)
    observed = original+(load-flexure(load, 10000, 30))/1000
    restored = observed-(load-flexure(load, 10000, 30))/1000
    assert boundary_proxy(x, original)['x_km'] == 0
    assert boundary_proxy(x, restored)['x_km'] == 0
    np.testing.assert_allclose(original, restored, atol=1e-12)
    # A no-load history also fits the observed relief exactly: relief alone
    # cannot identify the load or an earlier edge.
    assert np.max(abs(original-observed)) > .05


def test_perfect_arai_line_can_have_wrong_intensity():
    for ratio in [.5, 1., 2.]:
        result = arai_example(efficiency_ratio=ratio)
        x, y = result['lab_ptrm_normalized'], result['nrm_remaining_normalized']
        slope, intercept = np.polyfit(x, y, 1)
        np.testing.assert_allclose(np.polyval([slope, intercept], x), y, atol=1e-14)
        assert result['apparent_field_ut'] == pytest.approx(25*ratio)


def test_invalid_physical_inputs_are_rejected():
    for call in [lambda: layered_density(10, 14, 2600, 3400),
                 lambda: thermal_susceptibility(1.5),
                 lambda: rigidity(-1), lambda: arai_example(laboratory_field_ut=0),
                 lambda: flexure([0]*10, 0, 30),
                 lambda: modal_power_share([1], 1, [0])]:
        with pytest.raises(ValueError): call()


def test_saved_products_match_the_audited_sources_and_numerical_run():
    import hashlib
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root/'research/physics/manifest.json').read_text())
    assert manifest['downloads_required'] is False
    for name, digest in (manifest['inputs'] | manifest['outputs']).items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest() == digest, name
    provenance = json.loads((root/'research/physics/input_provenance.json').read_text())
    for name, digest in provenance['generated_inputs'].items():
        assert hashlib.sha256((root/'research/physics'/name).read_bytes()).hexdigest() == digest
