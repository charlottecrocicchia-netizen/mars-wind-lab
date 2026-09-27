"""Original predictive and laboratory sensitivity diagnostics; no causal fitting."""
import numpy as np


def ridge_predict(x_train, y_train, weights, x_test, alpha=.01):
    """Train-only weighted scaling; ridge on mean squared error, free intercept."""
    x, y, w, test = map(lambda a: np.asarray(a, dtype=float), (x_train, y_train, weights, x_test))
    if (x.ndim != 2 or test.ndim != 2 or x.shape[1] != test.shape[1]
            or y.shape != (len(x),) or w.shape != y.shape or np.any(w <= 0)
            or not all(np.isfinite(a).all() for a in (x, y, w, test)) or alpha <= 0):
        raise ValueError('Finite design matrices, positive weights and penalty required')
    w = w/w.sum()
    mean_y = w @ y
    if x.shape[1] == 0: return np.full(len(test), mean_y)
    mean = w @ x
    scale = np.sqrt(w @ ((x-mean)**2))
    # Features absent or constant in training cannot acquire a coefficient.
    keep = scale > 1e-10
    train = (x[:, keep]-mean[keep])/scale[keep]
    target = (test[:, keep]-mean[keep])/scale[keep]
    beta = np.linalg.solve(train.T@(w[:, None]*train)+alpha*np.eye(keep.sum()), train.T@(w*(y-mean_y)))
    return mean_y+target@beta


def longitude_folds(longitude, blocks=6, buffer_deg=10., offset_deg=0.):
    """Held-out complete wedges; a buffer excludes adjacent training longitudes.

    The angular separation shrinks near poles; callers limit latitude and must
    not describe this as a constant-distance or globally independent split.
    """
    lon = (np.asarray(longitude, dtype=float)-offset_deg) % 360
    if blocks < 2 or 360 % blocks or not 0 <= buffer_deg < 180-180/blocks:
        raise ValueError('Invalid wedge or buffer configuration')
    width = 360/blocks
    for i in range(blocks):
        center = (i+.5)*width
        distance = np.abs((lon-center+180) % 360-180)
        test = (lon >= i*width) & (lon < (i+1)*width)
        train = (~test) & (distance >= width/2+buffer_deg)
        yield train, test


def vector_from_direction(declination_deg, inclination_deg, magnitude):
    dec, inc = np.deg2rad(declination_deg), np.deg2rad(inclination_deg)
    return np.asarray(magnitude)[:, None]*np.column_stack((np.cos(inc)*np.cos(dec), np.cos(inc)*np.sin(dec), np.sin(inc)))


def axis_angle(a, b):
    """Unsigned angle between fitted axes; polarity is not resolved by an axis."""
    return float(np.rad2deg(np.arccos(np.clip(abs(np.dot(a, b)), 0, 1))))


def fit_demagnetization(vectors, anchored=False):
    """SVD line fit with an explicit direction convention and MAD index.

    Unanchored: centered line; anchored: line forced through zero. MAD is a
    collinearity index, not a confidence interval or evidence of ancient origin.
    The sign points along first-minus-last treatment vectors when resolvable.
    """
    x = np.asarray(vectors, dtype=float)
    if x.ndim != 2 or x.shape[1] != 3 or len(x) < 3 or not np.isfinite(x).all():
        raise ValueError('At least three finite 3-D treatment vectors required')
    norm = np.max(np.linalg.norm(x, axis=1))
    if norm <= 0: raise ValueError('Zero signal has no fitted direction')
    x = x/norm
    cloud = x if anchored else x-x.mean(axis=0)
    _, singular, axes = np.linalg.svd(cloud, full_matrices=False)
    if singular[0] < 1e-14: raise ValueError('Constant signal has no unanchored line')
    direction = axes[0]
    if np.dot(direction, x[0]-x[-1]) < 0: direction = -direction
    eigen = singular**2
    return {'axis': direction, 'mad_deg': float(np.rad2deg(np.arctan(np.sqrt(eigen[1:].sum()/eigen[0])))),
            'declination_deg': float(np.rad2deg(np.arctan2(direction[1], direction[0])) % 360),
            'inclination_deg': float(np.rad2deg(np.arcsin(np.clip(direction[2], -1, 1)))),
            'leading_variance_fraction': float(eigen[0]/eigen.sum())}


def line_sensitivity(vectors):
    fit = fit_demagnetization(vectors)
    anchored = fit_demagnetization(vectors, anchored=True)
    changes = []
    for j in range(len(vectors)):
        try: changes.append(axis_angle(fit['axis'], fit_demagnetization(np.delete(vectors, j, axis=0))['axis']))
        except ValueError: pass
    return {k: v for k, v in fit.items() if k != 'axis'} | {
        'anchored_axis_difference_deg': axis_angle(fit['axis'], anchored['axis']),
        'leave_one_treatment_out_max_axis_change_deg': max(changes) if changes else None,
        'leave_one_treatment_out_valid_fits': len(changes)}
