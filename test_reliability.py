import re
import unittest

import f1lib


class ReliabilityTests(unittest.TestCase):
    def test_dns_is_not_counted_as_a_dnf_or_starter(self):
        ctx = {"results": [{
            "label": "Race",
            "headers": ["Pos.", "No.", "Driver", "Team", "Laps", "Time / Retired", "Pts."],
            "rows": [
                ["1", "1", "Winner Driver WIN", "Team A", "71", "1:30:00", "25"],
                ["NC", "2", "Retired Driver RET", "Team B", "30", "DNF", "0"],
                ["NC", "3", "Nonstarter Driver DNS", "Team C", "0", "DNS", "0"],
                ["NC", "4", "Disqualified Driver DSQ", "Team D", "50", "DSQ", "0"],
            ],
        }]}

        body = f1lib.render_reliability(ctx)
        stats = {
            label: value
            for value, label in re.findall(
                r'<div class="stat"><div class="stat-val">([^<]+)</div>'
                r'<div class="stat-lbl">([^<]+)</div>',
                body,
            )
        }

        self.assertEqual(stats["Classified finishers"], "1")
        self.assertEqual(stats["Retirements (DNF)"], "1")
        self.assertEqual(stats["Started"], "3")
        retirement_table = body.split("<th>Retired</th></tr></thead>", 1)[1].split("</tbody>", 1)[0]
        self.assertIn("Retired Driver", retirement_table)
        self.assertNotIn("Nonstarter Driver", retirement_table)
        self.assertNotIn("Disqualified Driver", retirement_table)
        self.assertIn("<h3>Did not start</h3>", body)
        self.assertIn("Nonstarter Driver", body)

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
            "fastestlaps": {"headers": ["Driver", "Time of Day", "Time", "Lap", "Avg"], "rows": [
                ["Kimi AntonelliANT", "15:22:00", "1:22.000", "50", "250.100"]]},
        }}
        body = f1lib.render_reliability(ctx)
        self.assertIn("Pit-lane time", body)
        self.assertIn("include pit-lane transit and the stop", body)
        self.assertNotIn("<th>Stationary</th>", body)
        self.assertLess(body.index("22.100s"), body.index("24.600s"))
        self.assertNotIn("15:20:00s", body)
        self.assertIn("Kimi Antonelli — 1:22.000", body)
        self.assertNotIn("Kimi Antonelli — 15:22:00", body)
        self.assertIn("no championship bonus point", body)
        self.assertNotIn("point goes to a top-10", body)


if __name__ == "__main__":
    unittest.main()
