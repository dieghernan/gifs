"""Verify territorial grouping and independent date confirmation in the audit."""

from copy import deepcopy
from decimal import Decimal
import unittest

from scripts.audit_egif_2012 import AUDIT, ROOT, read_csv, reconcile


class Egif2012Tests(unittest.TestCase):
    def setUp(self):
        self.records = read_csv(ROOT / "data-raw/legacy/fires.csv")
        self.parts = read_csv(AUDIT / "egif-parts.csv")
        self.dates = read_csv(AUDIT / "report-dates.csv")

    def test_dates_groups_and_unresolved_differences(self):
        result, unmatched = reconcile(self.records, self.parts, self.dates)
        self.assertEqual(result, read_csv(AUDIT / "comparison.csv"))
        self.assertEqual(unmatched, read_csv(AUDIT / "unmatched-parts.csv"))
        self.assertEqual(len(result), 41)
        self.assertEqual(sum(Decimal(row["dataset_area_ha"]) for row in result),
                         Decimal("135580.04"))
        differences = {row["municipality"]: Decimal(row["difference_ha"])
                       for row in result if Decimal(row["difference_ha"])}
        self.assertEqual(differences, {"Chulilla": Decimal("2010.32"),
                                      "Llocnou de Sant Jeroni": Decimal("-0.14")})
        self.assertEqual([row["Municipio"] for row in unmatched], ["COCENTAINA"])
        linked = [part for row in result for part in row["egif_parts"].split("|")]
        self.assertEqual(len(linked), 43)
        self.assertEqual(len(set(linked)), 43)
        grouped = {row["municipality"] for row in result if "|" in row["egif_parts"]}
        self.assertEqual(grouped, {"Andilla", "Hellín / Moratalla"})

    def test_conflicting_official_date_is_rejected(self):
        dates = deepcopy(self.dates)
        dates[0]["date"] = "09/01/2012"
        with self.assertRaisesRegex(ValueError, "Date not confirmed"):
            reconcile(self.records, self.parts, dates)

    def test_duplicate_part_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate EGIF"):
            reconcile(self.records, self.parts + [self.parts[0]], self.dates)


if __name__ == "__main__":
    unittest.main()
