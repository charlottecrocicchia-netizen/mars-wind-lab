# Mars Wind Lab · Martian dichotomy research

A personal research project by **Charlotte Crocicchia**: understand the contrast between the northern lowlands and southern highlands by keeping observations, possible explanations and tests distinct.

The active website focuses on the dichotomy, crustal structure and the magnetic history of rocks. Its navigation has five entries: **Overview, Atlas, Results, Hypotheses, Sources**. The entire website, research notes and repository documentation are in English.

## Start locally

Python 3.11 or newer is sufficient to serve the committed research snapshot. No MCD installation, compilation or archive download is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test,research]'
python -m uvicorn marswind.server:app --app-dir src --host 127.0.0.1 --port 8765
```

Open **http://127.0.0.1:8765**. On an already configured Mac, `Launch Mars Wind.command` starts the same server. It is local; pushing the repository does not publish this server.

If a browser still shows an earlier design, reload once while bypassing its old cache: **Command+Shift+R in Firefox on macOS**. The server now sends HTML with `Cache-Control: no-store`; styles, scripts and datasets must revalidate before reuse, with ETags avoiding unnecessary downloads. GitHub Actions checks the repository; it does not refresh an already open browser tab.

## Follow the question

- **Hypotheses**: five common observations face four overlapping origin families. Open a cell for its requirement, proposed test and primary sources. This is a qualitative synthesis, not a probability ranking or a new model fit.
- **Overview and Results**: three computed findings have visual summaries linked to their experiments. The Results directory also collects the regional study, thermal model, dataset diagnostics and downloadable outputs.
- **Executed experiments**, inside Results: thermal acquisition kernels, exact synthetic magnetic fields, injection/recovery, 96 map-validation settings and a candidate laboratory component ledger. [Methods and qualified conclusions](research/EXECUTED_EXPERIMENTS.md) · local route `/research/experiments`.
- **Dynamo test programme**, inside Hypotheses: 30 proposals across five research questions, conditional tests, required inputs and explicit source-reading limits. These are planned discriminating tests, not executed dynamo models. [Assessment and next calculations](research/DYNAMO_TESTS.md) · local route `/research/dynamo`.
- **Chronology**, inside Hypotheses: formation, alteration, shock, magnetization and ejection remain distinct. Eleven selected events preserve ranges, reported uncertainties, approximate ages, bounds and unknown dates. [Method and exports](research/COMPARISON.md).
- **Atlas**: maps of relief, crust, magnetism and geology, 94 chronological sample records linked to 10 ejection groups and 16 proposed source craters, laboratory measurements and alteration evidence, with provenance.
- **Regional study**, inside Results: five guided chapters comparing regional magnetic contrasts. Reference terrain and observation altitude can change the result; the study does not select a unique origin. [Study and results](research/PILOT_STUDY.md) · [Other completed diagnostics](research/FIRST_RESULTS.md).
- **Thermal experiment**, inside Results: two original synthetic cooling histories, depth–time diagrams and an ordering-temperature exclusion gate. The solver is checked against analytic solutions and grid refinement; the histories are not fitted to Mars. [Method, sources and outputs](research/THERMAL_EXPERIMENT.md) · local route `/research/thermal`.
- **Sources**: 1,823 records in the active solid-planet selection, including 76 core references and 70 consulted beyond metadata. The historical 1,990-record catalog remains archived; atmosphere topics are excluded from the site search and filtered RIS exports. This is not a complete audit of the literature. [Search method](research/METHOD.md) · [September review](research/DICHOTOMY_REVIEW.md) · [RIS](research/library.ris) · [BibTeX](research/library.bib).

## Reproduce the small site artifacts

```bash
python scripts/research/export_comparison.py
python scripts/research/render_dynamo.py
python scripts/research/render_docs.py
python scripts/research/render_pilot.py
python scripts/thermal/build.py
python scripts/experiments/build.py
python scripts/research/render_overview.py
python -m pytest -q -m 'not integration'
node --test tests/*.test.mjs
```

The overview figures use the committed experiment outputs; `render_overview.py` also renders an original orthographic navigation globe from the permitted MOLA display grid. The meteorite explorer preserves preferred proposals, separately linked candidates, conditional alternatives and unlocated samples.

The comparison JSON is curated by hand; the CSV files and both interactive views use that same source. Regeneration does not download external data. The saved observations and study retain their existing [data notes](research/data/README.md), [manifest](research/data/manifest.json) and [study provenance](research/pilot/sources.json).

Large raw archives remain local and are not needed for browsing. Full reacquisition is deliberately blocked while some source permissions remain unresolved; see the [source policy](docs/SOURCE_POLICY.md). Existing extracted numerical products were expressly authorized by the project owner; that does not establish new redistribution rights for their source archives.

## Retired atmospheric interface

The atmospheric pages, browser scripts and HTTP calculation endpoints were removed on 27 September 2026 at the owner's request. The research server and desktop launcher do not import, build or call MCD. Old `/atmosphere` bookmarks return to the homepage.

Independently authored numerical modules, analytic tests and historical method notes remain in the repository as offline work. They are outside the active website. Any use of the external MCD software still requires an authorized installation and compliance with its terms; no MCD source or dataset is distributed here. Private internship/professor material is excluded and must not be restored.

## Credits and terms

Developed independently from published scientific methods and authorized data. This is not an official IPGP, NASA, JPL or MCD product. Research notes assembled with AI assistance retain reading-depth and uncertainty statements.

Original code uses the [MIT license](LICENSE). Plotly retains its [license](web/PLOTLY-LICENSE.txt). External datasets have separate licenses, including noncommercial terms where documented; the code license does not override them. Source links, attribution and [asset credits](docs/ASSETS.md) remain with the corresponding products.
