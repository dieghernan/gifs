# Project structured data

This layer generates only the project's Dataset JSON-LD. It does not replace
or modify Chulapa's structured data or the existing author normalization plugin.

`_data/structured_data.json` holds the dataset description, source, creators,
reuse terms, keywords and CSV distribution. Publication dates are separate
from the temporal coverage of the fire records. They come from the CSV's Git
history; there is no numbered dataset release.

`dataset.html`, `release.html` and `distribution.html` generate the JSON-LD.
The distribution shares the dataset's modification date. Review it when the
CSV changes; do not use the website build date.

Build with `bundle exec jekyll build`, then run
`py -m unittest discover -s tests` to verify the rendered metadata against the CSV.
