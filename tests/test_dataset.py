"""Check Dataset JSON-LD after building the Jekyll site."""

import csv
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DatasetTests(unittest.TestCase):
    def test_metadata_matches_the_downloadable_records(self):
        html = (ROOT / "_site/index.html").read_text(encoding="utf-8")
        schemas = [json.loads(raw) for raw in re.findall(
            r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)]
        dataset, = [item for item in schemas if item.get("@type") == "Dataset"]
        with (ROOT / "rdata/gif_d2010.csv").open(encoding="utf-8", newline="") as stream:
            records = list(csv.DictReader(stream))
        dates = sorted(row["date"] for row in records)
        self.assertEqual(dataset["temporalCoverage"], f"{dates[0]}/{dates[-1]}")
        self.assertIn(str(len(records)), dataset["description"])
        self.assertGreaterEqual(len(dataset["description"]), 50)
        self.assertLessEqual(len(dataset["description"]), 5000)
        self.assertEqual(dataset["creator"]["sameAs"], "https://orcid.org/0000-0001-8457-4658")
        self.assertEqual(dataset["license"], "https://www.miteco.gob.es/es/atencion-al-ciudadano/aviso-legal.html")
        self.assertEqual(dataset["isBasedOn"]["publisher"]["alternateName"], "MITECO")
        self.assertEqual(dataset["isBasedOn"]["url"], "https://www.miteco.gob.es/es/biodiversidad/temas/incendios-forestales/estadisticas-datos.html")
        self.assertIn("Origen de los datos", dataset["creditText"])
        self.assertIn("Superficie forestal quemada en hectáreas", dataset["variableMeasured"])
        download, = dataset["distribution"]
        self.assertEqual(download["encodingFormat"], "text/csv")
        self.assertEqual(download["contentUrl"],
                         "https://raw.githubusercontent.com/dieghernan/gifs/main/rdata/gif_d2010.csv")
        self.assertIn(download["contentUrl"], html)
        self.assertNotIn('content="noindex', html)


if __name__ == "__main__":
    unittest.main()
