# Source provenance and permitted use

This independent project uses its own analysis implementation, published scientific methods, and authorized data. Private internship scripts, reports, eigenfunctions and their derivatives are excluded. Their archive reader, API route, interface and local derivative exports were removed on 2026-09-27. Do not restore that functionality or use copies from the Trash.

## Code and numerical methods

The density–remanence follow-up reuses existing authorized project outputs, isolated cited material-property facts, and original mass-balance calculations. No new external dataset, article figure or third-party implementation is redistributed. Its [source ledger](../research/followup/mixture/sources.json) records the numerical facts, reading depth and conditional use; mineral-property scenarios do not establish the composition or porosity of Martian source rocks.

The project-specific Python diagnostics, scalar finite-element benchmark and thin Fortran batch adapter are maintained here. The scalar benchmark is derived from the documented differential equation in the [historical atmospheric method](archive/ATMOSPHERIC_METHOD.md), and checked against uniform-column analytic frequencies, convergence and uniform-advection identities. It is not a reconstruction or translation of the former internship software. A complete coupled solid-planet/atmosphere solver remains future work; the scalar benchmark is not a substitute for such a solver.

The rapid-body and reversal-identifiability calculations use original analytic and synthetic implementations with no newly redistributed external dataset or source code. Their reports distinguish cited mathematical methods from numerical results produced here. The pre-correction body snapshot is preserved for audit, not presented as current results. Website and GitHub link corrections do not change the saved scientific arrays; editorial manifest entries identify such report-only updates.

Third-party packages retain their licenses. Plotly's MIT notice is retained in `web/PLOTLY-LICENSE.txt`; the NASA decorative asset has its own [credit and usage references](ASSETS.md). A publication may be read and cited without making its text, figures or accompanying software freely reusable.

The [thermal experiment](../research/THERMAL_EXPERIMENT.md), added on 2026-09-27, is an original conductive-column implementation checked against analytic heat-equation solutions. Its parameters are synthetic and its figures and numerical exports are project-generated. Published papers supply scientific context and limitations; no external code, article figure or new dataset was incorporated. This experiment neither invokes MCD nor uses private internship material.

The [executed magnetic experiments](../research/EXECUTED_EXPERIMENTS.md) reuse only existing authorized extracted atlas and MagIC numerical products, preserving their attributions and terms. Synthetic recording/detection inputs and all new implementation code and figures are original. The workflow does not reacquire MOCAAS, crater catalogues or other raw archives. Candidate laboratory fits keep their provenance and do not replace published component interpretations.

## Atmospheric model

On 2026-09-27, the atmospheric interface and HTTP calculation endpoints were removed from the research website. The server and desktop launcher no longer import, build or call MCD. Independently authored numerical modules remain as historical offline work; their presence is not authorization to invoke an external installation. No local datasets were deleted as part of this website change.

MCD is an external product, not code authored by this project. The [producers' documentation](https://www-mars.lmd.jussieu.fr/mars/info_web/index.html) describes its intended scientific use. The [full-version access page](https://www-mars.lmd.jussieu.fr/MCD_pro/mcd_pro.html) requires requesting access and accepting non-transmission and noncommercial-use conditions. The bundled copyright additionally requires attribution and keeping the producers informed of use and developments.

An installation inherited from another person is not automatically an authorized installation for this project. Its provenance must be established before further calls to its software. Already extracted atmospheric products expressly authorized by the project owner remain separate from permission to use or redistribute the MCD software. No MCD source or datasets are distributed by this repository.

## Public observational datasets

The acquisition registry is `scripts/data/sources.json`; the recorded file identities, provider checksums, URLs and declared source terms are in `research/data/manifest.json`. The [data notes](../research/data/README.md) describe derived products and conventions. The registry contains:

- Zenodo magnetic field/depth, ejection-age/model and crustal products: recorded CC BY 4.0.
- Figshare thermal products: recorded CC BY 4.0.
- MIL 03346 Harvard Dataverse laboratory data: recorded CC0.
- MagIC laboratory contributions: recorded CC BY 4.0.
- NASA PDS MOLA and USGS mapping/nomenclature: public archive/government sources, with required source credits retained.
- Lagain 2022 published supplementary tables: recorded CC BY 4.0.
- Herd 2024 tables: recorded CC BY-NC 4.0; the noncommercial restriction must accompany derivatives.
- Weiss 2025 article and supplement: recorded CC BY-NC-ND 4.0. Do not adapt or redistribute protected figures/text as if openly licensed for adaptation. The retained numerical inventory is an attributed transcription with separately authored notes.

These entries record source metadata, not a blanket authorization for all uses. Check the actual product's terms before adding it or changing its use, especially before publication or commercial deployment. Keep raw research PDFs local and out of Git.

The Arabia Terra preflight adds the numerical named-feature outline from [USGS Gazetteer feature 336](https://planetarynames.wr.usgs.gov/Feature/336), detailed geometry `wkt-25452`. Its attribution, retrieval timestamp and reuse basis are embedded in `research/followup/arabia/arabia_polygon.geojson`. The [USGS public-domain and credit policy](https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits) covers USGS-produced numerical information. The supplied outline represents an approximate named-feature extent, not a geological boundary. No article figure, third-party map image or additional restricted archive was incorporated.

## Open permission questions

Two sources require a clearer reuse basis before new incorporation or redistribution:

- **MOCAAS raster database:** the [producer page](https://www.ias.u-psud.fr/moccas/) offers public download and a citation request but no explicit license. Do not label it CC BY, infer unrestricted reuse from download availability, or redistribute its rasters.
- **Revised crater catalogue:** the [public repository](https://github.com/alagain/martian_crater_database) has no explicit license visible in its root. Public hosting is not a software or data license; do not copy its code or assume unrestricted redistribution of the catalogue.

Previously extracted numerical products were expressly allowed by the project owner during the 2026-09-27 review. This does not establish new rights for raw source redistribution, new imports, or derivative publication. The acquisition scripts enforce `reuse_approved` decisions before any download. MOCAAS and the pilot bundle’s revised crater catalogue are blocked for new acquisition. Request only approved sources with `acquire.py --only …`; the full bundle stays blocked until its unresolved permissions are established. Further incorporation or publication still requires checking the intended use. No permission request has been sent on the owner's behalf.
