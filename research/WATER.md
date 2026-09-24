# Water, alteration and the dichotomy

Our working question is whether different thermal and chemical histories changed **the ability of northern and southern rocks to record and retain magnetization**. This can connect water to the magnetic dichotomy without assuming that water created the original crustal contrast.

## A physical branch with competing outcomes

Water–rock reactions can create magnetic minerals, transform existing carriers or destroy them. Heating, fluid chemistry, oxygen fugacity, permeability and the availability of a field determine the result. “Water removes magnetism” is therefore not a universal law. Nor does a hydrated surface mineral automatically identify a deep magnetic source.

This mechanism has published precedents. [Mittelholz et al. (2025)](https://doi.org/10.1029/2024JE008832) compare gravity, magnetism and potentially hydrothermal regions, discussing thermal, chemical and radiogenic controls. Those interpretations motivate regional tests; they do not establish a unique origin for the global dichotomy.

## New orbital data: MOCAAS

The November 2023 [MOCAAS archive](https://www.ias.u-psud.fr/moccas/) is downloaded and processed: five mineral-class maps from OMEGA/Mars Express and five from CRISM/MRO. The classes include Fe/Mg clays, Al clays/hydrated silica, sulfate groups, and carbonate/locally serpentine signatures. The map preserves the source's class ambiguities. [Carter et al. (2023)](https://doi.org/10.1016/j.icarus.2022.115164).

The [interactive water view](/research/data?view=water) compares those detections with topography or the crustal field at 150 km. A 2° marker means at least one native detection in that cell. It is neither a deposit centroid nor the altered fraction of the cell. Every nonzero raster pixel is included before aggregation, and instrument overlaps are unioned.

The [numerical product](data/water.json) records input hashes, processing code hashes and occupied cells. Original rasters remain local because the archive does not state an explicit reuse license. We publish a coarse project-computed occupancy summary and the retrieval/processing code.

### What the completed overlap diagnostic means

For each mineral class, we calculate the minimum, median and maximum modeled field at occupied display-cell centers. These are descriptive values, without significance or causal interpretation. They do not compare wet and dry areas: **non-detection is not an observed absence of alteration**. The maps do not provide a complete survey/exposure mask. Dust, burial, observation targeting and surface age can confound an apparent relationship.

This audit identifies what must be supplied before a hypothesis test is valid. Reporting an attractive correlation at this stage would confuse the observation process with geology.

## A separate clock inside a meteorite

[Tremblay et al. (2024)](https://doi.org/10.7185/geochemlet.2443) date Lafayette iddingsite alteration to **742 ± 15 Ma (2σ)**. The authors interpret local, transient activity; the result is not evidence for a global ocean at that time. Keep this event separate from the rock's much older crystallization and its later ejection. It does not automatically date Lafayette's magnetic component. The [Lafayette entry](/research/data?view=laboratory&sample=lafayette) shows these clocks separately.

Fluid histories can be constrained through mineral assemblages and chemistry as well as age. [Bridges & Schwenzer (2012)](https://www.sciencedirect.com/science/article/pii/S0012821X12005407) model the nakhlite hydrothermal brine. Such modeled conditions are conditional constraints, not direct thermometer measurements from every nakhlite.

## Three explicit alternatives to test

| History | Prediction | Observation that would challenge it |
|---|---|---|
| Retention of early remanence | An early component survives in carriers unaffected by later fluids/heating | That carrier generation was destroyed or formed after the proposed recording event |
| Chemical rebuilding | New mineral generations carry a later, distinguishable component | The remanence predates mineral growth, or required fluid chemistry cannot produce the carrier |
| Thermal resetting with limited chemical change | Reset follows blocking spectrum and time–temperature exposure | The thermal history cannot reset the observed component while preserving independently dated material |

These are recording histories, not mutually exclusive global origin theories. Impact excavation, impact-driven crust production and internal growth must each supply compatible histories of heat, fluids, carriers and fields. Mixtures must be constrained by geology; assigning a free history to every pixel would make any origin fit.

## The next discriminating analysis

1. Start with bounded regions such as Eridania, Huygens, Ladon and Schiaparelli, checking the published hydrothermal interpretations against original mineral products. Include regional controls, not only visually striking anomalies.
2. Obtain a survey/exposure mask and stratigraphic constraints. Compare like lithology and age at a common magnetic altitude and bandwidth. Treat spatial blocks, not neighboring pixels, as the replication scale.
3. Compare carrier-growth, thermal-reset and unchanged-carrier forward models. Propagate uncertain alteration ages, depth, mineral abundance, field history and acquisition efficiency.
4. Withhold regions for prediction. A chemical branch is justified if it explains those observations better under defensible constraints, not merely because extra free parameters improve an in-sample fit.

**Status:** data ingestion and descriptive overlap completed. Coverage-controlled association, reaction/transport modeling and joint origin inference remain unperformed.

## Other evidence that belongs in the same history

| Evidence stream | Role in the joint model | Current project status / next constraint |
|---|---|---|
| Crust, gravity, topography | Initial structure, loading and density–thickness tradeoffs | Global products ingested; expand beyond four crust examples |
| Seismology and tidal response | Present interior endpoints | Literature assessed; avoid imposing today's temperature on ancient crust |
| Radiogenic elements and geochemistry | Heat production, melt sources and carrier supply | Meteorite chemistry and literature available; GRS quantitative join still needed |
| Impact and ejection chronology | Heating, excavation, mixing and provenance | Chronology and candidate craters ingested; candidates remain conditional |
| Mineral alteration and isotope ages | Fluid processes and event ordering | MOCAAS ingested; Lafayette age curated; full mineral-age database incomplete |
| Valleys, lakes, deltas and erosion | Surface transport, deposition and boundary modification | Literature leads; dated geomorphic catalog and exposure controls still needed |
| Ice and radar structure | Water reservoirs, burial and present distribution | Mission archive inventory; no radar/ice inversion incorporated yet |
| Atmosphere and escape | Water loss, pressure history and climate boundary conditions | Present MCD atmosphere available; ancient escape histories are not fitted |
| Volcanism and tectonics | Resurfacing, intrusive heating, permeability and stress | Geologic units ingested; event-resolved regional histories still needed |

These streams share measurements and assumptions. For example, several magnetic products use the same spacecraft observations, and paired meteorites can share one ejection. A joint analysis must track these dependencies instead of counting each paper as an independent vote. “A theory that fits the puzzle” should mean a model that survives incompatible constraints and predicts withheld observations, not one flexible enough to accommodate everything afterward.
