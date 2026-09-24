"""Physical invariants, scientific missing data, and the published snapshot."""
import json
import hashlib
from pathlib import Path
import numpy as np
import pytest
from fastapi.testclient import TestClient
from marswind.observations import temperature_at_depth,threshold_depth,depth_quality,weighted_mean,hemisphere_contrast
from marswind import server
ROOT=Path(__file__).resolve().parents[1]


def test_temperature_uses_local_surface_and_never_extrapolates():
    # A 10 K/km linear gradient, with an arbitrary planetary reference radius.
    r=np.array([3300,3350,3400.]);t=220+10*(3400-r)
    np.testing.assert_allclose(temperature_at_depth(r,t,[0,10,100]),[220,320,1220])
    np.testing.assert_allclose(temperature_at_depth(r-6,t,[0,10,100]),[220,320,1220])
    assert np.isnan(temperature_at_depth(r,t,-1))
    assert np.isnan(temperature_at_depth(r,t,101))
    assert threshold_depth(r,t,853.15)==pytest.approx(63.315)
    assert threshold_depth(r,t,1300) is None


def test_depth_flags_preserve_negative_and_missing_estimates():
    b=np.array([-2.,10,25,8]);lo=np.array([-10.,-1e100,20,9]);hi=np.array([15.,-1e100,40,20])
    bounded,usable=depth_quality(b,lo,hi)
    assert bounded.tolist()==[True,False,True,False]
    assert usable.tolist()==[False,False,True,False]
    assert b[0]==-2 and lo[1]==-1e100


def test_spherical_area_weighting_and_symmetric_control():
    lat=np.arange(-89.75,90,.5);field=np.broadcast_to(np.sin(np.deg2rad(lat))[:,None]**2,(len(lat),720))
    assert weighted_mean(field,lat,np.ones_like(field,dtype=bool))==pytest.approx(1/3,abs=4e-6)
    for cut in [0,20]:assert hemisphere_contrast(field,lat,cut)['south_north_ratio']==pytest.approx(1)


def test_shtools_axial_dipole_normalization_and_upward_continuation():
    sh=pytest.importorskip('pyshtools')
    coeff=np.zeros((2,2,2));coeff[0,1,0]=100
    model=sh.SHMagCoeffs.from_array(coeff,r0=3393500,normalization='schmidt',csphase=1,units='nT')
    lat=np.array([0.,30.,60.]);lon=np.array([0.,45.,200.])
    base=np.linalg.norm(model.expand(lat=lat,lon=lon,r=np.full(3,3393500.)),axis=1)
    np.testing.assert_allclose(base,100*np.sqrt(1+3*np.sin(np.deg2rad(lat))**2),rtol=1e-12)
    higher=np.linalg.norm(model.expand(lat=lat,lon=lon,r=np.full(3,3793500.)),axis=1)
    np.testing.assert_allclose(higher/base,(3393500/3793500)**3,rtol=1e-12)


def test_observation_snapshot_is_consistent_and_has_no_unphysical_missing_values():
    load=lambda name:json.loads((ROOT/f'research/data/{name}.json').read_text())
    r=load('results');a=load('atlas');d=load('depths');m=load('meteorites');lab=load('laboratory')
    shape=(len(a['latitude']),len(a['longitude']))
    assert shape==(90,180)
    for grid in [a['topography_km'],*a['magnetic_nT'].values(),*a['crust_km'].values(),a['geology']['grid']]:assert np.shape(grid)==shape
    assert a['geology']['features']==1311 and len(a['geology']['units'])==44
    assert r['depth_quality']['usable']==sum(p['usable'] for p in d)
    for key,file in [('pipeline_sha256','scripts/data/build.py'),('observations_module_sha256','src/marswind/observations.py'),('input_manifest_sha256','research/data/manifest.json')]:
        assert r[key]==hashlib.sha256((ROOT/file).read_bytes()).hexdigest()
    assert len(m['samples'])==r['counts']['meteorites']
    assert len(lab['measurements'])==1073 and len(lab['specimens'])==11
    assert any(p['negative_best_fit'] and p['depth_km']<0 for p in d)
    assert all(p['lower_km'] is None and p['upper_km'] is None for p in d if not p['interval_available'])
    assert all(0<=p['lon']<360 and -90<=p['lat']<=90 for p in m['craters'])
    assert next(c for c in m['craters'] if c['name']=='Karratha')['lat']==-15.7
    assert all(c['status']!='Confirmed' for c in m['craters'])
    assert 'CC BY-NC' in m['license']
    assert 'locations' not in a  # Earth find locations must not become Mars coordinates.


def test_all_workspaces_and_derived_products_work_without_mcd(monkeypatch):
    def unavailable():raise RuntimeError('MCD unavailable')
    monkeypatch.setattr(server,'installation',unavailable)
    client=TestClient(server.app)
    for route in ['/','/atmosphere','/research/hypotheses','/research/data','/research/tests','/research/library']:
        r=client.get(route);assert r.status_code==200
        assert 'lang="en"' in r.text
    for name in ['atlas','meteorites','depths','thermal','results','laboratory','manifest','laboratory_extended','paleomagnetism','water']:
        assert client.get('/research/files/data/'+name+'.json').status_code==200
