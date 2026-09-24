# Scientific method and interpretation

Mars Wind Lab is an analysis interface to the official Mars Climate Database 6.1 sampler. It does not solve a new general circulation model. This document distinguishes implemented diagnostics from scientific questions that remain open.

## Sampling the atmospheric state

The adapter calls `CALL_MCD` with scenario 1 (climatology / average EUV), `hireskey=0`, `perturkey=1`, `datekey=1` and `zkey=2` for geometric altitude above the areoid. Lower and upper atmospheric fields are combined by the official routine. Code 17 (below surface) becomes a missing sample; other errors stop the calculation. Winds, thermodynamic fields and RMS variability are sampled together.

Raw NetCDF pseudo-altitude must not be treated as physical height. EOF files encode variability and cannot substitute for absolute fields. A denser query grid does not increase the physical resolution of the underlying GCM. Interpolation smooths extrema and gradients; results should not be described as exact atmospheric maxima.

Two time conventions are explicit: the same local true solar hour at each longitude, or a simultaneous field referenced to the true solar hour at 0° E. Guided column experiments always use the first convention at one fixed location.

## Implemented diagnostics

Horizontal speed is `sqrt(u² + v²)`. The vertical shear magnitude is `sqrt((du/dz)² + (dv/dz)²)`, with derivatives in SI units. Maps use a centred ±1 km difference; profiles use their own geometric grid. Spherical area weights are used for global means, excluding missing samples and renormalizing the remaining area. Atlas arrows have normalized lengths.

Thermodynamic sound speed is `c₀ = sqrt(γRT)`, with MCD values for `γ` and specific gas constant `R`. It does not include frequency-dependent molecular dispersion or relaxation. Effective sound speed is the directional diagnostic `c_eff = c₀ + W_parallel`, where `W_parallel = u sin α + v cos α` and α is clockwise from north. A local profile cannot establish a source–receiver path, arrival time, attenuation or ground detection.

### Direction experiment

Hold the entire thermodynamic column fixed and compare `c₀`, `c₀ + W_parallel`, and `c₀ − W_parallel`. This algebraically isolates advection; it does not recompute a physically wind-free climate. The displayed point maximizes `|W_parallel/c₀|` over the valid query grid. Nonpositive effective speeds in either direction are flagged and must not be interpreted as ordinary travel speeds.

### Seasonal decomposition

At the same geometric altitudes, location, azimuth and local time:

`Δc_eff = (c₀,B − c₀,A) + (W_parallel,B − W_parallel,A)`.

This is an exact decomposition of the diagnostic. The first term includes temperature, composition and heat capacities; it is not a temperature-only contribution. The displayed point maximizes `|Δc_eff|`. It identifies changes in the terms, not their dynamical causes. Opposite signs can partly or completely cancel.

### Reference wavelength and density scale

Define `λ₀ = c₀ T_ref`, where `T_ref` is the period in the resting medium, and `Hρ = |d ln ρ / dz|⁻¹`. The ratio `λ₀/Hρ` examines one local scale-separation consideration. The logarithmic derivative uses the geometric grid and never bridges missing blocks. At least three consecutive valid samples are required.

A ratio near or above 1 is inconsistent with a locally short wave relative to this scale. A small ratio alone is not sufficient to validate ray theory: velocity gradients, flow, turning points and losses also matter. `λ₀` is not a calculated modal vertical wavelength. Reference-period changes are exact linear rescalings of this diagnostic, not full frequency-dependent propagation calculations.

## Experimental modal benchmark

The scalar pressure column solves `−(a p′)′ + k² a p = ω² b p`, with `a=1/ρ`, `b=1/(ρc²)`, `k=sqrt(ℓ(ℓ+1))/R` and `R=3389.5 km`. It uses P1 finite elements, a positive diagonal mass, two rigid boundaries and no gravity. The first-order shift `k <W_parallel>_b` retains only diagonal advection. Nodal weights sum to one.

For uniform flow, `(ω − k·W)² = c²k²` gives `δω = k·W` at first order. An analytic test checks the full shift, avoiding a spurious factor of one half. A grid comparison checks part of the discretization error; it does not validate the rigid 200 km ceiling or omitted physics.

Non-Hermiticity alone proves neither attenuation nor complex eigenvalues. Attenuation requires a defensible operator, inner product, boundary fluxes and dissipation or exchange terms. This benchmark does not infer damping from a uniform wind.

## Optional archived eigenfunctions

The read-only archive reader preserves complex U/V components and duplicate radial samples at discontinuities. The archived model surface is at radius 3383 km; its reference must not be silently replaced by MCD’s areoid. Displayed shapes are normalized individually by their maximum modulus.

Modal integrals depend on whether the vector-harmonic V component is scaled. The reader compares coefficients 2 and ℓ(ℓ+1) to expose sensitivity to that convention; the comparison does not choose the correct convention by itself. Original density scaling is not certified as SI. Only shapes and conditional ratios are reported. An amplitude maximum is not total energy; atmospheric inertia fractions do not predict ground excitation or detectability.

Reconstruct the original solver conventions, frequency catalogue, radial model and derivative units before calculating a global coupling matrix. Preserve complex phase through Fourier and spherical-harmonic projections. Never extend atmospheric winds into the solid or beyond the available domain by constant extrapolation.

## Sources and next validation steps

The [MCD documentation](https://www-mars.lmd.jussieu.fr/mars/info_web/index.html) describes the source model and requested references. [Ortiz et al. (2022)](https://doi.org/10.1029/2021GL096225) provides the Martian wind/acoustic context. The density-scale comparison is an additional local diagnostic implemented here.

Next steps include physically motivated boundaries, gravity and frequency-dependent losses, verified global mode conventions, multiple dust/EUV scenarios, and independent TWINS/SEIS comparisons with instrument responses and quality flags. No SEIS inversion, energy partition or observationally validated arrival prediction is provided in this version.

## Animation semantics

A seasonal sequence varies only solar longitude; an altitude sequence varies only geometric height. All other atmospheric query parameters are held fixed. Every frame is independently sampled through the same official MCD adapter as a standalone map. No interpolation is added between frames. A seasonal sequence has 24 frames at 15° intervals; an altitude sequence has 20 frames at 10 km intervals.

One colour range is computed over all finite values of the selected field across the entire sequence. Signed fields use symmetric bounds; nonnegative speed/shear fields start at zero. Missing values remain missing. This prevents independent frame scaling from creating apparent variability. The 5° spatial sampling and MCD interpolation limits still apply.

Playback speed is chosen for presentation. Solar longitude is an orbital angle, not a uniform time coordinate; advancing in altitude is a spatial sweep. Neither animation is a parcel trajectory or a forecast. MP4 renders the same sampled fields and shared scale on a flat map with explicit metadata.
