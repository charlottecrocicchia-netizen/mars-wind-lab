"""Magnetic recording by rapidly cooled bodies: slabs, stacks and reversals.

A tabular igneous body (sill, dyke or lava unit) of thickness h emplaced at
temperature T_e into a host at uniform temperature T_h cools by conduction.
Without latent heat and with uniform properties the temperature has the exact
solution (Carslaw & Jaeger, 1959, §2.4):

    T(x, t) = T_h + (T_e − T_h)/2 · [erf((h/2 − x)/(2√(κt))) + erf((h/2 + x)/(2√(κt)))]

with x measured from the body's mid-plane. Each position acquires its
thermoremanence when it cools through the blocking band; the body's record is
the average over positions. Integrating that kernel against a reversing field
gives the retained fraction of a steady-field record, exactly as for the
conductive crust columns. A stack of bodies emplaced at different times adds
their signed records; the field sign at each emplacement decides the polarity.
"""
import numpy as np
from scipy.special import erf

from .recording import recording_intervals, record_intervals

SECONDS_PER_MYR = 1e6*365.25*86400


def slab_temperature(x_m, t_s, thickness_m, t_emplaced_k, t_host_k, diffusivity_m2_s):
    """Exact conductive cooling of an infinite slab in an infinite host."""
    x, t = np.asarray(x_m, float), np.asarray(t_s, float)
    if thickness_m <= 0 or diffusivity_m2_s <= 0 or np.any(t < 0):
        raise ValueError('Positive thickness, diffusivity and non-negative times are required')
    with np.errstate(divide='ignore', invalid='ignore'):
        s = 2*np.sqrt(diffusivity_m2_s*np.where(t > 0, t, np.nan))
        f = 0.5*(erf((thickness_m/2-x)/s)+erf((thickness_m/2+x)/s))
    f = np.where(t > 0, f, (np.abs(x) < thickness_m/2).astype(float))
    return t_host_k+(t_emplaced_k-t_host_k)*f


def body_kernels(thickness_m, t_emplaced_k, t_host_k, diffusivity_m2_s, band_k, positions=32, time_points=400):
    """Exact piecewise-linear acquisition kernels for positions across half the slab.

    Returns a list of kernel dicts (start, end, weight in Myr) from
    recording_intervals, one per position, plus the elapsed cooling time of the
    mid-plane through the band. Positions are cell centres from the mid-plane to
    the contact; by symmetry they represent the whole body.
    """
    low, high = band_k
    if not (t_host_k < low < high < t_emplaced_k):
        raise ValueError('The host must be cooler than the band and the body hotter than it')
    x = (np.arange(positions)+0.5)/positions*(thickness_m/2)
    tau = thickness_m**2/diffusivity_m2_s
    t = np.concatenate([[0.], np.geomspace(1e-6*tau, 1e4*tau, time_points)])
    kernels = []
    for xi in x:
        temp = slab_temperature(xi, t, thickness_m, t_emplaced_k, t_host_k, diffusivity_m2_s)
        kernels.append(recording_intervals(t/SECONDS_PER_MYR, temp, band_k))
    centre = slab_temperature(0., t, thickness_m, t_emplaced_k, t_host_k, diffusivity_m2_s)
    above_low = np.flatnonzero(centre >= low)
    return kernels, float(t[above_low[-1]]/SECONDS_PER_MYR) if len(above_low) else 0.


def body_retention(kernels, kind, chron_myr, realizations, seed=0):
    """Retained fraction of a steady record for one body under a reversing field.

    The signed record is the position average of each kernel's integral of the
    field; the known acquired fraction normalises it. Periodic fields use
    evenly spaced phases, Poisson fields one seed per realization.
    """
    known = float(np.mean([k['weight'].sum() for k in kernels]))
    if known <= 0:
        return np.full(realizations, np.nan), known
    out = []
    for m in range(realizations):
        signed = record_intervals(kernels, kind, chron_myr=chron_myr, phase=2*m/realizations if kind == 'periodic' else float(m % 2), seed=seed+m)
        out.append(abs(np.mean(signed))/known)
    return np.array(out), known


def poisson_sign(times_myr, chron_myr, rng):
    """Sign of a random telegraph field with exponential chrons at given times."""
    t = np.asarray(times_myr, float)
    edges = [0.]
    while edges[-1] <= t.max(initial=0):
        edges.append(edges[-1]+rng.exponential(chron_myr))
    return 1-2*(np.searchsorted(np.array(edges), t, side='right') % 2)


def stack_coherence(bodies, emplacement_span_myr, chron_myr, realizations, seed=0, body_retention_fraction=1.0):
    """Net coherence of N equal bodies emplaced at random times within a span.

    Each body records the field sign at its emplacement, scaled by its own
    retained fraction. The stack's coherence is |mean signed record|. For a
    span much longer than a chron the expectation tends to 1/sqrt(N).
    """
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(realizations):
        times = rng.uniform(0, emplacement_span_myr, bodies)
        signs = poisson_sign(times, chron_myr, rng)
        values.append(abs(np.mean(signs))*body_retention_fraction)
    return np.array(values)


def max_thickness_for_retention(thicknesses_m, medians, threshold=0.5):
    """Largest declared thickness whose median retention meets the threshold."""
    ok = [h for h, m in zip(thicknesses_m, medians) if np.isfinite(m) and m >= threshold]
    return max(ok) if ok else None
