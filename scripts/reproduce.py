"""Recompute atmospheric diagnostics from authorized MCD data and our scalar model."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import json
import numpy as np
from marswind.analysis import map_product,profile_product,modal_product
from marswind.export import dataset,csv_bytes,png_bytes
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
profile=profile_product();modes=modal_product()
(out/'profile_insight.json').write_text(json.dumps(clean(profile),ensure_ascii=False,indent=2))
(out/'acoustic_benchmark.json').write_text(json.dumps(clean(modes),ensure_ascii=False,indent=2))
fig,axes=plt.subplots(2,2,figsize=(12,7.6),layout='constrained')
maximum=max(np.nanmax(p['fields']['speed']) for p in products)
for ax,p in zip(axes.flat,products):
 mesh=ax.pcolormesh(p['longitude'],p['latitude'],p['fields']['speed'],vmin=0,vmax=maximum,cmap='magma',shading='nearest')
 ax.set(title=f"Ls = {p['provenance']['Ls']:g}° | mean = {p['stats']['mean_speed']:.1f} m/s",xlabel='East longitude (°)',ylabel='North latitude (°)',xlim=(-180,180),ylim=(-90,90))
fig.colorbar(mesh,ax=axes,label='Horizontal speed (m/s)',shrink=.8)
fig.suptitle('Mars | circulation at 60 km above areoid\nMCD 6.1 · climatology / average EUV · same instant, 12 h at 0° E',fontsize=14)
fig.savefig(out/'seasonal_comparison.png',dpi=180);plt.close(fig)
summary={'parameters':reference['provenance'],'seasons':[{**p['stats'],'Ls':p['provenance']['Ls']} for p in products],
         'benchmark_grid_difference_pct':modes['grid_difference_pct'].tolist(),
         'benchmark_relative_shift':modes['relative_shift'].tolist()}
(out/'run_summary.json').write_text(json.dumps(clean(summary),indent=2,ensure_ascii=False))
print(json.dumps(clean(summary),indent=2,ensure_ascii=False))
