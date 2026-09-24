# Using Mars Wind Lab

Open the local application. The overview offers Ideas, Data, Tests, Library and Atmosphere. In **Data**, choose a map layer and a candidate crater, or use its Meteorite records, Lab magnetism, Water & alteration and Sources views. **Tests** shows executed diagnostics with methods tucked into expandable panels.

Select **Atmosphere** for the wind laboratory. An example above InSight is calculated when this section opens. These coordinates are a starting point, not an assimilation of InSight observations.

## 1. Choose a question

**Direction.** Compare the same thermodynamic state without advection, eastward and westward. The largest relative correction is identified among 141 altitudes in the chosen layer. Reversing direction exchanges the curves and changes the sign of projected wind. Nonpositive effective speeds need a more careful propagation treatment; do not integrate them as ordinary positive travel speeds.

**Season.** Choose A and B, keeping location, direction and local solar time fixed. The total change is the sum of wind and thermodynamic contributions. Compensation can explain a small total change. As a control, compare a season with itself: all three changes should be zero.

**Scales.** Change the reference period. From 100 s to 10 s, `λ₀/Hρ` decreases by exactly ten in the same atmosphere. A ratio comparable to 1 contradicts a short-wavelength assumption relative to the local density scale. A small ratio alone does not validate rays: other gradients, turning points and losses still matter.

## 2. Change, calculate, interpret

Choose a season and layer. Expand **Location and local time** for another site. Click **Run experiment**. Until the changed parameters have been computed, a banner identifies the stale result and the study-note export is disabled.

Read the conclusion and the three indicators. Extrema refer to the query grid, not exact atmospheric extrema. Altitudes are above the areoid: equal altitude does not imply equal height above local terrain across Mars.

The explanation below the plot describes axes and curves. **Turn it into a scientific decision** suggests a useful next test. Expand the assumptions beneath the result for the limits of the interpretation.

## 3. Keep and investigate the result

**Study note** downloads Markdown with the result, parameters, limitations, sources and calculation fingerprints. The plot’s camera button exports a PNG. **Explore this atmospheric column** transfers the parameters of the displayed result, never uncomputed form edits.

The atlas provides spatial context. Drag the **Altitude** slider above the map, then click the map once it updates. **Find the fastest sampled wind** selects the maximum horizontal speed on the current grid and opens its vertical structure. This point depends on altitude, season and time convention.

Experimental modes and archives are under **Advanced research**. Their interpretation requires the precautions in [Scientific method](SCIENTIFIC_METHOD.md).

## Local data configuration

`MCD_ROOT` points to a folder containing `mcd/MCD.F90` and `data/`. Compilation records this location in `build/mcd_build.json`, which is excluded from Git.

`MARS_LEGACY_ROOT` points to the folder containing `marslmd_modes_200km_fbvire`. These archives are required only for the archive view and historical reproduction script. With MCD installed, the rest of the laboratory works without them.

For persistent local configuration, a root-level `local_settings.json` may contain these two path keys. Git ignores this file. Environment variables take precedence. Recompile the adapter after changing the MCD source version.

## Mars in motion: direct controls and movies

The atlas is the opening screen. **Altitude** and **Season** sliders sit directly above the map. Drag either slider, type a number, or use the four northern-season shortcuts. The map updates after a short debounce; its label always identifies the last completed calculation. **Time & direction** contains the less frequently changed settings.

Choose **A Martian year** to hold altitude fixed and sample Ls 0–345° every 15°. Choose **Through the atmosphere** to hold season fixed and sample 10–200 km every 10 km. Press **Play** to prepare all frames and calculate one shared colour scale. A frame counter and progress bar show the calculation. An uncached sequence can take a few minutes. Preparation can be cancelled; the last completed map remains visible.

**Pause**, step buttons and the timeline let you examine individual frames. Slow/Normal/Fast correspond to 1/2/4 displayed frames per second. This is presentation timing: equal Ls intervals are not equal elapsed time, and an altitude sweep is not atmospheric evolution. Playback repeats. Changing physical controls clears the sequence to avoid reusing frames for a different experiment.

**Create video** prepares the sequence if necessary, then encodes a labelled H.264 MP4 with fixed colours, variable and units, frame parameters, time convention and MCD credits. A player appears under the timeline: press its Play control to watch, or **Download MP4** to save a copy. It uses a flat geographic map even if the interactive view is a globe. A sequence is sampled climatology, not a forecast or parcel trajectory. The player retains the last generated movie with its own parameter label even if you subsequently change the map controls. Browser video controls follow the browser/system language.

Guided experiments also have a continuous season slider and editable lower/upper altitude bounds. These define the column interval analysed by the experiment; they are separate from the altitude of an atlas map.

## Dichotomy research

Select **Library** in the navigation, or open `http://127.0.0.1:8765/research/library`. Open **Reading notes** for the synthesis or meteorite dossier, then use search and the expandable filters. The default collection contains 69 core records; switch to **All discovery candidates** to search the 1,981-record inventory. Reading-depth badges distinguish metadata, abstracts and selected full-text sections. A record in the catalog is not an endorsement of its conclusions.

Use **Export these results · RIS** to import the filtered bibliography into Zotero, or download the complete RIS/BibTeX/CSV files. The reading room includes missions and data, a concrete research programme, the search method and separately assessed forum leads. The research page needs no MCD installation and makes no model calls.

## Meteorite records and water–rock histories

Open **Data → Lab magnetism** and choose a meteorite. MIL 03346 is the default; ALH 84001 and the NWA suite also have measurements to inspect. Other entries show sourced published results and clearly state that raw series have not yet been acquired. The sample selector is separate from the specimen selector. Open **Inspect laboratory directions** only when you need that additional detail. The directions are laboratory-relative, not geographic coordinates on Mars.

Choose Lafayette to see crystallization and aqueous alteration as separate events. “Secondary” describes a later recording event; it can still have occurred on Mars. Follow the recording guide for the distinction from terrestrial contamination.

Open **Data → Water & alteration**, choose a mineral class and instrument, then switch between elevation and the crustal magnetic-field background. Markers denote occupied 2° cells. They do not fill the entire cell with altered rock, and an unmarked cell is not a dry control. **Tests**, diagnostic 06, records the descriptive overlap and explains what is still needed for a physical association test.
