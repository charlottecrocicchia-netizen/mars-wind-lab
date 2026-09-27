"""Reproduce recording, detection, map-transfer and lab diagnostics offline."""
import csv
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import platform
from collections import Counter

import numpy as np
import scipy
from scipy.special import ndtri
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt']='mars-research-experiments-v1'
import matplotlib.pyplot as plt

from marswind.thermal import Column, HeatPulse, solve, steady_temperature
from marswind.recording import (last_downward_crossings, include_pre_pulse_samples, record,
    cylinder_axis_operator, harmonic_attenuation, detection_power,
    recording_intervals, record_intervals, interval_temporal_gain)
from marswind.research_checks import (ridge_predict, longitude_folds, vector_from_direction,
    fit_demagnetization, line_sensitivity, axis_angle)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/experiments'
P = json.loads((OUT/'protocol.json').read_text())


def sha(name): return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def save(name, obj): (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n')
def csv_save(name, rows):
    with (OUT/name).open('w', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
def quant(a): return [float(x) for x in np.quantile(a, [.05,.5,.95], axis=0)]


def thermal_run(case, refinement=1):
    p=json.loads((ROOT/P['recording']['thermal_protocol']).read_text())
    column=Column(**p['column']); column=replace(column,cells=column.cells*refinement)
    q,h=p['basal_flux'],p['heat_production']
    history=solve(column,p['duration_myr'],p['step_myr']/refinement,
        lambda t:q['asymptote_w_m2']+(q['initial_w_m2']-q['asymptote_w_m2'])*np.exp(-t/q['decay_time_myr']),
        lambda t:h['initial_w_m3']*2**(-t/h['effective_half_life_myr']),
        steady_temperature(column,q['initial_w_m2'],h['initial_w_m3']),
        tuple(HeatPulse(**x) for x in case['pulses']),pulse_step_myr=p['pulse_step_myr']/refinement,pulse_window_myr=p['pulse_window_myr'])
    return history


def acquisition(history, band, count):
    p=P['recording']
    centers=np.arange(p['source_top_km']+p['layer_thickness_km']/2,p['source_bottom_km'],p['layer_thickness_km'])
    thresholds=273.15+band[0]+(np.arange(count)+.5)/count*(band[1]-band[0])
    crossing, states=[],[]
    for z in centers:
        index=int(np.argmin(abs(history.depth_m-z*1000)))
        assert abs(history.depth_m[index]-z*1000)<1e-8
        t,temp=include_pre_pulse_samples(history,index)
        times,status=last_downward_crossings(t,temp,thresholds)
        crossing.append(times);states.append(status)
    return np.array(crossing),np.array(states)


def exact_acquisition(history, band):
    p=P['recording'];kernels=[]
    centers=np.arange(p['source_top_km']+p['layer_thickness_km']/2,p['source_bottom_km'],p['layer_thickness_km'])
    for z in centers:
        index=int(np.argmin(abs(history.depth_m-z*1000)))
        assert abs(history.depth_m[index]-z*1000)<1e-8
        t,temp=include_pre_pulse_samples(history,index)
        kernels.append(recording_intervals(t,temp,np.array(band)+273.15))
    return kernels


def recording_experiments():
    p=P['recording']; thermal=json.loads((ROOT/p['thermal_protocol']).read_text())
    top=np.arange(p['source_top_km'],p['source_bottom_km'],p['layer_thickness_km'])
    operator=cylinder_axis_operator(p['radius_km'],top,top+p['layer_thickness_km'],p['height_km'])
    modes=[(kind,None) for kind in ['steady','absent','shutdown','intermittent']]+[(kind,d) for kind in ['periodic','poisson'] for d in p['chron_durations_myr']]
    periods=np.geomspace(1,4000,100)
    batches=[];replicates=[];refinements=[]
    for case in thermal['scenarios']:
        history=thermal_run(case)
        refined=thermal_run(case,2)
        for band in p['blocking_bands_c']:
            cross,state=acquisition(history,band,p['threshold_samples'])
            kernels=exact_acquisition(history,band)
            finekernels=exact_acquisition(refined,band)
            steady=record_intervals(kernels,'steady')
            unknown=np.array([k['unknown'] for k in kernels]);hot=np.array([k['hot'] for k in kernels])
            field_steady=p['reference_magnetization_a_m']*(operator@steady)
            unresolved_bound=p['reference_magnetization_a_m']*(operator@unknown)
            phase_errors=[];quadrature_errors=[]
            for chron in p['chron_durations_myr']:
                for phase in np.arange(16)/8:
                    a=record_intervals(kernels,'periodic',chron_myr=chron,phase=phase)
                    b=record_intervals(finekernels,'periodic',chron_myr=chron,phase=phase)
                    c=record(cross,state,'periodic',chron_myr=chron,phase=phase)[0]
                    phase_errors.append(float(np.max(abs(a-b))))
                    quadrature_errors.append(float(np.max(abs(a-c))))
            refinements.append({'thermal':case['id'],'band_c':band,'thermal_refinement_max_signed_fraction_difference':max(phase_errors),
                'midpoint_quadrature_max_difference_from_exact':max(quadrature_errors),
                'scope':'16 phases at each of 5, 20 and 100 Myr chron durations; exact piecewise-linear kernel integration is the production result. Thermal grid refinement is a numerical check, not geological uncertainty.'})
            gain=interval_temporal_gain(kernels,operator[2],periods)
            batch={'thermal':case['id'],'band_c':band,'known_acquired_fraction':float(steady.mean()),'unknown_initial_fraction':float(unknown.mean()),
                'hot_final_fraction':float(hot.mean()),'initial_field_bound_nt':unresolved_bound.tolist(),'period_myr':periods.tolist(),'temporal_gain':gain.tolist(),'histories':[]}
            for kind,chron in modes:
                n=p['ensemble_members'] if chron else 1
                fields=[];profiles=[];distances=[];scales=[]
                for member in range(n):
                    signed=record_intervals(kernels,kind,chron_myr=chron or 20,phase=2*member/n,
                        seed=P['seed']+member,shutdown_myr=p['shutdown_elapsed_myr'])
                    field=p['reference_magnetization_a_m']*(operator@signed)
                    denom=float(field_steady@field_steady)
                    scale=float(field@field_steady/denom) if denom>0 else 0.
                    distance=float(np.linalg.norm(field-scale*field_steady)/p['noise_sigma_nt'])
                    fields.append(field);profiles.append(signed);distances.append(distance);scales.append(scale)
                    replicates.append({'thermal':case['id'],'band_low_c':band[0],'band_high_c':band[1],'history':kind,'chron_myr':chron,
                        'member':member,'mean_signed_record':float(signed.mean()),**{f'known_field_{h}km_nt':float(v) for h,v in zip(p['height_km'],field)},
                        'best_signed_scale_of_steady':scale,'distance_to_scaled_steady_sigma':distance})
                field=np.array(fields)
                batch['histories'].append({'id':kind+(f'_{chron}' if chron else ''),'kind':kind,'chron_myr':chron,'members':n,
                    'signed_fraction_q05_q50_q95':quant(np.array(profiles).mean(axis=1)),
                    'absolute_field_q05_q50_q95_nt':{str(h):quant(abs(field[:,i])) for i,h in enumerate(p['height_km'])},
                    'known_template_detection_power_q05_q50_q95':quant(detection_power(np.linalg.norm(field,axis=1)/p['noise_sigma_nt'],p['test_false_alarm_probability'])),
                    'distance_to_scaled_steady_sigma_q05_q50_q95':quant(distances),'best_signed_scale_q05_q50_q95':quant(scales),
                    'median_signed_profile':np.median(profiles,axis=0).tolist()})
            batches.append(batch)
        del history,refined
    rng=np.random.default_rng(P['seed']); z=ndtri(1-p['test_false_alarm_probability']/2)
    injections=[]
    for snr in [0,.5,1,2,3,5,10]:
        estimated=float(np.mean(abs(rng.normal(snr,1,p['injection_trials']))>z))
        expected=float(detection_power(snr,p['test_false_alarm_probability']))
        injections.append({'snr':snr,'analytic_power':expected,'recovered_fraction':estimated,'trials':p['injection_trials'],
                           'monte_carlo_standard_error':float(np.sqrt(expected*(1-expected)/p['injection_trials']))})
        if abs(estimated-expected)>.025: raise RuntimeError('Detection simulation does not match analytic benchmark')
    # Absolute tolerance applies to signed unit recording, for the declared tested phases.
    if max(x['thermal_refinement_max_signed_fraction_difference'] for x in refinements)>.01:
        raise RuntimeError('Recording refinement exceeds 0.01 of unit magnetization; inspect the crossings')
    degrees=[1,10,30,60,100,134]
    result={'scope':p['assumptions'],'observation_scope':p['observation_scope'],'layer_centers_km':(top+p['layer_thickness_km']/2).tolist(),
        'heights_km':p['height_km'],'batches':batches,'refinement':refinements,'injection_recovery':injections,
        'harmonic_transfer':{'degrees':degrees,'amplitude_by_height':{str(h):harmonic_attenuation(degrees,3393.5,h).tolist() for h in p['height_km']}},
        'quantiles':'5th, median and 95th ensemble quantiles over specified phase/Poisson histories; not posterior or confidence intervals',
        'unknown_initial_record':'Known new contribution is a conditional lower-information calculation, not the total field. Unknown initial contribution can add or subtract up to the explicit bound. The bound assumes the reference amplitude also bounds prehistory.'}
    csv_save('recording_ensemble.csv',replicates);save('recording.json',result)
    return result


def cross_validation(x,y,w,lon,scheme,seed,offset=0):
    if scheme=='random':
        labels=np.random.default_rng(seed).permutation(len(y)) % P['maps']['folds']
        splits=[(labels!=i,labels==i) for i in range(P['maps']['folds'])]
    else: splits=list(longitude_folds(lon,P['maps']['folds'],P['maps']['longitude_buffer_deg'],offset))
    prediction=np.full(len(y),np.nan); baseline=prediction.copy();folds=[]
    for i,(train,test) in enumerate(splits):
        assert not np.any(train&test) and train.any() and test.any()
        prediction[test]=ridge_predict(x[train],y[train],w[train],x[test],P['maps']['ridge_penalty_mean_loss'])
        baseline[test]=np.average(y[train],weights=w[train])
        outside=((x[test]<x[train].min(axis=0))|(x[test]>x[train].max(axis=0))).any(axis=1) if x.shape[1] else np.zeros(test.sum(),bool)
        folds.append({'fold':i,'train_cells':int(train.sum()),'test_cells':int(test.sum()),'buffer_excluded_cells':int((~(train|test)).sum()),
                      'any_covariate_outside_training_range_fraction':float(np.average(outside,weights=w[test]))})
    if not np.isfinite(prediction).all(): raise RuntimeError('Incomplete out-of-fold predictions')
    mse=float(np.average((prediction-y)**2,weights=w)); base=float(np.average((baseline-y)**2,weights=w))
    return {'weighted_rmse_log1p_nt':float(np.sqrt(mse)),'skill_over_training_mean':1-mse/base,'folds':folds},prediction


def map_experiments():
    p=P['maps']; d=json.loads((ROOT/p['input']).read_text());lat,lon=np.meshgrid(d['latitude'],d['longitude'],indexing='ij')
    geo=np.array(d['geology']['grid']);elevation=np.array(d['topography_km'],dtype=float)
    valid=(abs(lat)<=p['latitude_limit_deg'])&(geo>=0)&np.isfinite(elevation)
    for a in p['altitude_km']:valid &= np.isfinite(np.array(d['magnetic_nT'][str(a)],dtype=float))
    for density in p['crust_density_kg_m3']:valid &= np.isfinite(np.array(d['crust_km'][str(density)],dtype=float))
    la,lo=np.deg2rad(lat[valid]),np.deg2rad(lon[valid]);w=np.cos(la);longitudes=lon[valid]
    x=np.cos(la)*np.cos(lo);y=np.cos(la)*np.sin(lo);z=np.sin(la)
    location=np.column_stack([x,y,z,x*y,x*z,y*z,x*x-y*y,3*z*z-1])
    units=np.eye(len(d['geology']['codes']))[geo[valid]];height=elevation[valid]
    rows=[];controls=[];oof_example=None
    for density in p['crust_density_kg_m3']:
        crust=np.array(d['crust_km'][str(density)])[valid]
        structure=np.column_stack([height,crust,height**2,crust**2,height*crust,units])
        designs={'mean':np.empty((len(w),0)),'location':location,'structure':structure,'combined':np.column_stack([location,structure])}
        for altitude in p['altitude_km']:
            response=np.log1p(np.array(d['magnetic_nT'][str(altitude)])[valid])
            for name,features in designs.items():
                for scheme,offset in [('random',0),*(('regional',v) for v in p['wedge_offsets_deg'])]:
                    result,prediction=cross_validation(features,response,w,longitudes,scheme,P['seed'],offset)
                    rows.append({'density_kg_m3':density,'altitude_km':altitude,'model':name,'split':scheme,'wedge_offset_deg':offset,**result})
                    if density==2900 and altitude==150 and name=='combined' and scheme=='regional' and offset==0:
                        oof_example={'latitude':lat[valid].tolist(),'longitude':longitudes.tolist(),'observed_log1p_nt':response.round(5).tolist(),
                                     'predicted_log1p_nt':prediction.round(5).tolist(),'residual_log1p_nt':(response-prediction).round(5).tolist()}
            if density==2900:
                for shift in p['negative_control_shifts_deg']:
                    shifted=np.roll(np.array(d['magnetic_nT'][str(altitude)]),shift//2,axis=1)
                    if not np.isfinite(shifted[valid]).all():raise RuntimeError('Missing shifted targets')
                    result,_=cross_validation(structure,np.log1p(shifted[valid]),w,longitudes,'regional',P['seed'])
                    controls.append({'altitude_km':altitude,'target_shift_deg':shift,**result})
    result={'scope':p['scope'],'valid_grid_cells':int(valid.sum()),'excluded_grid_cells':int((~valid).sum()),'latitude_limit_deg':p['latitude_limit_deg'],
            'area_weight':'cos(latitude); regular 2-degree centers within common finite-data support','results':rows,'longitude_shift_controls':controls,
            'interpretation':'A positive score improves on a training-only mean for the chosen split. A regional score measures transfer to omitted wedges. Neither a score nor its change identifies the cause of magnetization.',
            'oof_example':oof_example}
    save('maps.json',result)
    csv_save('map_validation.csv',[{k:v for k,v in r.items() if k!='folds'} for r in rows])
    return result


def laboratory_experiments():
    p=P['laboratory']; extended=json.loads((ROOT/p['inputs'][0]).read_text()); nwa=json.loads((ROOT/p['inputs'][1]).read_text())
    records=[];inventory=[];treatment_series=[]
    for dataset,data in [('ALH84001',extended['alh']),('NWA_control',nwa)]:
        for specimen in data['specimens']:
            sp=specimen['specimen']
            raw=[r for r in data['measurements'] if r['specimen']==sp]
            natural=[r for r in raw if (('NRM-Demag-' in r['measurement']) if dataset=='ALH84001' else ('LP-DIR-AF' in r['method_codes'])) and r.get('quality','g')=='g']
            inventory.append({'dataset':dataset,'specimen':sp,'parent_sample':specimen['sample'],'raw_measurements':len(raw),'eligible_natural_measurements':len(natural),
                'status':'Candidate-window diagnostics' if natural else 'No eligible natural-remanence sequence; laboratory-only specimen excluded',
                'component_age_ma':None,'age_status':'No direct age for an automatically selected fit','independence_group':specimen['sample'],
                'carrier_context':'Chromite–sulfide assemblage; contextual source interpretation' if dataset=='ALH84001' else 'Paired-stone contamination control; no ancient component asserted',
                'source':data['source'],'license':data['license']})
            for treatment,windows in [('AF',p['af_windows_mt']),('thermal',p['thermal_windows_c'])]:
                selected=[]
                for r in natural:
                    if treatment=='AF' and (dataset=='NWA_control' or 'Demag-AF' in r['measurement']):
                        value=float(r.get('treat_ac_field') or 0)*1000
                    elif treatment=='thermal' and 'Demag-TT' in r['measurement'] and r.get('treat_temp'):
                        value=float(r['treat_temp'])-273.15
                    else:continue
                    try: dec,inc,mom=[float(r[k]) for k in ['dir_dec','dir_inc','magn_moment']]
                    except (ValueError,KeyError):continue
                    if not np.isfinite([dec,inc,mom]).all() or mom<0:continue
                    selected.append((value,vector_from_direction([dec],[inc],[mom])[0],r['measurement'],r.get('meas_orient_phi','')))
                if not selected:continue
                if len({r[3] for r in selected})>1:raise RuntimeError('Changing archived orientation requires an explicit transform')
                levels=sorted({r[0] for r in selected})
                grouped=[([r for r in selected if r[0]==level]) for level in levels]
                mean=np.array([np.mean([r[1] for r in group],axis=0) for group in grouped]);last=np.array([g[-1][1] for g in grouped])
                treatment_series.append({'dataset':dataset,'specimen':sp,'treatment':treatment,'levels':levels,'mean_vectors_a_m2':mean.tolist(),
                    'repeat_counts':[len(g) for g in grouped]})
                for low,high in windows:
                    mask=(np.array(levels)>=low)&(np.array(levels)<=high)
                    measurements=[r[2] for r in selected if low<=r[0]<=high]
                    row={'dataset':dataset,'specimen':sp,'parent_sample':specimen['sample'],'treatment':treatment,'window_low':low,'window_high':high,
                         'unit':'mT' if treatment=='AF' else 'C','unique_treatments':int(mask.sum()),'measurement_count':len(measurements),
                         'measurement_ids':measurements,'component_age_ma':None,'frame':'Archived within-specimen frame; no cross-specimen geographic transformation',
                         'status':'Insufficient distinct treatments','source':data['source'],'license':data['license']}
                    if mask.sum()>=p['minimum_unique_treatments']:
                        try:
                            result=line_sensitivity(mean[mask]); a=fit_demagnetization(mean[mask]);b=fit_demagnetization(last[mask])
                            row.update(result);row['repeat_aggregation_axis_difference_deg']=axis_angle(a['axis'],b['axis']);row['status']='Candidate fit; origin and age unresolved'
                        except ValueError:row['status']='Degenerate vector sequence; no direction inferred'
                    records.append(row)
    context=[{'event':'Crystallization','older_ma':4121,'younger_ma':4061,'basis':'Reported 4091 ± 30 Ma rock age, not a component acquisition date'},
        {'event':'Carbonate formation','older_ma':3970,'younger_ma':3930,'basis':'Reported 3950 ± 20 Ma contextual event, not a sulfide-component date'},
        {'event':'Earlier inferred recording','older_ma':4100,'younger_ma':3950,'basis':'Geological association in the cited interpretation; not assigned to these candidate fits'},
        {'event':'Later inferred recording','older_ma':3900,'younger_ma':3800,'basis':'Favored event interpretation in the cited paper; alternative histories remain discussed'}]
    result={'scope':p['scope'],'inventory':inventory,'candidate_fits':records,'treatment_series':treatment_series,'alh_chronology_context':context,
        'chronology_source':'https://doi.org/10.1126/sciadv.ade9071','chronology_review':'Selected primary sections on carriers, directions and timing read; supplements and published component intervals not fully audited. Candidate fits do not reproduce the published component selection.',
        'nwa_control_source':'https://doi.org/10.1029/2022JE007464','missing_calibrations':['No common geographic coordinate transform','No paleointensity calibration','No automatically assigned geological component age','No component-origin classifier'],
        'mil_use':'MIL 03346 exports remain a comparison lead; undocumented moment/treatment units prevent pooling them into this SI workflow.'}
    save('laboratory.json',result)
    fields=['dataset','specimen','parent_sample','treatment','window_low','window_high','unit','unique_treatments','measurement_count','status','mad_deg','declination_deg','inclination_deg','anchored_axis_difference_deg','leave_one_treatment_out_max_axis_change_deg','repeat_aggregation_axis_difference_deg','component_age_ma','source','license']
    csv_save('component_ledger.csv',[{k:r.get(k) for k in fields} for r in records])
    return result


def figures(recording,maps,lab):
    fig,axs=plt.subplots(2,2,figsize=(12,9),constrained_layout=True)
    for b in recording['batches']:
        if b['thermal']=='reheating':axs[0,0].semilogx(b['period_myr'],b['temporal_gain'],label=f"{b['band_c'][0]}–{b['band_c'][1]} °C")
    axs[0,0].set(xlabel='Sinusoidal field period (Myr elapsed)',ylabel='Gain of known recording kernel',title='A  Temporal filtering · synthetic reheating',ylim=(0,1.05));axs[0,0].legend(fontsize=8)
    batch=next(b for b in recording['batches'] if b['thermal']=='reheating' and b['band_c']==[250,550])
    keep=[r for r in batch['histories'] if r['id'] in ['steady','shutdown','intermittent','periodic_20','poisson_20']]
    for i,r in enumerate(keep):
        q=r['absolute_field_q05_q50_q95_nt']['150'];axs[0,1].errorbar(i,q[1],yerr=[[q[1]-q[0]],[q[2]-q[1]]],fmt='o',color='#a0522d',capsize=4)
    axs[0,1].set(xticks=range(len(keep)),xticklabels=['Steady','Shutdown','Intermittent','Periodic','Poisson'],ylabel='Known contribution |Bz| at 150 km (nT)',title='B  Different histories · one recording model')
    axs[0,1].text(.04,.75,f"Initial-record bound: ±{batch['initial_field_bound_nt'][2]:.2f} nT\n10 A/m reference; 5–95% ensemble spread",transform=axs[0,1].transAxes,va='top',fontsize=8)
    models=['location','structure','combined']
    for j,split in enumerate(['random','regional']):
        subset=[next(r for r in maps['results'] if r['density_kg_m3']==2900 and r['altitude_km']==150 and r['model']==m and r['split']==split and r['wedge_offset_deg']==0) for m in models]
        axs[1,0].bar(np.arange(3)+(j-.5)*.35,[r['skill_over_training_mean'] for r in subset],width=.35,label=split)
    axs[1,0].axhline(0,color='k',lw=.7);axs[1,0].set(xticks=range(3),xticklabels=['Location','Structure','Combined'],ylabel='Skill relative to training-only mean',title='C  Transfer test · existing 150 km field model');axs[1,0].legend(fontsize=8)
    for name,color in [('ALH84001','#386c94'),('NWA_control','#b25938')]:
        valid=[r for r in lab['candidate_fits'] if r['dataset']==name and 'mad_deg' in r]
        axs[1,1].scatter([r['mad_deg'] for r in valid],[r['anchored_axis_difference_deg'] for r in valid],s=22,alpha=.65,label=name,c=color)
    axs[1,1].set(xlabel='Unanchored MAD (degrees)',ylabel='Change when forced through origin (degrees)',title='D  Line-fit sensitivity · dependent candidate windows');axs[1,1].legend(fontsize=8)
    fig.suptitle('Executed research diagnostics · benchmarks and reanalysis, not a dynamo discovery',fontsize=13)
    for ax in axs.ravel():ax.grid(alpha=.18)
    fig.savefig(OUT/'research_experiments.png',dpi=170)
    fig.savefig(OUT/'research_experiments.svg',metadata={'Date':None})
    svg=OUT/'research_experiments.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)


def main():
    recording=recording_experiments();print('Recording and detection complete',flush=True)
    maps=map_experiments();print('Map transfer checks complete',flush=True)
    lab=laboratory_experiments();print('Laboratory sensitivity checks complete',flush=True)
    figures(recording,maps,lab)
    names=['research/experiments/protocol.json','research/thermal/protocol.json','research/data/atlas.json','research/data/laboratory_extended.json','research/data/laboratory.json',
           'src/marswind/thermal.py','src/marswind/recording.py','src/marswind/research_checks.py','scripts/experiments/build.py','tests/test_research_experiments.py']
    manifest={'command':'python scripts/experiments/build.py','downloads_required':False,'input_and_code_sha256':{n:sha(n) for n in names},
        'output_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.name not in ['manifest.json','protocol.json'] and p.is_file()},
        'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__},
        'scope':'Independent implementations; synthetic recording/detection, predictive map diagnostics and candidate laboratory fits. No source code copied, no MCD, no private internship data.',
        'attribution':[
            {'input':'research/data/atlas.json','sources':'Langlais et al. 2019 magnetic model; Wieczorek et al. crustal models; NASA PDS MOLA; USGS SIM3292','terms':'Existing authorized extracted product; CC BY 4.0 model products and public government archives as detailed in research/data/manifest.json'},
            {'input':'research/data/laboratory_extended.json','source':'https://earthref.org/MagIC/19859','terms':'CC BY 4.0; Steele et al. (2023), https://doi.org/10.1126/sciadv.ade9071; independently reanalyzed candidate windows'},
            {'input':'research/data/laboratory.json','source':'https://earthref.org/MagIC/19658','terms':'CC BY 4.0; Vervelidou et al. (2023), https://doi.org/10.1029/2022JE007464; independently reanalyzed candidate windows'}]}
    save('manifest.json',manifest)
    print('All outputs saved; no downloads.',flush=True)

if __name__=='__main__':main()
