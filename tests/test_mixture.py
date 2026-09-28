"""Analytic mass balance and independently optimized material bounds."""
import numpy as np
import pytest
from scipy.optimize import linprog
from marswind.mixture import Mixture


def test_known_units_and_inverse_recover_the_mixture():
    m = Mixture()
    density, magnetization = m.forward(.001, .1)
    assert density == pytest.approx(2612.052)
    assert magnetization == pytest.approx(4.5)
    x = m.inverse(density, magnetization)
    assert x['physical']
    assert x['porosity'] == pytest.approx(.1)
    assert x['solid_carrier_fraction_in_source'] == pytest.approx(.001)


def test_zero_carrier_and_pure_endpoints_conserve_mass():
    m = Mixture(pore_density=1000)
    assert m.forward(0, 0) == (2900, 0)
    assert m.forward(1, 0) == (5180, 5000)
    assert m.forward(.4, 1) == (1000, 0)
    result = m.inverse(2492, 0)
    assert result['porosity'] == pytest.approx((2900-2492)/(2900-1000))
    assert result['solid_carrier_fraction_in_source'] == 0


def test_source_occupancy_averages_density_but_not_local_magnetization():
    full, partial = Mixture(), Mixture(source_fraction=.25)
    rho_source, mag = full.forward(.03, .15)
    rho_background, _ = full.forward(0, .15)
    density, local_mag = partial.forward(.03, .15)
    assert density == pytest.approx(.25*rho_source+.75*rho_background)
    assert local_mag == mag
    result = partial.inverse(density, mag)
    assert result['porosity'] == pytest.approx(.15)
    assert result['solid_carrier_fraction_in_source'] == pytest.approx(.03)


def test_cancellation_is_applied_exactly_once():
    # Asking for net 4 A/m with 2% retention is equivalent to 200 A/m before it.
    net = Mixture(coherence=.02).inverse(2492, 4)
    already_corrected = Mixture(coherence=1).inverse(2492, 200)
    assert net == already_corrected


def test_algebraic_candidate_is_not_silently_clipped_to_physical_range():
    assert not Mixture(matrix_density=2400).inverse(2622, 1)['physical']
    assert not Mixture().inverse(2492, 10000)['physical']
    assert Mixture().attainable(2492, .1, .05) is None


@pytest.mark.parametrize('rho,rm,rp,q,pmax,fmax', [
    (2492,2900,0,1,.2,.05), (2622,2900,0,1,.2,.05),
    (2492,2400,0,1,.3,.1), (2492,2900,1000,.25,.3,.1),
    (2492,2900,0,1,.1,.05), (2622,2600,0,.5,0,.01),
    (2900,2900,0,1,0,0),
])
def test_attainable_interval_agrees_with_independent_linear_program(rho,rm,rp,q,pmax,fmax):
    m = Mixture(matrix_density=rm, pore_density=rp, source_fraction=q)
    interval = m.attainable(rho, pmax, fmax)
    kwargs = dict(A_eq=[[-(rm-rp),q*(5180-rm)]], b_eq=[rho-rm],
                  A_ub=[[fmax,1]], b_ub=[fmax], bounds=[(0,pmax),(0,None)], method='highs')
    lo = linprog([0,1], **kwargs); hi = linprog([0,-1], **kwargs)
    assert (interval is not None) == lo.success == hi.success
    if interval is not None:
        assert interval['magnetization_low_a_m'] == pytest.approx(lo.x[1]*5000, abs=1e-9)
        assert interval['magnetization_high_a_m'] == pytest.approx(hi.x[1]*5000, abs=1e-9)


def test_parameters_reject_undefined_physics():
    for bad in [dict(coherence=0),dict(source_fraction=2),dict(pore_density=3000),dict(carrier_remanence=np.nan)]:
        with pytest.raises(ValueError): Mixture(**bad)
