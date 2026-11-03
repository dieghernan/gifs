"""Behavioral checks for EGIF grouping, source priority and geolocation."""

import csv
from decimal import Decimal
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.build_dataset import (ROOT, build_fire_view, link_parts,
                                  read_csv, selected_parts, geojson)
from scripts.egif import read_export


class EgifPipelineTests(unittest.TestCase):
    def test_geojson_preserves_canary_coordinates_null_geometry_and_properties(self):
        rows = [{'egif_part_id': '2021386009', 'longitude': '-16.5', 'latitude': '28.2', 'notes': 'Canarias', 'area_forestal_ha': '500.0001'},
                {'egif_part_id': '2010200006', 'longitude': '', 'latitude': '', 'notes': 'Sin datum', 'area_forestal_ha': '500'}]
        collection = json.loads(geojson(rows, 'egif_part_id'))
        self.assertEqual(collection['type'], 'FeatureCollection')
        self.assertEqual(len(collection['features']), 2)
        point, missing = collection['features']
        self.assertEqual(point['id'], '2021386009')
        self.assertEqual(point['geometry'], {'type': 'Point', 'coordinates': [-16.5, 28.2]})
        self.assertEqual(point['properties']['area_forestal_ha'], 500.0001)
        self.assertIsNone(missing['geometry'])
        self.assertEqual(missing['properties']['notes'], 'Sin datum')
        self.assertNotIn('crs', collection)

    def test_geojson_rejects_incomplete_or_invalid_coordinates(self):
        for longitude, latitude in [('1', ''), ('181', '28'), ('nan', '28')]:
            with self.subTest(longitude=longitude, latitude=latitude):
                with self.assertRaises(ValueError):
                    geojson([{'fire_id': 'fire', 'longitude': longitude, 'latitude': latitude}], 'fire_id')

    def test_geojson_products_keep_every_record_and_match_typed_json(self):
        for stem, key in [('egif_parts', 'egif_part_id'), ('gif_d2010', 'fire_id')]:
            with self.subTest(product=stem):
                records = json.loads((ROOT / f'rdata/{stem}.json').read_text(encoding='utf-8'))
                collection = json.loads((ROOT / f'rdata/{stem}.geojson').read_text(encoding='utf-8'))
                self.assertEqual(len(collection['features']), len(records))
                self.assertEqual([feature['properties'] for feature in collection['features']], records)
                self.assertEqual([feature['id'] for feature in collection['features']], [row[key] for row in records])
                null_count = sum(feature['geometry'] is None for feature in collection['features'])
                self.assertEqual(null_count, sum(row['longitude'] is None for row in records))

    def test_display_displacement_applies_only_to_canary_points(self):
        locations = read_csv(ROOT / 'data-derived/fire-map-locations.csv')
        fires = {row['fire_id']: row for row in read_csv(ROOT / 'rdata/gif_d2010.csv')}
        for row in locations:
            with self.subTest(fire=row['fire_id']):
                if fires[row['fire_id']]['cpro'] not in {'35', '38'}:
                    self.assertAlmostEqual(float(row['source_longitude']), float(row['map_longitude']), places=8)
                    self.assertAlmostEqual(float(row['source_latitude']), float(row['map_latitude']), places=8)
                else:
                    self.assertGreater(float(row['map_latitude']), 33)
                    self.assertLess(float(row['source_latitude']), 30)

    def test_xlsx_reader_handles_unumbered_sheet_and_shared_strings(self):
        ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        workbook = io.BytesIO()
        with zipfile.ZipFile(workbook, 'w') as archive:
            archive.writestr('xl/sharedStrings.xml', f'<sst xmlns="{ns}"><si><t>Campania</t></si><si><t>NumeroParte</t></si></sst>')
            archive.writestr('xl/worksheets/sheet.xml', f'<worksheet xmlns="{ns}"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row><row r="2"><c r="A2"><v>2021</v></c><c r="B2" t="inlineStr"><is><t>2021010001</t></is></c></row></sheetData></worksheet>')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'export.zip'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('export.xlsx', workbook.getvalue())
            self.assertEqual(list(read_export(path)), [{'Campania': '2021', 'NumeroParte': '2021010001'}])

    def test_threshold_is_applied_after_grouping(self):
        parts = {'a': {'fire_id': 'one', 'egif_part_id': 'a', 'date': '2021-01-01', 'area_forestal_ha': '300'},
                 'b': {'fire_id': 'one', 'egif_part_id': 'b', 'date': '2021-01-01', 'area_forestal_ha': '200'},
                 'c': {'fire_id': '', 'egif_part_id': 'c', 'date': '2021-01-01', 'area_forestal_ha': '499'},
                 'd': {'fire_id': '', 'egif_part_id': 'd', 'date': '2021-01-01', 'area_forestal_ha': '500'}}
        self.assertEqual([row['egif_part_id'] for row in selected_parts(parts)], ['a', 'b', 'd'])
        self.assertEqual(parts['d']['fire_id'], '')

    def test_part_cannot_be_assigned_to_two_fires(self):
        parts = {'p': {'year': '2021'}}
        registry = [{'fire_id': name, 'egif_part_ids': 'p', 'match_status': 'reviewed', 'notes': ''}
                    for name in ['one', 'two']]
        with self.assertRaisesRegex(ValueError, 'more than one fire'):
            link_parts(parts, registry)

    def test_absent_egif_record_keeps_legacy_source_and_unknown_breakdown(self):
        old = {'prov_name': 'León', 'cpro': '24', 'munic_name': 'Example', 'cmun': '001',
               'codmun': '24001', 'date': '2023-01-01', 'area_forestal_ha': '700'}
        registry = [{'fire_id': 'stable-id', 'legacy_row': '1', 'egif_part_ids': '',
                     'match_status': 'pending_egif_match', 'notes': 'Pending'}]
        fires, audit = build_fire_view([old], registry, {}, {2023: 'https://example.org/source'})
        self.assertEqual(fires[0]['area_forestal_ha'], '700')
        self.assertEqual(fires[0]['source'], 'MITECO provisional bulletin')
        self.assertEqual(fires[0]['area_wooded_ha'], '')
        self.assertEqual(fires[0]['longitude'], '')
        self.assertEqual(audit[0]['egif_part_ids'], '')

    def test_products_preserve_ids_coordinates_and_optional_values(self):
        parts = read_csv(ROOT / 'rdata/egif_parts.csv')
        fires = read_csv(ROOT / 'rdata/gif_d2010.csv')
        self.assertEqual(len({row['egif_part_id'] for row in parts}), len(parts))
        self.assertEqual(len({row['fire_id'] for row in fires}), len(fires))
        self.assertEqual(len(parts), 329)
        by_id = {row['egif_part_id']: row for row in parts}
        for row in parts:
            with self.subTest(part=row['egif_part_id']):
                self.assertEqual(Decimal(row['area_wooded_ha']) + Decimal(row['area_non_wooded_ha']), Decimal(row['area_forestal_ha']))
                if row['datum'] == '' or row['location_method'] == 'missing_coordinates':
                    self.assertEqual((row['longitude'], row['latitude']), ('', ''))
                else:
                    self.assertGreater(float(row['latitude']), 27)
                    self.assertLess(float(row['latitude']), 45)
                    self.assertGreater(float(row['longitude']), -19)
                    self.assertLess(float(row['longitude']), 5)
        for row in fires:
            if row['location_method'] == 'egif_part':
                self.assertIn(row['location_part_id'], row['egif_part_ids'].split(';'))
                self.assertEqual(row['longitude'], by_id[row['location_part_id']]['longitude'])
            if row['source'] == 'EGIF':
                self.assertEqual(sum(Decimal(by_id[key]['area_forestal_ha']) for key in row['egif_part_ids'].split(';')), Decimal(row['area_forestal_ha']))
        # The source and geometric municipality must remain distinct when they disagree.
        discrepant = by_id['2021040012']
        self.assertEqual(discrepant['codmun'], '04068')
        self.assertEqual(discrepant['geo_codmun'], '04033')
        self.assertEqual(discrepant['municipality_check'], 'differs_from_declared')
        canary = next(row for row in parts if row['datum'] == 'REGCAN95')
        self.assertLess(float(canary['longitude']), -13)
        self.assertLess(float(canary['latitude']), 30)

    def test_egif_updates_surface_without_losing_legacy_territory(self):
        fires = read_csv(ROOT / 'rdata/gif_d2010.csv')
        chulilla = next(row for row in fires if row['egif_part_ids'] == '2012460249')
        self.assertEqual(Decimal(chulilla['area_forestal_ha']), Decimal('5713.65'))
        self.assertEqual(chulilla['source'], 'EGIF')
        hellin = next(row for row in fires if row['egif_part_ids'] == '2012020224;2012300087')
        self.assertEqual(hellin['munic_name'], 'Hellín / Moratalla')
        self.assertEqual(Decimal(hellin['area_forestal_ha']), Decimal('6549.47'))


if __name__ == '__main__':
    unittest.main()
