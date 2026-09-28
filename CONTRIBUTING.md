# Contributing

Corrections, clearer explanations and reproducible scientific checks are welcome. Start with the [current synthesis](research/STATE_OF_EVIDENCE.md) and [source policy](docs/SOURCE_POLICY.md).

## Report a problem

Include the page or file, the commit you used, the expected result, what happened and a minimal example or reproduction command. For a scientific correction, identify the equation, convention, numerical value or source passage at issue. Distinguish an implementation error from disagreement with a model assumption.

Do not attach credentials, private material, restricted source archives or full articles without redistribution permission.

## Make a change

1. Create a branch from the current `main` and keep the change focused.
2. Edit source Markdown or the relevant builder, then regenerate affected pages. Files under `web/reading/` are generated.
3. For a numerical change, state the question, assumptions and expected check before evaluation. Preserve earlier protocols and audit records; identify corrected runs explicitly.
4. Add or run meaningful analytic or synthetic checks appropriate to the change. Report limitations and any unexecuted full-data build.
5. Describe the resulting behavior, relevant validation and changed interpretation in the pull request.

```bash
python -m pip install -e '.[test,research,observations]'
python -m pytest -q -m 'not integration'
node --test tests/*.test.mjs
python scripts/research/render_site.py
python scripts/research/render_docs.py
```

See [Development](docs/DEVELOPMENT.md) for input requirements. The six-test `--quick` build overwrites the same output directory with reduced sampling; it must not be published as the full report dataset.

## Scientific and editorial conventions

- Keep project-authored documentation, interface labels and reports in English.
- Identify units, spatial support, time conventions, uncertainty and missing values.
- Separate observations, modeled quantities and interpretations. A failed support or recovery gate is a valid result.
- Treat surface age, crystallization, shock, ejection and magnetic acquisition as distinct clocks.
- Keep provenance and source-specific terms with external data. Public visibility is not permission to copy code or redistribute a dataset.
- Preserve historical results with their dates and clearly identify the current conclusion. Do not claim external peer review, novelty or a unique geological explanation without the corresponding evidence.

Original code contributions use the repository's MIT license. External material keeps its own terms. Private internship material and external MCD software are excluded from this repository; historical MCD integration work requires separate authorization.
