"""Render the curated dynamo test register without external downloads."""
import argparse
import csv
import io
import json
from html import escape
from pathlib import Path

from site_layout import context, navigation

ROOT = Path(__file__).resolve().parents[2]
DEPTHS = {
    'selected_sections': 'Selected primary sections read',
    'abstract': 'Abstract only',
    'correction_notice': 'Correction notice read',
    'selected_excerpt': 'Selected publisher excerpt',
    'report_lead': 'Report lead · not checked here',
}


def render(data):
    e = escape
    groups = {g['id']: g for g in data['groups']}
    options = ''.join(f'<option value="{e(g["id"])}">{e(g["title"])}</option>' for g in groups.values())
    cards = []
    for r in data['tests']:
        sources = ''.join(f'<li><a href="#source-{e(key)}">{e(data["sources"][key]["label"])}</a> <span class="source-depth">{e(DEPTHS[data["sources"][key]["review_depth"]])}</span></li>' for key in r['sources'])
        if not sources:
            sources = '<li>No supporting Mars-specific primary source established in this assessment. Treat this as an unverified lead.</li>'
        stage = 'Executed building block · full test pending' if r['execution_status']=='partial_benchmark' else 'Planned test'
        result_link = '<p><a href="/research/experiments">Inspect the executed building blocks →</a></p>' if r.get('results_url') else ''
        fields = [('Proposition to examine', r['claim']), ('Proposed test', r['test']), ('Required inputs', r['required_inputs']), ('What would discriminate?', r['discriminator']), ('What could mislead us?', r['limits']), ('Available project work', r['building_block'])]
        body = ''.join(f'<dt>{e(label)}</dt><dd>{e(value)}</dd>' for label, value in fields)
        cards.append(f'''<details class="dynamo-card" id="{e(r['id'])}" data-group="{e(r['group'])}"><summary><span class="proposal-id">{e(r['id'])}</span><span><strong>{e(r['title'])}</strong><small>{e(r['role'])} · {e(stage)}</small></span></summary><div class="proposal-body"><dl>{body}</dl>{result_link}<h3>Source trail</h3><ul class="proposal-sources">{sources}</ul><p class="proposal-link"><a href="/research/dynamo#{e(r['id'])}">Link to this proposal</a></p></div></details>''')
    source_cards = ''.join(f'''<li id="source-{e(key)}"><a href="{e(s['url'], quote=True)}">{e(s['label'])} ↗</a><span class="source-depth">{e(DEPTHS[s['review_depth']])}</span><p>{e(s['consulted_material'])}</p></li>''' for key, s in data['sources'].items())
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dynamo test programme · Martian dichotomy</title><link rel="stylesheet" href="/assets/research.css?v=design1"><link rel="stylesheet" href="/assets/workspace.css?v=20260927-design"><link rel="stylesheet" href="/assets/dynamo.css?v=1"><script defer src="/assets/dynamo.js?v=2"></script></head>
<body class="workspace"><a class="skip" href="#content">Skip to content</a><header class="workspace-header"><a class="wordmark" href="/"><i></i><span>Martian dichotomy<small>CHARLOTTE CROCICCHIA</small></span></a>{navigation('/research/comparison')}</header>
<main id="content">{context('/research/comparison', 'Hypotheses', 'Dynamo hypotheses · test programme')}
<div class="page-intro"><p class="eyebrow">DYNAMO / FROM PROPOSALS TO TESTS</p><h1>What would distinguish<br>the magnetic histories?</h1><p class="lead">Mars’s magnetic contrast has several possible causes. Separate the field that existed from the record the rocks preserved, then compare predictions against the same observations.</p></div>
<div class="project-reading-key"><div><b>30 proposals</b>Grouped by the question they address.</div><div><b>First benchmarks executed</b>Full discriminating tests remain open.</div><div><b>Sources with reading depth</b>Checked passages and unchecked leads stay visible.</div></div>
<section class="reading-callout" aria-labelledby="firstStep"><p class="eyebrow">START HERE / FIRST CALCULATIONS COMPLETED</p><h2 id="firstStep">Can different field histories leave the same signal?</h2><p>Use one shared recording model to compare a steady field, reversals, interruptions and shutdown. Then test what remains detectable at different heights. Original recording, detection, regional-transfer and laboratory benchmarks are now available. They expose ambiguities; they do not select a Martian dynamo history.</p><a class="button" href="/research/experiments">Explore the executed experiments →</a> · <a href="/research/thermal">Explore the existing thermal experiment</a></section>
<details class="method-drawer audit-brief"><summary>Four distinctions to keep in mind</summary><ul><li>A weak or null magnetic signal does not by itself prove that the dynamo was off.</li><li>An axial field can reverse polarity. Geometry and reversal history are separate choices.</li><li>Present-day interior structure does not directly date ancient dynamo conditions.</li><li>A laboratory material constraint does not set a universal dynamo shutdown date.</li></ul><a href="/assets/reading/dynamo_tests.html#critical-corrections">Read the source assessment and corrections →</a></details>
<section class="proposal-register" aria-labelledby="registerTitle"><p class="eyebrow">EXPLORE / ONE QUESTION AT A TIME</p><h2 id="registerTitle">Choose a research question.</h2><p>The proposals can overlap. For example, a reversing thermal dynamo and later hydrothermal alteration can belong to the same history. Open a proposal to see what would test it.</p>
<form class="map-controls" id="dynamoFilters" hidden><label for="dynamoGroup">Research question<select id="dynamoGroup"><option value="">All five questions</option>{options}</select></label><label for="dynamoSearch">Search all proposals<input id="dynamoSearch" type="search" placeholder="Try reversals, ALH 84001 or burial"></label><button type="reset" class="quiet">Reset filters</button></form>
<p id="dynamoCount" role="status">30 proposals · full discriminating tests remain open</p><noscript><p>All proposals are available below without JavaScript. Use your browser’s find command to search them.</p></noscript>
<div id="dynamoCards">{''.join(cards)}</div><p id="dynamoEmpty" hidden>No proposals match. Clear the search or choose another question.</p>
</section>
<section class="dynamo-source-trail" aria-labelledby="sourceTitle"><h2 id="sourceTitle">What has actually been checked?</h2><p>This is a targeted assessment of a supplied research synthesis. A test design is our proposal, not a result attributed to its cited authors. Reading depth below describes this assessment and does not update the separate library catalog.</p><details id="dynamoSources" class="method-drawer"><summary>Inspect all {len(data['sources'])} source records and reading limits</summary><ul class="dynamo-source-list">{source_cards}</ul></details></section>
<div class="next-step"><span>Continue with</span><a href="/research/tests">Completed calculations →</a><a href="/assets/reading/dynamo_tests.html">Assessment and priorities →</a><a href="/research/files/dynamo/tests.json" download>Register · JSON ↓</a><a href="/research/files/dynamo/tests.csv" download>Register · CSV ↓</a></div>
</main><footer><span>A personal research project by Charlotte Crocicchia.<br>Original test designs · targeted source assessment · updated {e(data['updated'])}.</span><a href="https://github.com/charlottecrocicchia-netizen/mars-wind-lab">GitHub ↗</a></footer></body></html>
'''
    output = io.StringIO(newline='')
    fields = ['id', 'group', 'title', 'role', 'execution_status', 'claim', 'test', 'required_inputs', 'discriminator', 'limits', 'building_block', 'sources', 'results_url']
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for r in data['tests']:
        writer.writerow({**r, 'sources': ' | '.join(data['sources'][s]['url'] for s in r['sources'])})
    return {'web/dynamo.html': html, 'research/dynamo/tests.csv': output.getvalue()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if committed outputs differ from the register.')
    args = parser.parse_args()
    data = json.loads((ROOT / 'research/dynamo/tests.json').read_text())
    for name, content in render(data).items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text() != content:
                raise SystemExit(f'Stale generated output: {name}')
        else:
            path.write_text(content)
            print(name)
