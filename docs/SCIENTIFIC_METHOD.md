# Scientific method and interpretation

The active project asks which histories can explain the Martian crustal magnetic contrast while respecting geology, thermal evolution and crustal structure. It connects evidence across disciplines without treating different measurements as interchangeable clocks.

Start with [Where the evidence stands](../research/STATE_OF_EVIDENCE.md), then the [six-test report](../research/DISCRIMINATING_TESTS.md). This guide explains how to read their claims.

## What each layer tells us

| Layer | Observation or model product | What it does not supply by itself |
| --- | --- | --- |
| Orbital magnetism | A spatially filtered field at a stated altitude and model resolution | Unique source direction, mineralogy or ancient field intensity |
| Surface geology | Mapped units and relative surface epochs | The acquisition age of a buried magnetic source |
| Gravity and topography | Constraints on mass distribution and surface shape | Crustal thickness independent of density assumptions |
| Thermal calculations | Cooling and acquisition under specified geometry, heating and boundary conditions | A uniquely reconstructed crustal history |
| Rock magnetism | Carrier, grain and recording properties of studied material | Representative properties of an entire hemisphere |
| Meteorite chronology | Formation, alteration, shock or ejection events with distinct clocks | A confirmed source location or a complete global reversal sequence |

A **remanence** is a magnetic record retained by rock. A **chron** is an interval of one polarity. A **blocking band** describes the temperatures over which the declared carrier acquires its modeled record. **Identifiability** asks whether distinct model histories can be distinguished by the specified observations.

## The workflow

1. Record input provenance, reuse terms, units, resolution and missing values.
2. Declare the comparison, scenarios, controls and interpretation rule before evaluation. Repository declarations are not external preregistration.
3. Implement the calculation and save its tables, figures, settings and available input/code/output hashes.
4. Check analytic cases, synthetic recovery, numerical convergence and spatial support. Report failed prerequisites.
5. Write a conclusion at the scope demonstrated. Preserve corrections and distinguish current reports from historical notes.

The [implementation audit](../research/DISCRIMINATING_AUDIT.md) and [follow-up reports](../research/README.md#follow-up-results) document both errors and unresolved assumptions. This is an internal, AI-assisted process, not external scientific certification.

## Reading a verdict

| Verdict | Meaning |
| --- | --- |
| Supports a stated prediction | The specified observation or calculation agrees with that prediction under its assumptions |
| Weakens a scenario | A named scenario fails a declared comparison; identify which assumptions are needed |
| Adds a constraint | The result limits a range or exposes a trade-off without selecting one history |
| Not decisive | Support is insufficient, uncertainties remain, or the alternatives are observationally indistinguishable |

An ensemble percentile describes the declared simulation ensemble. It is not automatically a probability for Mars. Nearby map cells and overlapping source windows are not independent samples. Predictive association is not a causal attribution.

## Why the latest controls matter

The [boundary comparison](../research/BOUNDARY_WALK.md) lacks enough common spatial support for its planned inferential comparison. The [material balance](../research/DENSITY_REMANENCE.md) relates remanence to density only under explicit efficiency, porosity and volume assumptions. The [body model](../research/RAPID_BODIES.md) separates individual cooling from correlations among bodies sharing one reversing field.

The [reversal prerequisite](../research/REVERSAL_IDENTIFIABILITY.md) constructs distinct histories with identical synthetic fields when recording clocks can change. Its ideal known-clock control demonstrates a way to break that particular ambiguity, not a chronology measured for Mars. Failing this gate is a result; fitting the observed map anyway would not supply the missing independent clock.

## Scope and earlier work

The six tests and follow-ups do not form a fully coupled inversion of crustal growth, mineral chemistry, water, impacts, density and dynamo evolution. The [roadmap](ROADMAP.md) lists useful independent constraints and remaining model development.

Earlier atmospheric diagnostics and the scalar acoustic benchmark are described in the preserved [atmospheric method](archive/ATMOSPHERIC_METHOD.md). They are separate from the current website and do not provide a coupled solid-planet/atmosphere solution. Their use remains subject to the [source policy](SOURCE_POLICY.md).
