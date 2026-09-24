"""Spherical sampling and descriptive contrasts for the regional pilot.

Grid nodes are quadrature samples of correlated model fields, never replicates.
No significance, posterior probability or causal attribution is calculated.
"""
import numpy as np
from scipy.ndimage import map_coordinates

MARS_RADIUS_KM = 3393.5


def distance_bearing(lat, lon, center_lat, center_lon):
    """Great-circle distance (km) and clockwise azimuth from north (degrees)."""
    p, p0 = np.deg2rad(lat), np.deg2rad(center_lat)
    dl = np.deg2rad(np.asarray(lon) - center_lon)
    a = np.sin((p-p0)/2)**2 + np.cos(p)*np.cos(p0)*np.sin(dl/2)**2
    distance = 2*MARS_RADIUS_KM*np.arcsin(np.sqrt(np.clip(a, 0, 1)))
    bearing = np.rad2deg(np.arctan2(np.sin(dl)*np.cos(p),
                       np.cos(p0)*np.sin(p)-np.sin(p0)*np.cos(p)*np.cos(dl))) % 360
    return distance, bearing


def destination(lat, lon, distance_km, bearing_deg):
    p, l, b = np.deg2rad(lat), np.deg2rad(lon), np.deg2rad(bearing_deg)
    d = np.asarray(distance_km)/MARS_RADIUS_KM
    p2 = np.arcsin(np.clip(np.sin(p)*np.cos(d)+np.cos(p)*np.sin(d)*np.cos(b), -1, 1))
    l2 = l+np.arctan2(np.sin(b)*np.sin(d)*np.cos(p), np.cos(d)-np.sin(p)*np.sin(p2))
    return np.rad2deg(p2), np.rad2deg(l2) % 360


def sample_mola(grid, lat, lon):
    """Bilinear sample of the north-first 4 ppd, pixel-centered MEGDR (km).

    Longitude is periodic; no pole extrapolation is allowed.
    """
    lat, lon = np.broadcast_arrays(lat, lon)
    if np.any(np.abs(lat) > 89.875):
        raise ValueError('MOLA interpolation cannot extrapolate past polar pixel centers')
    padded = np.pad(grid, ((0, 0), (1, 1)), mode='wrap')
    coords = np.array([(89.875-lat)*4, ((lon % 360)-.125)*4+1])
    return map_coordinates(padded.astype(float), coords, order=1, mode='nearest')/1000


def mean(values, weights, mask):
    mask = np.asarray(mask) & np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    return float(np.average(values[mask], weights=weights[mask])) if mask.any() else None


def contrast(values, weights, inside, outside, units=None):
    """Area-weighted ratio and exact map-unit standardization on common support.

    Matched ratio reweights outside means to inside map-unit area proportions.
    Neither map-unit matching nor an adjacent ring controls deep lithology,
    alteration age, exposure, impact effects, or magnetic source geometry.
    """
    inner, outer = mean(values, weights, inside), mean(values, weights, outside)
    result = {'inside_nT':inner, 'outside_nT':outer,
              'ratio':inner/outer if inner is not None and outer else None,
              'inside_nodes':int(np.sum(inside)), 'outside_nodes':int(np.sum(outside))}
    if units is None:
        return result
    strata = []
    for unit in np.intersect1d(units[inside], units[outside]):
        if unit < 0:
            continue
        a, b = inside & (units == unit), outside & (units == unit)
        strata.append({'unit_index':int(unit), 'inside_weight':float(weights[a].sum()),
                       'outside_weight':float(weights[b].sum()),
                       'inside_nodes':int(a.sum()), 'outside_nodes':int(b.sum()),
                       'inside_area_fraction':float(weights[a].sum()/weights[inside].sum()),
                       'outside_area_fraction':float(weights[b].sum()/weights[outside].sum()),
                       'inside_nT':mean(values, weights, a), 'outside_nT':mean(values, weights, b)})
    shared = sum(s['inside_weight'] for s in strata)
    total = float(weights[inside].sum())
    support = float(np.clip(shared/total, 0, 1)) if total else 0
    matched_inner = sum(s['inside_weight']*s['inside_nT'] for s in strata)/shared if shared else None
    matched_outer = sum(s['inside_weight']*s['outside_nT'] for s in strata)/shared if shared else None
    result.update(common_support_fraction=support, strata=strata,
                  matched_inside_nT=matched_inner, matched_outside_nT=matched_outer,
                  matched_ratio=matched_inner/matched_outer if matched_outer else None)
    return result


def radial_profile(values, weights, normalized_radius, edges):
    rows=[]
    for a,b in zip(edges[:-1],edges[1:]):
        m=(normalized_radius>=a)&(normalized_radius<b)
        rows.append({'radius_R':float((a+b)/2), 'mean':mean(values,weights,m), 'nodes':int(m.sum())})
    return rows


def morphology(grid, lat, lon, diameter, azimuth_step=30, radius_scale=1):
    """Published radial d/D recipe, with a fixed catalog rim (no rim optimization).

    Sample 12 radial rays; median across azimuth, center minimum within 0.2R,
    outer median at 1–1.2R. Negative depths are retained, not silently clipped.
    """
    radius = diameter/2*radius_scale
    x = np.linspace(0,2,201)
    bearings = np.arange(0,360,azimuth_step)
    lats,lons=destination(lat,lon,x[None,:]*radius,bearings[:,None])
    rays=sample_mola(grid,lats,lons)
    profile=np.median(rays,axis=0)
    floor=float(np.min(profile[x<=.2]))
    rim=float(np.median(profile[(x>=1)&(x<=1.2)]))
    return {'normalized_radius':x.tolist(),'median_elevation_km':profile.tolist(),
            'azimuth_q25_km':np.percentile(rays,25,axis=0).tolist(),
            'azimuth_q75_km':np.percentile(rays,75,axis=0).tolist(),
            'floor_km':floor,'rim_km':rim,'depth_km':rim-floor,
            'depth_diameter':(rim-floor)/(2*radius),'rays':len(bearings)}
