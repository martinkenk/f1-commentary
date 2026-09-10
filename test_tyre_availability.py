import unittest
from unittest.mock import patch

import f1lib


class TyreAvailabilityTests(unittest.TestCase):
    def test_official_inventory_does_not_require_fastf1(self):
        ctx = {"name": "Spanish Grand Prix", "year": "2026", "dir": "spain", "results": []}
        with patch.object(f1lib, "_load_pace", return_value=[]):
            body = f1lib.render_tyre_availability(
                ctx, official={"NOR": (1, 2, 3, 0, 1, 1)},
                compounds=("C2", "C3", "C4"), source_url="https://www.fia.com/example.pdf")
        self.assertIn("Tyre sets available for the race (official)", body)
        self.assertIn("Hard (C2)", body)
        self.assertIn("Soft (C4)", body)
        self.assertIn("Spanish Grand Prix", body)
        self.assertNotIn("Italian Grand Prix", body)
        self.assertIn("https://www.fia.com/example.pdf", body)

    def test_no_data_does_not_fabricate_inventory(self):
        with patch.object(f1lib, "_load_pace", return_value=[]):
            self.assertEqual(f1lib.render_tyre_availability({"dir": "spain"}), "")

    def test_invalid_official_counts_fail_explicitly(self):
        with patch.object(f1lib, "_load_pace", return_value=[]):
            for counts in ((1, 2), (1, 2, 3, 4, 5, -1)):
                with self.subTest(counts=counts), self.assertRaises(ValueError):
                    f1lib.render_tyre_availability({"dir": "spain"}, official={"NOR": counts})

    def test_estimate_uses_event_compounds_without_claiming_official_inventory(self):
        sessions = [{"tyre_stints": [{"fresh": True, "code": "NOR", "compound": "SOFT"}]}]
        with patch.object(f1lib, "_load_pace", return_value=sessions):
            body = f1lib.render_tyre_availability({"dir": "spain"}, compounds=("C2", "C3", "C4"))
        self.assertIn("Hard (C2)", body)
        self.assertIn("Soft (C4)", body)
        self.assertNotIn("C5", body)
        self.assertIn("not an official inventory", body)


if __name__ == "__main__":
    unittest.main()
