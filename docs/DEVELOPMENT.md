# Development and reproduction

Start with the [repository overview](../README.md) to install and run the local research website. All commands below run from the repository root with the virtual environment activated.

## Run the checks

Install the development dependencies. The observation extras support the scientific data checks; they are not required just to browse the saved site.

```bash
python -m pip install -e '.[test,research,observations]'
python -m pytest -q -m 'not integration'
node --test tests/*.test.mjs
```

The JavaScript checks require Node.js; CI uses Node.js 22. [GitHub Actions](../.github/workflows/tests.yml) runs the Python checks on Python 3.11 and 3.14, plus the browser-data checks. These validate implementations and data relationships, not a particular physical explanation for Mars.

## Regenerate the saved site artifacts

These commands use committed inputs and do not download external datasets. Run the thermal and experiment builders before rendering their overview summaries.

```bash
python scripts/research/export_comparison.py
python scripts/research/render_dynamo.py
python scripts/research/render_docs.py
python scripts/research/render_pilot.py
python scripts/thermal/build.py
python scripts/experiments/build.py
python scripts/physics/build.py
python scripts/research/render_physics.py
python scripts/research/render_overview.py
```

The experiment builders rerun numerical calculations and may take time. Inspect generated diffs before committing. Runtime-version metadata, floating-point results and rendered figures can differ between environments.

The comparison JSON is curated by hand; its CSV exports and interactive views share that source. The overview and result cards read the saved experiment outputs. `render_overview.py` also renders the navigation globe from the authorized MOLA display grid.

The physical-studies builder reproduces crustal support, spherical-shell response, conditional boundary restoration and an Arai counterexample from small committed inputs. It needs no raw archive or network. Its optional `--extract` flag refreshes MOLA strips and hemisphere summaries from already permitted local products; this additionally requires the observation extras. See the [physical methods](../research/DICHOTOMY_PHYSICS.md), [source ledger](../research/physics/sources.json) and [input hashes](../research/physics/input_provenance.json). Source hashes describe the saved run, not a promise of bit-identical figure rendering across library versions.

Raw-data acquisition and full atlas reconstruction are separate workflows. Large source archives remain local. Consult the [source policy](SOURCE_POLICY.md), [data guide](../research/data/README.md) and [manifest](../research/data/manifest.json) before adding or reacquiring inputs. Permission to use a derived product does not establish redistribution rights for its source archive.

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
