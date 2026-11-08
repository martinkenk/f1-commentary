import hashlib
import http.client
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from ops import agent_queue as queue, watchdog, watchdog_web as web


class QueueTests(unittest.TestCase):
    def test_explicit_verified_completion_updates_original_without_erasing_report(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            original = "20261107T120000Z"
            queue.save(state / "runs" / original / "status.json",
                       {"status": "timed_out", "finished_at": "earlier"})
            queue.save(state / "runs" / original / "report.json", {"status": "blocked"})
            task = queue.enqueue(state, "Complete original task")
            queue.update(state, task["id"], run_id=original, status="timed_out")
            report = {"status": "fixed", "resolved_runs": [original],
                      "resolution_basis": "Original feature deployed and independently checked",
                      "sources": ["https://example.org/evidence"]}
            self.assertEqual(queue.resolve_runs(state, "20261108T120000Z", report, "READ_ONLY"), [])
            self.assertEqual(queue.resolve_runs(state, "20261108T120000Z", report, "PUBLISH"), [original])
            self.assertEqual(queue.jobs(state)[0]["status"], "fixed")
            status = json.loads((state / "runs" / original / "status.json").read_text())
            self.assertEqual(status["previous_status"], "timed_out")
            self.assertEqual(json.loads((state / "runs" / original / "report.json").read_text()),
                             {"status": "blocked"})

    def test_resolution_rejects_active_runs_or_missing_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            original = "20261107T120000Z"
            queue.save(state / "runs" / original / "status.json", {"status": "running"})
            report = {"status": "fixed", "resolved_runs": [original]}
            with self.assertRaises(ValueError):
                queue.resolve_runs(state, "20261108T120000Z", report, "PUBLISH")
            with self.assertRaises(ValueError):
                queue.resolve_runs(state, "20261108T120000Z",
                                   dict(report, resolution_basis="Checked"), "PUBLISH")

    def test_fifo_claim_cancellation_and_interrupted_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            first = queue.enqueue(state, "First task", "read_only")
            second = queue.enqueue(state, "Second task")
            self.assertEqual(queue.claim(state, "20261106T120000Z")["id"], first["id"])
            with self.assertRaises(ValueError):
                queue.cancel(state, first["id"])
            self.assertEqual(queue.claim(state, "20261106T120100Z")["id"], second["id"])
            self.assertEqual(queue.jobs(state)[0]["status"], "interrupted")
            third = queue.enqueue(state, "Cancel this")
            queue.cancel(state, third["id"])
            self.assertIsNone(queue.claim(state, "20261106T120200Z"))

    def test_validation_and_retry_delay(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            for prompt in ("", " " * 3, "a" * 16385, None):
                with self.assertRaises(ValueError):
                    queue.enqueue(state, prompt)
            with self.assertRaises(ValueError):
                queue.enqueue(state, "Valid prompt", resume_run="../../outside")
            job = queue.enqueue(state, "Wait for a remote writer")
            queue.update(state, job["id"], not_before="2999-01-01T00:00:00+00:00")
            self.assertIsNone(queue.claim(state, "20261106T120000Z"))

    def test_recovery_preserves_finalized_outcome_or_marks_interruption(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            queue.enqueue(state, "A killed job")
            queue.claim(state, "20261106T120000Z")
            queue.recover(state)
            self.assertEqual(queue.jobs(state)[0]["status"], "interrupted")
            job = queue.enqueue(state, "A completed job")
            queue.claim(state, "20261106T120100Z")
            queue.save(state / "runs/20261106T120100Z/status.json",
                       {"task_id": job["id"], "status": "fixed", "finished_at": queue.now()})
            queue.recover(state)
            self.assertEqual(queue.jobs(state)[1]["status"], "fixed")


class WebTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.state, self.config = root / "state", root / "config"
        self.config.mkdir()
        self.app = web.ControlRoom(self.state, self.config)
        queue.save(self.config / "password.json", web.password_record("a-long-test-password"))

    def test_setup_is_single_use_and_password_is_hashed(self):
        (self.config / "password.json").unlink()
        queue.save(self.config / "setup.json", {
            "digest": hashlib.sha256(b"setup-code").hexdigest(), "expires": time.time() + 60})
        with self.assertRaises(PermissionError):
            self.app.login({"code": "wrong", "password": "another-long-password"})
        token, csrf = self.app.login({"code": "setup-code", "password": "another-long-password"})
        self.assertTrue(token and csrf)
        self.assertFalse((self.config / "setup.json").exists())
        self.assertNotIn("another-long-password", (self.config / "password.json").read_text())
        with self.assertRaises(PermissionError):
            self.app.login({"code": "setup-code", "password": "invalid"})

    def test_login_throttle_and_session_expiry(self):
        for _ in range(10):
            with self.assertRaises(PermissionError):
                self.app.login({"password": "wrong"})
        with self.assertRaisesRegex(PermissionError, "Too many"):
            self.app.login({"password": "a-long-test-password"})
        self.app.failures.clear()
        token, _ = self.app.login({"password": "a-long-test-password"})
        self.assertTrue(self.app.session(f"{web.COOKIE}={token}")[1])
        self.app.sessions[token]["expires"] = 0
        self.assertEqual(self.app.session(f"{web.COOKIE}={token}"), (None, None))

    def test_policy_preserves_unknown_preferences_and_guidance_is_bounded(self):
        queue.save(self.state / "preferences.json", {"audit_only": False, "health_issue": 115})
        self.app.action("policy", {"audit_only": True})
        self.assertEqual(json.loads((self.state / "preferences.json").read_text()),
                         {"audit_only": True, "health_issue": 115})
        with self.assertRaises(ValueError):
            self.app.action("guidance", {"text": "a" * 16385})
        with self.assertRaises(ValueError):
            self.app.action("policy", {"audit_only": "false"})

    def test_recovery_requires_confirmation_and_deduplicates_continuations(self):
        identity = "20261107T120000Z"
        queue.save(self.state / "runs" / identity / "status.json", {
            "status": "timed_out", "mode": "PUBLISH",
            "session_id": "d579ad9e-29fa-4e91-8d48-6a7fd274969b"})
        with self.assertRaises(ValueError):
            self.app.action("recover", {"run_id": identity})
        first = self.app.action("recover", {"run_id": identity, "confirmed": True})
        second = self.app.action("recover", {"run_id": identity, "confirmed": True})
        self.assertEqual(first["task"]["id"], second["task"]["id"])
        self.assertEqual(first["task"]["resume_run"], identity)
        self.assertEqual(len(queue.jobs(self.state)), 1)
        self.assertIn("preserve", first["task"]["prompt"].lower())

    def test_permission_block_is_not_retried_via_recovery_endpoint(self):
        identity = "20261107T120000Z"
        queue.save(self.state / "runs" / identity / "status.json", {
            "status": "blocked", "error": "Permission denied: interpreter requires approval"})
        with self.assertRaises(ValueError):
            self.app.action("recover", {"run_id": identity, "confirmed": True})
        self.assertEqual(queue.jobs(self.state), [])

    def test_snapshot_surfaces_corrupt_state_and_stale_clock(self):
        self.state.mkdir()
        (self.state / "scheduler.json").write_text("not json")
        with patch.object(web.console, "properties", return_value={"ActiveState": "inactive"}):
            snapshot = self.app.snapshot()
        self.assertTrue(snapshot["scheduler_stale"])
        self.assertIsNone(snapshot["scheduler"])
        self.assertTrue(any("scheduler.json" in error for error in snapshot["errors"]))

    def test_run_path_rejects_traversal_and_symlinks(self):
        (self.state / "runs").mkdir(parents=True)
        (self.state / "runs/20261106T120000Z").symlink_to(self.config, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.app.run_path("../../config")
        with self.assertRaises(FileNotFoundError):
            self.app.run_path("20261106T120000Z")

    def test_http_auth_csrf_origin_and_log_escaping_contract(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), web.Handler)
        server.app = self.app
        server.allowed_host = f"127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)

        def request(method, path, body=None, cookie=None, csrf=None, origin=None):
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            headers = {"Content-Type": "application/json"}
            if cookie:
                headers["Cookie"] = cookie
            if csrf:
                headers["X-CSRF-Token"] = csrf
            if origin:
                headers["Origin"] = origin
            connection.request(method, path, json.dumps(body) if body is not None else None, headers)
            response = connection.getresponse()
            result = response.status, json.loads(response.read()), response.getheaders()
            connection.close()
            return result

        self.assertEqual(request("GET", "/api/status")[0], 401)
        code, result, headers = request("POST", "/api/login", {"password": "a-long-test-password"})
        self.assertEqual(code, 200)
        cookie = dict(headers)["Set-Cookie"]
        self.assertIn("HttpOnly; Secure; SameSite=Strict", cookie)
        self.assertEqual(request("POST", "/api/actions/start", {}, cookie)[0], 403)
        self.assertEqual(request("POST", "/api/actions/start", {}, cookie, result["csrf"],
                                 "https://attacker.invalid")[0], 403)
        code, job, _ = request("POST", "/api/actions/task",
                              {"prompt": "<script>alert(1)</script>", "mode": "read_only"},
                              cookie, result["csrf"])
        self.assertEqual(code, 200)
        self.assertEqual(job["task"]["prompt"], "<script>alert(1)</script>")
        self.assertEqual(request("POST", "/api/logout", {}, cookie, result["csrf"])[0], 200)
        self.assertEqual(request("GET", "/api/status", cookie=cookie)[0], 401)


class QueuedWorkerTests(unittest.TestCase):
    def command(self, args, **kwargs):
        value = "main\n" if args[:3] == ["git", "branch", "--show-current"] else ""
        return subprocess.CompletedProcess(args, 0, value, "")

    def test_mid_task_writer_conflict_queues_bounded_same_conversation_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            queue.enqueue(state, "Finish this repair")

            def agent(args, log, timeout):
                report = next((state / "runs").iterdir()) / "report.json"
                queue.save(report, {"status": "blocked", "summary": "Publication deferred while another writer is active.",
                                    "findings": [], "changes": [], "remaining": [], "sources": []})
                return 0

            with patch.object(watchdog, "STATE", state), \
                 patch.object(watchdog, "command", side_effect=self.command), \
                 patch.object(watchdog, "recent_runs", return_value=[]), \
                 patch.object(watchdog, "run_agent", side_effect=agent):
                self.assertEqual(watchdog.run(), 1)
            job = queue.jobs(state)[0]
            self.assertEqual(job["status"], "queued")
            self.assertEqual(job["automatic_retries"], 1)
            self.assertEqual(job["resume_run"], job["run_id"])
            self.assertGreater(job["not_before"], queue.now())

    def test_task_prompt_mode_and_completion_are_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            task = queue.enqueue(state, "Investigate the last error; make no changes.", "read_only")
            prompts = []

            def agent(args, log, timeout):
                prompts.append(args[-1])
                report = next((state / "runs").iterdir()) / "report.json"
                report.write_text(json.dumps({
                    "status": "healthy", "summary": "Diagnosis complete",
                    "findings": [], "changes": [], "remaining": [], "sources": []}))
                return 0

            with patch.object(watchdog, "STATE", state), \
                 patch.object(watchdog, "command", side_effect=self.command), \
                 patch.object(watchdog, "recent_runs", return_value=[]), \
                 patch.object(watchdog, "run_agent", side_effect=agent):
                self.assertEqual(watchdog.run(), 0)
            self.assertIn(task["prompt"], prompts[0])
            self.assertIn("Publication mode: READ_ONLY", prompts[0])
            self.assertEqual(queue.jobs(state)[0]["status"], "read_only")
            self.assertIn("run_id", queue.jobs(state)[0])

    def test_publish_task_remains_queued_when_remote_writer_is_active(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            queue.enqueue(state, "Implement a website feature")
            with patch.object(watchdog, "STATE", state), \
                 patch.object(watchdog, "command", side_effect=self.command), \
                 patch.object(watchdog, "recent_runs", return_value=[
                     {"name": "Calendar refresh", "path": ".github/workflows/deploy.yml",
                      "status": "in_progress"}]), \
                 patch.object(watchdog, "run_agent") as agent:
                self.assertEqual(watchdog.run(), 0)
                agent.assert_not_called()
            job = queue.jobs(state)[0]
            self.assertEqual(job["status"], "queued")
            self.assertIn("active", job["error"])
            self.assertGreater(job["not_before"], queue.now())


if __name__ == "__main__":
    unittest.main()
