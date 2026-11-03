"""Check Dataset JSON-LD after building the Jekyll site."""

import csv
import json
import re
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DatasetTests(unittest.TestCase):
    def test_reconciled_view_preserves_legacy_records_and_source_priority(self):
        with (ROOT / "rdata/gif_d2010.csv").open(encoding="utf-8", newline="") as stream:
            records = list(csv.DictReader(stream))
        with (ROOT / "data-raw/legacy/fires.csv").open(encoding="utf-8", newline="") as stream:
            legacy = list(csv.DictReader(stream))
        with (ROOT / "data-raw/fire-registry.csv").open(encoding="utf-8", newline="") as stream:
            registry = list(csv.DictReader(stream))
        self.assertEqual(len(legacy), 449)
        self.assertEqual(sum(Decimal(row["area_forestal_ha"]) for row in legacy), Decimal("1311239.9728"))
        self.assertEqual({int(row["legacy_row"]) for row in registry if row["legacy_row"]}, set(range(1, 450)))
        self.assertEqual(len(records), 455)
        self.assertEqual(records, sorted(records, key=lambda row: (row["date"], -Decimal(row["area_forestal_ha"]), row["fire_id"])))
        self.assertEqual(len({row["fire_id"] for row in records}), len(records))
        for row in records:
            with self.subTest(fire=row["fire_id"]):
                self.assertGreaterEqual(Decimal(row["area_forestal_ha"]), Decimal(500))
                self.assertEqual(row["cpro"] + row["cmun"], row["codmun"])
                self.assertEqual(len(row["codmun"]), 5)
        year_2019 = [row for row in records if row["date"].startswith("2019-")]
        self.assertEqual(len(year_2019), 15)
        self.assertEqual(sum(Decimal(row["area_forestal_ha"]) for row in year_2019), Decimal("30789.09"))
        descriptor = json.loads((ROOT / "croissant.json").read_text(encoding="utf-8"))
        self.assertEqual(descriptor["creator"]["name"], "Diego HH")
        self.assertIn("EGIF", descriptor["description"])
        self.assertEqual(descriptor["version"], "2.0.0-dev")
        self.assertNotIn("identifier", descriptor)

    def test_catalog_contains_two_independent_datasets_matching_the_cards(self):
        html = (ROOT / "_site/index.html").read_text(encoding="utf-8")
        schemas = [json.loads(raw) for raw in re.findall(
            r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)]
        catalog, = [item for item in schemas if item.get("@type") == "DataCatalog"]
        self.assertEqual(catalog, json.loads((ROOT / "catalog.json").read_text(encoding="utf-8")))
        self.assertEqual(catalog, json.loads((ROOT / "_data/catalog.json").read_text(encoding="utf-8")))
        self.assertNotIn("distribution", catalog)
        self.assertNotIn("recordSet", catalog)
        self.assertEqual(len(catalog["dataset"]), 2)
        self.assertEqual(catalog["creator"]["sameAs"], "https://orcid.org/0000-0001-8457-4658")
        self.assertEqual(catalog["license"], "https://www.miteco.gob.es/es/atencion-al-ciudadano/aviso-legal.html")
        snapshot = json.loads((ROOT / "_data/structured_data.json").read_text(encoding="utf-8"))["croissant"]
        for dataset, resource in zip(catalog["dataset"], snapshot["resources"]):
            with self.subTest(dataset=resource["recordSet"]):
                self.assertEqual(dataset["@type"], "Dataset")
                self.assertEqual(dataset["includedInDataCatalog"], {"@id": catalog["@id"]})
                self.assertEqual(dataset["@id"], "https://dieghernan.github.io/gifs/#dataset-" + resource["recordSet"])
                self.assertEqual(dataset, json.loads((ROOT / f'croissant/{resource["recordSet"]}.json').read_text(encoding="utf-8")))
                self.assertEqual(dataset, json.loads((ROOT / f'_site/croissant/{resource["recordSet"]}.json').read_text(encoding="utf-8")))
                with (ROOT / resource["path"]).open(encoding="utf-8", newline="") as stream:
                    rows = list(csv.DictReader(stream))
                dates = sorted(row["date"] for row in rows)
                self.assertEqual(dataset["temporalCoverage"], f"{dates[0]}/{dates[-1]}")
                self.assertEqual(len(dataset["recordSet"]), 1)
                self.assertEqual(dataset["recordSet"][0]["name"], resource["recordSet"])
                self.assertEqual([item["encodingFormat"] for item in dataset["distribution"]], ["text/csv", "application/json", "application/geo+json"])
                for download, path in zip(dataset["distribution"], [resource["path"], resource["structuredPath"], resource["geoPath"]]):
                    self.assertEqual(download["contentUrl"], f'https://raw.githubusercontent.com/dieghernan/gifs/{snapshot["sourceRevision"]}/{path}')
                    self.assertIn(download["contentUrl"], html)
        self.assertNotIn('content="noindex', html)


if __name__ == "__main__":
    unittest.main()
