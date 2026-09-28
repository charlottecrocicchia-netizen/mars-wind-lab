# Where the evidence stands

**Synthesis · 28 September 2026 · six declared tests and six follow-ups, reviewed internally with AI assistance.** This page separates observations, conditional calculations and unresolved questions. The review is not external peer review. Linked reports contain the numerical outputs, assumptions and reproduction commands.

## The question

The southern highlands carry stronger crustal magnetic anomalies than the northern lowlands. A difference in the ancient field, a difference in recording and preservation, or a combination can contribute. Surface age, magnetic acquisition age, source depth and crustal density measure different properties. Connecting them requires a model; none can stand in for the others without testing that connection.

## Established within the stated comparisons

- **The orbital magnetic contrast persists across the tested boundaries.** The south-to-north field ratio at 150 km is about 3.8 for the main definition and 3.1–4.5 across the tested definitions. This describes the resolved orbital field, not an ancient dynamo-intensity ratio. ([First diagnostics](FIRST_RESULTS.md))
- **The calculated thickness contrast keeps its sign but changes substantially with density.** The south-minus-north contrast is 24.1 km at equal density and 8.4 km with the Goossens–Sabaka scenario; the declared range is 6.6–41.4 km. Agreement within 4.3 km RMS with the reference archive checks consistency, not independent geological accuracy. ([Test 6](DISCRIMINATING_TESTS.md))
- **The two ground comparisons expose a local extrapolation limit.** Continuing the orbital model to the surface overpredicts the checked Zhurong field and underpredicts InSight. These two sites do not define a universal correction factor or invalidate every regional orbital comparison. ([Test 5](DISCRIMINATING_TESTS.md))

## Conditional physical constraints

- **Slow acquisition can strongly cancel a reversing field.** At 30 km in the accepted southern thermal histories, the median magnetite-band crossing duration is 774 Myr. Poisson reversals with a 0.67 Myr mean chron leave 2.1% median retention, with a 6.3% 95th percentile. These are distributions over declared histories, not universal limits or probabilities for Mars. ([Test 4](DISCRIMINATING_TESTS.md))
- **Rapid cooling protects individual bodies in the slab scenario.** A 3 km body in a 300 °C host crosses the mid-plane blocking band in **0.853 Myr** and retains 76% at the simulated median. This exceeds one 0.67 Myr mean chron; cooling within a single chron is not a necessary condition for that median result. The tabulated thickness limits are the largest passing **tested** sizes, not continuous upper bounds. ([Rapidly cooled bodies](RAPID_BODIES.md))
- **Stack polarities remain correlated through the shared field.** For 100 equal instantaneous recorders and a 0.67 Myr mean chron, a 10 Myr emplacement span gives median coherence 0.20 and RMS 0.27; 100 Myr gives 0.08 and 0.13. The familiar 1/√N RMS limit needs a span long compared with N times the mean chron. Neither these stacks nor the single-body calculation is a coupled orbital-field inversion. ([Rapidly cooled bodies](RAPID_BODIES.md))
- **Early deep acquisition depends on the thermal and mineral assumptions.** At 30 km, 39% of accepted southern histories cross the magnetite Curie point before 4.1 Ga and 59% before 3.7 Ga; 21% begin below it, leaving an earlier record unresolved. The pyrrhotite result at tested depths must not become a universal carrier cutoff. ([Test 2](DISCRIMINATING_TESTS.md))
- **Density constrains a material balance, but does not determine it.** For a 2,900 kg/m³ matrix, empty pores and efficient single-domain magnetite, the 4.2 A/m coherent southern cylinder target needs about 0.05–0.10% magnetite by solid volume and 14% porosity. The already cancellation-corrected 208 A/m target needs 2.47–5.03% and about 16–17% porosity. Other efficiencies, matrix densities and pore limits can exclude combinations. These are conditional balances; neither deep pore survival nor actual mineral abundance is established. ([Density and remanence](DENSITY_REMANENCE.md))

## What the present comparisons do not resolve

**An age-controlled discontinuity at the dichotomy boundary.** Arabia matching fails its declared support and balance checks. Boundary transects, evaluated directly against the geological polygons and magnetic coefficients, retain too few adequately covered blocks; the common comparison with both shifted controls retains none. This is a limit of the declared designs and inputs, not proof that all public geology is exhausted. Fourteen of the 23 northern Early Noachian cells belong to Xanthe–Chryse, so their aggregate is not a geographically representative northern sample. ([Arabia preflight](ARABIA_PREFLIGHT.md), [Boundary transects](BOUNDARY_WALK.md))

**A supported source-depth relationship with surface age.** The primary northern rank correlation is +0.21 (block interval −0.03 to +0.40; 107 windows), and the southern one −0.12 (−0.27 to +0.09; 188 windows). Neither passes the declared support rule. The northern sign opposes the simple resurfacing prediction, but this does not select excavation: the oldest northern bin contains only one window, and uncertainty-endpoint shifts are sensitivity cases rather than a joint posterior. ([Depth and age](DEPTH_AGE.md))

**A reversal chronology from magnetic coherence alone.** In the declared flexible recording class, a changing reversal rate and a constant rate with transformed acquisition times produce identical synthetic source moments and fields at 150 and 400 km. The maximum relative map difference over 128 realizations is 1.8 × 10⁻¹³. Independently known acquisition times remove this particular ambiguity in an ideal positive control; they are not supplied by the orbital maps. This fails the gate to observed-map inference in that class, not every possible physically restricted inversion. No transition date has been inferred. ([Reversal identifiability](REVERSAL_IDENTIFIABILITY.md))

## What this leaves

Recording and preservation remain plausible contributors. Strong sources constrain combinations of carrier efficiency, acquisition duration, source geometry, emplacement history and reversal statistics. The calculations do not force construction within one chron, do not establish a change in reversal rate, and do not exclude a hemispheric difference in the ancient field. The next useful advance would restrict one of these freedoms with independent evidence and then repeat a declared recovery test.

## Measurements that would reduce the ambiguity

1. **Local magnetic surveys on old northern terrains, with matched southern comparisons and geological context.** These could separate unresolved local sources from the large-scale orbital contrast. One point measurement alone would not decide a hemispheric question.
2. **Southern seismology combined with gravity, composition and pore constraints.** This would reduce the density–thickness ambiguity; seismic velocity alone is not a direct unique density measurement.
3. **Dated, oriented samples that constrain acquisition times and polarity sequences.** These could distinguish reversal frequency from recording duration, subject to age uncertainty, remagnetization and sampling gaps.
4. **Carrier, grain-state and cooling-history measurements tied to a mapped anomaly.** These would connect the material budget and thermal scenarios to an actual source, particularly when paired with source geometry constraints.

## Follow the evidence

The [six tests](DISCRIMINATING_TESTS.md) are the numerical core. The [audit dossier](dossiers/audit.md) links corrections and follow-ups. The [method page](../docs/SCIENTIFIC_METHOD.md) distinguishes executed calculations from unexecuted stages. The earlier synthesis and body outputs are preserved in the [body-audit archive index](followup/bodies_audit/before_hashes.json); the current pages correct the cooling-duration label, correlated-stack interpretation and claims that observations could uniquely settle the origin question. Earlier literature notes remain dated background.
