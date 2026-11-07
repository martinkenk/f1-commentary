import datetime as dt
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import call, patch

from ops import watchdog


class WatchdogTests(unittest.TestCase):
    def test_both_github_writers_prevent_remote_publication(self):
        runs = [{"name": name, "status": status} for name, status in [
            ("Build & deploy to GitHub Pages", "in_progress"),
            ("Critical race coverage", "queued"),
            ("Other workflow", "in_progress"),
            ("Critical race coverage", "completed"),
        ]]
        self.assertEqual(watchdog.active_runs(runs), runs[:2])

    def test_agent_has_bounded_authority_not_all_paths(self):
        args = watchdog.agent_arguments("PROMPT", Path("/tmp/logs"))
        self.assertNotIn("--allow-all", args)
        self.assertNotIn("--allow-all-paths", args)
        self.assertNotIn("--allow-all-urls", args)
        self.assertIn("shell(sudo)", args)
        self.assertIn("--no-ask-user", args)
        for domain in ("api.github.com", "release-assets.githubusercontent.com", "www.statsf1.com",
                       "fantasy.formula1.com", "pbs.twimg.com", "x.com", "www.threads.com"):
            self.assertIn(domain, args)
        self.assertEqual(args[-1], "PROMPT")

    def test_dynamic_run_titles_still_block_using_stable_workflow_paths(self):
        run = {"name": "Calendar refresh 20261106T120000Z", "status": "in_progress",
               "path": ".github/workflows/deploy.yml"}
        self.assertEqual(watchdog.active_runs([run]), [run])

    def test_followup_resumes_without_trying_to_rename_existing_session(self):
        identity = "d579ad9e-29fa-4e91-8d48-6a7fd274969b"
        args = watchdog.agent_arguments("prompt", Path("/runs/run/cli"), identity, resume=True)
        self.assertIn("--resume", args)
        self.assertEqual(args[args.index("--resume") + 1], identity)
        self.assertNotIn("--name", args)
        self.assertNotIn("--session-id", args)

    def test_missing_gh_auth_still_audits_but_cannot_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            prompts = []

            def command(args, **kwargs):
                if args[:3] == ["gh", "auth", "status"]:
                    return subprocess.CompletedProcess(args, 1, "", "not logged in")
                value = "main\n" if args[:3] == ["git", "branch", "--show-current"] else ""
                return subprocess.CompletedProcess(args, 0, value, "")

            def agent(args, log, timeout):
                prompts.append(args[-1])
                report = next((state / "runs").iterdir()) / "report.json"
                report.write_text(json.dumps({
                    "status": "healthy", "summary": "public audit completed",
                    "findings": [], "changes": [], "remaining": [], "sources": [],
                }))
                return 0

            with patch.object(watchdog, "STATE", state), \
                 patch.object(watchdog, "command", side_effect=command), \
                 patch.object(watchdog, "recent_runs", return_value=[]), \
                 patch.object(watchdog, "run_agent", side_effect=agent):
                self.assertEqual(watchdog.run(), 0)
            status = json.loads((state / "latest.json").read_text())
            self.assertEqual(status["mode"], "READ_ONLY")
            self.assertEqual(status["status"], "read_only")
            self.assertIn("authentication_required", status)
            self.assertIn("Publication mode: READ_ONLY", prompts[0])

    def test_virtualenv_interpreter_grants_only_its_resolved_binary_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            system_bin = root / "usr/bin"
            system_bin.mkdir(parents=True)
            runtime = system_bin / "python3.12"
            runtime.touch()
            venv = root / "venv"
            (venv / "bin").mkdir(parents=True)
            interpreter = venv / "bin/python3"
            interpreter.symlink_to(runtime)
            with patch.object(watchdog.sys, "executable", str(interpreter)), \
                 patch.object(watchdog.sys, "prefix", str(venv)):
                args = watchdog.agent_arguments("PROMPT", Path("/tmp/logs"))
            directories = [args[i + 1] for i, arg in enumerate(args) if arg == "--add-dir"]
            self.assertEqual(directories, [str(watchdog.STATE), str(venv), str(system_bin.resolve())])
            self.assertIn(f"shell({interpreter}:*)", args)
            self.assertNotIn(str(system_bin.resolve().parent), directories)
            self.assertNotIn("--allow-all-paths", args)

    def test_timeout_stops_only_the_started_process_group(self):
        process = unittest.mock.Mock(pid=1234)
        process.wait.side_effect = [subprocess.TimeoutExpired("copilot", 1), 0, 0]
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(watchdog.subprocess, "Popen", return_value=process), \
             patch.object(watchdog.os, "killpg") as kill:
            self.assertEqual(watchdog.run_agent(["copilot"], Path(directory) / "log", 1), 124)
            self.assertEqual(kill.call_args_list, [
                call(1234, watchdog.signal.SIGTERM), call(1234, watchdog.signal.SIGKILL)])

    def test_budget_has_absolute_checkpoints_and_bounded_deployment_wait(self):
        started = dt.datetime(2026, 11, 6, 14, 30, tzinfo=dt.timezone.utc)
        prompt = watchdog.budget_instructions(started, 2700)
        self.assertIn("2026-11-06T15:05:00+00:00", prompt)
        self.assertIn("2026-11-06T15:13:00+00:00", prompt)
        self.assertIn("Hard process deadline: 2026-11-06T15:15:00+00:00", prompt)
        self.assertIn("provisional blocked report", prompt)
        self.assertIn("at most two minutes", prompt)
        short = watchdog.budget_instructions(started, 30)
        self.assertIn("Stop new investigation and edits by 2026-11-06T14:30:20", short)

    def test_timeout_counts_setup_and_preserves_or_generates_report(self):
        started = dt.datetime(2026, 11, 6, 14, 30, tzinfo=dt.timezone.utc)
        for existing_report in (False, True):
            with self.subTest(existing_report=existing_report), tempfile.TemporaryDirectory() as directory:
                state = Path(directory)
                partial = {"status": "blocked", "summary": "Deployment pending", "sources": ["run URL"]}
                head = "a" * 40

                def command(args, **kwargs):
                    if args == ["git", "rev-parse", "HEAD"]:
                        value = head
                    elif args == ["git", "status", "--short", "--branch"]:
                        value = "## main...origin/main [ahead 1]\n M content_brazil.py"
                    elif args[:3] == ["git", "branch", "--show-current"]:
                        value = "main"
                    else:
                        value = ""
                    return subprocess.CompletedProcess(args, 0, value, "")

                def agent(args, log, timeout):
                    self.assertEqual(timeout, 2090)
                    self.assertIn("Hard process deadline: 2026-11-06T15:15:00+00:00", args[-1])
                    if existing_report:
                        report = next((state / "runs").iterdir()) / "report.json"
                        report.write_text(json.dumps(partial))
                    return 124

                with patch.object(watchdog, "STATE", state), \
                     patch.object(watchdog, "command", side_effect=command), \
                     patch.object(watchdog, "recent_runs", return_value=[]), \
                     patch.object(watchdog, "run_agent", side_effect=agent), \
                     patch.object(watchdog.dt, "datetime", wraps=dt.datetime) as clock:
                    clock.now.side_effect = [started, started + dt.timedelta(seconds=10),
                                             started + dt.timedelta(seconds=2700),
                                             started + dt.timedelta(seconds=2700)]
                    self.assertEqual(watchdog.run(), 124)
                status = json.loads((state / "latest.json").read_text())
                report = json.loads(Path(status["report"]).read_text())
                self.assertEqual(status["status"], "timed_out")
                checkpoint = json.loads((Path(status["report"]).parent / "interruption.json").read_text())
                self.assertEqual(checkpoint["commit"], head)
                self.assertIn(" M content_brazil.py", checkpoint["remaining"][1])
                if existing_report:
                    self.assertEqual(report, partial)
                else:
                    self.assertEqual(report["status"], "blocked")
                    self.assertEqual(report["report_origin"], "wrapper_fallback")
                    self.assertEqual(report["commit"], head)
                    self.assertIn(" M content_brazil.py", report["remaining"][1])
                    self.assertIsNone(report["deployment_url"])

    def test_reserved_finalization_resumes_once_and_preserves_partial_report(self):
        started = dt.datetime(2026, 11, 7, 16, tzinfo=dt.timezone.utc)
        for final_code, mode in ((0, "PUBLISH"), (124, "PUBLISH"), (0, "READ_ONLY")):
            with self.subTest(final_code=final_code, mode=mode), tempfile.TemporaryDirectory() as directory:
                state = Path(directory)
                calls = []
                partial = {"status": "blocked", "summary": "Initial inspection"}
                final = {"status": "fixed", "summary": "Repair pushed; publication is not confirmed.",
                         "findings": [], "changes": ["Validated repair"], "remaining": ["Deployment"],
                         "sources": [], "commit": "b" * 40}
                if mode == "READ_ONLY":
                    final.update(status="read_only", summary="Audit completed without mutation", changes=[], commit=None)

                def command(args, **kwargs):
                    value = "main" if args[:3] == ["git", "branch", "--show-current"] else ""
                    return subprocess.CompletedProcess(args, 0, value, "")

                def agent(args, log, timeout):
                    calls.append((args, timeout))
                    report = log.parent / "report.json"
                    if len(calls) == 1:
                        self.assertEqual(timeout, 2090)
                        report.write_text(json.dumps(partial))
                        return 124
                    self.assertEqual(timeout, 570)
                    self.assertEqual(json.loads((state / "latest.json").read_text())["phase"], "finalizing")
                    self.assertIn("--resume", args)
                    identity = calls[0][0][calls[0][0].index("--session-id") + 1]
                    self.assertEqual(args[args.index("--resume") + 1], identity)
                    self.assertIn(f"Publication mode remains {mode}", args[-1])
                    self.assertIn("Do not wait for a deployment", args[-1])
                    if final_code == 0:
                        report.write_text(json.dumps(final))
                    return final_code

                with patch.object(watchdog, "STATE", state), \
                     patch.object(watchdog, "command", side_effect=command), \
                     patch.object(watchdog, "recent_runs", return_value=[]), \
                     patch.object(watchdog, "run_agent", side_effect=agent), \
                     patch.object(watchdog.dt, "datetime", wraps=dt.datetime) as clock:
                    clock.now.side_effect = [started, started + dt.timedelta(seconds=10),
                                             started + dt.timedelta(seconds=2110),
                                             started + dt.timedelta(seconds=2680)]
                    self.assertEqual(watchdog.run(audit_only=mode == "READ_ONLY"), final_code)
                self.assertEqual(len(calls), 2)
                status = json.loads((state / "latest.json").read_text())
                expected = "timed_out" if final_code else (
                    "read_only" if mode == "READ_ONLY" else "waiting_publication")
                self.assertEqual(status["status"], expected)
                saved = Path(status["report"]).parent / "report-before-finalization.json"
                self.assertEqual(json.loads(saved.read_text()), partial)
                if final_code:
                    self.assertEqual(json.loads(Path(status["report"]).read_text()), partial)

    def test_process_logs_append_across_finalization(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "agent.log"
            for value in ("investigation", "finalization"):
                self.assertEqual(watchdog.run_agent(
                    [watchdog.sys.executable, "-c", f"print({value!r})"], log, 5), 0)
            self.assertEqual(log.read_text(), "investigation\nfinalization\n")

    def test_fallback_records_git_inspection_failure_explicitly(self):
        with patch.object(watchdog, "command", side_effect=subprocess.TimeoutExpired("git", 5)):
            report = watchdog.incomplete_report({"status": "timed_out", "error": "Copilot exited 124"})
        self.assertEqual(report["status"], "blocked")
        self.assertIsNone(report["commit"])
        self.assertTrue(any("Could not capture checkout" in finding for finding in report["findings"]))


if __name__ == "__main__":
    unittest.main()
