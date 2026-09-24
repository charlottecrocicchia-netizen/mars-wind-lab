"""Controlled local comparisons, without trajectory or arrival-time claims."""
import numpy as np
from .analysis import evaluate

SOURCES = [
    {'title':'Ortiz et al. (2022), Autocorrelation Infrasound Interferometry on Mars',
     'url':'https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2021GL096225'},
    {'title':'Mars Climate Database 6.1 — documentation',
     'url':'https://www-mars.lmd.jussieu.fr/mars/info_web/index.html'},
]


def compare_columns(z_km, baseline, comparison, period_s):
    """Separate advection and thermodynamics at identical geometric coordinates.

    period_s is the reference rest-medium period: lambda_0 = c_0 * period_s.
    lambda_0/H_rho is a local scale diagnostic, not a sufficient ray criterion.
    """
    z=np.asarray(z_km,dtype=float)
    if z.ndim!=1 or len(z)<3 or not np.isfinite(z).all() or np.any(np.diff(z)<=0) or not np.isfinite(period_s) or period_s<=0:
        raise ValueError('A finite increasing altitude grid and positive finite period are required.')
    c=np.asarray(baseline['sound_speed'],float)
    w=np.asarray(baseline['along_wind'],float)
    rho=np.asarray(baseline['density'],float)
    c2=np.asarray(comparison['sound_speed'],float)
    w2=np.asarray(comparison['along_wind'],float)
    if any(a.shape!=z.shape for a in [c,w,rho,c2,w2]):
        raise ValueError('Profiles must share the same geometric altitude grid.')
    valid=np.isfinite(c)&np.isfinite(w)&np.isfinite(rho)&np.isfinite(c2)&np.isfinite(w2)&(c>0)&(c2>0)&(rho>0)
    if valid.sum()<3:
        raise ValueError('Not enough valid atmospheric samples in this layer.')
    # Never differentiate across an interior gap in a profile.
    scale=np.full_like(z,np.nan)
    indices=np.flatnonzero(valid)
    blocks=np.split(indices,np.where(np.diff(indices)>1)[0]+1)
    for b in blocks:
        if len(b)>=3:
            scale[b]=np.abs(np.gradient(np.log(rho[b]),z[b]*1000,edge_order=2))
    wavelength=c*period_s/1000
    epsilon=c*period_s*scale
    ratio=np.where(valid,100*w/c,np.nan)
    delta_w=w2-w
    delta_c=c2-c
    delta=delta_w+delta_c
    impact=int(np.nanargmax(np.abs(ratio)))
    change=int(np.nanargmax(np.where(valid,np.abs(delta),np.nan)))
    scale_point=int(np.nanargmax(epsilon)) if np.isfinite(epsilon).any() else None
    effective=c+w
    opposite=c-w
    fields={'sound_speed':c,'projected_wind':w,'effective_speed':effective,
            'opposite_effective_speed':opposite,'comparison_effective_speed':c2+w2,
            'wind_effect_pct':ratio,'season_wind_delta':delta_w,
            'season_thermodynamic_delta':delta_c,'season_total_delta':delta,
            'reference_wavelength_km':wavelength,'wavelength_density_scale_ratio':epsilon,
            'density_scale_km':np.divide(1,scale*1000,out=np.full_like(z,np.inf),where=scale>0)}
    for k in fields:
        fields[k]=np.where(valid,fields[k],np.nan)
    def point(i):
        return {'altitude_km':float(z[i]),**{k:float(v[i]) for k,v in fields.items()}}
    return {'altitude_km':z,'fields':fields,'impact_peak':point(impact),
            'season_peak':point(change),'scale_peak':point(scale_point) if scale_point is not None else None,
            'valid_samples':int(valid.sum()),'total_samples':len(z),
            'nonpositive_effective_samples':int(np.sum(valid&((effective<=0)|(opposite<=0)))),
            'selection_rule':'Largest absolute effect on the sampled, valid altitude grid; not a global extremum.'}


def experiment_product(lon=135.623,lat=4.502,ls=255,compare_ls=75,lt=12,azimuth=90,
                       z_min=20,z_max=160,period_s=100):
    if not 0<=z_min<z_max<=200 or z_max-z_min<5:
        raise ValueError('Choose a layer at least 5 km thick, within 0–200 km.')
    z=np.linspace(z_min,z_max,141)
    # Fixed local solar hour: an explicit controlled comparison at ONE location.
    a,pa=evaluate(z*1000,lon,lat,ls,lt,'local',azimuth)
    b,pb=evaluate(z*1000,lon,lat,compare_ls,lt,'local',azimuth)
    result=compare_columns(z,a,b,period_s)
    context={'longitude':lon,'latitude':lat,'Ls':ls,'comparison_Ls':compare_ls,
             'local_solar_hour':lt,'azimuth_deg':azimuth,'altitude_min_km':z_min,
             'altitude_max_km':z_max,'reference_period_s':period_s,
             'scenario':'MCD 6.1 climatology / average EUV',
             'time_convention':'Same local true solar hour at the selected location in both seasons',
             'height_convention':'Geometric kilometres above areoid'}
    result.update(context=context,provenance={'baseline':pa,'comparison':pb},sources=SOURCES,
        limits=[
            'A local column defines neither a source–receiver path, an arrival time, nor a SEIS detection.',
            'The no-wind comparison holds T, gamma and R fixed: it isolates advection algebraically without recomputing a wind-free climate.',
            'The thermodynamic contribution includes temperature, composition and heat capacities; it is not a temperature-only effect.',
            'The reference wavelength cT uses a period defined in the resting medium. Its ratio to the density scale is a local diagnostic, not a complete validation of geometric acoustics.',
            'Extrema refer to a grid of 141 altitudes. These climatological fields are not observations of a specific impact.'
        ])
    return result


def study_note(result,question='direction'):
    """Downloadable explanation, evidence and parameters from one result only."""
    c=result['context'];p=result['impact_peak'];s=result['season_peak'];q=result['scale_peak']
    titles={'direction':'How does propagation direction change the effect of wind?',
            'season':'Is the seasonal change driven by wind or thermodynamics?',
            'scale':'Is the reference wavelength small compared with the density scale?'}
    texts={
        'direction':f"At {p['altitude_km']:.1f} km, projected wind is {p['projected_wind']:+.2f} m/s. It changes effective sound speed by {p['wind_effect_pct']:+.2f}% relative to the resting medium ({p['sound_speed']:.2f} m/s). Effective speed in the opposite direction is {p['opposite_effective_speed']:.2f} m/s. This point maximizes |W_parallel/c| in the sampled layer.",
        'season':f"At {s['altitude_km']:.1f} km, the seasonal change B − A in effective sound speed is {s['season_total_delta']:+.2f} m/s: {s['season_wind_delta']:+.2f} m/s from wind and {s['season_thermodynamic_delta']:+.2f} m/s from thermodynamics. This point maximizes |delta c_eff| in the sampled layer.",
        'scale':f"The largest lambda_0/H_rho ratio is {q['wavelength_density_scale_ratio']:.2f} at {q['altitude_km']:.1f} km. The reference wavelength there is {q['reference_wavelength_km']:.2f} km." if q else 'The ratio cannot be evaluated at the valid samples.'}
    lines=['# Mars Wind Lab — study note','',titles[question],'','## Result','',texts[question],'','## Parameters','',
           f"- Location: {c['latitude']}° N, {c['longitude']}° E",
           f"- Season A: Ls={c['Ls']}°; season B: Ls={c['comparison_Ls']}°",
           f"- Local solar time: {c['local_solar_hour']} h",
           f"- Direction: {c['azimuth_deg']}° clockwise from north",
           f"- Layer: {c['altitude_min_km']}–{c['altitude_max_km']} km above areoid",
           f"- Reference period in the resting medium: {c['reference_period_s']} s",
           f"- Source: {c['scenario']}",'','## Limitations','',*['- '+x for x in result['limits']],'',
           f"Nonpositive effective speeds in either direction: {result['nonpositive_effective_samples']} sampled altitudes. These cases require a more careful propagation treatment; do not infer travel times from this column.",'','## Reproduce','']
    for name,pv in result['provenance'].items():
        lines.append(f"- {name}: cache `{pv['cache_key']}`; pipeline `{pv['pipeline_sha256']}`; MCD `{pv['source_sha256']}`")
    lines+=['','## Sources','',*['- ['+x['title']+']('+x['url']+')' for x in result['sources']]]
    return '\n'.join(lines)+'\n'
