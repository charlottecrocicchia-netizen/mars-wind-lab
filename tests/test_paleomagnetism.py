"""Protect event, unit, censoring and spatial-observation distinctions."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pytest
from marswind.paleomagnetism import read_rockpy_nrm, detection_cells, magic_tables

ROOT=Path(__file__).resolve().parents[1]
def load(name):return json.loads((ROOT/f'research/data/{name}.json').read_text())


def test_export_preserves_thermal_labels_and_separates_lab_acquisition():
    text='Sample >> RockPy exported\nheader\nNRM     20.0 10.0 20.0 10.0 2E-5\nAF  15  20.0 10.0 20.0 10.0 1E-5\nTT8531500 20.0 10.0 20.0 10.0 5E-6\nTRM8531500 40.0 10.0 40.0 10.0 8E-5\n'
    rows=read_rockpy_nrm(text)
    assert [r['relative_magnitude'] for r in rows]==[1,.5,.25,4]
    assert rows[2]['treatment_label']=='TT8531500'
    assert rows[3]['remanence_origin']=='laboratory'
    assert all('moment_Am2' not in r for r in rows)  # No invented SI conversion.
    with pytest.raises(ValueError):read_rockpy_nrm(text.replace('2E-5','0'))


def test_detection_cells_wrap_longitudes_and_union_instruments_without_inventing_absence():
    cells=detection_cells([-1,359,1,361,180],[0,0,0,0,90])
    assert cells.tolist()==[[45,0],[45,179],[89,90]]
    assert len(detection_cells([],[]))==0
    with pytest.raises(ValueError):detection_cells([1],[91])


def test_compilation_keeps_bounds_missing_errors_and_distinct_event_ages():
    data=load('paleomagnetism');records={r['name']:r for r in data['records']}
    assert len(records)==16
    assert {'MIL 03346','ALH 84001','EETA 79001','LEW 88516','Yamato 000593','Lafayette'}<=records.keys()
    assert records['GRV 020090']['paleointensity_kind']=='lower_bound'
    assert records['Yamato 000593']['paleointensity_kind']=='upper_bound'
    assert records['Shergotty']['paleointensity_uncertainty_uT'] is None
    assert records['Tissint']['age_kind']=='upper_bound'
    assert records['ALH 84001']['age_uncertainty_Ma']==75  # Superscript 2 is a footnote.
    assert all(r['mars_coordinates'] is None for r in records.values())
    events=records['Lafayette']['events']
    assert events[0]['age_Ma']>events[1]['age_Ma'] and events[2]['age_Ma'] is None
    assert records['NWA 7034 paired stones']['paleointensity_uT'] is None


def test_extended_lab_snapshot_preserves_provenance_and_lab_trm():
    data=load('laboratory_extended')
    assert len(data['mil']['series'])==10
    rows=[r for s in data['mil']['series'] for r in s['rows']]
    assert len(rows)==813
    assert sum(r['remanence_origin']=='laboratory' for r in rows)==1
    assert len(data['alh']['measurements'])==492
    assert len(data['alh']['specimens'])==12
    assert all(s['rows'][0]['relative_magnitude']==1 for s in data['mil']['series'])
    assert all(len(s['input_sha256'])==64 for s in data['mil']['series'])
    for key,file in [('pipeline_sha256','scripts/data/build_evidence.py'),('module_sha256','src/marswind/paleomagnetism.py')]:
        assert data[key]==hashlib.sha256((ROOT/file).read_bytes()).hexdigest()


def test_water_snapshot_is_presence_only_and_overlap_is_reproducible():
    data=load('water');atlas=load('atlas')
    assert len(data['products'])==10
    for p in data['products']:
        assert len(p['cells'])==len(set(map(tuple,p['cells'])))
        assert p['detected_pixels']>=len(p['cells'])
        assert all(0<=i<90 and 0<=j<180 for i,j in p['cells'])
    for result in data['overlap_diagnostic']:
        cells={tuple(c) for p in data['products'] if p['class']==result['class'] for c in p['cells']}
        assert len(cells)==result['occupied_cells']
        fields=[atlas['magnetic_nT']['150'][i][j] for i,j in cells]
        assert np.median(fields)==pytest.approx(result['field_median_nT'])
        assert result['field_min_nT']<=result['field_median_nT']<=result['field_max_nT']
    assert 'survey/exposure mask' in ' '.join(data['notes'])
    for key,file in [('pipeline_sha256','scripts/data/build_evidence.py'),('module_sha256','src/marswind/paleomagnetism.py'),('atlas_sha256','research/data/atlas.json')]:
        assert data[key]==hashlib.sha256((ROOT/file).read_bytes()).hexdigest()


def test_magic_table_separation_never_promotes_placeholder_coordinates():
    tables=magic_tables('tab delimited\tsites\nsite\tlat\tlon\na\t0\t0\n>>>>>>>>>>\ntab delimited\tmeasurements\nspecimen\tmagn_moment\na\t2e-11\n')
    assert tables['sites'][0]['lat']=='0'
    assert tables['measurements'][0]=={'specimen':'a','magn_moment':'2e-11'}
