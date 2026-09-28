"""Time-dependent conductive crust histories constrained by published endpoints.

Each history is a fixed-thickness crustal column heated by decaying radiogenic
isotopes and by a prescribed, decaying basal heat flux from the mantle. The
column starts hot at 4.5 Ga and cools monotonically. Histories are accepted
when their present-day profile lies inside the published envelope of Thiriet
et al. (2018) for that hemisphere and, for the south, when the Noachian
elastic thickness proxy lies in the compiled range. Accepted histories then
give, for each depth, the age at which a carrier of given blocking
temperature would last have cooled through it, and how long the cooling
through a blocking band lasted. Model time t is elapsed since 4.5 Ga.
"""
from dataclasses import dataclass

import numpy as np
from scipy.stats import qmc

from .thermal import Column, solve, steady_temperature
from .recording import last_downward_crossings, recording_intervals, record_intervals

START_AGE_GA = 4.5
# Present heat production per kilogram of element and half-lives (Gyr):
# Turcotte & Schubert (2014) values; isotope fractions U-235 0.0072, K-40 1.17e-4.
ISOTOPES = {
    'U238': {'per_kg_element': 9.46e-5*0.9928, 'half_life_gyr': 4.468, 'element': 'U'},
    'U235': {'per_kg_element': 5.69e-4*0.0072, 'half_life_gyr': 0.7038, 'element': 'U'},
    'Th232': {'per_kg_element': 2.64e-5, 'half_life_gyr': 14.05, 'element': 'Th'},
    'K40': {'per_kg_element': 2.92e-5*1.17e-4, 'half_life_gyr': 1.248, 'element': 'K'},
}


def heat_production_w_kg(age_ga, k_ppm, th_ppm, u_ppm):
    """Radiogenic heat production per kilogram of rock at an age before present."""
    conc = {'K': k_ppm*1e-6, 'Th': th_ppm*1e-6, 'U': u_ppm*1e-6}
    age = np.asarray(age_ga, float)
    total = 0.
    for iso in ISOTOPES.values():
        total = total+conc[iso['element']]*iso['per_kg_element']*2**(age/iso['half_life_gyr'])
    return total


@dataclass(frozen=True)
class HistoryParameters:
    """Declared parameters of one conductive crust history.

    basal_flux_now_mw is the basal heat flux AT THE PRESENT DAY (elapsed time
    duration_myr) and basal_flux_early_mw the flux at t = 0; the exponential
    decay with time constant basal_decay_gyr is normalised so that both
    endpoints are met exactly.
    """
    thickness_km: float
    conductivity: float
    th_ppm: float
    k_over_th: float
    u_over_th: float
    basal_flux_now_mw: float
    basal_flux_early_mw: float
    basal_decay_gyr: float
    surface_temperature_k: float
    density: float = 2900.
    heat_capacity: float = 1000.
    duration_myr: float = 4500.

    def heating_w_m3(self, t_myr):
        age = START_AGE_GA-t_myr/1000
        return self.density*heat_production_w_kg(age, self.th_ppm*self.k_over_th, self.th_ppm, self.th_ppm*self.u_over_th)

    def basal_flux_w_m2(self, t_myr):
        q_now, q0 = self.basal_flux_now_mw*1e-3, self.basal_flux_early_mw*1e-3
        tau = self.basal_decay_gyr*1000
        shape = (np.exp(-t_myr/tau)-np.exp(-self.duration_myr/tau))/(1-np.exp(-self.duration_myr/tau))
        return q_now+(q0-q_now)*shape


def run_history(p: HistoryParameters, duration_myr=None, step_myr=2.5, cell_km=1.):
    """Solve the column from a hot steady initial state; returns the History.

    The thickness must be a whole number of cells so that depth indices map to
    exact physical depths across histories of different thickness.
    """
    duration_myr = p.duration_myr if duration_myr is None else duration_myr
    if abs(duration_myr-p.duration_myr) > 1e-9:
        raise ValueError('duration_myr must match the parameter set so the present-day flux is met')
    cells = p.thickness_km/cell_km
    if abs(cells-round(cells)) > 1e-9:
        raise ValueError('thickness_km must be a whole number of cells')
    cells = int(round(cells))
    column = Column(thickness_m=p.thickness_km*1000, conductivity_w_m_k=p.conductivity,
                    density_kg_m3=p.density, heat_capacity_j_kg_k=p.heat_capacity,
                    surface_temperature_k=p.surface_temperature_k, cells=cells)
    initial = steady_temperature(column, p.basal_flux_w_m2(0.), p.heating_w_m3(0.))
    return solve(column, duration_myr, step_myr, p.basal_flux_w_m2, p.heating_w_m3, initial)


def isotherm_depth_km(depth_m, temperature_k, isotherm_k):
    """First downward crossing of an isotherm, linearly interpolated; None if never."""
    t = np.asarray(temperature_k, float)
    if t[0] >= isotherm_k:
        return 0.
    above = np.flatnonzero(t >= isotherm_k)
    if len(above) == 0:
        return None
    i = above[0]
    frac = (isotherm_k-t[i-1])/(t[i]-t[i-1])
    return float((depth_m[i-1]+frac*(depth_m[i]-depth_m[i-1]))/1000)


def profile_within_envelope(depth_m, temperature_k, check_depths_km, lower_k, upper_k, tolerance_k):
    """True when the profile lies inside [lower − tol, upper + tol] at every depth."""
    z = np.asarray(depth_m)/1000
    values = np.interp(check_depths_km, z, temperature_k)
    return bool(np.all(values >= np.asarray(lower_k)-tolerance_k) and np.all(values <= np.asarray(upper_k)+tolerance_k)), values


def acquisition_ages(history, thresholds_k):
    """Age (Ga) at which each depth last cooled through each threshold.

    Returns an array depth × threshold; NaN where the threshold was never
    reached (the material was always cooler: an unresolved earlier record) or
    where the column is still hotter than the threshold today.
    """
    t = history.time_myr
    out = np.full((len(history.depth_m), len(thresholds_k)), np.nan)
    status_all = np.zeros_like(out, dtype=int)
    for i in range(len(history.depth_m)):
        crossing, status = last_downward_crossings(t, history.temperature_k[:, i], np.asarray(thresholds_k, float))
        out[i] = START_AGE_GA-crossing/1000
        status_all[i] = status
    return out, status_all


def coherent_fractions(history, depth_index, band_k, chron_myr, realizations=16, kind='periodic', seed=0):
    """Retained fractions of a steady-field record for a reversing field.

    The acquisition kernel is the exact piecewise-linear cooling kernel of that
    depth through the blocking band; each value is |signed record| divided by
    the known acquired fraction, so 1 means no cancellation. 'periodic' uses
    equal chrons with the given duration and evenly spaced phases; 'poisson'
    uses exponentially distributed chrons of the given mean and one seed per
    realization. Returns the array of realizations and the known fraction.
    """
    kernel = recording_intervals(history.time_myr, history.temperature_k[:, depth_index], band_k)
    known = float(kernel['weight'].sum())
    if known <= 0:
        return np.full(realizations, np.nan), known
    values = []
    for member in range(realizations):
        signed = record_intervals([kernel], kind, chron_myr=chron_myr, phase=2*member/realizations if kind == 'periodic' else float(member % 2),
                                  seed=seed+member)[0]
        values.append(abs(signed)/known)
    return np.array(values), known


def coherent_fraction(history, depth_index, band_k, chron_myr, realizations=16, kind='periodic', seed=0):
    """Median of coherent_fractions, kept for the earlier call signature."""
    values, known = coherent_fractions(history, depth_index, band_k, chron_myr, realizations, kind, seed)
    return (float(np.nanmedian(values)) if np.isfinite(values).any() else np.nan), known


def cooling_duration_myr(history, depth_index, band_k):
    """Elapsed time between the last cooling through the top and bottom of a band."""
    crossing, status = last_downward_crossings(history.time_myr, history.temperature_k[:, depth_index], np.asarray(band_k, float))
    if np.any(status != 1):
        return None
    return float(crossing[0]-crossing[1])


def sample_parameters(n, ranges, seed):
    """Latin-hypercube sample of the declared parameter ranges."""
    names = list(ranges)
    sampler = qmc.LatinHypercube(d=len(names), seed=seed)
    unit = sampler.random(n)
    lows = np.array([ranges[k][0] for k in names], float)
    highs = np.array([ranges[k][1] for k in names], float)
    values = qmc.scale(unit, lows, highs)
    return [dict(zip(names, row)) for row in values]
