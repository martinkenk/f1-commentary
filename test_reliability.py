import unittest

import f1lib


class ReliabilityTests(unittest.TestCase):
    def test_future_event_does_not_describe_unrun_race_as_build_failure(self):
        ctx = {
            "status": "future",
            "sessions": [("Practice 1", "Fri", "2026-10-02", "12:30")],
            "results": [],
        }
        body = f1lib.render_reliability(ctx)
        self.assertIn("This weekend has not started yet", body)
        self.assertIn("official Race classification", body)
        self.assertNotIn("unavailable in this build", body)

    def test_past_event_points_to_saved_results_source_status(self):
        ctx = {
            "status": "past",
            "sessions": [("Race", "Sat", "2026-09-26", "15:00")],
            "results": [],
        }
        body = f1lib.render_reliability(ctx)
        self.assertIn("No official Race classification is available in the saved results", body)
        self.assertIn("Results page for its source status", body)

    def test_pitlane_times_and_fastest_lap_do_not_make_obsolete_claims(self):
        ctx = {"results": [], "extra": {
            "pitstops": {"headers": ["Driver", "Time of Day", "Time", "Lap"], "rows": [
                ["Kimi AntonelliANT", "15:20:00", "24.600", "20"],
                ["Lando NorrisNOR", "15:21:00", "22.100", "21"]]},
            "fastestlaps": {"headers": ["Driver", "Time", "Lap", "Avg"], "rows": [
                ["Kimi AntonelliANT", "1:22.000", "50", "250.100"]]},
        }}
        body = f1lib.render_reliability(ctx)
        self.assertIn("Pit-lane time", body)
        self.assertIn("include pit-lane transit and the stop", body)
        self.assertNotIn("<th>Stationary</th>", body)
        self.assertLess(body.index("22.100s"), body.index("24.600s"))
        self.assertNotIn("15:20:00s", body)
        self.assertIn("no championship bonus point", body)
        self.assertNotIn("point goes to a top-10", body)


if __name__ == "__main__":
    unittest.main()
