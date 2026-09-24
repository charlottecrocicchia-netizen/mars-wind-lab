"""Portable, labelled model outputs and static scientific figures."""
import io
import json
import numpy as np
import xarray as xr
from .mcd import UNITS
UNITS={**UNITS,'speed':'m s-1','sound_speed':'m s-1','along_wind':'m s-1','effective_speed':'m s-1','shear':'m s-1 km-1'}
LABELS={'speed':'Horizontal speed','u':'Zonal wind (eastward)','v':'Meridional wind (northward)',
        'w':'Vertical wind (upward)','temperature':'Temperature','effective_speed':'Effective sound speed',
        'shear':'Vertical shear horizontal','sound_speed':'Vitesse du son'}


def dataset(product):
    ds=xr.Dataset({k:(('latitude','longitude'),v,{'units':UNITS.get(k,'1')}) for k,v in product['fields'].items()},
       coords={'latitude':('latitude',product['latitude'],{'units':'degrees_north'}),
               'longitude':('longitude',product['longitude'],{'units':'degrees_east'})},
       attrs={'title':'Mars Wind Lab | MCD 6.1 sampled climatology','Conventions':'CF-1.10',
              'provenance_json':json.dumps(product['provenance'],ensure_ascii=False),
              'altitude_km_above_areoid':product['provenance']['altitude_km'],
              'Ls_degrees':product['provenance']['Ls'],'scenario':1,
              'comment':'Model output, not observed winds. RMS is model day-to-day variability.'})
    return ds


def csv_bytes(product):
    # Metadata travels with CSV; pandas can read it with comment='#'.
    prefix='# '+json.dumps(product['provenance'],ensure_ascii=False)+'\n'
    frame=dataset(product).to_dataframe().reset_index()
    frame.columns=[f'{c} [{UNITS[c]}]' if c in UNITS else c for c in frame.columns]
    return (prefix+frame.to_csv(index=False)).encode('utf-8')


def png_bytes(product,field='speed'):
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    lon,lat=product['longitude'],product['latitude']
    f=product['fields']; p=product['provenance']
    fig,ax=plt.subplots(figsize=(12,6.5),layout='constrained')
    signed=field in ['u','v','w','effective_speed']
    kwargs={}
    if signed:
        bound=max(float(np.nanmax(np.abs(f[field]))),1)
        kwargs={'vmin':-bound,'vmax':bound}
    mesh=ax.pcolormesh(lon,lat,f[field],cmap='RdBu_r' if signed else 'magma',shading='nearest',**kwargs)
    # Quiver EN components are explanatory glyphs, not parcel trajectories.
    xx,yy=np.meshgrid(lon[::3],lat[::3]); u=f['u'][::3,::3];v=f['v'][::3,::3]
    q=ax.quiver(xx,yy,u,v,color='white',scale=1800,width=.002)
    ax.quiverkey(q,.85,1.02,100,'100 m/s',labelcolor='#24262b')
    fig.colorbar(mesh,ax=ax,label=f'{LABELS.get(field,field)} [{UNITS[field]}]',shrink=.85)
    ax.set(xlim=(-180,180),ylim=(-90,90),xlabel='East longitude (°)',ylabel='North latitude (°)',
           title=f"MCD 6.1 · Ls {p['Ls']:g}° · {p['altitude_km']:g} km above areoid\n{p['time_mode']} · reference hour {p['hour_reference']:g} h")
    ax.grid(alpha=.15)
    fig.text(.01,.005,'Simulated fields · official CALL_MCD · arrows: E/N components, graphical scale · '+p['cache_key'][:12],fontsize=8)
    stream=io.BytesIO();fig.savefig(stream,format='png',dpi=180);plt.close(fig)
    return stream.getvalue()
