# Project structured data

This layer generates only the project's Dataset JSON-LD. It does not replace
or modify Chulapa's structured data or the existing author normalization plugin.

`_data/structured_data.json` holds the dataset description, source, creators,
reuse terms, keywords and CSV distribution. Publication dates are separate
from the temporal coverage of the fire records. They come from the CSV's Git
history. Version 1.0.0 is archived in Zenodo; the concept DOI in
`structured_data.json` identifies all versions.

As in codigospostales and celestial_data, the public page embeds the generated
Croissant Dataset instead of constructing a second independent JSON-LD object.
Chulapa continues to generate its own page and author metadata.

`CITATION.cff` is the source for the version DOI, release date and citation.
Run `ruby scripts/citation.rb` to generate the citation sections in README and
index and `_data/citation.json`. The download card reads that same JSON;
`build_croissant.py` uses it for `version`, `identifier`, `sameAs` and `citeAs`.
Run the citation generator before regenerating Croissant. Both generators
support `--check`, and CI checks both outputs before publication.

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
