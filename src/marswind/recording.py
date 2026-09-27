"""Original, explicitly synthetic recording and magnetic-observation benchmarks.

A blocking-temperature relay is not a calibrated grain-relaxation model.
Unknown prehistory remains an explicit fraction, never an inferred zero field.
"""
import numpy as np
from scipy.special import ndtr, ndtri

MU0 = 4e-7 * np.pi


def last_downward_crossings(time_myr, temperature_k, thresholds_k):
    """Last cooling crossing of each threshold in a piecewise-linear history.

    Duplicate times describe instantaneous jumps; a jump does not acquire TRM.
    Status 0: never reset/acquired in supplied history (unknown initial record).
    Status 1: last cooling crossing known. Status 2: unblocked at final time.
    """
    t, temp, thresholds = (np.asarray(x, dtype=float) for x in (time_myr, temperature_k, thresholds_k))
    if (t.ndim != 1 or temp.shape != t.shape or thresholds.ndim != 1 or len(t) < 2
            or not all(np.isfinite(x).all() for x in (t, temp, thresholds))
            or np.any(np.diff(t) < 0) or t[-1] <= t[0]):
        raise ValueError('Finite ordered thermal samples and thresholds required')
    result = np.full(thresholds.shape, np.nan)
    cooling = (np.diff(temp) < 0) & (np.diff(t) > 0)
    edges = np.diff(np.r_[False, cooling, False].astype(int))
    for start, end in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)):
        # Cooling intervals start..end-1 span samples start..end.
        eligible = (thresholds <= temp[start]) & (thresholds > temp[end])
        result[eligible] = np.interp(thresholds[eligible], temp[start:end+1][::-1], t[start:end+1][::-1])
    status = np.where(np.isfinite(result), 1, 0)
    status[temp[-1] >= thresholds] = 2
    result[status != 1] = np.nan
    return result, status


def include_pre_pulse_samples(history, depth_index):
    """Preserve conduction to an event before its instantaneous positive pulse."""
    times, values = list(history.time_myr), list(history.temperature_k[:, depth_index])
    for event in sorted(history.pulses, key=lambda x: x['time_myr'], reverse=True):
        index = int(np.searchsorted(history.time_myr, event['time_myr']))
        times.insert(index, event['time_myr'])
        values.insert(index, event['pre_pulse_temperature_k'][depth_index])
    return np.array(times), np.array(values)


def field_at(times, kind, *, chron_myr=20., phase=0., seed=0, shutdown_myr=500.):
    """Unit signed fields; time is elapsed Myr, never an absolute Mars age."""
    t = np.asarray(times, dtype=float)
    if not np.isfinite(t).all() or np.any(t < 0):
        raise ValueError('Finite nonnegative acquisition times required')
    if kind == 'steady': return np.ones_like(t)
    if kind == 'absent': return np.zeros_like(t)
    if kind == 'shutdown': return (t < shutdown_myr).astype(float)
    if kind == 'intermittent': return (((t < 300) | ((t >= 900) & (t < 1200)))).astype(float)
    if not np.isfinite(chron_myr) or chron_myr <= 0 or not 0 <= phase < 2:
        raise ValueError('Positive chron duration and phase in [0, 2) required')
    if kind == 'periodic': return 1. - 2*(np.floor(t/chron_myr+phase).astype(np.int64) % 2)
    if kind == 'poisson':
        rng = np.random.default_rng(seed)
        events, current = [], 0.
        while current <= t.max(initial=0):
            current += rng.exponential(chron_myr)
            events.append(current)
        polarity = 1 if phase < 1 else -1
        return polarity*(1. - 2*(np.searchsorted(events, t, side='right') % 2))
    raise ValueError('Unknown field history')


def record(crossings, status, kind, **kwargs):
    """Equal-weight midpoint quadrature over a declared temperature band.

    Returns known signed contribution, unresolved initial fraction, and hot
    fraction for each depth. No renormalization discards unrecorded material.
    """
    t, state = np.asarray(crossings), np.asarray(status)
    if t.shape != state.shape or t.ndim != 2 or not np.isin(state, [0, 1, 2]).all():
        raise ValueError('Depth × threshold arrays with valid states required')
    contributions = np.zeros_like(t, dtype=float)
    known = state == 1
    contributions[known] = field_at(t[known], kind, **kwargs)
    return contributions.mean(axis=1), (state == 0).mean(axis=1), (state == 2).mean(axis=1)


def cylinder_axis_operator(radius_km, top_km, bottom_km, heights_km):
    """Exact on-axis B_z of coaxial, vertically magnetized uniform cylinders.

    Positive magnetization and field point upwards. Entries are nT/(A/m).
    Each column is one layer; all boundaries and heights refer to a flat surface.
    This finite-body toy is not a spherical Mars orbital-field inversion.
    """
    top, bottom, h = (np.asarray(x, dtype=float) for x in (top_km, bottom_km, heights_km))
    if (not np.isfinite(radius_km) or radius_km <= 0 or top.ndim != 1 or top.shape != bottom.shape
            or h.ndim != 1 or not all(np.isfinite(x).all() for x in (top, bottom, h))
            or np.any(top < 0) or np.any(bottom <= top) or np.any(h < 0)):
        raise ValueError('Positive radius and ordered layer boundaries required')
    def disk(distance): return distance/np.sqrt(distance**2+radius_km**2)
    return MU0/2*1e9*(disk(h[:, None]+bottom)-disk(h[:, None]+top))


def temporal_gain(crossings, weights, periods_myr):
    """Normalized frequency response of the known acquisition kernel only."""
    t, w, p = (np.asarray(x, dtype=float) for x in (crossings, weights, periods_myr))
    if t.shape != w.shape or np.any(w < 0) or np.any(p <= 0) or not np.isfinite(w).all():
        raise ValueError('Nonnegative matching weights and positive periods required')
    mask = np.isfinite(t) & (w > 0)
    if not mask.any(): return np.full(p.shape, np.nan)
    return np.abs(np.exp(2j*np.pi*t[mask, None]/p[None, :]).T @ w[mask])/w[mask].sum()


def harmonic_attenuation(degrees, radius_km, height_km):
    """Exact single-degree radial magnetic-field attenuation in a vacuum."""
    degrees = np.asarray(degrees, dtype=float)
    if np.any(degrees < 1) or np.any(degrees != np.floor(degrees)) or radius_km <= 0 or height_km < 0:
        raise ValueError('Positive integer magnetic degrees and valid radii required')
    return (radius_km/(radius_km+height_km))**(degrees+2)


def detection_power(snr, alpha=.01):
    """Two-sided known-template Gaussian test, fixed template, no search trials."""
    if not 0 < alpha < 1: raise ValueError('Invalid false-alarm probability')
    z = ndtri(1-alpha/2)
    return ndtr(np.asarray(snr)-z)+ndtr(-np.asarray(snr)-z)


def recording_intervals(time_myr, temperature_k, band_k):
    """Exact acquisition density for a uniform blocking band on linear segments.

    A downward crossing survives only above every subsequent temperature. This
    future-maximum construction handles reheating without sampling thresholds.
    Each output interval carries a constant acquisition density in elapsed time.
    """
    t,temp=np.asarray(time_myr,dtype=float),np.asarray(temperature_k,dtype=float)
    low,high=band_k
    if (t.ndim!=1 or temp.shape!=t.shape or len(t)<2 or not np.isfinite(t).all()
            or not np.isfinite(temp).all() or np.any(np.diff(t)<0) or not np.isfinite([low,high]).all() or high<=low):
        raise ValueError('Ordered finite history and positive-width band required')
    future=np.maximum.accumulate(temp[::-1])[::-1]
    upper=np.minimum(temp[:-1],high)
    lower=np.maximum(future[1:],low)
    mask=(upper>lower)&(np.diff(temp)<0)&(np.diff(t)>0)
    slope=(temp[:-1][mask]-temp[1:][mask])/np.diff(t)[mask]
    start=t[:-1][mask]+(temp[:-1][mask]-upper[mask])/slope
    end=t[:-1][mask]+(temp[:-1][mask]-lower[mask])/slope
    weight=(upper[mask]-lower[mask])/(high-low)
    unknown=float(np.clip((high-max(low,temp.max()))/(high-low),0,1))
    hot=float(np.clip((min(high,temp[-1])-low)/(high-low),0,1))
    if not np.isclose(weight.sum()+unknown+hot,1,atol=1e-10):
        raise ValueError('History contains an unsupported instantaneous cooling jump')
    return {'start':start,'end':end,'weight':weight,'unknown':unknown,'hot':hot}


def interval_field_mean(start,end,kind,*,chron_myr=20.,phase=0.,seed=0,shutdown_myr=500.):
    """Analytic averages of each declared piecewise-constant field history."""
    a,b=np.asarray(start,dtype=float),np.asarray(end,dtype=float)
    if a.shape!=b.shape or np.any(a<0) or np.any(b<=a) or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('Positive-width, finite, nonnegative intervals required')
    if kind=='steady':return np.ones_like(a)
    if kind=='absent':return np.zeros_like(a)
    if kind=='shutdown':return np.clip(shutdown_myr-a,0,b-a)/(b-a)
    if kind=='intermittent':
        return sum(np.maximum(0,np.minimum(b,hi)-np.maximum(a,lo)) for lo,hi in [(0,300),(900,1200)])/(b-a)
    if not np.isfinite(chron_myr) or chron_myr<=0 or not 0<=phase<2:raise ValueError('Invalid reversal parameters')
    if kind=='periodic':
        def primitive(t):
            u=(t/chron_myr+phase)%2
            return chron_myr*np.where(u<=1,u,2-u)
        return (primitive(b)-primitive(a))/(b-a)
    if kind=='poisson':
        rng=np.random.default_rng(seed);edges=[0.]
        while edges[-1]<=b.max(initial=0):edges.append(edges[-1]+rng.exponential(chron_myr))
        edges=np.array(edges);signs=(1 if phase<1 else -1)*(1-2*(np.arange(len(edges)-1)%2))
        primitive=np.r_[0,np.cumsum(signs*np.diff(edges))]
        return (np.interp(b,edges,primitive)-np.interp(a,edges,primitive))/(b-a)
    raise ValueError('Unknown field history')


def record_intervals(kernels,kind,**kwargs):
    return np.array([np.dot(k['weight'],interval_field_mean(k['start'],k['end'],kind,**kwargs)) for k in kernels])


def interval_temporal_gain(kernels,layer_weights,periods_myr):
    """Frequency response with exact segment integration, not time sampling."""
    periods=np.asarray(periods_myr,dtype=float);numerator=np.zeros(len(periods),dtype=complex);denominator=0.
    for kernel,scale in zip(kernels,layer_weights):
        w=scale*kernel['weight'];denominator+=w.sum()
        # Block periods to bound memory for a finely sampled thermal history.
        for j,p in enumerate(periods):
            mid=(kernel['start']+kernel['end'])/2;dt=kernel['end']-kernel['start']
            numerator[j]+=np.dot(w,np.sinc(dt/p)*np.exp(2j*np.pi*mid/p))
    return np.abs(numerator)/denominator if denominator>0 else np.full(len(periods),np.nan)
