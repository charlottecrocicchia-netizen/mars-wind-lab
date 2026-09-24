"""SI diagnostics. Azimuth is clockwise from north; winds point TOWARDS."""
import numpy as np
from scipy.linalg import eigh


def sound_speed(temperature, gamma, gas_constant):
    t, g, r = np.broadcast_arrays(temperature, gamma, gas_constant)
    if np.any(t <= 0) or np.any(g <= 1) or np.any(r <= 0):
        raise ValueError('Sound speed requires T > 0, gamma > 1 and R > 0.')
    return np.sqrt(g * r * t)


def along_wind(u, v, azimuth):
    a = np.deg2rad(azimuth)
    return np.asarray(u) * np.sin(a) + np.asarray(v) * np.cos(a)


def vertical_shear(u, v, z):
    z = np.asarray(z)
    if len(z) < 3 or np.any(np.diff(z) <= 0):
        raise ValueError('At least three strictly increasing altitudes are required.')
    return np.hypot(np.gradient(u, z, axis=0, edge_order=2),
                    np.gradient(v, z, axis=0, edge_order=2))


def latitude_weights(lat):
    lat = np.asarray(lat)
    if len(lat) < 2 or np.any(np.diff(lat) <= 0):
        raise ValueError('Latitude centres must be strictly increasing.')
    edges = np.r_[-90., (lat[:-1] + lat[1:]) / 2, 90.]
    return np.diff(np.sin(np.deg2rad(edges)))


def area_mean(field, lat):
    f = np.asarray(field)
    w = np.broadcast_to(latitude_weights(lat)[:, None], f.shape)
    good = np.isfinite(f)
    return float(np.sum(np.where(good, f, 0) * w) / np.sum(w * good)) if good.any() else np.nan


def acoustic_modes(z, rho, c, wind, horizontal_degree=150, count=6):
    """EXPERIMENTAL scalar pressure column, rigid ends, no gravity/dissipation.

    -(a p')' + k² a p = omega² b p, a=1/rho, b=1/(rho*c²).
    P1 FEM with positive lumped mass; no surface/solid coupling.
    First-order diagonal advection only: delta_omega = k * <U>_b.
    This is a benchmark/sensitivity operator, NOT the report's global modes.
    """
    z, rho, c, wind = map(lambda x: np.asarray(x, dtype=float), (z, rho, c, wind))
    n = len(z)
    if n < 4 or any(x.shape != z.shape for x in (rho,c,wind)):
        raise ValueError('Four or more matching profile samples required.')
    if not all(np.isfinite(x).all() for x in (z,rho,c,wind)) or np.any(np.diff(z)<=0) or np.any(rho<=0) or np.any(c<=0):
        raise ValueError('Invalid modal profile.')
    if horizontal_degree < 1:
        raise ValueError('Positive horizontal degree required.')
    k = np.sqrt(horizontal_degree * (horizontal_degree + 1)) / 3389500.
    dz = np.diff(z)
    a = 0.5 * (1/rho[:-1] + 1/rho[1:])
    b = 0.5 * (1/(rho[:-1]*c[:-1]**2) + 1/(rho[1:]*c[1:]**2))
    mass = np.zeros(n)
    diag = np.zeros(n)
    for sl in (slice(None,-1),slice(1,None)):
        mass[sl] += b * dz/2
        diag[sl] += a/dz + k*k*a*dz/2
    off = -a/dz
    A = np.diag(diag/mass) + np.diag(off/np.sqrt(mass[:-1]*mass[1:]),1) + np.diag(off/np.sqrt(mass[:-1]*mass[1:]),-1)
    eigen, q = eigh(A, subset_by_index=[0, min(count,n)-1], driver='evr')
    if np.any(eigen<=0):
        raise ValueError('Non-positive modal eigenvalue.')
    omega = np.sqrt(eigen)
    weights = q*q  # sum over nodes = 1, equal to mass*p²
    ueff = weights.T @ wind
    delta = k * ueff
    return {'frequency_mhz': omega/(2*np.pi)*1000, 'period_s':2*np.pi/omega,
            'delta_frequency_mhz':delta/(2*np.pi)*1000, 'effective_wind':ueff,
            'relative_shift':delta/omega, 'weights':weights.T,
            'mean_altitude_km':weights.T @ z/1000, 'k_rad_m':float(k)}
