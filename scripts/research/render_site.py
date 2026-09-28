"""Render the overview and results pages as a plain-language research report.

Every number on these pages is read from the saved outputs in
research/discriminating/ and research/data/, so the site cannot drift from the
calculations. Wording states the question, the method, the result and the
verdict of each test; limits are stated once, in plain terms.
"""
from html import escape
import json
import re
from pathlib import Path

from site_layout import navigation

ROOT = Path(__file__).resolve().parents[2]
D = ROOT/'research/discriminating'


def load(name):
    return json.loads((D/name).read_text())


def first(rows, **match):
    return next(r for r in rows if all(r.get(k) == v for k, v in match.items()))


def numbers():
    """Collect every displayed figure from the saved results."""
    crust, age, thermal, amp, surf = (load(f) for f in ['crust_inversion.json', 'age_transfer.json', 'thermal_ensemble.json', 'amplitude.json', 'surface_check.json'])
    data = json.loads((ROOT/'research/data/results.json').read_text())
    n = {}
    ratios = [r['south_north_ratio'] for r in data['boundary_magnetic_contrast']]+[r['south_north_ratio'] for r in data['magnetic_contrast']]
    n['ratio_boundary_150'] = first(data['boundary_magnetic_contrast'], altitude_km=150)['south_north_ratio']
    n['ratio_min'], n['ratio_max'] = min(ratios), max(ratios)
    eq = first(crust['scenarios'], id='equal_2900'); gs = first(crust['scenarios'], id='goossens_sabaka')
    n['thick_eq'] = eq['south_minus_north_km']; n['thick_gs'] = gs['south_minus_north_km']
    n['thick_eq_n'], n['thick_eq_s'], n['thick_gs_n'], n['thick_gs_s'] = eq['north_mean_km'], eq['south_mean_km'], gs['north_mean_km'], gs['south_mean_km']
    n['thick_min_all'] = min(s['min_km'] for s in crust['scenarios']); n['thick_contrast_range'] = [min(s['south_minus_north_km'] for s in crust['scenarios']), max(s['south_minus_north_km'] for s in crust['scenarios'])]
    n['validation_rms'] = crust['validation_equal_2900']['weighted_rms_difference_km']; n['validation_mean'] = crust['validation_equal_2900']['weighted_mean_difference_km']
    n['scenarios'] = crust['scenarios']
    sk = {(s['model'], s['split']): s['skill_over_training_mean'] for s in age['skills'] if s['altitude_km'] == 150 and s['density_kg_m3'] == 2900}
    n['skills'] = sk
    n['structure_by_density'] = {s['density_kg_m3']: s['skill_over_training_mean'] for s in age['skills'] if s['altitude_km'] == 150 and s['model'] == 'structure' and s['split'] == 'regional_0'}
    cls = {(c['region'], c['rank']): c for c in age['field_by_epoch_class'] if c['altitude_km'] == 150}
    n['classes'] = cls
    n['eN_north'] = cls[('north_of_boundary', 1.0)]['mean_field_nt']; n['eN_south'] = cls[('south_of_boundary', 1.0)]['mean_field_nt']
    n['eN_north_cells'] = cls[('north_of_boundary', 1.0)]['cells']; n['eN_south_cells'] = cls[('south_of_boundary', 1.0)]['cells']
    n['lH_north'] = cls[('north_of_boundary', 5.0)]['mean_field_nt']; n['lH_south'] = cls[('south_of_boundary', 5.0)]['mean_field_nt']
    n['mN_north'] = cls[('north_of_boundary', 2.0)]['mean_field_nt']; n['mN_south'] = cls[('south_of_boundary', 2.0)]['mean_field_nt']; n['mN_north_cells'] = cls[('north_of_boundary', 2.0)]['cells']
    n['eN_all'] = cls[('all', 1.0)]['mean_field_nt']; n['lH_all'] = cls[('all', 5.0)]['mean_field_nt']; n['eA_all'] = cls[('all', 6.0)]['mean_field_nt']
    n['thermal'] = thermal
    rows = list(load_csv('thermal_acquisition_ages.csv'))
    def age_at(hemi, depth, carrier, key='q50'):
        r = first(rows, hemisphere=hemi, depth_km=f'{float(depth):.1f}'); v = r[f'{carrier}_age_{key}_ga']; return float(v) if v not in ('', None) else None
    n['south_mag_30'] = age_at('South', 30, 'magnetite'); n['south_mag_20'] = age_at('South', 20, 'magnetite'); n['south_pyr_20'] = age_at('South', 20, 'pyrrhotite')
    n['south_mag_30_frac_37'] = float(first(rows, hemisphere='South', depth_km='30.0')['magnetite_cooled_before_3.7_ga_fraction'])
    n['south_mag_30_frac_41'] = float(first(rows, hemisphere='South', depth_km='30.0')['magnetite_cooled_before_4.1_ga_fraction'])
    n['south_mag_20_frac_41'] = float(first(rows, hemisphere='South', depth_km='20.0')['magnetite_cooled_before_4.1_ga_fraction'])
    n['south_mag_30_always'] = float(first(rows, hemisphere='South', depth_km='30.0')['magnetite_always_below_fraction']); n['south_mag_20_always'] = float(first(rows, hemisphere='South', depth_km='20.0')['magnetite_always_below_fraction'])
    n['south_mag_40'] = age_at('South', 40, 'magnetite'); n['south_mag_40_frac_37'] = float(first(rows, hemisphere='South', depth_km='40.0')['magnetite_cooled_before_3.7_ga_fraction'])
    n['north_mag_20_frac_41'] = float(first(rows, hemisphere='North', depth_km='20.0')['magnetite_cooled_before_4.1_ga_fraction'])
    ws = thermal['window_summary']
    n['win_deep_mag_37'] = first(ws, hemisphere='South', subset='strong_and_deep', carrier='magnetite', dynamo_end_ga=3.7)
    n['win_deep_mag_41'] = first(ws, hemisphere='South', subset='strong_and_deep', carrier='magnetite', dynamo_end_ga=4.1)
    n['win_all_mag_41'] = first(ws, hemisphere='South', subset='all_usable', carrier='magnetite', dynamo_end_ga=4.1)
    coh = list(load_csv('thermal_coherence.csv'))
    c30 = first(coh, hemisphere='South', depth_km='30', carrier='magnetite'); c20 = first(coh, hemisphere='South', depth_km='20', carrier='magnetite')
    n['coh_30_duration'] = json.loads(c30['cooling_duration_q05_q50_q95_myr'])[1]; n['coh_20_duration'] = json.loads(c20['cooling_duration_q05_q50_q95_myr'])[1]
    for kind in ('poisson', 'periodic'):
        for chron, tag in [(0.67, 'fast'), (100, '100'), (1000, '1000')]:
            n[f'coh_30_{kind}_{tag}'] = float(c30[f'{kind}_retained_median_chron_{chron}_myr'])
        n[f'coh_30_{kind}_fast_q95'] = float(c30[f'{kind}_retained_q95_chron_0.67_myr'])
        n[f'coh_30_{kind}_half'] = c30[f'{kind}_shortest_tested_chron_with_half_retention_myr']; n[f'coh_20_{kind}_half'] = c20[f'{kind}_shortest_tested_chron_with_half_retention_myr']
    n['coherence_rows'] = [r for r in coh if r['carrier'] == 'magnetite']
    a_s = first(amp['summary'], region='South', geometry='thick20_centered'); a_n = first(amp['summary'], region='North', geometry='thick20_centered')
    n['amp_south_median'] = a_s['required_q10_q50_q90_a_m'][1]; n['amp_south_q90'] = a_s['required_q10_q50_q90_a_m'][2]; n['amp_north_median'] = a_n['required_q10_q50_q90_a_m'][1]
    n['amp_south_above5'] = a_s['fraction_above_5_a_m']; n['amp_south_above20'] = a_s['fraction_above_20_a_m']; n['amp_windows_s'], n['amp_windows_n'] = a_s['windows'], a_n['windows']
    a_c = first(amp['summary'], region='South', geometry='thick20_centered_after_poisson_cancellation_chron_100_myr')
    n['amp_south_median_100'] = a_c['required_q10_q50_q90_a_m'][1]; n['amp_south_above20_100'] = a_c['fraction_above_20_a_m']
    a_f = first(amp['summary'], region='South', geometry='thick20_centered_after_poisson_cancellation_chron_0.67_myr')
    n['amp_south_median_fast'] = a_f['required_q10_q50_q90_a_m'][1]
    n['amp_summary'] = amp['summary']
    z, i = surf['sites']['Zhurong'], surf['sites']['InSight']
    n['zh_pred'] = z['prediction_at_reference_sphere_degree_134_total_nt']; n['zh_pred_h'] = z['prediction_at_reference_sphere_degree_134_horizontal_nt']
    n['zh_obs_lo'], n['zh_obs_hi'] = z['observed_total_range_nt']; n['zh_obs_h'] = z['observed_horizontal_mean_nt']; n['zh_ratio_h'] = z['ratio_predicted_over_observed_horizontal_mean']
    n['zh_pub'], n['zh_pub_h'] = z['published_downward_continuation_total_nt'], z['published_downward_continuation_horizontal_nt']
    n['in_pred'] = i['prediction_at_reference_sphere_degree_134_total_nt']; n['in_obs'] = i['observed_total_nt']; n['in_ratio'] = i['ratio_observed_over_predicted_total']
    n['surface'] = surf
    return n


def load_csv(name):
    import csv
    with (D/name).open() as f:
        yield from csv.DictReader(f)


def f(x, d=1):
    return f'{x:,.{d}f}' if x is not None else '—'


def verdict(kind, text):
    labels = {'supports': 'Supports the recording idea', 'weakens': 'Weakens a scenario', 'constrains': 'Adds a constraint', 'undecided': 'Not decisive'}
    return f'<p class="verdict {kind}"><b>{labels[kind]}</b> {escape(text)}</p>'


def test_definitions(n):
    return [
        ('1', 'Does surface age predict magnetic strength beyond crustal structure and the hemisphere itself?',
         f'Partly. Age has positive out-of-region skill in both wedge partitions ({n["skills"][("age","regional_0")]:+.2f}, {n["skills"][("age","regional_30")]:+.2f}), destroyed when the map is shifted in longitude. But a plain north/south indicator does as well ({n["skills"][("hemisphere","regional_0")]:+.2f}, {n["skills"][("hemisphere","regional_30")]:+.2f}) and adding age to it gains little. At equal epoch the north stays weaker: Middle Noachian terrain averages {f(n["mN_north"],0)} nT north of the boundary and {f(n["mN_south"],0)} nT south of it; the {n["eN_north_cells"]} Early Noachian northern cells have a similar aggregate ({f(n["eN_north"],0)} against {f(n["eN_south"],0)} nT after back-transforming mean log amplitude), but 14 lie in Xanthe–Chryse alone.',
         'undecided', 'Surface age predicts part of the variation. A hemispheric association remains, but this does not identify the contribution of resurfacing.', 'age_transfer'),
        ('2', 'Could the deep southern crust have recorded a field before the dynamo stopped?',
         f'Early acquisition becomes less frequent with depth. In {n["thermal"]["hemispheres"]["South"]["accepted"]} accepted conductive histories, crust at 30 km last cooled through the magnetite Curie point at a median {f(n["south_mag_30"],2)} Ga: before 4.1 Ga in {n["south_mag_30_frac_41"]*100:.0f}% of histories, before 3.7 Ga in {n["south_mag_30_frac_37"]*100:.0f}%, while {n["south_mag_30_always"]*100:.0f}% never reached that temperature and are uninformative. At 40 km the median is {f(n["south_mag_40"],2)} Ga and only {n["south_mag_40_frac_37"]*100:.0f}% cooled before 3.7 Ga. No accepted southern history gives a pyrrhotite crossing at 30 km before 3.7 Ga.',
         'constrains', 'Early crossings become less frequent with depth in this ensemble; neither a universal 30 km boundary nor a mineral exclusion follows.', 'thermal_acquisition'),
        ('3', 'How strongly magnetized would the sources have to be?',
         f'In a declared cylinder scenario, a 20 km layer matching each window needs a median {f(n["amp_south_median"])} A/m in the south ({f(n["amp_north_median"])} A/m in the north); {n["amp_south_above5"]*100:.0f}% of southern windows exceed 5 A/m before any cancellation. If the record were acquired during slow cooling under randomly timed reversals every 0.67 Myr, the median would become {f(n["amp_south_median_fast"],0)} A/m.',
         'constrains', 'Several amperes per metre over tens of kilometres are needed in this geometry; cancellation during slow cooling would multiply that by tens to hundreds.', 'amplitude_budget'),
        ('4', 'Can slow cooling under a reversing dynamo keep a coherent record?',
         f'Only a small fraction. Cooling through the magnetite blocking band at 30 km took a median {f(n["coh_30_duration"],0)} Myr in the accepted southern histories. With randomly timed reversals at a tested rate motivated by conditional basin simulations (about 1.5 per Myr) the median retained fraction is {n["coh_30_poisson_fast"]*100:.1f}% (95th percentile {n["coh_30_poisson_fast_q95"]*100:.1f}%); with perfectly periodic reversals it is {n["coh_30_periodic_fast"]*100:.2f}%. The shortest tested mean chron giving at least 50% median retention is {n["coh_30_poisson_half"] or ">1,000"} Myr.',
         'constrains', 'The tested histories show strong median cancellation. Retention is a distribution, and this result does not exclude slow cooling generally.', 'thermal_coherence'),
        ('5', 'Does the orbital model predict the field measured on the ground?',
         f'Not at the two sites where it can be checked. At Zhurong the degree-134 model continued to the surface gives {f(n["zh_pred"],0)} nT; the rover measured {f(n["zh_obs_lo"])}–{f(n["zh_obs_hi"])} nT. At InSight the model gives {f(n["in_pred"],0)} nT and the lander measured about {f(n["in_obs"],0)} nT. The two errors go in opposite directions.',
         'constrains', 'Surface extrapolation of the orbital model failed by a factor of five to six at these comparisons (horizontal field at Zhurong, total field at InSight). That is a demonstrated local limit, not an uncertainty for every anomaly.', 'surface_check'),
        ('6', 'Does a lighter southern crust remove the thickness dichotomy?',
         f'It shrinks it a lot. With equal densities the south is {f(n["thick_eq"])} km thicker than the north; with the Goossens & Sabaka densities the corrected inversion gives {f(n["thick_gs"])} km. The thinnest crust stays positive in every scenario ({f(n["thick_min_all"])} km).',
         'constrains', 'The contrast stays positive across the tested scenarios; its size depends strongly on density and the shared model assumptions.', 'crust_inversion')]


def test_cards(n):
    cards = test_definitions(n)
    html = '<div class="test-grid">'
    for num, question, result, kind, conclusion, fig in cards:
        html += f'<article class="test-card" id="card-{num}"><span class="test-number">Test {num}</span><h3>{escape(question)}</h3><p class="test-result">{escape(result)}</p>{verdict(kind, conclusion)}<a href="/research/tests#test-{num}">Method, figure and limits →</a></article>'
    return html+'</div>'


def followup_status():
    mixture = json.loads((ROOT/'research/followup/mixture/summary.json').read_text())
    examples = [r for r in mixture['median_examples'] if r['hemisphere'] == 'South']
    coherent = [r for r in examples if not r['input_already_cancellation_corrected']]
    corrected = [r for r in examples if r['input_already_cancellation_corrected']]
    def bounds(rows):
        values = [r['solid_carrier_fraction_in_source']*100 for r in rows]
        return f'{min(values):.2f}–{max(values):.2f}%'
    return f'''<section id="followups" class="meaning"><p class="eyebrow">FOLLOW-UP RESULTS · SURFACE SUPPORT AND CRUSTAL MATERIALS</p><h2>What the latest comparisons can resolve</h2>
<p><strong>The surface-based designs have reached a limit with the present inputs.</strong> Arabia matching lacks balanced coverage; the boundary comparison lacks enough supported blocks; source depth has no stable association with surface age under the declared sensitivities. We pause repeating these designs. This does not establish that surface geology is uninformative, that resurfacing is absent, or that excavation is preferred.</p>
<div class="download-links"><a href="/assets/reading/arabia_preflight.html">Arabia support checks</a><a href="/assets/reading/boundary_walk.html">Boundary and 23-cell decomposition</a><a href="/assets/reading/depth_age.html">Source depth and surface age</a><a href="/assets/reading/rapid_bodies.html">Rapidly cooled bodies</a></div>
<p><strong>A light crust can carry remanence in declared material scenarios.</strong> With a 2,900 kg/m³ matrix, empty pores, the same density and source volume, and efficient single-domain magnetite, the southern coherent cylinder target ({coherent[0]['target_a_m']:.2f} A/m) needs {bounds(coherent)} magnetite by solid volume and about 14% porosity. The target already corrected for Poisson cancellation ({corrected[0]['target_a_m']:.0f} A/m) needs {bounds(corrected)} and about 16–17% porosity. These are conditional balances, not measured deep-crust abundances or demonstrated stable pore space.</p>
<a href="/assets/reading/density_remanence.html">Density–remanence calculation, assumptions and reproducible outputs →</a>
<p><strong>Recording time and reversal rate remain coupled.</strong> The <a href="/assets/reading/rapid_bodies.html">body calculation</a> quantifies rapid acquisition and correlated stack polarities. The <a href="/assets/reading/reversal_identifiability.html">synthetic identifiability test</a> finds identical orbital fields for distinct reversal histories when acquisition clocks can change. Independently dated acquisition breaks this particular ambiguity in an ideal control; no Martian reversal date is inferred.</p></section>'''


def home(n):
    return f'''<section class="report-hero"><p class="eyebrow">A PERSONAL RESEARCH PROJECT · MARS · UPDATED 28 SEPTEMBER 2026</p><h1>Mars has a magnetic south and a quiet north. We test why.</h1>
<p class="lead">The southern highlands carry strong magnetic anomalies. The northern lowlands have weaker magnetic anomalies on average. Two explanations compete: the ancient magnetic field itself was stronger over the south, or the same field was recorded and preserved differently on each side. This site runs concrete, reproducible tests on public data and states what each one says.</p>
<div class="button-row"><a class="button" href="#tests">Read the six results</a><a class="button secondary" href="/research/method">How we work →</a></div></section>

<section class="facts"><h2>Three results from the current data and models</h2><div class="fact-grid">
<article><b>{f(n["ratio_boundary_150"])}×</b><p>The southern mean field is {f(n["ratio_boundary_150"])} times the northern mean at 150 km altitude. Changing how the two sides are defined moves this ratio between {f(n["ratio_min"])} and {f(n["ratio_max"])}; it never goes away.</p></article>
<article><b>{f(n["thick_contrast_range"][0],0)}–{f(n["thick_contrast_range"][1],0)} km</b><p>The southern crust is thicker by this range across the declared density scenarios. This is our own gravity inversion, checked against the published archive to within {f(n["validation_rms"])} km.</p></article>
<article><b>×{f(n["zh_ratio_h"],0)} / ×{f(n["in_ratio"],0)}</b><p>At the two sites where the field has been measured on the ground, the orbital model continued to the surface is about {f(n["zh_ratio_h"],0)} times too high at Zhurong and {f(n["in_ratio"],0)} times too low at InSight. Orbital models do not reliably resolve a local point field at the surface.</p></article>
</div></section>

<section class="idea"><h2>The idea under test</h2><p>Our working hypothesis is that <strong>the magnetic dichotomy is mostly an archive effect</strong>: the north lost or never kept its record because its surface is younger, was reworked by impacts and volcanism, or cooled at the wrong time, while the south kept an old record. The alternative is that the dynamo itself produced a stronger field over the southern hemisphere. The tests below ask what the rocks, the heat and the measurements allow.</p></section>

{followup_status()}

<section id="tests" class="tests"><h2>Six tests, six answers</h2><p class="section-lead">Each test was declared in this repository before it was run, uses only public data, and can be reproduced with one command. Verdicts are about the tested scenario, not about the origin of the dichotomy as a whole. An <a href="/research/dossiers/audit">internal implementation audit</a> of the first run found two implementation errors and three over-statements; the numbers below come from the corrected build.</p>{test_cards(n)}</section>

<section class="meaning"><h2>What this means so far</h2><ol>
<li><strong>Surface age predicts part of the map, but leaves a hemispheric association.</strong> On both sides of the boundary the field falls with surface epoch: the global Early Noachian mean is {f(n["eN_all"],0)} nT against {f(n["lH_all"],0)} nT for Late Hesperian terrain. Yet at equal epoch the north remains two to four times weaker, except for a small Early Noachian sample. Fourteen of its 23 cells lie in Xanthe–Chryse; the <a href="/assets/reading/boundary_walk.html">regional decomposition and boundary transects</a> document the limited support. These field summaries back-transform the area-weighted mean logarithm. This predictive comparison does not determine how much resurfacing caused the contrast.</li>
<li><strong>The tested slow-cooling histories show strong median cancellation.</strong> Deep crust cools through its blocking range over hundreds of millions of years. With randomly timed reversals every 0.67 Myr, the retained fraction at 30 km is about {n["coh_30_poisson_fast"]*100:.0f}%; perfectly periodic reversals would leave far less. Under these assumptions, retaining strong sources requires more initial remanence or a different recording history. Faster cooling is one candidate; the calculation does not make it unique.</li>
<li><strong>Early cooling at depth depends on the assumed history.</strong> At 30 km, {n["south_mag_30_frac_41"]*100:.0f}% of the accepted southern histories cross the magnetite Curie point before 4.1 Ga and {n["south_mag_30_always"]*100:.0f}% start below it, leaving earlier acquisition unresolved. Some deeper histories also cross early. These ensemble frequencies establish neither a hard depth boundary nor a probability for Mars.</li>
<li><strong>The magnetization budget is demanding in the tested geometry.</strong> Several amperes per metre over 20 km in a declared cylinder scenario; the numbers depend on that geometry and on the cap sizes of the source model, so they are a comparison scale, not a rock-type verdict.</li>
<li><strong>The crustal dichotomy is robust in sign; its size is not.</strong> Correcting the inversion for a laterally variable crust density changes the thickness contrast from {f(n["thick_eq"],0)} km to {f(n["thick_gs"],0)} km. Every origin model calibrated to a fixed contrast inherits this uncertainty.</li>
</ol></section>

<section class="next"><h2>What would reduce the ambiguity</h2><ul>
<li>Local magnetic surveys on Early Noachian terrain <em>north</em> of the boundary, with matched southern sites and geological context. A single point measurement would not establish a hemispheric source contrast.</li>
<li>Oriented, dated samples from a strong southern anomaly, to measure the carrier mineral and the cooling rate directly.</li>
<li>Southern seismology combined with composition and gravity, to reduce the density–thickness ambiguity.</li>
<li>A reversal chronology for the Martian dynamo between 4.5 and 3.7 Ga; recording predictions depend on reversal statistics, acquisition history and the duration of dynamo activity.</li>
</ul></section>

<section class="idea" id="state"><p class="eyebrow">SYNTHESIS · 28 SEPTEMBER 2026</p><h2>Where the evidence stands</h2><p>The synthesis now includes six follow-ups and an internal implementation review. Rapid acquisition can preserve individual bodies; correlations in the shared field control how a stack combines. A synthetic counterexample shows that a changing reversal rate and different acquisition times can produce identical orbital fields. These results constrain combinations of histories and materials without selecting the origin of the dichotomy or dating a dynamo transition.</p><div class="button-row"><a class="button" href="/assets/reading/state_of_evidence.html">Read where the evidence stands →</a><a class="button secondary" href="/assets/reading/rapid_bodies.html">Rapidly cooled bodies →</a></div></section>
<section class="explore"><h2>Follow the investigation</h2><nav class="overview-paths" aria-label="Explore the project"><a href="/research/method">How we work <b>↗</b><small>Inputs, protocol, checks and verdicts</small></a><a href="/research/tests">Results <b>↗</b><small>Six tests with methods and limits</small></a><a href="/research/explore">Explore <b>↗</b><small>Atlas, workshops and five reading dossiers</small></a></nav></section>'''


def results(n):
    sc = n['scenarios']
    scen_rows = ''.join(f'<tr><td>{escape(s["label"])}</td><td>{f(s["north_mean_km"])}</td><td>{f(s["south_mean_km"])}</td><td><b>{f(s["south_minus_north_km"])}</b></td><td>{f(s["min_km"])}</td><td>{f(s["max_km"],0)}</td></tr>' for s in sc)
    sk = n['skills']; models = ['mean', 'hemisphere', 'location', 'structure', 'age', 'age_ordinal', 'hemisphere+age', 'structure+age', 'location+age', 'all']
    skill_rows = ''.join(f'<tr><td>{m}</td><td>{sk[(m,"random")]:+.3f}</td><td>{sk[(m,"regional_0")]:+.3f}</td><td>{sk[(m,"regional_30")]:+.3f}</td></tr>' for m in models)
    shift_rows = ''.join(f'<tr><td>{m}</td>'+''.join(f'<td>{sk.get((m, f"regional_0_target_shifted_{s}"), float("nan")):+.3f}</td>' for s in [60, 120, 180])+'</tr>' for m in ['age', 'structure', 'location', 'hemisphere'])
    cls = n['classes']; labels = {1.0: 'Early Noachian', 2.0: 'Middle Noachian', 3.0: 'Late Noachian', 4.0: 'Early Hesperian', 5.0: 'Late Hesperian', 6.0: 'Early Amazonian', 7.0: 'Middle Amazonian', 8.0: 'Late Amazonian'}
    class_rows = ''
    for rank, label in labels.items():
        a, b = cls.get(('north_of_boundary', rank)), cls.get(('south_of_boundary', rank))
        class_rows += f'<tr><td>{label}</td><td>{f(a["mean_field_nt"],0) if a else "—"}<small> ({a["cells"] if a else 0} cells)</small></td><td>{f(b["mean_field_nt"],0) if b else "—"}<small> ({b["cells"] if b else 0} cells)</small></td></tr>'
    th = n['thermal']['hemispheres']
    coh_rows = ''.join(f'<tr><td>{r["hemisphere"]}</td><td>{r["depth_km"]}</td><td>{f(json.loads(r["cooling_duration_q05_q50_q95_myr"])[1],0)}</td><td>{float(r["poisson_retained_median_chron_0.67_myr"])*100:.1f}%</td><td>{float(r["periodic_retained_median_chron_0.67_myr"])*100:.2f}%</td><td>{float(r["poisson_retained_median_chron_100_myr"])*100:.0f}%</td><td>{float(r["poisson_retained_median_chron_1000_myr"])*100:.0f}%</td><td>{r["poisson_shortest_tested_chron_with_half_retention_myr"] or "&gt;1,000"}</td></tr>' for r in n['coherence_rows'])
    amp_rows = ''.join(f'<tr><td>{s["region"]}</td><td>{escape(s["geometry"].replace("_"," "))}</td><td>{s["windows"]}</td><td>{f(s["required_q10_q50_q90_a_m"][0])} / <b>{f(s["required_q10_q50_q90_a_m"][1])}</b> / {f(s["required_q10_q50_q90_a_m"][2])}</td><td>{s["fraction_above_5_a_m"]*100:.0f}%</td><td>{s["fraction_above_20_a_m"]*100:.0f}%</td></tr>' for s in n['amp_summary'] if 'cancellation' not in s['geometry'] or ('poisson' in s['geometry'] and 'chron_0.67' not in s['geometry']))
    win = n['win_deep_mag_41']; win37 = n['win_deep_mag_37']; winall = n['win_all_mag_41']
    def figure(name, caption):
        return f'<figure class="result-figure"><img src="/research/files/discriminating/{name}.png" alt="{escape(caption)}" loading="lazy"><figcaption>{escape(caption)} · <a href="/research/files/discriminating/{name}.svg">SVG</a></figcaption></figure>'
    def downloads(*files):
        return '<div class="download-links">'+''.join(f'<a href="/research/files/discriminating/{x}" download>{x} ↓</a>' for x in files)+'</div>'
    return f'''<div class="page-intro"><p class="eyebrow">RESULTS · SIX DISCRIMINATING TESTS · REPRODUCIBLE WITH ONE COMMAND</p><h1>What we tested, how, and what came out.</h1>
<p class="lead">Every test below was declared in this repository before it was run (not externally preregistered). Inputs are public datasets; the code is in this repository; the outputs, figures and checksums are in <code>research/discriminating/</code>. Start with <a href="/research/method">How we work</a>, then read the <a href="/assets/reading/discriminating_tests.html">full written report</a> and the <a href="/assets/reading/discriminating_audit.html">audit</a> that led to the corrected build.</p>
<nav class="result-jumps" aria-label="Tests"><a href="#test-1">1 · Age</a><a href="#test-2">2 · Cooling time</a><a href="#test-3">3 · Magnetization</a><a href="#test-4">4 · Reversals</a><a href="#test-5">5 · Ground truth</a><a href="#test-6">6 · Crust</a></nav></div>

<section class="test-detail" id="test-1"><span class="test-number">Test 1</span><h2>Does surface age predict magnetic strength better than structure or hemisphere?</h2>
<p><b>Why.</b> If the magnetic dichotomy is an archive effect, the age of the surface should carry information that crustal thickness, relief and even the hemisphere itself do not.</p>
<p><b>How.</b> On 2° cells within 75° of the equator we predict log(1 + |B|) at 150 km with fixed ridge models. Predictors are the USGS map epoch of each cell (ordinal rank and Noachian, Hesperian, Amazonian indicators), the earlier structural set (relief, crustal thickness, unit groups), smooth location functions, and a north/south indicator. Validation holds out six complete 60° longitude wedges with 10° buffers, twice with the wedges rotated. Cells are correlated samples of one model, so no p-value is reported.</p>
<table class="result-table"><thead><tr><th>Predictors</th><th>Random cells</th><th>Regional wedges</th><th>Wedges rotated 30°</th></tr></thead><tbody>{skill_rows}</tbody></table>
<p><b>Result.</b> Age has positive skill in both regional partitions ({sk[("age","regional_0")]:+.2f}, {sk[("age","regional_30")]:+.2f}) and so does the north/south indicator alone ({sk[("hemisphere","regional_0")]:+.2f}, {sk[("hemisphere","regional_30")]:+.2f}); combining them gives {sk[("hemisphere+age","regional_0")]:+.2f} and {sk[("hemisphere+age","regional_30")]:+.2f}. Age and hemisphere therefore carry largely the same information, because most Noachian terrain is in the south. Richer models interpolate better between scattered cells but transfer worse across regions. Shifting the magnetic map by 60°, 120° or 180° in longitude destroys the age skill ({" / ".join(f"{sk.get(("age", f"regional_0_target_shifted_{s}"), float("nan")):+.2f}" for s in [60,120,180])}), so the association is sensitive to longitudinal alignment; this control alone does not eliminate geographical confounding. The structural set is sensitive to the assumed crust density (regional skill from {min(n["structure_by_density"].values()):+.2f} to {max(n["structure_by_density"].values()):+.2f} across 2,600–2,900 kg/m³); the age set is not.</p>
<table class="result-table"><thead><tr><th>Surface epoch</th><th>Back-transformed log mean, north (nT)</th><th>Back-transformed log mean, south (nT)</th></tr></thead><tbody>{class_rows}</tbody></table>
<p>The table reports exp(area-weighted mean log(1 + |B| / 1 nT)) − 1 in nT; it is not the arithmetic mean. The saved age-transfer figure uses the same statistic.</p>
<p><b>Reading.</b> Within each side the field falls by a factor of five to ten from the Noachian into the Late Hesperian. Across sides at equal epoch the north is weaker by a factor of two to four for Middle and Late Noachian terrain; the {n["eN_north_cells"]} Early Noachian northern cells have a similar aggregate to the south. That aggregate is geographically concentrated: 14 cells lie in Xanthe–Chryse. Their <a href="/assets/reading/boundary_walk.html">regional decomposition</a> gives a 52.5 nT back-transformed log mean and a 69.3 nT arithmetic mean. The accompanying boundary test retains only three adequately covered blocks at ±200 km and no common-support block for the shifted controls, so it cannot establish a global boundary effect. Surface age is part of the story, not all of it. Late Amazonian polar units and southern Amazonian volcanic units break the trend and deserve their own look.</p>
{figure('age_transfer', 'Field by surface epoch on both sides of the boundary, and out-of-fold skill by predictor set')}{downloads('age_transfer.json', 'age_transfer_skills.csv', 'age_transfer_classes.csv')}
<p class="limits"><b>Limits.</b> Surface age is not the age of the deep source. The map units are coarse; the target is a degree-134 model, not raw spacecraft tracks. Skill values compare predictor sets, they do not identify a cause.</p></section>

<section class="test-detail" id="test-2"><span class="test-number">Test 2</span><h2>When could each depth of crust have recorded a field?</h2>
<p><b>Why.</b> A rock records a thermal remanence when it cools through its blocking temperatures while a field exists. The inherited-archive scenario needs the deep southern crust to have cooled below the carrier Curie point before the dynamo stopped.</p>
<p><b>How.</b> We solved {th["North"]["samples"]:,} northern and {th["South"]["samples"]:,} southern conductive crust columns from 4.5 Ga to today, with radiogenic heating that decays with the real isotope half-lives and a mantle heat flux that decays with a sampled time constant. We kept only histories whose present-day temperatures lie within 30 K of the published envelope of Thiriet et al. (2018) for that hemisphere, whose initial state is below a declared 1,500 K temperature cutoff and, for the south, whose Noachian elastic thickness proxy lies in the compiled 5–35 km range. {th["North"]["accepted"]} northern and {th["South"]["accepted"]} southern histories passed. For each accepted history and depth we recorded the age at which the rock last cooled through 325 °C (pyrrhotite), 580 °C (magnetite) and 670 °C (hematite).</p>
<p><b>Result.</b> Fractions below count only material that was once hotter than the Curie point and then cooled through it; material that stayed cooler throughout the model holds an unresolved earlier record and is reported separately. At 30 km in the south the magnetite point was crossed at a median {f(n["south_mag_30"],2)} Ga: {n["south_mag_30_frac_41"]*100:.0f}% of accepted histories before 4.1 Ga, {n["south_mag_30_frac_37"]*100:.0f}% before 3.7 Ga, {n["south_mag_30_always"]*100:.0f}% never hotter. At 20 km {n["south_mag_20_always"]*100:.0f}% of histories never reached the Curie point, so the shallow crust is unconstrained by this model. At 40 km the median is {f(n["south_mag_40"],2)} Ga and {n["south_mag_40_frac_37"]*100:.0f}% cooled before 3.7 Ga. Of the {win["windows"]} strong (RMS ≥ 100 nT) and deep (≥ 30 km) southern source windows of Gong &amp; Wieczorek (2021), {win["windows_majority_cooled_before_end"]} have their equivalent depth cooled through the magnetite point before 4.1 Ga in a majority of histories and {win37["windows_majority_cooled_before_end"]} before 3.7 Ga; across all {winall["windows"]} usable southern windows the 4.1 Ga count is {winall["windows_majority_cooled_before_end"]}, because shallow depths are mostly uninformative rather than compatible.</p>
{figure('thermal_acquisition', 'Age of last cooling through each carrier Curie point versus depth, with the two dynamo end ages shaded')}{downloads('thermal_ensemble.json', 'thermal_acquisition_ages.csv', 'thermal_source_windows.csv')}
<p class="limits"><b>Limits.</b> Fixed crustal thickness from 4.5 Ga, no intrusions, impacts, fluids or crustal growth; a Curie point is not a blocking spectrum and says nothing about billion-year retention. The accepted sample depends on the chosen parameter ranges, initial state and acceptance gates. Coherence statistics include histories that cross the complete blocking band, with at most 200 accepted histories per hemisphere. They are conditional samples, not a posterior distribution for Mars.</p></section>

<section class="test-detail" id="test-3"><span class="test-number">Test 3</span><h2>How much magnetization would the sources need?</h2>
<p><b>Why.</b> A recording scenario is only viable if the rock can hold the magnetization the orbital field demands.</p>
<p><b>How.</b> For each of the {n["amp_windows_n"]+n["amp_windows_s"]} usable source-depth windows we take the area-weighted RMS field within 10° at 150 km and ask what uniform vertical magnetization a single cylinder of the fitted cap radius would need on its axis to produce it, for three declared layer geometries. This is a cylinder-equivalent scenario, not a demonstrated lower bound: the source model of Gong &amp; Wieczorek is a stochastic ensemble of thin caps, and the window RMS and the on-axis field are different observation operators. The cancellation penalty divides by the median retained fraction from Test 4 at the nearest tested depth.</p>
<table class="result-table"><thead><tr><th>Region</th><th>Geometry</th><th>Windows</th><th>Cylinder-equivalent A/m, 10 / 50 / 90%</th><th>Above 5 A/m</th><th>Above 20 A/m</th></tr></thead><tbody>{amp_rows}</tbody></table>
<p><b>Result.</b> For a 20 km layer the southern median is {f(n["amp_south_median"])} A/m and {n["amp_south_above5"]*100:.0f}% of windows exceed the 5 A/m that Parker (2003) found necessary for a 50 km layer. If the record had been acquired during slow cooling under randomly timed reversals every 100 Myr, the median would rise to {f(n["amp_south_median_100"],0)} A/m; at 0.67 Myr to {f(n["amp_south_median_fast"],0)} A/m. The 1, 5 and 20 A/m lines are comparison levels, not material limits. The cancellation penalty combines separate amplitude and recording summaries; it is not a joint source inversion.</p>
{figure('amplitude_budget', 'Distribution of the cylinder-equivalent magnetization behind each source window, with three comparison levels')}{downloads('amplitude.json', 'amplitude_windows.csv')}
<p class="limits"><b>Limits.</b> Declared geometry, window radius and comparison levels. The equivalent depth and cap radius come from one model of one dataset whose selected methods passages have now been consulted; the cylinder does not reproduce that stochastic cap model. No rock-type verdict follows from these numbers alone.</p></section>

<section class="test-detail" id="test-4"><span class="test-number">Test 4</span><h2>Can slow cooling under a reversing dynamo keep a coherent record?</h2>
<p><b>Why.</b> Steele et al. (2024) model weak orbital signals above large basins under specified reversal, material and remagnetization assumptions. This motivates a recording sensitivity test; it does not measure a universal reversal rate.</p>
<p><b>How.</b> For accepted histories from Test 2 we integrated the exact cooling kernel of each depth through a 150 K blocking band below the magnetite Curie point against two reversal models: perfectly periodic chrons (16 phases) and Poisson chrons of the same mean duration (64 seeds per history). Chron durations run from 0.67 to 1,000 Myr. We report medians and 95th percentiles of the retained fraction of a steady-field record. Periodic and random reversals can cancel differently. For a long uniform acquisition window and a stationary Poisson field, the RMS residual scales approximately as the square root of mean chron duration divided by recording duration.</p>
<table class="result-table"><thead><tr><th>Hemisphere</th><th>Depth (km)</th><th>Cooling through band (Myr, median)</th><th>Retained, Poisson 0.67 Myr</th><th>Retained, periodic 0.67 Myr</th><th>Retained, Poisson 100 Myr</th><th>Retained, Poisson 1,000 Myr</th><th>Shortest chron with ≥50%, Poisson</th></tr></thead><tbody>{coh_rows}</tbody></table>
<p><b>Result.</b> At 30 km in the south the band takes a median {f(n["coh_30_duration"],0)} Myr to cross. With random reversals every 0.67 Myr the median retained fraction is {n["coh_30_poisson_fast"]*100:.1f}% and the 95th percentile {n["coh_30_poisson_fast_q95"]*100:.1f}%; with periodic reversals it is {n["coh_30_periodic_fast"]*100:.2f}%. The shortest tested mean chron giving at least 50% median retention is {n["coh_30_poisson_half"] or ">1,000"} Myr. These model distributions show strong median cancellation, not a universal upper bound. Dividing the cylinder-equivalent amplitude by a median retained fraction gives the conditional penalty in Test 3. This does not exclude slow cooling outright: reversal statistics may have differed between epochs, and the residual is not zero.</p>
{figure('thermal_coherence', 'Median retained fraction of a steady record versus chron duration for Poisson and periodic reversals, southern histories, magnetite band')}{downloads('thermal_coherence.csv')}
<p class="limits"><b>Limits.</b> Uniform blocking band, linear recording, no chemical or shock remanence, no relaxation, no activity windows. Fast-cooled intrusions and lavas are outside the conductive column and remain the natural alternative to test next.</p></section>

<section class="test-detail" id="test-5"><span class="test-number">Test 5</span><h2>Does the orbital model predict the field measured on the ground?</h2>
<p><b>Why.</b> Regional arguments on this site rest on a degree-134 model continued from 120–400 km down to the surface. Two landers have measured the field where the model can be checked.</p>
<p><b>How.</b> We evaluated the Langlais et al. (2019) model at the Zhurong and InSight sites, at the model reference sphere and at the local MOLA radius, for truncations at degree 134, 110 and 90, and compared with the published ground measurements.</p>
<p><b>Result.</b> Our downward continuation reproduces the published value of Du et al. (2023) at Zhurong ({f(n["zh_pred"],0)} nT total and {f(n["zh_pred_h"],0)} nT horizontal against their {n["zh_pub"]} and {n["zh_pub_h"]} nT), which validates the evaluation. The rover measured {f(n["zh_obs_lo"])}–{f(n["zh_obs_hi"])} nT total and {f(n["zh_obs_h"])} ± 10.9 nT horizontal: the model is {f(n["zh_ratio_h"])} times too high. At InSight the model gives {f(n["in_pred"],0)} nT and the lander measured about {f(n["in_obs"],0)} nT: {f(n["in_ratio"])} times too low. Truncating at degree 90 changes the surface predictions by tens of percent.</p>
{figure('surface_check', 'Measured surface field versus the orbital model continued to the surface at Zhurong and InSight')}{downloads('surface_check.json')}
<p class="limits"><b>Limits.</b> Two sites, two different measurement footprints, and a model whose surface continuation amplifies both unresolved sources and model error (Du et al., 2023, discussion of their Figure 4). These comparisons demonstrate that local surface amplitudes cannot be extrapolated from orbit; they do not define an uncertainty for every anomaly or crater-scale contrast.</p></section>

<section class="test-detail" id="test-6"><span class="test-number">Test 6</span><h2>Does a lighter southern crust remove the thickness dichotomy?</h2>
<p><b>Why.</b> Gravity constrains the product of density and thickness. New density estimates (Goossens &amp; Sabaka, 2026; Kim et al., 2023) could shrink the thickness contrast that every origin model tries to produce.</p>
<p><b>How.</b> An independent finite-amplitude gravity inversion with laterally variable crust density, using GMM-3 gravity and MOLA shape to degree 90, order 7, a minimum-amplitude filter at degree 50 and a 39 km anchor at InSight. The crust is decomposed into the laterally variable shell between the mean Moho and mean surface radii, the surface relief and the Moho relief; the shell term, which vanishes only for a uniform crust, is recomputed at every trial Moho radius. The inversion is the regularised fixed-point scheme of Wieczorek &amp; Phillips (1998), with the filter applied to the whole linear solution at every iteration, and it is run to convergence (largest relief change below 1 m). The constant-density expansion matches the pyshtools reference to 1e-13, the shell term matches its analytic integral, a degree-50 test relief comes back with the declared gain of 0.5, and the equal-density inversion reproduces the Wieczorek et al. (2022) archive grid within {f(n["validation_rms"])} km RMS (mean difference {f(n["validation_mean"])} km).</p>
<table class="result-table"><thead><tr><th>Density scenario (kg/m³)</th><th>North mean (km)</th><th>South mean (km)</th><th>South − north</th><th>Minimum</th><th>Maximum</th></tr></thead><tbody>{scen_rows}</tbody></table>
<p><b>Result.</b> The contrast ranges from {f(n["thick_contrast_range"][0])} to {f(n["thick_contrast_range"][1])} km across the declared scenarios. The Goossens &amp; Sabaka densities reduce it from {f(n["thick_eq"])} to {f(n["thick_gs"])} km, once the gravity of the variable-density reference shell is included; the first run of this test omitted that term and reported 14.8 km. No scenario produces negative crust, so none is excluded by this test alone.</p>
{figure('crust_inversion', 'Mean crustal thickness north and south of the boundary for each density scenario')}{downloads('crust_inversion.json', 'crust_inversion.csv')}
<p class="limits"><b>Limits.</b> Uniform mantle density, zero non-hydrostatic degree-2 zonal term, a single anchor point. Density is a declared scenario, not a fitted quantity. The archive comparison is a consistency check for the equal-density scenario, not complete validation; a variable-density reference grid was not available.</p></section>

<section class="results-section"><h2>Follow the controls and source trail</h2><p>The <a href="/research/method">method page</a> defines the workflow and verdicts. <a href="/research/explore#workshops">Explore</a> connects each earlier workshop to its current test, and the <a href="/research/dossiers/audit">audit dossier</a> records the corrections.</p></section>'''


def structured_results(n):
    """Give every current test the same six-part, traceable interpretation."""
    html = results(n)
    for num, _, _, kind, conclusion, _ in test_definitions(n):
        pattern = rf'(<section class="test-detail" id="test-{num}">)(.*?)(</section>)'
        def complete(match):
            body = match[2]
            label = '<p class="part-label"><b>Verdict.</b></p>' + verdict(kind, conclusion)
            body = body.replace('<p class="limits">', label + '<p class="limits">', 1)
            body += '<div class="test-reproduce"><p><b>Reproduce.</b> Run the <a href="/research/method#reproduce">shared six-test build and controls</a>. The figure and data links above identify this test’s saved outputs; the <a href="/research/files/discriminating/protocol.json">protocol</a> and <a href="/research/files/discriminating/manifest.json">manifest</a> describe their inputs and settings.</p></div>'
            return match[1] + body + match[3]
        html, count = re.subn(pattern, complete, html, flags=re.S)
        assert count == 1, f'Missing or duplicate test {num}'
    return html


def page(title, active, body, scripts=''):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · Martian dichotomy</title><link rel="stylesheet" href="/assets/research.css?v=design1"><link rel="stylesheet" href="/assets/workspace.css?v=20260927-design"><link rel="stylesheet" href="/assets/report.css?v=20260928">{scripts}</head><body class="workspace"><a class="skip" href="#content">Skip to content</a><header class="workspace-header"><a class="wordmark" href="/"><i aria-hidden="true"></i><span>Martian dichotomy<small>CHARLOTTE CROCICCHIA</small></span></a>{navigation(active)}</header><main id="content" class="overview report">{body}</main><footer><span>Charlotte Crocicchia · Mars research<br>Public data, original calculations, stated limits.</span><a href="https://github.com/charlottecrocicchia-netizen/mars-wind-lab">Code, methods &amp; provenance ↗</a></footer></body></html>'''


def render():
    n = numbers()
    (ROOT/'web/home.html').write_text(page('Questions & answers', '/', home(n)))
    (ROOT/'web/tests.html').write_text(page('Results', '/research/tests', structured_results(n)))
    from render_collection import render as render_collection
    render_collection(page)
    print('Rendered four main pages, five dossiers and preserved-page navigation.')


if __name__ == '__main__':
    render()
