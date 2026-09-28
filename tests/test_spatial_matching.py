"""Analytic geometry and assignment/dependence counterexamples."""
import numpy as np
import pytest

from marswind.spatial_matching import (polyline_distance_km, caliper_match,
    block_labels, pair_block_components, standardized_balance)


def test_geodesic_distance_crosses_zero_longitude_without_long_way_round():
    radius = 3389.5
    d = polyline_distance_km([10, 0, 0], [0, 359, 20], [[350, 0], [10, 0]], radius, step_km=1)
    expected = np.deg2rad([10, 0, 10])*radius
    assert np.all(d >= expected-1e-8)
    assert np.all(d-expected <= .500001)


def test_assignment_finds_two_pairs_where_nearest_first_greedy_would_find_one():
    a = np.array([[.4], [0.]])
    b = np.array([[0.], [1.]])
    ia, ib, cost = caliper_match(a, b, [1, 1], [1, 1], [.7])
    assert list(zip(ia, ib)) == [(0, 1), (1, 0)]
    assert np.all(cost <= 1)


def test_assignment_respects_epoch_and_calipers_even_when_unmatched():
    ia, ib, _ = caliper_match(np.array([[0.], [5.]]), np.array([[0.], [5.]]), [1, 2], [2, 1], [.1])
    assert len(ia) == len(ib) == 0
    with pytest.raises(ValueError):
        caliper_match(np.array([[np.nan]]), np.array([[0.]]), [1], [1], [1])


def test_shared_blocks_merge_transitively_and_across_pair_roles():
    # Third pair's treatment block occurs as a control in the second pair.
    c = pair_block_components(['a', 'a', 'c', 'x'], ['b', 'c', 'd', 'y'])
    assert c[0] == c[1] == c[2]
    assert c[3] != c[0]
    assert len(pair_block_components([], [])) == 0


def test_block_labels_are_invariant_to_longitude_convention():
    assert np.array_equal(block_labels([10, 20], [-1, 5], 300), block_labels([10, 20], [359, 365], 300))


def test_post_balance_uses_the_target_area_weights_on_both_sides():
    a = np.array([[1.], [5.]])
    b = np.array([[1.], [5.]])
    pre, post = standardized_balance(a, b, np.array([1., 3.]), np.array([3., 1.]), [0, 1], [0, 1])
    assert pre[0] != 0
    assert post[0] == 0
