"""Independent, restricted physical tests; no origin or paleofield inference."""
import numpy as np
from scipy.linalg import solve_banded
from scipy.ndimage import gaussian_filter1d


def column_support(thickness_km, density_kg_m3, mantle_density_kg_m3=3500.):
    """Airy support above a shared compensation datum, in km.

    A free surface, constant mantle density and fully compensated columns are
    assumed. Absolute elevation needs a reference; differences cancel it.
    """
    h, rho = np.broadcast_arrays(np.asarray(thickness_km, float),
                                 np.asarray(density_kg_m3, float))
    if (not np.isfinite(mantle_density_kg_m3) or mantle_density_kg_m3 <= 0
            or not np.isfinite(h).all() or not np.isfinite(rho).all()
            or np.any(h < 0) or np.any(rho <= 0)):
        raise ValueError('Finite, nonnegative thickness and positive density required')
    return h * (1 - rho / mantle_density_kg_m3)


def layered_density(thickness_km, basal_km, upper_density, basal_density,
                    upper_porosity=0., pore_density=0.):
    """Volume-weighted density; pores occur only in the upper layer.

    Porosity is a declared endmember, not a depth-dependent compaction model.
    No dense material is silently discarded or converted into light crust.
    """
    vals = [thickness_km, basal_km, upper_density, basal_density,
            upper_porosity, pore_density]
    if (not np.isfinite(vals).all() or thickness_km <= 0
            or not 0 <= basal_km <= thickness_km or not 0 <= upper_porosity < 1
            or min(upper_density, basal_density) <= 0 or pore_density < 0):
        raise ValueError('Invalid layer geometry, density or porosity')
    upper_bulk = (1-upper_porosity)*upper_density + upper_porosity*pore_density
    return ((thickness_km-basal_km)*upper_bulk + basal_km*basal_density)/thickness_km


def thermal_susceptibility(degree, lid_km=100., radius_km=3390., cells=400):
    """Dimensionless basal response k*T/(H*R²) to harmonic lid heating.

    Solve -(x² u')' + l(l+1)u = x² on b/R <= x <= 1, with zero
    basal flux and zero surface temperature perturbation. Conservative radial
    finite volumes, half a volume at the basal Neumann node, fixed surface.
    Valid for a steady, uniform-conductivity shell, not evolving convection.
    """
    if (not isinstance(degree, (int, np.integer)) or degree < 0
            or not np.isfinite([lid_km, radius_km]).all()
            or not 0 < lid_km < radius_km or not isinstance(cells, int) or cells < 8):
        raise ValueError('Integer degree/cells and a positive spherical shell required')
    b = 1 - lid_km/radius_km
    x = np.linspace(b, 1., cells+1)
    dx = x[1]-x[0]
    lower_faces = np.r_[b, (x[:-2]+x[1:-1])/2]
    upper_faces = (x[:-1]+x[1:])/2
    width = upper_faces-lower_faces
    left = np.r_[0., lower_faces[1:]**2/dx]
    right = upper_faces**2/dx
    diagonal = left+right+degree*(degree+1)*width
    matrix = np.zeros((3, cells))
    matrix[1] = diagonal
    matrix[0, 1:] = -right[:-1]
    matrix[2, :-1] = -left[1:]
    rhs = (upper_faces**3-lower_faces**3)/3
    u = np.r_[solve_banded((1, 1), matrix, rhs), 0.]
    return float(u[0])


def modal_power_share(relative_growth, degree_one_efolds, initial_power):
    """Normalized modal power after a specified degree-one log-amplification.

    This linear calculation does not set geological time, select the initial
    spectrum, saturate growth or conserve a finite melt/HPE inventory.
    """
    rates, power = np.asarray(relative_growth, float), np.asarray(initial_power, float)
    if (rates.ndim != 1 or rates.shape != power.shape or np.any(power <= 0)
            or not np.isfinite(rates).all() or not np.isfinite(power).all()
            or not np.isfinite(degree_one_efolds) or degree_one_efolds < 0):
        raise ValueError('Finite rates and positive mode powers required')
    logs = np.log(power) + 2*rates*degree_one_efolds
    out = np.exp(logs-logs.max())
    return out/out.sum()


def rigidity(elastic_km, young_gpa=100., poisson=.25):
    """Thin-plate rigidity E Te³/[12(1-nu²)], in N m."""
    if (not np.isfinite([elastic_km, young_gpa, poisson]).all()
            or elastic_km < 0 or young_gpa <= 0 or not -1 < poisson < .5):
        raise ValueError('Invalid elastic properties')
    return young_gpa*1e9*(elastic_km*1000)**3/(12*(1-poisson**2))


def flexure(load_m, spacing_m, elastic_km, mantle_density=3500., load_density=2900.,
            gravity=3.71, padding=2):
    """Downward deflection of a planar plate under a signed surface load.

    D w'''' + rho_m*g*w = rho_load*g*t. Mantle replaces/displaces a free
    surface; rho_m is the restoring density, not a crust/mantle contrast.
    FFT periodic solver with zero padding for isolated finite profiles.
    padding=0 provides exact periodic sinusoid benchmarks.
    """
    load = np.asarray(load_m, float)
    if (load.ndim != 1 or len(load) < 8 or not np.isfinite(load).all()
            or not np.isfinite([spacing_m, mantle_density, load_density, gravity]).all()
            or min(spacing_m, mantle_density, load_density, gravity) <= 0
            or not isinstance(padding, int) or padding < 0):
        raise ValueError('Invalid load, spacing, density or padding')
    n = len(load)
    extended = np.pad(load, (padding*n, padding*n))
    k = 2*np.pi*np.fft.rfftfreq(len(extended), spacing_m)
    response = load_density*gravity/(rigidity(elastic_km)*k**4+mantle_density*gravity)
    w = np.fft.irfft(np.fft.rfft(extended)*response, n=len(extended))
    return w[padding*n:padding*n+n]


def boundary_proxy(x_km, elevation_km, smoothing_km=50., search_km=(-500., 500.)):
    """Grid-sampled maximum south-to-north descent; not a fault location.

    Only a predeclared search interval is inspected. Profiles are meridional,
    not automatically normal to the geological boundary.
    """
    x, z = np.asarray(x_km, float), np.asarray(elevation_km, float)
    if (x.ndim != 1 or x.shape != z.shape or len(x) < 8
            or not np.isfinite(x).all() or not np.isfinite(z).all()
            or not np.isfinite(smoothing_km) or smoothing_km <= 0
            or not np.allclose(np.diff(x), x[1]-x[0]) or x[1] <= x[0]
            or search_km[0] >= search_km[1]):
        raise ValueError('Uniform increasing profile and positive smoothing required')
    smooth = gaussian_filter1d(z, smoothing_km/(x[1]-x[0]), mode='nearest')
    slope = np.gradient(smooth, x)
    indices = np.flatnonzero((x >= search_km[0]) & (x <= search_km[1]))
    if len(indices) < 3:
        raise ValueError('Search interval has insufficient samples')
    index = indices[np.argmin(slope[indices])]
    return {'index': int(index), 'x_km': float(x[index]),
            'slope': float(slope[index]), 'at_search_edge': bool(index in indices[[0, -1]])}


def arai_example(true_field_ut=25., laboratory_field_ut=50., efficiency_ratio=1.):
    """Idealized two-efficiency counterexample; not a paleointensity estimator.

    x = lab pTRM / initial NRM, y = remaining NRM / initial NRM.
    Different natural/laboratory recording efficiencies can bias an exactly
    straight Arai line. Real specimens require protocol-specific controls.
    """
    if not np.isfinite([true_field_ut, laboratory_field_ut, efficiency_ratio]).all() or min(true_field_ut, laboratory_field_ut, efficiency_ratio) <= 0:
        raise ValueError('Positive fields and recording efficiencies required')
    fraction = np.linspace(0, 1, 11)
    x = fraction*laboratory_field_ut/(efficiency_ratio*true_field_ut)
    y = 1-fraction
    slope = -efficiency_ratio*true_field_ut/laboratory_field_ut
    return {'lab_ptrm_normalized': x.tolist(), 'nrm_remaining_normalized': y.tolist(),
            'slope': slope, 'apparent_field_ut': -slope*laboratory_field_ut,
            'true_field_ut': true_field_ut, 'efficiency_ratio': efficiency_ratio}
