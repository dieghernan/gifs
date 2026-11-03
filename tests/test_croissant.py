"""Validate both structured products and the official Croissant reader."""

import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import unittest

from scripts.build_croissant import build

ROOT = Path(__file__).resolve().parents[1]


class CroissantTests(unittest.TestCase):
    def test_descriptor_matches_generated_resources_and_keys(self):
        descriptor = json.loads((ROOT / "croissant.json").read_text(encoding="utf-8"))
        self.assertEqual(json.loads(build()), descriptor)
        self.assertEqual(json.loads((ROOT / "_data/croissant.json").read_text(encoding="utf-8")), descriptor)
        self.assertEqual(json.loads((ROOT / "_site/croissant.json").read_text(encoding="utf-8")), descriptor)
        self.assertEqual(descriptor["conformsTo"], "http://mlcommons.org/croissant/1.1")
        self.assertEqual(descriptor["version"], "2.0.0-dev")
        self.assertNotIn("identifier", descriptor)
        self.assertEqual(descriptor["@context"]["name"], "sc:name")
        resources = json.loads((ROOT / "_data/structured_data.json").read_text(encoding="utf-8"))["croissant"]["resources"]
        for download, record_set, resource in zip(descriptor["distribution"][::3], descriptor["recordSet"], resources):
            with self.subTest(resource=resource["path"]):
                content = subprocess.check_output(["git", "show", "HEAD:" + resource["path"]], cwd=ROOT)
                self.assertEqual(download["sha256"], hashlib.sha256(content).hexdigest())
                self.assertEqual(download["contentSize"], f"{len(content)} bytes")
                self.assertEqual(record_set["key"], {"@id": resource["recordSet"] + "/" + resource["key"]})

    def test_official_reader_preserves_both_products_and_unknown_values(self):
        import mlcroissant

        metadata = json.loads((ROOT / "_data/structured_data.json").read_text(encoding="utf-8"))
        descriptor = json.loads((ROOT / "croissant.json").read_text(encoding="utf-8"))
        mapping = None
        if os.environ.get("GIFS_LOCAL_SNAPSHOT") == "1":
            # Local branch commits are not downloadable until explicitly pushed.
            mapping = {}
            for resource in metadata["croissant"]["resources"]:
                mapping[resource["id"]] = ROOT / resource["path"]
                mapping[resource["id"] + "-json"] = ROOT / resource["structuredPath"]
                mapping[resource["id"] + "-geojson"] = ROOT / resource["geoPath"]
        dataset = mlcroissant.Dataset(jsonld=str(ROOT / "croissant.json"), mapping=mapping)
        for resource in metadata["croissant"]["resources"]:
            with (ROOT / resource["path"]).open(encoding="utf-8", newline="") as stream:
                expected = list(csv.DictReader(stream))
            loaded = list(dataset.records(record_set=resource["recordSet"]))
            self.assertEqual(len(loaded), len(expected))
            fields = json.loads((ROOT / resource["fields"]).read_text(encoding="utf-8"))
            for actual, row in zip(loaded, expected):
                for field in fields:
                    name = field["column"]
                    value = actual[resource["recordSet"] + "/" + name]
                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    with self.subTest(record=row[resource["key"]], column=name):
                        if row[name] == "":
                            self.assertIn(value, (None, ""))
                        elif field["dataType"] == "sc:Float":
                            self.assertAlmostEqual(float(value), float(row[name]), places=8)
                        elif field["dataType"] == "sc:Date":
                            self.assertEqual(value.strftime("%Y-%m-%d"), row[name])
                        else:
                            self.assertEqual(value, row[name])


if __name__ == "__main__":
    unittest.main()
