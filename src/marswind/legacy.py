"""Read-only recovery of archived eigenfunctions; no claim of validated coupling."""
import hashlib
import json
import os
from pathlib import Path
import numpy as np

_settings_path=Path(__file__).resolve().parents[2]/'local_settings.json'
_settings=json.loads(_settings_path.read_text()) if _settings_path.exists() else {}
DEFAULT=Path(os.environ.get('MARS_LEGACY_ROOT',_settings.get('MARS_LEGACY_ROOT',Path.home()/'MarsWindData/NormalModes')))


def load_archived_modes(root=None,degree=500):
    root=Path(root or os.environ.get('MARS_LEGACY_ROOT',DEFAULT))
    folder=root/'marslmd_modes_200km_fbvire'
    if not folder.is_dir():
        raise RuntimeError('Internship archives missing: configure MARS_LEGACY_ROOT.')
    surface=3383.0  # Explicit in original plotALLmodes.m; also density discontinuity in files.
    modes=[]; manifest=[]
    for n in range(10):
        arrays=[]
        for component in ['ur','ui','vr','vi']:
            name=f'amp_{component}__{n}_{degree}_marslmd0'
            path=folder/name
            if not path.exists():raise RuntimeError(f'Missing eigenfunction: {name}')
            raw=path.read_bytes()
            manifest.append({'name':name,'sha256':hashlib.sha256(raw).hexdigest()})
            arrays.append(np.loadtxt(path))
        ur,ui,vr,vi=arrays
        r=ur[:,1];rho_sqrt=ur[:,2]
        if any(not np.array_equal(a[:,1],r) for a in arrays) or np.any(np.diff(r)<0):
            raise ValueError('Inconsistent archived radial coordinates.')
        U=ur[:,0]+1j*ui[:,0];V=vr[:,0]+1j*vi[:,0]
        # Preserve both samples at discontinuities when integrating full-planet inertia.
        r_m=r*1000
        squared_u=np.abs(U)**2;squared_v=np.abs(V)**2
        density_standard=r_m*r_m*(squared_u+degree*(degree+1)*squared_v)
        density_two=r_m*r_m*(squared_u+2*squared_v)
        norm_standard=np.trapezoid(density_standard,r_m)
        norm_two=np.trapezoid(density_two,r_m)
        # The atmospheric side of the r=3383 km discontinuity is its final duplicate.
        start=np.where(r==surface)[0][-1]
        sl=slice(start,None);alt=r[sl]-surface
        atm_integral=np.trapezoid(density_standard[sl],r_m[sl])
        low=alt<=10
        lower_integral=np.trapezoid(density_standard[sl][low],r_m[sl][low])
        def normal_shape(a):
            b=a[sl];scale=np.max(np.abs(b))
            return {'real':b.real/scale,'imag':b.imag/scale,'magnitude':np.abs(b)/scale}
        modes.append({'n':n,'altitude_km':alt,'U':normal_shape(U),'V':normal_shape(V),
                      'max_sqrt_rho_U':float(np.max(np.abs(U))),
                      'max_sqrt_rho_V':float(np.max(np.abs(V))),
                      'normalization_integral_ratio':float(norm_standard/norm_two),
                      'atmospheric_inertia_fraction':float(atm_integral/norm_standard),
                      'lower_10km_fraction_of_atmosphere':float(lower_integral/atm_integral),
                      'radial_grid_samples':len(r)})
    return {'degree':degree,'surface_radius_km':surface,'top_radius_km':3583.,'modes':modes,
            'provenance':{'kind':'Archived complex eigenfunctions; not recalculated by Mars Wind Lab',
                          'convention':'Columns interpreted following plotALLmodes.m. Shape amplitude separately normalised for display.',
                          'inertia_definition':'Integral r² (|sqrt(rho) U|² + ell(ell+1)|sqrt(rho) V|²) dr. Conditional on unscaled vector-harmonic V convention.',
                          'density_units':'Archived density scaling not certified as SI; only ratios reported.',
                          'files':manifest},
            'caution':'A maximum amplitude is not total modal energy. Inertia fractions do not predict surface excitation, detection or damping.'}
