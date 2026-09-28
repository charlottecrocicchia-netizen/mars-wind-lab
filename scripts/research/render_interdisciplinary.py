"""Render original review annotations and CSV exports; no network or calculations."""
from collections import Counter
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / 'research' / 'interdisciplinary'


def write_csv(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: '; '.join(v) if isinstance(v, list) else v for k, v in row.items()})


def render():
    ledger = json.loads((DIRECTORY / 'sources.json').read_text())
    sources = ledger['sources']
    counts = Counter(s['reading_status'] for s in sources)
    ids = [s['id'] for s in sources]
    assert len(ids) == len(set(ids)), 'Duplicate source identifiers'
    assert all(s['reading_status'] in ledger['status_definitions'] for s in sources)
    chronology = json.loads((DIRECTORY / 'chronology.json').read_text())['events']
    assert all(set(e['source_ids']) <= set(ids) for e in chronology), 'Unknown chronology source'
    write_csv(DIRECTORY / 'sources.csv', sources)
    write_csv(DIRECTORY / 'chronology.csv', chronology)
    lines = [
        '# Annotated sources and actual reading coverage', '',
        '**Targeted interdisciplinary review · 28 September 2026**', '',
        '[Synthesis](INTERDISCIPLINARY_SYNTHESIS.md) · [Chronology](INTERDISCIPLINARY_CHRONOLOGY.md) · [Magnetic evidence](INTERDISCIPLINARY_MAGNETISM.md) · [Tests](INTERDISCIPLINARY_TESTS.md)', '',
        f'This supplement contains **{len(sources)} source records**, including {sum(s["source_kind"] == "book" for s in sources)} books and one correction notice. It combines current source consultation with explicitly labelled earlier project assessments. Inclusion is not a claim that a paper or book was read in full. **Complete methodological audits: 0.**', '',
        'The older 1,990-record discovery catalog and its reading totals are unchanged. Many sources overlap: do not add the two collections or their consulted counts. This is a critical targeted review, not an exhaustive systematic review.', '',
        '## What was consulted', '',
        '| Status in this pass | Records | Meaning |', '| --- | ---: | --- |',
    ]
    for status, definition in ledger['status_definitions'].items():
        lines.append(f'| {status.replace("_", " ").title()} | {counts[status]} | {definition} |')
    lines += [
        '', '## Search and inclusion method', '',
        'Discovery used cross-disciplinary queries, exact titles and DOIs, publisher pages, author repositories and original abstracts served by Europe PMC. Original research supplies scientific claims; integrated reviews organize the evidence. Book previews identify a reading route, while selected open textbook chapters support the physical framework. News articles and reposts were not used as scientific evidence.', '',
        'The [search ledger](interdisciplinary/search_log.json) preserves retained query batches and access limitations. It is not a complete export of every search result or ranking. The earlier 41-query catalog search was not rerun. Exact-DOI Crossref requests encountered rate limiting; unsuccessful requests were not counted as successful reads. Some publisher/PMC pages were unavailable, so indexed excerpts and prior assessments retain their narrower labels.', '',
        'Coverage spans crustal origin, petrology, isotope chronology, seismology, gravity, thermal evolution, dynamo physics, paleomagnetism, alteration, hydrology, climate/escape, geomorphology, rotation and satellite-formation models. Coverage is uneven. Accretion chronology, mineral reaction kinetics, complete rheological constraints, monographs and non-English literature require further work. Results and supplements were not independently reproduced.', '',
        'Selection favours sources that constrain a link between disciplines or challenge an attractive explanation. A newer paper does not automatically overturn older evidence. Corrections and date ambiguities are retained. Reading depth, uncertainty and shared input families must accompany any reuse.', '',
        '## Download the review records', '',
        '[Sources JSON](interdisciplinary/sources.json) · [Sources CSV](interdisciplinary/sources.csv) · [Chronology JSON](interdisciplinary/chronology.json) · [Chronology CSV](interdisciplinary/chronology.csv) · [Search ledger](interdisciplinary/search_log.json)', '',
        'These exports contain original short annotations and bibliographic facts, not copied abstracts, book chapters or scientific datasets. Public readability is not a general data/code reuse license. No new third-party dataset or model code was incorporated into this review. An AI-assisted synthesis requires source-level verification before manuscript use.', '',
    ]
    previous = None
    for s in sources:
        if s['domain'] != previous:
            lines += ['## ' + s['domain'], '']
            previous = s['domain']
        lines += [
            f'### {s["citation_label"]}', '',
            f'[{s["title"]}]({s["url"]})', '',
            f'**Read status:** {s["reading_status"].replace("_", " ")}. {s["consulted"]}', '',
            f'**Use:** {s["finding"]} **Limit:** {s["limitation"]}', '',
            f'**Shared evidence family:** {", ".join(s["dependency_groups"]).replace("_", " ")}. Record ID: `{s["id"]}`.', '',
        ]
    (ROOT / 'research' / 'INTERDISCIPLINARY_SOURCES.md').write_text('\n'.join(lines))
    print(json.dumps({'source_records': len(sources), 'reading_counts': dict(counts), 'chronology_events': len(chronology)}))


if __name__ == '__main__':
    render()
