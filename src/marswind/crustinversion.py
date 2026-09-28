"""Crustal thickness from gravity and topography with laterally variable density.

Independent implementation of the finite-amplitude potential of relief
(Wieczorek & Phillips, 1998, eq. 10) generalised to a density that varies
laterally but not with depth, of the gravity of the reference crustal shell
whose density varies laterally, and of the regularised iterative crust-mantle
relief inversion (their eq. 18) with a downward-continuation filter applied to
the whole linear solution at every iteration. Nothing here copies the archive
script of Wieczorek et al. (2022); that archive is used only as a validation
target.

Mass convention for a two-density crust. The crust is decomposed into three
bodies whose potentials add exactly:
  1. the shell between the mean crust-mantle radius d and the mean surface
     radius R, with lateral density rho(theta, phi)  -> shell_potential;
  2. the surface relief about R with density rho      -> relief_potential;
  3. the Moho relief about d with contrast rho_m − rho -> relief_potential.
With a uniform crust body 1 has no gravity above degree 0; with lateral
density variations it does, and it depends on d.

Conventions: geodesy 4-pi normalised real harmonics without Condon-Shortley
phase (pyshtools default), Driscoll-Healy grids with sampling 2, SI units.
"""
import numpy as np
import pyshtools as sh

G = 6.67430e-11


def relief_potential(relief_m, density_kg_m3, reference_radius_m, mass_kg, lmax, nmax):
    """Potential coefficients (4-pi normalised, referenced to reference_radius_m)
    of the body between the sphere of radius d and the surface d + relief.

    relief_m and density_kg_m3 are Driscoll-Healy grids (n × 2n). A negative
    relief with positive density represents missing mass; the expansion is
    linear in density, so lateral density variations enter exactly through the
    products density × relief**n. The Taylor order nmax controls the
    finite-amplitude accuracy; the grid must resolve degree lmax × nmax.
    """
    h = np.asarray(relief_m, dtype=float)
    rho = np.broadcast_to(np.asarray(density_kg_m3, dtype=float), h.shape)
    if h.ndim != 2 or h.shape[1] != 2*h.shape[0] or not np.isfinite(h).all() or not np.isfinite(rho).all():
        raise ValueError('Finite Driscoll-Healy grids with sampling 2 are required')
    if not (reference_radius_m > 0 and mass_kg > 0 and lmax >= 0 and nmax >= 1):
        raise ValueError('Positive reference radius, mass and orders are required')
    d = float(reference_radius_m)
    degrees = np.arange(lmax+1, dtype=float)
    coeffs = np.zeros((2, lmax+1, lmax+1))
    product = np.ones(lmax+1)  # prod_{j=1}^{n} (l+4-j), divided once by (l+3)
    factorial = 1.0
    x = h/d  # dimensionless relief keeps every expanded grid of order one
    scale = float(np.abs(rho).max()) or 1.0
    for n in range(1, nmax+1):
        product = product*(degrees+4-n)
        factorial *= n
        term = sh.expand.SHExpandDH(rho/scale*x**n, sampling=2, lmax_calc=lmax)
        coeffs += term*(product/(factorial*(degrees+3)))[None, :, None]
    coeffs *= (4*np.pi*d**3*scale/(mass_kg*(2*degrees+1)))[None, :, None]
    return coeffs


def shell_potential(density_kg_m3, inner_radius_m, outer_radius_m, mass_kg, lmax, reference_radius_m):
    """Exterior potential of a spherical shell whose density varies laterally.

    C_lm = 4 pi rho_lm (R^(l+3) − d^(l+3)) / [M (2l+1) (l+3) r0^l], the exact
    integral of rho r^(l+2) between the inner radius d and outer radius R.
    The degree-0 term (total shell mass) is returned as well; callers decide
    how to treat it. For a uniform shell every nonzero degree vanishes.
    """
    rho = np.asarray(density_kg_m3, dtype=float)
    if rho.ndim != 2 or rho.shape[1] != 2*rho.shape[0] or not np.isfinite(rho).all():
        raise ValueError('A finite Driscoll-Healy density grid with sampling 2 is required')
    d, R, r0 = float(inner_radius_m), float(outer_radius_m), float(reference_radius_m)
    if not 0 < d < R or r0 <= 0 or mass_kg <= 0:
        raise ValueError('Radii must satisfy 0 < inner < outer and the reference radius must be positive')
    rho_lm = sh.expand.SHExpandDH(rho, sampling=2, lmax_calc=lmax)
    degrees = np.arange(lmax+1, dtype=float)
    # (R^(l+3) − d^(l+3)) / r0^l evaluated with ratios to avoid overflow at high degree
    radial = r0**3*((R/r0)**(degrees+3)-(d/r0)**(degrees+3))/(degrees+3)
    return rho_lm*(4*np.pi*radial/(mass_kg*(2*degrees+1)))[None, :, None]


def rereference(coeffs, from_radius_m, to_radius_m):
    """Exterior potential coefficients scale as (r_from / r_to)**l."""
    degrees = np.arange(coeffs.shape[1], dtype=float)
    return coeffs*((from_radius_m/to_radius_m)**degrees)[None, :, None]


def minimum_amplitude_filter(degrees, half_degree, r0_m, d_m):
    """Wieczorek & Phillips (1998) minimum-amplitude downward-continuation filter.

    Equals 0.5 at half_degree. Returns 1 for degree 0 so the mean is untouched.
    """
    l = np.asarray(degrees, dtype=float)
    lh = float(half_degree)
    ratio = ((2*l+1)/(2*lh+1))**2*(r0_m/d_m)**(2*(l-lh))
    weight = 1/(1+ratio)
    return np.where(l == 0, 1.0, weight)


def invert_moho(bouguer_coeffs, reference_radius_m, crust_density_grid, mantle_density_kg_m3,
                mean_moho_radius_m, mass_kg, lmax, nmax, filter_half_degree=50, iterations=100,
                tolerance_m=1.0):
    """Regularised relief of the crust-mantle interface for a Bouguer anomaly.

    Fixed-point scheme of Wieczorek & Phillips (1998, eq. 18) with a laterally
    variable contrast. At every iteration the filtered first-order solution is
    recomputed from the anomaly minus the part of the current model potential
    that the mean-contrast first-order kernel does not describe:

        h_(k+1) = w · K · [BA − (U(h_k) − K⁻¹ h_k)]

    so the filter w acts on the whole linear solution and is never undone by
    iterating. Successive estimates are averaged to damp oscillation. The
    result carries the number of iterations, the largest change of the relief
    grid at the last iteration (metres), a convergence flag, and the remaining
    unfiltered data misfit in metres of first-order relief.
    """
    ba = np.asarray(bouguer_coeffs, dtype=float)
    rho_c = np.asarray(crust_density_grid, dtype=float)
    if ba.shape != (2, lmax+1, lmax+1) or rho_c.ndim != 2 or rho_c.shape[1] != 2*rho_c.shape[0]:
        raise ValueError('Coefficient and density grid dimensions must match lmax and sampling 2')
    contrast = mantle_density_kg_m3-rho_c
    if np.any(contrast <= 0):
        raise ValueError('The mantle must be denser than the crust everywhere')
    d = float(mean_moho_radius_m)
    degrees = np.arange(lmax+1, dtype=float)
    weights = np.cos(np.deg2rad(90-np.arange(rho_c.shape[0])*180/rho_c.shape[0]))
    mean_contrast = float(np.average(contrast.mean(axis=1), weights=weights))
    kernel = np.where(degrees == 0, 0.0, mass_kg*(2*degrees+1)/(4*np.pi*d**2*mean_contrast))*(reference_radius_m/d)**degrees
    inverse_kernel = np.where(degrees == 0, 0.0, 1/np.where(degrees == 0, 1.0, kernel))
    taper = minimum_amplitude_filter(degrees, filter_half_degree, reference_radius_m, d)
    target = ba.copy(); target[0, 0, 0] = 0.0
    relief = target*(kernel*taper)[None, :, None]
    grid_lmax = rho_c.shape[0]//2-1
    h_grid = sh.expand.MakeGridDH(relief, sampling=2, lmax=grid_lmax)
    converged = False; change = np.inf; iteration = 0
    for iteration in range(1, iterations+1):
        model = rereference(relief_potential(h_grid, contrast, d, mass_kg, lmax, nmax), d, reference_radius_m)
        model[0, 0, 0] = 0.0
        nonlinear = model-relief*inverse_kernel[None, :, None]
        proposal = (target-nonlinear)*(kernel*taper)[None, :, None]
        proposal[0, 0, 0] = 0.0
        new_relief = 0.5*(relief+proposal)
        new_grid = sh.expand.MakeGridDH(new_relief, sampling=2, lmax=grid_lmax)
        change = float(np.max(np.abs(new_grid-h_grid)))
        relief, h_grid = new_relief, new_grid
        if change < tolerance_m:
            converged = True
            break
    model = rereference(relief_potential(h_grid, contrast, d, mass_kg, lmax, nmax), d, reference_radius_m)
    model[0, 0, 0] = 0.0
    misfit = float(np.sqrt(np.sum(((target-model)*kernel[None, :, None])[:, 1:, :]**2)))
    return d+h_grid, {'iterations': iteration, 'last_change_m': change, 'converged': converged,
                      'unfiltered_data_misfit_m': misfit}


def area_weights(rows):
    """Cosine-latitude weights for a Driscoll-Healy latitude sampling."""
    latitudes = 90-np.arange(rows)*180/rows
    return np.cos(np.deg2rad(latitudes))


def weighted_mean(grid, mask):
    """Area-weighted mean over a boolean mask on a Driscoll-Healy grid."""
    g = np.asarray(grid, dtype=float)
    w = np.broadcast_to(area_weights(g.shape[0])[:, None], g.shape)
    m = np.asarray(mask, dtype=bool)&np.isfinite(g)
    if not m.any():
        raise ValueError('Empty selection')
    return float(np.sum(g[m]*w[m])/np.sum(w[m]))


def grid_value(grid, lat_deg, lon_deg):
    """Nearest Driscoll-Healy node (sampling 2, first row is 90 N, first column 0 E)."""
    rows = grid.shape[0]
    i = int(round((90-lat_deg)*rows/180)) % rows
    j = int(round((lon_deg % 360)*(2*rows)/360)) % (2*rows)
    return float(grid[i, j])
