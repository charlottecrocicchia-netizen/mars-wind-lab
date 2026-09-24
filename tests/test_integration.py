import io
import json
from pathlib import Path
import numpy as np
import pytest
import xarray as xr
from fastapi.testclient import TestClient
from marswind.mcd import ROOT, sample
from marswind.analysis import map_product,profile_product,modal_product
from marswind.server import app

pytestmark=[pytest.mark.integration,pytest.mark.skipif(not (ROOT/'build/sample_mcd').exists(),reason='Local MCD adapter missing')]


def test_official_sampler_periodicity_and_equation_of_state():
    points=[[60000,135.623,4.502,ls,12,1,2] for ls in [0,360]]
    f,p=sample(points)
    np.testing.assert_allclose(f['u'][0],f['u'][1],atol=1e-5)
    np.testing.assert_allclose(f['pressure'],f['density']*f['gas_constant']*f['temperature'],rtol=.02)
    assert len(p['source_sha256'])==64


def test_terrain_mask_and_vertical_profile():
    # Olympus area is higher than 1 km above areoid.
    f,_=sample([[1000,-133,18,255,12,1,2]])
    assert np.isnan(f['u'][0])
    p=profile_product()
    assert p['fields']['altitude_agl'][0]==pytest.approx(100,abs=1)
    assert np.isfinite(p['fields']['u']).all()
    assert np.all(p['fields']['density']>0)
    assert np.all(p['fields']['u_rms']>=0)


def test_map_and_local_solar_conventions_differ():
    m=map_product()
    local=map_product(time_mode='local')
    assert m['fields']['u'].shape==(36,72)
    assert not np.allclose(m['fields']['u'],local['fields']['u'])
    assert np.allclose(local['fields']['local_time'],12)
    assert 0<m['stats']['mean_speed']<m['stats']['max_speed']
    np.testing.assert_allclose(m['fields']['speed'],np.hypot(m['fields']['u'],m['fields']['v']))


def test_http_products_validation_and_portable_exports():
    client=TestClient(app)
    for endpoint in ['/','/api/health','/api/map','/api/profile','/api/section','/api/seasonal','/api/modes']:
        response=client.get(endpoint)
        assert response.status_code==200,(endpoint,response.text[:500])
    for params in [{'altitude':-5},{'lat':100},{'time_mode':'ambiguous'},{'ls':361},{'format':'exe'}]:
        assert client.get('/api/map',params=params).status_code==422
    response=client.get('/api/export',params={'format':'nc'})
    assert response.status_code==200
    with xr.open_dataset(io.BytesIO(response.content),engine='scipy') as ds:
        assert ds.u.attrs['units']=='m s-1'
        assert ds.sizes['longitude']==72
        assert json.loads(ds.attrs['provenance_json'])['Ls']==255
    csv=client.get('/api/export',params={'format':'csv'})
    assert csv.text.startswith('# {') and 'u [m s-1]' in csv.text
    png=client.get('/api/export',params={'format':'png'})
    assert png.content.startswith(b'\x89PNG\r\n\x1a\n')
    assert len(png.content)>10000


def test_archived_modes_preserve_surface_and_normalization_diagnostics():
    from marswind.legacy import DEFAULT,load_archived_modes
    if not DEFAULT.is_dir():pytest.skip('Legacy eigenfunctions absent')
    result=load_archived_modes()
    assert result['surface_radius_km']==3383
    assert len(result['modes'])==10
    assert len(result['provenance']['files'])==40
    for m in result['modes']:
        assert m['altitude_km'][0]==0
        assert m['altitude_km'][-1]==200
        assert 0<=m['lower_10km_fraction_of_atmosphere']<=1
        assert m['normalization_integral_ratio']>1
        assert np.max(m['U']['magnitude'])==pytest.approx(1)


def test_official_distributed_k9_reference():
    # Independent bundled reference: mcd/testcase/REF_OUTPUT_K9.
    # Its Earth timestamp is converted here using the rounded Ls/LT printed
    # by the official reference (97.9 deg / 7.47 h), so tolerance is 0.5%.
    f,_=sample([[150000,5,15,97.9,7.47,1,2]])
    expected={'pressure':4.79e-6,'density':1.21e-10,'temperature':193.,
              'u':-306.,'v':-79.9,'w':-.641,'gamma':1.36,'gas_constant':205.}
    for name,value in expected.items():
        assert f[name][0]==pytest.approx(value,rel=.005)
