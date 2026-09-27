# Visual assets

## Current research workspace

The blue, slate and teal interface uses original HTML, CSS and SVG graphics. Plotly supplies the interactive charts and retains its own [license](../web/PLOTLY-LICENSE.txt). Chart colors encode the quantities and categories stated in their captions; colors do not rank origin hypotheses.

`web/atlas-preview.svg` is an original orthographic rendering of the authorized 2° MOLA elevation summary in `research/data/atlas.json`, centered at 180° east. Dots use the proposed source-crater coordinates in `research/data/meteorites.json`; they do not locate confirmed launch sites. Only the visible hemisphere is shown. MOLA and meteorite source attribution and terms remain in the [data manifest](../research/data/manifest.json).

Regenerate the globe, overview and results cards with `python scripts/research/render_overview.py`. The three result summaries read the committed experiment JSON files, so the preview is an illustration of saved calculations, not a new inversion or real-time computation. The full methods and outputs remain linked from each card.

The scientific export figures retain their original publication palettes and file checksums. Changing the website theme does not modify numerical outputs or recolor those saved evidence files.

## Retained historical image

`web/images/mars-viking.jpg` is the **Mars Planet Globe** mosaic published by NASA and credited to **NASA/JPL-Caltech**. The current overview uses the data-derived SVG above. The older decorative image remains as an attributed repository asset; it is not a numerical observation layer.

- [Source and credit](https://science.nasa.gov/resource/mars-planet-globe/)
- [NASA media usage guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/)

NASA/JPL-Caltech does not endorse this personal project. The application's MIT license does not relicense the external asset.
