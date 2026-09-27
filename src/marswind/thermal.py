"""Independent 1-D conductive crust experiment; no atmosphere or external data.

Depth is positive downwards; basal heat flux is positive upwards. SI units are
used in the solver, except the explicitly named Myr arguments. This is a fixed,
solid column, not a reconstruction of a Martian region or a remanence model.
"""
from dataclasses import dataclass
from collections.abc import Callable

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import splu

SECONDS_PER_MYR = 1e6 * 365.25 * 86400


@dataclass(frozen=True)
class Column:
    thickness_m: float = 50_000.0
    conductivity_w_m_k: float = 3.0
    density_kg_m3: float = 2900.0
    heat_capacity_j_kg_k: float = 800.0
    surface_temperature_k: float = 220.0
    cells: int = 100

    def __post_init__(self):
        values = (self.thickness_m, self.conductivity_w_m_k, self.density_kg_m3,
                  self.heat_capacity_j_kg_k, self.surface_temperature_k)
        if not all(np.isfinite(v) and v > 0 for v in values):
            raise ValueError("Column properties must be finite and positive")
        if isinstance(self.cells, bool) or not isinstance(self.cells, int) or self.cells < 2:
            raise ValueError("At least two integer cells are required")

    @property
    def depth_m(self):
        return np.linspace(0.0, self.thickness_m, self.cells + 1)

    @property
    def diffusivity_m2_s(self):
        return self.conductivity_w_m_k / (self.density_kg_m3 * self.heat_capacity_j_kg_k)


@dataclass(frozen=True)
class HeatPulse:
    time_myr: float
    amplitude_k: float
    center_m: float
    width_m: float

    def profile(self, column: Column):
        """Gaussian heat increment tapered to zero at both boundaries.

        The sin² taper also gives zero derivative at the bottom. Amplitude is
        a scale, equal to the peak for a pulse centred at half the thickness.
        """
        if (not all(np.isfinite(v) for v in (self.time_myr, self.amplitude_k,
                                            self.center_m, self.width_m))
                or self.time_myr <= 0 or self.amplitude_k < 0 or self.width_m <= 0
                or not 0 < self.center_m < column.thickness_m):
            raise ValueError("Invalid heat pulse")
        z = column.depth_m
        delta = (self.amplitude_k * np.exp(-0.5 * ((z-self.center_m)/self.width_m)**2)
                 * np.sin(np.pi*z/column.thickness_m)**2)
        delta[[0, -1]] = 0.0
        return delta


@dataclass
class History:
    time_myr: np.ndarray
    depth_m: np.ndarray
    temperature_k: np.ndarray  # time × depth; post-pulse at an event time
    pulses: list[dict]

    def future_peak_k(self):
        """Maximum from each candidate recording time through the final time.

        Includes the candidate time itself. Uses every integration step before
        any display thinning. A threshold crossing is an exclusion criterion;
        remaining below it is not proof of remanence acquisition or survival.
        """
        return np.maximum.accumulate(self.temperature_k[::-1], axis=0)[::-1]


def steady_temperature(column: Column, basal_flux_w_m2: float,
                       heat_production_w_m3: float):
    """Exact solution for constant heat production and the mixed boundaries."""
    z, k, length = column.depth_m, column.conductivity_w_m_k, column.thickness_m
    return (column.surface_temperature_k + basal_flux_w_m2*z/k
            + heat_production_w_m3*(length*z-z*z/2)/k)


def solve(column: Column, duration_myr: float, step_myr: float,
          basal_flux: Callable[[float], float], heat_production: Callable[[float], float],
          initial_temperature_k: np.ndarray, pulses: tuple[HeatPulse, ...] = (),
          pulse_step_myr: float | None = None, pulse_window_myr: float = 20.) -> History:
    """Backward Euler with a half control volume at the flux boundary.

    Second-order spatial differences, first-order time stepping. Every event
    and the final time must lie on the requested base grid: never silently
    round a heat event. Sources are evaluated at the end of each time interval.
    Heat pulses are applied AFTER conduction to their event time, not before.
    An optional finer grid resolves the rapid post-pulse transient; it must
    divide the base step exactly. No stored temperature is interpolated.
    """
    if not (np.isfinite(duration_myr) and np.isfinite(step_myr)
            and duration_myr > 0 and step_myr > 0):
        raise ValueError("Duration and step must be finite and positive")
    count = duration_myr/step_myr
    if not np.isclose(count, round(count), rtol=0, atol=1e-8):
        raise ValueError("Duration must be an integer number of steps")
    count = round(count)
    initial = np.asarray(initial_temperature_k, dtype=float)
    if (initial.shape != (column.cells+1,) or not np.isfinite(initial).all()
            or np.any(initial <= 0)
            or not np.isclose(initial[0], column.surface_temperature_k, rtol=0, atol=1e-8)):
        raise ValueError("Initial profile must be positive, finite and satisfy the surface temperature")
    times = np.arange(count+1)*step_myr
    if pulse_step_myr is not None:
        if (not np.isfinite(pulse_step_myr) or pulse_step_myr <= 0
                or not np.isfinite(pulse_window_myr) or pulse_window_myr <= 0
                or pulse_step_myr > step_myr
                or not np.isclose(step_myr/pulse_step_myr, round(step_myr/pulse_step_myr), rtol=0, atol=1e-8)
                or not np.isclose(pulse_window_myr/step_myr, round(pulse_window_myr/step_myr), rtol=0, atol=1e-8)):
            raise ValueError("Pulse refinement must divide the base step and span whole base steps")
    increments = []
    for pulse in pulses:
        increment = pulse.profile(column)
        index = pulse.time_myr/step_myr
        if pulse.time_myr > duration_myr or not np.isclose(index, round(index), rtol=0, atol=1e-8):
            raise ValueError("Pulse time must lie on the integration grid")
        increments.append((pulse.time_myr, increment))
        if pulse_step_myr is not None:
            end = min(pulse.time_myr+pulse_window_myr, duration_myr)
            fine = pulse.time_myr+np.arange(round((end-pulse.time_myr)/pulse_step_myr)+1)*pulse_step_myr
            times = np.union1d(times, fine)
    events: dict[int, list] = {}
    for time, increment in increments:
        events.setdefault(int(np.searchsorted(times, time)), []).append(increment)

    n, dz = column.cells, column.thickness_m/column.cells
    capacity = column.density_kg_m3 * column.heat_capacity_j_kg_k
    factors = {}
    q = np.array([basal_flux(float(t)) for t in times])
    heating = np.array([heat_production(float(t)) for t in times])
    if not np.isfinite(q).all() or not np.isfinite(heating).all() or np.any(q < 0) or np.any(heating < 0):
        raise ValueError("This experiment requires finite, non-negative heat sources")
    temperature = np.empty((len(times), n+1))
    temperature[:, 0] = column.surface_temperature_k
    temperature[0] = initial
    event_log = []
    for i in range(1, len(times)):
        dt = (times[i]-times[i-1])*SECONDS_PER_MYR
        r = column.diffusivity_m2_s*dt/dz**2
        if dt not in factors:
            lower = np.full(n-1, -r)
            lower[-1] = -2*r
            factors[dt] = splu(diags([lower, np.full(n, 1+2*r), np.full(n-1, -r)],
                                    [-1, 0, 1], format="csc"))
        rhs = temperature[i-1, 1:] + dt*heating[i]/capacity
        rhs[0] += r*column.surface_temperature_k
        rhs[-1] += dt*2*q[i]/(capacity*dz)
        temperature[i, 1:] = factors[dt].solve(rhs)
        if i in events:
            before = temperature[i].copy()
            increment = np.sum(events[i], axis=0)
            temperature[i] += increment
            event_log.append({"time_myr": float(times[i]),
                              "pre_pulse_temperature_k": before.tolist(),
                              "added_energy_j_m2": float(capacity*np.trapezoid(increment, dx=dz))})
    return History(times, column.depth_m, temperature, event_log)


def eigenmode_benchmark(cells: int = 100, step_myr: float = 0.125,
                        duration_myr: float = 50.0):
    """Exact transient: insulating bottom, fixed surface, sinusoidal anomaly."""
    column = Column(cells=cells)
    wavenumber = np.pi/(2*column.thickness_m)
    initial = column.surface_temperature_k + 100*np.sin(wavenumber*column.depth_m)
    history = solve(column, duration_myr, step_myr, lambda t: 0., lambda t: 0., initial)
    exact = (column.surface_temperature_k + 100*np.sin(wavenumber*column.depth_m)
             * np.exp(-column.diffusivity_m2_s*wavenumber**2*duration_myr*SECONDS_PER_MYR))
    return float(np.max(np.abs(history.temperature_k[-1]-exact)))
