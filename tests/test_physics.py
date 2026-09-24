import numpy as np
import pytest
from marswind.physics import sound_speed, along_wind, vertical_shear, area_mean, latitude_weights, acoustic_modes
from marswind.analysis import local_hour


def test_sound_speed_and_invalid_state():
    assert sound_speed(200,1.3,190)==pytest.approx(np.sqrt(49400))
    with pytest.raises(ValueError):sound_speed(-1,1.3,190)


def test_bearings_are_towards_not_meteorological_from():
    assert along_wind(20,30,0)==pytest.approx(30)
    assert along_wind(20,30,90)==pytest.approx(20)
    assert along_wind(20,30,180)==pytest.approx(-30)
    assert along_wind(20,30,270)==pytest.approx(-20)


def test_nonuniform_vertical_grid_and_si_shear():
    z=np.array([0.,100.,700.,2000.])
    shear=vertical_shear(.003*z,-.004*z,z)
    np.testing.assert_allclose(shear,.005,rtol=1e-12)
    with pytest.raises(ValueError):vertical_shear(z,z,z[::-1])


def test_spherical_area_mean_not_arithmetic_mean():
    lat=np.arange(-89.5,90,1.)
    field=np.broadcast_to(np.sin(np.deg2rad(lat))[:,None]**2,(180,360)).copy()
    assert latitude_weights(lat).sum()==pytest.approx(2.)
    assert area_mean(field,lat)==pytest.approx(1/3,abs=3e-5)
    assert abs(field.mean()-area_mean(field,lat))>.1
    field[:20]=np.nan
    assert np.isfinite(area_mean(field,lat))
    assert area_mean(np.full_like(field,np.nan),lat)!=area_mean(np.full_like(field,np.nan),lat)


def test_synoptic_and_local_time_wrap():
    np.testing.assert_allclose(local_hour(np.array([-180.,0.,180.]),18,'universal'),[6,18,6])
    np.testing.assert_allclose(local_hour(np.array([-180.,0.,180.]),18,'local'),[18,18,18])


def test_rigid_column_matches_analytic_frequencies():
    z=np.linspace(0,100000,401);rho=np.ones_like(z);c=np.full_like(z,240.)
    m=acoustic_modes(z,rho,c,z*0,horizontal_degree=150)
    k=m['k_rad_m'];analytic=240*np.sqrt(k*k+(np.arange(6)*np.pi/100000)**2)/(2*np.pi)*1000
    np.testing.assert_allclose(m['frequency_mhz'],analytic,rtol=8e-5)
    np.testing.assert_allclose(m['weights'].sum(axis=1),1,atol=1e-12)


def test_uniform_advection_gives_full_doppler_shift_not_half():
    z=np.linspace(0,150000,201);ones=np.ones_like(z)
    m=acoustic_modes(z,ones,250*ones,30*ones)
    np.testing.assert_allclose(m['effective_wind'],30,rtol=1e-12)
    np.testing.assert_allclose(m['delta_frequency_mhz'],m['k_rad_m']*30/(2*np.pi)*1000,rtol=1e-12)
    zero=acoustic_modes(z,ones,250*ones,0*ones)
    np.testing.assert_array_equal(zero['delta_frequency_mhz'],0)


def test_grid_refinement_reduces_error():
    errors=[]
    for n in [41,81,161]:
        z=np.linspace(0,100000,n);ones=np.ones(n)
        m=acoustic_modes(z,ones,240*ones,0*ones)
        exact=240*np.sqrt(m['k_rad_m']**2+(5*np.pi/100000)**2)/(2*np.pi)*1000
        errors.append(abs(m['frequency_mhz'][5]-exact))
    assert errors[2]<errors[1]/3<errors[0]/9
