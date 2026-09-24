"""Reproduce the public experiment figure and local, traceable study notes."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import json
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.ticker import NullFormatter
from marswind.experiments import experiment_product,study_note
from marswind.server import clean


def main():
    result=experiment_product();f=result['fields'];z=result['altitude_km']
    figure_dir=ROOT/'docs/figures';figure_dir.mkdir(parents=True,exist_ok=True)
    output=ROOT/'output';output.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,
                         'axes.edgecolor':'#614134','axes.labelcolor':'#d9bba6','text.color':'#f2d9c8',
                         'xtick.color':'#bca08e','ytick.color':'#bca08e','grid.color':'#4b3235'})
    fig,axs=plt.subplots(1,3,figsize=(14,6.6),sharey=True)
    fig.set_facecolor('#100e11');fig.subplots_adjust(left=.065,right=.975,bottom=.23,top=.76,wspace=.28)
    fig.text(.065,.91,'MARS WIND LAB',fontsize=11,color='#ef9d70',weight='bold')
    fig.text(.065,.845,'Three questions. One atmospheric column.',fontsize=23,weight='bold')
    for ax in axs:
        ax.set_facecolor('#1b171b');ax.grid(True,alpha=.75);ax.set_ylim(20,160)
    a=axs[0]
    a.plot(f['sound_speed'],z,color='#ab9290',ls='--',label='At rest')
    a.plot(f['effective_speed'],z,color='#f29f6d',label='Eastward',lw=2)
    a.plot(f['opposite_effective_speed'],z,color='#bf92d7',label='Westward',lw=2)
    a.axvline(0,color='#b88468',lw=.8)
    a.set(title='01  Direction',xlabel='Effective sound speed (m/s)',ylabel='Altitude above areoid (km)')
    a.legend(loc='lower right',frameon=False,fontsize=9)
    a=axs[1]
    a.plot(f['season_total_delta'],z,color='#fbe3c6',label='Total',lw=2.5)
    a.plot(f['season_wind_delta'],z,color='#bf92d7',label='Wind',lw=1.8)
    a.plot(f['season_thermodynamic_delta'],z,color='#b097d0',label='Thermodynamics',lw=1.8)
    a.set(title='02  Season: Ls 75° − 255°',xlabel='Effective-speed change (m/s)')
    a.legend(loc='upper right',frameon=False,fontsize=9)
    a=axs[2]
    a.plot(f['wavelength_density_scale_ratio'],z,color='#f29f6d',label='100 s',lw=2)
    a.plot(f['wavelength_density_scale_ratio']/10,z,color='#ca95dd',label='10 s',lw=2)
    a.axvline(1,color='#bf92d7',ls='--',lw=1)
    a.set_xscale('log');a.set_xticks([.2,.5,1,2,5],labels=['0.2','0.5','1','2','5']);a.xaxis.set_minor_formatter(NullFormatter());a.set(title='03  Reference period',xlabel='Wavelength / density scale')
    a.legend(loc='lower left',frameon=False,fontsize=9)
    fig.text(.065,.12,'InSight coordinates · 135.623° E, 4.502° N · 12 h local solar time · geometric heights',fontsize=10)
    fig.text(.065,.075,'MCD 6.1 · climatology / average EUV · LMD / IPSL, OU, Oxford, IAA',fontsize=9,color='#bca08e')
    fig.text(.065,.038,'Local diagnostics only: no acoustic path, arrival prediction or explanation of the Martian dichotomy.',fontsize=9,color='#bca08e')
    fig.savefig(figure_dir/'experiments.png',dpi=160,facecolor=fig.get_facecolor());plt.close(fig)
    for question in ['direction','season','scale']:
        (output/f'study_{question}.md').write_text(study_note(result,question))
    (output/'guided_experiments.json').write_text(json.dumps(clean(result),indent=2))
    print(json.dumps(clean({k:result[k] for k in ['impact_peak','season_peak','scale_peak']}),indent=2))


if __name__=='__main__':main()
