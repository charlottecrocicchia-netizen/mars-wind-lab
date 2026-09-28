# Common observations, separate clocks

**Curated synthesis · 27 September 2026.** [Open the interactive comparison](COMPARISON.md) or [the chronology](COMPARISON.md?view=timeline). The interface, source notes and exports are in English.

## What the comparison means

Five observations are presented to the same four origin families. These are overlapping mechanisms, not mutually exclusive statistical models. The southern-impact examples already contain interior evolution. The regional recording histories in [Working hypothesis](HYPOTHESES.md) answer a different question: how rocks acquire and retain magnetization.

Each cell records a project assessment, a requirement, a future test and primary sources. “Compatible” applies to the stated mechanism and conditions. “Tension” identifies a specific variant. “Not tested” means a common confrontation has not been established in the selected reading; it does not mean no relevant publication exists. “Non-discriminating” means the observation alone cannot select an origin.

**No scores, posterior odds or model fits are calculated.** Rows share gravity, topography, seismic constraints or samples; they must not be counted as independent votes. Source consultation is selective, with its scope recorded for each reference. Predictions and proposed tests are our synthesis, not quotations or claims of author endorsement.

## How the chronology is drawn

All numeric ages are in millions of years before the present (Ma), increasing towards the past. Each displayed window has a linear axis; switching windows changes the scale. An event is included when its reported interval overlaps the selected window. Bounds are clipped to the display, never converted into finite scientific ranges.

- A solid interval is a reported estimate with uncertainty. The confidence convention is retained where verified; no conversion to a common confidence level is attempted.
- A dashed interval is a range. It can describe different grains or an interpreted event window, and is not automatically a confidence interval.
- A diamond is an approximate contextual or interpreted age. Its symbol width has no uncertainty meaning.
- A left arrow marks a lower bound on age (an event at least that old).
- Unknown ages have null numerical fields and remain outside the axis, including when zooming to recent time.

The event details identify the material, method, qualifications and source. Some contextual dates are cited within the consulted article; they are labelled as such, rather than presented as fresh audits of the original dating analyses. The Nakhla shock is not assigned directly to Lafayette. Alteration does not automatically date magnetization, and crystallization of a zircon does not date the global dichotomy.

The JSON also records a small set of within-material ordering relations. They are not causal links between distinct meteorites, fitted durations, or a universal chronology for Mars.

## Reproducibility and reuse

The [curated JSON](comparison/evidence.json) is the single source for both interactive views and the [matrix CSV](comparison/matrix.csv) and [event CSV](comparison/events.csv). Export complete tables with `python scripts/research/export_comparison.py`. Numeric cells for unknown ages stay empty in CSV. Every export keeps age conventions, caveats and source URLs; the CSV downloads contain the complete selection, irrespective of interface filters.

These are original notes and a small transcription of cited factual ages, not copied source tables, external code or figures. No new large archive was downloaded, no former internship material was consulted. Source dataset licenses remain distinct from the project's code license. This selection is neither a complete meteorite inventory nor a full-text audit of all competing models.
