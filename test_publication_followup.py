import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from ops import agent_queue as queue, publication_followup as followup, run_recovery


class PublicationTests(unittest.TestCase):
    def test_unpublished_local_commit_does_not_break_calendar_or_get_marked_live(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            path = state / "runs/20261107T120000Z"
            queue.save(path / "status.json", {"status": "blocked", "finished_at": "yes"})
            queue.save(path / "report.json", {
                "status": "blocked", "commit": "a" * 40,
                "summary": "Publication is deferred; local commit retained."})
            with patch.object(followup.urllib.request, "urlopen") as fetch:
                self.assertEqual(followup.reconcile(
                    state, [], None, [], Mock(return_value="b" * 40),
                    dt.datetime.now(dt.timezone.utc)), [])
                fetch.assert_not_called()
            self.assertEqual(json.loads((path / "status.json").read_text())["status"], "blocked")

    def test_recovery_explains_automatic_wait_and_manual_permission_boundaries(self):
        waiting = run_recovery.explain({"status": "waiting_publication"})
        self.assertTrue(waiting["automatic"])
        self.assertIsNone(waiting["action"])
        permission = run_recovery.explain({"status": "blocked", "error": "Permission denied"})
        self.assertFalse(permission["automatic"])
        self.assertEqual(permission["action"], "terminal")
        timeout = run_recovery.explain({"status": "timed_out"})
        self.assertEqual(timeout["action"], "recover")
    def test_pending_publication_requires_explicit_commit_and_no_fallback(self):
        report = {"status": "blocked", "commit": "a" * 40,
                  "summary": "Repair pushed; deployment remains in progress."}
        self.assertTrue(followup.pending_report(report))
        self.assertFalse(followup.pending_report(dict(report, commit=None)))
        self.assertFalse(followup.pending_report(dict(report, report_origin="wrapper_fallback")))
        self.assertFalse(followup.pending_report(dict(report, summary="Credentials need approval")))

    def test_successful_live_descendant_finishes_run_without_overwriting_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            path = state / "runs/20261107T120000Z"
            status = {"run_id": path.name, "status": "blocked", "finished_at": "2026-11-07T12:00:00Z"}
            report = {"status": "blocked", "commit": "a" * 40,
                      "summary": "Repair pushed; deployment remains in progress."}
            queue.save(path / "status.json", status)
            queue.save(path / "report.json", report)
            queue.save(state / "latest.json", status)
            deployed = {"id": 123, "status": "completed", "conclusion": "success",
                        "head_sha": "b" * 40, "html_url": "https://github.com/run"}
            live = {"run_id": "123", "generated_at": "2026-11-07T13:00:00Z", "findings": []}
            checked = Mock(side_effect=["a" * 40, "a" * 40 + "\n" + "b" * 40, "content_brazil.py"])
            response = Mock(status=200)
            response.read.return_value = b"<html>Verified page</html>"
            response.__enter__ = Mock(return_value=response)
            response.__exit__ = Mock(return_value=False)
            with patch.object(followup.urllib.request, "urlopen", return_value=response) as fetch:
                results = followup.reconcile(state, [deployed], live, [{"dir": "brazil"}],
                                             checked, dt.datetime.now(dt.timezone.utc))
            self.assertEqual(len(results), 1)
            self.assertEqual(fetch.call_count, 4)
            self.assertEqual(json.loads((path / "report.json").read_text()), report)
            self.assertEqual(json.loads((state / "latest.json").read_text())["status"], "fixed")
            self.assertTrue((path / "publication.json").exists())

    def test_premature_fixed_report_waits_for_live_evidence_and_finishes_only_once(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            path = state / "runs/20261107T164133Z"
            status = {"run_id": path.name, "status": "fixed", "finished_at": "2026-11-07T16:55:55Z"}
            report = {"status": "fixed", "commit": "a" * 40,
                      "summary": "Repair pushed, but publication is not confirmed."}
            queue.save(path / "status.json", status)
            queue.save(path / "report.json", report)
            queue.save(state / "latest.json", status)
            now = dt.datetime.now(dt.timezone.utc)
            self.assertEqual(followup.reconcile(
                state, [], None, [], Mock(return_value="a" * 40), now), [])
            self.assertEqual(json.loads((state / "latest.json").read_text())["status"], "waiting_publication")
            self.assertFalse((path / "publication.json").exists())
            deployed = {"id": 123, "status": "completed", "conclusion": "success",
                        "head_sha": "b" * 40, "html_url": "https://github.com/run"}
            live = {"run_id": "123", "generated_at": now.isoformat(), "findings": []}
            response = Mock(status=200)
            response.read.return_value = b"<html>Verified page</html>"
            response.__enter__ = Mock(return_value=response)
            response.__exit__ = Mock(return_value=False)
            checked = Mock(side_effect=["a" * 40, "a" * 40 + "\n" + "b" * 40, "content_brazil.py"])
            with patch.object(followup.urllib.request, "urlopen", return_value=response):
                result = followup.reconcile(state, [deployed], live, [{"dir": "brazil"}], checked, now)
            self.assertEqual(len(result), 1)
            self.assertEqual(json.loads((path / "status.json").read_text())["status"], "fixed")
            self.assertEqual(json.loads((path / "report.json").read_text()), report)
            checked.reset_mock()
            self.assertEqual(followup.reconcile(state, [deployed], live, [], checked, now), [])
            checked.assert_not_called()

    def test_workflow_success_without_live_identity_or_ancestry_does_not_finish(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            path = state / "runs/20261107T120000Z"
            queue.save(path / "status.json", {"status": "blocked", "finished_at": "yes"})
            queue.save(path / "report.json", {
                "status": "blocked", "commit": "a" * 40,
                "summary": "Repair pushed; deployment remains in progress."})
            deployed = {"id": 123, "status": "completed", "conclusion": "success", "head_sha": "b" * 40}
            for live in (None, {"run_id": 456}, {"run_id": 123}):
                with patch.object(followup.urllib.request, "urlopen") as fetch:
                    self.assertEqual(followup.reconcile(
                        state, [deployed], live, [], Mock(return_value="a" * 40 if live is None else "c" * 40),
                        dt.datetime.now(dt.timezone.utc)), [])
                    fetch.assert_not_called()
            self.assertEqual(json.loads((path / "status.json").read_text())["status"], "waiting_publication")
