"""Validate the published Croissant descriptor and its real remote CSV."""

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

from scripts.build_croissant import build

ROOT = Path(__file__).resolve().parents[1]


class CroissantTests(unittest.TestCase):
    def test_descriptor_matches_generated_and_embedded_metadata(self):
        descriptor = json.loads((ROOT / "croissant.json").read_text(encoding="utf-8"))
        self.assertEqual(json.loads(build()), descriptor)
        self.assertEqual(json.loads((ROOT / "_data/croissant.json").read_text(encoding="utf-8")), descriptor)
        self.assertEqual(json.loads((ROOT / "_site/croissant.json").read_text(encoding="utf-8")), descriptor)
        self.assertEqual(descriptor["conformsTo"], "http://mlcommons.org/croissant/1.1")
        self.assertNotIn("version", descriptor)  # No numbered data release exists.
        # Google rejects language-container objects in the embedded context.
        self.assertEqual(descriptor["@context"]["name"], "sc:name")
        self.assertEqual(descriptor["@context"]["description"], "sc:description")
        content = subprocess.check_output(["git", "show", "HEAD:rdata/gif_d2010.csv"], cwd=ROOT)
        file, = descriptor["distribution"]
        self.assertEqual(file["sha256"], hashlib.sha256(content).hexdigest())
        self.assertEqual(file["contentSize"], f"{len(content)} bytes")
        record_set, = descriptor["recordSet"]
        with (ROOT / "rdata/gif_d2010.csv").open(encoding="utf-8", newline="") as stream:
            columns = csv.DictReader(stream).fieldnames
        self.assertEqual([field["source"]["extract"]["column"] for field in record_set["field"]], columns)
        self.assertNotIn("key", record_set)  # A municipality/date pair need not be unique.

    def test_official_reader_preserves_all_downloaded_records_and_types(self):
        import mlcroissant

        dataset = mlcroissant.Dataset(jsonld=str(ROOT / "croissant.json"))
        loaded = list(dataset.records(record_set="fires"))
        with (ROOT / "rdata/gif_d2010.csv").open(encoding="utf-8", newline="") as stream:
            expected = list(csv.DictReader(stream))
        self.assertEqual(len(loaded), len(expected))
        for actual, row in zip(loaded, expected):
            with self.subTest(date=row["date"], municipality=row["codmun"]):
                for column in ("prov_name", "cpro", "munic_name", "cmun", "codmun"):
                    value = actual[f"fires/{column}"]
                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    self.assertIsInstance(value, str)
                    self.assertEqual(value, row[column])
                self.assertEqual(actual["fires/date"].strftime("%Y-%m-%d"), row["date"])
                self.assertAlmostEqual(actual["fires/area_forestal_ha"], float(row["area_forestal_ha"]), places=6)


if __name__ == "__main__":
    unittest.main()
