# Development and reproduction

Start with the [repository overview](../README.md) to install and run the local research website. All commands below run from the repository root with the virtual environment activated.

## Run the checks

Install the development dependencies. The observation extras support the scientific data checks; they are not required just to browse the saved site.

```bash
python -m pip install -e '.[test,research,observations]'
python -m pytest -q -m 'not integration'
node --test tests/*.test.mjs
python scripts/check_documentation.py
```

The JavaScript checks require Node.js; CI uses Node.js 22. [GitHub Actions](../.github/workflows/tests.yml) runs the Python checks on Python 3.11 and 3.14, plus browser-data and repository-documentation link checks. These validate implementations and data relationships, not a particular physical explanation for Mars.

## Choose the operation you need

| Operation | Inputs needed beyond a fresh checkout | Effect |
| --- | --- | --- |
| Browse the website | Base Python dependencies | Serves the saved research snapshot |
| Run the standard checks | Test and observation extras; Node.js for JS | Analytic, synthetic, data and route checks; no MCD |
| Render pages | Research extras | Reuses saved results; does not rerun science |
| Six-test numerical build | Permitted local magnetic, thermal and crustal archives; gravity/shape coefficients | Recalculates the six-test outputs |
| Arabia preflight | The boundary file named in its protocol, outside Git | Recalculates geometry and support diagnostics |
| Boundary transects | Permitted local coefficient, geological and boundary inputs listed in the frozen protocol | Recalculates the declared spatial comparison |
| Depth–age, mixture, bodies, reversal | Their saved project inputs and Python dependencies | Recalculates the respective follow-up |

Use a separate working copy when reproducing a saved scientific run: builders overwrite their output directories. Some older builders, including depth–age, also write a fresh declaration/run timestamp; retain the published protocol and manifest when comparing runs. The body and reversal builders read their preserved protocols. A run timestamp is not an external preregistration.

## Regenerate the saved site artifacts

For editorial and navigation changes only, reuse the saved numerical outputs:

```bash
python scripts/research/render_site.py
python scripts/research/render_docs.py
```

`render_site.py` writes the four main pages and five reading dossiers, then synchronizes navigation and context on preserved secondary pages. `reading_collection.py` assigns each original note to one dossier. Dossier prose lives in `research/dossiers/`; follow-up designs and execution status live in `research/NEXT_TEST_PROTOCOLS.md`. `render_docs.py` preserves each original reading URL and labels archive notes separately from current technical references. `site_links.py` translates portable Markdown links into local page routes; documents without a site page open on GitHub. Run these two renderers last after regenerating older workshops.

The following sequence also rebuilds numerical experiments. Most steps reuse saved inputs; the discriminating build may fetch its documented gravity and shape coefficients if they are absent from the external cache. Run the thermal and experiment builders before rendering their overview summaries.

```bash
python scripts/research/export_comparison.py
python scripts/research/render_dynamo.py
python scripts/research/render_docs.py
python scripts/research/render_pilot.py
python scripts/thermal/build.py
python scripts/experiments/build.py
python scripts/physics/build.py
python scripts/research/render_physics.py
python scripts/discriminating/build.py
python scripts/research/render_overview.py
python scripts/research/render_docs.py
```

`scripts/discriminating/build.py` reproduces the six discriminating tests (the corrected saved run took about 18 minutes; `--quick` runs a smaller smoke test whose outputs overwrite the same directory and must not replace the report dataset). It needs the observation extras plus the GMM-3 gravity and MOLA shape coefficients, which `pyshtools` downloads once from NASA PDS and Zenodo into its cache. `render_overview.py` draws the globe and then calls `render_site.py` for the four-page site. Numerical result values on the overview and results pages come from the saved JSON and CSV files.

The experiment builders rerun numerical calculations and may take time. Inspect generated diffs before committing. Runtime-version metadata, floating-point results and rendered figures can differ between environments.

The comparison JSON is curated by hand; its CSV exports and interactive views share that source. The overview and result cards read the saved experiment outputs. `render_overview.py` also renders the navigation globe from the authorized MOLA display grid.

The physical-studies builder reproduces crustal support, spherical-shell response, conditional boundary restoration and an Arai counterexample from small committed inputs. It needs no raw archive or network. Its optional `--extract` flag refreshes MOLA strips and hemisphere summaries from already permitted local products; this additionally requires the observation extras. See the [physical methods](../research/DICHOTOMY_PHYSICS.md), [source ledger](../research/physics/sources.json) and [input hashes](../research/physics/input_provenance.json). Source hashes describe the saved run, not a promise of bit-identical figure rendering across library versions.

Raw-data acquisition and full atlas reconstruction are separate workflows. Large source archives remain local. Consult the [source policy](SOURCE_POLICY.md), [data guide](../research/data/README.md) and [manifest](../research/data/manifest.json) before adding or reacquiring inputs. Permission to use a derived product does not establish redistribution rights for its source archive.

## Arabia Terra follow-up prerequisites

```bash
python scripts/followup/arabia_preflight.py
python -m pytest -q tests/test_spatial_matching.py
python scripts/research/render_site.py
python scripts/research/render_docs.py
```

This offline run uses the frozen `research/followup/arabia/protocol.json`, its attributed USGS polygon, and existing atlas/boundary products. It discards magnetic arrays before extracting covariates. Outputs contain the 23-cell coordinate ledger, eligibility masks, matching/balance diagnostics and block-dependence graphs. The 0.5° mask is geometric only; covariates remain at their native 2° grid. The primary feasibility screens fail, so no observed-field significance test or magnetic verdict is produced. See [the preflight report](../research/ARABIA_PREFLIGHT.md).

## Boundary transects and regional decomposition

```bash
python scripts/followup/boundary_walk.py
python scripts/followup/render_boundary_walk.py
python -m pytest -q tests/test_boundary_walk.py
python scripts/research/render_site.py
python scripts/research/render_docs.py
```

The numerical builder verifies the frozen input hashes, saves geometric eligibility and the null-calibration gate before reading observed magnetic values, then evaluates the degree-134 field directly at spherical transect endpoints. It also decomposes the previous 23-cell aggregate. The separate report renderer reads saved outputs without rerunning the calculation. Source coefficients and geological polygons must already be present under their existing documented permissions. Outputs and a manifest are in `research/followup/boundary_walk/`; the original Arabia and six-test numerical outputs are preserved. See [the boundary report](../research/BOUNDARY_WALK.md) for the failed support gate and conditional interpretation.

## Source depth versus surface age

```bash
python scripts/followup/depth_age.py
python -m pytest -q tests/test_depth_age.py
```

This uses the committed atlas, source-depth windows and saved six-test amplitude table. It writes window summaries, block-bootstrap correlations, figures and a report under `research/followup/depth_age/`. Preserve the original protocol timestamp as explained above. The [current report](../research/DEPTH_AGE.md) and [synthesis](../research/STATE_OF_EVIDENCE.md) distinguish a nonsupported association from evidence for excavation or the absence of resurfacing.

## Density–remanence follow-up

The density–remanence follow-up runs separately from the six-test build:

```bash
python scripts/followup/mixture.py
python scripts/followup/render_mixture.py
python -m pytest -q tests/test_mixture.py
python scripts/research/render_site.py
python scripts/research/render_docs.py
```

It verifies the frozen input hashes, solves exact mixture equations and attainable intervals, and saves the grid and prior-test illustrations under `research/followup/mixture/`. Existing cancellation penalties are applied once. The separate report renderer reuses those outputs. The [report](../research/DENSITY_REMANENCE.md) states the material and volume assumptions; this build neither reruns gravity inversion nor estimates local mineral abundance.

## Body cooling and reversal identifiability

```bash
python scripts/followup/rapid_bodies.py
python scripts/followup/reversal_identifiability.py
python -m pytest -q tests/test_rapid_bodies.py tests/test_reversal_identifiability.py
python scripts/research/render_docs.py
python scripts/research/render_site.py
```

The body builder reads and preserves its original protocol. It separates elapsed crossing times from actual blocking-band duration and adds the exact second moment for equal instantaneous recorders in a shared Poisson field. Original outputs are archived under `research/followup/bodies_audit/`; the [body report](../research/RAPID_BODIES.md) states the corrected interpretation.

The reversal builder verifies its frozen input hashes, creates only synthetic data and writes its report and manifest under `research/followup/reversal/`. A pathwise time-change counterexample closes the gate to observed-map inference in the declared nuisance class. The separate likelihood control uses independently calibrated thresholds and held-out dated signs. [The report](../research/REVERSAL_IDENTIFIABILITY.md) distinguishes this ideal control from available Mars observations. Neither script reruns the earlier gravity, regional support, depth–age or mixture calculations.

## Repository map

| Directory | Contents |
| --- | --- |
| `src/marswind/` | Python server, numerical models and analysis utilities |
| `web/` | Browser interface, charts and generated reading pages |
| `research/` | English research notes, protocols, source records and saved outputs |
| `scripts/` | Reproduction, export and page-generation commands |
| `tests/` | Analytic, numerical, data and browser-logic checks |
| `docs/` | Source policy, development instructions and visual credits |

## Refresh a running site

The server serves the working checkout. Restart it after changing Python server code. If a browser shows an older design, refresh while bypassing its cache: **Command+Shift+R** in Firefox on macOS.

HTML responses use `Cache-Control: no-store`. Styles, scripts and datasets revalidate before reuse; ETags allow unchanged assets to return an efficient `304` response. A successful GitHub Actions run does not restart a local server or refresh a browser tab.
