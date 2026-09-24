"""Transparent laboratory parsing; no automatic component or paleofield fitting."""
import csv
import io
import math


def magic_tables(text):
    tables = {}
    for chunk in text.split('>>>>>>>>>>'):
        lines = chunk.strip().splitlines()
        if len(lines) > 2:
            tables[lines[0].split('\t')[-1]] = list(csv.DictReader(io.StringIO('\n'.join(lines[1:])), delimiter='\t'))
    return tables


def read_rockpy_nrm(text):
    """Read the observed RockPy 2G export layout, preserving unverified units.

    Treatment labels and amplitude are kept verbatim. Magnitudes are normalized
    within each file: the export has no explicit magnitude unit. Do not interpret
    these as SI moments, convert AF labels, or infer a Martian geographic direction.
    """
    lines = text.splitlines()
    if not lines or 'RockPy exported' not in lines[0]:
        raise ValueError('Not a supported RockPy export')
    rows = []
    for line in lines[2:]:
        if not line.strip():
            continue
        # Thermal labels exceed the AF export's six-character prefix.
        if line.startswith(('TT', 'TRM')):
            label, remainder = line.split(maxsplit=1)
            fields = remainder.split()
        else:
            label, fields = line[:6].strip(), line[6:].split()
        if len(fields) < 5:
            raise ValueError('Incomplete laboratory row')
        dec, inc, magnitude = float(fields[0]), float(fields[1]), float(fields[4])
        if not all(math.isfinite(v) for v in [dec, inc, magnitude]) or magnitude < 0:
            raise ValueError('Invalid direction or magnitude')
        rows.append(dict(order=len(rows)+1, treatment_label=label,
                         remanence_origin='laboratory' if label.startswith('TRM') else 'natural',
                         declination_deg=dec, inclination_deg=inc,
                         magnitude_as_archived=magnitude))
    if not rows or rows[0]['magnitude_as_archived'] <= 0:
        raise ValueError('Cannot normalize an absent or zero initial magnitude')
    initial = rows[0]['magnitude_as_archived']
    for row in rows:
        row['relative_magnitude'] = row['magnitude_as_archived'] / initial
    return rows


def detection_cells(longitude, latitude, step=2):
    """Return occupied (latitude row, longitude column) bins, never dry cells."""
    import numpy as np
    lon, lat = np.broadcast_arrays(longitude, latitude)
    if not np.all(np.isfinite(lon) & np.isfinite(lat) & (abs(lat) <= 90)):
        raise ValueError('Invalid Mars coordinates')
    i = np.minimum(((lat+90)/step).astype(int), int(180/step)-1)
    j = ((lon % 360)/step).astype(int)
    return np.unique(np.column_stack((i.ravel(), j.ravel())), axis=0)
