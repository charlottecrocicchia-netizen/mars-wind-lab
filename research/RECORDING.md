# Reading a rock's magnetic history

The useful question is not simply whether a meteorite is magnetic. It is **which mineral generation recorded which field, during which event, and what survived afterward**.

## Primary and secondary are relative to an event

A primary remanence accompanies the event being studied, often igneous cooling. A secondary remanence is acquired later. It can be a valuable record of alteration or reheating **on Mars**. Terrestrial contamination is a separate branch: atmospheric entry, weathering, prolonged storage in Earth's field, handling and strong magnets.

| Process | What happens | What must be checked |
|---|---|---|
| Thermoremanence (TRM) | Magnetic grains record a field during cooling through their blocking range | Carrier, domain state, cooling rate, anisotropy and subsequent heating |
| Partial TRM | Heating resets only part of the blocking spectrum | Temperature **and duration**, surviving components and event age |
| Chemical / thermochemical remanence (CRM / TCRM) | Mineral growth or transformation changes the magnetic recorder | Petrographic generation, reaction conditions, age and acquisition efficiency |
| Shock / pressure effects | Pressure can erase or impart remanence; later cooling can record another field | Shock intensity, localized melt, carrier transitions and cooling history |
| Viscous remanence (VRM) | Magnetization changes with time in an ambient field | Relaxation times, storage history and stability over the relevant timescale |
| Isothermal remanence (IRM) | Strong-field exposure changes remanence without heating | Handling history and magnetic contamination tests |

High coercivity or high unblocking temperature alone does not prove antiquity. A hand-magnet overprint may persist into high-temperature demagnetization. Blocking temperature is not identical to a mineral's Curie or Néel temperature. These are central cautions from [Gattacceca, Maurel, Hutzler, Rochette & Weiss (2025)](https://doi.org/10.1007/s11214-025-01194-2); the curation and contamination sections were consulted.

## Three cases with different meanings

**MIL 03346 — test the interior against the fusion crust.** Volk, Fu, Mittelholz & Day report a coherent high-coercivity interior component, distinct from the fusion-crust overprint, and favour thermal acquisition during emplacement. They discuss possible thermochemical contributions. Their field estimate can be explained by crustal magnetism without requiring a late dynamo. [Primary study](https://doi.org/10.1029/2021JE006856), [open experiments](https://doi.org/10.7910/DVN/S0R98P).

**Tissint — a secondary Martian record.** Gattacceca et al. interpret its remanence as recording cooling after shock, before ejection. Assigning this signal directly to the igneous age would conflate two events. [Primary study](https://doi.org/10.1111/maps.12172).

**ALH 84001 — several ancient components.** Steele, Fu et al. use mineral-scale observations and heating/shock constraints to interpret a complex record, potentially including reversals. A single bulk direction or a single rock age does not capture that history. [Primary study](https://doi.org/10.1126/sciadv.ade9071), [MagIC archive](https://earthref.org/MagIC/19859).

The site now lets you [select these and other meteorites](/research/data?view=laboratory). The NWA paired-stone contamination experiment remains accessible as a distinct case, not as a representative sample of all Martian meteorites.

## What was added and what remains unknown

The [curated inventory](data/paleomagnetism.json) includes all 15 entries of Weiss et al. (2025), SI Table S1, and the separate NWA contamination suite. This includes Antarctic MIL, ALH, EETA, LEW, GRV and Yamato samples, as well as named falls/finds. The synthesis's approximately 18 studied pairing groups are a different population from its 15-entry paleointensity table. Neither is a census of all Martian stones. See the [source synthesis, coauthored by Clara Maurel](https://doi.org/10.1073/pnas.2404259121).

The 94-record chronological compilation, this paleointensity table, and the individual laboratory specimens have different selection criteria. A stone absent from one dataset is not absent from Mars research. MIL 090030, MIL 090032 and MIL 090136 are retained as pairs mentioned by the MIL study; measurements of MIL 03346 must not be relabelled as measurements of those stones.

The table retains upper/lower bounds, missing errors and the original age conventions. Many non-thermal paleointensities have additional empirical calibration uncertainties; their reported errors cannot be pooled as comparable Gaussian standard deviations. ALH's 75 Ma uncertainty has a superscript footnote in the PDF; it is not 752 Ma. The MIL age in the synthesis differs from ages in other studies. We retain that difference rather than silently harmonizing it.

## Reproducible laboratory views

- **MIL:** all 25 selected bulk experimental files were acquired from Harvard Dataverse, CC0. Ten natural-remanence files are parsed; ARM, IRM, anisotropy, FORC and other rock-magnetic experiments remain separately archived. Exported magnitude units are not explicit, so the plot uses magnitude divided by the first value. AF and thermal treatment labels are preserved verbatim.
- **ALH:** the MagIC 19859 ZIP includes the contribution table and magnetic maps. The site parses its 492 fitted-source records and lets users inspect natural-remanence series separately from laboratory acquisition. Full QDM maps remain local; no new inversion or component fit is claimed. Zero location placeholders are never used as Martian coordinates.
- **NWA suite:** MagIC 19658 contributes 1,073 measurements across 11 specimens from nine paired stones. Known treatment-label discontinuities remain flagged.

Acquisition order is used consistently to avoid assuming equivalent treatment spacing. Directions are in laboratory frames. They cannot supply Martian latitude, longitude or absolute paleodirection. The curves are an audit interface, not a new paleointensity estimator.

## How to turn this into a physical test

For each component, require a carrier, acquisition mechanism, event-age constraint, source-field alternatives and survival tests. A useful joint model must predict the observed component sequence, not just the total moment. Distinguish core dynamo, local crustal and external fields. Reject a history when it requires a dated mineral to record a field before that mineral existed, or to preserve a component through an incompatible reset.

The next laboratory step is a documented, specimen-specific component analysis with quality criteria, anisotropy and calibration uncertainties. No new fitted directions, paleointensities or dynamo dates are reported here.
