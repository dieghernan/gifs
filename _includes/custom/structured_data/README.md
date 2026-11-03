# Project structured data

This layer generates the project's DataCatalog and its two Dataset descriptions. It does not replace
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
Before Zenodo assigns a version DOI, the citation uses the tagged GitHub
release URL. After archiving, add the DOI to both citation fields in
`CITATION.cff` and regenerate without moving the published tag. The catalog
identifies the archived collection and links the concept DOI through
`isPartOf` as a URL. The child datasets link the catalog through
`includedInDataCatalog` and use the archived collection's DOI URL for
`isPartOf`; they have no separate DOI. Google accepts Dataset or URL values
for `isPartOf`, so the DataCatalog is not used as that property's object.
`spatialCoverage` preserves the place name España and adds a `GeoShape.box`
computed from the available GeoJSON points for each dataset. Its order is
south latitude, west longitude, north latitude, east longitude, as required
by Google's Dataset documentation. The catalog uses the combined extent.
Null geometries are excluded and Canary Islands coordinates remain real.
The box describes available point locations, including municipal fallbacks;
it does not represent burned perimeters or complete territorial coverage.
Run the citation generator before regenerating Croissant. Both generators
support `--check`, and CI checks both outputs before publication.

`dataset.html` embeds `_data/catalog.json`: one DataCatalog containing the
part and fire Datasets. Standalone Croissant descriptors are served at
`/croissant/parts.json` and `/croissant/fires.json`. The global
`/croissant.json` is retained for compatibility. The older
`release.html` and `distribution.html` partials are not used by that descriptor.
The distribution shares the dataset's modification date. Review it when the
CSV changes; do not use the website build date.

`measurementTechnique` describes collection and processing. `subjectOf`
links to `METODOLOGIA.md`, and `isBasedOn.hasPart` lists the annual MITECO
sources. The description and field metadata document EGIF source priority, nullable
coordinates and unresolved matches. The development descriptor includes
part and fire resources in CSV and typed JSON; it does not reuse the
archived release DOI for the development data.

Build with `bundle exec jekyll build`, then run
`py -m unittest discover -s tests` to verify the rendered metadata against the CSV.

## Croissant

The public Dataset now embeds the generated `_data/croissant.json`, also
served as `/croissant.json`. See `scripts/README-croissant.md` for generation,
validation, immutable source URLs and the official-reader integration test.
