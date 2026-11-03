"""Build part-level EGIF data and a reconciled fire view from versioned sources."""

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
from decimal import Decimal
import hashlib
import io
import json
import math
from pathlib import Path
import re
import unicodedata

try:
    from scripts.egif import read_export
except ModuleNotFoundError:
    from egif import read_export

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data-raw"
BASE_FIELDS = ["prov_name", "cpro", "munic_name", "cmun", "codmun", "date", "area_forestal_ha"]
FIRE_FIELDS = BASE_FIELDS + ["fire_id", "egif_part_ids", "source", "source_url", "source_date",
                           "data_status", "area_wooded_ha", "area_non_wooded_ha", "match_status", "notes",
                           "longitude", "latitude", "location_method", "location_part_id"]
PART_MAP = {
    "Campania": "year", "NumeroParte": "egif_part_id", "Estado": "source_state",
    "Comunidad": "community", "Provincia": "prov_name", "Municipio": "munic_name",
    "ComarcaIsla": "district", "EntidadMenor": "locality",
    "NumeroMunicipiosAfectados": "affected_municipalities", "Hoja": "map_sheet",
    "Cuadricula": "map_grid", "Huso": "utm_zone", "CoordenadaX": "coordinate_x",
    "CoordenadaY": "coordinate_y", "Datum": "datum",
    "NumeroPuntosInicioIncendio": "ignition_points", "Detectado": "detected_at",
    "Extinguido": "extinguished_at", "Causa": "cause", "Motivacion": "motivation",
    "SuperficieArbolada": "area_wooded_ha", "SuperficieNoArbolada": "area_non_wooded_ha",
    "SuperficieTotalForestal": "area_forestal_ha", "SuperficieAgricola": "area_agricultural_ha",
    "OtrasSuperficiesNoforestales": "area_other_non_forest_ha",
    "AfectoZonasInterfazUrbanoForestal": "affected_wildland_urban_interface",
    "TipoInterfazAfectado": "interface_type", "AfectoEspacioProtegido": "affected_protected_area",
    "AfectoTierrasAgrarias": "affected_agricultural_land", "AfectoZar": "affected_zar",
    "NumeroPartePss": "source_related_part_id",
}
PART_FIELDS = ["egif_part_id", "fire_id"] + [field for field in PART_MAP.values()
               if field != "egif_part_id"] + ["cpro", "cmun", "codmun", "date", "source", "source_url",
               "source_date", "source_file", "match_status", "notes", "longitude", "latitude",
               "source_epsg", "location_method", "geo_codmun", "geo_municipality", "municipality_check"]
AUDIT_FIELDS = ["fire_id", "legacy_date", "legacy_municipality", "legacy_area_ha", "egif_part_ids",
                "egif_date", "egif_area_ha", "difference_ha", "match_status", "notes"]


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def csv_text(rows, fields):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def typed_records(rows):
    records = []
    for row in rows:
        records.append({key: None if value == "" else float(value)
                        if key.startswith("area_") or key in {"longitude", "latitude"} else value
                        for key, value in row.items()})
    return records


def typed_json(rows):
    return json.dumps(typed_records(rows), ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def geojson(rows, key):
    features = []
    for properties in typed_records(rows):
        longitude, latitude = properties["longitude"], properties["latitude"]
        geometry = None
        if longitude is not None or latitude is not None:
            if longitude is None or latitude is None:
                raise ValueError("A GeoJSON point requires both longitude and latitude")
            if not (math.isfinite(longitude) and math.isfinite(latitude)
                    and -180 <= longitude <= 180 and -90 <= latitude <= 90):
                raise ValueError("Invalid EPSG:4326 coordinates")
            geometry = {"type": "Point", "coordinates": [longitude, latitude]}
        features.append({"type": "Feature", "id": properties[key],
                         "geometry": geometry, "properties": properties})
    return json.dumps({"type": "FeatureCollection", "features": features},
                      ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def clean(value):
    value = value.strip()
    return "" if value in {"-", "\\xa0"} else value


def decimal(value):
    return Decimal(value.replace(",", "."))


def normalize(value):
    value = "".join(char for char in unicodedata.normalize("NFKD", value.upper())
                    if not unicodedata.combining(char))
    return " ".join(sorted(re.findall(r"[A-Z]+", value)))


def normalize_part(row, source, municipalities):
    missing = set(PART_MAP) - set(row)
    if missing:
        raise ValueError(f"Missing source columns: {sorted(missing)}")
    part = {target: clean(row[key]) for key, target in PART_MAP.items()}
    part_id = part["egif_part_id"]
    if not re.fullmatch(r"\d{10}", part_id) or part_id[:4] != part["year"]:
        raise ValueError(f"Invalid part identifier/year: {part_id}")
    for field in ("detected_at", "extinguished_at"):
        if part[field]:
            part[field] = datetime.strptime(part[field], "%d/%m/%Y %H:%M:%S").isoformat()
    part["date"] = part["detected_at"][:10]
    if not part["date"]:
        raise ValueError(f"Missing detection date: {part_id}")
    for field in PART_MAP.values():
        if field.startswith("area_"):
            if not part[field]:
                raise ValueError(f"Missing surface {field}: {part_id}")
            amount = decimal(part[field])
            if amount < 0:
                raise ValueError(f"Negative surface: {part_id}")
            part[field] = str(amount)
    if Decimal(part["area_wooded_ha"]) + Decimal(part["area_non_wooded_ha"]) != Decimal(part["area_forestal_ha"]):
        raise ValueError(f"Forest area components do not add up: {part_id}")
    part["cpro"] = part_id[4:6]
    matches = municipalities.get((part["cpro"], normalize(part["munic_name"])), [])
    part["cmun"] = matches[0]["cmun"] if len(matches) == 1 else ""
    part["codmun"] = matches[0]["codmun"] if len(matches) == 1 else ""
    part.update(fire_id="", source="EGIF", source_url=source["source_url"],
                source_date=source["download_date"], source_file=source["path"],
                match_status="unassigned_part", notes="", longitude="", latitude="", source_epsg="",
                location_method="not_processed", geo_codmun="", geo_municipality="", municipality_check="not_checked")
    return part


def link_parts(parts, registry):
    """Apply reviewed links, never infer that an unassigned part is a new fire."""
    linked = {}
    seen_fires = set()
    for entry in registry:
        fire_id = entry["fire_id"]
        if not fire_id or fire_id in seen_fires:
            raise ValueError(f"Duplicate or empty fire ID: {fire_id}")
        seen_fires.add(fire_id)
        ids = entry["egif_part_ids"].split(";") if entry["egif_part_ids"] else []
        for part_id in ids:
            if part_id not in parts:
                raise ValueError(f"Registry references missing part: {part_id}")
            if part_id in linked:
                raise ValueError(f"Part assigned to more than one fire: {part_id}")
            linked[part_id] = fire_id
            parts[part_id].update(fire_id=fire_id, match_status=entry["match_status"], notes=entry["notes"])
        if len({parts[key]["year"] for key in ids}) > 1:
            raise ValueError(f"Fire spans multiple campaign years: {fire_id}")
    return linked


def selected_parts(parts, minimum=Decimal(500)):
    """Apply the threshold after explicit grouping; keep unassigned large parts."""
    totals = defaultdict(Decimal)
    for part in parts.values():
        if part["fire_id"]:
            totals[part["fire_id"]] += Decimal(part["area_forestal_ha"])
    return sorted((part for part in parts.values()
                   if (part["fire_id"] and totals[part["fire_id"]] >= minimum)
                   or (not part["fire_id"] and Decimal(part["area_forestal_ha"]) >= minimum)),
                  key=lambda row: (row["date"], row["egif_part_id"]))


def build_fire_view(baseline, registry, parts, source_urls, centers=None):
    fires, audit = [], []
    covered = set()
    for entry in registry:
        legacy_index = int(entry["legacy_row"]) - 1 if entry["legacy_row"] else None
        if legacy_index is not None:
            if legacy_index in covered or not 0 <= legacy_index < len(baseline):
                raise ValueError("Invalid or repeated legacy row")
            covered.add(legacy_index)
        old = baseline[legacy_index] if legacy_index is not None else None
        group = [parts[key] for key in entry["egif_part_ids"].split(";") if key]
        if group:
            area = sum(Decimal(part["area_forestal_ha"]) for part in group)
            primary = group[0]
            if old:
                row = dict(old)
            else:
                row = {field: primary[field] for field in BASE_FIELDS}
            row.update(date=min(part["date"] for part in group), area_forestal_ha=str(area),
                       source="EGIF", source_url=primary["source_url"], source_date=primary["source_date"],
                       data_status="egif_export",
                       area_wooded_ha=str(sum(Decimal(part["area_wooded_ha"]) for part in group)),
                       area_non_wooded_ha=str(sum(Decimal(part["area_non_wooded_ha"]) for part in group)))
            # Descriptions/codes from the legacy dataset are reference locations, not EGIF origin codes.
        elif old:
            row = dict(old)
            year = int(old["date"][:4])
            row.update(source="MITECO annual report" if year <= 2021 else "MITECO provisional bulletin",
                       source_url=source_urls[year], source_date="", data_status="definitive_report" if year <= 2021 else "provisional",
                       area_wooded_ha="", area_non_wooded_ha="")
        else:
            raise ValueError("Registry row has neither legacy data nor EGIF parts")
        row.update(fire_id=entry["fire_id"], egif_part_ids=entry["egif_part_ids"],
                   match_status=entry["match_status"], notes=entry["notes"])
        located = [part for part in group if part["longitude"] and part["latitude"]]
        if located:
            reference = located[0]
            row.update(longitude=reference["longitude"], latitude=reference["latitude"],
                       location_method="egif_part", location_part_id=reference["egif_part_id"])
        elif centers and row["codmun"].zfill(5) in centers:
            center = centers[row["codmun"].zfill(5)]
            row.update(longitude=center["longitude"], latitude=center["latitude"],
                       location_method="municipal_seat", location_part_id="")
        else:
            row.update(longitude="", latitude="", location_method="unavailable", location_part_id="")
        for field, width in (("cpro", 2), ("cmun", 3), ("codmun", 5)):
            row[field] = row[field].zfill(width) if row[field] else ""
        if Decimal(row["area_forestal_ha"]) >= 500:
            fires.append(row)
        audit.append({"fire_id": row["fire_id"], "legacy_date": old["date"] if old else "",
                      "legacy_municipality": old["munic_name"] if old else "", "legacy_area_ha": old["area_forestal_ha"] if old else "",
                      "egif_part_ids": row["egif_part_ids"], "egif_date": row["date"] if group else "",
                      "egif_area_ha": row["area_forestal_ha"] if group else "",
                      "difference_ha": str(Decimal(row["area_forestal_ha"]) - Decimal(old["area_forestal_ha"])) if group and old else "",
                      "match_status": row["match_status"], "notes": row["notes"]})
    if covered != set(range(len(baseline))):
        raise ValueError("The registry must account for every legacy record")
    return sorted(fires, key=lambda row: (row["date"], -Decimal(row["area_forestal_ha"]), row["fire_id"])), audit


def build(root=ROOT, prepare_locations=False):
    raw = root / "data-raw"
    manifest = json.loads((raw / "egif/sources.json").read_text(encoding="utf-8"))
    municipalities = defaultdict(list)
    for municipality in read_csv(raw / "municipalities.csv"):
        municipalities[(municipality["cpro"], normalize(municipality["munic_name"]))].append(municipality)
        alternatives = municipality["munic_name"].split("/")
        if len(alternatives) > 1:
            for alternative in alternatives:
                municipalities[(municipality["cpro"], normalize(alternative))].append(municipality)
    aliases = read_csv(raw / "municipality-aliases.csv")
    by_code = {row["codmun"]: row for rows in municipalities.values() for row in rows}
    for alias in aliases:
        municipalities[(alias["cpro"], normalize(alias["source_name"]))] = [by_code[alias["codmun"]]]
    parts, coverage = {}, []
    years = set()
    for source in manifest:
        year = source["year"]
        if year in years:
            raise ValueError(f"Duplicate source year: {year}")
        years.add(year)
        path = root / source["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Source checksum mismatch: {path}")
        count = 0
        provinces = Counter()
        for record in read_export(path):
            if record["Campania"] != str(year):
                raise ValueError(f"Unexpected year in {path}")
            part = normalize_part(record, source, municipalities)
            key = part["egif_part_id"]
            if key in parts:
                raise ValueError(f"Duplicate source part: {key}")
            parts[key] = part
            provinces[part["cpro"]] += 1
            count += 1
        if count != source["records"]:
            raise ValueError(f"Source record count mismatch: {path}")
        for province in [f"{i:02}" for i in range(1, 53)]:
            coverage.append({"year": str(year), "cpro": province, "parts": str(provinces[province]),
                             "coverage_status": "records_available_not_proof_of_completeness" if provinces[province] else "no_records_in_export"})
    registry = read_csv(raw / "fire-registry.csv")
    link_parts(parts, registry)
    selected = selected_parts(parts)
    if prepare_locations:
        fields = ["egif_part_id", "coordinate_x", "coordinate_y", "utm_zone", "datum", "codmun"]
        return {"dev/egif-location-input.csv": csv_text([{field: part[field] for field in fields} for part in selected], fields)}
    locations = {row["egif_part_id"]: row for row in read_csv(root / "data-derived/egif-locations.csv")}
    if set(locations) != {part["egif_part_id"] for part in selected}:
        raise ValueError("Geolocation cache is stale; prepare and geolocate the selected parts again")
    for part in selected:
        location = locations[part["egif_part_id"]]
        if any(part[field] != location[field] for field in ("coordinate_x", "coordinate_y", "utm_zone", "datum")) or part["codmun"] != location["declared_codmun"]:
            raise ValueError(f"Stale geolocation for part {part['egif_part_id']}")
        part.update({field: location[field] for field in ("longitude", "latitude", "source_epsg", "geo_codmun", "geo_municipality", "municipality_check")})
        part["location_method"] = location["location_status"]
    source_urls = {int(row["year"]): row["source_url"] for row in read_csv(raw / "legacy/sources.csv")}
    centers = {row["codmun"]: row for row in read_csv(raw / "municipal-centers-4326.csv")}
    fires, comparison = build_fire_view(read_csv(raw / "legacy/fires.csv"), registry, parts, source_urls, centers)
    baseline = read_csv(raw / "legacy/fires.csv")
    candidates = []
    for entry in registry:
        if entry["match_status"] != "pending_egif_match":
            continue
        old = baseline[int(entry["legacy_row"]) - 1]
        old_date = datetime.fromisoformat(old["date"])
        for part in parts.values():
            if part["fire_id"] or part["cpro"] != old["cpro"].zfill(2):
                continue
            delta = (datetime.fromisoformat(part["date"]) - old_date).days
            if abs(delta) <= 3 and Decimal(part["area_forestal_ha"]) >= 400:
                candidates.append({"fire_id": entry["fire_id"], "legacy_date": old["date"],
                                   "legacy_municipality": old["munic_name"], "egif_part_id": part["egif_part_id"],
                                   "egif_date": part["date"], "egif_municipality": part["munic_name"],
                                   "egif_area_ha": part["area_forestal_ha"], "day_difference": str(delta),
                                   "evidence": "same_province_within_3_days_area_at_least_400ha_not_a_confirmed_match"})
    unassigned = [part for part in selected if not part["fire_id"]]
    summary = {"egif_years": sorted(years), "source_parts": len(parts), "selected_parts": len(selected),
               "unassigned_selected_parts": len(unassigned), "fire_view_records": len(fires),
               "fire_view_area_ha": str(sum(Decimal(row["area_forestal_ha"]) for row in fires)),
               "pending_legacy_matches": sum(row["match_status"] == "pending_egif_match" for row in registry),
               "fire_view_note": "La vista conserva registros anteriores pendientes de conciliación; no se suman partes sin asignar a esos registros.",
               "years": [{"year": year, "fires": sum(row["date"].startswith(str(year)) for row in fires),
                          "area_ha": str(sum(Decimal(row["area_forestal_ha"]) for row in fires if row["date"].startswith(str(year))))}
                         for year in sorted({int(row["date"][:4]) for row in fires})]}
    return {
        "rdata/egif_parts.csv": csv_text(selected, PART_FIELDS),
        "rdata/gif_d2010.csv": csv_text(fires, FIRE_FIELDS),
        "rdata/egif_parts.json": typed_json(selected),
        "rdata/gif_d2010.json": typed_json(fires),
        "rdata/egif_parts.geojson": geojson(selected, "egif_part_id"),
        "rdata/gif_d2010.geojson": geojson(fires, "fire_id"),
        "rdata/audit/egif-comparison.csv": csv_text(comparison, AUDIT_FIELDS),
        "rdata/audit/egif-unassigned-parts.csv": csv_text(unassigned, PART_FIELDS),
        "rdata/audit/egif-coverage.csv": csv_text(coverage, ["year", "cpro", "parts", "coverage_status"]),
        "rdata/audit/egif-candidates.csv": csv_text(candidates, ["fire_id", "legacy_date", "legacy_municipality", "egif_part_id", "egif_date", "egif_municipality", "egif_area_ha", "day_difference", "evidence"]),
        "rdata/audit/egif-summary.json": json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check outputs without modifying files.")
    parser.add_argument("--prepare-locations", action="store_true", help="Write coordinate inputs for the R geolocation step.")
    args = parser.parse_args()
    for relative, content in build(prepare_locations=args.prepare_locations).items():
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Stale generated file: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    print("Dataset outputs verified" if args.check else "Dataset outputs generated")


if __name__ == "__main__":
    main()
