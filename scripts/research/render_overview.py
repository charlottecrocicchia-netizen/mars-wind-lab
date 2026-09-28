"""Render the overview and results directory from the committed result snapshot.

The SVG globe is an original orthographic rendering of the authorized 2° MOLA
summary. It is a navigation preview, not a new scientific product or inversion.
"""
from pathlib import Path
from html import escape
import json
import math
from site_layout import navigation

ROOT = Path(__file__).resolve().parents[2]
def load(path):
    return json.loads((ROOT / 'research' / path).read_text())


def globe():
    atlas, meteorites = load('data/atlas.json'), load('data/meteorites.json')
    def project(lon, lat):
        a, b = math.radians(lon - 180), math.radians(lat)
        return 270 + 195 * math.cos(b) * math.sin(a), 220 - 195 * math.sin(b), math.cos(b) * math.cos(a)
    def color(v):
        stops = [(-8, (26, 56, 85)), (0, (76, 115, 132)), (8, (174, 203, 203)), (22, (233, 241, 241))]
        v = max(-8, min(22, v))
        for (lo, a), (hi, b) in zip(stops, stops[1:]):
            if v <= hi:
                t = (v - lo) / (hi - lo)
                return '#'+''.join(f'{round(x+(y-x)*t):02x}' for x,y in zip(a,b))
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 450" role="img"><title>Mars elevation preview, centered on 180 degrees east</title><desc>Orthographic rendering of the project MOLA display grid. Dots mark proposed meteorite source craters. They are not confirmed launch sites.</desc><defs><radialGradient id="shade" cx="35%" cy="30%" r="75%"><stop offset="50%" stop-color="#07111e" stop-opacity="0"/><stop offset="100%" stop-color="#07111e" stop-opacity=".6"/></radialGradient><clipPath id="disk"><circle cx="270" cy="220" r="195"/></clipPath></defs><circle cx="270" cy="220" r="207" fill="none" stroke="#23394d"/><g clip-path="url(#disk)"><circle cx="270" cy="220" r="195" fill="#244760"/>']
    for i,lat in enumerate(atlas['latitude']):
        for j,lon in enumerate(atlas['longitude']):
            if project(lon,lat)[2] < 0: continue
            pts=[project(lon+dx,lat+dy) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
            c=color(atlas['topography_km'][i][j])
            svg.append('<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y,_ in pts)+f'" fill="{c}" stroke="{c}" stroke-width=".35"/>')
    svg.append('<circle cx="270" cy="220" r="195" fill="url(#shade)"/>')
    # Geographical graticule. No inferred dichotomy boundary is drawn in this preview.
    for lat in [-60,-30,0,30,60]:
        pts=[project(lon,lat) for lon in range(90,271,2)]
        svg.append('<polyline points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y,_ in pts)+'" fill="none" stroke="#d5eeee" stroke-opacity=".15" stroke-width=".7"/>')
    for c in meteorites['craters']:
        x,y,z=project(c['lon'],c['lat'])
        if z>0:svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="#a2fff0" stroke="#0c242c" stroke-width="1"/>')
    svg.append('</g>')
    for name,dx,dy in [('Karratha',-112,39),('Corinto',-100,-36),('Tooting',32,-35)]:
        c=next(c for c in meteorites['craters'] if c['name']==name)
        x,y,_=project(c['lon'],c['lat']);tx,ty=x+dx,y+dy
        svg.append(f'<path d="M{x:.1f} {y:.1f} L{tx+10:.1f} {ty+5:.1f}" stroke="#b1e6df" stroke-width=".8" fill="none"/><text x="{tx:.1f}" y="{ty:.1f}" fill="#e1f5f2" font-family="system-ui,sans-serif" font-size="11">{escape(name)}</text>')
    svg.append('</svg>')
    (ROOT/'web/atlas-preview.svg').write_text(''.join(svg))


def findings():
    maps=load('experiments/maps.json')
    rows=[r for r in maps['results'] if r['density_kg_m3']==2900 and r['altitude_km']==150 and r['model']=='combined']
    bars=''
    for label,split,offset in [('Random cells','random',0),('Regions · 0°','regional',0),('Regions · 30°','regional',30)]:
        r=next(r for r in rows if r['split']==split and r['wedge_offset_deg']==offset)
        v=r['skill_over_training_mean']
        bars+=f'<div class="bar-row"><span>{label}</span><span class="bar-track signed"><i style="left:{(min(v,0)+.5)/1.5*100:.2f}%;width:{abs(v)/1.5*100:.2f}%"></i></span><b>{v:+.3f}</b></div>'
    batch=next(b for b in load('experiments/recording.json')['batches'] if b['thermal']=='reheating' and b['band_c']==[250,550])
    signals=''
    for name in ['steady','intermittent']:
        value=next(h for h in batch['histories'] if h['id']==name)['absolute_field_q05_q50_q95_nt']['150'][1]
        signals+=f'<div class="bar-row"><span>{name.title()}</span><span class="bar-track"><i style="width:{value/150*100:.2f}%"></i></span><b>{value:.1f}</b></div>'
    fits=[f for f in load('experiments/laboratory.json')['candidate_fits'] if f['dataset']=='NWA_control' and f.get('mad_deg') is not None]
    passing=sum(f['mad_deg']<5 for f in fits)
    dots=''.join('<i'+(' class="passed"' if f['mad_deg']<5 else '')+'></i>' for f in fits)
    return f'''<div class="finding-grid">
<article class="finding-card"><span class="evidence-label">Map analysis</span><h3>A good local prediction can fail elsewhere.</h3><figure class="mini-chart" aria-label="Prediction skill: random cells plus 0.609; regional wedges minus 0.338; rotated wedges plus 0.382">{bars}<figcaption>Prediction skill · zero = the mean baseline</figcaption></figure><p class="finding-meaning">The result changes when we hold out whole regions instead of scattered cells.</p><p class="finding-limit">150 km altitude · 2,900 kg/m³ · combined model. A negative skill is worse than the baseline; this is not a causal test.</p><a href="/research/experiments?view=maps">Compare regional predictions →</a></article>
<article class="finding-card"><span class="evidence-label synthetic">Synthetic experiment</span><h3>Different field histories can leave the same record.</h3><figure class="mini-chart" aria-label="Steady and intermittent fields both give a known contribution of 108.9 nanotesla at 150 kilometers">{signals}<figcaption>Known new |Bz| at 150 km · nT</figcaption></figure><p class="finding-meaning">In this reheating case, the difference between the two fields is not preserved.</p><p class="finding-limit">250–550 °C blocking band · {batch['unknown_initial_fraction']*100:.1f}% unresolved initial record. A model example, not an inferred history of Mars.</p><a href="/research/experiments?view=recording">Explore magnetic recording →</a></article>
<article class="finding-card"><span class="evidence-label laboratory">Laboratory control</span><h3>A straight magnetic component can be misleading.</h3><figure class="mini-chart" aria-label="19 of 32 candidate fits from the contaminated NWA control have MAD below 5 degrees"><div class="fit-count">{passing} / {len(fits)}<small>fits with MAD &lt; 5°</small></div><div class="fit-dots" aria-hidden="true">{dots}</div><figcaption>Blue dots: low angular scatter in candidate fits</figcaption></figure><p class="finding-meaning">Even the contaminated control produces tightly aligned demagnetization segments.</p><p class="finding-limit">Overlapping windows are not independent samples. Fit quality alone cannot establish ancient remanence.</p><a href="/research/experiments?view=laboratory">Inspect laboratory controls →</a></article>
</div>'''


def page(title, active, body, scripts=''):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · Martian dichotomy</title><link rel="stylesheet" href="/assets/research.css?v=design1"><link rel="stylesheet" href="/assets/workspace.css?v=20260927-design">{scripts}</head><body class="workspace"><a class="skip" href="#content">Skip to content</a><header class="workspace-header"><a class="wordmark" href="/"><i aria-hidden="true"></i><span>Martian dichotomy<small>CHARLOTTE CROCICCHIA</small></span></a>{navigation(active)}</header><main id="content" class="overview">{body}</main><footer><span>Charlotte Crocicchia · Mars research<br>Observations, original calculations and open questions.</span><a href="https://github.com/charlottecrocicchia-netizen/mars-wind-lab">Code, methods & provenance ↗</a></footer></body></html>'''


def render():
    """Draw the globe, then render the report pages from the saved test outputs."""
    globe()
    from render_site import render as render_report
    render_report()


def legacy_render():
    globe()
    cards=findings()
    home=f'''<section class="overview-hero"><div><p class="eyebrow">MARS / CRUST · ROCKS · MAGNETIC MEMORY</p><h1>One planet.<br>Two different histories?</h1><p class="lead">Low northern plains. High southern terrain. Explore the evidence behind the Martian dichotomy, and the tests we are building to understand it.</p><div class="button-row"><a class="button" href="/research/data?view=meteorites">Explore the meteorite atlas ↗</a><a class="button secondary" href="/research/tests">See our results →</a></div><p class="hero-note">Research in progress · the origin remains an open question</p></div><figure class="planet-preview"><a href="/research/data?view=meteorites" aria-label="Open the Mars atlas and proposed meteorite sources"><img src="/assets/atlas-preview.svg" width="540" height="450" alt="Elevation on the hemisphere centered on 180°E, with proposed meteorite source craters including Karratha, Corinto and Tooting."></a><figcaption><span>MOLA elevation · 2° preview</span><span>Dots = proposed sources</span><a href="/research/data?view=sources">Data provenance ↗</a></figcaption></figure></section>
<nav class="overview-paths" aria-label="Explore the project"><a href="/research/data">Atlas <b>↗</b><small>Maps, meteorites & measurements</small></a><a href="/research/tests">Results <b>↗</b><small>Our calculations, explained</small></a><a href="/research/comparison">Hypotheses <b>↗</b><small>Compare origins & separate ages</small></a><a href="/research/library">Sources <b>↗</b><small>Papers, methods & reading notes</small></a></nav>
<div class="reading-callout"><p class="eyebrow">INTERDISCIPLINARY REVIEW · 28 SEPTEMBER 2026</p><h2>One planet. Connected histories.</h2><p>Connect crust formation, interior heat, paleomagnetism, water and climate. Follow the event chronology, compare origin scenarios and inspect what each source actually supports.</p><div class="download-links"><a href="/assets/reading/interdisciplinary_synthesis.html">Read the synthesis →</a><a href="/assets/reading/interdisciplinary_chronology.html">Explore the chronology →</a><a href="/assets/reading/interdisciplinary_sources.html">52 sources &amp; reading depth →</a></div></div>
<div class="reading-callout"><p class="eyebrow">NEW PHYSICAL STUDIES</p><h2>Rocks, amplification and an earlier boundary.</h2><p>Explore the three mechanisms with saved calculations and real MOLA profiles. Learn how to evaluate magnetic evidence before inferring a field.</p><div class="download-links"><a href="/research/physics">Open the physical studies →</a><a href="/research/physics?view=paleomagnetism">Learn paleomagnetism →</a></div></div>
<section aria-labelledby="findingsHeading"><div class="section-top"><div><p class="eyebrow">FROM OUR COMPUTATIONS</p><h2 id="findingsHeading">What the tests are showing</h2></div><a href="/research/tests">All results & downloads →</a></div>{cards}</section>
<section class="programme-strip"><div><p class="eyebrow">FOLLOW THE RESEARCH</p><h2>From a map to a testable question.</h2><p>Start with a measurement, compare possible explanations, then inspect the calculations. A synthetic result, a published interpretation and an observation each carry a different kind of evidence.</p><a href="/research/comparison">Compare the four origin scenarios →</a></div><div class="programme-links"><a href="/research/pilot"><span>A guided regional study<small>Five steps from crater selection to magnetic contrast</small></span><b>→</b></a><a href="/research/comparison?view=timeline"><span>Put the events in order<small>Formation, alteration, magnetization and ejection</small></span><b>→</b></a><a href="/research/dynamo"><span>What should we test next?<small>Dynamo proposals, completed checks and missing constraints</small></span><b>→</b></a></div></section>
<details class="reading-drawer"><summary>New to the subject? Four useful terms</summary><dl class="site-glossary"><dt>Dichotomy</dt><dd>The large contrast between the northern lowlands and southern highlands.</dd><dt>Remanence</dt><dd>A magnetic memory preserved in rock, which can be acquired or modified more than once.</dd><dt>Dynamo</dt><dd>A process in a planet’s conducting interior that can generate a global magnetic field.</dd><dt>Ma / Ga</dt><dd>Millions / billions of years before the present. Different clocks can date different events.</dd></dl></details>'''
    (ROOT/'web/home.html').write_text(page('Overview','/',home))
    results=f'''<div class="page-intro"><p class="eyebrow">RESULTS / ORIGINAL PROJECT CALCULATIONS</p><h1>What we have tested.<br>What it changes.</h1><p class="lead">Start with the findings, open an interactive experiment, or download the saved outputs. These checks sharpen the questions; they do not yet select an origin of the dichotomy.</p></div><nav class="result-jumps" aria-label="Results sections"><a href="#findings">Key findings</a><a href="/research/physics">New physical studies ↗</a><a href="/research/physics?view=paleomagnetism">Learn paleomagnetism ↗</a><a href="#workbenches">Experiments & downloads</a><a href="#diagnostics">Dataset diagnostics</a><a href="/research/dynamo">Next tests ↗</a></nav>
<section id="findings" aria-label="Key findings">{cards}</section>
<section id="workbenches" class="results-section"><div class="section-top"><div><p class="eyebrow">INSPECT · CHANGE ASSUMPTIONS · REUSE</p><h2>Open a research workbench</h2></div></div><div class="workbench-grid">
<article class="workbench-card"><span class="evidence-label">Crust & rocks</span><h3>More crust, or lighter crust?</h3><p>Separate density and thickness contributions to highland support. Keep dense basal material in the mass budget.</p><a href="/research/physics?view=crust">Explore composition & buoyancy →</a></article>
<article class="workbench-card"><span class="evidence-label synthetic">Thermal amplification</span><h3>Can a small lead become a hemisphere?</h3><p>Compare wavelength growth and initial power spectra. The fastest mode does not necessarily dominate.</p><a href="/research/physics?view=feedback">Explore amplification →</a></article>
<article class="workbench-card"><span class="evidence-label">MOLA & deformation</span><h3>Which earlier edge could fit?</h3><p>Conditionally undo assumed loads. Identify where a boundary proxy switches features instead of tracking motion.</p><a href="/research/physics?view=boundary">Explore boundary restoration →</a></article>
<article class="workbench-card"><span class="evidence-label">Regional study</span><h3>How fair is the terrain comparison?</h3><p>Newton changes sign after surface-unit standardization. Schiaparelli changes sign with altitude. Follow the controls behind these contrasts.</p><a href="/research/pilot/results">View regional results →</a><div class="download-links"><a href="/research/pilot">Guided study</a><a href="/research/files/pilot/results.json" download>Results JSON ↓</a></div></article>
<article class="workbench-card"><span class="evidence-label synthetic">Thermal model</span><h3>When can a rock record a field?</h3><p>Follow cooling and reheating through depth and time. Temperature compatibility is a necessary check, not a guarantee of long-term preservation.</p><a href="/research/thermal">Explore thermal histories →</a><div class="download-links"><a href="/assets/reading/thermal_experiment.html">Method & outputs</a></div></article>
<article class="workbench-card"><span class="evidence-label synthetic">Detection test</span><h3>Could an instrument see the signal?</h3><p>Compare signal attenuation with altitude and injection–recovery trials. An ideal detectable signal need not identify a unique field history.</p><a href="/research/experiments?view=detection">Explore detectability →</a><div class="download-links"><a href="/assets/reading/executed_experiments.html">Methods & all exports</a><a href="/research/files/experiments/manifest.json" download>Run manifest ↓</a></div></article>
</div><details class="method-drawer"><summary>Download the three featured result sets</summary><div class="download-links"><a href="/research/files/experiments/maps.json" download>Regional prediction · JSON ↓</a><a href="/research/files/experiments/recording.json" download>Magnetic recording · JSON ↓</a><a href="/research/files/experiments/laboratory.json" download>Laboratory fits · JSON ↓</a></div><p>Saved calculations from the permitted input snapshot. The linked methods explain assumptions, reproducible commands, validation and CSV exports.</p></details></section>
<section id="diagnostics" class="results-section"><div class="section-top"><div><p class="eyebrow">FOUNDATIONS / CHECK THE INPUTS FIRST</p><h2>What the assembled datasets support</h2></div></div><p id="testStatus" role="status">Loading completed diagnostics…</p><div id="testCards" class="test-list"></div><details class="method-drawer"><summary>Methods, provenance & diagnostic outputs</summary><p>These figures show a saved run. No calculation or large download starts when you open this page. Reproduction requires the permitted inputs listed in each method and the corresponding optional dependencies.</p><div class="download-links"><a href="/assets/reading/first_results.html">Diagnostic method →</a><a href="/research/files/data/results.json" download>Results · JSON ↓</a><a href="/research/files/data/first_diagnostics.svg" download>Scientific figure · SVG ↓</a><a href="/research/data?view=sources">Input provenance →</a></div></details></section>'''
    scripts='<script defer src="/assets/plotly.min.js"></script><script defer src="/assets/observations.js?v=design1"></script>'
    (ROOT/'web/tests.html').write_text(page('Results','/research/tests',results,scripts))

if __name__=='__main__':
    render()
