import datetime
import unittest

from fastf1_selection import active_analysis_slugs


class ActiveFastF1SelectionTests(unittest.TestCase):
    def test_selects_live_events_and_latest_race_within_seven_days(self):
        gps = [
            {"dir": "live", "status": "live", "race_date": "2026-11-21"},
            {"dir": "recent", "status": "past", "race_date": "2026-11-08"},
            {"dir": "older", "status": "past", "race_date": "2026-11-01"},
            {"dir": "future", "status": "future", "race_date": "2026-11-21"},
        ]

        self.assertEqual(
            active_analysis_slugs(gps, datetime.date(2026, 11, 11)),
            {"live", "recent"},
        )

    def test_includes_seventh_day_and_excludes_eighth_day(self):
        gps = [{"dir": "latest", "status": "past", "race_date": "2026-11-04"}]

        self.assertEqual(
            active_analysis_slugs(gps, datetime.date(2026, 11, 11)),
            {"latest"},
        )
        self.assertEqual(
            active_analysis_slugs(gps, datetime.date(2026, 11, 12)),
            set(),
        )

    def test_does_not_select_an_event_before_its_race_date(self):
        gps = [{"dir": "future", "status": "past", "race_date": "2026-11-12"}]

        self.assertEqual(
            active_analysis_slugs(gps, datetime.date(2026, 11, 11)),
            set(),
        )


if __name__ == "__main__":
    unittest.main()
