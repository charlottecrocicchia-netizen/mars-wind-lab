"""Render the method, exploration and dossier layer without rerunning science."""
from html import escape
from pathlib import Path
import re

import markdown

from reading_collection import COLLECTION_DATE, CURRENT_NOTES, DOSSIERS
from site_layout import navigation
from site_links import rewrite_links

ROOT = Path(__file__).resolve().parents[2]


def method():
    prospective = (ROOT/'research/NEXT_TEST_PROTOCOLS.md').read_text()
    prospective = re.sub(r'^(#{1,5}) ', r'#\1 ', prospective, flags=re.M)
    protocols = markdown.markdown(prospective, extensions=['tables', 'fenced_code', 'toc'])
    protocols = rewrite_links(protocols, ROOT/'research/NEXT_TEST_PROTOCOLS.md')
    return '''<section class="report-hero"><p class="eyebrow">HOW WE WORK · METHOD AND EVIDENCE</p>
<h1>From a public observation to a limited claim.</h1>
<p class="lead">One chain connects the inputs, assumptions, calculations, checks and written verdict. Each link is inspectable. Opening this site displays saved results; it does not start a scientific calculation.</p></section>
<section aria-labelledby="pipeline-title"><h2 id="pipeline-title">Five steps, with a trace at each step</h2>
<ol class="method-pipeline" aria-label="Research pipeline">
<li><span class="step-number">01</span><h3>Identify the inputs</h3><p>Record the origin, units, coverage, attribution and reuse terms of each dataset. Reading a paper and reusing its data are different actions. <a href="/research/data?view=sources">Input provenance →</a></p></li>
<li><span class="step-number">02</span><h3>Declare the comparison</h3><p>Specify the question, parameter ranges, masks, controls and interpretation before running it. The current protocol was declared locally and revised after the audit; it has no external preregistration timestamp. <a href="/research/files/discriminating/protocol.json">Protocol →</a></p></li>
<li><span class="step-number">03</span><h3>Calculate and save</h3><p>One numerical build generates the six tests. Saved tables and figures have a manifest recording input, code and output hashes, settings and software versions. Hashes identify a run; they do not establish scientific correctness. <a href="/research/files/discriminating/manifest.json">Run manifest →</a></p></li>
<li><span class="step-number">04</span><h3>Check the implementation</h3><p>Use analytic cases, synthetic controls, convergence checks and comparisons with published products. The audit found errors and triggered recalculation. This is an internal, AI-assisted review, not external peer review. <a href="/research/dossiers/audit">Corrections and controls →</a></p></li>
<li><span class="step-number">05</span><h3>Write the verdict</h3><p>State what changed relative to the tested alternative and what the result cannot decide. Separate measured values, model-dependent inferences and proposed explanations. Numerical success alone does not validate a geological history. <a href="/research/tests">Six current results →</a></p></li>
</ol></section>
<section id="verdicts"><h2>What a verdict means</h2>
<div class="verdict-key">
<article><h3>Supports the recording idea</h3><p>A stated prediction agrees with the tested observations or calculation. This is conditional support, not a unique explanation of the dichotomy.</p></article>
<article><h3>Weakens a scenario</h3><p>A declared scenario fails a specified comparison or control. The result must name that scenario and the assumptions needed for the conflict.</p></article>
<article><h3>Adds a constraint</h3><p>The test narrows an allowed range or exposes a trade-off without selecting one history.</p></article>
<article><h3>Not decisive</h3><p>The tested alternatives remain compatible, the comparison lacks support, or the result cannot distinguish the proposed causes.</p></article>
</div><p>Every current test follows <strong>Why → How → Result → Verdict → Limits → Reproduce</strong>. Ensemble percentiles describe the declared simulations, not automatically probabilities for Mars. Surface epoch is not magnetic acquisition age; a model grid cell is not an independent observation.</p></section>
<section id="reproduce"><h2>Reproduce the current evidence</h2>
<p>Run these commands from the repository root after preparing the Python environment and the permitted inputs. The full numerical build uses local magnetic coefficients, atlas and crustal products, thermal profiles, and cached GMM-3/MOLA coefficients. Missing inputs must be obtained under their documented terms. A fresh checkout of the site alone is not sufficient.</p>
<details class="method-drawer"><summary>Numerical build, controls and rendering commands</summary>
<pre><code>python -m pip install -e '.[test,research,observations]'
python scripts/discriminating/build.py
python scripts/discriminating/audit_controls.py
python -m pytest -q -m 'not integration'
python scripts/research/render_site.py
python scripts/research/render_docs.py</code></pre>
<p>The saved corrected full build took about 18 minutes on the development machine. The <code>--quick</code> option changes the sampling and overwrites outputs in the same directory; it is a smoke test, not the report dataset. Render commands alone reuse the saved numerical outputs.</p>
<div class="download-links"><a href="/research/files/discriminating/sources.json">Build source ledger</a><a href="/research/files/discriminating/manifest.json">Build hashes</a><a href="/research/files/discriminating_audit/controls.json">Audit controls</a><a href="/assets/reading/discriminating_tests.html">Full technical report</a></div></details>
<p>The <a href="/research/dossiers/literature">literature dossier</a> explains reading depth and source assessment. The <a href="/research/dossiers/experiments">earlier-experiment dossier</a> keeps the separate commands for the older workshops.</p></section>
<section id="next-tests"><p class="eyebrow">FOLLOW-UPS · STATUS AND PROTOCOLS</p><h2>Executed follow-ups and their limits</h2>
<p>The <a href="/assets/reading/arabia_preflight.html">Arabia prerequisite checks</a> fail the declared overlap and block screens. The subsequent <a href="/assets/reading/boundary_walk.html">boundary-transect calculation</a> is complete: only three adequately covered blocks remain at ±200 km, and none for the comparison with both shifted controls on common stations. It gives descriptive contrasts, without a calibrated significance claim. The same report decomposes the 23 northern Early Noachian cells by region.</p>
<p>The <a href="/assets/reading/depth_age.html">depth–age comparison</a> shows no stable association under its declared sensitivities. The <a href="/assets/reading/density_remanence.html">density–remanence balance</a> is now executed: low density and magnetization can coexist under specified matrix, porosity and recording assumptions. These follow-ups do not establish a unique geological history. Their novelty is unestablished, and the original failed Arabia design remains preserved.</p>
<div class="verdict-key"><article><h3>Reversal timing</h3><p>Synthetic prerequisite executed: changing rates and transformed acquisition clocks can produce identical fields. No observed-map inference follows in that model class. <a href="/assets/reading/reversal_identifiability.html">Read the test →</a></p></article><article><h3>Arabia Terra</h3><p>Prerequisites executed: the declared support and balance screens fail.</p></article><article><h3>Density and remanence</h3><p>Executed: exact material balances and attainable intervals, with explicit assumptions about source volume.</p></article><article><h3>Rapidly cooled bodies</h3><p>Executed: single-slab retention and an instantaneous-recording stack, including shared-field correlations. A coupled thermal stack with orbital fields remains unexecuted. <a href="/assets/reading/rapid_bodies.html">Read the calculation →</a></p></article></div>
<details class="method-drawer prospective"><summary>Read the four sourced protocols and their decision rules</summary><div class="prose">''' + protocols + '''</div></details>
<a href="/research/files/NEXT_TEST_PROTOCOLS.md" download>Download the protocols and execution status · Markdown ↓</a></section>'''


def dossier_cards():
    return '<div class="dossier-grid">'+''.join(
        f'<a class="dossier-card" href="/research/dossiers/{key}"><span>{i:02d}</span><h3>{escape(title)}</h3><p>{escape(description)}</p></a>'
        for i, (key, (title, description, _)) in enumerate(DOSSIERS.items(), 1))+'</div>'


def explore():
    workshops = [
        ('Regional transfer', '/research/experiments?view=maps', '1', 'Check the effect of withholding whole regions.'),
        ('Recording and reversals', '/research/experiments?view=recording', '4', 'See which parts of a field history a cooling rock records.'),
        ('Thermal histories', '/research/thermal', '2', 'Explore the earlier conductive-column benchmark.'),
        ('Detection and altitude', '/research/experiments?view=detection', '5', 'Separate observing a signal from identifying its source.'),
        ('Laboratory controls', '/research/experiments?view=laboratory', '3', 'Check what a component fit can establish about a rock.'),
        ('Crust and material properties', '/research/physics?view=crust', '6', 'Explore density, support and the earlier physical controls.'),
    ]
    cards = ''.join(f'<article class="workbench-card"><h3><a href="{url}">{title} →</a></h3><p>{description}</p><a href="/research/tests#test-{test}">Connection to Test {test} →</a></article>' for title, url, test, description in workshops)
    return '''<section class="report-hero"><p class="eyebrow">EXPLORE · DATA, TOOLS AND READING</p><h1>Go deeper without losing the question.</h1><p class="lead">Use the atlas to inspect a place, the workshops to understand a control, and the five dossiers to follow an argument. The six-test report remains the current statement of results.</p></section>
<section><h2>Inspect the evidence</h2><div class="verdict-key"><article><h3><a href="/research/data">Atlas →</a></h3><p>Magnetic fields, topography, crustal structure, meteorites and provenance.</p></article><article><h3><a href="/research/library">Source catalogue →</a></h3><p>Search references with their reading depth, source notes and exports.</p></article><article><h3><a href="/research/comparison">Origin scenarios →</a></h3><p>Compare the broader explanations and their chronological assumptions.</p></article><article><h3><a href="/research/method#next-tests">Follow-up status →</a></h3><p>Arabia support checks, boundary transects and the remaining physical protocols.</p></article></div></section>
<section id="dossiers"><h2>Five reading dossiers</h2><p>A consolidated route through the original notes and current technical reports. The dossiers explain how the pieces fit together; original notes remain accessible with their dates, citations and earlier qualifications.</p>''' + dossier_cards() + '''</section>
<section id="workshops"><h2>Workshops connected to the tests</h2><p>These earlier controls are useful for understanding the current methods. A workshop is not an additional independent confirmation.</p><div class="workbench-grid">''' + cards + '''</div></section>
<section id="archives"><h2>Earlier study routes</h2><p>Archive collection · ''' + COLLECTION_DATE + '''. These routes preserve exploratory work and previous proposals. Use <a href="/research/tests">Results</a> for the current conclusions.</p><div class="download-links"><a href="/research/pilot">Regional pilot study →</a><a href="/research/dynamo">Earlier dynamo proposals →</a><a href="/research/hypotheses">Earlier hypothesis workbench →</a><a href="/research/dossiers/experiments">Earlier methods and outputs →</a></div></section>'''


def render_dossiers(page):
    directory = ROOT/'web/dossiers'
    directory.mkdir(exist_ok=True)
    for key, (title, _, notes) in DOSSIERS.items():
        body = markdown.markdown((ROOT/f'research/dossiers/{key}.md').read_text(), extensions=['tables', 'fenced_code'])
        body = rewrite_links(body, ROOT/f'research/dossiers/{key}.md')
        links = ''.join(f'<li><a href="/assets/reading/{stem.lower()}.html">{escape(label)}</a> <small>{"Current reference" if stem in CURRENT_NOTES else "Archive collection · " + COLLECTION_DATE}</small></li>' for stem, label in notes.items())
        content = f'<p class="eyebrow">READING DOSSIER · {COLLECTION_DATE}</p><div class="prose dossier-prose">{body}</div><section class="dossier-sources"><h2>Original notes and technical references</h2><p>The archive date identifies this collection, not the original authorship date of each note. Dates stated within the notes are retained.</p><ul>{links}</ul></section><section><h2>Continue through the collection</h2>{dossier_cards()}</section>'
        (directory/f'{key}.html').write_text(page(title, '/research/explore', content))


PANEL_TESTS = {
    'recording': ('2 and 4', '4'), 'detection': ('3 and 5', '5'),
    'maps': ('1', '1'), 'laboratory': ('3', '3'),
    'crust': ('6', '6'), 'feedback': ('2', '2'),
    'boundary': ('1 and 6', '1'), 'paleomagnetism': ('3', '3'),
}


def sync_secondary_pages():
    """Keep preserved addresses, update their shared navigation and context."""
    roles = {
        'data': ('Evidence atlas', '1 and 6', '1'),
        'library': ('Source catalogue', '', ''),
        'comparison': ('Background scenario comparison', '', ''),
        'experiments': ('Earlier interactive controls', '1–5', '1'),
        'physics': ('Earlier physical controls', '1, 2, 3 and 6', '6'),
        'thermal': ('Earlier thermal benchmark', '2 and 4', '2'),
        'dynamo': ('Archive: earlier dynamo proposals', '', ''),
        'ideas': ('Archive: earlier hypothesis workbench', '', ''),
    }
    paths = [*(ROOT/f'web/{name}.html' for name in roles), *(ROOT/'web/pilot').glob('*.html')]
    for path in paths:
        html = path.read_text()
        html = re.sub(r'<nav aria-label="Main navigation"[^>]*>.*?</nav>', navigation('/research/explore'), html, count=1, flags=re.S)
        html = re.sub(r'<div class="collection-context"[^>]*>.*?</div>', '', html, flags=re.S)
        role, related, test = roles.get(path.stem, ('Archive: regional pilot study', '1 and 5', '5'))
        detail = f'Collection reviewed {COLLECTION_DATE}. ' if role.startswith(('Archive', 'Earlier')) else ''
        related_link = f'<a href="/research/tests#test-{test}">Connection to Test {related} →</a>' if test else '<a href="/research/method">How we work →</a>'
        banner = f'<div class="collection-context"><p>{escape(role)} · {detail}<a href="/research/explore">← Explore</a></p>{related_link}</div>'
        html = re.sub(r'(<main\b[^>]*>)', lambda m: m[0]+banner, html, count=1)
        html = re.sub(r'<p class="test-connection">.*?</p>', '', html, flags=re.S)
        def connect(match):
            labels, number = PANEL_TESTS.get(match[1], ('', ''))
            if not number: return match[0]
            return match[0]+f'<p class="test-connection">Methodological connection: <a href="/research/tests#test-{number}">Test {labels} →</a>. This earlier control is not a new verdict.</p>'
        html = re.sub(r'<section\b[^>]*(?:data-panel="|id="view-)([^"]+)"[^>]*>', connect, html)
        if path.stem == 'library':
            html = re.sub(r'<details class="reading-drawer">.*?</details>', '<div class="reading-callout"><h2>Read through five dossiers</h2><p>Scientific context, literature method, earlier experiments, interdisciplinary review, and audit.</p><a href="/research/explore#dossiers">Open the consolidated reading route →</a></div>', html, count=1, flags=re.S)
        path.write_text(html)


def render(page):
    (ROOT/'web/method.html').write_text(page('How we work', '/research/method', method()))
    (ROOT/'web/explore.html').write_text(page('Explore', '/research/explore', explore()))
    render_dossiers(page)
    sync_secondary_pages()
