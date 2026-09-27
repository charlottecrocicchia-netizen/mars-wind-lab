<div align="center">

# Martian Dichotomy

### One planet. Two different histories?

**Interactive maps, original experiments and a traceable research notebook.**

A personal research project by **Charlotte Crocicchia** · Mars Wind Lab

[![Scientific checks](https://github.com/charlottecrocicchia-netizen/mars-wind-lab/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/charlottecrocicchia-netizen/mars-wind-lab/actions/workflows/tests.yml)
[![Python 3.11+](docs/images/python-version.svg)](pyproject.toml)
[![Code license: MIT](docs/images/code-license.svg)](LICENSE)

[Explore the project](#explore-the-project) · [Research results](#what-the-tests-show) · [Run locally](#run-locally) · [Methods & sources](#methods--sources)

</div>

![The research website: a blue Mars globe, proposed meteorite sources and the question “One planet. Two different histories?”](docs/images/site-overview.png)

Mars has low northern plains and high southern terrain. How did that contrast form, and what can rocks, crustal structure and magnetic records tell us about its history?

This workspace brings the evidence together so you can **explore a place, inspect a measurement, compare an explanation and follow a calculation**. Observations, published interpretations and our own experiments remain clearly identified. The origin of the dichotomy is still an open question.

## Explore the project

| On the website | What you can do | Read on GitHub |
| --- | --- | --- |
| **Overview** | Start with the question and the latest computed results. | [Research guide](research/README.md) |
| **Atlas** | Compare relief, crust, magnetism and geology; follow meteorites to their proposed source craters. | [Data guide & provenance](research/data/README.md) |
| **Results** | Explore experiments, regional comparisons and downloadable outputs. | [Executed experiments](research/EXECUTED_EXPERIMENTS.md) |
| **Hypotheses** | Compare four origin families and distinguish formation, alteration, magnetization and ejection ages. | [Comparison & chronology](research/COMPARISON.md) |
| **Sources** | Search the literature and inspect reading notes, methods and source links. | [Search & reading method](research/METHOD.md) |

### From a meteorite to a place on Mars

![The meteorite atlas with Karratha selected, showing proposed source craters, the dichotomy boundary and a linked interpretation panel](docs/images/meteorite-atlas.png)

**94 sample records · 10 ejection groups · 16 candidate craters.** Select a sample or crater to follow its published source proposals. Mapped locations are candidates, not confirmed origins; shared ejection groups do not represent independent samples of Mars. [Data and references](research/data/meteorites.json)

*Both images are captures of the working website. [Visual credits](docs/ASSETS.md)*

## What the tests show

Our completed calculations currently establish methodological limits, rather than a unique explanation for the dichotomy:

- **A good local prediction can fail elsewhere.** Map-prediction performance changes when whole regions are held out instead of scattered cells.
- **Different magnetic histories can leave the same record.** A synthetic reheating experiment illustrates how rock recording can erase distinctions between field histories.
- **A clean laboratory fit can be misleading.** A contaminated control can produce tightly aligned demagnetization segments; fit quality alone cannot establish ancient remanence.

Each result links its assumptions, numerical checks and outputs in the [experiment report](research/EXECUTED_EXPERIMENTS.md). Explore the [regional study](research/PILOT_STUDY.md), [thermal experiment](research/THERMAL_EXPERIMENT.md) and [planned dynamo tests](research/DYNAMO_TESTS.md) for the next questions.

## Run locally

Requires **Python 3.11+** and Git. The repository includes the research snapshot needed to browse the site; no raw scientific archive download is needed.

```bash
git clone https://github.com/charlottecrocicchia-netizen/mars-wind-lab.git
cd mars-wind-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m uvicorn marswind.server:app --app-dir src --host 127.0.0.1 --port 8765
```

Open **[localhost:8765](http://127.0.0.1:8765/)**. On an already configured Mac, double-click `Launch Mars Wind.command` to start the same site. On Windows, replace the activation command with `.venv\Scripts\Activate.ps1` in PowerShell.

The website runs on your computer. GitHub hosts the code, notes and saved outputs; GitHub Actions runs the scientific and browser-data checks.

## Methods & sources

The site, research notes and repository documentation are in English. Calculations are independently implemented from published methods and permitted inputs, with analytic benchmarks and sensitivity checks where applicable.

- [Research plan](research/RESEARCH_PLAN.md) and [critical literature review](research/DICHOTOMY_REVIEW.md)
- [Source policy](docs/SOURCE_POLICY.md), [dataset manifest](research/data/manifest.json) and [regional-study provenance](research/pilot/sources.json)
- [Development, reproduction & checks](docs/DEVELOPMENT.md)

The active literature selection contains **1,823 records**, including **76 core references** and **70 consulted beyond metadata**. These counts describe the current selection, not an exhaustive review. Research notes prepared with AI assistance record reading depth and uncertainty.

## Credits & license

Created by **Charlotte Crocicchia**. Original code is released under the [MIT license](LICENSE). External datasets and visual assets retain their own attribution and terms; see the [data guide](research/data/README.md), [visual credits](docs/ASSETS.md) and [Plotly license](web/PLOTLY-LICENSE.txt).

This is an independent personal research project, with no institutional endorsement.
