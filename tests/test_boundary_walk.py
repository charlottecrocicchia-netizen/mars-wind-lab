"""Known spherical geometry, closed-curve weights and sign-flip controls."""
import numpy as np
from marswind.boundary_walk import (ClosedCurve, advance, lat_lon, block_operator,
    sign_patterns, reference_tails, synthetic_calibration)


def equator():
    return ClosedCurve(np.column_stack((np.arange(0, 361, 5), np.zeros(73))))


def test_closed_curve_drops_duplicate_and_weights_integrate_circumference():
    curve = equator()
    assert len(curve.points) == 72
    assert np.isclose(curve.length, 2*np.pi*curve.radius_km)
    assert np.isclose(curve.weights.sum(), curve.length)
    assert np.allclose(curve.at(curve.arc), curve.points)
    assert np.allclose(curve.at(curve.arc+curve.length), curve.points)


def test_normals_and_offsets_are_exact_on_equator():
    curve = equator(); normal = curve.normals(100)
    assert np.allclose(normal, [0, 0, -1])
    south = advance(curve.points, normal, 600, curve.radius_km)
    north = advance(curve.points, normal, -600, curve.radius_km)
    slat, slon = lat_lon(south); nlat, nlon = lat_lon(north)
    assert np.allclose(slat, -np.rad2deg(600/curve.radius_km))
    assert np.allclose(nlat, -slat)
    assert np.allclose(slon % 360, nlon % 360)


def test_uneven_vertices_do_not_change_constant_boundary_integral():
    points = np.column_stack(([0, 1, 3, 10, 40, 90, 170, 250, 330, 360], np.zeros(10)))
    curve = ClosedCurve(points)
    assert np.isclose(np.sum(3*curve.weights)/curve.length, 3)
    matrix, labels, coverage, width = block_operator(curve, np.ones(len(curve.points), bool), minimum_weight_km=0.1)
    assert len(labels) == len(matrix) == len(coverage)
    assert np.allclose(matrix.sum(axis=1), 1)
    assert np.allclose(matrix @ np.full(len(curve.points), 3.), 3)


def test_exact_sign_reference_has_expected_extreme_and_zero_tails():
    signs, exact = sign_patterns(4)
    assert exact and len(signs) == 16
    assert reference_tails(np.ones(4), signs, exact)[0] == 2/16
    assert reference_tails(np.zeros(4), signs, exact)[0] == 1


def test_sign_flips_are_invariant_to_block_order():
    values = np.array([1., -2., 4., -1., 3.])
    signs, exact = sign_patterns(5)
    assert reference_tails(values, signs, exact)[0] == reference_tails(values[::-1], signs, exact)[0]


def test_shared_global_null_exposes_false_independent_block_sign_flips():
    # Every block sees the same two field locations: perfectly dependent errors.
    positions = np.array([[1., 0, 0], [0., 1., 0]])
    operator = np.tile([1., -1.], (8, 1))
    result = synthetic_calibration(operator, positions, lengths=[500], features=64, trials=80)
    assert result[0]['false_positive_rate_at_005'] > .9
