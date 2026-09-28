# Using the research website

[Install and start the server](../README.md#run-the-website), then open [localhost:8765](http://127.0.0.1:8765/). The four navigation links stay in the same order throughout the site.

| Section | Use it to… |
| --- | --- |
| **Questions & answers** | Read the main question, the latest synthesis and six result summaries |
| **How we work** | Follow inputs, protocol, calculation, checks and verdicts; inspect follow-up execution status |
| **Results** | Read each test's Why, How, Result, Verdict, Limits and Reproduce sections |
| **Explore** | Reach the atlas, source catalogue, workshops, five reading dossiers and dated archives |

## Three useful routes

**Understand a result.** Start with “Where the evidence stands,” open the linked technical report, then inspect its table, figure or manifest. A verdict applies to the named comparison and assumptions, not the whole origin of Mars's dichotomy.

**Explore a place or sample.** Open Explore → Atlas. Change the map layer, select a candidate crater or search a meteorite. Keep source proposals and measured locations distinct. A source depth is a model-dependent equivalent depth; a surface epoch does not automatically date magnetic acquisition.

**Trace a claim.** Open the source catalogue or a reading dossier. Reading-depth labels distinguish metadata, abstracts and selected sections. Follow the original DOI or dataset attribution. The literature collection is selective, not an exhaustive systematic review.

## Controls and downloads

Maps and tables keep their own altitude, layer, region and filtering controls. On small screens, wide tables scroll within their frame. The scenario comparison and event chronology remain available through Explore; different event ages and uncertain source locations retain their labels.

Comparison CSV exports contain the complete curated tables, independent of display filters. The catalogue's RIS export follows the active library filters. Notes can be downloaded as Markdown. Scientific outputs show the saved run; opening a report does not start a calculation.

## Current pages and archives

Current reports are labeled “Current technical reference.” Earlier workshops, the regional pilot and background notes remain accessible with archive context. Use the current synthesis and audit for corrected interpretations, especially cooling durations, density scenarios and reversal statistics.

## Local operation

The browser connects to the server running in your terminal. Keep that terminal open; Ctrl+C stops it. If port 8765 is occupied, either use the existing site or start with `--port 8766` and open the corresponding address. Restart the server after Python server-code changes. Refresh the page after regenerating saved HTML.

GitHub is the code and documentation host. The localhost links work only while the application is running on your computer. No MCD installation is needed to browse the current website.
