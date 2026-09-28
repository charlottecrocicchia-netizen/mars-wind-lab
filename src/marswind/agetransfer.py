"""Surface age as a predictor of orbital magnetic amplitude.

The USGS SIM 3292 unit codes encode the epoch of the mapped surface. This
module turns those codes into ordinal and indicator features and evaluates
whether age improves out-of-region prediction of the crustal field beyond the
structural predictors already tested. Surface age is not the age of the deep
magnetic source; a result here constrains predictability, not causation.
"""
import re

import numpy as np

# Ordinal position of each epoch class (Tanaka et al., 2014 chronostratigraphy).
EPOCH_RANK = {'eN': 1., 'mN': 2., 'lN': 3., 'eH': 4., 'lH': 5., 'eA': 6., 'mA': 7., 'lA': 8.,
              'N': 2., 'H': 4.5, 'A': 7.}
# Declared approximate class-centre ages in Ga. These are reading aids for the
# ordinal classes, not radiometric or crater-count ages of individual units.
EPOCH_AGE_GA = {'eN': 4.1, 'mN': 3.9, 'lN': 3.75, 'eH': 3.6, 'lH': 3.45, 'eA': 2.6, 'mA': 1.1, 'lA': 0.3,
                'N': 3.9, 'H': 3.5, 'A': 1.5}
CODE = re.compile(r'^([eml]?)([NHA]{1,2})([a-z]*)$')


def epoch_features(unit_code):
    """Ordinal rank, approximate age and period indicators from a SIM 3292 code.

    Two-period codes (HN, AH, AN) average their undivided classes. A prefix
    e/m/l applies only to single-period codes. Unknown codes raise.
    """
    match = CODE.match(str(unit_code))
    if not match:
        raise ValueError(f'Unrecognised geological unit code: {unit_code!r}')
    prefix, periods, _ = match.groups()
    if len(periods) == 1:
        key = prefix+periods if prefix else periods
        rank, age = EPOCH_RANK[key], EPOCH_AGE_GA[key]
    else:
        if prefix:
            raise ValueError(f'Prefix on a two-period code is not defined: {unit_code!r}')
        rank = float(np.mean([EPOCH_RANK[p] for p in periods]))
        age = float(np.mean([EPOCH_AGE_GA[p] for p in periods]))
    return {'rank': rank, 'age_ga': age, 'noachian': float('N' in periods),
            'hesperian': float('H' in periods), 'amazonian': float('A' in periods),
            'mixed': float(len(periods) == 2)}


def location_features(lat_deg, lon_deg):
    """Smooth degree-one and degree-two Cartesian functions on the sphere."""
    lat, lon = np.deg2rad(lat_deg), np.deg2rad(lon_deg)
    x, y, z = np.cos(lat)*np.cos(lon), np.cos(lat)*np.sin(lon), np.sin(lat)
    return np.column_stack([x, y, z, x*x, y*y, z*z, x*y, x*z, y*z])


def structure_features(relief_km, thickness_km, group_index, group_count):
    r, h = np.asarray(relief_km, float), np.asarray(thickness_km, float)
    groups = np.zeros((len(r), group_count))
    groups[np.arange(len(r)), np.asarray(group_index, int)] = 1.
    return np.column_stack([r, h, r*r, h*h, r*h, groups])


def age_features(unit_codes):
    rows = [epoch_features(c) for c in unit_codes]
    return np.column_stack([[r['rank'] for r in rows], [r['age_ga'] for r in rows],
                            [r['noachian'] for r in rows], [r['hesperian'] for r in rows],
                            [r['amazonian'] for r in rows]])


def skill(y_true, y_pred, weights, baseline):
    """1 − weighted MSE / weighted MSE of a constant baseline; negative is worse."""
    w = np.asarray(weights, float)
    num = np.sum(w*(np.asarray(y_true)-np.asarray(y_pred))**2)
    den = np.sum(w*(np.asarray(y_true)-baseline)**2)
    return float(1-num/den)


def by_class_summary(values, weights, ranks, masks):
    """Area-weighted mean of a target by epoch rank within each named mask."""
    out = []
    for name, mask in masks.items():
        for rank in np.unique(ranks):
            sel = mask & (ranks == rank) & np.isfinite(values)
            if sel.sum() >= 5:
                out.append({'region': name, 'rank': float(rank), 'cells': int(sel.sum()),
                            'weighted_mean': float(np.average(values[sel], weights=weights[sel]))})
    return out
