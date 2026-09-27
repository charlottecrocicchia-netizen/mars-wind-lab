"""Build the three physical workstreams and a paleomagnetic counterexample.

Default: reproduce from small committed inputs, with no network or raw archive.
--extract: explicitly refresh permitted MOLA strips and hemisphere summaries
from already present local source products; never downloads or unpacks archives.
"""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path
import platform

import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'mars-physics-v1'
import matplotlib.pyplot as plt

from marswind.dichotomy_physics import (column_support, layered_density,
    thermal_susceptibility, modal_power_share, flexure, boundary_proxy, arai_example)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/physics'
P = json.loads((OUT/'protocol.json').read_text())

def sha(path): return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def save(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n')
def csv_save(name, rows):
    with (OUT/name).open('w', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
def csv_read(name):
    with (OUT/name).open() as f:
        return [{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]


def extract():
    import pyshtools as sh
    raw='data/observations/raw/mola/megt90n000cb.img'
    boundary='data/observations/raw/crustal_models/selected/dichotomy_coordinates-JAH-0-360.txt'
    registry=json.loads((ROOT/'research/data/manifest.json').read_text())
    expected=next(f['sha256'] for r in registry for f in r.get('files',[]) if f.get('local_path')==raw)
    assert sha(raw)==expected, 'MOLA bytes differ from the permitted snapshot'
    grid=np.fromfile(ROOT/raw,dtype='>i2').reshape(720,1440)[::-1]/1000
    lat=np.arange(-89.875,90,.25); lon=np.arange(.125,360,.25)
    p=P['boundary']; chosen=(lat>=p['latitude_range_deg'][0])&(lat<=p['latitude_range_deg'][1])
    rows=[]
    for center in p['longitude_centers_deg_e']:
        strip=grid[:,abs(lon-center)<=p['half_strip_width_deg']]
        median=np.median(strip,axis=1)
        lower,upper=np.quantile(strip,[.25,.75],axis=1)
        for i in np.flatnonzero(chosen):
            rows.append({'longitude_center_deg_e':center,'latitude_deg_n':lat[i],
                'median_elevation_km':median[i],'strip_q25_km':lower[i],'strip_q75_km':upper[i]})
    csv_save('mola_transects.csv',rows)
    a=json.loads((ROOT/'research/data/atlas.json').read_text())
    latitude=np.array(a['latitude']);longitude=np.array(a['longitude'])
    curve=np.loadtxt(ROOT/boundary)
    mask=sh.backends.shtools.Curve2Mask(180,curve[:,[1,0]],0,sampling=2,extend=True)
    south=mask[np.ix_((90-latitude).astype(int),longitude.astype(int))].astype(bool)
    assert south[latitude < -75].mean()>.95 and south[latitude > 75].mean()<.05
    weights=np.broadcast_to(np.cos(np.deg2rad(latitude))[:,None],south.shape)
    def mean(values, region):
        v=np.asarray(values);return float(np.sum(v[region]*weights[region])/weights[region].sum())
    summaries=[]
    for rho,thickness in a['crust_km'].items():
        summaries.append({'south_density_kg_m3':int(rho),'north_density_kg_m3':2900,
            'north_thickness_km':mean(thickness,~south),'south_thickness_km':mean(thickness,south),
            'north_elevation_km':mean(a['topography_km'],~south),'south_elevation_km':mean(a['topography_km'],south)})
    csv_save('hemisphere_inputs.csv',summaries)
    save('input_provenance.json',{'command':'python scripts/physics/build.py --extract',
        'sources':{f:sha(f) for f in [raw,raw.replace('.img','.xml'),boundary,'research/data/atlas.json','research/data/manifest.json']},
        'extraction_script_sha256':sha('scripts/physics/build.py'),'pyshtools':sh.__version__,
        'mola_note':'Median and interquartile spread across eight longitude pixels per strip. Spread is spatial variability, not measurement uncertainty. Coordinates are pixel centers; rows reversed to increasing latitude.',
        'hemisphere_note':'Full archived boundary with the same spherical mask convention as the atlas builder, cosine-area weights on the 2-degree grid, all latitudes. Includes Tharsis and basins; not a pristine pre-volcanic contrast.',
        'licenses':{'MOLA':'NASA PDS public archive; retain credit','crust_and_boundary':'Wieczorek et al. 2022 archive, CC BY 4.0'},
        'generated_inputs':{name:sha('research/physics/'+name) for name in ['mola_transects.csv','hemisphere_inputs.csv']}})


def crust():
    p=P['crust']; maps=csv_read('hemisphere_inputs.csv'); rows=[]
    for row,rm in itertools.product(maps,p['mantle_densities_kg_m3']):
        hn,hs=row['north_thickness_km'],row['south_thickness_km']
        rn,rs=row['north_density_kg_m3'],row['south_density_kg_m3']
        # Exact symmetric decomposition of the column-support contrast.
        thickness_term=(1-(rn+rs)/(2*rm))*(hs-hn)
        density_term=-(hs+hn)/2*(rs-rn)/rm
        relief=float(column_support(hs,rs,rm)-column_support(hn,rn,rm))
        assert abs(relief-thickness_term-density_term)<1e-10
        rows.append(row|{'mantle_density_kg_m3':rm,'thickness_support_km':thickness_term,
            'density_support_km':density_term,'total_support_contrast_km':relief,
            'observed_relief_contrast_km':row['south_elevation_km']-row['north_elevation_km']})
    layers=[]
    for basal,upper,dense,porosity in itertools.product(p['basal_layer_km'],p['upper_grain_densities_kg_m3'],p['basal_densities_kg_m3'],p['upper_porosities']):
        rho=layered_density(p['layer_column_km'],basal,upper,dense,porosity)
        layers.append({'basal_thickness_km':basal,'upper_grain_density_kg_m3':upper,
            'basal_density_kg_m3':dense,'upper_porosity':porosity,'bulk_density_kg_m3':rho,
            'support_km_at_mantle3500':float(column_support(p['layer_column_km'],rho,3500)),
            'basal_density_exceeds_mantle3500':bool(basal>0 and dense>3500)})
    csv_save('crust_support.csv',rows);csv_save('layer_sensitivity.csv',layers)
    result={'status':'Conditional hydrostatic support accounting; no new gravity or petrological inversion',
        'maps':rows,'layers':layers,'published_density_context':p['context_density_kg_m3'],
        'reported_plus_minus':p['context_reported_plus_minus_kg_m3'],'context_note':p['context_note'],
        'reference_porosity_example':{h:1-rho/2900 for h,rho in p['context_density_kg_m3'].items()},
        'porosity_note':'Empty-pore effective mixture at uniform grain density 2900 kg/m3, with no basal layer; illustrates ambiguity, not a plausible whole-crust compaction profile.'}
    save('crust.json',result);return result


def feedback():
    p=P['feedback']; rows=[]; sets=[]
    degrees=np.arange(1,p['maximum_degree']+1)
    for lid in p['lid_thicknesses_km']:
        response=np.array([thermal_susceptibility(int(l),lid,P['radius_km'],p['cells']) for l in degrees])
        finer=np.array([thermal_susceptibility(int(l),lid,P['radius_km'],p['cells']*2) for l in degrees])
        ratio=response/response[0]
        for l,v,r in zip(degrees,response,ratio):
            rows.append({'lid_km':lid,'degree':int(l),'dimensionless_basal_response':float(v),'relative_growth_rate':float(r)})
        histories=[];n=p['power_spectrum_maximum_degree'];ld=degrees[:n]
        for spectrum,power in [('equal_degree_power',np.ones(n)),('equal_coefficient_power',2*ld+1)]:
            for efolds in p['degree_one_efolds']:
                shares=modal_power_share(ratio[:n],efolds,power)
                histories.append({'spectrum':spectrum,'degree_one_efolds':efolds,'degree_one_share':float(shares[0]),'shares':shares.tolist()})
        sets.append({'lid_km':lid,'degree':degrees.tolist(),'relative_growth':ratio.tolist(),
            'degree1_vs_degree2_efolds_for_tenfold_amplitude_advantage':float(np.log(10)/(ratio[0]-ratio[1])),
            'max_refinement_relative_change':float(np.max(abs(finer-response)/abs(finer))),
            'histories':histories})
    assert max(s['max_refinement_relative_change'] for s in sets)<1e-5
    csv_save('feedback_modes.csv',rows)
    result={'status':'Linear spherical-shell benchmark; finite-time dominance depends on initial spectrum',
        'sets':sets,'note':p['note'],'power_note':'Equal coefficient variance gives expected power proportional to 2l+1; normalized expected powers are illustrative allocations, not Monte Carlo probabilities of Mars.'}
    save('feedback.json',result);return result


def boundary():
    p=P['boundary']; data=csv_read('mola_transects.csv'); profiles=[];csvrows=[];pad_errors=[]
    spacing=p['profile_radius_km']*np.pi/180*.25
    search=np.array(p['search_latitude_range_deg'])-p['reference_latitude_deg']
    search=search*p['profile_radius_km']*np.pi/180
    for center in p['longitude_centers_deg_e']:
        strip=[r for r in data if r['longitude_center_deg_e']==center]
        lat=np.array([r['latitude_deg_n'] for r in strip]);z=np.array([r['median_elevation_km'] for r in strip])
        x=(lat-p['reference_latitude_deg'])*p['profile_radius_km']*np.pi/180
        observed={str(s):boundary_proxy(x,z,s,search) for s in p['smoothing_km']}
        reference=observed['50']['x_km']
        scenarios=[]
        configs=[(0,30,150,100)]+list(itertools.product(p['load_peaks_km'],p['elastic_thicknesses_km'],p['load_offsets_km'],p['load_widths_km']))
        for amp,te,offset,width in configs:
            load=amp*1000*np.exp(-.5*((x-reference-offset)/width)**2)
            w=flexure(load,spacing*1000,te,p['mantle_density_kg_m3'],p['load_density_kg_m3'],p['gravity_m_s2'],p['padding'])
            fine=flexure(load,spacing*1000,te,p['mantle_density_kg_m3'],p['load_density_kg_m3'],p['gravity_m_s2'],4)
            pad_errors.append(float(np.max(abs(fine-w))))
            restored=z-(load-w)/1000
            edges={str(s):boundary_proxy(x,restored,s,search) for s in p['smoothing_km']}
            sid=f'a{amp:g}_te{te}_offset{offset}_width{width}'
            scenarios.append({'id':sid,'peak_load_km':amp,'elastic_km':te,'offset_km':offset,'width_km':width,
                'restored_km':np.round(restored,6).tolist(),'edges':edges})
            for smooth,e in edges.items():
                csvrows.append({'longitude_deg_e':center,'scenario':sid,'peak_load_km':amp,'elastic_km':te,'offset_km':offset,'width_km':width,
                    'smoothing_km':int(smooth),'observed_proxy_km':observed[smooth]['x_km'],'restored_proxy_km':e['x_km'],
                    'shift_km':e['x_km']-observed[smooth]['x_km'],'at_search_edge':e['at_search_edge']})
        shifts=[r['shift_km'] for r in csvrows if r['longitude_deg_e']==center and r['smoothing_km']==50]
        profiles.append({'longitude_deg_e':center,'latitude_deg_n':lat.tolist(),'x_km':x.tolist(),
            'observed_km':z.tolist(),'strip_q25_km':[r['strip_q25_km'] for r in strip],
            'strip_q75_km':[r['strip_q75_km'] for r in strip],'observed_proxies':observed,
            'shift_range_50km': [min(shifts),max(shifts)],'scenarios':scenarios})
    assert max(pad_errors)<.1, 'Periodic image contamination exceeds 0.1 m'
    csv_save('boundary_scenarios.csv',csvrows)
    result={'status':'Conditional elastic unloading of observed profiles; no unique ancient boundary recovered',
        'profiles':profiles,'spacing_km':spacing,'max_padding_difference_m':max(pad_errors),'note':p['note'],
        'scenario_envelope_note':'Range over selected assumed loads; not confidence or credible intervals. Every scenario explains the same observed profile exactly by construction.'}
    save('boundary.json',result);return result


def paleomagnetism():
    p=P['paleomagnetism'];cases=[arai_example(p['true_field_ut'],p['laboratory_field_ut'],r) for r in p['natural_to_lab_efficiency_ratios']]
    save('paleomagnetism.json',{'status':'Educational counterexample, not measured paleointensities','cases':cases,'note':p['note']})
    csv_save('arai_counterexample.csv',[{'efficiency_ratio':r['efficiency_ratio'],'true_field_ut':r['true_field_ut'],'apparent_field_ut':r['apparent_field_ut'],'lab_ptrm_normalized':x,'nrm_remaining_normalized':y} for r in cases for x,y in zip(r['lab_ptrm_normalized'],r['nrm_remaining_normalized'])])
    return cases


def figures(c,f,b,p):
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
    colors=['#267b81','#5a77b8','#8a62a5']
    def finish(fig,name):
        fig.savefig(OUT/(name+'.png'),dpi=150);fig.savefig(OUT/(name+'.svg'),metadata={'Date':None});plt.close(fig)
        svg=OUT/(name+'.svg')
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig,ax=plt.subplots(figsize=(8,4.7),layout='constrained')
    rows=[r for r in c['maps'] if r['mantle_density_kg_m3']==3500]
    xx=np.arange(len(rows));th=np.array([r['thickness_support_km'] for r in rows]);den=np.array([r['density_support_km'] for r in rows])
    ax.bar(xx-.18,th,width=.36,label='Thickness contribution',color=colors[0]);ax.bar(xx+.18,den,width=.36,label='Density contribution',color=colors[1])
    ax.plot(xx,th+den,'ko-',label='Total column support')
    ax.axhline(rows[0]['observed_relief_contrast_km'],ls='--',color='#777',label='Observed MOLA contrast')
    ax.set(xticks=xx,xticklabels=[int(r['south_density_kg_m3']) for r in rows],xlabel='Assumed south crust density (kg m⁻³); north = 2900',ylabel='South minus north support (km)',title='Density and thickness share the same support budget')
    ax.legend(fontsize=8);fig.supxlabel('Conditional published maps · not an independent gravity fit',fontsize=9)
    finish(fig,'crust_support')
    fig,(ax,other)=plt.subplots(1,2,figsize=(10,4.5),layout='constrained')
    for s,color in zip(f['sets'],colors):
        ax.plot(s['degree'],s['relative_growth'],label=f"{s['lid_km']} km lid",color=color)
        rr=[r for r in s['histories'] if r['spectrum']=='equal_coefficient_power']
        other.plot([r['degree_one_efolds'] for r in rr],[r['degree_one_share']*100 for r in rr],'o-',color=color)
    ax.set(xlabel='Spherical harmonic degree',ylabel='Growth rate / degree-one rate',title='Long wavelengths grow at similar rates');ax.legend()
    other.set(xlabel='Degree-one e-folds (not geological time)',ylabel='Degree-one share of modal power (%)',title='Fastest does not mean dominant')
    fig.supxlabel('Linear shell test · equal initial coefficient power over degrees 1–20 · large growth is an extrapolation',fontsize=9)
    finish(fig,'feedback_selection')
    fig,axes=plt.subplots(2,2,figsize=(10,7),layout='constrained')
    for ax,s in zip(axes.ravel(),b['profiles']):
        curves=np.array([r['restored_km'] for r in s['scenarios']]);xx=np.array(s['x_km'])
        ax.fill_between(xx,curves.min(axis=0),curves.max(axis=0),color=colors[1],alpha=.22,label='Assumed-load envelope')
        ax.plot(xx,s['observed_km'],color='#172936',label='Observed MOLA median')
        ax.axvline(s['observed_proxies']['50']['x_km'],color=colors[0],ls='--',lw=1)
        ax.set(xlim=(-800,800),title=f"{s['longitude_deg_e']}°E median strip",xlabel='Distance north of 35°N (km)',ylabel='Areoid-relative elevation (km)')
    axes[0,0].legend(fontsize=8);fig.supxlabel('Conditional pre-load relief · envelope is not an uncertainty interval or a mapped ancient boundary',fontsize=9)
    finish(fig,'boundary_restoration')
    fig,ax=plt.subplots(figsize=(7,4.5),layout='constrained')
    for r,color in zip(p,colors):
        ax.plot(r['lab_ptrm_normalized'],r['nrm_remaining_normalized'],'o-',color=color,label=f"Efficiency ratio {r['efficiency_ratio']:g}: apparent {r['apparent_field_ut']:g} µT")
    ax.set(xlabel='Laboratory pTRM gained / initial NRM',ylabel='Natural remanence remaining / initial NRM',title='Three perfect lines; one known input field of 25 µT')
    ax.legend(fontsize=9);fig.supxlabel('Synthetic counterexample · laboratory field 50 µT · no specimen re-estimated',fontsize=9)
    finish(fig,'paleointensity_control')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--extract',action='store_true');args=parser.parse_args()
    if args.extract:extract()
    provenance=json.loads((OUT/'input_provenance.json').read_text())
    for name,digest in provenance['generated_inputs'].items():
        assert sha('research/physics/'+name)==digest, 'Committed extraction differs from provenance'
    c,f,b,p=crust(),feedback(),boundary(),paleomagnetism();figures(c,f,b,p)
    inputs=['scripts/physics/build.py','src/marswind/dichotomy_physics.py','tests/test_dichotomy_physics.py',
        'research/physics/protocol.json','research/physics/sources.json','research/physics/input_provenance.json','research/physics/mola_transects.csv','research/physics/hemisphere_inputs.csv']
    outputs=[q for q in OUT.iterdir() if q.suffix in ['.json','.csv','.png','.svg'] and q.name not in ['manifest.json','protocol.json','sources.json','input_provenance.json','mola_transects.csv','hemisphere_inputs.csv']]
    save('manifest.json',{'status':'Three bounded studies and one educational control executed; no unique origin selected',
        'command':'python scripts/physics/build.py','downloads_required':False,'inputs':{n:sha(n) for n in inputs},
        'outputs':{str(q.relative_to(ROOT)):sha(str(q.relative_to(ROOT))) for q in sorted(outputs)},
        'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
        'validation':{'feedback_max_refinement_relative_change':max(s['max_refinement_relative_change'] for s in f['sets']),
            'flexure_max_padding_difference_m':b['max_padding_difference_m']}})
    print(json.dumps({'observed_relief_km':c['maps'][0]['observed_relief_contrast_km'],
        'feedback_100km':f['sets'][1]['histories'][-1],
        'boundary_shift_ranges_km':{s['longitude_deg_e']:s['shift_range_50km'] for s in b['profiles']},
        'output_bytes':sum(q.stat().st_size for q in outputs)},indent=2))

if __name__=='__main__':main()
