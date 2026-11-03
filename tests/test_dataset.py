"""Check Dataset JSON-LD after building the Jekyll site."""

import csv
import json
import re
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DatasetTests(unittest.TestCase):
    def test_audited_records_and_methodology_are_preserved(self):
        with (ROOT / "rdata/gif_d2010.csv").open(encoding="utf-8", newline="") as stream:
            records = list(csv.DictReader(stream))
        self.assertEqual(len(records), 449)
        self.assertEqual(sum(Decimal(row["area_forestal_ha"]) for row in records),
                         Decimal("1311239.9728"))
        self.assertEqual(records, sorted(records, key=lambda row:
                         (row["date"], -Decimal(row["area_forestal_ha"]))))
        self.assertEqual(len({tuple(row.values()) for row in records}), len(records))
        for row in records:
            with self.subTest(date=row["date"], municipality=row["munic_name"]):
                self.assertGreaterEqual(Decimal(row["area_forestal_ha"]), Decimal(500))
                self.assertEqual(row["cpro"].zfill(2) + row["cmun"].zfill(3),
                                 row["codmun"].zfill(5))
        year_2012 = [row for row in records if row["date"].startswith("2012-")]
        self.assertEqual(len(year_2012), 41)
        with (ROOT / "rdata/audit/2012/comparison.csv").open(encoding="utf-8", newline="") as stream:
            confirmed = {row["codmun"]: row["date"] for row in csv.DictReader(stream)}
        self.assertEqual({row["codmun"].zfill(5): row["date"] for row in year_2012}, confirmed)
        self.assertEqual(min(row["date"] for row in year_2012), "2012-01-08")
        self.assertEqual(max(row["date"] for row in year_2012), "2012-09-23")
        year_2019 = [row for row in records if row["date"].startswith("2019-")]
        self.assertEqual(len(year_2019), 15)
        self.assertEqual(sum(Decimal(row["area_forestal_ha"]) for row in year_2019),
                         Decimal("30789.09"))
        descriptor = json.loads((ROOT / "croissant.json").read_text(encoding="utf-8"))
        self.assertEqual(descriptor["creator"]["name"], "Diego HH")
        self.assertEqual(descriptor["creator"]["url"], "https://dieghernan.github.io/")
        self.assertIn("EGIF", descriptor["description"])
        self.assertIn("inferencia", descriptor["measurementTechnique"])
        self.assertEqual(len(descriptor["isBasedOn"]["hasPart"]), 17)
        self.assertEqual(descriptor["subjectOf"]["url"],
                         "https://github.com/dieghernan/gifs/blob/main/METODOLOGIA.md")

    def test_metadata_matches_the_downloadable_records(self):
        html = (ROOT / "_site/index.html").read_text(encoding="utf-8")
        schemas = [json.loads(raw) for raw in re.findall(
            r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)]
        dataset, = [item for item in schemas if item.get("@type") == "Dataset"]
        descriptor = json.loads((ROOT / "croissant.json").read_text(encoding="utf-8"))
        self.assertEqual(dataset, descriptor)
        with (ROOT / "rdata/gif_d2010.csv").open(encoding="utf-8", newline="") as stream:
            records = list(csv.DictReader(stream))
        dates = sorted(row["date"] for row in records)
        self.assertEqual(dataset["temporalCoverage"], f"{dates[0]}/{dates[-1]}")
        self.assertIn(str(len(records)), dataset["description"])
        self.assertGreaterEqual(len(dataset["description"]), 50)
        self.assertLessEqual(len(dataset["description"]), 5000)
        self.assertEqual(dataset["creator"]["sameAs"], "https://orcid.org/0000-0001-8457-4658")
        self.assertEqual(dataset["datePublished"], "2025-02-21")
        self.assertEqual(dataset["dateModified"], "2026-11-03")
        self.assertIn("superficie forestal quemada", dataset["keywords"])
        self.assertEqual(dataset["license"], "https://www.miteco.gob.es/es/atencion-al-ciudadano/aviso-legal.html")
        self.assertEqual(dataset["isBasedOn"]["publisher"]["alternateName"], "MITECO")
        self.assertEqual(dataset["isBasedOn"]["url"], "https://www.miteco.gob.es/es/biodiversidad/temas/incendios-forestales/estadisticas-datos.html")
        self.assertIn("Origen de los datos", dataset["creditText"])
        self.assertIn("Superficie forestal quemada en hectáreas", dataset["variableMeasured"])
        download, = dataset["distribution"]
        self.assertEqual(download["encodingFormat"], "text/csv")
        self.assertEqual(download["dateModified"], dataset["dateModified"])
        snapshot = json.loads((ROOT / "_data/structured_data.json").read_text(encoding="utf-8"))["croissant"]
        self.assertEqual(download["contentUrl"],
                         f'https://raw.githubusercontent.com/dieghernan/gifs/{snapshot["sourceRevision"]}/{snapshot["sourcePath"]}')
        self.assertIn("sc:DataDownload", download["@type"])
        self.assertIn("cr:FileObject", download["@type"])
        self.assertIn(download["contentUrl"], html)
        self.assertNotIn('content="noindex', html)


if __name__ == "__main__":
    unittest.main()
