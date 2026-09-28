"""Outcome-free spatial matching and dependence diagnostics on a sphere.

These functions do not establish exchangeability or compute a scientific
p-value. Shared spatial blocks connect pairs that cannot be flipped separately.
"""
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components


def unit_vectors(latitude, longitude):
    lat, lon = np.deg2rad(latitude), np.deg2rad(longitude)
    return np.column_stack((np.cos(lat)*np.cos(lon), np.cos(lat)*np.sin(lon), np.sin(lat)))


def polyline_distance_km(latitude, longitude, line_lon_lat, radius_km=3389.5, step_km=5.):
    """Nearest sampled minor-arc distance, overestimating by at most step/2.

    Densify each great-circle segment before the nearest-neighbour lookup.
    Coordinates wrap naturally at longitude zero. This error bound concerns
    sampling only, not the uncertainty of the supplied boundary.
    """
    line = np.asarray(line_lon_lat, float)
    if step_km <= 0 or radius_km <= 0 or len(line) < 2:
        raise ValueError('A polyline and positive distance scales are required')
    vertices = unit_vectors(line[:, 1], line[:, 0])
    samples = []
    for a, b in zip(vertices[:-1], vertices[1:]):
        angle = np.arctan2(np.linalg.norm(np.cross(a, b)), np.dot(a, b))
        if np.isclose(angle, np.pi):
            raise ValueError('Antipodal endpoints do not define a unique minor arc')
        if angle < 1e-12:
            samples.append(a[None, :]); continue
        t = np.linspace(0, 1, max(1, int(np.ceil(angle*radius_km/step_km)))+1)
        samples.append((np.sin((1-t)*angle)[:, None]*a+np.sin(t*angle)[:, None]*b)/np.sin(angle))
    nodes = np.vstack(samples)
    chord, _ = cKDTree(nodes).query(unit_vectors(latitude, longitude))
    return 2*radius_km*np.arcsin(np.clip(chord/2, 0, 1))


def caliper_match(target, controls, target_epochs, control_epochs, calipers):
    """Maximize matched count, then minimize squared caliper-scaled distance.

    Exact epoch matching; no replacement; each coordinate must satisfy its
    caliper. A dummy assignment costs more than all valid edge costs combined.
    """
    a, b = np.asarray(target, float), np.asarray(controls, float)
    scales = np.asarray(calipers, float)
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[1] or scales.shape != (a.shape[1],):
        raise ValueError('Matching covariates must share dimensions')
    if not np.all(np.isfinite(scales)) or np.any(scales <= 0):
        raise ValueError('Calipers must be finite and positive')
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError('Missing covariates must be handled before matching')
    if len(a) == 0 or len(b) == 0:
        return np.array([], int), np.array([], int), np.array([], float)
    delta = (a[:, None, :]-b[None, :, :])/scales
    eligible = np.all(np.abs(delta) <= 1+1e-12, axis=2)
    eligible &= np.asarray(target_epochs)[:, None] == np.asarray(control_epochs)[None, :]
    costs = np.sum(delta*delta, axis=2)
    dummy_cost = (len(a)+1)*(a.shape[1]+1)
    matrix = np.full((len(a), len(b)+len(a)), dummy_cost, dtype=float)
    matrix[:, :len(b)] = np.where(eligible, costs, 2*dummy_cost)
    rows, columns = linear_sum_assignment(matrix)
    real = columns < len(b)
    rows, columns = rows[real], columns[real]
    assert np.all(eligible[rows, columns])
    return rows, columns, costs[rows, columns]


def block_labels(latitude, longitude, nominal_km, offset=0., radius_km=3389.5):
    """Nominal spatial blocks; widths vary within each latitude band."""
    if nominal_km <= 0 or not 0 <= offset < 1:
        raise ValueError('Positive block width and an offset in [0, 1) are required')
    lat = np.deg2rad(latitude)
    step = nominal_km/radius_km
    band = np.floor((lat+np.pi/2)/step-offset).astype(int)
    middle = np.clip(-np.pi/2+(band+offset+.5)*step, -np.pi/2, np.pi/2)
    sectors = np.maximum(1, np.rint(2*np.pi*radius_km*np.cos(middle)/nominal_km).astype(int))
    sector = np.floor((np.asarray(longitude) % 360)/360*sectors-offset).astype(int) % sectors
    return np.array([f'{i}:{j}' for i, j in zip(band, sector)])


def pair_block_components(target_blocks, control_blocks):
    """Return component IDs per pair; block identity is shared across groups."""
    if len(target_blocks) != len(control_blocks):
        raise ValueError('One target and one control block are needed per pair')
    if not len(target_blocks):
        return np.array([], int)
    labels, index = np.unique(np.concatenate([target_blocks, control_blocks]), return_inverse=True)
    a, b = np.split(index, 2)
    graph = coo_matrix((np.ones(len(a)*2), (np.r_[a, b], np.r_[b, a])), shape=(len(labels), len(labels))).tocsr()
    _, components = connected_components(graph, directed=False)
    assert np.array_equal(components[a], components[b])
    return components[a]


def standardized_balance(a, b, wa, wb, ia, ib):
    """Pre/post weighted differences with fixed pooled pre-match denominators."""
    def stats(x, w):
        mean = np.average(x, weights=w, axis=0)
        var = np.average((x-mean)**2, weights=w, axis=0)
        return mean, var
    ma, va = stats(a, wa); mb, vb = stats(b, wb)
    scale = np.sqrt((va+vb)/2)
    pre = np.divide(ma-mb, scale, out=np.zeros_like(ma), where=scale > 0)
    pre[(scale == 0) & (ma != mb)] = np.inf
    if not len(ia): return pre, np.full_like(pre, np.nan)
    # The target-area weight defines the estimand for both members of each pair.
    difference = np.average(a[ia]-b[ib], weights=wa[ia], axis=0)
    post = np.divide(difference, scale, out=np.zeros_like(ma), where=scale > 0)
    post[(scale == 0) & (difference != 0)] = np.inf
    return pre, post
