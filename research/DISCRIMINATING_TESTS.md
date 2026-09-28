# Six discriminating tests of the Martian dichotomy

**Executed 28 September 2026, corrected the same day after an independent audit · Charlotte Crocicchia's Mars project · reproducible with `python scripts/discriminating/build.py`**

[Results on the website](DISCRIMINATING_TESTS.md) · [Audit](DISCRIMINATING_AUDIT.md) · [Protocol](discriminating/protocol.json) · [Sources and reading depth](discriminating/sources.json) · [Run manifest and checksums](discriminating/manifest.json)

Each test was declared in `protocol.json` in this repository before it was run (this is not an external, timestamped preregistration), uses only public inputs, and states a verdict about the scenario it tests. None of them identifies the origin of the dichotomy. Together they narrow what a viable explanation must do.

## What the audit changed

The [audit](DISCRIMINATING_AUDIT.md) of the first build found two implementation errors and several over-statements. The numerical corrections and their effects are listed below. A subsequent verification also narrowed the interpretation of ensemble frequencies, magnetic retention and source depths:

| Finding | Correction | Effect |
|---|---|---|
| The gravity of the reference crustal shell was omitted when the crust density varies laterally | `shell_potential` added and recomputed at every trial Moho radius; validated against the analytic integral and a decomposition identity | Goossens & Sabaka contrast 14.8 → 8.4 km; the ±200 kg/m³ scenarios now span 6.6–41.4 km |
| Iterating the residual correction undid the declared filter | Regularised fixed-point scheme of Wieczorek & Phillips (eq. 18); a degree-50 test relief now returns the declared gain of 0.5; every inversion is run to convergence (<1 m) | Equal-density contrast unchanged (24.1 km), maximum thickness now matches the archive (116 km) |
| The "present-day" basal flux was an infinite-time asymptote | Decay normalised to meet both endpoints exactly | Ensemble re-run: 636 northern and 66 southern histories accepted |
| Periodic reversals presented as a general exclusion | Poisson reversals added (64 seeds per history), distributions reported | Retained fraction at 1.5 reversals/Myr: 2% (Poisson) instead of 0.04% (periodic); verdict softened |
| Material never hotter than the Curie point counted as "cooled before" every cutoff | Reported separately as an unresolved earlier record | Shallow crust is now stated as unconstrained rather than compatible |
| "Universal factor five", "lower bound", "excluded" | Reworded at the demonstrated scope | Tests 3, 4 and 5 now carry "constrains" verdicts |

## Summary

| # | Question | Result | Verdict |
|---|---|---|---|
| 1 | Does surface age predict the magnetic map beyond structure and hemisphere? | Age has out-of-region skill (+0.13, +0.15), but a north/south indicator does as well (+0.17, +0.16) and adding age gains little. Middle and Late Noachian northern cells are 2–4 times weaker; 23 Early Noachian northern cells have a similar aggregate to the south, but 14 lie in Xanthe–Chryse. | Not decisive: mapped surface age leaves a hemispheric association; its cause is unresolved |
| 2 | When did each depth of crust last cool through a carrier Curie point? | In 66 accepted southern histories, 30 km crossed 580 °C at a median 4.09 Ga (39% before 4.1 Ga, 59% before 3.7 Ga, 21% never hotter); 40 km at 3.50 Ga (30% before 3.7 Ga). Pyrrhotite below 25 km never cooled in time. | Early crossings are less frequent at depth in this ensemble; no universal depth or carrier cutoff follows |
| 3 | How much magnetization would the anomalies need? | In a declared cylinder scenario a 20 km layer needs a median 4.2 A/m in the south (1.0 north); 43% of southern windows exceed 5 A/m. After Poisson cancellation with 100 Myr chrons the median is 16 A/m; with 0.67 Myr chrons 208 A/m. | Constrains: demanding in this geometry; not a rock-type verdict |
| 4 | Can slow cooling under a reversing dynamo keep a coherent record? | Cooling through the magnetite band at 30 km took a median 774 Myr. At 1.5 random reversals per Myr the median retained fraction is 2.1% (95th percentile 6.3%); periodic reversals leave 0.03%. 500 Myr is the shortest tested mean chron giving at least 50% median retention in this ensemble. | Constrains: strong median cancellation under the declared histories; no universal upper bound on retention |
| 5 | Does the orbital model match ground measurements? | At Zhurong the model gives 79 nT against 5–40 nT measured; at InSight 312 nT against about 2,000 nT. | Constrains: local surface extrapolation failed by ×5–6 at both checked sites; not an uncertainty for every anomaly |
| 6 | Does a lighter southern crust remove the thickness dichotomy? | Contrast 24.1 km at equal density, 8.4 km with Goossens & Sabaka densities, 6.6 to 41.4 km across the ±200 kg/m³ scenarios; minimum thickness stays positive everywhere. | Constrains: positive across the tested scenarios, strongly density-dependent in size |

## Test 1 — Surface age as a predictor of the magnetic map

**Question.** If the magnetic dichotomy is an archive effect, the age of the mapped surface should carry information that relief, crustal thickness and the hemispheric boundary do not.

**Method.** On the 13,680 two-degree cells within 75° of the equator, the target is log(1 + |B|/1 nT) from the degree-134 Langlais et al. (2019) model at 150 km. Predictor sets: the epoch of the USGS SIM 3292 unit at each cell (ordinal rank eN=1 … lA=8, a declared class-centre age in Ga, and Noachian, Hesperian and Amazonian indicators; `age_ordinal` drops the class-centre age), the earlier structural set (relief, crustal thickness for four density variants, unit groups), smooth degree-one and degree-two location functions, and a north/south indicator from the Andrews-Hanna boundary. Fixed ridge models with training-only scaling. Validation: six random folds, then six complete 60° longitude wedges with 10° buffers, repeated with the wedges rotated by 30°. Longitude shifts of the target by 60°, 120° and 180° are controls. Skill compares predictor sets out of region; it does not establish causation.

**Result** (150 km, crust density 2,900, skill over the training mean):

| Predictors | Random cells | Wedges 0° | Wedges 30° |
|---|---:|---:|---:|
| hemisphere | +0.22 | +0.17 | +0.16 |
| location | +0.53 | −0.10 | +0.32 |
| structure | +0.26 | +0.07 | +0.17 |
| age | +0.19 | +0.13 | +0.15 |
| age, ordinal only | +0.19 | +0.12 | +0.13 |
| hemisphere + age | +0.26 | +0.17 | +0.18 |
| structure + age | +0.28 | −0.01 | +0.14 |
| all | +0.59 | −0.31 | +0.44 |

Shifting the target in longitude drives the age skill to −0.02, −0.09 and −0.02. The structural set's regional skill depends on the assumed density (+0.23 at 2,600 kg/m³, +0.07 at 2,900); the age set's does not.

Back-transformed area-weighted mean log(1 + |B| / 1 nT) at 150 km, expressed in nT (cells in parentheses). These are not arithmetic means; the saved age-transfer figure uses the same statistic:

| Epoch | North of boundary | South of boundary |
|---|---:|---:|
| Early Noachian | 52.5 nT (23) | 55 nT (1,591) |
| Middle Noachian | 20 nT (222) | 49 nT (3,080) |
| Late Noachian | 10 nT (63) | 37 nT (1,025) |
| Early Hesperian | 15 nT (455) | 33 nT (471) |
| Late Hesperian | 11 nT (2,259) | 9 nT (315) |
| Early Amazonian | 5 nT (54) | — |
| Middle Amazonian | 8 nT (773) | 48 nT (91) |
| Late Amazonian | 18 nT (311) | 38 nT (14) |

**Reading.** Age carries genuine, spatially aligned, out-of-region information, and within each side the field falls by a factor of five to ten from the Noachian to the Late Hesperian. But age and hemisphere are largely the same information because most Noachian terrain lies south of the boundary, and at equal epoch the north remains two to four times weaker for Middle and Late Noachian terrain. The 23 Early Noachian northern cells have similar aggregate amplitudes to the south, but this is not a representative northern equivalence. The subsequent [regional decomposition and boundary transects](BOUNDARY_WALK.md) find that 14 cells lie in Xanthe–Chryse; their joint 52.5 nT statistic is a back-transformed logarithmic mean, compared with a 69.3 nT arithmetic mean. The boundary test has only three adequately covered primary blocks and no admissible block for the common-support control comparison. The subsequent [geometry preflight](ARABIA_PREFLIGHT.md) corrects the original claim that they were all adjacent to the boundary: only 10 are within 160 km, and only two lie inside the declared Arabia footprint. The predictive association is compatible with resurfacing effects, but it does not establish their causal contribution. A ground magnetometer on Noachian terrain north of the boundary would be the direct test.

**Limits.** Surface age is not the age of the deep source. Cells are correlated samples of one model, so no significance is claimed. Some southern Amazonian cells have high fields; inheritance from older buried crust is a possible explanation, not a result of this regression.

## Test 2 — When each depth could have recorded a field

**Question.** A thermal remanence is acquired when rock cools through its blocking temperatures while a field exists. The inherited-archive scenario needs the deep southern crust to have cooled below the carrier Curie point before the dynamo stopped, at 4.1 Ga in the classical view or 3.7 Ga in recent interpretations.

**Method.** Fixed-thickness conductive crust columns (thickness rounded to whole kilometres, 1 km cells, 2.5 Myr steps) from 4.5 Ga to today, heated by K, Th and U decaying with their real half-lives and by a mantle heat flux that decays from a sampled early value to a sampled present-day value (both endpoints met exactly). Latin-hypercube samples of nine parameters, 5,000 per hemisphere. Gates: initial temperature below 1,500 K everywhere, present-day temperatures within 30 K of the published Thiriet et al. (2018) envelope at 5–35 km, and for the south a 650–850 K isotherm between 5 and 35 km at 3.9 Ga. 636 northern and 66 southern histories passed. For each accepted history and depth we record the age at which the rock last cooled through 325 °C (pyrrhotite), 580 °C (magnetite) and 670 °C (hematite). Material never hotter than a threshold in the model is reported as an unresolved earlier record, not as compatible.

**Result** (south, magnetite):

| Depth | Median age of crossing | Cooled before 4.1 Ga | Cooled before 3.7 Ga | Never hotter (unresolved) |
|---:|---:|---:|---:|---:|
| 20 km | 4.37 Ga | 12% | 12% | 88% |
| 25 km | 4.18 Ga | 32% | 48% | 52% |
| 30 km | 4.09 Ga | 39% | 59% | 21% |
| 35 km | 3.81 Ga | 11% | 53% | 11% |
| 40 km | 3.50 Ga | 6% | 30% | 6% |

Pyrrhotite at 30 km crossed its Curie point at a median 2.5 Ga and never before 3.7 Ga in any accepted history. Hematite at 40 km crossed at 3.9 Ga. Of the 32 usable southern source windows with equivalent depth ≥ 30 km, none has that depth cooled through the magnetite point before 4.1 Ga in a majority of histories; 22 do before 3.7 Ga. Accepted southern thicknesses are 42–61 km (5–95%).

**Reading.** Computed early magnetite crossings become less frequent with depth in this accepted ensemble, but some occur below 30 km. Pyrrhotite at 30 km has no computed crossing before 3.7 Ga in these histories. Neither result excludes other thermal histories or a mineral throughout the southern hemisphere. Many shallow histories start below the Curie point, leaving their earlier record unresolved. These are frequencies in a sampled, filtered model ensemble, not probabilities for the actual history of Mars.

**Limits.** No crustal growth, intrusions, impacts or fluids; the hot initial steady state is a declared choice; a Curie point is not a blocking spectrum and says nothing about billion-year retention; the accepted southern ensemble is small. Fast-cooled bodies are outside the model.

## Test 3 — The magnetization budget (cylinder-equivalent scenario)

**Method.** For each of the 295 usable source-depth windows, the area-weighted RMS |B| within 10° at 150 km is matched by the on-axis field of a single vertically magnetized cylinder of the fitted cap radius, for three declared layer geometries. This is a declared geometry scenario, not a demonstrated lower bound: the source model of Gong & Wieczorek (2021) is a stochastic ensemble of thin caps, and the window RMS and the on-axis field are different observation operators. The cancellation penalty divides by the median retained fraction from Test 4 at the nearest tested depth.

**Result** (20 km layer, A/m, 10/50/90%):

| Region | Windows | Cylinder-equivalent | Above 5 A/m | Above 20 A/m |
|---|---:|---|---:|---:|
| North | 107 | 0.2 / 1.0 / 4.2 | 7% | 0% |
| South | 188 | 0.9 / 4.2 / 17.8 | 43% | 9% |
| South, after Poisson cancellation, 100 Myr chrons | 188 | 3.1 / 15.9 / 81 | 81% | 42% |
| South, after Poisson cancellation, 0.67 Myr chrons | 188 | 41 / 208 / 1,028 | 100% | 97% |
| South, after periodic cancellation, 0.67 Myr chrons | 188 | 2,152 / 12,355 / 72,927 | 100% | 100% |

**Reading.** Several amperes per metre over 20 km are needed in this geometry, and slow cooling under a reversing dynamo multiplies that by tens to thousands depending on the reversal statistics. The 1, 5 and 20 A/m lines are comparison levels; material limits for Martian crust have not been established here.

## Test 4 — Coherence under a reversing dynamo

**Method.** For accepted histories from Test 2, the exact cooling kernel of each depth through a 150 K band below the magnetite Curie point is integrated against two reversal models: periodic chrons (16 phases) and Poisson chrons of the same mean duration (64 seeds per history), for mean durations 0.67–1,000 Myr. Medians, 95th percentiles and RMS of the retained fraction of a steady-field record are saved.

**Result** (south, magnetite band):

| Depth | Cooling through band (median) | Poisson, 0.67 Myr (median / 95%) | Periodic, 0.67 Myr | Poisson, 100 Myr | Poisson, 1,000 Myr | Half retention (Poisson) |
|---:|---:|---:|---:|---:|---:|---:|
| 20 km | 637 Myr | 2.2% / 6.3% | 0.05% | 30% | 100% | 500 Myr |
| 30 km | 774 Myr | 2.1% / 6.3% | 0.03% | 26% | 96% | 500 Myr |
| 40 km | 1,015 Myr | 1.7% / 5.4% | 0.02% | 22% | 78% | 500 Myr |

**Reading.** Steele et al. (2024) provide a conditional basin-model comparison motivating the tested rate near 1.5 reversals per Myr; it is not an independently measured universal Martian reversal rate. At that rate, slowly cooled crust keeps about 2% of a steady record if reversals are randomly timed, and far less if they are regular. This does not exclude slow cooling: 2% of a strong field is not zero, and reversal statistics may have differed between epochs. It does mean that a slowly cooled source needs tens of times more magnetization than a coherent one, which is what Test 3 quantifies. Bodies that cooled within a chron, or a dynamo with chrons of several hundred million years, avoid the penalty.

**Limits.** Uniform band, linear recording, no chemical or shock remanence, no relaxation, no activity windows, no spatial forward model coupled to the recording. Coherence statistics condition on complete band crossings and use at most 200 accepted histories per hemisphere. Percentiles describe this selected ensemble, not confidence bounds on Martian retention.

## Test 5 — Ground truth for the orbital model

**Method.** The Langlais et al. (2019) model is evaluated at the Zhurong (25.066° N, 109.926° E) and InSight (4.502° N, 135.623° E) sites at the reference sphere and the local MOLA radius, for truncations at degree 134, 110 and 90.

**Result.** At Zhurong the degree-134 model gives 79 nT total and 53 nT horizontal, reproducing the 81 and 55 nT published by Du et al. (2023); the rover measured 5.2–39.8 nT total and 11.2 ± 10.9 nT horizontal, so the model is about five times too high. At InSight the model gives 312 nT and the lander measured about 2,000 nT, about six times too low. Truncation at degree 90 changes the surface predictions by tens of percent.

**Reading.** At both sites where it can be checked, surface extrapolation of the orbital model fails by a factor of five to six, in opposite directions. Du et al. attribute this to unresolved structure and amplified model error. This is a demonstrated limit of local surface extrapolation, including for this project's earlier regional pilot; it is not an uncertainty distribution for every anomaly.

## Test 6 — Crustal thickness with laterally variable density

**Method.** An independent finite-amplitude gravity inversion with GMM-3 gravity and MOLA shape to degree 90, order 7 on a degree-719 grid, a minimum-amplitude filter at degree 50, the Bouguer degree-2 zonal term set to zero, and a 39 km anchor at InSight. Mass convention: the crust is the laterally variable-density shell between the mean Moho and mean surface radii (exact analytic integral, recomputed at every trial Moho radius), plus the surface relief with the crust density, plus the Moho relief with the contrast mantle − crust. The inversion is the regularised fixed-point scheme of Wieczorek & Phillips (1998, eq. 18); the filter multiplies the whole linear solution at every iteration and the run stops when the relief changes by less than 1 m. Checks: constant-density expansion equal to the pyshtools reference to 1e-13; shell term equal to its analytic integral; a body decomposed as shell + relief equal to the same body expanded as one relief; a degree-50 test relief returned with gain 0.500; the equal-density Mars inversion within 4.3 km RMS of the Wieczorek et al. (2022) archive grid (mean difference −3.2 km, maximum thickness 116 km in both).

**Result** (mean crustal thickness, km):

| Scenario (kg/m³) | North | South | South − north | Minimum | Iterations |
|---|---:|---:|---:|---:|---:|
| 2,900 / 2,900, mantle 3,382 | 39.2 | 63.3 | 24.1 | 5.1 | 17 |
| 2,622 north / 2,492 south (Goossens & Sabaka, 2026) | 34.9 | 43.3 | 8.4 | 9.3 | 15 |
| 2,900 north / 2,700 south | 35.9 | 42.4 | 6.6 | 0.9 | 21 |
| 2,700 north / 2,900 south | 39.9 | 81.2 | 41.4 | 16.2 | 22 |
| Goossens & Sabaka, mantle 3,500 | 34.6 | 42.6 | 8.0 | 11.0 | 14 |
| 2,900 / 2,900, mantle 3,500 | 37.9 | 58.1 | 20.2 | 9.6 | 15 |

**Reading.** Once the gravity of the variable-density shell is included, the density assumption controls the size of the thickness contrast: a southern crust lighter by 130–200 kg/m³ leaves 7–8 km, a denser southern crust gives 41 km. The sign never changes and no scenario produces vanishing crust. Origin models should propagate this sensitivity. Southern seismology, compositional constraints and improved gravity models could help reduce it.

**Limits.** Uniform mantle density, zero non-hydrostatic degree-2 zonal term, one anchor point. Densities are declared scenarios. The archive comparison is a consistency check for the equal-density scenario, not a complete validation of the inverse problem.

## What the six tests say together

1. Mapped surface age predicts part of the magnetic variation, while a hemispheric association remains for several epoch classes. The causal contribution of resurfacing is unresolved.
2. The tested slow-cooling and Poisson-reversal ensemble gives about 2% median retention at 30 km, with a 95th percentile near 6%. This is not a universal ceiling. The associated amplitude penalty remains conditional on the cylinder and recording assumptions.
3. Early computed Curie crossings become less frequent with depth in this ensemble. It establishes neither a hard 30 km source boundary nor a planet-wide mineral exclusion.
4. The cylinder-equivalent magnetization is several amperes per metre over 20 km; this is a comparison scale in a declared geometry, not a rock-type verdict.
5. The crustal thickness contrast is robust in sign and strongly dependent on the assumed densities: 7 to 41 km across the declared scenarios.

Unequal recording and preservation remain candidate explanations; a genuine difference between the hemispheres at equal surface age remains to be explained, by field geometry, by deep crustal composition or by what lies under the northern plains.

## Reproduction

```bash
python -m pip install -e '.[observations,research,test]'
python scripts/discriminating/build.py
python scripts/discriminating/audit_controls.py
python scripts/research/render_docs.py
python scripts/research/render_overview.py
python -m pytest -q -m 'not integration'
```

The build needs the local Langlais coefficients, Thiriet profiles and Wieczorek archive already used by the project, plus the GMM-3 gravity and MOLA shape coefficients that pyshtools downloads once from NASA PDS and Zenodo. It takes about 18 minutes; `--quick` gives a smoke test whose outputs must not be committed. Original implementations are in `src/marswind/crustinversion.py`, `agetransfer.py`, `crusthistory.py` and `amplitude.py`; declared parameters are in `discriminating/protocol.json`; every output hash is in `discriminating/manifest.json`; the audit's controls are regenerated by `audit_controls.py`.
