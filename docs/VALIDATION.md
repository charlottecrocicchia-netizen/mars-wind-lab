# Validation

Locally checked with Python 3.14, gfortran 15.1 and MCD 6.1 on macOS. Exact Python dependencies are in `requirements-lock.txt`. Numerical tests do not replace independent observational validation.

## Numerical checks

Run `python -m pytest -q`. The current suite contains 24 cases: 17 checks independent of external scientific data and 7 optional integration checks requiring the local MCD installation (including an optional archive check).

- Sound speed, invalid thermodynamic states and four cardinal projections.
- Known shear on a nonuniform geometric grid and SI conversion.
- Spherical area integration of sin²(latitude), including missing values.
- Local solar time periodicity and the distinction between simultaneous and fixed-local-hour maps.
- Analytic eigenfrequencies of a uniform rigid column, full uniform-flow Doppler shift and grid refinement.
- Opposite-direction symmetry, zero wind, seasonal compensation and identical-state controls.
- Exponential density: exact scale height, wavelength and linear period scaling on a nonuniform grid.
- Missing-data blocks: density derivatives never span a gap.
- Invalid grids, nonfinite periods, invalid coordinates and insufficient layer thickness.
- MCD seasonal periodicity, equation of state, terrain masking and consistent map/profile fields.
- API responses, NetCDF reopening, CSV metadata and PNG signature.
- Real MCD columns, reverse-direction symmetry and English study notes with reproducible parameters.
- Optional archive shapes, radial boundaries and normalization diagnostics.

An independent reference distributed with MCD, `REF_OUTPUT_K9`, is sampled at 150 km, 5° E, 15° N, Ls≈97.9° and local time≈7.47 h. Reference values include p≈4.79×10⁻⁶ Pa, T≈193 K, u≈−306 m/s and v≈−79.9 m/s. The adapter agrees within 0.5%; rounded reference timestamps do not support a bit-for-bit claim.

The GitHub workflow runs analytic/API validation on Python 3.11 and 3.14 without MCD or internship archives. It does not claim to validate the external data or Fortran sampler in CI.

## Interface checks

The guided experiments are checked in the local browser, including parameter-change warnings, identical-season controls, reference-period changes, direction reversal and transfer to the explorer. Atlas and advanced views retain their physical conventions and explicit limitations.

Plotly is served locally; its cloud-share button is removed. Study notes and plots are local downloads. Public repository publication does not expose the local application server.

## Reproducible examples

`python scripts/illustrate_experiments.py` creates the three-panel overview and English study notes. It requires MCD but not the archives. `python scripts/reproduce.py` creates the extended atmospheric and archived-mode research bundle, requiring both external sources.

The reduced-model default case has a grid-frequency difference below 0.1% between 101 and 201 samples for its six modes. This checks discretization sensitivity within that formulation, not boundary conditions or the full propagation model.

There is no TWINS validation, SEIS inversion, complete GSH coupling matrix or recalculation of the original global modes yet. See [Scientific method](SCIENTIFIC_METHOD.md) for interpretation and [Research directions](ROADMAP.md) for proposed development.
