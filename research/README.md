# Research guide

**Start with [Where the evidence stands](STATE_OF_EVIDENCE.md).** It separates measured contrasts, conditional physical constraints and questions the current comparisons do not resolve.

This is an interdisciplinary investigation of the Martian dichotomy by Charlotte Crocicchia. The active work connects orbital magnetism, surface geology, gravity, crustal density, cooling, rock magnetism and distinct meteorite clocks. It does not claim a unique origin model or an exhaustive systematic literature review.

## A short reading route

1. [Current synthesis](STATE_OF_EVIDENCE.md): what we know and what remains ambiguous.
2. [Six discriminating tests](DISCRIMINATING_TESTS.md): the core questions, methods, numerical results and limits.
3. [Implementation audit](DISCRIMINATING_AUDIT.md): corrections to gravity, regularization, heat flux and reversal interpretation.
4. [Follow-up results](#follow-up-results): where the subsequent comparisons succeed, fail or add a constraint.
5. [Scientific method](../docs/SCIENTIFIC_METHOD.md) and [reproduction guide](../docs/DEVELOPMENT.md): how to read a verdict and rerun a calculation.

## The six core tests

| Test | Question | Main scope of the result |
| --- | --- | --- |
| 1 · Surface age and hemisphere | Which predictors retain skill outside their training regions? | Association remains; spatial support limits an age-controlled causal interpretation |
| 2 · Cooling and acquisition | When can the modeled crust cross carrier Curie temperatures? | Conditional acquisition histories; unresolved earlier records remain separate |
| 3 · Source strength | What magnetization matches the observations in the chosen geometry? | Cylinder-equivalent requirements, not a unique source inversion or mineral abundance |
| 4 · Slow cooling and reversals | How much signed record survives repeated inversions? | Strong median cancellation in the tested histories, not a universal retention bound |
| 5 · Orbital versus ground field | How well does a continued orbital model match two local measurements? | Local extrapolation discrepancies, not a universal correction factor |
| 6 · Gravity and crust | How does lateral density change inferred thickness? | Positive contrast across the declared scenarios, with a large range in magnitude |

[Technical report](DISCRIMINATING_TESTS.md) · [Protocol](discriminating/protocol.json) · [Sources](discriminating/sources.json) · [Manifest](discriminating/manifest.json) · [Audit controls](discriminating_audit/controls.json)

## Follow-up results

| Study | Outcome | Saved evidence |
| --- | --- | --- |
| [Arabia Terra prerequisites](ARABIA_PREFLIGHT.md) | Matching lacks the declared balance and spatial support; no magnetic significance test follows | [Protocol](followup/arabia/protocol.json) · [Summary](followup/arabia/summary.json) |
| [Boundary transects and the 23 northern cells](BOUNDARY_WALK.md) | Too few admissible blocks for the planned inference; the northern aggregate is geographically concentrated | [Protocol](followup/boundary_walk/protocol.json) · [Summary](followup/boundary_walk/summary.json) |
| [Source depth versus surface age](DEPTH_AGE.md) | No supported association under the declared sensitivity rule | [Protocol](followup/depth_age/protocol.json) · [Summary](followup/depth_age/summary.json) |
| [Density and remanence](DENSITY_REMANENCE.md) | Exact conditional material balances; feasibility depends on porosity, efficiency and compatible source volumes | [Protocol](followup/mixture/protocol.json) · [Summary](followup/mixture/summary.json) |
| [Rapidly cooled bodies](RAPID_BODIES.md) | Individual bodies can retain a strong record; stack polarities stay correlated through their shared field | [Protocol](followup/bodies/protocol.json) · [Correction controls](followup/bodies_audit/controls.json) |
| [Reversal identifiability](REVERSAL_IDENTIFIABILITY.md) | Distinct histories give identical synthetic fields when acquisition clocks are free; an ideal dated control breaks that ambiguity | [Protocol](followup/reversal/protocol.json) · [Summary](followup/reversal/summary.json) |

The [protocol status](NEXT_TEST_PROTOCOLS.md) separates executed stages from the unexecuted coupled thermal stack and observed-map reversal inference. The [roadmap](../docs/ROADMAP.md) identifies independent constraints that could improve future tests. No dated Martian reversal transition or novelty claim follows from these calculations.

## Five reading dossiers

| Dossier | Reading focus |
| --- | --- |
| [Scientific context](dossiers/science.md) | Interior, crust, observations and magnetic recording |
| [Literature method](dossiers/literature.md) | Reading depth, provenance, search coverage and source limitations |
| [Earlier experiments](dossiers/experiments.md) | Thermal, recording, regional and laboratory controls |
| [Interdisciplinary review](dossiers/interdisciplinary.md) | Connect physical processes while keeping clocks and sampled volumes distinct |
| [Audit and current evidence](dossiers/audit.md) | Corrections, current reports and limits on interpretation |

For foundations, read [paleomagnetism](PALEOMAGNETISM_FOUNDATIONS.md), [recording processes](RECORDING.md), [meteorites](METEORITES.md) and [water and alteration](WATER.md). The [interdisciplinary synthesis](INTERDISCIPLINARY_SYNTHESIS.md) connects the broader physical history; its [source ledger](INTERDISCIPLINARY_SOURCES.md) records what was actually consulted.

Earlier hypotheses, the [regional pilot](PILOT_STUDY.md), [physical studies](DICHOTOMY_PHYSICS.md) and [research programme](RESEARCH_PLAN.md) remain background. Their original scope and dates matter; current conclusions are in the synthesis above.

## Data, literature and exports

The [data guide](data/README.md) and [input manifest](data/manifest.json) describe the retained observation products. Full raw archives are separate from the saved browsing snapshot. Check the [source policy](../docs/SOURCE_POLICY.md) before obtaining or redistributing an input.

The September 27 catalogue contains **1,990 records**, **79 core records** and **72 consulted beyond metadata**, according to its [saved summary](summary.json). The current website filters out atmospheric topics: **1,823 records**, **76 core** and **70 consulted beyond metadata**. These are different selections, not conflicting totals. Neither count is a completed full-method audit. The interdisciplinary supplement overlaps this catalogue and must not be added to it.

[Complete BibTeX](library.bib) · [Core BibTeX](core.bib) · [RIS](library.ris) · [CSV](catalog.csv) · [JSON](catalog.json) · [Search log](search_log.json)

The catalogue includes articles, conference records, preprints, books, chapters and datasets. A record type does not establish peer review or relevance. Source-reading labels distinguish metadata, abstracts and selected sections; consulted material is not automatically reproduced methodology. Publisher PDFs and article figures are not redistributed as project-authored work.

## Use the interactive version

Follow the [installation instructions](../README.md#run-the-website) and [interface guide](../docs/USAGE.md). The four sections are Questions & answers, How we work, Results and Explore. GitHub provides the readable reports and saved artifacts; the interactive application runs locally.
