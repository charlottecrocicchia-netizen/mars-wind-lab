"""Magnetization required by orbital anomalies, and orbital-model surface checks.

The required magnetization is a lower bound: a uniformly, vertically
magnetized cylinder observed on its axis is the most efficient geometry for a
given volume. Random directions, thinner sources or lateral cancellation all
require more. Capacities are declared scenarios, not measured Martian crust.
"""
import numpy as np

from .recording import cylinder_axis_operator

MARS_RADIUS_KM = 3393.5


def required_magnetization(field_nt, radius_km, top_km, bottom_km, height_km):
    """A/m needed for a coaxial vertical cylinder to produce field_nt at height_km."""
    if not (np.isfinite(field_nt) and field_nt >= 0):
        raise ValueError('A finite non-negative field is required')
    operator = cylinder_axis_operator(radius_km, [top_km], [bottom_km], [height_km])[0, 0]
    return float(field_nt/operator)


def angular_distance_deg(lat, lon, lat0, lon0):
    p, p0 = np.deg2rad(lat), np.deg2rad(lat0)
    dl = np.deg2rad(np.asarray(lon)-lon0)
    a = np.sin((p-p0)/2)**2+np.cos(p)*np.cos(p0)*np.sin(dl/2)**2
    return np.rad2deg(2*np.arcsin(np.sqrt(np.clip(a, 0, 1))))


def window_statistics(field_grid, lat, lon, center_lat, center_lon, radius_deg):
    """Area-weighted RMS and maximum of a scalar grid inside an angular radius."""
    la, lo = np.meshgrid(lat, lon, indexing='ij')
    inside = angular_distance_deg(la, lo, center_lat, center_lon) <= radius_deg
    if not inside.any():
        raise ValueError('Empty window')
    w = np.cos(np.deg2rad(la))[inside]
    v = np.asarray(field_grid, float)[inside]
    return {'rms': float(np.sqrt(np.sum(w*v*v)/np.sum(w))), 'max': float(v.max()),
            'mean': float(np.sum(w*v)/np.sum(w)), 'cells': int(inside.sum())}


def magnetic_vector(model, lat, lon, radius_km):
    """Total and horizontal intensity (nT) of a pyshtools magnetic model at a point."""
    v = np.atleast_2d(model.expand(lat=float(lat), lon=float(lon), r=float(radius_km)*1000))
    total = float(np.linalg.norm(v[0]))
    horizontal = float(np.hypot(v[0, 1], v[0, 2]))
    return {'total_nt': total, 'horizontal_nt': horizontal, 'radial_nt': float(v[0, 0])}


def coherence_penalty(required_a_m, coherent_fraction):
    """Magnetization needed before cancellation for a retained fraction."""
    f = np.asarray(coherent_fraction, float)
    if np.any(f <= 0) or np.any(f > 1):
        raise ValueError('Coherent fraction must lie in (0, 1]')
    return np.asarray(required_a_m, float)/f
