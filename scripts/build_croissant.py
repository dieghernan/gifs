"""Build reproducible Croissant metadata from the project metadata and CSV."""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HOME = "https://dieghernan.github.io/gifs/"


def build():
    metadata = json.loads((ROOT / "_data/structured_data.json").read_text(encoding="utf-8"))
    fields = json.loads((ROOT / "_data/croissant_fields.json").read_text(encoding="utf-8"))
    snapshot = metadata["croissant"]
    # Git blob bytes avoid platform-dependent CRLF conversions in the checksum.
    content = subprocess.check_output(
        ["git", "show", f'HEAD:{snapshot["sourcePath"]}'], cwd=ROOT)
    rows = list(csv.DictReader(io.StringIO(content.decode("utf-8"))))
    with (ROOT / snapshot["sourcePath"]).open(encoding="utf-8", newline="") as stream:
        if rows != list(csv.DictReader(stream)):
            raise ValueError("Commit CSV changes before generating its Croissant snapshot.")
    if list(rows[0]) != [field["column"] for field in fields]:
        raise ValueError("CSV columns differ from the documented Croissant fields.")
    if any(value == "" for row in rows for value in row.values()):
        raise ValueError("Empty CSV cells require a review of the documented missing-value policy.")
    dates = sorted(row["date"] for row in rows)
    if metadata["dataset"]["temporalCoverage"] != f"{dates[0]}/{dates[-1]}":
        raise ValueError("Dataset temporal coverage does not match the CSV.")

    context = json.loads((ROOT / "_data/croissant_context.json").read_text(encoding="utf-8"))
    dataset = dict(metadata["dataset"])
    dataset.update({
        "@context": context, "@type": "Dataset", "@id": HOME + "#dataset",
        "url": HOME, "conformsTo": "http://mlcommons.org/croissant/1.1",
        **metadata["publication"],
    })
    dataset["creator"] = {**dataset["creator"], "@id": HOME + "#author"}
    dataset["distribution"] = [{
        "@type": ["cr:FileObject", "sc:DataDownload"], "@id": "gif-csv",
        "name": metadata["dataset"]["distribution"][0]["name"],
        "contentUrl": ("https://raw.githubusercontent.com/dieghernan/gifs/"
                       + snapshot["sourceRevision"] + "/" + snapshot["sourcePath"]),
        "encodingFormat": "text/csv", "contentSize": f"{len(content)} bytes",
        "sha256": hashlib.sha256(content).hexdigest(),
        "dateModified": metadata["publication"]["dateModified"],
    }]
    record_set = snapshot["recordSet"]
    dataset["recordSet"] = [{
        "@type": "cr:RecordSet", "@id": record_set, "name": record_set,
        "description": "Un registro por incendio incluido en el CSV; los municipios y las fechas pueden repetirse. No se declara una clave única ni se distingue el estado definitivo o provisional de cada registro. No hay celdas vacías en esta instantánea; no se infieren valores ausentes ni se completan series anuales.",
        "field": [{
            "@type": "cr:Field", "@id": f'{record_set}/{field["column"]}',
            "name": field["column"], "description": field["description"],
            "dataType": field["dataType"],
            "source": {"fileObject": {"@id": "gif-csv"},
                       "extract": {"column": field["column"]}},
        } for field in fields],
    }]
    return json.dumps(dataset, ensure_ascii=False, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated metadata is stale.")
    args = parser.parse_args()
    output = build()
    for path in (ROOT / "croissant.json", ROOT / "_data/croissant.json"):
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != output:
                raise SystemExit(f"Stale descriptor: {path}. Run scripts/build_croissant.py.")
        else:
            path.write_text(output, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
