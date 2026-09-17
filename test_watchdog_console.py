import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

from ops import watchdog, watchdog_console as console


class ConsoleTests(unittest.TestCase):
    def test_terminal_escape_sequences_and_controls_are_removed(self):
        self.assertEqual(console.clean("\x1b[31mERROR\x1b[0m\n\x1b]0;title\x07ok\x00"), "ERROR\nok")

    def test_history_only_reads_own_run_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            (state / "runs/20260917T063838Z").mkdir(parents=True)
            (state / "runs/20260916T063838Z").mkdir()
            (state / "runs/unrelated").mkdir()
            (state / "runs/20260918T063838Z").symlink_to(state, target_is_directory=True)
            self.assertEqual([p.name for p in console.runs(state)],
                             ["20260917T063838Z", "20260916T063838Z"])

    def test_log_is_bounded_and_missing_log_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "log"
            self.assertIn("No log", console.read_tail(path))
            path.write_bytes(b"a" * 600000 + b"END")
            text = console.read_tail(path)
            self.assertTrue(text.endswith("END"))
            self.assertLess(len(text), 530000)

    def test_guidance_and_policy_are_consumed_by_runner(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            console.save_private(state / "preferences.json", '{"audit_only": true}')
            console.save_private(state / "operator-guidance.txt", "Focus on Azerbaijan's FIA documents.")
            self.assertEqual(watchdog.operator_settings(state),
                             (True, "Focus on Azerbaijan's FIA documents."))
            self.assertEqual(os.stat(state / "preferences.json").st_mode & 0o777, 0o600)
            console.save_private(state / "preferences.json", '{"audit_only": "false"}')
            with self.assertRaises(ValueError):
                watchdog.operator_settings(state)

    def test_sessions_are_named_and_resumed_by_validated_id(self):
        identity = "d579ad9e-29fa-4e91-8d48-6a7fd274969b"
        args = watchdog.agent_arguments("prompt", Path("/runs/run/cli"), identity)
        self.assertEqual(args[args.index("--session-id") + 1], identity)
        self.assertEqual(console.resume_arguments(Path("/repo"), {"session_id": identity}),
                     ["copilot", "-C", "/repo", "--mode", "interactive", "--resume", identity])
        self.assertEqual(console.resume_arguments(Path("/repo"), {})[-1], "--resume")
        with self.assertRaises(ValueError):
            console.resume_arguments(Path("/repo"), {"session_id": "--allow-all"})

    def test_stopped_run_does_not_appear_running(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run"
            path.mkdir()
            latest = {"run_id": "run", "status": "running", "mode": "PUBLISH"}
            self.assertEqual(console.run_status(path, latest, "inactive"),
                             ("interrupted", "PUBLISH"))
            self.assertEqual(console.run_status(path, latest, "activating"),
                             ("running", "PUBLISH"))

    def test_systemctl_failure_is_not_reported_as_success(self):
        result = subprocess.CompletedProcess([], 1, "", "permission denied")
        with patch.object(console.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "permission denied"):
                console.systemctl("start", console.SERVICE)

    def test_takeover_stops_writer_then_holds_lock_and_does_not_resume_timer(self):
        with tempfile.TemporaryDirectory() as directory:
            ui = object.__new__(console.Console)
            ui.state, ui.checkout = Path(directory), Path(directory)
            ui.history, ui.latest = [], {}
            ui.screen = Mock()
            ui.confirm = Mock(return_value=True)
            with patch.object(console, "systemctl") as control, \
                 patch.object(console.fcntl, "flock") as lock, \
                 patch.object(console.subprocess, "run") as run, \
                 patch.object(console.curses, "def_prog_mode"), \
                 patch.object(console.curses, "endwin"), \
                 patch.object(console.curses, "reset_prog_mode"):
                ui.takeover()
            self.assertEqual(control.call_args_list[0].args, ("disable", "--now", console.TIMER))
            self.assertEqual(control.call_args_list[1].args, ("stop", console.SERVICE))
            self.assertEqual(control.call_count, 2)
            lock.assert_called_once()
            run.assert_called_once()
            self.assertIn("PAUSED", ui.message)


if __name__ == "__main__":
    unittest.main()
