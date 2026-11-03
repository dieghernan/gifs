# Project structured data

This layer generates only the project's Dataset JSON-LD. It does not replace
or modify Chulapa's structured data or the existing author normalization plugin.

`_data/structured_data.json` holds the dataset description, source, creators,
reuse terms, keywords and CSV distribution. Publication dates are separate
from the temporal coverage of the fire records. They come from the CSV's Git
history; there is no numbered dataset release.

`dataset.html` embeds the generated Croissant Dataset JSON-LD. The older
`release.html` and `distribution.html` partials are not used by that descriptor.
The distribution shares the dataset's modification date. Review it when the
CSV changes; do not use the website build date.

`measurementTechnique` describes collection and processing. `subjectOf`
links to `METODOLOGIA.md`, and `isBasedOn.hasPart` lists the annual MITECO
sources. The description and field metadata retain the conventional 2012
dates and the provisional status of the recent annual sources.

Build with `bundle exec jekyll build`, then run
`py -m unittest discover -s tests` to verify the rendered metadata against the CSV.

## Croissant

The public Dataset now embeds the generated `_data/croissant.json`, also
served as `/croissant.json`. See `scripts/README-croissant.md` for generation,
validation, immutable source URLs and the official-reader integration test.
