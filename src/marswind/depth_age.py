"""Equivalent magnetic source depth against the age of the overlying surface.

Small, testable pieces for the depth–age follow-up: surface-age summaries of
the 2° geological atlas inside an angular window, a rank correlation, and a
block bootstrap over longitude wedges that respects the strong overlap of the
source-depth windows. No p-value is produced; the bootstrap gives an interval
for the rank correlation under the declared block scheme only.
"""
import numpy as np


def angular_distance_deg(lat, lon, lat0, lon0):
    p, p0 = np.deg2rad(lat), np.deg2rad(lat0)
    dl = np.deg2rad(np.asarray(lon)-lon0)
    a = np.sin((p-p0)/2)**2+np.cos(p)*np.cos(p0)*np.sin(dl/2)**2
    return np.rad2deg(2*np.arcsin(np.sqrt(np.clip(a, 0, 1))))


def surface_summary(lat_grid, lon_grid, rank_grid, noachian_grid, center_lat, center_lon, radius_deg):
    """Area-weighted Noachian fraction and mean epoch rank inside an angular radius.

    Cells without an assigned unit (rank NaN) are excluded from both numerator
    and denominator; their fraction is reported so callers can screen windows.
    """
    dist = angular_distance_deg(lat_grid, lon_grid, center_lat, center_lon)
    inside = dist <= radius_deg
    if not inside.any():
        raise ValueError('Empty window')
    w = np.cos(np.deg2rad(lat_grid))[inside]
    rank = np.asarray(rank_grid, float)[inside]; noach = np.asarray(noachian_grid, float)[inside]
    valid = np.isfinite(rank)
    unassigned = float(np.sum(w[~valid])/np.sum(w))
    if not valid.any():
        return {'noachian_fraction': np.nan, 'mean_rank': np.nan, 'unassigned_fraction': unassigned, 'cells': int(inside.sum())}
    return {'noachian_fraction': float(np.sum(w[valid]*noach[valid])/np.sum(w[valid])),
            'mean_rank': float(np.sum(w[valid]*rank[valid])/np.sum(w[valid])),
            'unassigned_fraction': unassigned, 'cells': int(inside.sum())}


def rankdata(values):
    """Average ranks for ties, 1-based."""
    v = np.asarray(values, float)
    order = np.argsort(v, kind='mergesort')
    ranks = np.empty(len(v), float)
    sorted_v = v[order]
    i = 0
    while i < len(v):
        j = i
        while j+1 < len(v) and sorted_v[j+1] == sorted_v[i]:
            j += 1
        ranks[order[i:j+1]] = (i+j)/2+1
        i = j+1
    return ranks


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 3:
        return np.nan
    rx, ry = rankdata(x[ok]), rankdata(y[ok])
    if rx.std() == 0 or ry.std() == 0:
        return np.nan
    return float(np.corrcoef(rx, ry)[0, 1])


def wedge_labels(lon, wedges=6, offset_deg=0.):
    return ((np.asarray(lon, float)-offset_deg) % 360*wedges//360).astype(int)


def block_bootstrap_spearman(x, y, blocks, draws=2000, seed=0):
    """Resample whole blocks with replacement; return rho and its 5–95% interval.

    Blocks are the unit of resampling because the windows inside a block share
    sources and are not independent. With few blocks the interval is coarse;
    the number of blocks is returned so that readers can judge it.
    """
    x, y, b = np.asarray(x, float), np.asarray(y, float), np.asarray(blocks)
    labels = np.unique(b)
    if len(labels) < 3:
        raise ValueError('At least three blocks are required')
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(draws):
        chosen = rng.choice(labels, size=len(labels), replace=True)
        idx = np.concatenate([np.flatnonzero(b == c) for c in chosen])
        values.append(spearman(x[idx], y[idx]))
    values = np.array(values)
    values = values[np.isfinite(values)]
    return {'rho': spearman(x, y), 'q05': float(np.quantile(values, .05)), 'q95': float(np.quantile(values, .95)),
            'blocks': int(len(labels)), 'draws': int(len(values)),
            'fraction_of_draws_with_opposite_sign': float(np.mean(np.sign(values) != np.sign(spearman(x, y)))) if np.isfinite(spearman(x, y)) else np.nan}


def binned_means(x, y, edges):
    """Mean of y in declared bins of x, with counts; NaN where a bin is empty."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = (x >= lo) & (x < hi) & np.isfinite(y)
        out.append({'low': float(lo), 'high': float(hi), 'count': int(sel.sum()), 'mean': float(y[sel].mean()) if sel.any() else None,
                    'median': float(np.median(y[sel])) if sel.any() else None})
    return out
