"""Reconcile the retained 2012 EGIF extract with the dataset and report dates."""

import argparse
import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "rdata/audit/2012"
ALIASES = {
    "Torremanzanas/la Torre de les Maçanes": "TORRE DE LES MAÇANES, LA",
    "Hellín / Moratalla": "HELLÍN",
}
GROUPS = {
    "2012020224": ["2012020224", "2012300087"],
    "2012460247": ["2012460247", "2012120050"],
}


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def normalize(value):
    text = "".join(char for char in unicodedata.normalize("NFKD", value.upper())
                   if not unicodedata.combining(char))
    return " ".join(sorted(re.findall(r"[A-Z]+", text)))


def reconcile(records, parts, dates):
    """Match by province and municipality, then independently verify the date."""
    by_id = {part["NumeroParte"]: part for part in parts}
    if len(by_id) != len(parts):
        raise ValueError("Duplicate EGIF part identifiers")
    used = set()
    result = []
    for row in records:
        if not row["date"].startswith("2012-"):
            continue
        municipality = normalize(ALIASES.get(row["munic_name"], row["munic_name"]))
        matches = [part for part in parts
                   if part["NumeroParte"][4:6] == row["cpro"].zfill(2)
                   and normalize(part["Municipio"]) == municipality]
        if len(matches) != 1:
            raise ValueError(f"Ambiguous municipality: {row['munic_name']}")
        part, = matches
        group = GROUPS.get(part["NumeroParte"], [part["NumeroParte"]])
        if used.intersection(group):
            raise ValueError("EGIF part matched more than once")
        used.update(group)
        date = part["Detectado"].split()[0]
        location = normalize(part["Provincia"] + " " + part["Municipio"])
        report_matches = [entry for entry in dates
                          if normalize(entry["location"]) == location]
        if len(report_matches) != 1 or report_matches[0]["date"] != date:
            raise ValueError(f"Date not confirmed by report: {row['munic_name']}")
        area = sum(Decimal(by_id[key]["SuperficieTotalForestal"].replace(",", "."))
                   for key in group)
        difference = area - Decimal(row["area_forestal_ha"])
        result.append({
            "codmun": row["codmun"].zfill(5), "municipality": row["munic_name"],
            "date": datetime.strptime(date, "%d/%m/%Y").date().isoformat(),
            "egif_parts": "|".join(group), "dataset_area_ha": row["area_forestal_ha"],
            "egif_area_ha": str(area), "difference_ha": str(difference),
            "decision": "retain_report_area_pending_review" if difference else "match",
        })
    return sorted(result, key=lambda row: (row["date"], row["codmun"])), [
        part for part in parts if part["NumeroParte"] not in used]


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    records = read_csv(ROOT / "data-raw/legacy/fires.csv")
    comparison, unmatched = reconcile(records, read_csv(AUDIT / "egif-parts.csv"),
                                      read_csv(AUDIT / "report-dates.csv"))
    write_csv(AUDIT / "comparison.csv", comparison)
    write_csv(AUDIT / "unmatched-parts.csv", unmatched)
    print(f"{len(comparison)} dates confirmed; {len(unmatched)} unmatched part(s); "
          f"{sum(Decimal(row['difference_ha']) != 0 for row in comparison)} area discrepancies")


if __name__ == "__main__":
    main()
