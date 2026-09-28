"""Exact checks for the depth–age follow-up helpers."""
import numpy as np
import pytest

from marswind.depth_age import surface_summary, rankdata, spearman, wedge_labels, block_bootstrap_spearman, binned_means


def test_surface_summary_weights_and_unassigned():
    lat = np.arange(-89, 90, 2.); lon = np.arange(1, 360, 2.)
    LA, LO = np.meshgrid(lat, lon, indexing='ij')
    rank = np.where(LA > 0, 2., 6.); noach = np.where(LA > 0, 1., 0.)
    s = surface_summary(LA, LO, rank, noach, 30., 100., 5.)
    assert s['noachian_fraction'] == pytest.approx(1.) and s['mean_rank'] == pytest.approx(2.) and s['unassigned_fraction'] == 0.
    rank[:, :] = np.nan
    s = surface_summary(LA, LO, rank, noach, 30., 100., 5.)
    assert np.isnan(s['noachian_fraction']) and s['unassigned_fraction'] == pytest.approx(1.)
    with pytest.raises(ValueError):
        surface_summary(LA, LO, rank, noach, 30., 100., 0.01)


def test_rankdata_and_spearman():
    assert rankdata([10, 20, 20, 30]).tolist() == [1., 2.5, 2.5, 4.]
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.)
    assert spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.)
    assert np.isnan(spearman([1, 1, 1], [1, 2, 3]))
    assert spearman([1, 2, np.nan, 4], [1, 2, 3, 4]) == pytest.approx(1.)


def test_wedges_and_block_bootstrap():
    lon = np.array([5., 65., 125., 185., 245., 305.])
    assert wedge_labels(lon, 6).tolist() == [0, 1, 2, 3, 4, 5]
    assert wedge_labels(lon, 6, 30.).tolist() == [5, 0, 1, 2, 3, 4]
    rng = np.random.default_rng(1)
    lons = rng.uniform(0, 360, 120); x = rng.normal(size=120); y = 2*x+0.01*rng.normal(size=120)
    boot = block_bootstrap_spearman(x, y, wedge_labels(lons, 6), draws=200, seed=2)
    assert boot['rho'] > 0.99 and boot['q05'] > 0.95 and boot['blocks'] == 6 and boot['fraction_of_draws_with_opposite_sign'] == 0.
    with pytest.raises(ValueError):
        block_bootstrap_spearman(x, y, np.zeros(120, int))


def test_binned_means():
    out = binned_means([0.1, 0.2, 0.6, 0.9], [10, 20, 30, 40], [0, .5, 1.01])
    assert out[0]['count'] == 2 and out[0]['mean'] == 15. and out[1]['median'] == 35.
    assert binned_means([0.1], [1.], [0, .5, 1.01])[1]['mean'] is None
