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
    def test_completed_check_with_editorial_findings_is_attention_not_service_failure(self):
        now = at("2026-11-06T12:00")
        evidence = live(now)
        evidence["findings"] = [{"gp": "brazil", "kind": "editorial",
                                 "message": "The previous editorial briefing has expired."}]
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory)
            (state_path / "preferences.json").write_text('{"health_issue":115}')
            (state_path / "scheduler.json").write_text(json.dumps({
                "last_coverage_refresh": now.isoformat(), "agent_requested_at": now.isoformat()}))
            with patch.object(scheduler, "STATE", state_path), \
                 patch.object(scheduler, "checked", return_value=""), \
                 patch("build.season_gps", return_value=[]), \
                 patch.object(scheduler, "fetch_json", return_value=evidence), \
                 patch.object(scheduler, "api", return_value={"workflow_runs": []}), \
                 patch.object(scheduler, "heartbeat") as heartbeat:
                self.assertEqual(scheduler.tick(now), 0)
            record = json.loads((state_path / "scheduler.json").read_text())
            self.assertEqual(record["health_status"], "attention")
            self.assertEqual(record["coverage_findings"], evidence["findings"])
            self.assertTrue(record["errors"])
            self.assertEqual(record["execution_errors"], [])
            heartbeat.assert_called_once()

    def test_scheduler_execution_failure_still_exits_nonzero(self):
        now = at("2026-11-06T12:00")
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory)
            with patch.object(scheduler, "STATE", state_path), \
                 patch.object(scheduler, "checked", side_effect=RuntimeError("Repository fetch failed")), \
                 patch.object(scheduler, "heartbeat"):
                self.assertEqual(scheduler.tick(now), 1)
            record = json.loads((state_path / "scheduler.json").read_text())
            self.assertEqual(record["health_status"], "error")
            self.assertEqual(record["execution_errors"], ["Repository fetch failed"])

    def test_heartbeat_failure_is_not_hidden_as_successful_check(self):
        now = at("2026-11-06T12:00")
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory)
            with patch.object(scheduler, "STATE", state_path), \
                 patch.object(scheduler, "checked", return_value=""), \
                 patch("build.season_gps", return_value=[]), \
                 patch.object(scheduler, "fetch_json", return_value=live(now)), \
                 patch.object(scheduler, "api", return_value={"workflow_runs": []}), \
                 patch.object(scheduler, "heartbeat", side_effect=RuntimeError("GitHub unavailable")):
                self.assertEqual(scheduler.tick(now), 1)
            record = json.loads((state_path / "scheduler.json").read_text())
            self.assertEqual(record["health_status"], "error")
            self.assertIn("Health issue update failed", record["execution_errors"][0])

    def test_calendar_offsets_drive_preflight_and_polling(self):
        jobs = list(scheduler.jobs([context()], at("2026-11-06T14:00")))
        upgrade = next(job for job in jobs if job["kind"] == "upgrades")
        pre = next(job for job in jobs if job["kind"] == "pre" and job["label"] == "Practice 1")
        results = next(job for job in jobs if job["kind"] == "results"
                       and job["label"] == "Practice 1")
        self.assertEqual(upgrade["due"], at("2026-11-06T14:00"))
        self.assertEqual(upgrade["deadline"], at("2026-11-06T15:30"))
        self.assertEqual(pre["due"], at("2026-11-06T14:30"))
        self.assertEqual(pre["deadline"], at("2026-11-06T15:00"))
        self.assertEqual(results["due"], at("2026-11-06T16:20"))
        self.assertEqual(results["deadline"], at("2026-11-06T16:45"))
        self.assertEqual(jobs[-1]["due"], at("2026-11-08T18:00"))

    def test_revised_timezone_and_sprint_schedule_change_job_identity(self):
        ctx = context()
        ctx["cal"]["sessions"][0].update(time="13:30", gmt_offset="+05:30")
        first = list(scheduler.jobs([ctx], at("2026-11-06T01:00")))
        upgrade = next(job for job in first if job["kind"] == "upgrades")
        pre = next(job for job in first if job["kind"] == "pre")
        self.assertEqual(upgrade["due"], at("2026-11-06T06:30"))
        self.assertEqual(pre["due"], at("2026-11-06T07:00"))
        ctx["cal"]["sessions"][0]["time"] = "13:00"
        second = list(scheduler.jobs([ctx], at("2026-11-06T01:00")))
        self.assertEqual(upgrade["key"],
                         next(job for job in second if job["kind"] == "upgrades")["key"])
        self.assertNotEqual(pre["key"], next(job for job in second if job["kind"] == "pre")["key"])

    def test_preflight_requires_successful_collection_not_just_fresh_build(self):
        now = at("2026-11-06T14:55")
        pre = next(job for job in scheduler.jobs([context()], now) if job["kind"] == "pre")
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
        job = next(job for job in scheduler.jobs([context()], now)
                   if job["kind"] == "results" and job["label"] == "Practice 1")
        value = live(now)
        value["events"] = {"brazil": {"sessions": {"Practice 1": {"digest": "old"}}}}
        self.assertFalse(scheduler.live_satisfies(job, {"digest": "new"}, value))
        value["events"]["brazil"]["sessions"]["Practice 1"] = {"digest": "new", "retained": True}
        self.assertFalse(scheduler.live_satisfies(job, {"digest": "new"}, value))
        value["events"]["brazil"]["sessions"]["Practice 1"]["retained"] = False
        self.assertTrue(scheduler.live_satisfies(job, {"digest": "new"}, value))

    def test_unpublished_results_remain_polled_after_the_active_weekend_window(self):
        earlier = at("2026-11-06T16:30")
        job = next(job for job in scheduler.jobs([context()], earlier)
                   if job["kind"] == "results" and job["label"] == "Practice 1")
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
                key = next(job["key"] for job in scheduler.jobs([context()], now)
                           if job["kind"] == "results" and job["label"] == "Practice 1")
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

    def test_upgrade_watch_is_one_stable_job_and_requires_its_own_publication(self):
        ctx = context()
        first = at("2026-11-06T14:05")
        job = next(job for job in scheduler.jobs([ctx], first) if job["kind"] == "upgrades")
        item = {"refresh_key": "upgrade-key"}
        value = live(first)
        value.update(refresh_mode="upgrades", refresh_key="upgrade-key", collection_gp="brazil")
        self.assertTrue(scheduler.live_satisfies(job, item, value))
        value["refresh_mode"] = "pre-session"
        self.assertFalse(scheduler.live_satisfies(job, item, value))
        value["refresh_mode"] = "upgrades"
        value["collection"]["fia_media"] = "failure"
        self.assertFalse(scheduler.live_satisfies(job, item, value))
        records = {job["key"]: {"status": "done"}}
        self.assertFalse(any(job["kind"] == "upgrades"
                             for job in scheduler.jobs([ctx], first, records)))

    def test_upgrade_dispatch_persists_single_attempt_before_request(self):
        now = at("2026-11-06T14:00")
        job = next(job for job in scheduler.jobs([context()], now) if job["kind"] == "upgrades")
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(scheduler, "STATE", Path(directory)), \
                patch.object(scheduler, "checked"):
            state = {"jobs": {}}
            scheduler.dispatch(state, "upgrades", "brazil", now, job)
            saved = json.loads((Path(directory) / "scheduler.json").read_text())
        self.assertEqual(saved["jobs"][job["key"]]["status"], "dispatched")
        self.assertEqual(saved["jobs"][job["key"]]["refresh_key"], "20261106T140000Z")
        self.assertEqual(saved["request"]["job_key"], job["key"])

    def test_upgrade_run_failure_is_terminal_for_the_weekend(self):
        now = at("2026-11-06T14:10")
        job = next(job for job in scheduler.jobs([context()], now) if job["kind"] == "upgrades")
        state = {"errors": [], "jobs": {job["key"]: {"status": "dispatched",
                "refresh_key": "upgrade-key"}},
                 "request": {"at": "2026-11-06T14:00:00+00:00",
                             "title": "Calendar refresh key", "job_key": job["key"],
                             "gp": "brazil", "due": job["due"].isoformat(),
                             "start": job["start"].isoformat()}}
        run = {"display_title": "Calendar refresh key", "id": 123,
               "html_url": "https://github.com/run", "status": "completed",
               "conclusion": "failure"}
        scheduler.reconcile_request(state, [run], live(now), now)
        self.assertEqual(state["jobs"][job["key"]]["status"], "failed")
        self.assertFalse(any(item["kind"] == "upgrades"
                             for item in scheduler.jobs([context()], now, state["jobs"])))

    def test_successful_upgrade_run_is_verified_against_its_live_refresh_key(self):
        now = at("2026-11-06T14:10")
        job = next(job for job in scheduler.jobs([context()], now) if job["kind"] == "upgrades")
        state = {"errors": [], "jobs": {job["key"]: {"status": "dispatched",
                "refresh_key": "upgrade-key"}},
                 "request": {"at": "2026-11-06T14:00:00+00:00",
                             "title": "Calendar refresh key", "job_key": job["key"],
                             "gp": "brazil", "due": job["due"].isoformat(),
                             "start": job["start"].isoformat()}}
        run = {"display_title": "Calendar refresh key", "id": 123,
               "html_url": "https://github.com/run", "status": "completed",
               "conclusion": "success"}
        evidence = live(now)
        evidence.update(refresh_mode="upgrades", refresh_key="upgrade-key",
                        collection_gp="brazil")
        scheduler.reconcile_request(state, [run], evidence, now)
        self.assertEqual(state["jobs"][job["key"]]["status"], "done")
        self.assertEqual(state["jobs"][job["key"]]["published_at"], now.isoformat())
        self.assertEqual(state["errors"], [])

    def test_completed_upgrade_check_does_not_retrigger_only_for_unpublished_filing(self):
        findings = [
            {"gp": "brazil", "kind": "expected_source",
             "message": "Check publication/collection of upgrade submissions; expected by first practice"},
            {"gp": "brazil", "kind": "editorial", "message": "Review new FIA source"},
        ]
        records = {"2026/brazil/upgrades": {"status": "done"}}
        self.assertEqual(scheduler.retryable_findings(findings, [context()], records), [findings[1]])
        self.assertEqual(scheduler.retryable_findings(findings, [context()], {}), findings)


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

    def test_refresh_mode_is_reported_for_scheduler_reconciliation(self):
        with patch.dict("os.environ", {"F1_REFRESH_MODE": "upgrades"}):
            report = health.report([], ".", at("2026-11-06T09:00"))
        self.assertEqual(report["refresh_mode"], "upgrades")

    def test_quick_build_retains_failed_news_check_until_news_is_retried(self):
        now = at("2026-11-06T09:00")
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "data").mkdir()
            health.record_collection(directory, {"enrichment": "failure"}, "brazil", now)
            health.record_collection(directory, {"enrichment": "skipped", "session_results": "success"},
                                     "brazil", now + dt.timedelta(minutes=5))
            report = health.report([], directory, now + dt.timedelta(minutes=6))
            self.assertTrue(any("enrichment collector failed" in x["message"] for x in report["findings"]))
            health.record_collection(directory, {"enrichment": "success"}, "brazil",
                                     now + dt.timedelta(minutes=10))
            self.assertEqual(health.report([], directory, now + dt.timedelta(minutes=11))["findings"], [])

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
