# Using Mars Wind Lab

Open the local application. An example above InSight is calculated on startup. These coordinates are a starting point, not an assimilation of InSight observations.

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

The atlas provides spatial context. Choose an altitude under **Explorer settings**, update, then click the map. **Find the fastest sampled wind** selects the maximum horizontal speed on the current grid and opens its vertical structure. This point depends on altitude, season and time convention.

Experimental modes and archives are under **Advanced research**. Their interpretation requires the precautions in [Scientific method](SCIENTIFIC_METHOD.md).

## Local data configuration

`MCD_ROOT` points to a folder containing `mcd/MCD.F90` and `data/`. Compilation records this location in `build/mcd_build.json`, which is excluded from Git.

`MARS_LEGACY_ROOT` points to the folder containing `marslmd_modes_200km_fbvire`. These archives are required only for the archive view and historical reproduction script. With MCD installed, the rest of the laboratory works without them.

For persistent local configuration, a root-level `local_settings.json` may contain these two path keys. Git ignores this file. Environment variables take precedence. Recompile the adapter after changing the MCD source version.
