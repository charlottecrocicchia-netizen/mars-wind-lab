"""Analytic geometry, selection effects and provenance for the regional pilot."""
from pathlib import Path
import hashlib
import json

import numpy as np
import pytest
from fastapi.testclient import TestClient
from marswind.pilot import distance_bearing, destination, sample_mola, morphology, contrast
from marswind import server

ROOT=Path(__file__).resolve().parents[1]


def test_great_circle_geometry_wraps_and_roundtrips():
    lat,lon=destination(-30,359,np.array([10,500,1000]),np.array([0,90,235]))
    distance,bearing=distance_bearing(lat,lon,-30,359)
    np.testing.assert_allclose(distance,[10,500,1000],atol=1e-9)
    np.testing.assert_allclose(bearing,[0,90,235],atol=1e-9)
    assert distance_bearing(0,1,0,359)[0]==pytest.approx(3393.5*np.deg2rad(2))
    assert distance_bearing(0,360,0,0)[0]==pytest.approx(0,abs=1e-10)


def test_mola_pixel_centers_linear_latitude_and_periodic_seam():
    lat=89.875-np.arange(720)*.25
    lon=.125+np.arange(1440)*.25
    grid=np.broadcast_to(lat[:,None]*1000,(720,1440))
    np.testing.assert_allclose(sample_mola(grid,[45.1,-30,0],[359.99,0,360]),[45.1,-30,0],atol=1e-12)
    periodic=np.broadcast_to(1000*np.cos(np.deg2rad(lon)),(720,1440))
    a=sample_mola(periodic,[0,0,0],[-.01,359.99,719.99])
    np.testing.assert_allclose(a,a[0],atol=1e-12)
    assert a[0]==pytest.approx(1,abs=5e-6)
    with pytest.raises(ValueError):sample_mola(grid,90,0)


def test_radial_depth_on_a_known_bowl_and_vertical_datum_shift():
    lon,lat=np.meshgrid(.125+np.arange(1440)*.25,89.875-np.arange(720)*.25)
    d,_=distance_bearing(lat,lon,0,180)
    # A 2 km bowl, radius 300 km. Rim and exterior are at zero.
    grid=-2000*np.maximum(0,1-(d/300)**2)
    p=morphology(grid,0,180,600)
    assert p['depth_km']==pytest.approx(2,abs=.005)
    assert p['depth_diameter']==pytest.approx(2/600,abs=1e-5)
    shifted=morphology(grid+6000,0,180,600)
    assert shifted['depth_km']==pytest.approx(p['depth_km'],abs=1e-12)


def test_geologic_composition_can_reverse_a_descriptive_contrast():
    values=np.array([100,100,100,10,110,20,20,20.])
    units=np.array([0,0,0,1,0,1,1,1])
    inside=np.arange(8)<4;outside=~inside
    result=contrast(values,np.ones(8),inside,outside,units)
    assert result['ratio']==pytest.approx(77.5/42.5)
    assert result['matched_ratio']==pytest.approx(77.5/87.5)
    assert result['ratio']>1>result['matched_ratio']
    assert result['common_support_fraction']==1


def test_unmatched_terrain_is_excluded_and_never_imputed():
    values=np.array([5.,100,10,20]);inside=np.array([True,True,False,False]);outside=~inside
    result=contrast(values,np.ones(4),inside,outside,np.array([0,1,0,2]))
    assert result['common_support_fraction']==.5
    assert result['matched_ratio']==.5  # the 100-valued unmatched unit is excluded
    missing=contrast(values,np.ones(4),inside,outside,np.array([0,0,1,1]))
    assert missing['matched_ratio'] is None and missing['common_support_fraction']==0
    empty=contrast(values,np.ones(4),inside,np.zeros(4,dtype=bool))
    assert empty['ratio'] is None


def test_saved_pilot_provenance_and_scientific_accounting():
    data=json.loads((ROOT/'research/pilot/results.json').read_text())
    assert len(data['cases'])==5
    for file,digest in data['provenance'].items():
        if file.startswith('data/'):continue  # raw archives are deliberately not in CI
        assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest,file
    primary=[c for c in data['cases'] if c['site']['role']=='Primary crater case']
    assert len(primary)==4
    assert len({c['site']['region'] for c in primary})==3  # not four independent regions
    assert next(c for c in data['cases'] if c['site']['id']=='ladon')['site']['catalog_status']=='Misidentified'
    for c in data['cases']:
        assert len(c['sensitivity'])==81
        assert len(c['sector_omission'])==8
        shape=(len(c['map']['lat']),len(c['map']['lon']))
        for v in c['map']['field_nT'].values():assert np.shape(v)==shape
        assert np.all(np.diff(c['map']['lon'])>0)  # no seam inside regional raster axes
        for b in c['baseline'].values():
            assert 0<=b['common_support_fraction']<=1
            assert b['ratio']==pytest.approx(b['inside_nT']/b['outside_nT'],abs=1e-7)
            w=np.array([s['inside_weight'] for s in b['strata']])
            a=np.array([s['inside_nT'] for s in b['strata']]);z=np.array([s['outside_nT'] for s in b['strata']])
            assert b['matched_ratio']==pytest.approx((w*a).sum()/(w*z).sum(),rel=1e-6)
        assert c['summary']['ratio_min']<=c['baseline']['150']['ratio']<=c['summary']['ratio_max']
    assert max(v['absolute_error_nT'] for v in data['numerical_checks'])<.00051
    assert 'posterior' not in data and 'p_value' not in data


def test_pilot_navigation_and_downloads_without_atmospheric_installation(monkeypatch):
    def unavailable():raise RuntimeError('No MCD installation')
    monkeypatch.setattr(server,'installation',unavailable)
    client=TestClient(server.app)
    for page in ['', '/regions','/hypotheses','/method','/results']:
        response=client.get('/research/pilot'+page)
        assert response.status_code==200
        assert 'lang="en"' in response.text and 'Study chapters' in response.text
    for file in ['results.json','protocol.json','sources.json','contrasts.csv','regional_pilot.png','regional_pilot.svg']:
        assert client.get('/research/files/pilot/'+file).status_code==200
    assert client.get('/research/pilot/not-a-page').status_code==422
