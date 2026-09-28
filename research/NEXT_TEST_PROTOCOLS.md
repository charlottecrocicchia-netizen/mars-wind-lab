# Four follow-up protocols

Prepared and updated 28 September 2026. **Status: Arabia prerequisites, conditional density–remanence balances, single-body cooling and the synthetic reversal-identifiability prerequisite are executed. A coupled thermal stack and observed-map reversal inference are not executed.** The original proposals below remain visible with explicit execution notes. These extend the corrected six-test report. They are not externally preregistered, and no novelty is claimed. Exact input selections and numerical settings must be frozen in a machine-readable protocol before execution; exploratory choices must be recorded separately. The [Arabia preflight report](ARABIA_PREFLIGHT.md) contains prerequisite findings only, with no observed magnetic contrast or p-value.

## 1. Can reversal histories be distinguished from recording histories?

**Why.** The slow-cooling ensemble attenuates a frequently reversing field. A change in reversal rate is one possible explanation for strong old sources, alongside faster acquisition, different materials or different geometry. It is not forced by the two existing calculations. The basin rate in [Steele et al. (2024)](https://doi.org/10.1038/s41467-024-51092-4) is conditional on material and remagnetization assumptions. Selected results and discussion were consulted.

**How.** First compare stationary and piecewise-constant Poisson reversal rates using synthetic sources, the same cooling histories and explicit dynamo activity windows. Fit each family with the same allowed nuisance parameters and test recovery on withheld synthetic realizations. Only then compare radial-field correlation lengths and connected-sign areas between declared terrain groups at common altitudes and truncations. Map sign is an observable; it is not directly the ancient magnetization direction or a reversal clock.

**Expected output.** Recovery and confusion matrices, distributions of observable spatial summaries, and held-out predictive differences between model families. Record source emplacement and acquisition ages separately from mapped surface ages.

**Decision rule.** Evidence for a rate change requires predictive improvement over constant-rate models after recording geometry and material uncertainty are admitted, plus synthetic evidence that the change is identifiable. Otherwise report a constraint or non-identifiability, not a dated reversal history. A specific transition date requires independent source-age information.

**Limits and prior work.** [Voorhies (2008)](https://doi.org/10.1029/2007JE002928) already relates extensive magnetic sources, igneous production and long polarity chrons; its abstract was consulted. [Steele et al. (2023)](https://doi.org/10.1126/sciadv.ade9071) interpret ALH 84001 in terms of potentially reversed fields and impact histories; selected chronology and interpretation sections were consulted. This is not a measured global reversal-frequency curve. Source-scale inference must respect the approximately 160 km surface resolution reported by [Langlais et al. (2019)](https://doi.org/10.1029/2018JE005854), with further altitude filtering; selected model-resolution passages were consulted.

**Executed prerequisite.** The frozen follow-up tests a declared class of piecewise-affine acquisition clocks. A pathwise counterexample makes a changing rate and a constant rate observationally identical, including two-altitude synthetic fields. An independently calibrated, ideal dated-sign likelihood control succeeds; freeing its acquisition spacings restores the likelihood ridge. This establishes failure of global identifiability in that class, not universal impossibility under all coupled physical models. The original broader comparison of real correlation lengths and terrain groups is not executed because this gate fails.

**Reproduce.** Run `python scripts/followup/reversal_identifiability.py`. The [report](REVERSAL_IDENTIFIABILITY.md) links the frozen protocol, equality checks, held-out recovery and classification tables, source ledger and manifest under `research/followup/reversal/`.

## 2. Does Arabia Terra contradict a specified preservation model?

**Why.** A matched regional comparison can challenge an age-and-structure predictor. It cannot falsify every possible archive mechanism. The 23 northern Early Noachian cells in Test 1 must first be geolocated; they are not automatically an Arabia Terra sample.

**How.** Declare an Arabia Terra polygon and eligible control regions before inspecting magnetic outcomes. Match geological epoch, elevation, crustal thickness and boundary distance, with density variants retained as sensitivity cases. Use the 0.5° grid only for sampling geometry. Aggregate inference at spatial scales compatible with the field model, and report common support, rejected matches, pair balance and the number of spatial blocks.

The primary contrast is the paired difference in area-weighted `log(1 + |B| / 1 nT)` at 150 km. Repeat at 400 km as a dependent sensitivity check. Predeclare 300, 600 and 900 km block-size sensitivity cases, and 10,000 candidate block-label permutations with a recorded seed. Such permutations are interpretable only if matched blocks are plausibly exchangeable under the stated null; use simulated null maps to check calibration. Do not present arbitrary longitude shifts or individual-cell shuffles as valid significance tests. If overlap or exchangeability fails, retain a descriptive contrast and report why a calibrated test was unavailable.

**Expected output.** Region masks, matching balance, spatial support, paired contrasts and a calibrated null comparison where justified.

**Decision rule.** A robust residual weakens the declared age-and-structure preservation model. It does not choose between unmeasured alteration, mineralogy, acquisition history and a different ancient field.

**Limits and prior work.** [Evans et al. (2010)](https://doi.org/10.1029/2009JE003469) addresses erosion in Arabia Terra through geophysical constraints. Its abstract was consulted through the [MIT repository](https://dspace.mit.edu/entities/publication/317d9879-1029-4e3f-a496-fb8ea93e634c). The proposed “1–2 km measured erosion” must not become a fixed bound until its location, model assumptions and uncertainty are verified. Existing gravity-derived thickness is not an independent control for every density hypothesis.

**Reproduce.** Run `python scripts/followup/arabia_preflight.py` for the completed geometry, matching and block-dependence diagnostics in `research/followup/arabia/`. The primary overlap and block screens fail, so no observed-field contrast or permutation test has been run. The [saved protocol](followup/arabia/protocol.json) fixes the footprint, native 2° covariate grid, calipers, scenarios and screening rules before this matching. A separate 0.5° mask contains geometry only.

## 3. Can density and remanence fit one material mixture?

**Why.** A low bulk density and a magnetized source need a joint material model. Several A/m does not by itself imply a particular percentage of magnetite.

**How.** For a declared two-solid mixture with solid-volume magnetite fraction `f`, porosity `phi`, pore density `rho_p`, matrix density `rho_m` and magnetite density `rho_mag`, calculate:

```text
rho_bulk = (1 - phi) * ((1 - f)*rho_m + f*rho_mag) + phi*rho_p
M_bulk   = (1 - phi) * f * M_carrier * c
```

Here `M_carrier` is remanence per unit magnetic-mineral volume for a declared acquisition field and grain state, and `c` is a specified directional coherence factor. It is not saturation magnetization substituted for natural remanence. Extend the mixture if other magnetic carriers or a magnetic matrix matter.

**Expected output.** Feasible regions over mineral fraction, porosity, matrix density, remanence efficiency and coherence, using spatially and vertically compatible source and density scenarios.

**Decision rule.** Exclude only combinations that fail both constraints across their declared uncertainty ranges. Do not compare a local source requirement to a hemispheric average as though they described the same volume.

**Limits and prior work.** [AlHantoobi et al. (2021)](https://doi.org/10.1029/2020GL090379) explicitly studies compositional enhancement of Martian magnetization. Only indexed passages were consulted here; full material calibration remains to be checked. The conditional joint balance is now implemented; its novelty is unestablished. It uses the published single-domain magnetite TRM range from Dunlop & Arkani-Hamed (2005) while treating matrix density, porosity and source-volume correspondence as scenarios.

**Reproduce.** Run `python scripts/followup/mixture.py` and `python scripts/followup/render_mixture.py`. The [completed report](DENSITY_REMANENCE.md) links the frozen protocol, source ledger, exact feasible intervals, parameter grid and prior-test illustrations under `research/followup/mixture/`. Reported fractions are conditional mixture solutions, not measured mineral abundances.

## 4. Can rapidly cooled bodies retain a strong combined signal?

**Why.** The conductive-column ensemble does not represent individual sills or lava units. Rapid cooling may reduce within-body cancellation, while different bodies may still cancel each other.

**How.** Solve slab cooling for declared host temperatures, boundary conditions, diffusivities and blocking spectra. Use `h²/kappa` as a scale, not an exact blocking duration. Integrate each body's recording kernel against shared reversal realizations, then sum vector fields for the full source geometry at observation altitude. Body emplacement timing determines whether polarities are correlated; random signs are not assumed automatically.

**Expected output.** Retention distributions versus body thickness and chron statistics, followed by whole-stack orbital fields and magnetization requirements. Verify the thermal solver against an analytic slab solution before geological interpretation.

**Decision rule.** Report thickness ranges meeting a declared retention criterion under specified conditions. Do not infer a unique southern crustal architecture from that inequality alone.

**Limits and prior work.** Intrusion, cooling and magnetic-source architecture have a substantial literature, including [Ogawa and Manga (2007)](https://doi.org/10.1029/2007GL030565), whose indexed introduction and references were consulted. Its citations point to earlier dike-source models that remain to be read for this follow-up. No novelty claim is made.

**Executed scope.** The single-body slab calculation and a stack in the instantaneous-recording limit are complete. The stack uses one shared field; its polarities are correlated even when emplacement times are independent. The 1/√N RMS limit requires a span long relative to N mean chrons. Reported thickness limits are the largest passing sizes in a discrete grid. Finite cooling, mutual reheating, finite body geometry and orbital fields have not been coupled into a complete stack inversion.

**Reproduce.** Run `python scripts/followup/rapid_bodies.py`. The [reviewed body report](RAPID_BODIES.md) links the original saved protocol, corrected analytic band durations, unchanged retention fractions and an analytic correlated-stack RMS. Earlier outputs are retained under `research/followup/bodies_audit/`.

## Execution order

The working order is **2 → 3 → 4 → 1**: Arabia's feasibility checks, calibrated material mixtures, verified body cooling, then reversal-history identifiability. Arabia's initial prerequisites have now been run and fail the declared screens. A revised spatial design would require a separately recorded protocol and synthetic-null calibration before magnetic inference. Failed prerequisite checks are findings about what the declared comparison can resolve; they should not be bypassed to obtain a verdict.

The material balance, single-body cooling and the reversal prerequisite are now complete within the scopes above. Repetition of the same surface-based designs is paused pending new support or an independently identifiable comparison; this does not declare the surface map universally exhausted. A useful next model would restrict acquisition ages, material properties or geometry independently, and pass a fresh recovery test before any claim about Martian reversal timing. The present work does not establish that this is the only possible research direction.
