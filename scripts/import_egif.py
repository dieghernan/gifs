"""Import downloaded EGIF ZIPs, retaining complete originals and provenance."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil

try:
    from scripts.egif import read_export
except ModuleNotFoundError:
    from egif import read_export

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--download-date", required=True, help="Date the exports were downloaded, YYYY-MM-DD.")
    parser.add_argument("--replace", action="store_true", help="Replace a prior annual snapshot after reviewing the change.")
    args = parser.parse_args()
    from datetime import date
    date.fromisoformat(args.download_date)
    folder = ROOT / "data-raw/egif"
    folder.mkdir(parents=True, exist_ok=True)
    index = folder / "sources.json"
    manifest = {row["year"]: row for row in json.loads(index.read_text(encoding="utf-8"))} if index.exists() else {}
    incoming = {}
    for path in sorted(args.directory.glob("*.zip")):
        rows = list(read_export(path))
        years = {row["Campania"] for row in rows}
        if len(years) != 1:
            raise ValueError(f"Expected one campaign year in {path}")
        year = int(years.pop())
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if year in incoming and digest != incoming[year]["sha256"]:
            raise ValueError(f"Conflicting downloads for {year}; choose one source snapshot")
        if year in manifest and digest != manifest[year]["sha256"] and not args.replace:
            raise ValueError(f"Snapshot for {year} already exists; review differences and use --replace")
        target = folder / f"egif-{year}.zip"
        incoming[year] = {"year": year, "path": target.relative_to(ROOT).as_posix(),
                          "download_date": args.download_date, "sha256": digest,
                          "records": len(rows), "states": dict(Counter(row["Estado"] for row in rows)),
                          "provinces": sorted({row["NumeroParte"][4:6] for row in rows}),
                          "source_url": "https://servicio.mapa.gob.es/incendios/Search/Publico",
                          "query_filters": "No se conserva captura de los filtros. Año observado en Campania."}
    if not incoming:
        raise ValueError("No ZIP exports found")
    # Validate all incoming files before replacing any snapshots.
    for year, entry in incoming.items():
        matching = [path for path in args.directory.glob("*.zip")
                    if hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]]
        source = matching[0]
        target = ROOT / entry["path"]
        if source.resolve() != target.resolve():
            shutil.copyfile(source, target)
        manifest[year] = entry
    index.write_text(json.dumps([manifest[year] for year in sorted(manifest)], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(incoming)} annual snapshots")


if __name__ == "__main__":
    main()
