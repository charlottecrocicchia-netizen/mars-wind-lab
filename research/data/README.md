# Observation snapshot: provenance, units and licenses

These compact products accompany [the first diagnostics](../FIRST_RESULTS.md). They can be served locally without MCD or the raw scientific archives. Download and processing recipes are in `scripts/data/acquire.py` and `scripts/data/build.py` at the repository root.

| File | Meaning and convention | Source / reuse |
|---|---|---|
| `manifest.json` | Versioned acquisition metadata; URL, local relative path, access time, SHA256, provider checksum verification | Source-specific license recorded for each entry |
| `atlas.json` | 2° cell-center grid, planetocentric latitude, 0–360° east longitude | Multi-source derivative; retain all below attributions |
| `depths.json` | Equivalent depth below regional mean surface, km; separate source-cap radius and 20° localization window | Gong & Wieczorek (2021), Zenodo 4686358, CC BY 4.0 |
| `thermal.json` | Published modeled temperatures (K) and depth below each profile's local surface (km) | Thiriet et al. (2018), figshare 5909929, CC BY 4.0 |
| `meteorites.json` | Sample/group/crater facts; individual uncertainty conventions retained; also original age/isotope table rows | Herd et al. (2024) portions **CC BY-NC 4.0**; Lagain et al. (2022) CC BY 4.0; Zenodo age compilation CC BY 4.0 |
| `laboratory.json` | Archived moments (A m²), treatment amplitudes (T), method codes and specimen IDs; no paleointensity reconstruction | Vervelidou et al. (2023), MagIC 19658, CC BY 4.0 |
| `results.json` | Deterministic diagnostic results with run time and input/code checksums | Project-derived results; retain underlying attribution |
| `first_diagnostics.png`, `.svg` | Exportable scientific figure, including candidate positions | Multi-source derivative including Herd candidate locations; retain **CC BY-NC 4.0** restriction |

## Map-specific conventions

- **Topography:** NASA MGS MOLA MEGDR `megt90n000cb`, IAU2000, areoid-relative elevation. Original 720 × 1440, signed big-endian 16-bit meters; 8 × 8 arithmetic block means for display, converted to km. This is not planetary radius or crustal thickness.
- **Magnetism:** Langlais et al. (2019), Zenodo 3876714, CC BY 4.0. Full degree/order 134, Schmidt semi-normalization; evaluated at radii 3,543.5 and 3,793.5 km. Scalar field magnitude in nT, not remanent magnetization in A/m.
- **Crust:** Wieczorek et al. (2022), Zenodo 6477509, CC BY 4.0. Four Khan2022 grids, InSight thickness 39 km; north density 2,900 and south density 2,600–2,900 kg/m³. Original 721 × 1441 nodes including poles and longitude seam; sampled at the 2° cell centers. No ensemble probability is implied.
- **Boundary:** Andrews-Hanna et al. (2008) coordinates distributed with the crust archive. Full curve used for the spherical mask; every fourth vertex used for display. It is not the equator.
- **Geology:** Tanaka et al. (2014), USGS SIM 3292, public domain. The official USGS service returns 1,311 polygons in Mars 2000 Sphere geographic coordinates (WKID 104971). Ring interiors/holes are retained; point-in-polygon queries use a spatial index. Classification at 2° cell centers is a display sampling of a 1:20 million map, not a higher-resolution mineral retrieval. Zero display centers are unassigned or multiply assigned in this snapshot.
- **Candidates:** 15 crater positions from Herd Data S2 plus Karratha from Lagain supplementary table 2. Site associations are conditional. Center-point unit classifications can differ from the surrounding terrain quoted by a source.

## Data quality notes

`null` depth bounds represent unavailable intervals; negative best fits remain negative. The original `-1e100` sentinel is not plotted as a physical measurement. Filtering does not imply no magnetization in excluded regions.

The MagIC series include changes in archived treatment amplitude and moment. The viewer uses measurement order, exposing the original amplitude on hover. Values are not rescaled to force monotonic treatment steps. The repository's source files should be checked with authors before using them for quantitative demagnetization fits. No terrestrial collection coordinates are interpreted as Martian coordinates.

Source metadata can change between API queries. File checksums provide the product identity; the manifest checksum identifies this particular acquisition snapshot. Rerunning acquisition refreshes access metadata. “Downloaded” and “processed” are separate states in the interface. This collection is not an exhaustive or continuously updated Mars archive.
