"""Batch official CALL_MCD execution with immutable, content-addressed cache."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
COLUMNS = ['pressure','density','temperature','u','v','w','temperature_rms','u_rms','v_rms','w_rms',
           'cp','gamma','gas_constant','radius','altitude_areoid','altitude_agl','orography','local_time']
UNITS = dict(zip(COLUMNS, ['Pa','kg m-3','K','m s-1','m s-1','m s-1','K','m s-1','m s-1','m s-1',
    'J kg-1 K-1','1','J kg-1 K-1','m','m','m','m','hour']))
LOCK = threading.Lock()


def installation():
    build = ROOT/'build/mcd_build.json'
    if not build.exists() or not (ROOT/'build/sample_mcd').exists():
        raise RuntimeError('Build the engine with python scripts/build_mcd.py.')
    manifest = json.loads(build.read_text())
    mcdroot = Path(os.environ.get('MCD_ROOT',manifest['mcd_root'])).resolve()
    data = mcdroot/'data'
    if not data.is_dir():
        raise RuntimeError('MCD data missing: configure MCD_ROOT.')
    # Changing a dataset invalidates cached results; SHA256 of the adapter/source identifies the code.
    files = sorted(data.rglob('*.nc'))
    signature = hashlib.sha256('\n'.join(f'{p.relative_to(data)}:{p.stat().st_size}:{p.stat().st_mtime_ns}' for p in files).encode()).hexdigest()
    return data, manifest, signature


def sample(points):
    """Input columns: geometric z m, lon E, lat N, Ls deg, local hour, scenario, zkey."""
    points = np.atleast_2d(np.asarray(points,dtype=float))
    if points.shape[1] != 7 or not np.isfinite(points).all():
        raise ValueError('Invalid MCD query.')
    if len(points)>60000:
        raise ValueError('Query exceeds 60,000 samples.')
    data, manifest, signature = installation()
    identity = json.dumps({'points': points.tolist(), 'source':manifest['source_sha256'],
                          'adapter':manifest['adapter_sha256'],'data':signature,'schema':1},sort_keys=True)
    key = hashlib.sha256(identity.encode()).hexdigest()
    cache = ROOT/'data/cache'
    cache.mkdir(parents=True,exist_ok=True)
    path = cache/f'{key}.npz'
    with LOCK:  # Fortran retains state; each subprocess is independent, requests are bounded.
        if path.exists():
            with np.load(path,allow_pickle=False) as saved:
                values=saved['values']
                created=str(saved['created'])
        else:
            with tempfile.TemporaryDirectory(prefix='marswind-') as folder:
                inp, out = Path(folder)/'points.txt', Path(folder)/'values.txt'
                with inp.open('w') as f:
                    f.write(f'{len(points)}\n')
                    np.savetxt(f,points,fmt='%.10g')
                result = subprocess.run([str(ROOT/'build/sample_mcd'),str(data)+'/',str(inp),str(out)],
                                        capture_output=True,text=True,timeout=150)
                if result.returncode or not out.exists():
                    raise RuntimeError('MCD failure: '+(result.stdout+result.stderr)[-1200:])
                values=np.loadtxt(out,ndmin=2)
                if values.shape!=(len(points),19):
                    raise RuntimeError('Incomplete MCD response: '+(result.stdout+result.stderr)[-800:])
                codes=values[:,0].astype(int)
                fatal=(codes!=0)&(codes!=17)
                if np.any(fatal):
                    raise RuntimeError(f'CALL_MCD error codes {np.unique(codes[fatal]).tolist()}')
                created=datetime.now(timezone.utc).isoformat()
                np.savez_compressed(path,values=values,created=created)
    fields={name:values[:,i+1].copy() for i,name in enumerate(COLUMNS)}
    # Areoid queries below GCM terrain must not appear as atmospheric samples.
    underground=(values[:,0]==17)|((points[:,6]==2)&(points[:,0]<fields['orography']))
    for name in COLUMNS[:13]:
        fields[name][underground]=np.nan
    for name in COLUMNS:
        fields[name][values[:,0]==17]=np.nan
    fields['local_time']=points[:,4].copy()
    provenance={'model':'Mars Climate Database 6.1','provider':'LMD / IPSL, Open University, Oxford, IAA',
                'method':'Official CALL_MCD; hireskey=0; perturkey=1; datekey=1',
                'source_sha256':manifest['source_sha256'],'adapter_sha256':manifest['adapter_sha256'],
                'data_inventory_fingerprint':signature,'cache_key':key,'computed_utc':created,
                'source_url':'https://www-mars.lmd.jussieu.fr/mars/access.html',
                'kind':'GCM climatology; not direct wind observations',
                'rms_note':'Day-to-day variability of the model; not observational error bars or a confidence interval.'}
    return fields,provenance
