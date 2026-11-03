"""Validate both structured products and the official Croissant reader."""

import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import unittest

from scripts.build_croissant import build, spatial_coverage

ROOT = Path(__file__).resolve().parents[1]


class CroissantTests(unittest.TestCase):
    def test_spatial_box_uses_latitude_longitude_and_preserves_canary_coordinates(self):
        place = {'@type': 'Place', 'name': 'España'}
        collection = {'features': [
            {'geometry': {'type': 'Point', 'coordinates': [-17.9, 28.6]}},
            {'geometry': None},
            {'geometry': {'type': 'Point', 'coordinates': [2.4, 43.2]}},
        ]}
        coverage = spatial_coverage(place, [collection])
        self.assertEqual(coverage['name'], 'España')
        self.assertEqual(coverage['geo']['@type'], 'GeoShape')
        self.assertEqual(coverage['geo']['box'], '28.6 -17.9 43.2 2.4')
        self.assertNotIn('geo', place)
        self.assertEqual(spatial_coverage(place, [{'features': [{'geometry': None}]}]), place)

    def test_each_dataset_box_matches_its_geolocated_records(self):
        catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
        resources = json.loads((ROOT / '_data/structured_data.json').read_text(encoding='utf-8'))['croissant']['resources']
        all_points = []
        for dataset, resource in zip(catalog['dataset'], resources):
            collection = json.loads((ROOT / resource['geoPath']).read_text(encoding='utf-8'))
            points = [feature['geometry']['coordinates'] for feature in collection['features'] if feature['geometry']]
            all_points.extend(points)
            with self.subTest(dataset=dataset['@id']):
                south, west, north, east = map(float, dataset['spatialCoverage']['geo']['box'].split())
                self.assertEqual((west, south, east, north), (
                    min(point[0] for point in points), min(point[1] for point in points),
                    max(point[0] for point in points), max(point[1] for point in points)))
                self.assertLess(west, -13)
                self.assertLess(south, 30)
        south, west, north, east = map(float, catalog['spatialCoverage']['geo']['box'].split())
        self.assertEqual((west, south, east, north), (
            min(point[0] for point in all_points), min(point[1] for point in all_points),
            max(point[0] for point in all_points), max(point[1] for point in all_points)))

    def test_archive_doi_describes_the_collection_and_not_its_children(self):
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        citation = json.loads((ROOT / "_data/citation.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog['isPartOf']['@id'], citation['conceptDoiUrl'])
        self.assertEqual(catalog.get('identifier'), citation['doiUrl'])
        for dataset in catalog['dataset']:
            with self.subTest(dataset=dataset['@id']):
                self.assertEqual(dataset['isPartOf'], {'@id': catalog['@id']})
                self.assertNotIn('identifier', dataset)
                self.assertNotIn('sameAs', dataset)

    def test_catalog_jsonld_resolves_to_one_catalog_and_two_datasets(self):
        import rdflib
        from rdflib.namespace import RDF

        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        graph = rdflib.Graph().parse(data=json.dumps(catalog), format="json-ld")
        schema = rdflib.Namespace("https://schema.org/")
        self.assertEqual(len(list(graph.subjects(RDF.type, schema.DataCatalog))), 1)
        datasets = set(graph.objects(rdflib.URIRef(catalog["@id"]), schema.dataset))
        self.assertEqual(datasets, {rdflib.URIRef("https://dieghernan.github.io/gifs/#dataset-parts"),
                                    rdflib.URIRef("https://dieghernan.github.io/gifs/#dataset-fires")})
        for dataset in datasets:
            self.assertIn((dataset, RDF.type, schema.Dataset), graph)

    def test_descriptor_matches_generated_resources_and_keys(self):
        descriptor = json.loads((ROOT / "croissant.json").read_text(encoding="utf-8"))
        self.assertEqual(json.loads(build()), descriptor)
        self.assertEqual(json.loads((ROOT / "_data/croissant.json").read_text(encoding="utf-8")), descriptor)
        self.assertEqual(json.loads((ROOT / "_site/croissant.json").read_text(encoding="utf-8")), descriptor)
        self.assertEqual(descriptor["conformsTo"], "http://mlcommons.org/croissant/1.1")
        citation = json.loads((ROOT / "_data/citation.json").read_text(encoding="utf-8"))
        self.assertEqual(descriptor["version"], citation["version"])
        self.assertEqual(descriptor.get("identifier"), citation["doiUrl"])
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
        for resource in metadata["croissant"]["resources"]:
            mapping = None
            if os.environ.get("GIFS_LOCAL_SNAPSHOT") == "1":
                base = "https://dieghernan.github.io/gifs/"
                mapping = {base + resource["id"]: ROOT / resource["path"],
                           base + resource["id"] + "-json": ROOT / resource["structuredPath"],
                           base + resource["id"] + "-geojson": ROOT / resource["geoPath"]}
            dataset = mlcroissant.Dataset(jsonld=str(ROOT / f'croissant/{resource["recordSet"]}.json'), mapping=mapping)
            with (ROOT / resource["path"]).open(encoding="utf-8", newline="") as stream:
                expected = list(csv.DictReader(stream))
            loaded = list(dataset.records(record_set="https://dieghernan.github.io/gifs/" + resource["recordSet"]))
            self.assertEqual(len(loaded), len(expected))
            fields = json.loads((ROOT / resource["fields"]).read_text(encoding="utf-8"))
            for actual, row in zip(loaded, expected):
                for field in fields:
                    name = field["column"]
                    value = actual["https://dieghernan.github.io/gifs/" + resource["recordSet"] + "/" + name]
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
