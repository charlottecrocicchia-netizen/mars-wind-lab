"""Physical controls and movie invariants, using independent small map fixtures."""
import numpy as np
import pytest
from marswind import motion


@pytest.fixture
def sampler(monkeypatch):
    calls=[]
    def fake_map(**p):
        calls.append(p.copy())
        u=np.full((2,3),p['ls']-180.);u[0,0]=np.nan
        v=np.full((2,3),p['altitude']/2)
        fields={'u':u,'v':v,'speed':np.hypot(u,v),'temperature':200+v,'local_time':np.full((2,3),p['lt'])}
        return {'longitude':np.array([-120.,0.,120.]),'latitude':np.array([-45.,45.]),'fields':fields,
                'stats':{'mean_speed':float(np.nanmean(fields['speed'])),'max_speed':float(np.nanmax(fields['speed'])),'mean_temperature':float(np.mean(fields['temperature'])),'valid_fraction':5/6},
                'provenance':{'altitude_km':p['altitude'],'Ls':p['ls'],'time_mode':p['time_mode'],'hour_reference':p['lt']}}
    monkeypatch.setattr(motion,'map_product',fake_map)
    return calls


def test_season_sweep_holds_height_hour_and_azimuth_fixed(sampler):
    result=motion.sequence_product(axis='season',field='u',altitude=70,ls=45,lt=7.5,time_mode='local',azimuth=270)
    assert len(result['frames'])==24
    assert result['values'].tolist()==list(range(0,360,15))
    assert all((p['altitude'],p['lt'],p['time_mode'],p['azimuth'])==(70,7.5,'local',270) for p in sampler)
    assert result['scale']['min']==-180 and result['scale']['max']==180
    assert all(np.isnan(f['fields']['u'][0,0]) for f in result['frames'])
    assert 'local_time' in result['frames'][0]['fields']


def test_altitude_sweep_has_one_scale_and_holds_season_fixed(sampler):
    result=motion.sequence_product(axis='altitude',field='speed',ls=210,lt=15)
    assert result['values'].tolist()==list(range(10,201,10))
    assert all((p['ls'],p['lt'])==(210,15) for p in sampler)
    assert result['scale']['min']==0
    assert result['scale']['max']==pytest.approx(np.hypot(30,100))
    for frame in result['frames']:
        values=frame['fields']['speed']
        assert np.nanmax(values)<=result['scale']['max']
        assert frame['provenance']['altitude_km']==frame['value']


def test_movie_is_decodable_and_preserves_frame_count(sampler,tmp_path):
    import imageio_ffmpeg
    sequence=motion.sequence_product(axis='altitude',field='speed')
    data=motion.movie_bytes(sequence,fps=4)
    assert data[4:8]==b'ftyp' and len(data)>10000
    path=tmp_path/'test.mp4';path.write_bytes(data)
    reader=imageio_ffmpeg.read_frames(str(path));metadata=next(reader)
    assert metadata['size']==(1280,720) and metadata['fps']==4
    assert sum(1 for _ in reader)==20
    with pytest.raises(ValueError):motion.movie_bytes(sequence,fps=3)


def test_stream_reports_each_frame_before_complete_payload(sampler):
    events=list(motion.sequence_events(axis='altitude',field='speed'))
    assert [event['completed'] for event in events[:-1]]==list(range(21))
    assert all(event['total']==20 for event in events[:-1])
    assert events[-1]['event']=='complete'
    assert len(events[-1]['sequence']['frames'])==20


def test_sequence_surfaces_model_errors(monkeypatch):
    def failed(**p):raise RuntimeError('Test model unavailable')
    monkeypatch.setattr(motion,'map_product',failed)
    events=motion.sequence_events(axis='altitude',field='speed')
    assert next(events)['event']=='progress'
    with pytest.raises(RuntimeError,match='Test model unavailable'):
        next(events)
