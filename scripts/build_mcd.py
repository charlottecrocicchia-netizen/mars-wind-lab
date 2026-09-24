"""Compile our adapter against a separately installed MCD (no vendor edits)."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    settings_path = ROOT / 'local_settings.json'
    settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
    mcd = Path(os.environ.get('MCD_ROOT', settings.get('MCD_ROOT', Path.home() / 'MCD_6.1'))).resolve()
    source = mcd / 'mcd/MCD.F90'
    if not source.is_file():
        raise SystemExit('MCD.F90 absent. Set MCD_ROOT to your MCD 6.1 installation.')
    for binary in ('gfortran', 'nf-config'):
        if not shutil.which(binary):
            raise SystemExit(f'{binary} missing. macOS: brew install gcc netcdf-fortran')
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    flags = shlex.split(subprocess.check_output(['nf-config', '--fflags'], text=True))
    libs = shlex.split(subprocess.check_output(['nf-config', '--flibs'], text=True))
    if shutil.which('nc-config'):
        libs += shlex.split(subprocess.check_output(['nc-config', '--libs'], text=True))
    if shutil.which('xcrun'):
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        flags += ['-isysroot', sdk, '-L' + sdk + '/usr/lib']
    command = ['gfortran', '-O2', '-ffree-line-length-none', *flags, str(source),
               str(ROOT / 'native/sample_mcd.f90'), *libs, '-o', str(build / 'sample_mcd')]
    subprocess.run(command, cwd=build, check=True)
    manifest = {'mcd_root': str(mcd), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'adapter_sha256': hashlib.sha256((ROOT / 'native/sample_mcd.f90').read_bytes()).hexdigest(),
                'compiler': subprocess.check_output(['gfortran','--version'],text=True).splitlines()[0],
                'command': command}
    (build / 'mcd_build.json').write_text(json.dumps(manifest, indent=2))
    print('MCD adapter compiled:', build / 'sample_mcd')


if __name__ == '__main__':
    main()
