"""Spherical transects and conditional block sign-flip diagnostics.

The reference tail probabilities require sign symmetry at the joint block
level. Choosing a block length does not establish that condition.
"""
import numpy as np
from .spatial_matching import unit_vectors


def lat_lon(vectors):
    v = np.asarray(vectors, float)
    v = v/np.linalg.norm(v, axis=-1, keepdims=True)
    return np.rad2deg(np.arcsin(np.clip(v[..., 2], -1, 1))), np.rad2deg(np.arctan2(v[..., 1], v[..., 0])) % 360


def advance(points, directions, distance_km, radius_km=3389.5):
    """Exponential map on a sphere, with a signed great-circle distance."""
    angle = np.asarray(distance_km)/radius_km
    result = np.cos(angle)[..., None]*points+np.sin(angle)[..., None]*directions
    return result/np.linalg.norm(result, axis=-1, keepdims=True)


class ClosedCurve:
    def __init__(self, longitude_latitude, radius_km=3389.5):
        coords = np.asarray(longitude_latitude, float)
        points = unit_vectors(coords[:, 1], coords[:, 0])
        if np.linalg.norm(points[-1]-points[0]) < 1e-10:
            points = points[:-1]
        self.points = points
        self.radius_km = radius_km
        next_points = np.roll(points, -1, axis=0)
        angles = np.arctan2(np.linalg.norm(np.cross(points, next_points), axis=1), np.sum(points*next_points, axis=1))
        if len(points) < 3 or np.any(angles < 1e-12) or np.any(angles >= np.pi-1e-10):
            raise ValueError('Curve needs at least three distinct vertices and unique minor-arc segments')
        self.segments = angles*radius_km
        self.arc = np.r_[0, np.cumsum(self.segments[:-1])]
        self.length = float(self.segments.sum())
        self.weights = (self.segments+np.roll(self.segments, 1))/2

    def at(self, distances_km):
        s = np.asarray(distances_km) % self.length
        i = np.searchsorted(self.arc, s, side='right')-1
        fraction = (s-self.arc[i])/self.segments[i]
        angle = self.segments[i]/self.radius_km
        a, b = self.points[i], self.points[(i+1) % len(self.points)]
        return (np.sin((1-fraction)*angle)[..., None]*a+np.sin(fraction*angle)[..., None]*b)/np.sin(angle)[..., None]

    def normals(self, half_window_km=100.):
        tangent = self.at(self.arc+half_window_km)-self.at(self.arc-half_window_km)
        tangent -= np.sum(tangent*self.points, axis=1)[:, None]*self.points
        norm = np.linalg.norm(tangent, axis=1)
        if np.any(norm < 1e-12): raise ValueError('Smoothed tangent is undefined')
        tangent /= norm[:, None]
        return np.cross(tangent, self.points)


def block_operator(curve, eligible, nominal_km=1000., offset_fraction=0., minimum_weight_km=200.):
    """Rows are within-block quadrature weights; sum each retained row to one."""
    count = max(1, round(curve.length/nominal_km))
    width = curve.length/count
    ids = np.floor(((curve.arc+offset_fraction*width) % curve.length)/width).astype(int)
    rows, labels, coverage = [], [], []
    for label in range(count):
        w = curve.weights*((ids == label) & np.asarray(eligible, bool))
        if w.sum() >= minimum_weight_km:
            labels.append(label); coverage.append(float(w.sum())); rows.append(w/w.sum())
    matrix = np.array(rows) if rows else np.empty((0, len(curve.points)))
    return matrix, np.asarray(labels), np.asarray(coverage), width


def sign_patterns(blocks, seed=20260928, draws=10000, exact_limit=12):
    if blocks < 1: return np.empty((0, 0)), False
    if blocks <= exact_limit:
        integers = np.arange(2**blocks, dtype=np.uint64)[:, None]
        signs = 2*((integers >> np.arange(blocks, dtype=np.uint64)) & 1).astype(float)-1
        return signs, True
    return np.random.default_rng(seed).choice([-1., 1.], size=(draws, blocks)), False


def reference_tails(block_values, signs, exact):
    """Two-sided tail fractions; columns can be independent synthetic trials."""
    values = np.asarray(block_values, float)
    if values.ndim == 1: values = values[:, None]
    if not len(values): return np.full(values.shape[1], np.nan)
    observed = np.abs(np.mean(values, axis=0))
    count = np.zeros(values.shape[1], int)
    # Bounded memory even when many blocks permit all 10,000 sign patterns.
    for start in range(0, len(signs), 1000):
        null = np.abs(signs[start:start+1000] @ values/len(values))
        count += np.sum(null >= observed[None, :]-1e-12, axis=0)
    return count/len(signs) if exact else (count+1)/(len(signs)+1)


def synthetic_calibration(operators, positions, lengths=(160., 500., 1000.),
                          radius_km=3389.5, features=512, trials=1000, seed=20260928):
    """Stationary Gaussian log-field nulls, using the actual linear contrast.

    operators has shape (blocks, points); positions are unit vectors. Random
    Fourier features approximate a Gaussian kernel of 3-D chord separation.
    The block covariance follows directly from this declared finite model.
    """
    rng = np.random.default_rng(seed)
    signs, exact = sign_patterns(len(operators), seed=seed)
    frequencies = rng.normal(size=(3, features))
    phases = rng.uniform(0, 2*np.pi, size=features)
    out = []
    for length in lengths:
        basis = np.sqrt(2/features)*np.cos(radius_km*np.asarray(positions) @ frequencies/length+phases)
        block_basis = operators @ basis
        covariance = block_basis @ block_basis.T
        eigenvalues, eigenvectors = np.linalg.eigh(covariance)
        transform = eigenvectors*np.sqrt(np.maximum(0, eigenvalues))[None, :]
        simulated = transform @ rng.normal(size=(len(operators), trials))
        tails = reference_tails(simulated, signs, exact)
        rate = float(np.mean(tails <= .05))
        out.append({'correlation_length_km': length, 'trials': trials,
            'false_positive_rate_at_005': rate, 'binomial_standard_error': float(np.sqrt(rate*(1-rate)/trials)),
            'sign_patterns': len(signs), 'exact_sign_enumeration': exact})
    return out
