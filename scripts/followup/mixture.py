"""Run the frozen density–remanence balance; never infer local density from it."""
import csv
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'mixture-v1'
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from marswind.mixture import Mixture

OUT = ROOT/'research/followup/mixture'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save_json(name, data):
    (OUT/name).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def save_csv(name, rows):
    with (OUT/name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def material(rm, rp, q, mc, coherence, protocol):
    return Mixture(matrix_density=rm, carrier_density=protocol['carrier_density_kg_m3'],
                   pore_density=rp, source_fraction=q, carrier_remanence=mc, coherence=coherence)


def candidate(m, rho, target):
    row = m.inverse(rho, target)
    if row['physical']:
        phi = max(0., row['porosity']); f = min(1., row['solid_carrier_fraction_in_source'])
        forward_density, forward_m = m.forward(f, phi)
        assert abs(forward_density-rho) < 1e-8
        assert abs(forward_m-target) < 1e-8
        source_rho = rho+(1-m.source_fraction)*row['bulk_carrier_fraction_in_source']*m.density_contrast
        row['carrier_mass_fraction_of_source'] = row['bulk_carrier_fraction_in_source']*m.carrier_density/source_rho
    else:
        row['carrier_mass_fraction_of_source'] = None
    row['within_phi_020_f_005'] = bool(row['physical'] and row['porosity'] <= .2+1e-12
                                     and row['solid_carrier_fraction_in_source'] <= .05+1e-12)
    return row


def grids(p):
    inverse, intervals = [], []
    for (hemisphere, density), offset, rm, rp, q in product(
            p['density_targets_kg_m3'].items(), p['density_offsets_in_quoted_error'],
            p['matrix_density_kg_m3'], p['pore_density_kg_m3'], p['source_volume_fraction_q']):
        rho = density['central']+offset*density['quoted_error']
        base = {'hemisphere': hemisphere, 'density_kg_m3': rho, 'density_error_offset': offset,
                'matrix_density_kg_m3': rm, 'pore_density_kg_m3': rp, 'source_volume_fraction': q}
        for m50, field, eta, c, target in product(p['remanence_at_50_microtesla_a_m'],
                p['acquisition_field_microtesla'], p['preservation_efficiency'], p['coherent_fraction'],
                p['net_source_targets_a_m']):
            mc = m50*field/50*eta
            m = material(rm, rp, q, mc, c, p)
            inverse.append({**base, 'carrier_trm_50_a_m': m50, 'field_microtesla': field,
                'preservation_efficiency': eta, 'effective_carrier_remanence_a_m': mc,
                'coherence': c, 'target_source_magnetization_a_m': target,
                **candidate(m, rho, target)})
        # Carrier-volume bounds factor out remanence and coherence exactly.
        m = material(rm, rp, q, 1., 1., p)
        for phimax, fmax in product(p['porosity_caps'], p['solid_carrier_caps']):
            attainable = m.attainable(rho, phimax, fmax)
            intervals.append({**base, 'porosity_cap': phimax, 'solid_carrier_cap': fmax,
                'density_feasible': attainable is not None,
                'porosity_low': attainable['porosity_low'] if attainable else None,
                'porosity_high': attainable['porosity_high'] if attainable else None,
                'bulk_carrier_low': attainable['bulk_carrier_low'] if attainable else None,
                'bulk_carrier_high': attainable['bulk_carrier_high'] if attainable else None})
    save_csv('inverse_grid.csv', inverse); save_csv('attainable_intervals.csv', intervals)
    return inverse, intervals


def applications(p):
    amplitude = json.loads((ROOT/'research/discriminating/amplitude.json').read_text())
    geometries = ['thin10_centered', 'thick20_centered', 'surface_to_depth',
                  'thick20_centered_after_poisson_cancellation_chron_0.67_myr']
    rows = []
    for case in amplitude['summary']:
        if case['geometry'] not in geometries: continue
        rho = p['density_targets_kg_m3'][case['region']]['central']
        for quantile, target in zip([.1,.5,.9], case['required_q10_q50_q90_a_m']):
            for mc, q in product(p['remanence_at_50_microtesla_a_m'], p['source_volume_fraction_q']):
                # This input may ALREADY include cancellation. Never penalize it again.
                m = material(2900, 0, q, mc, 1, p)
                rows.append({'hemisphere': case['region'], 'density_kg_m3': rho,
                    'geometry': case['geometry'], 'quantile': quantile, 'windows': case['windows'],
                    'target_a_m': target, 'carrier_remanence_a_m': mc, 'coherence_applied_here': 1,
                    'input_already_cancellation_corrected': 'after_poisson' in case['geometry'],
                    'source_volume_fraction': q, **candidate(m, rho, target)})
    save_csv('prior_test_scenarios.csv', rows)
    return rows


def baseline(p):
    rows = []
    for hemi, target in p['density_targets_kg_m3'].items():
        for rm, rp in product(p['matrix_density_kg_m3'], p['pore_density_kg_m3']):
            phi = (rm-target['central'])/(rm-rp)
            rows.append({'hemisphere': hemi, 'density_kg_m3': target['central'],
                'matrix_density_kg_m3': rm, 'pore_density_kg_m3': rp,
                'zero_carrier_porosity': phi, 'physical_zero_carrier': 0 <= phi < 1})
    save_csv('zero_carrier_baseline.csv', rows)
    return rows


def figures(p):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4), layout='constrained')
    f = np.linspace(0, .1, 201)
    for rm, color in zip([2600,2900,3100], ['#288b84','#285c9e','#b7692c']):
        for hemi, style in [('South','-'),('North','--')]:
            rho = p['density_targets_kg_m3'][hemi]['central']
            phi = 1-rho/(rm+f*(p['carrier_density_kg_m3']-rm))
            axes[0].plot(f*100, np.where(phi >= 0, phi*100, np.nan), style, color=color,
                         label=f'{hemi}, matrix {rm:,} kg/m³')
    axes[0].set(xlabel='Magnetite fraction of source solids (%)', ylabel='Porosity required by density (%)',
                title='Density constraint · empty pores, q = 1')
    axes[0].axhline(20, color='grey', lw=.8, ls=':'); axes[0].legend(fontsize=8)
    demands = np.geomspace(.1, 1000, 250)
    for c, color in [(1,'#285c9e'),(.02,'#b7692c')]:
        bounds = []
        for mc in p['remanence_at_50_microtesla_a_m']:
            m = material(2900,0,1,mc,c,p)
            candidates = [m.inverse(2492,float(v)) for v in demands]
            bounds.append([x['solid_carrier_fraction_in_source']*100 if x['physical'] else np.nan for x in candidates])
        axes[1].fill_between(demands, bounds[0], bounds[1], color=color, alpha=.23,
                            label=f'Coherent fraction {c:g}; carrier 5–10 kA/m')
        axes[1].plot(demands, bounds[0], color=color, lw=1)
        axes[1].plot(demands, bounds[1], color=color, lw=1)
    axes[1].axhline(5,color='grey',lw=.8,ls=':',label='Declared 5% solid-fraction screen')
    axes[1].axvline(4, color='grey', lw=.8, ls='--')
    axes[1].set(xscale='log',yscale='log',ylim=(.001,100),xlabel='Net source magnetization (A/m)',
                ylabel='Required magnetite fraction of solids (%)',
                title='Southern target · matrix 2,900 kg/m³, q = 1')
    axes[1].legend(fontsize=8,loc='upper left')
    for ax in axes: ax.grid(alpha=.18)
    fig.suptitle('Conditional material balance · compatibility is not a mineral-abundance measurement',fontsize=12)
    fig.savefig(OUT/'mixture.png',dpi=180)
    fig.savefig(OUT/'mixture.svg',metadata={'Date':None})
    plt.close(fig)


def main():
    p = json.loads((OUT/'protocol.json').read_text())
    for filename, expected in p['input_sha256'].items():
        assert sha(ROOT/filename) == expected, f'Frozen input changed: {filename}'
    inverse, intervals = grids(p)
    prior = applications(p); zero = baseline(p); figures(p)
    examples = [r for r in prior if r['quantile'] == .5 and r['source_volume_fraction'] == 1
                and r['geometry'] in ['thick20_centered','thick20_centered_after_poisson_cancellation_chron_0.67_myr']]
    summary = {'status':'Conditional material compatibility, not a local compositional inference',
        'executed_utc':datetime.now(timezone.utc).isoformat(),'protocol_sha256':sha(OUT/'protocol.json'),
        'inverse_cases':len(inverse),'attainable_intervals':len(intervals),'prior_scenarios':len(prior),
        'median_examples':examples,'zero_carrier_baseline':zero,
        'limits':'No geographical or depth match between the density constraint and local magnetic sources has been established. Feasible fractions of parameter grids are not probabilities.'}
    save_json('summary.json',summary)
    save_json('manifest.json',{'generated_by':'scripts/followup/mixture.py','input_sha256':p['input_sha256'],
        'protocol_sha256':sha(OUT/'protocol.json'),
        'code_sha256':{str(x.relative_to(ROOT)):sha(x) for x in [Path(__file__).resolve(),ROOT/'src/marswind/mixture.py']},
        'outputs_sha256':{x.name:sha(x) for x in sorted(OUT.iterdir()) if x.is_file() and x.name!='manifest.json'},
        'software':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__}})
    print(json.dumps({'inverse_cases':len(inverse),'examples':examples},indent=2))


if __name__ == '__main__': main()
