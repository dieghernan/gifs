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
    citation = json.loads((ROOT / "_data/citation.json").read_text(encoding="utf-8"))
    snapshot = metadata["croissant"]
    distributions, record_sets, all_dates = [], [], []
    for resource in snapshot["resources"]:
        fields = json.loads((ROOT / resource["fields"]).read_text(encoding="utf-8"))
        content = subprocess.check_output(["git", "show", f'HEAD:{resource["path"]}'], cwd=ROOT)
        rows = list(csv.DictReader(io.StringIO(content.decode("utf-8"))))
        with (ROOT / resource["path"]).open(encoding="utf-8", newline="") as stream:
            if rows != list(csv.DictReader(stream)):
                raise ValueError("Commit CSV changes before generating its Croissant snapshot.")
        if list(rows[0]) != [field["column"] for field in fields]:
            raise ValueError("CSV columns differ from the documented Croissant fields.")
        keys = [row[resource["key"]] for row in rows]
        if len(set(keys)) != len(keys) or not all(keys):
            raise ValueError(f"Invalid record key: {resource['key']}")
        all_dates.extend(row["date"] for row in rows)
        file_id, record_set = resource["id"], resource["recordSet"]
        distributions.append({
            "@type": ["cr:FileObject", "sc:DataDownload"], "@id": file_id,
            "name": resource["name"], "contentUrl": "https://raw.githubusercontent.com/dieghernan/gifs/" + snapshot["sourceRevision"] + "/" + resource["path"],
            "encodingFormat": "text/csv", "contentSize": f"{len(content)} bytes",
            "sha256": hashlib.sha256(content).hexdigest(), "dateModified": metadata["publication"]["dateModified"],
        })
        structured_content = subprocess.check_output(["git", "show", f'HEAD:{resource["structuredPath"]}'], cwd=ROOT)
        if json.loads(structured_content) != json.loads((ROOT / resource["structuredPath"]).read_text(encoding="utf-8")):
            raise ValueError("Commit JSON changes before generating its Croissant snapshot.")
        structured_id = file_id + "-json"
        distributions.append({
            "@type": ["cr:FileObject", "sc:DataDownload"], "@id": structured_id,
            "name": resource["name"] + " (JSON)",
            "contentUrl": "https://raw.githubusercontent.com/dieghernan/gifs/" + snapshot["sourceRevision"] + "/" + resource["structuredPath"],
            "encodingFormat": "application/json", "contentSize": f"{len(structured_content)} bytes",
            "sha256": hashlib.sha256(structured_content).hexdigest(), "dateModified": metadata["publication"]["dateModified"],
        })
        geo_content = subprocess.check_output(["git", "show", f'HEAD:{resource["geoPath"]}'], cwd=ROOT)
        if json.loads(geo_content) != json.loads((ROOT / resource["geoPath"]).read_text(encoding="utf-8")):
            raise ValueError("Commit GeoJSON changes before generating its Croissant snapshot.")
        distributions.append({
            "@type": ["cr:FileObject", "sc:DataDownload"], "@id": file_id + "-geojson",
            "name": resource["name"] + " (GeoJSON)",
            "contentUrl": "https://raw.githubusercontent.com/dieghernan/gifs/" + snapshot["sourceRevision"] + "/" + resource["geoPath"],
            "encodingFormat": "application/geo+json", "contentSize": f"{len(geo_content)} bytes",
            "sha256": hashlib.sha256(geo_content).hexdigest(), "dateModified": metadata["publication"]["dateModified"],
        })
        record_sets.append({
            "@type": "cr:RecordSet", "@id": record_set, "name": record_set,
            "description": resource["description"], "key": {"@id": f'{record_set}/{resource["key"]}'},
            "field": [{"@type": "cr:Field", "@id": f'{record_set}/{field["column"]}', "name": field["column"],
                       "description": field["description"], "dataType": field["dataType"],
                       "source": {"fileObject": {"@id": structured_id}, "extract": {"jsonPath": "$[*]." + field["column"]}}}
                      for field in fields],
        })
    dates = sorted(all_dates)
    if metadata["dataset"]["temporalCoverage"] != f"{dates[0]}/{dates[-1]}":
        raise ValueError("Dataset temporal coverage does not match the CSV.")

    context = json.loads((ROOT / "_data/croissant_context.json").read_text(encoding="utf-8"))
    dataset = dict(metadata["dataset"])
    dataset["version"] = metadata.get("developmentVersion", citation["version"])
    if "developmentVersion" in metadata:
        dataset["citeAs"] = f'Diego HH. Grandes incendios forestales en España ({metadata["developmentVersion"]}). Instantánea del repositorio {snapshot["sourceRevision"]}; sin DOI de versión.'
    if "developmentVersion" not in metadata:
        dataset.update(identifier=citation["doiUrl"], sameAs=citation["doiUrl"], citeAs=citation["citeAs"])
    dataset.update({
        "@context": context, "@type": "Dataset", "@id": HOME + "#dataset",
        "url": HOME, "conformsTo": "http://mlcommons.org/croissant/1.1",
        **metadata["publication"],
    })
    dataset["creator"] = {**dataset["creator"], "@id": HOME + "#author"}
    dataset["distribution"] = distributions
    dataset["recordSet"] = record_sets
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
