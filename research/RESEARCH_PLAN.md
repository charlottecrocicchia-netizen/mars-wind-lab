# From a literature atlas to useful physical tests

The initial thermal–magnetic study is specified in the [joint test protocol](TEST_PROTOCOL.md), based on the [working hypothesis](HYPOTHESES.md). Complementary analyses now include the three executed physical studies below. The remaining directions are questions for further work, with completed parts identified individually.

The [results directory](/research/tests) separates completed diagnostics and synthetic experiments from the remaining investigations below. They prioritize questions that can fail a model, quantify uncertainty or improve an observation.

## Executed physical studies · September 2026

The [new workbench](/research/physics) and [methods report](DICHOTOMY_PHYSICS.md) implement all three complementary axes:

| Axis | Executed result | Next missing constraint |
| --- | --- | --- |
| Composition and buoyancy | Density assumptions can reverse the inferred thickness contrast while maintaining highland support; 180 layer cases retain the dense residue. | Composition-to-density predictions with pressure, temperature and depth-dependent porosity, checked jointly against seismic and gravity data. |
| Amplification of an initial difference | A 100 km conductive shell gives nearly equal growth rates for degrees one and two; the initial spectrum controls the finite-amplification power share. | Conserved melt/heat inventories, nonlinear saturation, absolute timescales and alternative convective forcing. |
| Earlier boundary through deformation | Four observed MOLA profiles tested under 48 loads plus a control; the 56°E proxy can switch features by hundreds of kilometres. | Dated features, measured loading history and a restoration that tracks the same structure rather than the steepest available slope. |

The [paleomagnetism learning path](PALEOMAGNETISM_FOUNDATIONS.md) supplies the complementary foundation: recording process, component geometry, conversion to intensity, retention, age and the difference between local and planetary claims. A known-input Arai counterexample demonstrates why a perfect line can still yield a biased field. No new meteorite paleointensity has been inferred.

## 1. Does magnetic asymmetry survive fair spatial comparisons?

**Question.** How much of the magnetic contrast remains after accounting for geological province, resurfacing, altitude and spatial bandwidth?

**Initial execution:** these four products have been acquired; common-altitude, boundary and density-sensitivity results are in [First diagnostics](FIRST_RESULTS.md). Further work: Compare geological highlands/lowlands using several published boundary definitions, not only the equator. Evaluate magnetic models at a common altitude and bandwidth. Mask large basins and young volcanic provinces in separate sensitivity runs. Weight by spherical area, and use spatial blocks for uncertainty rather than treating every map pixel as independent.

**Deliverable.** Maps of coverage and residual contrast, distributions by geological unit, and an uncertainty table across boundary/model choices. A contrast that disappears under plausible masks is less diagnostic than one that persists. Neither outcome alone identifies a dynamo geometry.

Starting sources: [Langlais et al., 2019](https://doi.org/10.1029/2018JE005854), [Wieczorek et al., 2022](https://doi.org/10.1029/2022JE007298), [USGS geological map](https://www.usgs.gov/maps/geologic-map-mars).

## 2. Can preservation explain weak magnetic regions?

**Question.** Can plausible carrier distributions, burial, impact heating and reversal histories reproduce weak anomalies without requiring an absent dynamo?

Build a forward model that predicts the measured field at spacecraft altitude from source magnetization and geometry. Test simple synthetic cases before importing real data. Compare constant-polarity and reversing-field cooling histories. Use specimen-quality controls from the meteorite dossier to constrain carrier capacities; do not use contaminated natural remanence as a paleointensity observation.

**Deliverable.** A map or envelope of compatible source properties and a list of scenarios that fail. Existing basin-reversal simulations offer a starting benchmark; Borealis-scale extrapolation requires a separate physical calculation. [Steele et al., 2024](https://doi.org/10.1038/s41467-024-51092-4), [published model repository](https://github.com/ssteele1111/BasinCoolMag), [Vervelidou et al., 2023](https://doi.org/10.1029/2022JE007464).

## 3. Build a chronology that does not mix unlike ages

**Question.** Which formation histories are inconsistent with securely preserved old crust or dated resetting events?

The [curated event timeline](/research/comparison?view=timeline) is available. Extend it with permitted analytical tables for zircons, ALH 84001, regolith breccias and major ejection groups. Label crystallization, reservoir extraction, alteration, shock, remanence and ejection ages separately. Include uncertainty in chronometers and provenance. Plot inferred sequences as ranges and partial order constraints rather than forcing every event to one precise date.

**Deliverable.** A machine-readable event table and a dependency-aware timeline. It should show explicitly where an age constrains one grain or province instead of the entire dichotomy. [Bouvier et al., 2018](https://doi.org/10.1038/s41586-018-0222-z); [Cox et al., 2022](https://doi.org/10.1126/sciadv.abl7497); [Herd et al., 2024](https://doi.org/10.1126/sciadv.adn2378).

## 4. Compare mechanisms on the same evidence

The [current comparison](/research/comparison) provides a qualitative first matrix. The next stage is to harmonize the datasets and construct a quantitative comparison of northern impact, southern impact, internal growth and hybrid models. Require predictions for the same observables, spatial scales and epochs. Define uncertainty and model discrepancy explicitly. Keep simulations with shared codes or initial conditions grouped rather than treating their number as independent support.

A suitable output is a constraint matrix with **compatible, in tension, not tested, or non-discriminating** entries and the reason for each. Numerical posterior probabilities would require defensible priors, likelihoods and comparable model ensembles; the current qualitative literature assessment does not supply them.

## Less-developed domains to pursue deliberately

- **Magnetic carrier chemistry and hydrothermal alteration:** separate stronger recording capacity from stronger ancient field.
- **Shock physics and partial remagnetization:** reconcile petrographic shock evidence with component-level magnetization.
- **Crustal differentiation without plate tectonics:** compare petrological predictions with local seismic structure and orbital exposures.
- **Isotopic reservoirs and crust–mantle exchange:** test whether a model mixes reservoirs that meteorites indicate survived.
- **True polar wander and reference-frame changes:** distinguish the original location of a province from its current latitude.
- **Buried northern crust and radar selection:** determine what surface smoothness conceals rather than assigning a young age to all underlying crust.
- **Moon origins and giant-impact angular momentum:** require an impact scenario to remain compatible with satellite constraints; detailed screening is still pending.

The discovery library includes leads in these areas, but their full assessment is uneven. Use the review-depth filter and citation queue to choose the next papers; a search hit is not an endorsed conclusion.
