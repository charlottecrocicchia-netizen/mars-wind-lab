"""Synthetic reversal-clock identifiability, with no fitted Mars observations.

All times are elapsed Myr. A shared Poisson path is transformed together with
the acquisition kernels, preserving recorded moments path by path.
"""
from dataclasses import dataclass

import numpy as np
from scipy.special import xlogy


@dataclass(frozen=True)
class PiecewiseClock:
    switch_myr: float
    early_rate: float
    late_rate: float
    reference_rate: float

    def __post_init__(self):
        if not all(np.isfinite(x) and x > 0 for x in
                   (self.switch_myr, self.early_rate, self.late_rate, self.reference_rate)):
            raise ValueError('Positive finite switch time and rates required')

    def hazard(self, time):
        t = np.asarray(time, float)
        if np.any(t < 0) or not np.isfinite(t).all():
            raise ValueError('Finite nonnegative elapsed times required')
        return self.early_rate*np.minimum(t, self.switch_myr) + self.late_rate*np.maximum(t-self.switch_myr, 0)

    def inverse_hazard(self, exposure):
        h = np.asarray(exposure, float)
        if np.any(h < 0) or not np.isfinite(h).all():
            raise ValueError('Finite nonnegative cumulative hazard required')
        split = self.early_rate*self.switch_myr
        return np.minimum(h, split)/self.early_rate + np.maximum(h-split, 0)/self.late_rate

    def warp(self, time):
        return self.hazard(time)/self.reference_rate


def warp_kernel(kernel, clock):
    """Push forward a piecewise-uniform acquisition measure, preserving mass."""
    start, end, mass = (np.asarray(kernel[key], float) for key in ('start', 'end', 'weight'))
    if start.shape != end.shape or end.shape != mass.shape or np.any(end <= start) or np.any(mass < 0):
        raise ValueError('Matching ordered intervals and nonnegative masses required')
    a, b, w = [], [], []
    for left, right, weight in zip(start, end, mass):
        edges = [left, right]
        if left < clock.switch_myr < right:
            edges.insert(1, clock.switch_myr)
        for lo, hi in zip(edges[:-1], edges[1:]):
            a.append(float(clock.warp(lo)))
            b.append(float(clock.warp(hi)))
            w.append(weight*(hi-lo)/(right-left))
    return {'start': np.array(a), 'end': np.array(b), 'weight': np.array(w)}


def poisson_hazard_events(max_hazard, rng):
    """Unit-rate Poisson arrivals censored at the supplied finite horizon."""
    events, value = [], 0.
    while True:
        value += rng.exponential()
        if value >= max_hazard:
            return np.asarray(events)
        events.append(value)


def record_explicit_events(kernel, events, activity_window, initial_sign=1):
    """Exact signed acquisition on uniform intervals, including an on/off window."""
    events = np.asarray(events, float)
    if (events.ndim != 1 or np.any(np.diff(events) <= 0) or np.any(events <= 0)
            or not np.isfinite(events).all() or initial_sign not in (-1, 1)):
        raise ValueError('Ordered positive finite arrivals and a unit sign required')
    low, high = activity_window
    if low < 0 or high <= low:
        raise ValueError('Ordered nonnegative activity window required')
    a, b, w = (np.asarray(kernel[key], float) for key in ('start', 'end', 'weight'))
    if a.shape != b.shape or b.shape != w.shape or np.any(a < 0) or np.any(b <= a) or np.any(w < 0):
        raise ValueError('Valid acquisition intervals required')
    edges = np.r_[0., events]
    signs = initial_sign*(1-2*(np.arange(len(edges)) % 2))
    cumulative = np.r_[0., np.cumsum(np.diff(edges)*signs[:-1])]
    def primitive(t):
        index = np.searchsorted(events, t, side='right')
        return cumulative[index] + signs[index]*(t-edges[index])
    left, right = np.maximum(a, low), np.minimum(b, high)
    keep = right > left
    return float(np.sum(w[keep]*(primitive(right[keep])-primitive(left[keep]))/(b[keep]-a[keep])))


def radial_dipole_operator(source_xyz_m, observation_xyz_m):
    """Radial nT per A m² for parallel global-z point dipoles in vacuum."""
    src, obs = np.asarray(source_xyz_m, float), np.asarray(observation_xyz_m, float)
    if src.ndim != 2 or obs.ndim != 2 or src.shape[1] != 3 or obs.shape[1] != 3:
        raise ValueError('Cartesian arrays must have three columns')
    delta = obs[:, None, :]-src[None, :, :]
    distance = np.linalg.norm(delta, axis=2)
    radius = np.linalg.norm(obs, axis=1)
    if np.any(distance <= 0) or np.any(radius <= 0):
        raise ValueError('Observations must avoid source points and the origin')
    direction, radial = delta/distance[:, :, None], obs/radius[:, None]
    vector = 3*direction*direction[:, :, 2, None]-np.array([0., 0., 1.])
    # mu0/(4*pi) * tesla-to-nT = 100 in SI distance and moment units.
    return 100*np.einsum('ijk,ik->ij', vector, radial)/distance**3


def flip_probability(rate_per_myr, spacing_myr):
    """Probability of an odd Poisson count between instantaneous sign samples."""
    rate, dt = np.asarray(rate_per_myr), np.asarray(spacing_myr)
    if np.any(rate < 0) or np.any(dt <= 0):
        raise ValueError('Nonnegative rate and positive spacing required')
    return -.5*np.expm1(-2*rate*dt)


def binomial_log_likelihood(counts, intervals, probabilities):
    """Log likelihood up to the model-independent binomial coefficient."""
    k, p = np.asarray(counts), np.asarray(probabilities)
    return np.sum(xlogy(k, p)+xlogy(intervals-k, 1-p), axis=-1)


def fit_dated_signs(counts, intervals, spacing_myr):
    """Two-segment MLE and likelihood ratio against a common rate."""
    k = np.asarray(counts)
    if k.shape[-1] != 2 or intervals < 1 or np.any(k < 0) or np.any(k > intervals):
        raise ValueError('Two valid segment counts required')
    separate = np.clip(k/intervals, 0, .5)
    common = np.minimum(np.mean(k, axis=-1, keepdims=True)/intervals, .5)
    ll_separate = binomial_log_likelihood(k, intervals, separate)
    ll_common = binomial_log_likelihood(k, intervals, common)
    with np.errstate(divide='ignore'):
        rates = -.5*np.log1p(-2*separate)/spacing_myr
    return {'lr': np.maximum(0., 2*(ll_separate-ll_common)), 'rates': rates,
            'probabilities': separate, 'll_change': ll_separate, 'll_constant': ll_common}


def profile_unknown_spacing(counts, intervals, spacing_bounds=(.01, 1.)):
    """Exact profile where a common-rate ridge lies within clock bounds.

    For finite positive fitted exposures e_j, any common rate in
    [max(e_j/dt_max), min(e_j/dt_min)] attains the unconstrained maximum.
    Rows outside that interval are explicitly marked, not assigned a fit.
    """
    p = np.clip(np.asarray(counts)/intervals, 0., .5)
    with np.errstate(divide='ignore', invalid='ignore'):
        exposure = -.5*np.log1p(-2*p)
        lower = np.max(exposure/spacing_bounds[1], axis=-1)
        upper = np.min(exposure/spacing_bounds[0], axis=-1)
        feasible = np.isfinite(exposure).all(axis=-1) & (lower > 0) & (upper >= lower) & (upper > 0)
        common_rate = np.where(feasible, np.sqrt(lower*upper), np.nan)
        spacings = exposure/common_rate[..., None]
    return {'feasible': feasible, 'common_rate': common_rate, 'spacings': spacings,
            'll_profile': np.where(feasible, binomial_log_likelihood(counts, intervals, p), np.nan)}
