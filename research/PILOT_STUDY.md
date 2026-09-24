# Regional recording pilot: the comparison changes the interpretation

**Completed exploratory analysis, 24 September 2026.** Four primary craters in three regional settings, plus one flagged Ladon window. No unique remanence history or origin of the Martian dichotomy is selected.

With the local server running: [start the guided study](http://127.0.0.1:8765/research/pilot) · [explore regions](http://127.0.0.1:8765/research/pilot/regions) · [compare histories](http://127.0.0.1:8765/research/pilot/hypotheses) · [method](http://127.0.0.1:8765/research/pilot/method) · [results](http://127.0.0.1:8765/research/pilot/results)

## Question and scope

Do crater interiors have the same sign of orbital magnetic contrast, and does that sign survive changes in altitude, reference terrain and mapped surface geology? This is a necessary measurement audit before fitting competing recording histories. A magnetic field measured above the surface is not the magnetization of a particular rock, nor the ancient field that magnetized it.

The cases are motivated by [Mittelholz et al. (2025)](https://doi.org/10.1029/2024JE008832). Their hydrothermal interpretation motivates the selection; our amplitude ratios do not reproduce their joint density–magnetization inversion. The cases are literature-selected, not independent wet/dry controls or a representative sample of Mars. Newton and Copernicus belong to the same Eridania setting.

## What was calculated

The [protocol](pilot/protocol.json) specifies the primary comparison and sensitivity settings, fixed before the first regional calculation. This is not a preregistered or confirmatory study.

- Evaluate all degree-134 coefficients of the [Langlais et al. magnetic model](https://doi.org/10.1029/2018JE005854) at 130, 150 and 400 km above its 3393.5 km reference sphere. Take the magnitude at each point before averaging. These are three evaluations of one model, not independent datasets.
- Sample on a 0.5° grid, weighting latitude–longitude cells by cos(latitude). The sampling interval does not establish physical resolution or an independent observation count.
- Divide mean field inside 0.8 R by mean field in a reference ring 1.2–2 R, where R is half the catalog diameter. The ring is not assumed to be unaltered.
- Repeat for 81 combinations of altitude, inside radius, reference ring and catalog-radius factor per case. Also omit each of eight azimuthal sectors and separately exclude other catalog crater interiors ≥150 km from the reference ring.
- Standardize the reference to the interior's proportions of common [USGS surface map units](https://doi.org/10.3133/sim3292). This is descriptive stratification. It does not control deep lithology, exact age, exposure or heating; surface units can themselves reflect the impact or alteration being studied.

For common units u, the standardized ratio is

`sum(A_inside,u × mean(B_inside,u)) / sum(A_inside,u × mean(B_outside,u))`.

Only units with samples on both sides enter the sum. The retained fraction of interior area is reported. Unmatched terrain is never assigned a synthetic control value.

### Source geometry audit

Four crater geometries were checked against acquired IAU/USGS Gazetteer pages, using **MDIM 2.1, planetocentric, east-positive** values: [Newton](https://planetarynames.wr.usgs.gov/Feature/4236), [Copernicus](https://planetarynames.wr.usgs.gov/Feature/1297), [Huygens](https://planetarynames.wr.usgs.gov/Feature/2596), and [Schiaparelli](https://planetarynames.wr.usgs.gov/Feature/5366). Circular apertures approximate the features; they are not traced geological boundaries.

The large Ladon-region entry `19-000000` in the [versioned author-hosted revised crater catalog](https://github.com/alagain/martian_crater_database/tree/ccd5de7bbc6525d25d746332b4a1e58ba1f72680/Global) is labelled **Misidentified**. We preserve the flag, retain its coordinates and diameter only as an exploratory regional window, and exclude it from primary crater conclusions. This is a catalog-quality flag, not a claim that all geological interpretations of Ladon are invalid. Its large footprint also makes it unsuitable as a size-matched control for the other cases.

### Published-method transfer and numerical checks

The radial depth diagnostic follows the recipe in Mittelholz et al.: sample azimuths every 30°, take their median profile, use the minimum within 0.2 R and the outer median at 1–1.2 R, and divide the depth difference by diameter. Here we use the local [MOLA 4 ppd MEGDR](https://pds-geosciences.wustl.edu/missions/mgs/megdr.html), bilinear interpolation and fixed catalog rims; sensitivity varies radius and azimuth spacing. Their visual rim adjustment, full gravity selection and joint inversion are **not reproduced**. Their inversion regularization favours related density and magnetization patterns; those inferred relationships cannot be counted as wholly independent confirmation.

Four direct magnetic evaluations agree with the existing atlas within its 0.001 nT rounding. Analytic tests separately check a known radial bowl, invariance to a vertical datum shift, spherical distances and longitude wrapping, map-unit selection effects, and missing common support. These validate calculation behavior, not the geological mechanisms.

## Results

| Case | Raw ratio, 150 km | Same-unit ratio, 150 km | Interior retained | Raw range over all 81 settings |
|---|---:|---:|---:|---:|
| Newton | 0.778 | 1.448 | 100% | 0.606–0.881 |
| Copernicus | 0.771 | 0.746 | 100% | 0.568–0.839 |
| Huygens | 0.463 | 0.384 | 100% | 0.262–0.922 |
| Schiaparelli | 0.951 | 1.707 | 34.7% | 0.864–1.523 |
| Ladon window — sensitivity only | 0.340 | 0.386 | 100% | 0.263–0.791 |

The full-precision saved values and every setting are in [results JSON](pilot/results.json) and [contrasts CSV](pilot/contrasts.csv). The [scientific figure](pilot/regional_pilot.png) is also available as [SVG](pilot/regional_pilot.svg). Ranges are **sensitivity envelopes, not confidence intervals**. No coefficient covariance, independent regional sampling distribution or inferred uncertainty on a physical history is supplied.

**Newton is sensitive to the geological reference mixture.** Its raw interior mean is about 135.0 nT, versus 173.5 nT in the ring. Giving the ring the interior's common-unit proportions reverses the ratio. This does not make the standardized value a uniquely correct estimate of the impact's effect: the strata remain spatially structured, and the map describes surface units rather than magnetic source volumes.

**Schiaparelli is sensitive to observation scale and common support.** Its raw ratio increases from 0.870 at 130 km to 1.367 at 400 km. Upward continuation changes the relative contribution of spatial wavelengths; the three measurements cannot be interpreted as distinct geological events. About 65% of the interior lacks the same map unit in the reference ring. The standardized ratio describes the remaining terrain, not the full crater.

**Copernicus and Huygens provide more stable contrasts to explain.** Both raw and standardized ratios remain below one over all 81 settings for each case. Baseline sector omissions and the additional large-crater reference screen also leave these ratios below one. This stability applies only to the tested model and choices; it does not establish removal of magnetization or identify its cause.

## What can be decided about the histories?

The restrictive observable rule “all primary crater interiors are stronger” is contradicted at the baseline. “All are weaker” agrees with that baseline but does not survive every altitude and comparison choice. Neither rule is a forward model of thermal or chemical evolution.

| Recording history | Required distinguishing constraint | Current verdict |
|---|---|---|
| Early remanence preserved | Dated carrier/component and a compatible survival history | Not identifiable from orbital amplitude alone |
| Later thermal resetting | Blocking spectrum and time–temperature path consistent with other surviving records | Not fitted; remains possible |
| Chemical rebuilding | Mineral-generation age, reaction path and component linked to that generation | Not fitted; remains possible |

Meteorites supply mechanism and event-order constraints, not automatic geographic labels. [MIL 03346](https://doi.org/10.1029/2021JE006856) helps assess interior versus fusion-crust records; [Tissint](https://doi.org/10.1111/maps.12172) illustrates a proposed post-shock acquisition history; [ALH 84001](https://doi.org/10.1126/sciadv.ade9071) supplies ancient carrier-scale records. Lafayette's [742 ± 15 Ma alteration date](https://doi.org/10.7185/geochemlet.2443) is kept separate from crystallization and magnetic-component ages. Unknown source locations remain unknown, and local crustal fields remain alternatives to a late core dynamo. The [recording guide](RECORDING.md) explains primary/secondary remanence and contamination, drawing on Gattacceca, Clara Maurel, Roger Fu, Benjamin Weiss and collaborators' studies.

## Why a water-effect estimate is still unavailable

[MOCAAS](https://www.ias.u-psud.fr/moccas/) supplies positive mineral detections. The paper [Carter et al. (2023)](https://doi.org/10.1016/j.icarus.2022.115164) describes coverage products and limitations, but no usable survey/exposure mask was acquired from the ten-raster archive or listed global downloads. A generic CRISM footprint alone would not specify dust, burial, analyzed observations or mineral detectability. We therefore neither label blank cells dry nor fit a water–magnetism regression.

The maps show presence-only 2° occupancy as context. They do not establish the altered volume, fluid-event age or magnetic carrier content. Native mineral-map georeferencing and latitude conventions have not been independently validated for precise deposit-scale association. These coarse markers never enter the magnetic estimand.

## Physical interpretation and the next discriminating evidence

Our working strategy is to constrain **recording and preservation before inferring ancient field asymmetry**. This pilot supports the need for that strategy; it does not demonstrate a particular recording history. Copernicus and Huygens are priorities for geometry-constrained source modeling, while Newton and Schiaparelli are useful tests of geological and spatial-scale dependence.

A subsequent physical model needs regional age and carrier constraints, time-dependent thermal or reaction paths, observation coverage, and a consistent magnetic source geometry. Only then can histories be fitted and evaluated on a region withheld from fitting. No held-out physical prediction has been made here. Origin mechanisms for the crustal dichotomy remain separate, unresolved hypotheses; later magnetic modification need not have created the original crustal contrast.

## Reproduction and attribution

From the repository root, after the base observation acquisition/build:

```bash
python -m pip install -e '.[observations,research,test]'
python scripts/data/acquire_pilot.py
python scripts/data/build_pilot.py
python scripts/research/render_pilot.py
python -m pytest -q -m 'not integration'
```

The [additional source manifest](pilot/sources.json), protocol and output provenance include input/code hashes. The build is offline and deterministic apart from serialization changes caused by software versions; versions are recorded. Original third-party archives and source HTML remain local. The public products are project-computed numerical summaries, figures and original explanatory text; underlying dataset terms are separate from the repository's code license. This is a personal research prototype by Charlotte Crocicchia, developed with AI assistance, not a peer-reviewed result.
