# Thermal experiment 01 — A temperature history before a magnetic interpretation

**27 September 2026 · Original controlled numerical experiment · No Martian region fitted.**

[Open the interactive experiment](THERMAL_EXPERIMENT.md) · [Input protocol](thermal/protocol.json) · [Saved results and provenance](thermal/results.json) · [Scientific figure](thermal/thermal_history.png)

This first physical building block follows a solid crustal column through time. It compares progressive cooling with the same history interrupted by an imposed heat pulse. It tests whether a hypothetical old magnetic component would encounter a selected magnetic ordering temperature later. It does **not** calculate its acquisition, duration-dependent relaxation, surviving intensity or orbital signal.

## Question and result

Can a temperature check at the proposed recording time miss a later thermal exclusion? Yes, in the controlled experiment: at 25 km depth, a component introduced at elapsed time 500 Myr is initially below the magnetite endmember's 580 °C ordering temperature. The imposed pulse at 1,000 Myr subsequently exceeds that threshold, whereas the progressive-cooling control does not. The resulting difference comes from the specified heat pulse, not from fitting northern or southern Mars.

The lower panels of the figure show the maximum **future** temperature, classified against the chosen threshold. A “no crossing” window is only compatible with this gate. It is not a survival probability, a measured recording age, or evidence that those rocks actually acquired a remanence. A new component could be acquired after a reset if suitable carriers and a field existed; that process is not simulated here.

## Equation, signs and boundaries

For depth `z` positive downwards, fixed column thickness `L`, constant conductivity `k`, density `rho`, heat capacity `cp`, and uniform volumetric heating `H(t)`:

```text
rho cp dT/dt = k d²T/dz² + H(t)
T(0,t) = Ts
k dT/dz (L,t) = qb(t)       [qb is upward basal heat flux]
```

Basal heat flux is not surface heat flux. At steady state with uniform internal heating, the outward surface flux is `qb + H L`. For constant sources, the exact profile is:

```text
T(z) = Ts + qb z/k + H (L z − z²/2)/k
```

Each scenario starts in this exact steady state for its initial sources. The subsequently decaying sources need not remain in steady equilibrium; the solver follows their transient response.

| Input | Illustrative value or law | Interpretation |
|---|---|---|
| Column thickness | 50 km | Fixed solid column, not inferred source depth |
| Surface temperature | 220 K | Prescribed, fixed boundary |
| Conductivity | 3 W m⁻¹ K⁻¹ | Constant |
| Density | 2,900 kg m⁻³ | Constant |
| Heat capacity | 800 J kg⁻¹ K⁻¹ | Constant; no latent heat |
| Upward basal flux | `15 + 30 exp(−t/1000)` mW m⁻² | `t` in Myr; asymptote is not the exact 4,000 Myr endpoint |
| Volumetric heating | `0.04 × 2^(−t/2000)` µW m⁻³ | Effective decay; not an isotope abundance model |
| Duration | 4,000 Myr | Elapsed model time, not independently dated Martian chronology |
| Pulse | At 1,000 Myr, scale +500 K, centre 25 km, Gaussian width 5 km | Artificial perturbation, not an impact, intrusion or fluid model |

The pulse adds `500 exp(−0.5 ((z−25000)/5000)²) sin²(pi z/L)` kelvin, with metres for distances. The taper leaves the surface temperature and basal derivative unchanged analytically. At the selected midpoint the increment peaks at 500 K; away from the midpoint its amplitude parameter would be a scale rather than the actual peak. The synthetic event's added energy per area is exported, not interpreted as a measured impact energy.

All physical parameters above are declared choices, **not** values estimated from the cited papers. Neither scenario is assigned to a hemisphere, crater or meteorite source. Both share all parameters except the pulse.

## Numerical method and verification

The independent Python implementation uses backward Euler in time, second-order centred differences in depth and a half control volume at the prescribed-flux lower boundary. The fixed-temperature surface node is not evolved. For a depth spacing `dz`, the bottom equation has `2 k (T[N−1]−T[N])/dz² + 2 qb/dz + H`; the factor of two follows from the half cell. This sign and weighting are checked by a discrete energy-balance test. The dynamic-volume check excludes the half cell held at the imposed surface temperature.

The saved baseline uses 100 cells (0.5 km spacing), a 0.125 Myr base step, and 0.015625 Myr steps for 20 Myr after a pulse. Event and final times must lie on the base grid; invalid times are rejected, never rounded. Conduction advances **to** the event using the pre-event state, then the temperature increment is applied. Event-time exports are post-pulse, with the pre-pulse profile retained separately. The surface remains fixed.

Verification includes:

- **Exact steady solution:** the parabolic profile above remains invariant to approximately `1.7e−10 K` in the saved check.
- **Exact transient:** a 100 K perturbation `sin(pi z/(2L))` over an isothermal column, with zero basal flux and heating, decays as `exp(−kappa (pi/(2L))² t)`. After 50 Myr, the saved maximum error is approximately **0.0682 K**. Time refinement shows first-order convergence; separate tests check spatial convergence.
- **Physical invariants:** no artificial heating of that source-free cooling mode; fixed surface; energy balance including the bottom half cell; no heating before an imposed pulse.
- **Full-history refinement:** 200 cells and half both time steps, compared at matching times and depths. Maximum temperature differences are approximately **0.0044 K** for cooling and **1.126 K** with reheating. Future-peak differences are also exported. These are numerical discrepancies, not geological uncertainty intervals.

The builder refuses to publish outputs if the steady error exceeds `1e−7 K`, the exact-transient error exceeds `0.08 K`, or the history-refinement temperature difference exceeds `2 K`. These are computational checks, not evidence-based acceptance criteria for a Mars hypothesis. Threshold boundaries closer than the numerical discrepancy require refinement before interpretation; CSV time decimals report sampled grid points, not age precision.

## Ordering-temperature gate

For a candidate recording time `tr`, compute `Tmax(z,tr) = max T(z,t)` for all integration steps from `tr` to the final time. The candidate time itself is included. Classification is performed before display thinning and before rounding saved temperatures:

| Code | Condition | Permitted reading |
|---|---|---|
| 0 | `Tmax < Torder` | This exclusion does not apply; acquisition and survival remain unresolved |
| 1 | `T(tr) < Torder`, but `Tmax >= Torder` | A subsequent ordering-temperature crossing excludes preservation of the original component in that carrier under this model |
| 2 | `T(tr) >= Torder` | The ordered magnetic carrier is unavailable at that candidate time |

The selected endmembers reuse the project's existing illustrative values: pyrrhotite 598.15 K (325 °C), magnetite 853.15 K (580 °C), and hematite 943.15 K (670 °C, Néel temperature). Composition and grain properties matter; these labels do not identify local minerals, fix blocking spectra or convert equivalent magnetic source depth into a Curie depth.

Remaining below an ordering threshold does not demonstrate billion-year retention. Relaxation depends on temperature, time and grain energy barriers; the published grain-scale calculations illustrate why a single Curie gate cannot supply a stability model ([Nagy et al., 2017](https://doi.org/10.1073/pnas.1708344114)). No constant-barrier toy model is presented as mineral-specific survival here.

## Scientific context and source boundaries

| Primary source | Material consulted for this step | Role and limit |
|---|---|---|
| [Thiriet et al. (2018)](https://doi.org/10.1002/2017JE005431) | Publisher article, thermal-model context | Crustal properties matter to thermal evolution. This fixed conductive column does not reproduce their coupled parameterized mantle/lithosphere model. |
| [Steele et al. (2024)](https://doi.org/10.1038/s41467-024-51092-4) | Publisher abstract; full methods not audited in this step | Cooling and field reversals affect basin magnetism. Their magnetic recording calculation is not reproduced here. |
| [Nagy et al. (2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5625920/) | Selected stability and methods sections in the PMC full text | Grain-scale energy barriers and temperature/time dependence motivate the gate's limitation, not a calibrated carrier model. |

The methods note supplies these references directly; it does not change the larger library's catalog counts or promote these readings to full methodological audits. The solver was written independently from the heat equation and analytic cases. Inputs are synthetic; figures and tables are project-generated. No external code, article figure, full text or new dataset is redistributed. No former internship material or raw archive acquisition is involved.

## Reproduction and outputs

After the repository's base Python installation, run from its root:

```bash
python scripts/thermal/build.py
python -m pytest -q tests/test_thermal.py
python scripts/research/render_docs.py
```

- [Protocol](thermal/protocol.json): equations' parameters, event definitions, conventions, sources and exclusions.
- [Results](thermal/results.json): saved temperature/future-peak grids, classification codes, pulse energy and pre-event profile, numerical checks, runtime versions, protocol/model/builder/test SHA-256 hashes.
- [Profiles](thermal/profiles.csv): temperatures and future peaks at five selected times, in kelvin.
- [Windows](thermal/windows.csv): earliest sampled times after which the threshold is never reached, at five depths. Empty times mean no compatible sample before the endpoint; `0` means compatible from the initial time. Both remain conditional thermal windows.
- [PNG](thermal/thermal_history.png) and [SVG](thermal/thermal_history.svg): original four-panel scientific figure.

The browser reads a saved run; selecting a history or threshold does not fit a new model. Heatmaps display all depth nodes and thinned time samples. Future maxima use every integration step, including the fine post-pulse steps. Contour locations and colored cell boundaries have finite plotting resolution. Plots must not be digitized as precise ages; use the protocol and full solver for further analysis.

## What remains before testing the dichotomy

This is a verified numerical building block of the [joint-model protocol](TEST_PROTOCOL.md), not its completion. It omits crustal growth, lateral transport, variable properties, latent heat, fluid chemistry, shock, mineral growth and relaxation, field reversals and the magnetic forward operator. No regional parameters are inferred and no held-out observations are predicted.

The next step is an independently constrained regional time–temperature ensemble, followed by carrier-specific recording/stability and source geometry. Copernicus and Huygens remain candidates from the [regional pilot](PILOT_STUDY.md), but their weak orbital contrasts do not supply a thermal pulse magnitude or date. A predictive comparison between shared and hemispherically asymmetric fields must wait until those missing pieces are explicit.
