# From a literature atlas to useful physical tests

The selected first study is now specified in the [joint thermal–magnetic test protocol](TEST_PROTOCOL.md), based on the [working hypothesis](HYPOTHESES.md). The directions below remain complementary analyses rather than completed results.

These are proposed investigations, not results already computed. They prioritize questions that can fail a model, quantify uncertainty or improve an observation. The existing wind maps and acoustics experiments remain atmospheric diagnostics.

## 1. Does magnetic asymmetry survive fair spatial comparisons?

**Question.** How much of the magnetic contrast remains after accounting for geological province, resurfacing, altitude and spatial bandwidth?

Acquire MOLA, a global crustal-field model, a crustal-thickness ensemble and geological units. Compare geological highlands/lowlands using several published boundary definitions, not only the equator. Evaluate magnetic models at a common altitude and bandwidth. Mask large basins and young volcanic provinces in separate sensitivity runs. Weight by spherical area, and use spatial blocks for uncertainty rather than treating every map pixel as independent.

**Deliverable.** Maps of coverage and residual contrast, distributions by geological unit, and an uncertainty table across boundary/model choices. A contrast that disappears under plausible masks is less diagnostic than one that persists. Neither outcome alone identifies a dynamo geometry.

Starting sources: [Langlais et al., 2019](https://doi.org/10.1029/2018JE005854), [Wieczorek et al., 2022](https://doi.org/10.1029/2022JE007298), [USGS geological map](https://www.usgs.gov/maps/geologic-map-mars).

## 2. Can preservation explain weak magnetic regions?

**Question.** Can plausible carrier distributions, burial, impact heating and reversal histories reproduce weak anomalies without requiring an absent dynamo?

Build a forward model that predicts the measured field at spacecraft altitude from source magnetization and geometry. Test simple synthetic cases before importing real data. Compare constant-polarity and reversing-field cooling histories. Use specimen-quality controls from the meteorite dossier to constrain carrier capacities; do not use contaminated natural remanence as a paleointensity observation.

**Deliverable.** A map or envelope of compatible source properties and a list of scenarios that fail. Existing basin-reversal simulations offer a starting benchmark; Borealis-scale extrapolation requires a separate physical calculation. [Steele et al., 2024](https://doi.org/10.1038/s41467-024-51092-4), [published model repository](https://github.com/ssteele1111/BasinCoolMag), [Vervelidou et al., 2023](https://doi.org/10.1029/2022JE007464).

## 3. A direct bridge from MCD to interior constraints

**Question.** How sensitive are seasonal gravity corrections to the atmospheric scenario?

Berne et al.'s tidal-tomography methods project MCD surface pressure onto spherical harmonics and include the solid body's loading response. Their reference cites MCD 5.3; this project uses MCD 6.1, so a comparison would be a version/scenario sensitivity experiment, not a literal reproduction. [Berne et al., 2026, Methods](https://doi.org/10.1038/s41586-026-10893-x).

Proposed sequence:

1. Extend the sampler to obtain pressure **at the local surface** globally, with explicit units and terrain handling. Pressure at a fixed 60-km areoid altitude is not the needed quantity.
2. Sample the whole planet at a common instant. A constant-local-time mosaic is not an instantaneous mass distribution.
3. Project pressure onto explicitly normalized real spherical harmonics, integrating with the spherical area element. Validate the uniform-pressure case, a prescribed single harmonic, and grid-convergence behaviour.
4. Separate the seasonal mean, pressure redistribution and polar mass exchange consistently with the comparison model. Propagate the assumed loading Love numbers.
5. Repeat over dust/solar scenarios and model versions where available. Preserve phase as well as amplitude. Compare with published correction coefficients before attempting any interior inference.

**Deliverable.** Reproducible seasonal coefficient curves and scenario uncertainty, with no claim of a new mantle-temperature inversion. The current application exposes only its installed climatology scenario; adding the proposed ensemble requires extra model configuration and validation.

## 4. Build a chronology that does not mix unlike ages

**Question.** Which formation histories are inconsistent with securely preserved old crust or dated resetting events?

Extract analytical tables for zircons, ALH 84001, regolith breccias and major ejection groups. Label crystallization, reservoir extraction, alteration, shock, remanence and ejection ages separately. Include uncertainty in chronometers and provenance. Plot inferred sequences as ranges and partial order constraints rather than forcing every event to one precise date.

**Deliverable.** A machine-readable event table and a dependency-aware timeline. It should show explicitly where an age constrains one grain or province instead of the entire dichotomy. [Bouvier et al., 2018](https://doi.org/10.1038/s41586-018-0222-z); [Cox et al., 2022](https://doi.org/10.1126/sciadv.abl7497); [Herd et al., 2024](https://doi.org/10.1126/sciadv.adn2378).

## 5. Compare mechanisms on the same evidence

Only after the datasets above are harmonized, construct a common comparison of northern impact, southern impact, internal growth and hybrid models. Require predictions for the same observables, spatial scales and epochs. Define uncertainty and model discrepancy explicitly. Keep simulations with shared codes or initial conditions grouped rather than treating their number as independent support.

A suitable output is a constraint matrix with **compatible, in tension, not tested, or non-discriminating** entries and the reason for each. Numerical posterior probabilities would require defensible priors, likelihoods and comparable model ensembles; the current qualitative literature assessment does not supply them.

## Less-developed domains to pursue deliberately

- **Magnetic carrier chemistry and hydrothermal alteration:** separate stronger recording capacity from stronger ancient field.
- **Shock physics and partial remagnetization:** reconcile petrographic shock evidence with component-level magnetization.
- **Crustal differentiation without plate tectonics:** compare petrological predictions with local seismic structure and orbital exposures.
- **Isotopic reservoirs and crust–mantle exchange:** test whether a model mixes reservoirs that meteorites indicate survived.
- **True polar wander and reference-frame changes:** distinguish the original location of a province from its current latitude.
- **Buried northern crust and radar selection:** determine what surface smoothness conceals rather than assigning a young age to all underlying crust.
- **Moon origins and giant-impact angular momentum:** require an impact scenario to remain compatible with satellite constraints; detailed screening is still pending.
- **Paleoclimate, oceans and escape:** evaluate later modification and feedback without making them automatic explanations of primordial crustal structure.

The discovery library includes leads in these areas, but their full assessment is uneven. Use the review-depth filter and citation queue to choose the next papers; a search hit is not an endorsed conclusion.
