import unittest
from career_starts import milestone, rank, render, snapshot


class CareerTests(unittest.TestCase):
    def test_completed_brazil_page_keeps_the_career_table_explicitly_pre_weekend(self):
        body = render({})
        self.assertIn("deliberately frozen", body)
        self.assertIn("completed Brazil classification", body)
        self.assertNotIn("before a classification", body)
        self.assertNotIn("not a forecast of his Brazil result", body)

    def test_shared_rank_and_passing_requires_one_more_start(self):
        rows = [{"id": "a", "name": "A", "starts": 10},
                {"id": "b", "name": "B", "starts": 10},
                {"id": "c", "name": "C", "starts": 8}]
        self.assertEqual(rank(rows, 10), 1)
        self.assertEqual(rank(rows, 8), 3)
        result = milestone(rows[-1], rows, {"c"}, 23)
        self.assertIn("3 further starts", result)
        self.assertIn("total stays fixed", result)

    def test_active_rival_cannot_be_caught_at_equal_participation(self):
        rows = [{"id": "a", "name": "A", "starts": 445},
                {"id": "b", "name": "B", "starts": 399}]
        self.assertIn("no catch", milestone(rows[1], rows, {"a", "b"}, 23))
        self.assertIn("47 more starts", milestone(rows[1], rows, {"a", "b"}, 23))
        self.assertIn("Already leads", milestone(rows[0], rows, {"a", "b"}, 23))

    def test_new_grid_driver_is_unknown_not_legacy_same_code_or_zero(self):
        drivers = [{"id": str(n), "name": f"Driver {n}", "abbreviation": f"{n:03}",
                    "totalRaceStarts": n} for n in range(22)]
        drivers[-1]["id"] = "legacy-driver"
        data = {"drivers": drivers,
                "seasons-drivers": [{"year": 2026, "driverId": str(n)} for n in range(21)],
                "races": [{"id": 1, "date": "2026-11-01"}],
                "races-race-results": [{"raceId": 1}]}
        grid = {"headers": ["Driver"], "source_url": "https://example.org/grid",
                "rows": [[f"Driver {n} {n:03}"] for n in range(22)]}
        value = snapshot(data, {}, grid, 2026)
        self.assertNotIn("legacy-driver", value["current_grid"])
        self.assertEqual(value["missing_totals"][0]["name"], "Driver 21")
        self.assertIsNone(value["missing_totals"][0]["starts"])
        data["races"][0]["date"] = "2026-11-08"
        with self.assertRaises(ValueError):
            snapshot(data, {}, grid, 2026)
