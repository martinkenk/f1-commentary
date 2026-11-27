import datetime
from html.parser import HTMLParser
import os
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import calendar_scraper as calendar
import json

import enrich
import f1lib
import build


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

    def test_event_is_upcoming_until_its_first_session_start(self):
        ctx = {
            "sessions": [
                ("Practice 1", "Fri 6 Nov", "2026-11-06", "12:30"),
                ("Race", "Sun 8 Nov", "2026-11-08", "14:00"),
            ],
            "cal": {"sessions": [
                {"label": "Practice 1", "date": "2026-11-06",
                 "time": "12:30", "gmt_offset": "-03:00"},
                {"label": "Race", "date": "2026-11-08",
                 "time": "14:00", "gmt_offset": "-03:00"},
            ]},
        }
        before = datetime.datetime(2026, 11, 6, 15, 29, tzinfo=datetime.timezone.utc)
        start = datetime.datetime(2026, 11, 6, 15, 30, tzinfo=datetime.timezone.utc)
        self.assertEqual(f1lib.event_status(ctx, now=before), "future")
        self.assertEqual(f1lib.event_status(ctx, now=start), "live")

    def test_active_gps_accepts_raw_calendar_events(self):
        today = datetime.datetime.now(datetime.timezone.utc).date()
        yesterday = today - datetime.timedelta(days=1)
        events = [
            {"slug": "spain", "name": "Spanish Grand Prix", "race_date": yesterday.isoformat(),
             "sessions": [{"label": "Race", "date": yesterday.isoformat(), "time": "15:00"}]},
            {"slug": "azerbaijan", "name": "Azerbaijan Grand Prix", "race_date": today.isoformat(),
             "sessions": [{"label": "Race", "date": today.isoformat(), "time": "14:00"}]},
        ]
        picked = enrich.active_gps(events)
        self.assertEqual({c["slug"] for c in picked}, {"spain", "azerbaijan"})


class NextGrandPrixTests(unittest.TestCase):
    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.events = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == "a" and "data-start" in attrs:
                self.events.append({
                    "href": attrs["href"],
                    "dataset": {"start": attrs["data-start"], "end": attrs["data-end"]},
                })

    def test_shortcut_renders_calendar_and_rejects_missing_schedule(self):
        gps = [ctx for ctx in build.season_gps() if ctx["dir"] in ("qatar", "united-arab-emirates")]
        page = f1lib.render_next_gp(gps)
        self.assertIn('src="assets/next-gp.js"', page)
        self.assertIn("<noscript>", page)
        self.assertIn('href="index.html"', page)
        links = self.Links()
        links.feed(page)
        self.assertEqual(len(links.events), 2)
        self.assertEqual(links.events[0]["dataset"]["start"], "2026-11-27T16:30:00+03:00")
        self.assertEqual(links.events[0]["dataset"]["end"], "2026-11-30T00:00:00+03:00")
        with self.assertRaisesRegex(ValueError, "Invalid schedule"):
            f1lib.render_next_gp([{**gps[0], "cal": {"sessions": []}}])

    @unittest.skipUnless(shutil.which("node"), "Node.js is required to exercise the browser script")
    def test_shortcut_selects_at_access_time_and_handles_season_end(self):
        gps = [ctx for ctx in build.season_gps() if ctx["dir"] in ("qatar", "united-arab-emirates")]
        links = self.Links()
        links.feed(f1lib.render_next_gp(gps))
        script = os.path.join(f1lib.ROOT, "assets_src", "next-gp.js")
        runner = """
const fs = require("fs"), vm = require("vm");
const input = JSON.parse(fs.readFileSync(0, "utf8"));
const status = {textContent: ""};
let target = null;
const context = {
  document: {querySelectorAll: () => input.events, getElementById: () => status},
  window: {location: {replace: value => { target = value; }}},
  Date: {parse: Date.parse, now: () => Date.parse(input.now)}
};
vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), context);
console.log(JSON.stringify({target, status: status.textContent}));
"""
        for now, expected in (
            ("2026-11-27T10:00:00Z", "qatar/overview.html"),
            ("2026-11-29T20:59:59Z", "qatar/overview.html"),
            ("2026-11-29T21:00:00Z", "united-arab-emirates/overview.html"),
            ("2026-12-06T20:00:00Z", None),
        ):
            with self.subTest(now=now):
                result = subprocess.run(
                    ["node", "-e", runner, script], check=True, capture_output=True, text=True,
                    input=json.dumps({"events": list(reversed(links.events)), "now": now}))
                output = json.loads(result.stdout)
                self.assertEqual(output["target"], expected)
                if expected is None:
                    self.assertIn("season is complete", output["status"])


class CalendarFieldTests(unittest.TestCase):
    def test_skips_markup_contamination_before_well_formed_value(self):
        page = (
            '"meetingOfficialName":"])</script><script>self.__next_f.push([1,"'
            '"meetingOfficialName":"FORMULA 1 QATAR AIRWAYS AZERBAIJAN GRAND PRIX 2026"'
        )
        self.assertEqual(
            calendar._field(page, "meetingOfficialName"),
            "FORMULA 1 QATAR AIRWAYS AZERBAIJAN GRAND PRIX 2026",
        )

    def test_returns_empty_when_only_malformed_value_exists(self):
        page = '"meetingOfficialName":"</script><script>invalid"'
        self.assertEqual(calendar._field(page, "meetingOfficialName"), "")


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
