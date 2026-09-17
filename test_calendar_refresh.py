import datetime
import os
import tempfile
import unittest
from unittest.mock import patch

import calendar
import json

import enrich
import f1lib


class SessionCompatibilityTests(unittest.TestCase):
    def test_session_dicts_are_normalized_for_status_and_rendering(self):
        ctx = {"sessions": [
            {"label": "Practice 1", "date": "2026-09-11", "time": "11:30"},
            {"label": "Race", "date": "2026-09-13", "time": "15:00"},
        ]}
        self.assertEqual(f1lib.event_status(ctx, datetime.date(2026, 9, 12)), "live")
        self.assertEqual(f1lib.days_to_start(ctx, datetime.date(2026, 9, 10)), 1)
        rows = f1lib.schedule_rows({"sessions": ctx["sessions"], "tz_offset": 1})
        self.assertIn("Practice 1", rows)
        self.assertIn("Race", rows)
        self.assertIn("11:30", rows)
        self.assertIn("Fri", rows)

    def test_active_gps_accepts_raw_calendar_events(self):
        events = [
            {"slug": "spain", "name": "Spanish Grand Prix", "race_date": "2026-09-13",
             "sessions": [{"label": "Race", "date": "2026-09-13", "time": "15:00"}]},
            {"slug": "azerbaijan", "name": "Azerbaijan Grand Prix", "race_date": "2026-09-26",
             "sessions": [{"label": "Race", "date": "2026-09-26", "time": "14:00"}]},
        ]
        picked = enrich.active_gps(events)
        self.assertEqual({c["slug"] for c in picked}, {"spain", "azerbaijan"})


class TrackMapRefreshTests(unittest.TestCase):
    def event(self, days=0):
        day = datetime.datetime.now(datetime.timezone.utc).date() + datetime.timedelta(days=days)
        return {"slug": "test", "race_date": day.isoformat(),
                "track_image": "https://media.formula1.com/track.png"}

    def test_active_map_is_refreshed_even_if_it_already_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            os.mkdir(os.path.join(directory, "assets_src"))
            path = os.path.join(directory, "assets_src", "track-test.png")
            with open(path, "wb") as handle:
                handle.write(b"old")
            image = b"\x89PNG\r\n\x1a\nupdated map"
            with patch.object(calendar, "ROOT", directory), patch.object(calendar, "_get", return_value=image):
                calendar.fetch_track_maps([self.event()], 2026)
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), image)

    def test_bad_response_preserves_previous_map(self):
        with tempfile.TemporaryDirectory() as directory:
            os.mkdir(os.path.join(directory, "assets_src"))
            path = os.path.join(directory, "assets_src", "track-test.png")
            with open(path, "wb") as handle:
                handle.write(b"previous verified map")
            event = self.event()
            failures = []
            with patch.object(calendar, "ROOT", directory), patch.object(calendar, "_get", return_value=b"<html>blocked</html>"):
                calendar.fetch_track_maps([event], 2026, failures)
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), b"previous verified map")
            self.assertEqual(event["track_asset"], "track-test.png")
            self.assertEqual(len(failures), 1)
            self.assertIn("not a PNG", failures[0])

    def test_distant_existing_map_does_not_need_redownload(self):
        with tempfile.TemporaryDirectory() as directory:
            os.mkdir(os.path.join(directory, "assets_src"))
            path = os.path.join(directory, "assets_src", "track-test.png")
            with open(path, "wb") as handle:
                handle.write(b"map")
            with patch.object(calendar, "ROOT", directory), patch.object(calendar, "_get") as get:
                calendar.fetch_track_maps([self.event(50)], 2026)
            get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
