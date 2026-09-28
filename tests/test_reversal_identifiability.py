import numpy as np
import pytest

from marswind.reversal_identifiability import (
    PiecewiseClock, warp_kernel, record_explicit_events, radial_dipole_operator,
    flip_probability, fit_dated_signs, profile_unknown_spacing,
)


def test_hazard_and_inverse_cross_the_break():
    clock = PiecewiseClock(100, .15, 1.5, 1.5)
    t = np.array([0, 50, 100, 101, 200.])
    np.testing.assert_allclose(clock.warp(t), [0, 5, 10, 11, 110])
    np.testing.assert_allclose(clock.inverse_hazard(clock.hazard(t)), t)
    with pytest.raises(ValueError):
        PiecewiseClock(100, 0, 1.5, 1.5)


def test_acquisition_mass_and_record_survive_piecewise_warp():
    clock = PiecewiseClock(100, .15, 1.5, 1.5)
    kernel = {'start': np.array([40., 90.]), 'end': np.array([80., 120.]), 'weight': np.array([.3, .7])}
    events = np.array([12., 47., 70., 95., 103., 109., 130.])
    pushed = warp_kernel(kernel, clock)
    assert len(pushed['weight']) == 3
    assert pushed['weight'].sum() == pytest.approx(1)
    # The activity gate also cuts through intervals, on both sides of the break.
    for window in [(0., 200.), (55., 111.)]:
        before = record_explicit_events(kernel, events, window)
        after = record_explicit_events(pushed, clock.warp(events), clock.warp(window))
        assert after == pytest.approx(before, abs=1e-13)


def test_event_integral_has_correct_sign_and_activity_fraction():
    kernel = {'start': np.array([0.]), 'end': np.array([10.]), 'weight': np.array([1.])}
    assert record_explicit_events(kernel, [2., 5.], (0., 10.)) == pytest.approx(.4)
    assert record_explicit_events(kernel, [2., 5.], (1., 7.)) == pytest.approx(0.)
    assert record_explicit_events(kernel, [], (2., 7.)) == pytest.approx(.5)


def test_uniform_clock_warp_agrees_with_a_different_conductive_thickness():
    from marswind.rapid_bodies import body_kernels
    clock = PiecewiseClock(100, .15, 1.5, 1.5)
    original, _ = body_kernels(3000., 1473.15, 573.15, 1e-6, (703.15, 853.15), positions=8)
    faster, _ = body_kernels(3000*np.sqrt(.1), 1473.15, 573.15, 1e-6, (703.15, 853.15), positions=8)
    for old, new in zip(original, faster):
        mapped = warp_kernel(old, clock)
        for key in ('start', 'end', 'weight'):
            np.testing.assert_allclose(mapped[key], new[key], atol=1e-13, rtol=1e-10)


def test_dipole_radial_field_has_si_units_and_polar_signs():
    r = 1e6
    observations = [[0, 0, r], [0, 0, -r], [r, 0, 0]]
    field = radial_dipole_operator([[0, 0, 0]], observations).ravel()*1e14
    np.testing.assert_allclose(field, [.02, -.02, 0.], atol=1e-15)


def test_likelihood_and_rate_recovery_for_exact_counts():
    equal = fit_dated_signs([[20, 20]], 1000, .1)
    assert equal['lr'][0] == pytest.approx(0.)
    changed = fit_dated_signs([[10, 130]], 1000, .1)
    assert changed['lr'][0] > 100
    np.testing.assert_allclose(flip_probability(changed['rates'], .1), [[.01, .13]])
    edge = fit_dated_signs([[0, 100]], 100, .1)
    assert np.isfinite(edge['lr']).all()


def test_unknown_clock_profiles_the_same_likelihood():
    k = np.array([[15, 130], [10, 100]])
    fixed = fit_dated_signs(k, 1000, .1)
    free = profile_unknown_spacing(k, 1000)
    assert free['feasible'].all()
    np.testing.assert_allclose(free['ll_profile'], fixed['ll_change'])
    np.testing.assert_allclose(flip_probability(free['common_rate'][:, None], free['spacings']), k/1000)
    assert not profile_unknown_spacing([[0, 100]], 1000)['feasible'][0]
    np.testing.assert_allclose(flip_probability([.15, 1.5], .1), flip_probability(1.5, [.01, .1]))
