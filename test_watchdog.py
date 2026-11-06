import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

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
        process.wait.side_effect = [subprocess.TimeoutExpired("copilot", 1), 0]
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(watchdog.subprocess, "Popen", return_value=process), \
             patch.object(watchdog.os, "killpg") as kill:
            self.assertEqual(watchdog.run_agent(["copilot"], Path(directory) / "log", 1), 124)
            kill.assert_called_once_with(1234, watchdog.signal.SIGTERM)


if __name__ == "__main__":
    unittest.main()
