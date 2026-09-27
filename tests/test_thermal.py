"""Analytic and physical checks for the independent conductive column."""
import numpy as np
import pytest
import hashlib
import json
from pathlib import Path

from marswind.thermal import Column, HeatPulse, SECONDS_PER_MYR, eigenmode_benchmark, solve, steady_temperature


def test_exact_steady_state_with_heat_production_and_upward_basal_flux():
    column = Column(cells=50)
    initial = steady_temperature(column, .03, 4e-8)
    history = solve(column, 100, 1, lambda t: .03, lambda t: 4e-8, initial)
    np.testing.assert_allclose(history.temperature_k, np.broadcast_to(initial, history.temperature_k.shape), atol=2e-9, rtol=0)
    # Analytic surface flux equals basal flux plus heat produced in the column.
    dz = column.thickness_m/column.cells
    derivative = (-3*initial[0]+4*initial[1]-initial[2])/(2*dz)
    assert column.conductivity_w_m_k*derivative == pytest.approx(.03+4e-8*column.thickness_m)


def test_transient_matches_mixed_boundary_eigenmode_and_converges():
    errors = [eigenmode_benchmark(cells=400, step_myr=dt) for dt in [1., .5, .25]]
    assert errors[0]/errors[1] > 1.9
    assert errors[1]/errors[2] > 1.9
    assert eigenmode_benchmark() < .08  # K, from a 100 K initial anomaly
    spatial = [eigenmode_benchmark(cells=n, step_myr=.005, duration_myr=1.) for n in [10, 20, 40]]
    assert spatial[0]/spatial[1] > 3.0
    assert spatial[1]/spatial[2] > 2.0  # Eventually limited by first-order time error


def test_no_spurious_heating_in_a_source_free_column():
    column = Column(cells=50)
    initial = column.surface_temperature_k + 100*np.sin(np.pi*column.depth_m/(2*column.thickness_m))
    history = solve(column, 100, 2, lambda t: 0., lambda t: 0., initial)
    assert np.all(history.temperature_k >= column.surface_temperature_k-1e-10)
    assert np.max(np.diff(history.temperature_k, axis=0)) < 1e-10


def test_discrete_energy_balance_includes_bottom_half_cell():
    column = Column(cells=50)
    initial = np.full(column.cells+1, column.surface_temperature_k)
    dt_myr, q, h = .5, .03, 4e-8
    history = solve(column, dt_myr, dt_myr, lambda t: q, lambda t: h, initial)
    temperature = history.temperature_k[-1]
    dz = column.thickness_m/column.cells
    # Dynamic volume excludes the prescribed-temperature surface half-cell.
    energy = (column.density_kg_m3*column.heat_capacity_j_kg_k
              * dz*(np.sum(temperature[1:-1]-initial[1:-1])+(temperature[-1]-initial[-1])/2))
    outgoing = column.conductivity_w_m_k*(temperature[1]-temperature[0])/dz
    assert energy == pytest.approx(dt_myr*SECONDS_PER_MYR*(q+h*(column.thickness_m-dz/2)-outgoing), rel=1e-10)


def test_pulse_is_instantaneous_and_future_exclusion_uses_the_peak():
    column = Column(cells=50)
    initial = np.full(column.cells+1, 220.)
    pulse = HeatPulse(1., 500., 25_000., 5000.)
    history = solve(column, 2., .25, lambda t: 0., lambda t: 0., initial, (pulse,))
    np.testing.assert_allclose(history.temperature_k[:4], 220., atol=1e-10)
    np.testing.assert_allclose(history.temperature_k[4], initial+pulse.profile(column), atol=1e-10)
    assert history.pulses[0]['added_energy_j_m2'] > 0
    peak = history.future_peak_k()
    assert history.temperature_k[0, 25] < 598.15 < peak[0, 25]
    assert np.all(np.diff(peak, axis=0) <= 0)
    np.testing.assert_array_equal(peak[-1], history.temperature_k[-1])


def test_events_and_invalid_inputs_are_not_silently_changed():
    column = Column()
    initial = np.full(101, 220.)
    with pytest.raises(ValueError, match="integer"):
        solve(column, 1., .3, lambda t: 0., lambda t: 0., initial)
    with pytest.raises(ValueError, match="grid"):
        solve(column, 1., .25, lambda t: 0., lambda t: 0., initial, (HeatPulse(.3, 5., 25000., 5000.),))
    with pytest.raises(ValueError, match="surface"):
        solve(column, 1., .25, lambda t: 0., lambda t: 0., initial+1)
    with pytest.raises(ValueError, match="sources"):
        solve(column, 1., .25, lambda t: float('nan'), lambda t: 0., initial)
    with pytest.raises(ValueError):
        Column(cells=1)


def test_refined_event_grid_preserves_base_times_and_pulse_energy():
    column = Column(cells=50)
    initial = np.full(51, 220.)
    pulse = HeatPulse(1., 500., 25000., 5000.)
    fine = solve(column, 3., .25, lambda t: 0., lambda t: 0., initial, (pulse,),
                 pulse_step_myr=.03125, pulse_window_myr=1.)
    assert set(np.arange(0, 3.25, .25)) <= set(fine.time_myr)
    assert np.all(np.diff(fine.time_myr) > 0)
    at_event = np.flatnonzero(fine.time_myr == 1.)[0]
    np.testing.assert_allclose(fine.temperature_k[:at_event], 220., atol=1e-10)
    np.testing.assert_allclose(fine.temperature_k[at_event], initial+pulse.profile(column), atol=1e-10)
    assert fine.time_myr[at_event+1]-1. == .03125
    assert fine.time_myr[-1]-fine.time_myr[-2] == .25


def test_saved_experiment_has_current_provenance_and_qualified_exclusions():
    root = Path(__file__).resolve().parents[1]
    result = json.loads((root/'research/thermal/results.json').read_text())
    assert result['protocol'] == json.loads((root/'research/thermal/protocol.json').read_text())
    for relative, expected in result['provenance']['sha256'].items():
        assert hashlib.sha256((root/relative).read_bytes()).hexdigest() == expected, relative
    assert result['provenance']['downloads_required'] is False
    v = result['validation']
    assert v['steady_max_error_k'] < 1e-7 and v['transient_max_error_k'] < .08
    assert all(c['max_temperature_difference_k'] < 2 for c in v['scenario_comparisons'])
    for case in result['scenarios']:
        temperature, peak = np.array(case['temperature_k']), np.array(case['future_peak_k'])
        assert temperature.shape == peak.shape == (len(case['time_myr']), len(case['depth_km']))
        assert np.isfinite(temperature).all() and np.isfinite(peak).all()
        assert np.all(peak >= temperature)
        assert np.all(np.diff(peak, axis=0) <= 0)
        assert case['time_myr'][0] == 0 and case['time_myr'][-1] == 4000
        assert 'survival' not in case and 'probability' not in case
    cooling, reheating = result['scenarios']
    for case, expected in [(cooling, 0), (reheating, 1)]:
        i, j = case['time_myr'].index(500), case['depth_km'].index(25)
        assert case['gates']['magnetite'][i][j] == expected
