"""Exact and limiting checks for the rapidly cooled body model."""
import numpy as np
import pytest

from marswind.rapid_bodies import (slab_temperature, body_kernels, body_retention, poisson_sign,
                                   stack_coherence, max_thickness_for_retention, SECONDS_PER_MYR,
                                   midplane_crossing_times, expected_stack_rms)

KAPPA = 1e-6


def test_slab_solution_limits():
    h, Te, Th = 1000., 1400., 500.
    assert slab_temperature(0., 0., h, Te, Th, KAPPA) == Te
    assert slab_temperature(2000., 0., h, Te, Th, KAPPA) == Th
    # contact temperature immediately after emplacement is the mean of both
    assert slab_temperature(h/2, 1e-3, h, Te, Th, KAPPA) == pytest.approx((Te+Th)/2, rel=1e-6)
    late = slab_temperature(0., 1e4*h**2/KAPPA, h, Te, Th, KAPPA)
    assert abs(late-Th) < 5.
    # monotonic cooling at the mid-plane and symmetry
    t = np.geomspace(1., 1e12, 50)
    centre = slab_temperature(0., t, h, Te, Th, KAPPA)
    assert np.all(np.diff(centre) <= 1e-9)
    assert slab_temperature(300., 1e9, h, Te, Th, KAPPA) == pytest.approx(slab_temperature(-300., 1e9, h, Te, Th, KAPPA))


def test_mid_plane_cooling_scales_with_thickness_squared():
    band = (703.15, 853.15)
    _, t1 = body_kernels(1000., 1473.15, 573.15, KAPPA, band)
    _, t10 = body_kernels(10000., 1473.15, 573.15, KAPPA, band)
    assert t10/t1 == pytest.approx(100.)


def test_kernel_weights_and_retention_limits():
    band = (703.15, 853.15)
    kernels, _ = body_kernels(1000., 1473.15, 573.15, KAPPA, band, positions=8, time_points=200)
    assert all(abs(k['weight'].sum()+k['unknown']+k['hot']-1) < 1e-9 for k in kernels)
    assert all(k['weight'].sum() > 0.999 for k in kernels)  # whole band crossed
    steady, known = body_retention(kernels, 'periodic', 1e6, 4)
    assert known == pytest.approx(1., abs=1e-6) and np.allclose(steady, 1., atol=1e-6)
    fast, _ = body_retention(kernels, 'poisson', 0.67, 16, seed=3)
    assert np.median(fast) > 0.99  # a 1 km body crosses this band in about 95 kyr
    thick, _ = body_kernels(30000., 1473.15, 573.15, KAPPA, band, positions=8, time_points=200)
    slow, _ = body_retention(thick, 'poisson', 0.67, 16, seed=3)
    assert np.median(slow) < 0.3
    with pytest.raises(ValueError):
        body_kernels(1000., 1473.15, 800., KAPPA, band)


def test_poisson_sign_and_stack_scaling():
    rng = np.random.default_rng(0)
    s = poisson_sign([0., 1., 2.], 5., rng)
    assert set(np.unique(s)).issubset({-1, 1}) and len(s) == 3
    one = stack_coherence(1, 100., 0.67, 200, seed=1)
    assert np.all(one == 1.)
    many = stack_coherence(100, 1000., 0.67, 400, seed=1)
    assert 0.03 < np.sqrt(np.mean(many**2)) < 0.2  # about 1/sqrt(100)
    single_chron = stack_coherence(50, 0.01, 1e6, 50, seed=2)
    assert np.all(single_chron == 1.)


def test_thickness_bound():
    assert max_thickness_for_retention([100, 1000, 10000], [0.99, 0.6, 0.1]) == 1000
    assert max_thickness_for_retention([100, 1000], [0.1, 0.05]) is None


def test_analytic_band_duration_excludes_time_before_upper_crossing():
    times = midplane_crossing_times(3000,1473.15,573.15,KAPPA,(703.15,853.15))
    for key, temperature in [('upper_crossing_myr',853.15),('lower_crossing_myr',703.15)]:
        assert slab_temperature(0,times[key]*SECONDS_PER_MYR,3000,1473.15,573.15,KAPPA) == pytest.approx(temperature)
    assert times['band_duration_myr'] == pytest.approx(.85341975799)
    assert times['band_duration_myr'] < times['lower_crossing_myr']


def test_correlated_stack_rms_matches_monte_carlo_and_limits():
    assert expected_stack_rms(100,0,.67) == 1
    assert expected_stack_rms(1,100,.67) == 1
    expected = expected_stack_rms(100,10,.67)
    assert expected == pytest.approx(.27222774473)
    values = stack_coherence(100,10,.67,4000,seed=83)
    assert abs(np.mean(values**2)-expected**2) < .004
    assert expected_stack_rms(100000,10,.67) > .25  # finite-span correlation floor
    assert expected_stack_rms(100,1e8,.67) == pytest.approx(.1,abs=1e-7)
