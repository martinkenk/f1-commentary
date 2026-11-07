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

try:
    from . import agent_queue
    from . import publication_followup
except ImportError:
    import agent_queue
    import publication_followup

ROOT = Path(__file__).resolve().parents[1]
STATE = Path.home() / ".local/state/f1-watchdog"
REPOSITORY = "martinkenk/f1-commentary"
WORKFLOWS = {"Build & deploy to GitHub Pages", "Critical race coverage"}
WORKFLOW_PATHS = {".github/workflows/deploy.yml", ".github/workflows/critical-race-coverage.lock.yml"}
ACTIVE = {"queued", "in_progress", "waiting", "pending", "requested"}


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def command(args, cwd=ROOT, timeout=60):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def active_runs(runs):
    return [run for run in runs if (run.get("name") in WORKFLOWS or run.get("path") in WORKFLOW_PATHS)
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
        "id", "name", "path", "status", "conclusion", "created_at", "html_url", "head_sha")}
        for run in payload["workflow_runs"]]


def agent_arguments(prompt, report_dir, session_id=None, resume=False):
    args = [
        "copilot", "-C", str(ROOT), "--model", "auto", "--autopilot",
        "--max-autopilot-continues", "6", "--no-ask-user", "--allow-all-tools",
        "--deny-tool", "shell(sudo)", "--deny-tool", "shell(ssh)",
        "--deny-tool", "shell(scp)", "--deny-tool", "shell(crontab)",
        "--deny-tool", "shell(systemctl)", "--deny-tool", "shell(loginctl)",
        "--add-dir", str(STATE), "--log-dir", str(report_dir),
        "--add-dir", sys.prefix,
        "--add-dir", str(Path(sys.executable).resolve().parent),
        "--allow-tool", f"shell({sys.executable}:*)",
        "--allow-url", "github.com", "--allow-url", "api.github.com",
        "--allow-url", "release-assets.githubusercontent.com",
        "--allow-url", "raw.githubusercontent.com", "--allow-url", "objects.githubusercontent.com",
        "--allow-url", "www.statsf1.com", "--allow-url", "statsf1.com",
        "--allow-url", "coffeecornermotorsport.com", "--allow-url", "content.presspage.com",
        "--allow-url", "racingpass.net",
        "--allow-url", "fantasy.formula1.com", "--allow-url", "x.com",
        "--allow-url", "pbs.twimg.com", "--allow-url", "www.threads.com",
        "--allow-url", "martinkenk.github.io", "--allow-url", "www.formula1.com",
        "--allow-url", "media.formula1.com", "--allow-url", "www.fia.com",
        "--allow-url", "www.the-race.com", "--allow-url", "www.pirelli.com",
        "--allow-url", "press.pirelli.com", "--allow-url", "api.open-meteo.com",
        "--allow-url", "archive-api.open-meteo.com", "-p", prompt,
    ]
    if session_id:
        args[1:1] = (["--resume", session_id] if resume else
                     ["--session-id", session_id, "--name", f"F1 watchdog {report_dir.parent.name}"])
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
    with log.open("a") as output:
        process = subprocess.Popen(args, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                pass
            # A CLI can exit before a child command; do not overlap it with finalization.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            return 124


def budget_instructions(started, timeout):
    deadline = started + dt.timedelta(seconds=timeout)
    reserve = min(600, timeout / 3)
    finish_margin = min(120, timeout / 10)
    return (
        f"\n## Wall-clock checkpoints (UTC)\n"
        f"Stop new investigation and edits by {(deadline - dt.timedelta(seconds=reserve)).isoformat()}.\n"
        f"Write the final report and finish by "
        f"{(deadline - dt.timedelta(seconds=finish_margin)).isoformat()}.\n"
        f"Hard process deadline: {deadline.isoformat()}; setup time counts against it.\n"
        "Write a provisional blocked report immediately after initial inspection, then update "
        "it after validation and before any deployment wait. Record retained files, commit "
        "and run URL; do not claim pending publication is live. Check UTC time at each phase "
        "boundary. Do not start a command that cannot finish within the remaining budget. "
        "Never use an unbounded gh run watch: check status with bounded calls, spend at most "
        "two minutes waiting in total, then report pending deployment for a later invocation. "
        "Do not repeat a completed audit or start unrelated work on a resumed conversation.\n"
    )


def finalization_instructions(status, result_path, deadline):
    return (
        "The investigation phase reached its wall-clock limit and its process group was stopped. "
        "This is the single reserved FINALIZATION turn in the SAME conversation, not a new audit. "
        f"Publication mode remains {status['mode']}; all original permission and source boundaries apply. "
        f"Finish before {deadline.isoformat()}. Write the final report to {result_path} now, "
        "then update it only as completion is verified. Inspect git status and the last commands for "
        "interrupted operations; preserve all edits. Do not reread the entire runbook, start new "
        "research, refresh sources, or expand the scope. Finish only already-understood work that "
        "can be validated within this remaining budget. Never skip failing checks to publish. "
        "Recheck active writers and origin/main before any normal push; defer on conflicts. "
        "If a repair was pushed, record its full commit and deployment URL and report publication "
        "as pending unless live evidence is already verified. Do not wait for a deployment: the "
        "calendar verifies publication independently. If validation or safe publication cannot "
        "finish, report blocked with exact retained files, commands/failures and next steps, then exit. "
        "Do not repeat completed work or start another autopilot task after writing the report."
    )


def incomplete_report(status):
    """Keep process failure distinct from verified publication or source success."""
    findings = [status.get("error") or status.get("summary") or "Worker did not finalize a report"]
    commit = None
    retained = status.get("retained_changes", "")
    branch = status.get("checkout_branch", "unknown")
    for args, label in ((["git", "rev-parse", "HEAD"], "commit"),
                        (["git", "status", "--short", "--branch"], "checkout")):
        try:
            result = command(args, timeout=5)
            if result.returncode:
                findings.append(f"Could not capture {label}: git exited {result.returncode}")
            elif label == "commit":
                commit = result.stdout.strip()
            else:
                retained = result.stdout.strip()
        except (OSError, subprocess.TimeoutExpired) as error:
            findings.append(f"Could not capture {label}: {error}")
    return {
        "status": "blocked",
        "summary": "Worker ended without a final report; publication is unverified. "
                   "Inspect retained work before continuing.",
        "findings": findings,
        "changes": [],
        "remaining": [f"Inspect branch {branch}, HEAD {commit or 'unknown'}, and agent.log.",
                      f"Retained checkout state: {retained or 'no changes recorded'}",
                      "Reconcile any pushed commit and deployment; do not reset or retry blindly."],
        "sources": [], "commit": commit, "deployment_url": None, "reviewed_prs": [],
        "report_origin": "wrapper_fallback",
    }


def run(audit_only=False, timeout=2700):
    if timeout <= 0:
        raise ValueError("Watchdog timeout must be positive")
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
        task = None
        try:
            task = agent_queue.claim(STATE, run_id)
            if task:
                status["task_id"] = task["id"]
                status["task_title"] = task["title"]
                audit_only = audit_only or task["mode"] == "read_only"
            previous = json.loads(latest_path.read_text()) if latest_path.exists() else None
            preferred_audit, guidance = operator_settings(STATE)
            preferences = STATE / "preferences.json"
            if preferences.exists():
                blocker = json.loads(preferences.read_text()).get("agent_blocked_reason")
                if blocker:
                    raise RuntimeError(f"Operator agent blocker: {blocker}")
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
            if task and task["mode"] == "publish" and not writable:
                reason = status.get("publication_deferred") or status.get(
                    "authentication_required") or "Operator policy is read-only"
                agent_queue.update(
                    STATE, task["id"], status="queued", error=reason,
                    not_before=(started + dt.timedelta(minutes=5)).isoformat())
                task = None
                status.update(status="waiting", summary=f"Operator job will retry automatically: {reason}")
                return 0
            if task and task.get("resume_run"):
                prior = STATE / "runs" / task["resume_run"]
                record = json.loads((prior / "status.json").read_text())
                session = record.get("session_id")
                if not session:
                    raise ValueError("Selected run has no resumable session ID")
                uuid.UUID(session)
                status["session_id"] = session
                write_json(latest_path, status)
            prompt = (ROOT / "ops/watchdog-context.md").read_text()
            request = STATE / "repair-request.json"
            if request.exists():
                prompt += "\n\n## Deterministic coverage findings\n" + request.read_text()
            prompt += (
                f"\n\n## This invocation\nUTC start: {started.isoformat()}\n"
                f"Publication mode: {status['mode']}\n"
                f"Checkout: {ROOT}\nState directory: {STATE}\n"
                f"Required final report: {result_path}\n"
                "Live health evidence: https://martinkenk.github.io/f1-commentary/automation-health.json "
                "(fetch this URL; no local state-directory copy is supplied).\n"
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
            if task:
                prompt += (
                    "\n## Explicit operator task (browser control room)\n"
                    "Complete this task instead of a general coverage sweep. Relevant website "
                    "features, tests and repository automation improvements are authorized, "
                    "within the publication mode and authority boundaries above. Validate "
                    "changes, publish only when permitted, verify live results and write the "
                    "required report for THIS invocation. Do not change host services, "
                    "credentials, web authentication or your own permissions. Do not install "
                    "operator-service updates yourself; report when installation is required.\n"
                    f"Task: {task['title']}\n{task['prompt']}\n")
            prompt += budget_instructions(started, timeout)
            remaining = timeout - (dt.datetime.now(dt.timezone.utc) - started).total_seconds()
            if remaining <= 0:
                status["status"] = "timed_out"
                status["error"] = "Execution budget exhausted during setup; agent was not started"
                return 124
            reserve = min(600, timeout / 3)
            # Leave room to stop the first process group and finish before the hard deadline.
            finalize = reserve >= 60 and remaining > reserve
            code = run_agent(agent_arguments(prompt, report_dir / "cli", status["session_id"],
                                            resume=bool(task and task.get("resume_run"))),
                             report_dir / "agent.log", remaining - reserve if finalize else remaining)
            if code == 124 and finalize:
                status["investigation_exit_code"] = code
                checkpoint = incomplete_report(status)
                write_json(report_dir / "interruption.json", checkpoint)
                if result_path.exists():
                    (report_dir / "report-before-finalization.json").write_bytes(result_path.read_bytes())
                resumed_at = dt.datetime.now(dt.timezone.utc)
                remaining = timeout - (resumed_at - started).total_seconds() - 20
                if remaining > 0:
                    status.update(phase="finalizing", finalization_started_at=resumed_at.isoformat())
                    write_json(latest_path, status)
                    deadline = started + dt.timedelta(seconds=timeout - 20)
                    code = run_agent(
                        agent_arguments(finalization_instructions(status, result_path, deadline),
                                        report_dir / "cli", status["session_id"], resume=True),
                        report_dir / "agent.log", remaining)
            status["agent_exit_code"] = code
            if code:
                status["status"] = "timed_out" if code == 124 else "agent_failed"
                status["error"] = f"Copilot exited {code}; inspect this run's agent output"
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
            if writable and publication_followup.pending_report(report):
                status.update(status="waiting_publication", publication_commit=report["commit"],
                              summary="Repair pushed; automatic calendar verification will finish publication. "
                                      + report["summary"])
            print(f"Watchdog {status['status']}: {report['summary']}")
            return 1 if status["status"] == "blocked" else 0
        except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired,
                urllib.error.URLError) as error:
            status["status"] = "failed"
            status["error"] = str(error)
            print(f"Watchdog failed: {error}", file=sys.stderr)
            return 1
        finally:
            if status["status"] in ("timed_out", "agent_failed", "failed"):
                checkpoint = incomplete_report(status)
                write_json(report_dir / "interruption.json", checkpoint)
                status.setdefault("summary", checkpoint["summary"])
            if not result_path.exists():
                report = incomplete_report(status)
                write_json(result_path, report)
                status.setdefault("summary", report["summary"])
            status["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
            write_json(report_dir / "status.json", status)
            write_json(latest_path, status)
            if task:
                if (status["status"] == "blocked" and status.get("mode") == "PUBLISH"
                        and "publication" in status.get("summary", "").lower()
                        and "defer" in status.get("summary", "").lower()
                        and task.get("automatic_retries", 0) < 3):
                    agent_queue.update(
                        STATE, task["id"], status="queued", resume_run=run_id,
                        automatic_retries=task.get("automatic_retries", 0) + 1,
                        not_before=(dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5)).isoformat(),
                        summary=status.get("summary"), error="Temporary publication conflict; automatic continuation queued")
                    task = None
            if task:
                agent_queue.update(STATE, task["id"], status=status["status"],
                                   finished_at=status["finished_at"],
                                   summary=status.get("summary"), error=status.get("error"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-only", action="store_true",
                        help="inspect/report without repository mutations or publication")
    parser.add_argument("--timeout", type=int, default=2700)
    args = parser.parse_args()
    raise SystemExit(run(args.audit_only, args.timeout))
