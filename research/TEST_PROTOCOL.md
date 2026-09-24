# Test 01 — A common thermal history for crust and magnetism

**Proposed analysis specification · 24 September 2026 · Not externally preregistered.**

Companion to the [working hypothesis](HYPOTHESES.md). The target is a falsifiable consistency test, not a vote among papers. The [first observational diagnostics](FIRST_RESULTS.md) have been executed; the joint acquisition/survival model comparison below remains a proposed study.

## Question and estimand

For each selected province and candidate carrier, which crustal growth and temperature histories permit the inferred source volume to acquire and retain enough coherent magnetization to reproduce regional orbital magnetic spectra?

Primary output: a set of feasible histories and recording-depth/time windows, with explicit dependence on nuisance parameters. Secondary output: whether a shared dynamo-history model predicts withheld magnetic observations adequately, and whether a hemispheric-field alternative improves those predictions enough to justify its extra freedom. This is not yet a probability distribution over impact versus convection origins.

## Inputs and independent information

| Input | Intended role | Dependency or limitation |
|---|---|---|
| [Langlais et al., 2019](https://doi.org/10.1029/2018JE005854) MGS/MAVEN field model and coefficients | Magnetic observations represented at a common radius and harmonic bandwidth | Model coefficients, regularization and measurement coverage affect spectra |
| [Gong & Wieczorek, 2021](https://doi.org/10.1029/2020JE006690) source-depth analysis; [author dataset](https://doi.org/10.5281/zenodo.4686358) | Reproduction target and starting geometry alternatives | Derived from the same field model: depth and field amplitude are not independent likelihood terms |
| [Wieczorek et al., 2022](https://doi.org/10.1029/2022JE007298) crustal ensembles, MOLA and geology | Crustal thickness, province definition, basin/volcanic masks | Density assumptions and common gravity information propagate into depth comparisons |
| [Thiriet et al., 2018](https://doi.org/10.1002/2017JE005431) thermal histories; [author result archive](https://figshare.com/projects/2017JE005431RR/29467) | Thermal benchmark, followed by updated crustal constraints | Hemispheric parameterization, polar elastic-thickness assumptions; endpoint temperatures alone cannot reconstruct a history |
| [Berne et al., 2026](https://doi.org/10.1038/s41586-026-10893-x) time-variable gravity | Present interior endpoint, including composition/melt alternatives | Do not impose its inferred temperature contrast as a directly observed ancient crust temperature; check shared gravity/systematic errors |
| Meteorite mineralogy, event ages and preservation tests in the [sample dossier](METEORITES.md) | Carrier alternatives and local chronological constraints | Unknown depth/provenance; paired specimens and common source terrains require grouping |

The [acquisition manifest](data/manifest.json) now records downloaded products and checksums. [Data conventions and licenses](data/README.md) document units, frames, resolution and permitted use. Field evaluation, depth-quality screening, four crustal grids and a present-day thermal gate have been computed. Full thermal histories, covariance and the joint fit below remain outstanding.

## Freeze the spatial comparison before interpreting it

Use geological provinces rather than an equatorial split. Begin with Cimmeria/Sirenum and northern controls selected for usable magnetic signal and data coverage. Document selection without tuning it to maximize hemispheric separation. Treat weak-signal locations as uninformative or upper limits where justified; excluding them limits the target population and must be reported.

Evaluate coefficients at one stated radius. Use the source paper's bandwidth for reproduction; then vary altitude, degree range, localization window, source geometry and masks. Use the intersection of supported bandwidths for cross-model comparisons. Do not compare surface downward-continuation maxima to orbital measurements as equivalent observations. Fit vector-field statistics or spectra; a signed mean can cancel genuine magnetization.

Publish a footprint and resolution table. Area weighting and spatial blocks are required; grid cells, overlapping windows and spherical-harmonic coefficients cannot be counted as independent observations. Hold out whole spatial blocks, large enough to account for localization and smoothing. Estimate their separation from the actual correlation structure rather than guessing an independence scale.

## Forward model and physical gates

The thermal calculation must follow time since formation, not just draw a present-day conductive geotherm. It requires crustal accretion/burial, heat production and redistribution, basal heat flux, conductivity, heat capacity and event heating. First reproduce a published benchmark. Specify when a one-dimensional column is inadequate for lateral intrusion or impact cooling.

For a thermoremanent branch, a schematic linear recording model is:

```text
M_today(x,z) = integral K_acquire(x,z,t; thermal history, carrier)
                      * R_survive(x,z,t -> today) * B_ancient(x,z,t) dt
B_predicted = G_geometry_and_altitude[M_today]
```

`K_acquire` is a time-distributed, unit-consistent recording response, not a fitted arbitrary weight at every time. `R_survive` represents subsequent relaxation, heating and shock damage. `B_ancient` is a vector, so polarity reversals and cooling duration can cancel bulk signals. `G` is the magnetic forward operator. This schematic expression is a model specification, not an implemented solver. Chemical and shock remanence require separate response models rather than silently sharing a thermoremanent kernel.

For each candidate history:

1. **Geometry:** magnetic material must lie in a permitted source volume. A thin-layer equivalent depth is not a magnetic bottom depth or Curie depth.
2. **Acquisition:** the material must form or cool through its blocking-temperature spectrum while a field is available. Curie temperatures alone do not specify blocking temperatures or retention over billions of years.
3. **Survival:** later thermal duration, mineral alteration and shocks must permit the proposed record to survive. Laboratory grain-size and relaxation properties matter.
4. **Amplitude and coherence:** surviving material and its vector-summed remanence must reproduce observed spectral power within errors. Thermal feasibility alone passes neither this gate nor the next one.
5. **Joint consistency:** the same histories must satisfy crustal and chronological constraints and the present interior endpoint. Do not fit a separate thermal history to each observable.

## Comparisons and outcomes fixed in advance

| Outcome | Permitted conclusion | Conclusion not permitted |
|---|---|---|
| Early inheritance fits held-out magnetic data and other constraints | An inherited archive remains viable in the tested regions | Impact or convection has been proven |
| Inheritance fails; later acquisition succeeds | Later recording is required within the tested parameterization | Every southern rock was remagnetized |
| Both recording histories work | Current constraints do not identify acquisition history | Choose the more attractive narrative |
| Shared-history field models fail, asymmetric variants predict withheld data better | Field geometry is a useful additional parameter under stated carrier/thermal assumptions | The ancient dynamo was necessarily hemispheric |
| No acquisition/survival window remains | Reject that parameterized thermal/carrier history | Increase field strength to rescue zero recording capacity |
| Missing uncertainty, no usable spectrum or incompatible resolutions | Not yet testable | Assign zero likelihood or “no magnetization” |

Declare residual statistics, measurement/model covariance and the predictive comparison rule after auditing data error products but before examining the main comparison. A numerical acceptance threshold is deliberately not invented without those errors. Compare identical data and nuisance-parameter budgets. Sensitivity to prior ranges must be reported; no posterior odds can be obtained by counting compatible papers.

## Dependencies, counterexamples and stopping conditions

Orbital source depths reuse magnetic coefficients. Crustal models reuse gravity and InSight constraints. Different meteorite stones can share a parent rock, pairing group, ejection event or reservoir. These dependencies belong in the covariance/hierarchical grouping or must be acknowledged by using one summary per family, not counted twice.

Published basin models show why weak fields can coexist with an active dynamo ([Steele et al., 2024](https://doi.org/10.1038/s41467-024-51092-4)). Their tested basin scales do not justify direct extrapolation to Borealis. Use them to verify cancellation physics before changing scale. Surface mineral maps and meteorites cannot silently fix unobserved deep carrier abundance.

Abandon the recording-first baseline for the tested regions if no physically allowed carrier/history ensemble fits the joint constraints, or if success requires unconstrained per-region adjustments that eliminate predictive power. Do not claim its survival if only arbitrary mixtures work. If the field and recording kernels remain unidentifiable, publish that result and identify which contextualized sample age, magnetic depth constraint or mineral measurement would discriminate them.

## Deliverables and present status

- Source/version manifest and a table separating direct measurements from derived inversions.
- Reproduced magnetic/thermal benchmarks with resolution and covariance checks.
- Depth–time feasibility diagrams for each carrier/history family, including rejected histories.
- Withheld-region predictions and sensitivity to field geometry, dynamo intervals and alteration.
- A conclusion that states which causal links are constrained and which origin triggers remain indistinguishable.

**Current status: initial acquisitions and five exploratory diagnostics completed; joint time-dependent inference not implemented.** See [completed results](FIRST_RESULTS.md). This protocol is not a claim that a new joint planetary model has been validated.
