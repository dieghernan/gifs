# Croissant pilot

The dataset is published as Croissant 1.1 at
<https://dieghernan.github.io/gifs/croissant.json>. The landing page embeds the
same descriptor once, with the existing Dataset identifier. Its CSV resource
has both Croissant FileObject and Schema.org DataDownload types, preserving
its role as a downloadable distribution for existing consumers.

## Sources

- `_data/structured_data.json`: dataset description, creators, source, reuse
  terms, publication dates and the pinned CSV revision/path.
- `_data/croissant_fields.json`: the seven columns, types and descriptions.
- `_data/croissant_context.json`: the JSON-LD context from mlcroissant 1.1.1's
  Croissant 1.1 context, with Spanish as the default language.
- `rdata/gif_d2010.csv`: the existing data, without conversions or edits.

`build_croissant.py` writes `croissant.json` and `_data/croissant.json` from
these sources. The latter is embedded by the existing Dataset include; the
former is served unchanged by GitHub Pages. Do not hand-edit generated files.
The old release/distribution includes remain available but the public Dataset
now comes from the generated Croissant descriptor.

## Generate and verify

Install the pinned validator into a Python 3.12 virtual environment:

```sh
python -m pip install -r scripts/requirements-croissant.txt
python scripts/build_croissant.py
python scripts/build_croissant.py --check
mlcroissant validate --jsonld croissant.json
bundle exec jekyll build
python -m unittest discover -s tests
```

The integration test uses the official library to download the real immutable
CSV, verify its hash and read all 404 records. It compares every code, name,
date and area with the local CSV. Municipality codes are text; dates are dates;
area values are numeric hectares. No record key is asserted because several
fires can share a municipality and date.

```python
import mlcroissant as mlc

dataset = mlc.Dataset("https://dieghernan.github.io/gifs/croissant.json")
records = dataset.records(record_set="fires")
first = next(iter(records))
```

The library can represent text as UTF-8 bytes. Consumers can decode these
values as needed; the descriptor does not coerce identifiers to integers.

## Update data

Commit CSV content changes first, then update `croissant.sourceRevision` to a
commit containing that snapshot, review dates and coverage, and regenerate.
Hashes and sizes use Git blob bytes to avoid Windows newline conversions.
The official reader's integration test confirms that the pinned URL and the
current CSV contain the same records and that the checksum is correct.

No numbered release or formal citation has been invented. The validator may
recommend `version` and `citeAs`; these recommendations do not prevent loading.
The dataset's reuse terms remain the MITECO legal notice, not the code's MIT
license. Existing provisional/final-data and completeness limitations remain.

The workflow checks regeneration, validates Croissant, builds Jekyll and runs
the integration tests before publication. Neither Chulapa's markup nor the
visible landing-page content is replaced.
