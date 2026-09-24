"""Controlled map sequences and labelled movies with a single shared colour scale."""
import tempfile
from pathlib import Path
import numpy as np
from .analysis import map_product
from .export import LABELS,UNITS,PLOT_LOCK

SEQUENTIAL=['#251626','#6b2940','#b64938','#e88448','#f5c77a','#fff0c5']
DIVERGING=['#484268','#7875b1','#b8abd6','#eee4d5','#e89b67','#c85d39','#763325']


def sequence_product(axis='season',field='speed',altitude=60,ls=255,lt=12,time_mode='universal',azimuth=90):
    if axis not in ('season','altitude') or field not in ('speed','u','v','w','temperature','effective_speed','shear'):
        raise ValueError('Unknown sweep axis or physical field.')
    values=np.arange(0,360,15) if axis=='season' else np.arange(10,201,10)
    frames=[];minimum=np.inf;maximum=-np.inf
    for value in values:
        height=float(value) if axis=='altitude' else altitude
        season=float(value) if axis=='season' else ls
        product=map_product(altitude=height,ls=season,lt=lt,time_mode=time_mode,azimuth=azimuth)
        selected=product['fields'][field]
        valid=selected[np.isfinite(selected)]
        if valid.size:
            minimum=min(minimum,float(valid.min()));maximum=max(maximum,float(valid.max()))
        # Only the map, tooltip and statistics fields travel in the sequence.
        fields={key:product['fields'][key] for key in {field,'speed','u','v','temperature','local_time'}}
        frames.append({'value':float(value),'fields':fields,'stats':product['stats'],'provenance':product['provenance']})
    if not np.isfinite(minimum):
        raise ValueError('No finite atmospheric values in this sequence.')
    signed=field in ('u','v','w') or minimum<0
    if signed:
        bound=max(abs(minimum),abs(maximum),1e-9);minimum,maximum=-bound,bound
    elif field!='temperature':minimum=0.
    if maximum<=minimum:maximum=minimum+1.
    return {'axis':axis,'field':field,'values':values,'frames':frames,
            'longitude':product['longitude'],'latitude':product['latitude'],
            'scale':{'min':minimum,'max':maximum,'colors':DIVERGING if signed else SEQUENTIAL},
            'context':{'altitude':altitude,'ls':ls,'lt':lt,'time_mode':time_mode,'azimuth':azimuth},
            'note':'A sweep of sampled climatology, not a weather forecast or parcel trajectory. Equal Ls steps are not equal elapsed times. Altitudes are above the areoid.'}


def movie_bytes(sequence,fps=2):
    """Create an H.264 MP4. Frame timing is presentation timing, not Mars time."""
    if fps not in (1,2,4):raise ValueError('Playback must be 1, 2 or 4 frames per second.')
    import matplotlib
    matplotlib.use('Agg')
    import imageio_ffmpeg
    from matplotlib import pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.animation import FFMpegWriter
    # Matplotlib and its rcParams are process-global; serialize movie rendering.
    with PLOT_LOCK, tempfile.TemporaryDirectory(prefix='marswind-movie-') as folder:
        destination=Path(folder)/'marswind.mp4'
        with matplotlib.rc_context({'animation.ffmpeg_path':imageio_ffmpeg.get_ffmpeg_exe(),
                                    'font.family':'DejaVu Sans','text.color':'#f4e5d8','axes.labelcolor':'#b5a49b',
                                    'xtick.color':'#b5a49b','ytick.color':'#b5a49b','axes.edgecolor':'#493934'}):
            fig=plt.figure(figsize=(12.8,7.2),facecolor='#100e10');ax=fig.add_axes([.075,.225,.78,.53])
            ax.set_facecolor('#1b1619')
            field=sequence['field'];scale=sequence['scale'];cmap=LinearSegmentedColormap.from_list('marswind',scale['colors'])
            f=sequence['frames'][0];lon=sequence['longitude'];lat=sequence['latitude']
            mesh=ax.pcolormesh(lon,lat,f['fields'][field],cmap=cmap,vmin=scale['min'],vmax=scale['max'],shading='nearest')
            ax.set(xlim=(-180,180),ylim=(-90,90),xlabel='East longitude (°)',ylabel='North latitude (°)')
            ax.set_xticks(np.arange(-180,181,60));ax.set_yticks(np.arange(-90,91,30));ax.grid(alpha=.12)
            cax=fig.add_axes([.88,.225,.015,.53]);bar=fig.colorbar(mesh,cax=cax);bar.set_label(f'{LABELS[field]} ({UNITS[field]})',labelpad=12)
            xx,yy=np.meshgrid(lon[::3],lat[::3]);u=f['fields']['u'][::3,::3];v=f['fields']['v'][::3,::3]
            speed=np.hypot(u,v);arrows=ax.quiver(xx,yy,np.divide(u,speed,where=speed>0,out=np.zeros_like(u)),np.divide(v,speed,where=speed>0,out=np.zeros_like(v)),color='#fff5e5aa',scale=45,width=.002)
            fig.text(.075,.92,'MARS WIND LAB / '+('A MARTIAN YEAR' if sequence['axis']=='season' else 'THROUGH THE ATMOSPHERE'),color='#f19a70',size=12,weight='bold')
            heading=fig.text(.075,.84,'',size=24,weight='bold');context=sequence['context']
            convention=f"{context['lt']:g} h at 0° E · simultaneous map" if context['time_mode']=='universal' else f"{context['lt']:g} h local at every longitude · not simultaneous"
            fig.text(.075,.12,'MCD 6.1 · climatology / average EUV · '+convention,size=9)
            fig.text(.075,.078,f"Fixed colour scale · azimuth {context['azimuth']:g}° · normalized arrows show direction, not trajectories",size=9,color='#b5a49b')
            fig.text(.075,.04,'LMD / IPSL · OU · Oxford · IAA | Geometric altitude / areoid | Playback spacing is not elapsed Mars time.',size=8,color='#b5a49b')
            frame_label=fig.text(.84,.92,'',ha='right',size=10,color='#b5a49b')
            writer=FFMpegWriter(fps=fps,codec='libx264',bitrate=2000,extra_args=['-pix_fmt','yuv420p','-movflags','+faststart'])
            try:
                with writer.saving(fig,str(destination),dpi=100):
                    for i,frame in enumerate(sequence['frames']):
                        p=frame['provenance'];heading.set_text(f"{LABELS[field]} · {p['altitude_km']:g} km · Ls {p['Ls']:g}°")
                        mesh.set_array(frame['fields'][field])
                        u=frame['fields']['u'][::3,::3];v=frame['fields']['v'][::3,::3];speed=np.hypot(u,v)
                        arrows.set_UVC(np.divide(u,speed,where=speed>0,out=np.zeros_like(u)),np.divide(v,speed,where=speed>0,out=np.zeros_like(v)))
                        frame_label.set_text(f'{i+1:02d} / {len(sequence["frames"]):02d}')
                        writer.grab_frame()
                return destination.read_bytes()
            finally:plt.close(fig)
