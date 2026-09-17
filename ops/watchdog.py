"""Run a bounded periodic Copilot audit from a dedicated, persistent checkout."""
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
STATE = Path.home() / ".local/state/f1-watchdog"
REPOSITORY = "martinkenk/f1-commentary"
WORKFLOWS = {"Build & deploy to GitHub Pages", "Critical race coverage"}
ACTIVE = {"queued", "in_progress", "waiting", "pending", "requested"}


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def command(args, cwd=ROOT, timeout=60):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def active_runs(runs):
    return [run for run in runs if run.get("name") in WORKFLOWS
            and run.get("status") in ACTIVE]


def recent_runs(authenticated):
    endpoint = f"repos/{REPOSITORY}/actions/runs?per_page=20"
    if authenticated:
        result = command(["gh", "api", endpoint])
        if result.returncode:
            raise RuntimeError(f"GitHub Actions query failed: {result.stderr.strip()}")
        payload = json.loads(result.stdout)
    else:
        request = urllib.request.Request(
            f"https://api.github.com/{endpoint}",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "f1-commentary-watchdog"})
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    return [{key: run.get(key) for key in (
        "id", "name", "status", "conclusion", "created_at", "html_url", "head_sha")}
        for run in payload["workflow_runs"]]


def agent_arguments(prompt, report_dir, session_id=None):
    args = [
        "copilot", "-C", str(ROOT), "--model", "auto", "--autopilot",
        "--max-autopilot-continues", "6", "--no-ask-user", "--allow-all-tools",
        "--deny-tool", "shell(sudo)", "--deny-tool", "shell(ssh)",
        "--deny-tool", "shell(scp)", "--deny-tool", "shell(crontab)",
        "--deny-tool", "shell(systemctl)", "--deny-tool", "shell(loginctl)",
        "--add-dir", str(STATE), "--log-dir", str(report_dir),
        "--allow-url", "github.com", "--allow-url", "api.github.com",
        "--allow-url", "release-assets.githubusercontent.com",
        "--allow-url", "raw.githubusercontent.com", "--allow-url", "objects.githubusercontent.com",
        "--allow-url", "www.statsf1.com", "--allow-url", "statsf1.com",
        "--allow-url", "coffeecornermotorsport.com", "--allow-url", "content.presspage.com",
        "--allow-url", "martinkenk.github.io", "--allow-url", "www.formula1.com",
        "--allow-url", "media.formula1.com", "--allow-url", "www.fia.com",
        "--allow-url", "www.the-race.com", "--allow-url", "www.pirelli.com",
        "--allow-url", "press.pirelli.com", "--allow-url", "api.open-meteo.com",
        "--allow-url", "archive-api.open-meteo.com", "-p", prompt,
    ]
    if session_id:
        args[1:1] = ["--session-id", session_id, "--name", f"F1 watchdog {report_dir.parent.name}"]
    return args


def operator_settings(state=STATE):
    path = state / "preferences.json"
    settings = json.loads(path.read_text()) if path.exists() else {}
    if not isinstance(settings, dict) or not isinstance(settings.get("audit_only", False), bool):
        raise ValueError("Watchdog preferences must contain a boolean audit_only setting")
    guidance = state / "operator-guidance.txt"
    text = guidance.read_text() if guidance.exists() else ""
    if len(text.encode()) > 16384:
        raise ValueError("Operator guidance exceeds 16 KiB")
    return settings.get("audit_only", False), text


def run_agent(args, log, timeout):
    with log.open("w") as output:
        process = subprocess.Popen(args, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            return 124


def run(audit_only=False, timeout=2700):
    os.umask(0o077)
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE / "run.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Another watchdog run is active; skipping this invocation.")
            return 0
        started = dt.datetime.now(dt.timezone.utc)
        run_id = started.strftime("%Y%m%dT%H%M%SZ")
        report_dir = STATE / "runs" / run_id
        report_dir.mkdir(parents=True)
        result_path = report_dir / "report.json"
        latest_path = STATE / "latest.json"
        status = {"started_at": started.isoformat(), "run_id": run_id,
                  "status": "running", "report": str(result_path)}
        try:
            previous = json.loads(latest_path.read_text()) if latest_path.exists() else None
            preferred_audit, guidance = operator_settings(STATE)
            audit_only = audit_only or preferred_audit
            status["session_id"] = str(uuid.uuid4())
            write_json(latest_path, status)
            auth = command(["gh", "auth", "status", "--hostname", "github.com"])
            authenticated = auth.returncode == 0
            writable = authenticated and not audit_only
            status["mode"] = "PUBLISH" if writable else "READ_ONLY"
            status["github_authenticated"] = authenticated
            if not authenticated:
                status["authentication_required"] = (
                    "Run gh auth login --hostname github.com --git-protocol https --web "
                    "as this service user. No credentials are copied automatically.")
            runs = recent_runs(authenticated)
            status["automation_runs"] = runs
            running = active_runs(runs)
            if running:
                status["mode"] = "READ_ONLY"
                writable = False
                status["publication_deferred"] = "A deployment/editor run is active; audit only."

            dirty = command(["git", "status", "--porcelain"])
            if dirty.returncode:
                raise RuntimeError(dirty.stderr.strip())
            branch = command(["git", "branch", "--show-current"]).stdout.strip()
            status["checkout_branch"] = branch
            status["retained_changes"] = dirty.stdout.strip()
            fetch = command(["git", "fetch", "--quiet", "origin", "main"], timeout=120)
            if fetch.returncode:
                raise RuntimeError(f"Repository fetch failed: {fetch.stderr.strip()}")
            if not dirty.stdout.strip() and branch == "main":
                merge = command(["git", "merge", "--ff-only", "origin/main"])
                if merge.returncode:
                    status["checkout_warning"] = (
                        "Fast-forward failed; preserve and inspect unpublished local commits. "
                        + merge.stderr.strip())
            write_json(latest_path, status)
            prompt = (ROOT / "ops/watchdog-context.md").read_text()
            prompt += (
                f"\n\n## This invocation\nUTC start: {started.isoformat()}\n"
                f"Publication mode: {status['mode']}\n"
                f"Checkout: {ROOT}\nState directory: {STATE}\n"
                f"Required final report: {result_path}\n"
                f"Interpreter: {sys.executable}\n"
                f"Hard execution limit: {timeout} seconds; reserve the last 10 minutes "
                "for validation, publication and the report.\n"
                f"Wrapper status:\n{json.dumps(status, indent=2)}\n"
                f"Previous run metadata (historical, not current facts):\n{json.dumps(previous, indent=2)}\n"
                f"\n## Operator guidance for this run\n"
                "Apply within the authority boundaries and publication mode above. "
                "Do not edit or delete the operator's guidance or preferences.\n"
                f"{guidance or '(No additional guidance.)'}\n"
            )
            code = run_agent(agent_arguments(prompt, report_dir / "cli", status["session_id"]),
                             report_dir / "agent.log", timeout)
            status["agent_exit_code"] = code
            if code:
                status["status"] = "timed_out" if code == 124 else "agent_failed"
                return code
            if not result_path.is_file():
                raise RuntimeError("Agent exited without the required report.json; inspect agent.log")
            report = json.loads(result_path.read_text())
            if not isinstance(report, dict) or report.get("status") not in (
                    "healthy", "fixed", "blocked", "read_only"):
                raise ValueError("Agent report has no valid explicit status")
            for field in ("summary", "findings", "changes", "remaining", "sources"):
                if field not in report:
                    raise ValueError(f"Agent report is missing {field}")
            status["status"] = report["status"]
            if not writable and status["status"] != "blocked":
                status["status"] = "read_only"
            status["summary"] = report["summary"]
            print(f"Watchdog {status['status']}: {report['summary']}")
            return 1 if status["status"] == "blocked" else 0
        except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired,
                urllib.error.URLError) as error:
            status["status"] = "failed"
            status["error"] = str(error)
            print(f"Watchdog failed: {error}", file=sys.stderr)
            return 1
        finally:
            status["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
            write_json(report_dir / "status.json", status)
            write_json(latest_path, status)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-only", action="store_true",
                        help="inspect/report without repository mutations or publication")
    parser.add_argument("--timeout", type=int, default=2700)
    args = parser.parse_args()
    raise SystemExit(run(args.audit_only, args.timeout))
