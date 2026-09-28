# Validation and its limits

The standard checks exercise original implementations, curated data relationships and the saved website. They do not independently validate a geological explanation for Mars.

## Run the standard checks

```bash
python -m pip install -e '.[test,research,observations]'
python -m pytest -q -m 'not integration'
node --test tests/*.test.mjs
```

The [GitHub workflow](../.github/workflows/tests.yml) runs Python 3.11 and 3.14, JavaScript checks on Node.js 22, and repository-link checks. The September 28 publication snapshot passed 150 Python and 8 JavaScript tests locally. The workflow result for a commit is the authoritative check status for that commit.

Six historical MCD integration tests are excluded from the standard run. They require a separately authorized installation and are not run by CI. Browsing the site requires none of them.

## What is checked

| Area | Representative checks |
| --- | --- |
| Gravity and crust | Analytic shell integral, relief decomposition, regularization gain and synthetic Moho recovery |
| Thermal recording | Analytic heat solutions, basal-flux endpoints, acquisition bookkeeping and slab crossing times |
| Reversals | Shared-field stack second moment, event integrals, time-change equivalence and known-clock likelihood controls |
| Material mixtures | Exact mass balances and attainable bounds checked against independent linear optimization |
| Spatial comparisons | Spherical geometry, matching constraints, connected block dependence and null/support gates |
| Data and chronology | Missing values, units, source references, distinct event clocks and candidate locations |
| Website | Routes, current navigation, local links, cache behavior and downloadable products |

The [six-test audit](../research/DISCRIMINATING_AUDIT.md), [audit controls](../research/discriminating_audit/controls.json) and [body correction record](../research/followup/bodies_audit/controls.json) retain the corrections behind the current results. A match to a published product is a consistency check under stated conventions, not a proof of that product's geological accuracy.

## Reproducibility checks

Manifests identify saved inputs, code, outputs and software versions. Not every historical manifest has the same fields. A changed source file can legitimately make an old run's code hash differ; preserve that history and label a new run separately. Floating-point results and figure bytes can vary with library versions and platforms.

Numerical builders are distinct from HTML renderers. Full gravity, regional and thermal builds are not rerun in every CI job, and external raw archives are not included in the repository. See [Development](DEVELOPMENT.md) for each workflow's requirements.

## Interface review

Current home, method, synthesis, body and reversal pages have been checked locally at desktop and mobile widths for layout, images, JavaScript errors and internal links. Automated route/link checks complement these inspections. JavaScript unit tests cover browser data logic; they are not a full end-to-end browser test suite.

## Historical records

The [earlier validation log](archive/ATMOSPHERIC_VALIDATION.md) preserves atmospheric, acoustic, animation and pilot checks from the previous interface. Its test counts and MCD comparisons are historical records, not new validations performed for this publication.
