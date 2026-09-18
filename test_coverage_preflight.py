import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import re

import coverage_preflight as preflight


class CoveragePreflightTests(unittest.TestCase):
    def test_editor_serializes_data_writers_and_reports_failed_pushes(self):
        lock = preflight.LOCK.read_text()
        concurrency = re.search(r"^concurrency:\n((?:  .*\n)+)", lock, re.M)[1]
        self.assertIn("group: pages", concurrency)
        self.assertIn("cancel-in-progress: false", concurrency)
        deploy = (preflight.ROOT / ".github/workflows/deploy.yml").read_text()
        self.assertIn("group: pages", deploy)
        guard = lock.split("  verify-publication:\n", 1)[1]
        self.assertIn("- agent\n      - safe_outputs", guard)
        self.assertIn("needs.safe_outputs.outputs.code_push_failure_count", guard)
        script = re.search(
            r"name: Fail on deferred code-push errors\n        run: \|\n"
            r"((?:          .*\n)+)", guard)[1]
        script = "\n".join(line[10:] for line in script.splitlines())
        for count, expected in [("", 0), ("0", 0), ("1", 1), ("3", 1)]:
            result = subprocess.run(["bash", "-c", script],
                                    env=dict(os.environ, CODE_PUSH_FAILURE_COUNT=count),
                                    capture_output=True)
            self.assertEqual(result.returncode, expected)
        self.assertIn("git merge --ff-only origin/main", lock)
        self.assertIn("/tmp/gh-aw/python/venv/bin/python3", lock)
        self.assertIn("--python-preference only-managed", lock)

    def test_actual_policies_allow_collector_outputs_and_shared_rendering(self):
        paths = ["data/standings_2026.json", "data/season_h2h_2026.json",
                 "data/circuit_history_2026.json", "circuit_history.py", "history_render.py",
                 "race_tyres.py", "data/spain/race_tyres_verified.json", "passing_history.py",
                 "data/spain/news_highlights.json", "data/spain/nested/source.json",
                 "f1lib.py", "standings.py", "content_spain.py", "test_spain_content.py",
                 "assets_src/fia-spain-example-p2.png"]
        self.assertEqual(preflight.validate(paths, 2000, preflight.policies()), [])

    def test_recursive_glob_does_not_cover_root_json(self):
        self.assertFalse(preflight.matches("data/standings_2026.json", "data/**/*.json"))
        self.assertTrue(preflight.matches("data/standings_2026.json", "data/*.json"))
        self.assertFalse(preflight.matches("data/spain/news.json", "data/*.json"))
        self.assertFalse(preflight.matches("data/a.json", "data/?.json"))

    def test_workflow_permissions_remain_out_of_editorial_scope(self):
        paths = [".github/workflows/deploy.yml", "SKILL.md", "requirements.txt",
                 "unrelated.py", "data/secret.txt"]
        errors = preflight.validate(paths, 2000, preflight.policies())
        self.assertEqual(len(errors), 2)
        for path in paths:
            self.assertTrue(all(path in error for error in errors))

    def test_patch_limits(self):
        self.assertEqual(preflight.validate(["content_spain.py"], 10 * 1024**2,
                                            preflight.policies()), [])
        self.assertEqual(len(preflight.validate(["content_spain.py"], 10 * 1024**2 + 1,
                                                preflight.policies())), 2)
        self.assertTrue(preflight.validate([f"data/{i}.json" for i in range(101)], 1,
                                          preflight.policies()))

    def test_snapshot_includes_all_changes_without_touching_real_index(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            env = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_COMMITTER_NAME="Test",
                       GIT_AUTHOR_EMAIL="test@example.com", GIT_COMMITTER_EMAIL="test@example.com")

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, env=env)

            git("init", "-q")
            (root / "content_spain.py").write_text("original\n")
            git("add", ".")
            git("commit", "-qm", "base")
            base = git("rev-parse", "HEAD").decode().strip()
            (root / "content_spain.py").write_text("committed\n")
            git("commit", "-qam", "change")
            (root / "content_spain.py").write_text("staged\n")
            git("add", ".")
            before = (root / ".git/index").read_bytes()
            (root / "content_spain.py").write_text("working\n")
            (root / "new.json").write_text("{}\n")
            paths, size = preflight.snapshot(base, root)
            self.assertEqual(set(paths), {"content_spain.py", "new.json"})
            self.assertGreater(size, 0)
            self.assertEqual((root / ".git/index").read_bytes(), before)
            with self.assertRaisesRegex(ValueError, "not clean"):
                preflight.committed_patch(base, root)
            git("add", ".")
            git("commit", "-qm", "final edits")
            paths, size = preflight.committed_patch(base, root)
            patch = git("format-patch", f"{base}..HEAD", "--stdout")
            self.assertEqual(size, len(patch) + len(f"X-GH-AW-Base-Commit: {base}\n"))
            self.assertEqual(set(paths), {"content_spain.py", "new.json"})
            (root / "new.json").unlink()
            git("commit", "-qam", "remove new file")
            paths, _ = preflight.committed_patch(base, root)
            self.assertIn("new.json", paths)


if __name__ == "__main__":
    unittest.main()
