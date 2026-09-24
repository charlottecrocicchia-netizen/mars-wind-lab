# First observational diagnostics

**Executed analysis · 24 September 2026 · Exploratory, not a joint origin inference.**

The calculations now connect real public products. They test consistency and sensitivity; they do not identify the mechanism that formed the dichotomy. The [saved numerical results](data/results.json), [input manifest](data/manifest.json), [source registry](https://github.com/charlottecrocicchia-netizen/mars-wind-lab/blob/main/scripts/data/sources.json) and [pipeline](https://github.com/charlottecrocicchia-netizen/mars-wind-lab/blob/main/scripts/data/build.py) accompany this note.

## What is available

- MOLA global topography and the USGS geological map: **1,311 polygons, 44 units**.
- MGS/MAVEN crustal magnetic coefficients and **412 equivalent source-depth estimates**.
- The full 2.67 GB InSight crustal-model archive; four published grids from its Khan2022 family evaluated here.
- Northern and southern thermal profiles, plus additional thermal and elastic-thickness ensembles downloaded for subsequent work.
- **94 meteorite sample records**, **10 ejection-group entries**, **16 candidate craters**, the separate ejection-age compilation and the NWA 7034 isotope table.
- **1,073 laboratory measurements from 11 specimens** belonging to nine NWA 7034 paired stones.

The manifest records **115 downloaded products across 21 source entries**, including the later laboratory and water extension. The diagnostics below use selected products from that archive. This is a useful initial collection, not every observation made of Mars. Some downloaded ensembles and morphology products remain unanalyzed. The [mission inventory](MISSIONS.md) describes additional archives.

## 1. A common-altitude magnetic comparison

We evaluate the [Langlais et al. (2019) model](https://doi.org/10.1029/2018JE005854) at its full degree 134 on 2° cell centers. Radii are 3,393.5 km + 150 or 400 km. Schmidt semi-normalized coefficients and the SHTOOLS magnetic convention are retained; an analytic axial-dipole test verifies normalization and cubic radial decay.

Area-weighted means of the field magnitude use cosine-latitude weights. Regions follow the Andrews-Hanna boundary supplied in the [crust archive](https://zenodo.org/records/6477509), rasterized with the archive authors' spherical-mask method at 1° and sampled on the analysis grid. Tharsis is included.

| Comparison altitude | North mean | South mean | South / north |
|---|---:|---:|---:|
| 150 km | 21.68 nT | 81.77 nT | 3.77 |
| 400 km | 4.99 nT | 17.40 nT | 3.48 |

A latitude-only split yields ratios of 3.07 and 3.17; excluding ±20° gives 4.45 and 4.46. These checks expose sensitivity to region definition rather than selecting the largest contrast. The persistent contrast is consistent with different magnetic archives, different ancient fields, or both. It does not distinguish these causes. Grid cells are correlated; no p-values or confidence intervals are inferred from their count.

## 2. Source-depth quality before interpretation

The [Gong & Wieczorek data](https://zenodo.org/records/4686358) retain negative fits and missing-bound sentinels. Of 412 windows, 61 lack available intervals and 67 have a negative best fit; 11 belong to both categories. **295** have a nonnegative fit bracketed by published bounds.

This conservative subset does not mean all excluded regions are physically unmagnetized. Negative estimates may have intervals extending into the crust. Depths refer to the regional mean local surface, as clarified in the [paper](https://doi.org/10.1029/2020JE006690). The fitted source-cap radius and the 20° localization-window radius are separate quantities.

These overlapping windows and the orbital coefficients are dependent information. Equivalent thin-layer depths are neither magnetic-layer bottom depths nor Curie depths. Their uncertainty is retained in the output and figure.

## 3. A mineral-dependent thermal check

The [Thiriet et al. model endpoints](https://figshare.com/articles/dataset/_/5909929) are interpolated below each profile's own local surface. Each magnetic window is assigned the northern or southern profile by its center's side of the published boundary. Windows can span both regions, so this is a coarse screening assumption.

Illustrative ordering temperatures are 598.15 K for pyrrhotite, 853.15 K for magnetite and 943.15 K for hematite (Néel temperature in the latter case). They are endmember screening choices, not measured mineral compositions or blocking-temperature spectra. There is no extrapolation beyond a thermal profile.

| Region | Carrier | Best-fit depths below threshold | Entire nonnegative portion of depth interval below threshold | Model threshold depth |
|---|---|---:|---:|---:|
| North | Pyrrhotite | 107 / 107 | 73 / 107 | 95.3 km |
| North | Magnetite | 107 / 107 | 107 / 107 | 175.7 km |
| North | Hematite | 107 / 107 | 107 / 107 | 205.2 km |
| South | Pyrrhotite | 128 / 188 | 50 / 188 | 44.1 km |
| South | Magnetite | 188 / 188 | 152 / 188 | 90.7 km |
| South | Hematite | 188 / 188 | 183 / 188 | 116.5 km |

**A useful next hypothesis:** deep southern sources could require higher-ordering-temperature carriers than pure pyrrhotite, or a different thermal history/profile. Under this particular endpoint model, 60 of 188 southern best-fit depths exceed the pyrrhotite threshold. Only 13 southern windows have their entire nonnegative depth interval above the pyrrhotite threshold; 50 have it entirely below, leaving 125 straddling the threshold. These counts are conditional on the chosen endpoint profile and are not rejection probabilities.

A surviving ancient record must also pass time-dependent acquisition, relaxation, alteration, shock and cancellation tests. None is established by being cool enough today. The published southern “Min” and “Max” temperature files have identical checksums; we do not interpret them as a validated uncertainty envelope. Present models also cannot date magnetization.

## 4. Crustal density changes the interpretation

Four gridded examples from [Wieczorek et al. (2022)](https://doi.org/10.1029/2022JE007298) share a Khan2022 interior, 39 km InSight anchor and northern density 2,900 kg/m³. We sample their 0.25° node-registered grids at the analysis cell centers, then apply the same boundary and area weights.

| Southern density | North mean thickness | South mean thickness | South minus north |
|---|---:|---:|---:|
| 2,600 kg/m³ | 42.35 km | 40.00 km | −2.35 km |
| 2,700 kg/m³ | 42.55 km | 46.08 km | +3.53 km |
| 2,800 kg/m³ | 42.78 km | 54.33 km | +11.55 km |
| 2,900 kg/m³ | 43.06 km | 66.21 km | +23.15 km |

Within these examples, the sign and amplitude of the thickness contrast depend on density. Treating one thickness map as an independent, uniquely measured geological fact would conceal that tradeoff. These four examples are not the full ensemble and have no assigned probabilities.

## 5. Meteorites are contextual samples, not a global magnetic map

[Herd et al. (2024)](https://doi.org/10.1126/sciadv.adn2378) provides sample ages, conditional crater alternatives and five preferred associations. We retain all alternatives and add the Karratha hypothesis for NWA 7034 from [Lagain et al. (2022)](https://doi.org/10.1038/s41467-022-31444-8). Karratha is at 15.7° S, 203.6° E. Its source table's coordinate headings are inverted; the correction is explicit. No candidate becomes a confirmed provenance.

Crystallization uncertainties in Herd S1 are 2σ; group summaries in S3 use 1σ. Ejection, cosmic-ray exposure, terrestrial residence, breccia lithification and individual clast ages remain distinct. Multiple stones and group members are not independent locations. The isotope table preserves the original columns and dating systems without treating each date as a separate geological event.

The [Tanaka et al. surface map](https://doi.org/10.3133/sim3292) is joined at crater centers. Some centers fall in impact units while the source paper describes surrounding terrain; both labels are retained. Neither fixes the deep rock's mineralogy. Field values evaluated above a candidate are contemporary crustal-model predictions, not the meteorite's measured paleointensity.

The [MagIC laboratory data](https://earthref.org/MagIC/19658) are a particularly useful quality counterexample. [Vervelidou et al. (2023)](https://doi.org/10.1029/2022JE007464) identified terrestrial hand-magnet remagnetization in the nine paired stones. The interface shows archived moment by measurement order and retains method codes. Treatment amplitudes contain discontinuities in some sequences; no unverified unit correction or paleofield fitting is applied. Terrestrial find coordinates are never placed on the Mars map.

## What remains scientifically open

A source-depth inversion has been parsed, not independently re-inverted. The thermal endpoint comparison is not a coupled evolution model. Density sensitivity is not an origin likelihood. The next discriminating analysis is still the [acquisition and survival protocol](TEST_PROTOCOL.md): spatially matched source-volume uncertainty, carrier alternatives, time-dependent cooling, coherent remanence and withheld regional magnetic predictions.

Additional acquisitions should target calibrated InSight/Zhurong comparisons, GRS elemental products, CRISM mineral products and other paleomagnetic datasets. Local measurements and orbital inversions require separate observation operators and shared-error accounting. A surface abundance should not silently constrain an inaccessible deep carrier fraction.

## Reproduction and reuse

```bash
python -m pip install -e '.[observations,test]'
python scripts/data/acquire.py --large
python scripts/data/build.py
python -m pytest -q -m 'not integration'
```

The large archive requires several GB of local disk space. Raw downloads remain under ignored `data/observations/raw/`. The source manifest contains URLs, file sizes, SHA-256 and provider checksums where supplied. The result records the input-manifest, pipeline and numerical-module hashes and key package versions. All calculations are deterministic apart from the run timestamp; no Monte Carlo probabilities are generated here.

The code's MIT license does not replace source-data licenses. In particular, the Herd-derived meteorite table retains **CC BY-NC 4.0**; NASA/USGS public products, CC BY products and other sources retain their own terms. See [data licensing and conventions](data/README.md).

The later [laboratory extension](RECORDING.md) and [water/alteration screening](WATER.md) add explicit recording-process and fluid-history constraints. These additions do not change the previously computed global field and crustal contrasts.
