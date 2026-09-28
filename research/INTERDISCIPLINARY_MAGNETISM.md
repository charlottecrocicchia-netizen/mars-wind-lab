# Paleomagnetism inside the whole Mars problem

**Interdisciplinary review · 28 September 2026**

[Synthesis](INTERDISCIPLINARY_SYNTHESIS.md) · [Chronology](INTERDISCIPLINARY_CHRONOLOGY.md) · [Tests](INTERDISCIPLINARY_TESTS.md) · [Sources](INTERDISCIPLINARY_SOURCES.md)

The target is the history of a **field recorded by particular minerals**, later modified and observed through a particular instrument. A magnetic anomaly, a magnetic mineral and a paleofield estimate are different evidence. This dossier connects the existing [paleomagnetism guide](PALEOMAGNETISM_FOUNDATIONS.md), [recording notes](RECORDING.md) and [meteorite inventory](METEORITES.md) to the broader planetary history.

## The evidence chain

Ancient field → acquisition by a mineral generation → survival through subsequent events → remaining magnetization → measured laboratory or planetary signal.

The inverse problem runs against that chain. Missing information at any step can allow several field histories to fit the same observation. The [Essentials of Paleomagnetism](https://pmagpy.github.io/Essentials-JupyterBook/) chapters on mineralogy, remanence and paleointensity provide the physical foundation; selected passages were read, not the entire book.

| Evidence | Direct measurement | Necessary interpretation | Cross-disciplinary control |
| --- | --- | --- | --- |
| Orbital magnetic model | Spacecraft magnetic observations represented by a field model | Separation of external fields, spatial bandwidth and source geometry | Source depth, buried geology, altitude and common mission data |
| Rover magnetic survey | Local field along a traverse | Local crustal signal after instrumental/environmental corrections | Lithology, survey footprint, regolith and deeper structure |
| Laboratory component | Remanence change under demagnetization; direction in sample coordinates | Carrier, acquisition process and overprint removal | Petrography, thermal/chemical history and handling |
| Paleointensity experiment | Relationship between natural remanence and calibrated laboratory acquisition | Suitable recording physics and correction for experimental biases | Alteration checks, grain behaviour, anisotropy and cooling history |
| Magnetic mineral identification | Mineralogical or chemical evidence | Ability to acquire and preserve a signal | Grain structure, oxidation state, growth age and subsequent reactions |

Orbital examples: [Langlais et al.](https://doi.org/10.1029/2018JE005854), [Gong and Wieczorek](https://doi.org/10.1029/2020JE006690). Local rover example: [Du et al.](https://doi.org/10.1038/s41550-023-02008-7). Mineral assessment for future samples: [Mansbach et al.](https://doi.org/10.1029/2024JE008505).

## What changes when we include petrology and water?

For a thermal remanence, cooling and blocking behaviour matter. Chemical growth can record a field without cooling from a melt; later alteration can replace or erase carriers. Heating, shock and terrestrial handling add other possible changes. Mineral identity alone cannot settle which process dominates. These distinctions follow the acquisition and paleointensity chapters of [Tauxe and collaborators](https://pmagpy.github.io/Essentials-JupyterBook/).

The hydrothermal zircon illustrates the separation clearly: evidence of ancient fluids and magnetite inclusions does not establish that those inclusions preserve a measurable primary field. [Gillespie et al.](https://doi.org/10.1126/sciadv.adq3694) Lafayette supplies an alteration date but no magnetic acquisition date from that dating experiment. [Tremblay et al.](https://doi.org/10.7185/geochemlet.2443)

Hydrothermal activity can have different magnetic outcomes depending on temperature, reactions and whether a field is present during acquisition. Mittelholz et al. explore geological interpretations of jointly inverted gravity and magnetic structure. Their coupling regularization encourages structural association: the association cannot also be counted as wholly independent proof of a shared process. Separate inversions, coupling-strength sensitivity and alternative geological explanations are essential controls. [Mittelholz et al.](https://doi.org/10.1029/2024JE008832)

## What weak basins do and do not tell us

Weak orbital fields can be compatible with several histories: little magnetic material, an unfavourable acquisition field, cancellation during changing field polarity, deep or buried sources, later thermal/chemical changes, or combinations of these. They are hypotheses to compare with explicit recording calculations, not a list that automatically explains every basin.

Cooling-in-reversal simulations demonstrate one route to weak basin-scale signals within the sizes and physical assumptions modelled. Extrapolating that result to a Borealis-sized event requires a new calculation. [Steele et al., 2024](https://doi.org/10.1038/s41467-024-51092-4) Full-sphere dynamo simulations supply a distinct alternative involving asymmetric core heat loss. A successful field morphology still needs a compatible recording timescale. [Yan et al., 2025](https://doi.org/10.1029/2024GL113926)

## What the selected meteorites allow

| Sample or study | Admissible use here | Excluded shortcut |
| --- | --- | --- |
| ALH 84001, Steele et al. 2023 | Magnetic components support an interpretation involving an ancient, potentially reversing field, conditional on event history | Turning every component into an independently dated global polarity or absolute planetary direction |
| MIL 03346, Volk et al. 2021 | Investigate a young recording with a possible local crustal-field source | Equating a young remanence with a young core dynamo |
| Tissint, Gattacceca et al. 2013 | Compare mineral carriers, magnetic properties and acquisition interpretations | Setting acquisition age equal to crystallization age without the event argument |
| Nine investigated NWA 7034 paired stones, Vervelidou et al. 2023 | Use the reported overprints to control the reliability of their magnetic archive | Rejecting all their geochemistry, or assuming all untested stones are equally compromised |
| Perseverance mineral observations, Mansbach et al. 2024 | Identify promising carriers and future sample tests | Claiming a laboratory paleofield was already measured from returned samples |

References: [Steele](https://doi.org/10.1126/sciadv.ade9071), [Volk](https://doi.org/10.1029/2021JE006856), [Gattacceca](https://doi.org/10.1111/maps.12172), [Vervelidou](https://doi.org/10.1029/2022JE007464), [Mansbach](https://doi.org/10.1029/2024JE008505). The source ledger distinguishes fresh consultation from earlier project assessments reused for these entries.

## Admission rules for a future quantitative reconstruction

These are proposed project controls, not a claim that the cited studies fail them. A record can remain useful for mineralogy or chronology even when it cannot constrain paleointensity.

1. Preserve specimen identity, paired-stone/ejection relationships and handling history. Count independent acquisition events separately from measurement replicates.
2. Identify the magnetic component, carrier evidence and candidate acquisition mechanism. A straight demagnetization segment alone is insufficient.
3. Keep formation, alteration and acquisition ages separate, including alternate interpretations and stated uncertainty conventions.
4. For intensity, record calibration, repeat measurements and the relevant alteration, anisotropy, cooling-rate and grain-state checks. Missing checks remain missing; this review supplies no universal acceptance threshold.
5. Distinguish specimen coordinates, relative within-rock directions and any reconstructed planetary frame. Record shock and rotational uncertainties.
6. Keep local crustal and core-dynamo field hypotheses available where the experiment does not distinguish them.
7. Forward-predict the observation at its altitude, spatial scale and instrument response. A fit to a derived map is not an independent fit to the underlying observations.

No new paleointensity value, polarity timescale or dynamo shutdown date is inferred by this review. The immediate deliverable is an evidence chain that lets paleomagnetism constrain the **same** material, water and thermal history as the other disciplines.
