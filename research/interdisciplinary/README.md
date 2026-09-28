# Interdisciplinary review records

Snapshot: **28 September 2026**. Start with [the synthesis](../INTERDISCIPLINARY_SYNTHESIS.md).

- `sources.json`: 52 source records, original annotations, consultation status and shared evidence families. This is the editable source ledger.
- `chronology.json`: 12 selected material/event records, with age types and uncertainty conventions. Approximate/model ages are explicitly labelled. Null is not zero.
- `search_log.json`: retained query batches, discovery method, access failures and coverage gaps. This is not a complete search-engine result archive.
- `sources.csv` and `chronology.csv`: generated exports. List fields use semicolons; CSV fields use standard quoting. Text is UTF-8.

Source IDs are local identifiers. The ledger is a supplement to the existing catalog, with overlapping records; its counts must not be added to the older catalog or presented as newly read papers. A book preview or metadata lead is not a full reading. No complete methodological audit was performed.

Regenerate from the repository root:

```sh
.venv/bin/python scripts/research/render_interdisciplinary.py
.venv/bin/python scripts/research/render_docs.py
.venv/bin/python scripts/research/render_overview.py
```

The first command validates source IDs and chronology references, writes both CSVs and generates `research/INTERDISCIPLINARY_SOURCES.md`. The following commands render the reading pages and site entry points. The four interpretive chapters are authored Markdown, not generated scientific results.

This pass added research notes and bibliographic exports, not new scientific datasets. Temporary fetched abstracts, article copies and visual checks stay outside the committed review. Dataset/code reuse must follow the repository source policy.
