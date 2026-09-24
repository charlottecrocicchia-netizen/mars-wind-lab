# Search method and coverage

## Question and scope

Which observations distinguish possible **formation mechanisms** of the Martian hemispheric dichotomy from its **later modification**? The search also covers evidence needed to evaluate those observations: interior and magnetic inversions, meteorite preservation, geochronology, surface alteration, atmospheric escape and mission sampling.

The cutoff is **2026-09-24**. The included material spans early hypotheses through 2026 publications. Publication dates come from Crossref; online and issue dates can differ. DOI strings containing a year are not used as publication dates. For example, the Sun–Tkalčić attenuation work has an online/issue-date distinction; inspect its full citation rather than inferring the year from `2024GL110921`.

## Discovery

1. `scripts/research/queries.json` defines 41 Crossref title queries. `harvest.py` retrieves 80–500 ranked results per query, with the cutoff filter, and records the exact URL and counts in `search_log.json`.
2. An automated title filter retains Mars/Martian terms and named Martian meteorites. This produced 1,967 unique DOI candidates. The filter is an efficiency choice, **not** a scientific exclusion decision. It can miss relevant titles that omit these terms.
3. Targeted searches of publisher pages, author repositories, NASA/ESA/ISRO/USGS archives and public discussions supplied additional leads. `core_dois.json` identifies 65 anchor records; exact Crossref DOI enrichment gives a final total of 1,980 candidates.
4. DOI normalization removes case-only duplicates. Crossref types and query provenance are preserved. Preprint and journal versions with different DOIs have **not** been fully reconciled.
5. References attached to core metadata are compared with the catalog. The resulting `citation_queue.json` contains 2,297 missing DOI leads. These are not included in the 1,980 count and are not all about Mars. A citation is a discovery lead, not evidence of relevance.

The enormous `total_results_reported` values in the search log are fuzzy-search totals, **not** the size of the Martian-dichotomy literature. Queries were capped and not paginated to exhaustion. A record appearing in several queries can carry several topic labels; these discovery labels are not independently verified classifications.

## What was actually read?

| Label | Meaning | Count |
|---|---|---:|
| Metadata / preview only | Bibliographic record, title or limited publisher preview | 1,921, including 6 core records |
| Abstract consulted | Publisher/author abstract or publisher-supplied Crossref abstract | 50 |
| Selected full-text sections consulted | Relevant passages, figure captions or methods inspected, without complete audit | 9 |
| Complete full-text audit | Methods, supplements, uncertainties and result reproduction all audited | 0 |

Original short annotations identify a finding, its relevance and a limitation. They are a reading aid, not peer review. The nine selected-section records are Irwin–Watters 2010, Wieczorek et al. 2022, Berne et al. 2026, the 2025 inner-core correction, Mackay-Champion et al. 2026, Steele et al. 2024, Gattacceca et al. 2014, Vervelidou et al. 2023 and Weiss et al. 2025. For Weiss et al., the returned-sample review's meteorite discussion and preservation-test figure were inspected. Berne et al.'s atmospheric-loading methods were checked explicitly.

Primary-source links are attached to every core record. Paywalled previews are not marked as full-text readings. A bibliography entry does not imply that its dataset or code was downloaded, run or validated. No mission archive has yet been ingested into a joint dichotomy inversion.

## Inclusion and assessment rules for the next screening pass

Retain an original study if it constrains formation, timing, geometry, crustal structure, thermal evolution, magnetization, or subsequent modification of the contrast, or provides a necessary measurement/model validation. Retain reviews for orientation but do not count them as independent observations. Mark conference abstracts and preprints separately from journal versions. Exclude unrelated Mars uses, news, duplicate versions and peripheral astrobiology unless an explicit connection to a testable dichotomy constraint exists. Record exclusions rather than silently deleting them.

Extract: actual measured quantity; location/footprint/depth; age being dated; uncertainty; calibration; assumptions; alternative explanations; dependence on other studies; data/code availability; correction or retraction status. Presently only one identified author correction was checked; a corpus-wide retraction/correction audit is outstanding.

## Coverage gaps

The present search is broad but **not demonstrably exhaustive**. Full NASA ADS searches, additional multilingual indexes, complete LPSC abstracts, dissertations, reference-book chapters, citation closure and forward-citation searches remain outstanding. Non-English titles, older non-DOI literature and small laboratory studies can be missed. Detailed isotopic-reservoir, true-polar-wander, crustal recycling, hydrothermal mineralogy, satellite-origin and paleoclimate literature is less deeply assessed than the magnetic and geophysical anchors. Negative results are especially vulnerable to discovery bias.

To claim an exhaustive review, define a narrower eligible question and date range, search multiple indexes, screen all retrieved records, reconcile versions, follow citations to saturation, document exclusions and audit full texts. The current release makes the remaining work visible instead of claiming that threshold was met.

## Reproduction

From the repository root:

```sh
python scripts/research/harvest.py
python scripts/research/enrich.py
python scripts/research/build.py
```

The harvest uses the public Crossref API; no account or secret is needed. Cache files under ignored `output/research_raw/` contain abstracts for private reading. Existing caches are reused; move that directory aside for a fresh retrieval. Crossref rankings and metadata can change between runs. The committed JSON, query log and annotations preserve this release's state.

Rebuild exports from the distributed metadata without contacting Crossref:

```sh
python scripts/research/build.py --input research/catalog.json
```

The site's prose pages are generated from these Markdown files with `python scripts/research/render_docs.py` after installing the optional `research` dependencies. Do not hand-edit generated HTML. The scientific statements are original summaries linked to their sources, not redistributed publisher full texts.
