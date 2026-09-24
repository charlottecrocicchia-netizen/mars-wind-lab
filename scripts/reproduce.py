"""Recompute the first research bundle from official data and legacy eigenfunctions."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import json
import numpy as np
from marswind.analysis import map_product,profile_product,modal_product
from marswind.export import dataset,csv_bytes,png_bytes
from marswind.legacy import load_archived_modes
from marswind.server import clean
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

out=ROOT/'output';out.mkdir(exist_ok=True)
products=[map_product(ls=ls) for ls in [75,165,255,345]]
reference=products[2]
dataset(reference).to_netcdf(out/'marswind_Ls255_60km.nc')
(out/'marswind_Ls255_60km.csv').write_bytes(csv_bytes(reference))
(out/'marswind_Ls255_60km.png').write_bytes(png_bytes(reference))
profile=profile_product();modes=modal_product();legacy=load_archived_modes()
(out/'profile_insight.json').write_text(json.dumps(clean(profile),ensure_ascii=False,indent=2))
(out/'acoustic_benchmark.json').write_text(json.dumps(clean(modes),ensure_ascii=False,indent=2))
(out/'archived_modes_audit.json').write_text(json.dumps(clean(legacy),ensure_ascii=False))
fig,axes=plt.subplots(2,2,figsize=(12,7.6),layout='constrained')
maximum=max(np.nanmax(p['fields']['speed']) for p in products)
for ax,p in zip(axes.flat,products):
 mesh=ax.pcolormesh(p['longitude'],p['latitude'],p['fields']['speed'],vmin=0,vmax=maximum,cmap='magma',shading='nearest')
 ax.set(title=f"Ls = {p['provenance']['Ls']:g}° | mean = {p['stats']['mean_speed']:.1f} m/s",xlabel='East longitude (°)',ylabel='North latitude (°)',xlim=(-180,180),ylim=(-90,90))
fig.colorbar(mesh,ax=axes,label='Horizontal speed (m/s)',shrink=.8)
fig.suptitle('Mars | circulation at 60 km above areoid\nMCD 6.1 · climatology / average EUV · same instant, 12 h at 0° E',fontsize=14)
fig.savefig(out/'seasonal_comparison.png',dpi=180);plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(12,7),sharey=True,layout='constrained')
for i,m in enumerate(legacy['modes']):
 for ax,field in zip(axes,['U','V']):
  x=np.asarray(m[field]['real']);xi=np.asarray(m[field]['imag'])
  ax.plot(i*2.5+x,m['altitude_km'],color=plt.cm.viridis(i/9),linewidth=1.2)
  ax.plot(i*2.5+xi,m['altitude_km'],color=plt.cm.viridis(i/9),linewidth=.8,linestyle='--')
  ax.axvline(i*2.5,color='grey',linewidth=.3)
for ax,field in zip(axes,['U','V']):
 ax.set(title=f'Component {field} weighted by √ρ',xlabel='Radial order n (offset profiles)',xticks=np.arange(10)*2.5,xticklabels=range(10),ylim=(0,200))
axes[0].set_ylabel('Archived-model altitude: r − 3383 km (km)')
fig.suptitle('Archived eigenfunctions | ℓ = 500\nReal: solid · imaginary: dashed · each normalized by maximum modulus',fontsize=13)
fig.savefig(out/'archived_eigenfunctions.png',dpi=180);plt.close(fig)
summary={'parameters':reference['provenance'],'seasons':[{**p['stats'],'Ls':p['provenance']['Ls']} for p in products],
         'benchmark_grid_difference_pct':modes['grid_difference_pct'].tolist(),
         'benchmark_relative_shift':modes['relative_shift'].tolist(),
         'archived_inertia_ratios':[m['normalization_integral_ratio'] for m in legacy['modes']]}
(out/'run_summary.json').write_text(json.dumps(clean(summary),indent=2,ensure_ascii=False))
print(json.dumps(clean(summary),indent=2,ensure_ascii=False))
