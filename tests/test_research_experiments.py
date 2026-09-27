"""Independent analytic checks and safeguards for the new research diagnostics."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import quad

from marswind.recording import (last_downward_crossings, record, cylinder_axis_operator,
    temporal_gain, harmonic_attenuation, detection_power, field_at, recording_intervals,
    record_intervals, interval_field_mean, interval_temporal_gain)
from marswind.research_checks import (ridge_predict, longitude_folds, vector_from_direction,
    fit_demagnetization, line_sensitivity, axis_angle)

ROOT=Path(__file__).resolve().parents[1]


def test_last_crossings_track_reheating_without_inventing_an_initial_record():
    t=[0,1,2,2,3,4];temp=[600,400,200,700,400,200]
    cross,state=last_downward_crossings(t,temp,[100,300,500,800])
    np.testing.assert_array_equal(state,[2,1,1,0])
    np.testing.assert_allclose(cross[1:3],[3.5,2+2/3])
    signed,unknown,hot=record(cross[None,:],state[None,:],'steady')
    np.testing.assert_allclose([signed[0],unknown[0],hot[0]],[.5,.25,.25])
    np.testing.assert_allclose(record(cross[None,:],state[None,:],'absent')[0],0)


def test_linear_cooling_matches_a_boxcar_kernel_and_balanced_polarities():
    n=4096; thresholds=500-(np.arange(n)+.5)/n*200
    crossing,state=last_downward_crossings([0,10],[500,300],thresholds)
    np.testing.assert_allclose(crossing,(np.arange(n)+.5)/n*10,atol=1e-12)
    # Exactly two 5 Myr opposite-polarity intervals cancel when integrated.
    assert abs(record(crossing[None,:],state[None,:],'periodic',chron_myr=5)[0][0])<1e-12
    periods=np.array([3.,7.,10.,20.,100.])
    gain=temporal_gain(crossing,np.ones(n),periods)
    np.testing.assert_allclose(gain,abs(np.sinc(10/periods)),atol=2e-7)
    np.testing.assert_allclose(temporal_gain([3],[1],[1,2,8]),1,atol=1e-14)


def test_shutdown_and_poisson_histories_do_not_infer_activity_between_samples():
    np.testing.assert_array_equal(field_at([0,499,500,900],'shutdown'),[1,1,0,0])
    t=np.linspace(0,4000,1000)
    np.testing.assert_array_equal(field_at(t,'poisson',seed=42),field_at(t,'poisson',seed=42))
    assert set(field_at(t,'poisson',seed=42))=={-1.,1.}


def test_cylinder_axis_field_matches_independent_ring_integral_and_layer_additivity():
    radius=150.;height=40.;top=20.;bottom=30.
    # Integrate the field of horizontal surface magnetic-charge rings directly.
    def surface(distance):
        return quad(lambda r:distance*r/(distance*distance+r*r)**1.5,0,radius,epsabs=1e-12)[0]
    exact=2*np.pi*1e-7*1e9*(surface(height+top)-surface(height+bottom))
    operator=cylinder_axis_operator(radius,[top],[bottom],[height])[0,0]
    assert operator==pytest.approx(exact,rel=1e-11)
    split=cylinder_axis_operator(radius,[20,25],[25,30],[height]).sum()
    assert split==pytest.approx(operator,rel=1e-12)
    distant=cylinder_axis_operator(1,[0],[.1],[1000])[0,0]
    dipole=4e-7*np.pi*1e9*1**2*.1/(2*1000.05**3)
    assert distant==pytest.approx(dipole,rel=1e-4)
    assert cylinder_axis_operator(1e9,[20],[30],[height])[0,0]<1e-4


def test_single_degree_transfer_and_gaussian_false_alarm_limit():
    np.testing.assert_allclose(harmonic_attenuation([1,2,3],100,100),[1/8,1/16,1/32])
    assert detection_power(0,.01)==pytest.approx(.01,abs=1e-14)
    assert detection_power(10)>.99999


def test_spatial_folds_are_complete_disjoint_and_buffered_across_the_seam():
    longitude=np.arange(1,360,2.)
    for offset in [0,30]:
        seen=np.zeros(len(longitude),int)
        for train,test in longitude_folds(longitude,6,10,offset):
            seen+=test
            assert not np.any(train&test)
            distance=abs((longitude[train,None]-longitude[None,test]+180)%360-180)
            assert distance.min()>=10
        np.testing.assert_array_equal(seen,1)


def test_ridge_scaling_is_train_only_and_constant_features_are_ignored():
    x=np.array([[0,3],[1,3],[2,3],[3,3.]])
    pred=ridge_predict(x,np.array([1.,3,5,7]),np.ones(4),[[4,9],[100,400]],alpha=1e-8)
    np.testing.assert_allclose(pred,[9,201],rtol=1e-7)
    assert ridge_predict(x,[1,3,5,7],[1,1,1,1],[[4,9]],alpha=1e-8)[0]==pytest.approx(pred[0])
    np.testing.assert_allclose(ridge_predict(x[:,:0],[1,3,5,7],[1,1,1,1],np.empty((3,0))),4)


def test_pca_recovers_a_known_line_and_exposes_forced_origin_bias():
    axis=np.array([1.,2,3]);axis/=np.linalg.norm(axis)
    offset=np.array([2.,-1,0])
    vectors=np.linspace(5,1,12)[:,None]*axis+offset
    fit=fit_demagnetization(vectors)
    assert axis_angle(fit['axis'],axis)<1e-5
    assert fit['mad_deg']<1e-10
    sensitivity=line_sensitivity(vectors)
    assert sensitivity['anchored_axis_difference_deg']>20
    assert sensitivity['leave_one_treatment_out_max_axis_change_deg']<1e-5
    rotated=vectors@np.array([[0,-1,0],[1,0,0],[0,0,1.]])
    assert fit_demagnetization(rotated)['mad_deg']<1e-10
    with pytest.raises(ValueError):fit_demagnetization(np.ones((5,3)))
    np.testing.assert_allclose(vector_from_direction([0,90],[0,0],[1,1]),[[1,0,0],[0,1,0]],atol=1e-14)


def test_committed_experiment_outputs_match_their_provenance():
    manifest=json.loads((ROOT/'research/experiments/manifest.json').read_text())
    for name,digest in manifest['input_and_code_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    for name,digest in manifest['output_sha256'].items():
        assert hashlib.sha256((ROOT/'research/experiments'/name).read_bytes()).hexdigest()==digest,name
    lab=json.loads((ROOT/'research/experiments/laboratory.json').read_text())
    assert all(r['component_age_ma'] is None for r in lab['candidate_fits'])
    assert any(r['eligible_natural_measurements']==0 for r in lab['inventory'])


def test_exact_recording_kernel_matches_analytic_boxcar_without_quadrature_aliasing():
    kernel=recording_intervals([0,10],[500,300],[300,500])
    assert kernel['weight'].sum()==pytest.approx(1)
    for phase in [0,.1,.77,1.91]:
        assert record_intervals([kernel],'periodic',chron_myr=1,phase=phase)[0]==pytest.approx(0,abs=1e-12)
    periods=np.array([.07,.5,3,7,10,20,100.])
    np.testing.assert_allclose(interval_temporal_gain([kernel],[1],periods),abs(np.sinc(10/periods)),atol=1e-14)
    hot=recording_intervals([0,1],[100,700],[200,600]);assert hot['hot']==1
    unknown=recording_intervals([0,1],[100,90],[200,600]);assert unknown['unknown']==1
    reheated=recording_intervals([0,1,2,2,3,4],[600,400,200,700,400,200],[300,500])
    assert reheated['weight'].sum()==pytest.approx(1)
    assert record_intervals([reheated],'shutdown',shutdown_myr=2)[0]==0
    # Piecewise-constant averages agree with independent fine midpoint sampling.
    times=(np.arange(100000)+.5)/100000*31.3
    for kind in ['periodic','poisson','shutdown','intermittent']:
        actual=interval_field_mean([0],[31.3],kind,chron_myr=3.7,phase=.37,seed=23,shutdown_myr=12.3)[0]
        sampled=field_at(times,kind,chron_myr=3.7,phase=.37,seed=23,shutdown_myr=12.3).mean()
        assert abs(actual-sampled)<2e-4
