import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import coverage_inventory


class InventoryTests(unittest.TestCase):
    def test_passing_inventory_distinguishes_recent_check_from_recent_race_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            ctx = {"dir": "azerbaijan", "race_date": "2026-09-26", "sessions": [],
                   "nav": [], "pages": coverage_inventory.inventory}
            passing = {
                "checked_at": "2026-09-18T08:00:00Z", "error": "",
                "series": [{"name": "Example source", "races": [
                    {"year": 2025, "overtakes": None}, {"year": 2024, "overtakes": 47},
                ]}],
            }
            with patch.object(coverage_inventory.passing_history, "context", return_value=passing):
                report = coverage_inventory.inventory([ctx], Path(temporary))["events"][0]
            series = report["circuit_history"]["passing"]["series"][0]
            self.assertEqual(series["covered_editions"], 1)
            self.assertFalse(series["latest_edition_covered"])
            self.assertEqual(series["latest_covered_year"], 2024)
            self.assertFalse(report["circuit_history"]["passing"]["latest_edition_covered_by_any_series"])
            passing["series"].append({"name": "Reviewed 2025 source", "races": [
                {"year": 2025, "overtakes": 25}, {"year": 2024, "overtakes": None},
            ]})
            with patch.object(coverage_inventory.passing_history, "context", return_value=passing):
                report = coverage_inventory.inventory([ctx], Path(temporary))["events"][0]
            self.assertTrue(report["circuit_history"]["passing"]["latest_edition_covered_by_any_series"])

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
            self.assertFalse(event["circuit_history"]["available"])
            self.assertIsNone(event["circuit_history"]["completed_venue_races"])
            self.assertFalse(event["race_tyres"]["chart_available"])
            self.assertEqual(event["race_tyres"]["numeric_inventory"], "no_chart")
            self.assertEqual(event["race_tyres"]["verified_driver_rows"], 0)

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

    def test_history_debut_and_failed_refresh_are_distinct_from_missing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "data").mkdir()
            (root / "data/circuit_history_2026.json").write_text(json.dumps({
                "source": {"release": "v2026.14.0"},
                "profiles": {"spain": {"completed_races": 0, "drivers": [],
                                      "grand_prix": {"completed_races": 55},
                                      "teammates": {"pairs": []}}},
            }))
            (root / "data/circuit_history_2026_status.json").write_text(json.dumps({
                "ok": False, "error": "Checksum mismatch",
            }))
            ctx = {"dir": "spain", "race_date": "2026-09-13", "sessions": [],
                   "nav": [], "pages": coverage_inventory.inventory}
            history = coverage_inventory.inventory([ctx], root)["events"][0]["circuit_history"]
            self.assertTrue(history["available"])
            self.assertEqual(history["completed_venue_races"], 0)
            self.assertEqual(history["refresh"]["error"], "Checksum mismatch")


if __name__ == "__main__":
    unittest.main()
