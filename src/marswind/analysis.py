"""Scientific products with explicit coordinate and time conventions."""
import hashlib
from pathlib import Path
import numpy as np
from .mcd import sample
from .physics import area_mean, along_wind, vertical_shear, acoustic_modes


def local_hour(lon, lt, time_mode):
    return np.mod(lt + (np.asarray(lon)/15 if time_mode=='universal' else np.zeros_like(lon)),24)


def evaluate(z, lon, lat, ls=255, lt=12, time_mode='universal', azimuth=90):
    z,lon,lat,ls = np.broadcast_arrays(z,lon,lat,ls)
    hours=local_hour(lon,lt,time_mode)
    points=np.column_stack([z.ravel(),lon.ravel(),lat.ravel(),ls.ravel()%360,hours.ravel(),
                           np.ones(z.size),np.full(z.size,2)])
    fields,provenance=sample(points)
    f={k:v.reshape(z.shape) for k,v in fields.items()}
    f['speed']=np.hypot(f['u'],f['v'])
    f['sound_speed']=np.sqrt(f['gamma']*f['gas_constant']*f['temperature'])
    f['along_wind']=along_wind(f['u'],f['v'],azimuth)
    f['effective_speed']=f['sound_speed']+f['along_wind']
    provenance.update({'time_mode':time_mode,'hour_reference':float(lt),'azimuth_deg':float(azimuth),
                       'altitude_reference':'m above areoid; below-terrain samples masked',
                       'scenario':1,'scenario_label':'Climatology / average solar EUV'})
    provenance['pipeline_sha256']=hashlib.sha256(b''.join(
        p.read_bytes() for p in sorted(Path(__file__).parent.glob('*.py')))).hexdigest()
    return f,provenance


def map_product(altitude=60, ls=255, lt=12, time_mode='universal', azimuth=90):
    lon=np.arange(-177.5,180,5.)
    lat=np.arange(-87.5,90,5.)
    lon2,lat2=np.meshgrid(lon,lat)
    z=np.array([altitude*1000-1000,altitude*1000,altitude*1000+1000])[:,None,None]
    f,p=evaluate(z,lon2[None],lat2[None],ls,lt,time_mode,azimuth)
    shear=vertical_shear(f['u'],f['v'],z[:,0,0])[1]*1000 # m/s per km
    central={k:v[1] for k,v in f.items()}
    central['shear']=shear
    p.update({'Ls':ls%360,'altitude_km':altitude,'grid_spacing_deg':5,'shear_stencil_m':1000})
    return {'longitude':lon,'latitude':lat,'fields':central,'provenance':p,
            'stats':{'mean_speed':area_mean(central['speed'],lat),
                     'max_speed':float(np.nanmax(central['speed'])),
                     'mean_temperature':area_mean(central['temperature'],lat),
                     'valid_fraction':float(np.isfinite(central['speed']).mean())}}


def profile_product(lon=135.623,lat=4.502,ls=255,lt=12,time_mode='universal',azimuth=90,n=101):
    anchor,_=evaluate(60000,lon,lat,ls,lt,time_mode,azimuth)
    bottom=float(anchor['orography'])+100
    z=np.linspace(bottom,200000,n)
    f,p=evaluate(z,lon,lat,ls,lt,time_mode,azimuth)
    f['shear']=vertical_shear(f['u'],f['v'],z)*1000
    p.update({'longitude':lon,'latitude':lat,'Ls':ls%360,'vertical_samples':n})
    return {'altitude_km':z/1000,'fields':f,'provenance':p}


def section_product(lon=135.623,ls=255,lt=12,time_mode='universal',azimuth=90):
    lat=np.arange(-87.5,90,5.)
    z=np.linspace(1000,200000,51)
    f,p=evaluate(z[:,None],lon,lat[None,:],ls,lt,time_mode,azimuth)
    f['shear']=vertical_shear(f['u'],f['v'],z)*1000
    p.update({'longitude':lon,'Ls':ls%360})
    return {'latitude':lat,'altitude_km':z/1000,'fields':f,'provenance':p}


def seasonal_product(lon=135.623,lat=4.502,altitude=60,lt=12,time_mode='universal',azimuth=90):
    ls=np.arange(0,361,15.)
    f,p=evaluate(altitude*1000,lon,lat,ls,lt,time_mode,azimuth)
    p.update({'longitude':lon,'latitude':lat,'altitude_km':altitude})
    return {'Ls':ls,'fields':f,'provenance':p}


def modal_product(lon=135.623,lat=4.502,ls=255,lt=12,time_mode='universal',azimuth=90,degree=500):
    fine=profile_product(lon,lat,ls,lt,time_mode,azimuth,n=201)
    f=fine['fields']; z=fine['altitude_km']*1000
    result=acoustic_modes(z,f['density'],f['sound_speed'],f['along_wind'],degree)
    coarse=acoustic_modes(z[::2],f['density'][::2],f['sound_speed'][::2],f['along_wind'][::2],degree)
    result['grid_difference_pct']=100*abs(result['frequency_mhz']-coarse['frequency_mhz'])/result['frequency_mhz']
    result['altitude_km']=z/1000
    result['provenance']=fine['provenance']
    result['provenance'].update({'horizontal_degree':degree,'horizontal_reference_radius_m':3389500.,
                                'modal_model':'scalar pressure P1, lumped mass, rigid endpoints',
                                'fine_nodes':201,'coarse_nodes':101,'top_altitude_areoid_km':200})
    result['assumptions']='Experimental scalar pressure column; rigid top and bottom, no buoyancy, loss or solid coupling. Diagonal first-order advection only. Not the normal modes of the internship report.'
    return result
