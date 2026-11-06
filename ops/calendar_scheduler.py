"""One-minute deterministic clock; only dispatch when calendar/data evidence requires it."""
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import coverage_health as health
import session_results
from ops import watchdog

STATE = watchdog.STATE
UTC = dt.timezone.utc
LIVE = "https://martinkenk.github.io/f1-commentary/automation-health.json"


def checked(args, timeout=60):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"{args[0]} {args[1]} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def api(endpoint, *args):
    return json.loads(checked(["gh", "api", endpoint, *args]) or "{}")


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "f1-calendar-watchdog",
                                                 "Cache-Control": "no-cache"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def jobs(gps, now, records=None):
    """Recompute deadlines from the calendar every tick, including after timetable revisions."""
    for ctx in gps:
        race = session_results.session_start(ctx, "Race")
        if race is None or now < race - dt.timedelta(days=10):
            continue
        recent = now <= race + dt.timedelta(days=2)
        for label, endpoint in session_results.f1lib.RESULT_SESSIONS:
            start = session_results.session_start(ctx, label)
            if start is None:
                continue
            end = health.session_end(ctx, label)
            identity = f"{ctx['year']}/{ctx['dir']}/{endpoint}/{start.isoformat()}"
            if recent and label != "Starting Grid":
                yield {"key": identity + "/pre", "kind": "pre", "ctx": ctx, "label": label,
                       "due": start - dt.timedelta(minutes=45),
                       "deadline": start - dt.timedelta(minutes=30), "start": start}
            key = identity + "/results"
            if not recent and (key not in (records or {}) or records[key].get("status") == "done"):
                continue
            # Race duration varies substantially by venue. Cover short dry races
            # without declaring a delayed/red-flagged race finished.
            lead = 60 if label == "Race" else 0 if label == "Starting Grid" else 10
            yield {"key": key, "kind": "results", "ctx": ctx, "label": label,
                   "due": end - dt.timedelta(minutes=lead),
                   "deadline": end + dt.timedelta(minutes=15), "start": start, "url":
                       session_results.source_url(ctx, endpoint)}


def live_satisfies(job, item, live):
    if live is None:
        return False
    if job["kind"] == "pre":
        collected = live.get("collection", {})
        return (live.get("collection_gp", "") in ("", job["ctx"]["dir"])
                and job["due"] <= health.timestamp(live["generated_at"]) < job["start"]
                and collected.get("enrichment") == "success"
                and collected.get("calendar") == "success"
                and collected.get("fia_media") == "success"
                and collected.get("race_tyres") == "success")
    evidence = live.get("events", {}).get(job["ctx"]["dir"], {}).get("sessions", {}).get(job["label"], {})
    return bool(item.get("digest") and evidence.get("digest") == item["digest"]
                and not evidence.get("retained"))


def poll_result(job):
    request = urllib.request.Request(job["url"], headers={"User-Agent": session_results.f1lib.UA})
    with urllib.request.urlopen(request, timeout=25) as response:
        if response.url != job["url"]:
            raise ValueError(f"Unexpected classification redirect: {response.url}")
        headers, rows = session_results.parse_table(response.read().decode("utf-8"))
    return health.digest(headers, rows)


def reconcile_request(state, runs, live, now):
    request = state.get("request")
    if not request:
        return False
    matching = [run for run in runs if run.get("display_title") == request["title"]]
    if matching:
        run = max(matching, key=lambda row: row["id"])
        request["run_id"] = run["id"]
        request["url"] = run["html_url"]
        if run["status"] != "completed":
            if now - health.timestamp(request["at"]) > dt.timedelta(minutes=20):
                state["errors"].append(f"Publication queue/run overdue: {run['html_url']}")
            return True
        if run["conclusion"] != "success":
            state["errors"].append(f"Publication failed ({run['conclusion']}): {run['html_url']}")
        elif live is None or health.timestamp(live["generated_at"]) < health.timestamp(request["at"]):
            state["errors"].append(f"Successful deployment not yet visible live: {run['html_url']}")
            if now - health.timestamp(request["at"]) < dt.timedelta(minutes=20):
                return True
        state["last_request"] = request
        state.pop("request")
        state["retry_after"] = (now + dt.timedelta(minutes=2)).isoformat()
        return False
    # Persist before dispatch: recover an accepted request even if the process died before the reply.
    if now - health.timestamp(request["at"]) < dt.timedelta(minutes=5):
        return True
    state["errors"].append(f"Dispatch never appeared in Actions: {request['title']}")
    state.pop("request")
    return False


def dispatch(state, mode, gp, now):
    key = now.strftime("%Y%m%dT%H%M%SZ")
    state["request"] = {"at": now.isoformat(), "title": f"Calendar refresh {key}",
                        "mode": mode, "gp": gp}
    watchdog.write_json(STATE / "scheduler.json", state)
    checked(["gh", "workflow", "run", "deploy.yml", "--repo", watchdog.REPOSITORY,
             "--ref", "main", "-f", f"refresh={mode}", "-f", f"gp={gp}",
             "-f", f"refresh_key={key}"])


def heartbeat(state, preferences, now):
    """Update an operator issue; an independent GitHub clock checks this timestamp."""
    number = preferences.get("health_issue")
    if not number:
        raise ValueError("preferences.json must name the operator's health_issue")
    if (state.get("heartbeat_at") and now - health.timestamp(state["heartbeat_at"])
            < dt.timedelta(minutes=30) and state.get("alert_signature") == state["errors"]):
        return
    payload = {"heartbeat_at": now.isoformat(), "errors": state["errors"],
               "pending": state.get("pending", []), "request": state.get("request"),
               "next": state.get("next", []),
               "agent": state.get("agent"), "live_generated_at": state.get("live_generated_at")}
    body = ("Calendar scheduler health. Updated automatically; stale heartbeat is a failure, "
            "not a healthy idle state.\n\n```json\n" + json.dumps(payload, indent=2) + "\n```\n")
    endpoint = f"repos/{watchdog.REPOSITORY}/issues/{number}"
    api(endpoint, "--method", "PATCH", "-f", f"body={body}")
    if state["errors"] and state.get("alert_signature") != state["errors"]:
        api(endpoint + "/comments", "--method", "POST", "-f",
            "body=Automation needs attention:\n\n" + "\n".join(f"- {e}" for e in state["errors"]))
    state["alert_signature"] = list(state["errors"])
    state["heartbeat_at"] = now.isoformat()


def tick(now=None):
    now = now or dt.datetime.now(UTC)
    state = health.read(STATE / "scheduler.json")
    state.update(checked_at=now.isoformat(), errors=[])
    preferences = health.read(STATE / "preferences.json")
    try:
        # The clock has its own checkout: agent edits can never change the running scheduler.
        if checked(["git", "status", "--porcelain"]):
            raise RuntimeError("Scheduler checkout is dirty; preserving it rather than overwriting")
        checked(["git", "fetch", "--quiet", "origin", "main"], timeout=120)
        checked(["git", "merge", "--ff-only", "origin/main"])
        import build
        gps = build.season_gps()
        try:
            live = fetch_json(LIVE + f"?t={now.strftime('%Y%m%d%H%M')}")
        except (OSError, ValueError) as error:
            live = None
            state["errors"].append(f"Live publication evidence unavailable: {error}")
        state["live_generated_at"] = live["generated_at"] if live else None
        runs = api(f"repos/{watchdog.REPOSITORY}/actions/workflows/deploy.yml/runs?per_page=30")["workflow_runs"]
        busy = reconcile_request(state, runs, live, now)
        busy |= any(run["status"] in watchdog.ACTIVE for run in runs)
        due, pending = [], []
        records = state.setdefault("jobs", {})
        planned = list(jobs(gps, now, records))
        upcoming = sorted((job for job in planned if job["due"] > now),
                          key=lambda job: job["due"])
        state["next"] = [{"gp": job["ctx"]["dir"], "session": job["label"],
                          "kind": job["kind"], "due": job["due"].isoformat(),
                          "deadline": job["deadline"].isoformat()} for job in upcoming[:6]]
        for job in planned:
            if now < job["due"]:
                continue
            item = records.setdefault(job["key"], {})
            if (job["kind"] == "pre" and now >= job["start"]
                    and item.get("status") != "done" and not live_satisfies(job, item, live)):
                # Restart catch-up records a missed refresh, never publishes an old pre-session job.
                item.update(status="missed", error="No completed pre-session refresh recorded")
            if item.get("status") == "missed":
                if now <= job["start"] + dt.timedelta(hours=2):
                    state["errors"].append(f"{job['ctx']['dir']} {job['label']}: missed pre-session refresh")
                continue
            if item.get("status") == "done":
                if item.get("late") and now <= job["start"] + dt.timedelta(hours=2):
                    state["errors"].append(f"{job['ctx']['dir']} {job['label']}: pre-session deadline missed")
                continue
            if job["kind"] == "results":
                interval = 2 if now < job["deadline"] + dt.timedelta(hours=6) else 15
                if not item.get("polled_at") or now - health.timestamp(item["polled_at"]) >= dt.timedelta(minutes=interval):
                    item["polled_at"] = now.isoformat()
                    try:
                        item["digest"] = poll_result(job)
                        item.pop("error", None)
                    except (OSError, ValueError) as error:
                        item["error"] = str(error)
                if not item.get("digest"):
                    pending.append({"gp": job["ctx"]["dir"], "session": job["label"],
                                    "kind": "results", "deadline": job["deadline"].isoformat(),
                                    "error": item.get("error")})
                    if now >= job["deadline"]:
                        state["errors"].append(f"{job['ctx']['dir']} {job['label']}: official classification overdue")
                    continue
            if live_satisfies(job, item, live):
                item.update(status="done", published_at=live["generated_at"])
                if job["kind"] == "pre" and health.timestamp(live["generated_at"]) > job["deadline"]:
                    item["late"] = True
                    state["errors"].append(f"{job['ctx']['dir']} {job['label']}: pre-session deadline missed")
                continue
            pending.append({"gp": job["ctx"]["dir"], "session": job["label"],
                            "kind": job["kind"], "deadline": job["deadline"].isoformat()})
            due.append(job)
            if now >= job["deadline"]:
                state["errors"].append(f"{job['ctx']['dir']} {job['label']}: {job['kind']} publication overdue")
        state["pending"] = pending
        findings = live.get("findings", []) if live else [
            {"gp": "site", "kind": "publication", "message": "Live health endpoint unavailable"}]
        state["coverage_findings"] = findings
        if findings:
            state["errors"].append(f"{len(findings)} live coverage findings need retry/review (see automation-health.json)")
        audit_only = preferences.get("audit_only", False)
        if audit_only:
            state["errors"].append("Operator read-only mode: dispatch and repair disabled")
        retry_ready = not state.get("retry_after") or now >= health.timestamp(state["retry_after"])
        # Re-run the deterministic collectors before escalating stale source data to an agent.
        refresh_due = (findings and (not state.get("last_coverage_refresh") or
                       now - health.timestamp(state["last_coverage_refresh"]) >= dt.timedelta(hours=1)))
        if not busy and not audit_only and retry_ready and (due or refresh_due):
            chosen = min(due, key=lambda job: (job["kind"] != "pre", job["deadline"])) if due else None
            dispatch(state, "pre-session" if not chosen or chosen["kind"] == "pre" else "results",
                     chosen["ctx"]["dir"] if chosen else "", now)
            state["last_coverage_refresh"] = now.isoformat()
            busy = True
        latest = health.read(STATE / "latest.json")
        state["agent"] = {key: latest.get(key) for key in ("status", "finished_at", "summary", "error")}
        if latest.get("status") in ("failed", "blocked", "agent_failed", "timed_out"):
            state["errors"].append(f"Last AI repair {latest['status']}: "
                                   f"{latest.get('summary') or latest.get('error', 'inspect agent log')}")
        blocked = preferences.get("agent_blocked_reason")
        if blocked:
            state["errors"].append(f"AI repair blocked: {blocked}")
        else:
            imminent = any(job["kind"] == "pre" and job["due"] - dt.timedelta(minutes=45) <= now < job["due"]
                           for job in planned)
            last = state.get("agent_requested_at")
            cooldown = not last or now - health.timestamp(last) >= dt.timedelta(hours=1)
            if (not busy and not audit_only and cooldown and (imminent or findings)
                    and checked(["systemctl", "--user", "show", "f1-watchdog.service",
                                 "--property=ActiveState", "--value"]) not in ("active", "activating")):
                watchdog.write_json(STATE / "repair-request.json",
                                    {"requested_at": now.isoformat(), "findings": findings,
                                     "pre_session": imminent, "pending": pending})
                checked(["systemctl", "--user", "start", "--no-block", "f1-watchdog.service"])
                state["agent_requested_at"] = now.isoformat()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as error:
        state["errors"].append(str(error))
    finally:
        try:
            heartbeat(state, preferences, now)
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
            state["errors"].append(f"Health issue update failed: {error}")
        watchdog.write_json(STATE / "scheduler.json", state)
    print(json.dumps({key: state.get(key) for key in ("checked_at", "errors", "pending", "request")}, indent=2))
    return int(bool(state["errors"]))


def main():
    os.umask(0o077)
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE / "scheduler.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        return tick()


if __name__ == "__main__":
    raise SystemExit(main())
