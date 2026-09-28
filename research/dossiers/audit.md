# Audit and current evidence

The six-test report uses the corrected calculation outputs. The audit records both the first-run errors and their follow-up, so an older number in a historical section must not be mistaken for the current result.

## What was corrected

The gravity calculation now includes the reference shell with lateral density variations and retains the declared regularization throughout inversion. The basal heat-flux decay meets both specified endpoints. Randomly timed reversals supplement periodic histories, and material already below the relevant temperature at the start is reported as an unresolved earlier record.

## What the checks establish

Analytic cases, convergence diagnostics and controlled synthetic inputs check implementation behavior. Comparisons with published products check consistency under specified assumptions. The [audit controls](../discriminating_audit/controls.json) and [build manifest](../discriminating/manifest.json) expose the corresponding saved evidence. Passing a numerical check does not establish a unique geological explanation.

## What the interpretation now says

Retention is a distribution over the declared simulations. The thermal ensemble does not impose a universal depth boundary. Cylinder-equivalent source strengths depend on geometry and are not mineral abundances. The thickness contrast remains positive in the tested density scenarios, with substantial variation in size.

The [Arabia Terra preflight](../ARABIA_PREFLIGHT.md) adds a check on the next proposed comparison. The 23 northern Early Noachian cells are not all adjacent to the dichotomy boundary, and only two lie within the declared Arabia footprint. The declared matching and block screens fail, so this follow-up supplies no magnetic verdict.

The subsequent [boundary-transect test](../BOUNDARY_WALK.md) evaluates the magnetic model directly on spherical normals and shifted southern controls. At ±200 km, 120 eligible pairs supply only three adequately covered blocks. Requiring common stations on all three lines leaves no admissible block. The result is not decisive. The accompanying regional decomposition also corrects the interpretation of Test 1's northern aggregate: 14 of its 23 cells lie in Xanthe–Chryse, and the reported 52.5 nT is a back-transformed logarithmic mean, not the 69.3 nT arithmetic mean.

## Follow-up checks

The [depth–age study](../DEPTH_AGE.md) reports no supported association under its rule. Its northern table has 8 positive cases out of 12, with repeated point estimates for the two wedge offsets. The oldest northern surface bin has only one window. These results do not by themselves select excavation over resurfacing; the shifted uncertainty endpoints are sensitivity cases, not a joint posterior.

The [density–remanence calculation](../DENSITY_REMANENCE.md) supplies exact mass balances and material-cap intervals, checked against independent linear optimization. Under a declared efficient magnetite scenario, the coherent southern cylinder target requires about 0.05–0.10% of the solid volume; the already cancellation-corrected target requires about 2.47–5.03%. These remain conditional on porosity, matrix density and the assumed correspondence between density and magnetic-source volumes.

The [body-cooling review](../RAPID_BODIES.md) corrects elapsed time to the lower blocking boundary into the actual duration between both crossings. The primary 3 km body crosses in 0.853 Myr, with its simulated 76% median retention unchanged. The stack's exact second moment includes shared-field polarity correlations; 1/√N is only a long-span RMS limit. The original files are preserved in the body-audit archive.

The [reversal-identifiability prerequisite](../REVERSAL_IDENTIFIABILITY.md) finds a pathwise equivalence between a changing rate and a constant rate with different acquisition clocks, including synthetic fields at two altitudes. A calibrated ideal dated-sign control recovers rate changes, but freeing its acquisition clock restores the likelihood ambiguity. No observed Mars map was fitted. The [current synthesis](../STATE_OF_EVIDENCE.md) incorporates these limits.

## Who checked it

This is an internal, AI-assisted implementation and interpretation review. It is not external peer review or an independent scientific certification. The [method page](../../docs/SCIENTIFIC_METHOD.md#reading-a-verdict) defines the verdict vocabulary and the [reproduction section](../../docs/DEVELOPMENT.md) separates numerical builds from site rendering.

The technical references below remain current. Historical findings inside the audit are explicitly marked; the rest of the reading collection is preserved as dated background.
