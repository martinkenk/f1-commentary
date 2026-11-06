import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import coverage_health as health
from ops import calendar_scheduler as scheduler
from ops import check_heartbeat

UTC = dt.timezone.utc


def context():
    return {"dir": "brazil", "year": "2026", "round_no": 20, "race_id": "1280",
            "results_slug": "brazil", "race_date": "2026-11-08", "ref": {},
            "cal": {"sessions": [
                {"label": "Practice 1", "date": "2026-11-06", "time": "12:30",
                 "gmt_offset": "-03:00"},
                {"label": "Race", "date": "2026-11-08", "time": "14:00",
                 "gmt_offset": "-03:00"}]}}


def at(value):
    return dt.datetime.fromisoformat(value).replace(tzinfo=UTC)


def live(now):
    return {"generated_at": now.isoformat(), "events": {}, "findings": [],
            "collection": {name: "success" for name in
                           ("enrichment", "calendar", "fia_media", "race_tyres")}}


class CalendarTests(unittest.TestCase):
    def test_calendar_offsets_drive_preflight_and_polling(self):
        jobs = list(scheduler.jobs([context()], at("2026-11-06T14:00")))
        pre, results = jobs[:2]
        self.assertEqual(pre["due"], at("2026-11-06T14:45"))
        self.assertEqual(pre["deadline"], at("2026-11-06T15:00"))
        self.assertEqual(results["due"], at("2026-11-06T16:20"))
        self.assertEqual(results["deadline"], at("2026-11-06T16:45"))
        self.assertEqual(jobs[-1]["due"], at("2026-11-08T18:00"))

    def test_revised_timezone_and_sprint_schedule_change_job_identity(self):
        ctx = context()
        ctx["cal"]["sessions"][0].update(label="Sprint Qualifying", gmt_offset="+05:30")
        first = list(scheduler.jobs([ctx], at("2026-11-06T01:00")))
        self.assertEqual(first[0]["due"], at("2026-11-06T06:15"))
        self.assertEqual(first[1]["due"], at("2026-11-06T07:35"))
        ctx["cal"]["sessions"][0]["time"] = "13:00"
        second = list(scheduler.jobs([ctx], at("2026-11-06T01:00")))
        self.assertNotEqual(first[0]["key"], second[0]["key"])

    def test_preflight_requires_successful_collection_not_just_fresh_build(self):
        now = at("2026-11-06T14:55")
        pre = next(scheduler.jobs([context()], now))
        value = live(now)
        self.assertTrue(scheduler.live_satisfies(pre, {}, value))
        value["collection"]["enrichment"] = "failure"
        self.assertFalse(scheduler.live_satisfies(pre, {}, value))
        self.assertFalse(scheduler.live_satisfies(pre, {}, None))
        value = live(now)
        value["collection_gp"] = "mexico"
        self.assertFalse(scheduler.live_satisfies(pre, {}, value))

    def test_old_or_retained_classification_does_not_finish_polling(self):
        now = at("2026-11-06T16:30")
        job = list(scheduler.jobs([context()], now))[1]
        value = live(now)
        value["events"] = {"brazil": {"sessions": {"Practice 1": {"digest": "old"}}}}
        self.assertFalse(scheduler.live_satisfies(job, {"digest": "new"}, value))
        value["events"]["brazil"]["sessions"]["Practice 1"] = {"digest": "new", "retained": True}
        self.assertFalse(scheduler.live_satisfies(job, {"digest": "new"}, value))
        value["events"]["brazil"]["sessions"]["Practice 1"]["retained"] = False
        self.assertTrue(scheduler.live_satisfies(job, {"digest": "new"}, value))

    def test_unpublished_results_remain_polled_after_the_active_weekend_window(self):
        earlier = at("2026-11-06T16:30")
        job = list(scheduler.jobs([context()], earlier))[1]
        records = {job["key"]: {"polled_at": earlier.isoformat(), "error": "delayed"}}
        late = at("2026-11-20T12:00")
        self.assertEqual([x["key"] for x in scheduler.jobs([context()], late, records)], [job["key"]])
        records[job["key"]]["status"] = "done"
        self.assertEqual(list(scheduler.jobs([context()], late, records)), [])

    def test_accepted_dispatch_is_recovered_after_restart(self):
        now = at("2026-11-06T14:50")
        state = {"errors": [], "request": {"at": "2026-11-06T14:48:00+00:00", "title": "Calendar refresh key"}}
        run = {"display_title": "Calendar refresh key", "id": 123, "html_url": "https://github.com/run",
               "status": "in_progress"}
        self.assertTrue(scheduler.reconcile_request(state, [run], live(now), now))
        self.assertEqual(state["request"]["run_id"], 123)
        run.update(status="completed", conclusion="failure")
        self.assertFalse(scheduler.reconcile_request(state, [run], live(now), now))
        self.assertNotIn("request", state)
        self.assertIn("Publication failed", state["errors"][0])

    def test_green_workflow_without_live_publication_remains_pending(self):
        now = at("2026-11-06T14:50")
        state = {"errors": [], "request": {"at": "2026-11-06T14:48:00+00:00", "title": "Calendar refresh key"}}
        run = {"display_title": "Calendar refresh key", "id": 123, "html_url": "https://github.com/run",
               "status": "completed", "conclusion": "success"}
        self.assertTrue(scheduler.reconcile_request(state, [run], live(at("2026-11-06T14:00")), now))
        self.assertIn("request", state)

    def test_delayed_results_retry_without_duplicate_dispatch_then_verify_live(self):
        now = at("2026-11-06T16:46")
        value = live(now)
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory)
            (state_path / "preferences.json").write_text('{"health_issue":115,"agent_blocked_reason":"approval"}')
            with patch.object(scheduler, "STATE", state_path), \
                 patch.object(scheduler, "checked", return_value=""), \
                 patch("build.season_gps", return_value=[context()]), \
                 patch.object(scheduler, "fetch_json", return_value=value), \
                 patch.object(scheduler, "api", return_value={"workflow_runs": []}), \
                 patch.object(scheduler, "heartbeat"), \
                 patch.object(scheduler, "poll_result", side_effect=[ValueError("not published"), "new"]) as poll, \
                 patch.object(scheduler, "dispatch") as dispatch:
                scheduler.tick(now)
                self.assertEqual(poll.call_count, 1)
                dispatch.assert_not_called()
                record = json.loads((state_path / "scheduler.json").read_text())
                self.assertTrue(any("classification overdue" in error for error in record["errors"]))
                scheduler.tick(now + dt.timedelta(minutes=1))
                self.assertEqual(poll.call_count, 1)
                scheduler.tick(now + dt.timedelta(minutes=2))
                self.assertEqual(poll.call_count, 2)
                dispatch.assert_called_once()
                self.assertEqual(dispatch.call_args.args[1:3], ("results", "brazil"))
                value["events"] = {"brazil": {"sessions": {"Practice 1": {"digest": "new"}}}}
                scheduler.tick(now + dt.timedelta(minutes=3))
                self.assertEqual(dispatch.call_count, 1)
                record = json.loads((state_path / "scheduler.json").read_text())
                key = list(scheduler.jobs([context()], now))[1]["key"]
                self.assertEqual(record["jobs"][key]["status"], "done")

    def test_restart_records_missed_preflight_without_historical_dispatch(self):
        now = at("2026-11-06T15:35")
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory)
            (state_path / "preferences.json").write_text('{"health_issue":115,"agent_blocked_reason":"approval"}')
            with patch.object(scheduler, "STATE", state_path), \
                 patch.object(scheduler, "checked", return_value=""), \
                 patch("build.season_gps", return_value=[context()]), \
                 patch.object(scheduler, "fetch_json", return_value=live(now)), \
                 patch.object(scheduler, "api", return_value={"workflow_runs": []}), \
                 patch.object(scheduler, "heartbeat"), \
                 patch.object(scheduler, "dispatch") as dispatch:
                scheduler.tick(now)
                dispatch.assert_not_called()
                record = json.loads((state_path / "scheduler.json").read_text())
                self.assertTrue(any("missed pre-session" in error for error in record["errors"]))


class HealthTests(unittest.TestCase):
    def test_frozen_standings_are_detected_even_outside_previous_weekend_window(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data/standings_2026.json").write_text('{"results_round":16}')
            result = health.report([context()], root, at("2026-11-20T12:00"))
            self.assertEqual([x["kind"] for x in result["findings"]], ["standings"])

    def test_future_results_and_post_qualifying_tyres_are_not_overdue(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(health.news_briefing, "select", return_value={"mode": "Editor-collated"}):
            report = health.report([context()], directory, at("2026-11-06T09:00"))
            self.assertFalse(any(f["kind"] in ("results", "standings") for f in report["findings"]))
            self.assertFalse(any("strategy" in f["message"] or "inventory" in f["message"]
                                 for f in report["findings"]))

    def test_revised_fia_hash_requires_review_not_just_cached_screenshot(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(health.news_briefing, "select", return_value={"mode": "Editor-collated"}):
            path = Path(directory) / "data/brazil"
            path.mkdir(parents=True)
            (path / "fia_media.json").write_text(json.dumps({"documents": [
                {"filename": "power_unit_information.pdf", "url": "https://www.fia.com/file.pdf", "sha256": "new"}]}))
            receipt = path / "coverage_review.json"
            receipt.write_text(json.dumps({"fia_sha256": {"https://www.fia.com/file.pdf": "old"}}))
            report = health.report([context()], directory, at("2026-11-06T09:00"))
            self.assertTrue(any("New/revised FIA" in f["message"] for f in report["findings"]))
            receipt.write_text(json.dumps({"fia_sha256": {"https://www.fia.com/file.pdf": "new"}}))
            report = health.report([context()], directory, at("2026-11-06T09:00"))
            self.assertFalse(any("New/revised FIA" in f["message"] for f in report["findings"]))

    def test_collector_failure_is_visible_even_when_last_good_data_exists(self):
        with patch.dict("os.environ", {"F1_COLLECTION": '{"standings":"failure"}'}):
            report = health.report([], ".", at("2026-11-06T09:00"))
        self.assertEqual(report["findings"][0]["kind"], "source_error")

    def test_independent_monitor_rejects_stale_and_future_heartbeats(self):
        now = at("2026-11-06T09:00")
        def body(stamp, errors=None):
            return "```json\n" + json.dumps({"heartbeat_at": stamp, "errors": errors or []}) + "\n```"
        self.assertEqual(check_heartbeat.assess(body("2026-11-06T08:30:00+00:00"), now), "")
        self.assertIn("stale", check_heartbeat.assess(body("2026-11-06T06:30:00+00:00"), now))
        self.assertIn("Invalid", check_heartbeat.assess(body("2026-11-06T09:30:00+00:00"), now))
        self.assertIn("unresolved", check_heartbeat.assess(body("2026-11-06T08:30:00+00:00", ["blocked"]), now))


if __name__ == "__main__":
    unittest.main()
