"""Small, explicit scientific operations used by the observation pipeline.

This module has no network or MCD dependency. No calculation identifies the
origin of the dichotomy, or turns a candidate crater into a measured provenance.
"""
import numpy as np


def east_longitude(longitude):
    return np.asarray(longitude) % 360


def temperature_at_depth(radius_km, temperature_k, depth_km):
    """Linear interpolation below this profile's OWN surface; no extrapolation."""
    radius=np.asarray(radius_km,dtype=float);temperature=np.asarray(temperature_k,dtype=float)
    if radius.shape!=temperature.shape or radius.ndim!=1 or len(radius)<2:
        raise ValueError('Radius and temperature must be matching 1-D profiles')
    depth=radius.max()-radius;order=np.argsort(depth);depth=depth[order]
    if np.any(np.diff(depth)<=0):raise ValueError('Profile depths must be unique')
    return np.interp(depth_km,depth,temperature[order],left=np.nan,right=np.nan)


def threshold_depth(radius_km, temperature_k, threshold_k):
    """First downward crossing of an ordering temperature, linearly interpolated."""
    radius=np.asarray(radius_km);t=np.asarray(temperature_k)
    d=radius.max()-radius;i=np.argsort(d);d=d[i];t=t[i]
    if t[0]>=threshold_k:return float(d[0])
    for k in range(1,len(d)):
        if t[k]>=threshold_k and t[k-1]<threshold_k:
            return float(d[k-1]+(d[k]-d[k-1])*(threshold_k-t[k-1])/(t[k]-t[k-1]))
    return None


def depth_quality(best, lower, upper):
    """Preserve negative fits; -1e100 in the published files is a missing bound."""
    b=np.asarray(best,dtype=float);lo=np.asarray(lower,dtype=float);hi=np.asarray(upper,dtype=float)
    bounded=np.isfinite(lo)&np.isfinite(hi)&(lo>-1e90)&(hi>-1e90)&(lo<=b)&(b<=hi)
    usable=bounded&np.isfinite(b)&(b>=0)
    return bounded,usable


def weighted_mean(values, latitude, mask):
    """Cos(latitude) area weights on an evenly spaced longitude/latitude grid."""
    a=np.asarray(values);w=np.broadcast_to(np.cos(np.deg2rad(latitude))[:,None],a.shape)
    valid=np.asarray(mask,dtype=bool)&np.isfinite(a)
    if not np.any(valid):raise ValueError('Empty spatial selection')
    return float(np.sum(a[valid]*w[valid])/np.sum(w[valid]))


def hemisphere_contrast(field,lat,minimum_latitude=0):
    a=np.asarray(field);lat=np.asarray(lat)
    n=np.broadcast_to((lat>minimum_latitude)[:,None],a.shape)
    s=np.broadcast_to((lat<-minimum_latitude)[:,None],a.shape)
    north=weighted_mean(a,lat,n);south=weighted_mean(a,lat,s)
    return {'north_mean_nT':north,'south_mean_nT':south,'south_north_ratio':south/north}
