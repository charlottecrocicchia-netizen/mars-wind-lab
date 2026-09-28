# Martian dynamo: a programme of discriminating tests

**Assessment date: 27 September 2026.** [Explore the proposals](DYNAMO_TESTS.md) · [Machine-readable register](dynamo/tests.json) · [CSV export](dynamo/tests.csv)

The supplied research synthesis is a useful discovery map. This assessment converts its 30 proposals into original, conditional test designs. **Full discriminating tests remain open.** Five questions now have executed building blocks: recording and detection benchmarks, regional transfer checks and a candidate laboratory ledger. [Inspect the calculations and their limits](EXECUTED_EXPERIMENTS.md). They do not establish a dynamo history.

The register retains the supplied identifiers (T1–T8, D1–D11, G1–G6, C3a–C3c, C5 and H) so that each proposal can be traced. Those identifiers are not a ranking. The list is the coverage of the supplied matrix, not an exhaustive inventory of all possible Martian dynamos.

## Separate five questions

| Question | What belongs here | What must remain separate |
|---|---|---|
| When was the dynamo active? | Dated activity, permanent shutdown, interruptions | Formation age, alteration age and acquisition age |
| What could power it? | Thermal or compositional energy budgets | Material parameters, boundary conditions and hysteresis are not additional energy sources |
| What shape was its field? | Axial, hemispheric or more complex geometry | Polarity changes and the averaging window |
| What did the rocks preserve? | Thermal, chemical and shock acquisition or removal | Source mineral abundance, burial and observation resolution |
| What does the present interior constrain? | An endpoint for evolution calculations | Ancient core structure and ancient core–mantle heat flow |

These dimensions can coexist. For example, a thermal dynamo may reverse while different regions acquire and later alter their remanence. Counting papers or cells in this register cannot provide independent votes for or against such a combined history.

## Critical corrections

### A null field does not identify an extinct dynamo

A non-detection is informative only relative to a model’s predicted detectable signal. Cancellation, source depletion, later alteration, burial and resolution must be included before rejecting activity. Steele et al. (2024) model cancellation during basin cooling; the amplitude and low-altitude structure depend on recording assumptions. A flat transect alone cannot establish permanent shutdown. [Primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11316139/)

A useful test must first inject the competing predicted signals into the measurement model and determine which would have been recovered. A null observation can then disfavor a specified model that reliably predicts a detectable signal. It cannot eliminate every possible active dynamo history.

### Conductivity does not impose a universal shutdown date

Hsieh et al. (2024) extrapolate solid-alloy measurements to liquid-core conditions and couple conductivity to thermal evolution. The discussion around Fig. 4 includes modeled lifetimes of roughly 0.9 and 1.1 billion years elapsed for particular parameter choices; mantle rheology matters too. The supplied report’s categorical exclusion of activity at 3.7 Ga is not established by the inspected passages. Do not convert an elapsed model time into an age before present without specifying the start age. This assessment has not rerun the authors’ model. [Author-hosted primary article](https://www.jsg.utexas.edu/lin/files/HsiehMarsDynamoFeSSciAd2024.pdf)

### Stable dynamo and absent dynamo are different assumptions

The publisher-supplied abstract of Steele et al. (2025) evaluates basin-source depletion under a **non-reversing dynamo** and finds that the resulting fields can remain too strong. The supplied synthesis describes this condition as an absence of dynamo activity, which changes the argument. The study motivates testing reversing or intermittent histories; its preferred reversal rate remains model dependent. **Only the abstract has been assessed here**, not the full numerical method. [Article](https://doi.org/10.1029/2025JE009173) · [Publisher metadata and abstract through Crossref](https://api.crossref.org/works/10.1029/2025JE009173)

### Axial geometry does not mean constant polarity

Axial geometry describes orientation relative to the rotation axis. It does not specify whether polarity reverses. In a comparison, allow geometry and polarity history to vary independently. Do not reject an axial-field hypothesis merely because different dated components have opposed directions.

Yan et al. (2025) also illustrate why the recording window matters: selected finite-time averages and averages across many reversals need not have the same amplitude or hemispheric contrast. Some modeled regimes do not reverse. Neither “all hemispheric dynamos reverse” nor a universal inverse relation between cooling duration and hemisphericity follows from the selected results inspected here. [Primary article](https://doi.org/10.1029/2024GL113926)

### Present structure does not date ancient structure

The proposed present-day inner core in Bi et al. (2025) does not, by itself, date nucleation or exclude an earlier full-sphere dynamo. Its correction notice changes a Methods citation and does not withdraw the seismic interpretation. [Article, abstract assessed](https://doi.org/10.1038/s41586-025-09361-9) · [Correction notice, read](https://www.nature.com/articles/s41586-025-09981-1)

Likewise, the present mantle asymmetry inferred by Berné et al. (2026) is an endpoint constraint for evolution models. It does not directly measure ancient core-boundary heat flow or establish a particular ancient demagnetization event. [Primary article, selected sections assessed](https://www.nature.com/articles/s41586-026-10893-x)

### Record origin and field origin are separate questions

“Primary” and “secondary” describe a remanence relative to geological events. They do not, by definition, determine whether the magnetizing field came from a global dynamo or nearby crust. Each interpretation needs carrier evidence, event timing, and a bound on the local field. A measured equivalent magnetic source depth is also distinct from layer thickness or a Curie-depth calculation. The relevant source leads and outstanding checks remain explicit in C3a–C5; no new laboratory result is claimed.

## Next calculations

**Progress update:** the first implementation is now available in [Executed experiments](EXECUTED_EXPERIMENTS.md). The roadmap below distinguishes those initial benchmarks from the still-missing calibrated physics and geological inference.

### 1. Connect a recording model to the thermal histories

**Question:** can different field histories leave an indistinguishable remanence under the same recording conditions?

Start with a controlled synthetic benchmark. Specify one acquisition kernel, one source geometry and the same field amplitude convention for all cases. Compare a steady field, periodic or stochastic reversals, interruptions and permanent shutdown. Include random reversal phase and acquisition-window uncertainty. Keep the thermal and magnetic clocks aligned and clearly distinguish elapsed time from geological age.

The existing [thermal experiment](THERMAL_EXPERIMENT.md) supplies temperature histories and an ordering-temperature exclusion gate. It does **not** provide a physically calibrated acquisition kernel, blocking spectrum, grain relaxation, chemical remanence or shock response. A simple averaging kernel could be an explicit mathematical benchmark; it must not be labelled as a mineral survival calculation.

Before applying the model to Mars, verify limiting cases: constant field, zero field, instantaneous acquisition and cancellation across balanced opposite-polarity intervals. Require convergence where time discretization is used. Report signed components as well as magnitudes so that taking an absolute value too early cannot hide cancellation. If several histories remain indistinguishable, report that degeneracy instead of selecting a winner.

**Required deliverable:** original implementation, declared kernel and units, analytic checks, synthetic predictions with uncertainty, and an explicit list of mineral parameters still missing.

### 2. Test which differences survive observation

**Question:** would the competing remanence patterns be distinguishable by the available measurements?

Use the same magnetic source geometry and forward-field operator for every history. Compare predictions at common observation heights and resolution, with an explicit noise and sampling model. Inject known synthetic signals and test recovery before interpreting a null result. A one-dimensional conductive column cannot by itself predict an orbital magnetic map.

The [regional study](PILOT_STUDY.md) already demonstrates sensitivity to reference terrain and height in existing extracted products. It supplies context and sensitivity checks, not a calibrated magnetic inversion. Select evaluation regions or observations before fitting model parameters, then assess predictions on that held-out material. Reusing the same underlying field model at several heights does not create independent datasets.

**Required deliverable:** one common observation model, detection-power curves, parameter degeneracies and validation on observations excluded from fitting. Any new data import remains subject to source permissions.

### 3. Build a component-level chronology ledger

**Question:** which measurements securely constrain activity at distinct times?

For each candidate magnetic component, record the sample or region, mineral carrier, petrographic relation, demagnetization treatment, direction and intensity where available, uncertainty, handling history, and the event used to assign an age. Distinguish measured acquisition ages from ages inferred through association. Preserve dependencies between components from the same rock or event.

Begin with the ALH 84001 evidence trail, but first audit its figures, statistical tests and age associations against the primary article and supplements. The initial pass assessed its abstract; the subsequent experiment pass read selected primary carrier, direction and timing sections. Supplements and published component intervals still require a full audit. Do not import a table or repository merely because it is publicly visible. The first candidate-window ledger has now been computed independently from the existing permitted MagIC extract. It retains null acquisition ages; a published-component chronology audit remains unfinished. [Steele et al. (2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10957104/)

**Required deliverable:** traceable records with qualified ages and component origin, data-use status and unresolved alternatives; no duplicated measurements counted as independent dynamo episodes.

## What this does not implement

Core and mantle energy evolution, magnetohydrodynamic dynamos, inner-core growth, iron snow, fluid reactions and shock acquisition require additional equations, inputs and validation. They cannot be switched on by renaming the existing conductive scenarios. This register records those dependencies instead of presenting all thirty ideas as immediately executable options.

No probability ranking, fitted dynamo lifetime, measured reversal rate or newly established Martian origin is produced here. The proposed full tests are methodological priorities. New project benchmarks and reanalyses are documented separately and are not findings attributed to the source authors.

## Reading depth and reproducibility

The [register](dynamo/tests.json) is the authoritative source for the 30 proposals, their conditional tests, required inputs and limitations. Its 27 reference records distinguish selected sections, an abstract, a selected excerpt, a correction notice and unchecked leads from the supplied report. **Ten source records were consulted beyond the report in this assessment; seventeen remain leads.** A selected passage is not a complete methodological audit. D10 has no established supporting Mars-specific primary source in this assessment; that is not a claim that no such literature exists.

This targeted source trail is separate from the existing library catalog and does not change its counts or review-depth labels. Researcher biographies, mission funding claims, unverified personal statements and the report’s assertion that research communities do not cite one another are not adopted. The cited basin literature itself acknowledges earlier cancellation ideas.

The supplied report and publisher full texts are not redistributed. This release introduces original test designs, short attributed assessments and source links. It imports no external code or new numerical dataset, accesses no former internship material.

To regenerate the small committed outputs, without downloading data:

```bash
python scripts/research/render_dynamo.py
python scripts/research/render_docs.py
python scripts/research/render_dynamo.py --check
python -m pytest -q -m 'not integration'
```

The first command generates the webpage and CSV from the JSON register; the second renders this note and the reading navigation. Technical integrity checks verify references, execution-state labels and generated-output consistency. They do not validate the scientific hypotheses.
