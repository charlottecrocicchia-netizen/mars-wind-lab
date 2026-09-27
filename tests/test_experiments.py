import numpy as np
import pytest
from marswind.experiments import compare_columns
from marswind.mcd import ROOT


def column(z,c=200.,wind=30.,height=10.):
    return {'sound_speed':np.full_like(z,c),'along_wind':np.full_like(z,wind),'density':np.exp(-z/height)}


def test_opposite_direction_and_no_wind_control():
    z=np.linspace(20,160,141);a=column(z)
    f=compare_columns(z,a,a,100)['fields']
    np.testing.assert_allclose(f['effective_speed'],230)
    np.testing.assert_allclose(f['opposite_effective_speed'],170)
    np.testing.assert_allclose(f['wind_effect_pct'],15)
    b=column(z,wind=-30)
    g=compare_columns(z,b,b,100)['fields']
    np.testing.assert_allclose(g['effective_speed'],f['opposite_effective_speed'])
    calm=column(z,wind=0)
    np.testing.assert_array_equal(compare_columns(z,calm,calm,100)['fields']['wind_effect_pct'],0)


def test_seasonal_compensation_and_identity():
    z=np.linspace(20,160,141);a=column(z);b=column(z,c=220,wind=10)
    f=compare_columns(z,a,b,100)['fields']
    np.testing.assert_allclose(f['season_wind_delta'],-20)
    np.testing.assert_allclose(f['season_thermodynamic_delta'],20)
    np.testing.assert_array_equal(f['season_total_delta'],0)
    np.testing.assert_allclose(f['comparison_effective_speed']-f['effective_speed'],f['season_total_delta'])
    same=compare_columns(z,a,a,100)
    np.testing.assert_array_equal(same['fields']['season_thermodynamic_delta'],0)


def test_exponential_atmosphere_and_period_scaling():
    z=np.array([20.,21.,24.,30.,40.,60.]);a=column(z,height=10)
    f=compare_columns(z,a,a,100)['fields'];g=compare_columns(z,a,a,10)['fields']
    np.testing.assert_allclose(f['density_scale_km'],10,rtol=1e-12)
    np.testing.assert_allclose(f['reference_wavelength_km'],20,rtol=1e-12)
    np.testing.assert_allclose(f['wavelength_density_scale_ratio'],2,rtol=1e-12)
    np.testing.assert_allclose(g['wavelength_density_scale_ratio'],.2,rtol=1e-12)


def test_density_derivative_never_bridges_a_missing_block():
    z=np.arange(10.,dtype=float);a=column(z);a['density'][3:6]=np.nan;a['density'][6:]*=100
    r=compare_columns(z,a,a,100);f=r['fields']
    assert r['valid_samples']==7
    assert np.isnan(f['wavelength_density_scale_ratio'][3:6]).all()
    np.testing.assert_allclose(f['wavelength_density_scale_ratio'][[0,1,2,6,7,8,9]],2,rtol=1e-12)


@pytest.mark.parametrize('z,period',[(np.array([0.,1.,1.]),100),(np.array([0.,1.,2.]),0),(np.array([0.,np.nan,2.]),100),(np.array([0.,1.,2.]),float('nan'))])
def test_invalid_grids_or_periods(z,period):
    with pytest.raises(ValueError):compare_columns(z,column(z),column(z),period)


@pytest.mark.integration
@pytest.mark.skipif(not (ROOT/'build/sample_mcd').exists(),reason='Local MCD adapter missing')
def test_experiment_on_real_columns_and_downloadable_note():
    from marswind.experiments import experiment_product, study_note
    result=experiment_product(compare_ls=255);f=result['fields']
    assert len(result['altitude_km'])==141 and result['valid_samples']==141
    np.testing.assert_allclose(f['season_total_delta'],0,atol=1e-12)
    assert result['context']['local_solar_hour']==12
    opposite=experiment_product(azimuth=270)
    np.testing.assert_allclose(opposite['fields']['effective_speed'],f['opposite_effective_speed'],atol=1e-10)
    for question in ['direction','season','scale']:
        note=study_note(experiment_product(lt=15),question)
        assert 'Local solar time: 15.0 h' in note
        assert 'pipeline' in note and 'Limitations' in note
