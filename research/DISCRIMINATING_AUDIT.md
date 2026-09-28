# Audit of the six-test report

**28 September 2026 · targeted code and interpretation review**

## Follow-up verification of the corrected build

**Status:** the four principal numerical corrections are present in the inspected code. The non-integration suite was rerun: **105 passed, 6 deselected**. Saved output and builder/module hashes match the corrected build manifest, which records a 1,050-second run; that full build was not repeated during this verification.

The reference-shell contribution is included at every trial mean-Moho radius, the complete inversion preserves the declared degree-50 gain of 0.5, the basal flux reaches its finite-time endpoint, and the recording ensemble includes Poisson reversals. The updated [audit controls](discriminating_audit/controls.json) now check the implemented shell term as well as the omitted-term counterexample. All six saved crustal inversions meet their reported stopping criterion. These checks verify the identified corrections, not a unique Martian history.

The corrected snapshot gives an 8.4 km contrast for the Goossens–Sabaka density scenario and 6.6–41.4 km across the full declared set. Its southern 30 km magnetite calculation gives approximately 2.1% median retention and 6.3% at the 95th percentile for 0.67 Myr Poisson chrons. These are conditional model results. The report, README and site have been revised to avoid treating a quantile as a maximum, ensemble frequencies as planetary probabilities, or 30 km as a universal source boundary. Mapped surface-age association is distinguished from causal attribution to resurfacing.

Selected original methods passages of [Gong and Wieczorek (2021)](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2020JE006690) were accessible during this verification, including the stochastic thin-cap model and localized spectrum procedure. The original run's source ledger records its earlier access limitation. No complete equations/supplement audit or implementation of that cap model is claimed; the cylinder exercise remains a declared alternative geometry.

## Historical findings from the first build

**The sections below describe the original, uncorrected snapshot.** Their implementation defects have the follow-up status above; their original numbers are retained to explain the corrections. `controls.json` describes the latest verification, rather than the original faulty run.

The six-test calculation exists, and its **14 targeted tests pass** on the inspected snapshot. However, additional analytic controls expose implementation defects and unsupported extensions of the numerical results. In particular, the variable-density thickness contrast and the general exclusion of slow magnetic acquisition should not be treated as established findings from this build.

This audit adds diagnostic evidence. It does not replace the saved six-test outputs, rerun the full thermal ensemble, audit every cited article or certify the complete test suite. File hashes in [controls.json](discriminating_audit/controls.json) identify the inspected code and report.

## 1. Missing reference-shell gravity in the variable-density inversion — high priority

**Location:** `scripts/discriminating/build.py`, lines 115–120; `src/marswind/crustinversion.py`, forward construction.

The builder subtracts the gravity of topographic relief about a mean surface sphere and models Moho relief about another sphere. With uniform crustal density, the reference spherical shell has no nonzero-degree gravity. With lateral density variations, it does. The mass anomaly within the shell between the two reference spheres is absent from this construction.

An independent analytic control uses a flat 50 km shell and a degree-3, order-1 density coefficient of 100 kg/m³. Both relief grids are zero, so the current relief-only construction returns zero. Direct radial integration gives a nonzero exterior coefficient, **1.541151091 × 10⁻⁴** for the declared control parameters. This harmonic is not the intentionally removed degree-2 zonal term.

For a shell bounded by radii d and R, with density coefficient rho_lm and exterior reference radius r0, the contribution is:

```text
C_lm = 4*pi*rho_lm*(R^(l+3) - d^(l+3)) / [M*(2*l+1)*(l+3)*r0^l]
```

**Consequence:** agreement with a constant-density reference cannot validate the variable-density extension. The reported 14.8 km contrast and approximately 40% reduction require a corrected forward model and a complete recomputation. This audit does not supply a replacement contrast.

**Required correction:** include the lateral-density reference-shell contribution at each mean-Moho trial, document the background mass convention, and validate against independently constructed variable-density shells before fitting Mars.

## 2. Iteration progressively undoes the stated filter — high priority

**Location:** `src/marswind/crustinversion.py`, lines 94–108.

The taper multiplies the residual correction on every iteration. In a linear constant-density case, it controls the rate of convergence rather than the final regularized solution. Starting from the filtered estimate, the recovered gain after n updates is `1 - (1 - taper)^(n + 1)`.

For a pure degree-50, 10 m relief coefficient and a declared half-amplitude degree of 50, the control recovers **0.9999999991 of the input**, rather than 0.5, after 29 updates. The scalar filter's own unit test passes; it does not test the behaviour of the whole inversion.

All six saved Mars inversions also hit the 30-iteration ceiling, with final update norms of 3.8–23 m against the function's default 1 m stopping tolerance. An iteration update norm is not a data-space error or a scientific uncertainty.

**Required correction:** define and implement the intended regularized inverse, test its complete spectral response, and report convergence explicitly. Recheck the equal-density reference after correcting the algorithm; a several-kilometre archive mismatch is a comparison, not proof of correctness.

## 3. Periodic reversals do not test all frequently reversing dynamos — high priority

**Location:** `src/marswind/crusthistory.py`, lines 112–126; `scripts/discriminating/build.py`, lines 256–267; report Test 4 and combined conclusions.

The build uses `kind='periodic'` with 16 phases. Equal-duration positive and negative chrons can cancel far more efficiently than randomly timed reversals. The primary study being invoked examines random reversal histories; its basin results also depend on material properties and recording/remagnetization assumptions. [Steele et al., 2024](https://doi.org/10.1038/s41467-024-51092-4), [author-hosted article](https://www.research-collection.ethz.ch/server/api/core/bitstreams/0c422011-1923-47c4-b5c7-94ac28870f31/content).

A separate synthetic control integrates the **same uniform 800 Myr acquisition kernel** against both field models, with a mean chron of 0.67 Myr. Median retained magnitude is **0.0025% for periodic reversals** and **1.86% across 512 Poisson realizations**. The stochastic RMS, 2.82%, agrees approximately with the analytic value, 2.89%. These values belong to this control, not to the report's accepted thermal ensemble and not to a reproduction of Steele's basin calculation.

**Consequence:** the reported 0.04% is specific to its periodic-field experiment. It does not establish a general exclusion, a uniquely necessary 1,000 Myr chron, or a contradiction between strong southern anomalies and weak basins. Different epochs could also have different reversal statistics. Strong cancellation may remain important; its magnitude and admissible alternatives require testing.

**Required correction:** compare periodic, stochastic and time-varying field histories with explicit activity windows; retain distributions and acquisition fractions. Couple the actual spatial magnetic forward model to recording before converting coherence into a planetary exclusion.

## 4. The parameter labelled present basal flux is an asymptote — medium priority

**Location:** `src/marswind/crusthistory.py`, lines 60–62.

The implemented function is `q_now + (q_early - q_now)*exp(-t/tau)`. At the model's present time, 4.5 Gyr after initialization, it has not generally reached `q_now`. A control with declared values of 15 mW/m² now, 60 mW/m² initially and tau = 3 Gyr actually gives **25.04 mW/m² today**.

**Required correction:** either rename and justify the parameter as the infinite-time asymptote or normalize the decay to satisfy both finite-time endpoints, then rebuild. The choice changes the stated parameter bounds and thermal-history interpretation.

Additional thermal controls are needed before making global carrier exclusions: sensitivity to the adopted initial state and elastic-thickness proxy; interpolation onto common physical depths instead of equating grid indices across slightly different cell sizes; and separate reporting of an unknown earlier record versus a computed cooling event. The builder currently counts always-cool material as compatible with every early cutoff, which is not evidence that acquisition occurred there.

## 5. Two ground comparisons do not establish a universal factor-five uncertainty

**Location:** report Test 5; `scripts/research/render_site.py`, fifth test card.

A surface prediction compared with a rover traverse or a lander's local field is a comparison of different spatial bandwidths. Two local discrepancies do not define an uncertainty distribution for every orbital anomaly or crater-scale contrast. The Zhurong paper explicitly discusses both unresolved structure and amplified model errors; it does not uniquely attribute both sites' discrepancies to small sources. [Du et al., 2023](https://doi.org/10.1038/s41550-023-02008-7), discussion around its Figure 4.

**Required correction:** retain the site-specific predicted/measured quantities and their different components. Replace the universal factor-five statement with the demonstrated limitation of local surface extrapolation. Calibrate any regional uncertainty model using suitable additional observations and resolution/noise analyses.

## 6. The cylinder calculation is a geometry scenario, not an established lower bound

**Location:** `src/marswind/amplitude.py`, opening description; `scripts/discriminating/build.py`, lines 329–338; report Test 3.

The code divides an orbital window RMS by the on-axis response of one uniform cylinder. Those are different observation operators. The claim that this geometry provides a universal minimum required magnetization has not been demonstrated by an optimization or independent bound.

The source paper's equivalent depths and cap sizes arise from a stochastic ensemble of thin spherical caps, not a unique physical cylinder beneath each window. Its finite-layer comparison further qualifies the depth interpretation. Relevant primary methods text is now accessible in [Gong and Wieczorek, 2021](https://doi.org/10.1029/2020JE006690), sections 2 and 4; it should be incorporated into the source assessment before further modelling.

**Required correction:** label the present numbers as a declared cylinder-equivalent calculation. For an inferred budget, predict the same window statistic with a compatible source geometry and propagate depth/size uncertainty. Rock-type or impossibility claims need independently justified material limits; the selected 1, 5 and 20 A/m scenarios do not themselves establish those limits.

## Interpretation and provenance checks

The age-transfer model tests prediction, not causation. Its association with mapped surface age cannot by itself establish what fraction of the dichotomy resurfacing caused. The code also uses approximate class-centre ages as numerical predictors (`age_features`), although the protocol calls them reading aids only. The protocol should describe the actual features, and an ordinal-only sensitivity run is needed.

The local protocol has a declaration date, but this audit has not established an independently timestamped version predating all exploratory results. It should not be described as external preregistration. Passing checksums proves consistency with a saved snapshot, not that its scientific model is valid.

## What remains usable and what must be recomputed

The project retains useful numerical infrastructure, transparent saved outputs, prediction diagnostics and site-specific field comparisons. The audit does not establish a different origin of the dichotomy or prove that slow cooling works. It shows why the current experiments cannot support several of their strongest verdicts.

Correct the gravity forward model and regularization first; then resolve the basal-flux convention and rerun the thermal/recording ensemble with alternative reversal statistics. Recast the amplitude exercise and ground comparisons at their demonstrated scope. Fast-cooled bodies remain a useful subsequent model family, but should not be introduced as the only remaining explanation on the basis of this build.

## Reproduce the audit controls

```sh
.venv/bin/python -m pytest tests/test_discriminating.py -q
.venv/bin/python scripts/discriminating/audit_controls.py
```

The first command passed 14 tests in this review. The second writes [controls.json](discriminating_audit/controls.json), including input/code hashes. It uses the existing numerical environment and saved output; it does not fetch datasets or overwrite the six-test results. The complete 101-test claim and full 11-minute build were not rerun in this audit.
