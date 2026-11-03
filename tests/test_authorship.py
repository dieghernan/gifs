"""Check the author identity inherited from the Chulapa layout."""

from pathlib import Path
import unittest

import mf2py

SITE = Path(__file__).resolve().parents[1] / "_site"
HOME = "https://dieghernan.github.io/"
PROJECT = HOME + "gifs/"


class AuthorshipTests(unittest.TestCase):
    def test_landing_page_identifies_the_author_at_the_personal_home(self):
        parsed = mf2py.parse(doc=(SITE / "index.html").read_text(encoding="utf-8"), url=PROJECT)
        entry, = [item for item in parsed["items"] if "h-entry" in item["type"]]
        self.assertEqual(entry["properties"]["url"], [PROJECT])
        author, = entry["properties"]["author"]
        self.assertIn("h-card", author["type"])
        self.assertEqual(author["properties"]["name"], ["Diego HH"])
        self.assertEqual(author["properties"]["url"][0], HOME)


if __name__ == "__main__":
    unittest.main()
