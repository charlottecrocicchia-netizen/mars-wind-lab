# Follow-up artifacts

Read the [research guide](../README.md#follow-up-results) for the questions and conclusions. Each calculation's report links its protocol, tables, figures and manifest.

| Directory | Calculation | Entry point |
| --- | --- | --- |
| `arabia/` | Matching feasibility and spatial support | [Report](../ARABIA_PREFLIGHT.md) |
| `boundary_walk/` | Boundary transects, shifted controls and regional decomposition | [Report](../BOUNDARY_WALK.md) |
| `depth_age/` | Equivalent source depth against surface-epoch summaries | [Report](../DEPTH_AGE.md) |
| `mixture/` | Density–remanence material balances | [Report](../DENSITY_REMANENCE.md) |
| `bodies/` | Single-slab acquisition and instantaneous-recording stacks | [Report](../RAPID_BODIES.md) |
| `bodies_audit/` | Original body outputs and correction comparison | [Controls](bodies_audit/controls.json) |
| `reversal/` | Synthetic time-change equivalence and dated-sign recovery | [Report](../REVERSAL_IDENTIFIABILITY.md) |

`protocol.json` records declared settings; `summary.json` contains numerical summaries; CSV files expose tables; PNG/SVG files are project-generated figures. Manifests record the hashes available for that run. A manifest is provenance, not independent scientific certification.

The `bodies_audit/before/` tree is a preserved pre-correction snapshot. It is intentionally historical: use `bodies/` and the current report for corrected results. Do not run archived builders as if they were current commands.
