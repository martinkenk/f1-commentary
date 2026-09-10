import json
from pathlib import Path
import tempfile
import unittest

import coverage_inventory


class InventoryTests(unittest.TestCase):
    def test_distinguishes_missing_pages_images_and_optional_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            page = root / "site/spain/circuit.html"
            page.parent.mkdir(parents=True)
            page.write_text('<img src="../assets/missing.png"><img src="https://example.org/map.png">')
            ctx = {"dir": "spain", "race_date": "2026-09-13", "sessions": [],
                   "nav": [("circuit", "circuit.html"), ("tyres", "tyres.html")],
                   "pages": coverage_inventory.inventory}
            event = coverage_inventory.inventory([ctx], root)["events"][0]
            self.assertEqual(event["missing_rendered_pages"], ["tyres"])
            self.assertEqual(len(event["broken_local_images"]), 1)
            self.assertEqual(event["fia_documents_without_automatic_screenshots"], [])
            self.assertTrue(event["editorial_review_required"])

    def test_reports_uncached_sources_and_actual_discovery_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "data/spain"
            directory.mkdir(parents=True)
            (directory / "fia_documents.json").write_text(json.dumps({
                "documents": [{"filename": "power_unit_information.pdf",
                               "url": "https://www.fia.com/power_unit_information.pdf"}]}))
            (directory / "fia_discovery_status.json").write_text('{"error": "HTTP 403"}')
            ctx = {"dir": "spain", "race_date": "2026-09-13", "sessions": [],
                   "nav": [], "pages": coverage_inventory.inventory}
            event = coverage_inventory.inventory([ctx], root)["events"][0]
            self.assertEqual(event["fia_discovery"]["error"], "HTTP 403")
            self.assertEqual(event["fia_documents_without_automatic_screenshots"],
                             ["power_unit_information.pdf"])


if __name__ == "__main__":
    unittest.main()
