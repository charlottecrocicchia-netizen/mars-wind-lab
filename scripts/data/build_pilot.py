"""Reproduce the regional pilot from public, local inputs. No network at build time."""
from pathlib import Path
import csv
import hashlib
import json
import re
import sys
import zipfile
from itertools import product

import numpy as np
import pyshtools as sh
import shapely
from shapely.geometry import Polygon, GeometryCollection

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from marswind.pilot import (distance_bearing, destination, sample_mola, contrast,
                            radial_profile, morphology, mean)

RAW=ROOT/'data/observations/raw'
OUT=ROOT/'research/pilot'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(x):
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [clean(v) for v in x]
    if isinstance(x,(float,np.floating)):return round(float(x),8) if np.isfinite(x) else None
    if isinstance(x,np.integer):return int(x)
    return x


def save(name,data):
    (OUT/name).write_text(json.dumps(clean(data),allow_nan=False,separators=(',',':'))+'\n')


def geology_classifier():
    data=json.loads((RAW/'geology/units.json').read_text())
    assert data['spatialReference']['wkid']==104971
    attrs={};shapes=[];codes=[]
    for f in data['features']:
        a=f['attributes'];attrs[a['Unit']]=a;codes.append(a['Unit'])
        g=GeometryCollection()
        for ring in f['geometry']['rings']:
            g=shapely.symmetric_difference(g,shapely.make_valid(Polygon(ring)))
        shapes.append(g)
    tree=shapely.STRtree(shapes)
    names=sorted(attrs)
    def classify(lat,lon):
        points=shapely.points(((lon+180)%360-180).ravel(),lat.ravel())
        pairs=tree.query(points,predicate='within')
        ids=np.full(lat.size,-1,dtype=int)
        for p,f in pairs.T:ids[p]=names.index(codes[f])
        ids[np.bincount(pairs[0],minlength=lat.size)!=1]=-1
        return ids.reshape(lat.shape)
    return classify,[{'code':n,'description':attrs[n]['UnitDesc'],'group':attrs[n]['UnitGroup']} for n in names]


def audit_geometry(config):
    """Check transcribed MDIM 2.1 values against the acquired HTML rows."""
    for site in config['sites']:
        if site['id']=='ladon':continue
        text=(RAW/f"pilot/{site['id']}.html").read_text()
        selected=re.findall(r'<option label="MDIM 2.1" value="(\d+)"\s+selected',text)[0]
        rows=re.findall(r'<tr class="geometry geom-'+selected+r' cs-6">(.*?)</tr>',text,re.S)
        fields={}
        for row in rows:
            key=re.search(r'<th>([^<]+)</th>',row).group(1)
            value=re.sub('<[^>]+>',' ',row.split('</th>')[1])
            fields[key]=float(re.search(r'-?\d+\.?\d*',value).group())
        assert fields['Center Latitude']==site['lat']
        assert fields['Center Longitude']==site['lon']
        assert fields['Diameter']==site['diameter_km']


def main():
    config=json.loads((OUT/'protocol.json').read_text());audit_geometry(config)
    with zipfile.ZipFile(RAW/'pilot/lagain_db.json.zip') as z:
        catalog=[f['properties'] for f in json.loads(z.read('lagain_db.json'))['features']]
    ladon=next(c for c in catalog if c['CRATER_ID']=='19-000000')
    assert ladon['STATUS']=='Misidentified' and ladon['RADIUS']==548325
    large=[c for c in catalog if c['RADIUS']>=75000 and c['TYPE']!=5]
    classify,units=geology_classifier();print('Geologic polygons ready',flush=True)
    mola=np.fromfile(RAW/'mola/megt90n000cb.img',dtype='>i2').reshape(720,1440)
    model=sh.SHMagCoeffs.from_file(str(RAW/'magnetic_field/Langlais2019.sh.gz'),lmax=134,skip=4,
              r0=3393500,header=False,file_units='nT',units='nT',encoding='utf-8')
    atlas=json.loads((ROOT/'research/data/atlas.json').read_text())
    water=json.loads((ROOT/'research/data/water.json').read_text())
    # Independent code path, same source model: numerical continuity check, not
    # independent scientific evidence for the model itself.
    checks=[]
    for i,j in [(20,100),(38,27),(43,8),(35,166)]:
        lat,lon=atlas['latitude'][i],atlas['longitude'][j]
        direct=float(np.linalg.norm(model.expand(lat=float(lat),lon=float(lon),r=3543500.)))
        stored=atlas['magnetic_nT']['150'][i][j]
        checks.append({'lat':lat,'lon':lon,'direct_nT':direct,'atlas_nT':stored,'absolute_error_nT':abs(direct-stored)})
        assert abs(direct-stored)<0.00051
    cases=[]
    for site in config['sites']:
        print('Computing',site['name'],flush=True)
        R=site['diameter_km']/2;step=config['grid_step_deg']
        extent=np.rad2deg(2.8*R/config['radius_km'])+step
        latitude=np.arange(np.floor((site['lat']-extent)/step)*step+step/2,site['lat']+extent,step)
        lon_extent=extent/np.cos(np.deg2rad(min(80,abs(site['lat'])+extent)))
        longitude=np.arange(np.floor((site['lon']-lon_extent)/step)*step+step/2,site['lon']+lon_extent,step)
        x,y=np.meshgrid(longitude,latitude)
        distance,bearing=distance_bearing(y,x,site['lat'],site['lon']);r=distance/R
        weights=np.cos(np.deg2rad(y));geology=classify(y,x)
        fields={}
        for h in config['altitudes_km']:
            v=model.expand(lat=y.ravel(),lon=x.ravel()%360,r=np.full(x.size,(3393.5+h)*1000))
            fields[str(h)]=np.linalg.norm(v,axis=1).reshape(x.shape)
        inner=r<=.8;outer=(r>=1.2)&(r<=2)
        baseline={h:contrast(v,weights,inner,outer,geology) for h,v in fields.items()}
        variants=[]
        for h,cut,ring,scale in product(config['altitudes_km'],config['sensitivity']['inside_radius_R'],
                    config['sensitivity']['outside_radius_R'],config['sensitivity']['radius_scale']):
            inside=r<=cut*scale;outside=(r>=ring[0]*scale)&(r<=ring[1]*scale)
            result=contrast(fields[str(h)],weights,inside,outside,geology)
            variants.append({'altitude_km':h,'inside_R':cut,'outside_R':ring,'radius_scale':scale,
                             **{k:v for k,v in result.items() if k!='strata'}})
        # Directional sensitivity; overlapping samples are not a bootstrap CI.
        sectors=[]
        for k in range(8):
            keep=np.floor(bearing/45).astype(int)!=k
            sectors.append({'omitted_sector':k,**contrast(fields['150'],weights,inner&keep,outer&keep)})
        # Additional reference-ring screen: remove interiors of other large,
        # non-misidentified catalog craters. Their ejecta/thermal zones remain.
        keep=np.ones_like(inner);excluded=[]
        for c in large:
            d,_=distance_bearing(c['Y'],c['X'],site['lat'],site['lon'])
            if d < .5*R:continue  # target / overlapping central catalog definition
            dist,_=distance_bearing(y,x,c['Y'],c['X'])
            intersects=outer&(dist<=c['RADIUS']/1000)
            if intersects.any():
                keep &= dist>c['RADIUS']/1000
                excluded.append(c['CRATER_ID'])
        screened=contrast(fields['150'],weights,inner,outer&keep,geology)
        screened['reference_area_retained_fraction']=float(weights[outer&keep].sum()/weights[outer].sum())
        screened['excluded_crater_ids']=excluded
        # These coarse presence points do not participate in the estimand.
        mineral_points=[];mineral_counts=[]
        for kind in ['RED','GREEN','BLUE','ORANGE','CYAN']:
            cells={tuple(c) for p in water['products'] if p['class']==kind for c in p['cells']}
            count=0
            for i,j in sorted(cells):
                lat,lon=water['latitude'][i],water['longitude'][j]
                d,_=distance_bearing(lat,lon,site['lat'],site['lon'])
                if d<=2*R:
                    count+=1;mineral_points.append({'class':kind,'lat':lat,'lon':lon})
            label=next(p['label'] for p in water['products'] if p['class']==kind)
            mineral_counts.append({'class':kind,'label':label,'occupied_2deg_cells_within_2R':count})
        morph=morphology(mola,site['lat'],site['lon'],site['diameter_km'])
        morph['sensitivity']=[{'radius_scale':scale,'azimuth_step_deg':az,
            'depth_diameter':morphology(mola,site['lat'],site['lon'],site['diameter_km'],az,scale)['depth_diameter']}
            for scale,az in product([.9,1,1.1],[15,30])]
        profiles={h:radial_profile(v,weights,r,np.arange(0,2.51,.25)) for h,v in fields.items()}
        core_geo=[]
        for u in np.unique(geology[inner]):
            core_geo.append({'unit_index':int(u),'area_fraction':float(weights[inner&(geology==u)].sum()/weights[inner].sum())})
        ratios=[v['ratio'] for v in variants]
        # Topography and crust context are separate, not causal adjustment.
        crust_context={}
        ai=np.clip(((y+90)//2).astype(int),0,89);aj=((x%360)//2).astype(int)
        for density,v in atlas['crust_km'].items():
            grid=np.asarray(v)[ai,aj]
            crust_context[density]={'inside_km':mean(grid,weights,inner),'outside_km':mean(grid,weights,outer)}
        regional_map={'lat':latitude,'lon':longitude,'topography_km':sample_mola(mola,y,x),
                      'field_nT':fields,'units':geology,'mineral_points':mineral_points}
        summary={'ratio_min':min(ratios),'ratio_max':max(ratios),
            'all_variants_below_one':all(v<1 for v in ratios),'all_variants_above_one':all(v>1 for v in ratios),
            'sector_ratio_min':min(s['ratio'] for s in sectors),'sector_ratio_max':max(s['ratio'] for s in sectors)}
        case={'site':site,'baseline':baseline,'sensitivity':variants,'sector_omission':sectors,
              'impact_screen':screened,'summary':summary,'morphology':morph,'profiles':profiles,
              'geology':core_geo,'crust_context':crust_context,'mineral_counts':mineral_counts,
              'map':regional_map}
        cases.append(case)
        print(site['name'],'150 km ratio',baseline['150']['ratio'],'range',summary['ratio_min'],summary['ratio_max'],
              'common geology support',baseline['150']['common_support_fraction'],flush=True)
    primary=[c for c in cases if c['site']['role']=='Primary crater case']
    rules=[]
    for name,lower in [('uniform-low',True),('uniform-high',False)]:
        counter=[c['site']['name'] for c in primary if ((c['baseline']['150']['ratio']>=1) if lower else (c['baseline']['150']['ratio']<=1))]
        rules.append({'id':name,'baseline_status':'Contradicted by this descriptive contrast' if counter else 'Consistent at baseline only',
                      'baseline_counterexamples':counter,'scope':'Observable rule; not a rejection of a physical remanence mechanism'})
    files=['scripts/data/build_pilot.py','src/marswind/pilot.py','research/pilot/protocol.json','research/pilot/sources.json',
           'research/data/atlas.json','research/data/water.json','research/data/paleomagnetism.json',
           'data/observations/raw/mola/megt90n000cb.img','data/observations/raw/mola/megt90n000cb.xml',
           'data/observations/raw/magnetic_field/Langlais2019.sh.gz','data/observations/raw/geology/units.json',
           'data/observations/raw/pilot/lagain_db.json.zip']
    data={'protocol':config,'cases':cases,'units':units,'numerical_checks':checks,'rule_tests':rules,
          'provenance':{p:sha(ROOT/p) for p in files},
          'software':{'numpy':np.__version__,'pyshtools':sh.__version__,'shapely':shapely.__version__},
          'status':'Regional descriptive sensitivity study completed. Physical histories remain unidentifiable; no origin selected.'}
    save('results.json',data)
    with (OUT/'contrasts.csv').open('w',newline='') as f:
        keys=['case','role','altitude_km','inside_R','outside_inner_R','outside_outer_R','radius_scale',
              'inside_nT','outside_nT','ratio','matched_ratio','common_support_fraction']
        writer=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');writer.writeheader()
        for c in cases:
            for v in c['sensitivity']:
                writer.writerow({'case':c['site']['name'],'role':c['site']['role'],
                    'outside_inner_R':v['outside_R'][0],'outside_outer_R':v['outside_R'][1],
                    **{k:v[k] for k in keys if k in v}})
    figure(data)
    print('Saved pilot results, contrasts and scientific figure',flush=True)


def figure(data):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'regional-pilot-v1'})
    fig,axes=plt.subplots(2,2,figsize=(13,9),layout='constrained')
    colors=['#bd613f','#465e7d','#917064'];cases=data['cases'];y=np.arange(len(cases))
    case_colors=['#b45c3f','#718dab','#c89a5b','#a27b9f','#887b6e']
    for j,h in enumerate(['130','150','400']):
        ratios=np.array([c['baseline'][h]['ratio'] for c in cases])
        lo=np.array([min(v['ratio'] for v in c['sensitivity'] if v['altitude_km']==int(h)) for c in cases])
        hi=np.array([max(v['ratio'] for v in c['sensitivity'] if v['altitude_km']==int(h)) for c in cases])
        axes[0,0].errorbar(ratios,y+(j-1)*.2,xerr=[ratios-lo,hi-ratios],fmt='o',ms=4,
                           color=colors[j],capsize=2,label=h+' km')
    axes[0,0].axvline(1,color='gray',ls='--');axes[0,0].set_yticks(y,[c['site']['name'] for c in cases])
    axes[0,0].invert_yaxis();axes[0,0].set(xlabel='Mean |B| inside / nearby ring',title='A. Geometry sensitivity, by altitude (not confidence intervals)')
    axes[0,0].legend(fontsize=9)
    for k,c in enumerate(cases):
        p=c['profiles']['150'];axes[0,1].plot([v['radius_R'] for v in p],[v['mean'] for v in p],label=c['site']['name'],color=case_colors[k])
    axes[0,1].axvline(1,color='gray',ls=':');axes[0,1].set(xlabel='Distance / catalog radius R',ylabel='Mean model |B| at 150 km (nT)',title='B. Radial orbital-field profiles')
    axes[0,1].legend(fontsize=8)
    for i,c in enumerate(cases):
        b=c['baseline']['150'];axes[1,0].scatter(b['ratio'],i,marker='o',color=colors[0],label='Unadjusted' if i==0 else None)
        if b['matched_ratio'] is not None:
            axes[1,0].scatter(b['matched_ratio'],i,marker='D',facecolors='none',edgecolors=colors[1],label='Common map units only' if i==0 else None)
        axes[1,0].text(.98,i,f"{b['common_support_fraction']:.0%}",transform=axes[1,0].get_yaxis_transform(),ha='right',va='center',fontsize=9)
    axes[1,0].set_yticks(y,[c['site']['name'] for c in cases]);axes[1,0].invert_yaxis();axes[1,0].axvline(1,color='gray',ls='--')
    axes[1,0].set(xlabel='Ratio at 150 km; right labels = retained inside area',xlim=(.1,2.1),title='C. Raw (dots) and common surface units (diamonds)')
    for k,c in enumerate(cases):
        m=c['morphology'];axes[1,1].plot(m['normalized_radius'],np.array(m['median_elevation_km'])-m['rim_km'],label=c['site']['name'],color=case_colors[k])
    axes[1,1].axvline(1,color='gray',ls=':');axes[1,1].axhline(0,color='gray',lw=.5)
    axes[1,1].set(xlabel='Distance / catalog radius R',ylabel='Median elevation relative to outer band (km)',title='D. MOLA radial depth diagnostic; fixed catalog rims')
    fig.suptitle('Regional recording pilot · orbital field is not rock magnetization',fontsize=16)
    fig.supxlabel('Five literature-selected windows; Ladon is a flagged sensitivity case. No survey-controlled water effect or physical-history fit.',fontsize=10)
    for ax in axes.flat:ax.spines[['top','right']].set_visible(False)
    fig.savefig(OUT/'regional_pilot.png',dpi=180)
    fig.savefig(OUT/'regional_pilot.svg',metadata={'Date':None})
    plt.close(fig)
    p=OUT/'regional_pilot.svg';p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')


if __name__=='__main__':main()
