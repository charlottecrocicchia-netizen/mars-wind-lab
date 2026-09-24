# Validation

Locally checked with Python 3.14, gfortran 15.1 and MCD 6.1 on macOS. Exact Python dependencies are in `requirements-lock.txt`. Numerical tests do not replace independent observational validation.

## Numerical checks

Run `python -m pytest -q`. The current suite contains 53 cases: 46 checks that run without MCD or raw scientific downloads and 7 optional integration checks requiring the local MCD installation (including an optional archive check).

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

## Animation and video checks

A controlled synthetic sampler checks that seasonal sequences preserve altitude, hour and azimuth, while altitude sequences preserve season and hour. Tests check shared colour limits across all frames, signed symmetry and retention of missing samples. API tests reject unsupported sweep axes, heights and playback rates. A generated H.264 MP4 is decoded to verify its 1280×720 dimensions, chosen frame rate and complete 20-frame count.

Local browser checks cover automatic altitude updates, northern-season shortcuts, seasonal playback, a 20-frame altitude sweep, pause/scrub, field changes that invalidate a prepared sequence, MP4 download, and a guided experiment at Ls 123° over 80–180 km. A real MCD seasonal movie at 80 km was decoded as 24 frames at 2 fps (12 seconds, 1280×720). The dark interface was visually inspected in the desktop app browser.

## Version 0.4: playback feedback and research atlas

Sequence streaming is checked for every progress event, completion payload, preserved masked cells and explicit failure reporting. The MP4 test decodes the encoded movie and verifies dimensions, rate and frame count. Local browser checks exercised direct numeric altitude entry, preparation feedback, seasonal playback, pause and the inline MP4 player.

The literature checks cover DOI uniqueness, source-reading counts, core annotations, correction linkage, export record counts, exclusion of private abstracts and references between the local reading pages. These are catalog-integrity checks, **not validation of the scientific conclusions of the papers**. The research interface can load without a working MCD installation.

## Observation diagnostics

The observation tests verify an analytic axial dipole and its radial decay, spherical weighting against an analytic integral, local-surface temperature interpolation with no extrapolation, missing/negative source-depth handling, product integrity and pages available without MCD. The completed scientific calculations are documented separately in [First results](../research/FIRST_RESULTS.md); unit tests do not validate their planetary interpretation.

The revised workspace was checked in the local browser: persistent navigation, map-layer and altitude/density switches, crater selection, meteorite search, specimen switching, expandable test methods, bibliography search and browser Back within atmospheric views. Seasonal playback prepared 24 frames and advanced while preserving the shared color scale.

## Expanded meteorite and water evidence

Six additional checks protect distinct natural and laboratory remanence, preserved treatment labels and unverified units, upper/lower bounds and missing errors, separated mineral/event ages, coordinate wrapping and instrument unions, and reproducible occupancy/field summaries with code and input hashes. The ALH archive's coordinate placeholders are never treated as source locations.

Browser checks exercised MIL and ALH specimen selection, ALH thermal demagnetization, the exclusion of the appended MIL25 laboratory TRM, expandable directions, Lafayette's separate age table, mineral-class and instrument/background controls, and the new descriptive-overlap diagnostic. No component fitting, paleointensity replication, coverage-controlled mineral association or joint origin inference is claimed.


## Regional recording pilot — 24 September 2026

The complete local suite passes **53 tests**: 46 run without MCD and 7 require the configured atmospheric installation. Seven new pilot tests verify great-circle geometry and longitude wrapping, MOLA pixel registration and periodic interpolation, a known bowl's depth and datum invariance, composition-driven contrast reversal, missing common-unit support, scientific snapshot/provenance accounting, and all five study routes/downloads without MCD.

The saved regional build recomputes the full degree-134 magnetic model at three altitudes, runs 81 analysis settings for each of five windows, retains the Ladon catalog warning, and checks four direct field values against the rounded existing atlas. No p-values, confidence intervals or physical-history posteriors are manufactured from correlated grid nodes.

Browser checks exercise chapter navigation, region and altitude changes, the elevation layer, presence-only mineral overlays, the Schiaparelli common-support warning, and expandable MOLA profiles. Browser console errors were checked. Reproduction of the original paper's joint inversion is not claimed.
