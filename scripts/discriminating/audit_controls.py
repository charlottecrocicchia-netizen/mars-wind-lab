"""Small independent controls for the 28 September discriminating-test audit.

These diagnose the inspected implementation; they do not rebuild the six tests
or provide replacement Martian estimates. Source hashes identify the snapshot.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
import pyshtools as sh

from marswind.recording import recording_intervals, record_intervals
from marswind.crustinversion import relief_potential, rereference, invert_moho, shell_potential
from marswind.crusthistory import HistoryParameters

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research' / 'discriminating_audit'


def main():
    result = {'scope': 'Synthetic controls and saved-run convergence inspection, not replacement Mars results.'}
    duration, chron = 800., .67
    kernel = recording_intervals([0, duration], [853.15, 703.15], [703.15, 853.15])
    periodic = [abs(record_intervals([kernel], 'periodic', chron_myr=chron, phase=2*i/16)[0]) for i in range(16)]
    stochastic = np.array([abs(record_intervals([kernel], 'poisson', chron_myr=chron, seed=i)[0]) for i in range(512)])
    result['reversal_control'] = {
        'kernel': 'Uniform acquisition over 800 Myr; identical kernel for both field models',
        'mean_chron_myr': chron, 'periodic_phases': 16, 'poisson_realizations': 512,
        'periodic_median_fraction': float(np.median(periodic)),
        'poisson_median_fraction': float(np.median(stochastic)),
        'poisson_q05_q95': np.quantile(stochastic, [.05, .95]).tolist(),
        'poisson_rms': float(np.sqrt(np.mean(stochastic**2))),
        'analytic_poisson_rms': float(np.sqrt(chron/duration-chron**2/(2*duration**2)*(1-np.exp(-2*duration/chron)))),
        'limit': 'Sensitivity demonstration; not a reproduction of Steele et al. or a rerun of the accepted thermal ensemble.',
    }
    mass, d, radius, r0, lmax, grid_lmax = 6.4171e23, 3340e3, 3390e3, 3396e3, 50, 63
    coeff = np.zeros((2, grid_lmax+1, grid_lmax+1))
    coeff[0, 50, 0] = 10.
    relief = sh.expand.MakeGridDH(coeff, sampling=2, lmax=grid_lmax)
    ba = rereference(relief_potential(relief, 482., d, mass, lmax, 1), d, r0)
    recovered, info = invert_moho(
        ba, r0, np.full(relief.shape, 2900.), 3382., d, mass, lmax, 1,
        filter_half_degree=50, iterations=100, tolerance_m=1e-8,
    )
    iterations, update = info['iterations'], info['last_change_m']
    recovered_coeff = sh.expand.SHExpandDH(recovered-d, sampling=2, lmax_calc=lmax)
    result['filter_control'] = {
        'input_degree': 50, 'true_relief_coefficient_m': 10.,
        'requested_filter_gain_at_degree_50': .5,
        'recovered_gain': float(recovered_coeff[0, 50, 0]/10),
        'iterations': iterations, 'last_change_m': update,
        'note': 'Before the 28 September correction the iteration undid the filter (gain 1 - (1 - taper)^(n + 1)); the regularised scheme now applies the filter to the whole linear solution.',
    }
    # Analytic exterior gravity of the reference shell: integrate rho_lm*r^(l+2) dr.
    # Degree 3, order 1 avoids the intentionally removed degree-2 zonal term.
    degree, order, density_coeff = 3, 1, 100.
    exact = (4*np.pi*density_coeff*(radius**(degree+3)-d**(degree+3))
             /(mass*(2*degree+1)*(degree+3)*r0**degree))
    coeff[:] = 0.
    coeff[0, 0, 0], coeff[0, degree, order] = 2800., density_coeff
    density = sh.expand.MakeGridDH(coeff, sampling=2, lmax=grid_lmax)
    current_relief_terms = (
        rereference(relief_potential(np.zeros_like(density), density, radius, mass, lmax, 1), radius, r0)
        + rereference(relief_potential(np.zeros_like(density), 3382.-density, d, mass, lmax, 1), d, r0)
    )
    corrected_shell = shell_potential(density, d, radius, mass, lmax, r0)
    corrected_coefficient = float((corrected_shell+current_relief_terms)[0, degree, order])
    assert np.isclose(corrected_coefficient, exact, rtol=1e-11, atol=0)
    result['reference_shell_control'] = {
        'degree': degree, 'order': order, 'shell_thickness_km': (radius-d)/1000,
        'density_harmonic_coefficient_kg_m3': density_coeff,
        'analytic_exterior_coefficient': float(exact),
        'relief_only_construction_coefficient': float(current_relief_terms[0, degree, order]),
        'corrected_shell_plus_relief_coefficient': corrected_coefficient,
        'relative_error_vs_analytic': abs(corrected_coefficient-exact)/abs(exact),
        'limit': 'The relief-only value documents the original omission. The corrected construction includes shell_potential and is checked against the independent radial integral.',
    }
    p = HistoryParameters(40, 3, .7, 4500, .27, 15, 60, 3, 220)
    result['basal_endpoint_control'] = {
        'declared_present_mw_m2': 15., 'early_mw_m2': 60., 'decay_gyr': 3.,
        'actual_at_4_5_gyr_mw_m2': float(p.basal_flux_w_m2(4500)*1000),
    }
    saved = json.loads((ROOT/'research/discriminating/crust_inversion.json').read_text())
    result['saved_inversion_convergence'] = [
        {k: row.get(k) for k in ['id', 'iterations', 'final_update_norm_m', 'last_change_m', 'converged', 'unfiltered_data_misfit_m']} for row in saved['scenarios']
    ]
    result['inspected_files_sha256'] = {
        name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in [
            'src/marswind/crustinversion.py', 'src/marswind/crusthistory.py',
            'src/marswind/recording.py', 'scripts/discriminating/build.py',
            'research/DISCRIMINATING_TESTS.md', 'research/discriminating/crust_inversion.json',
        ]
    }
    OUT.mkdir(exist_ok=True)
    (OUT/'controls.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
