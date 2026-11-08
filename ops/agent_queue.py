"""Durable operator jobs, consumed only while holding the watchdog writer lock."""
import contextlib
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import tempfile
import uuid

RUN_ID = re.compile(r"\d{8}T\d{6}Z")
JOB_ID = re.compile(r"[0-9a-f]{32}")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".write-")
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(json.dumps(value, indent=2) + "\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextlib.contextmanager
def locked(state):
    state.mkdir(parents=True, exist_ok=True)
    with (state / "queue.lock").open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def jobs(state):
    directory = state / "tasks"
    if not directory.exists():
        return []
    records = [json.loads(p.read_text()) for p in directory.glob("*.json")
               if JOB_ID.fullmatch(p.stem) and not p.is_symlink()]
    return sorted(records, key=lambda record: record["created_at"])


def enqueue(state, prompt, mode="publish", title="", resume_run=None):
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt.encode()) > 16384:
        raise ValueError("A prompt of 1-16384 bytes is required")
    if mode not in ("publish", "read_only"):
        raise ValueError("Mode must be publish or read_only")
    if not isinstance(title, str) or len(title) > 160:
        raise ValueError("Title must be at most 160 characters")
    if resume_run is not None:
        if not isinstance(resume_run, str) or not RUN_ID.fullmatch(resume_run):
            raise ValueError("Invalid conversation run")
        if not (state / "runs" / resume_run).is_dir():
            raise ValueError("Conversation run does not exist")
    with locked(state):
        if sum(job["status"] in ("queued", "running") for job in jobs(state)) >= 25:
            raise ValueError("Queue is full (25 outstanding jobs)")
        job = {"id": uuid.uuid4().hex, "title": title.strip() or prompt.strip().splitlines()[0][:100],
               "prompt": prompt.strip(), "mode": mode, "resume_run": resume_run,
               "status": "queued", "created_at": now()}
        save(state / "tasks" / (job["id"] + ".json"), job)
        return job


def update(state, identity, **values):
    if not isinstance(identity, str) or not JOB_ID.fullmatch(identity):
        raise ValueError("Invalid task ID")
    with locked(state):
        path = state / "tasks" / (identity + ".json")
        job = json.loads(path.read_text())
        job.update(values, updated_at=now())
        save(path, job)
        return job


def cancel(state, identity):
    if not isinstance(identity, str) or not JOB_ID.fullmatch(identity):
        raise ValueError("Invalid task ID")
    with locked(state):
        path = state / "tasks" / (identity + ".json")
        job = json.loads(path.read_text())
        if job["status"] != "queued":
            raise ValueError("Only queued jobs can be cancelled; use Stop for the active agent")
        job.update(status="cancelled", finished_at=now())
        save(path, job)
        return job


def claim(state, run_id):
    # Caller holds run.lock: any prior running task no longer has a writer.
    with locked(state):
        records = jobs(state)
        for job in records:
            if job["status"] == "running":
                job.update(status="interrupted", finished_at=now(),
                           error="Worker ended without finalizing this task; inspect its run before retrying")
                save(state / "tasks" / (job["id"] + ".json"), job)
        for job in records:
            if job["status"] == "queued" and job.get("not_before", "") <= now():
                job.update(status="running", run_id=run_id, started_at=now())
                save(state / "tasks" / (job["id"] + ".json"), job)
                return job
    return None


def recover(state):
    """Reconcile killed workers without automatically retrying unfinished edits."""
    state.mkdir(parents=True, exist_ok=True)
    with (state / "run.lock").open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        with locked(state):
            for job in jobs(state):
                if job["status"] != "running":
                    continue
                path = state / "runs" / job["run_id"] / "status.json"
                record = json.loads(path.read_text()) if path.exists() else {}
                finished = record.get("finished_at") and record.get("task_id") == job["id"]
                job.update(status=record["status"] if finished else "interrupted",
                           finished_at=record.get("finished_at") if finished else now(),
                           summary=record.get("summary") if finished else None,
                           error=record.get("error") if finished else
                           "Worker stopped without finalizing; inspect retained edits before retrying")
                save(state / "tasks" / (job["id"] + ".json"), job)


def resolve_runs(state, completed_run, report, mode):
    """Propagate explicit, verified completion without inferring task success."""
    if report.get("status") != "fixed" or mode != "PUBLISH":
        return []
    identities = report.get("resolved_runs", [])
    if not isinstance(identities, list) or any(
            not isinstance(identity, str) or not RUN_ID.fullmatch(identity)
            for identity in identities):
        raise ValueError("resolved_runs must list valid run IDs")
    if identities and (not isinstance(report.get("resolution_basis"), str)
                       or not report["resolution_basis"].strip()):
        raise ValueError("resolved_runs requires verified resolution_basis")
    resolved = []
    with locked(state):
        records = []
        for identity in dict.fromkeys(identities):
            if identity == completed_run:
                continue
            path = state / "runs" / identity
            status_path = path / "status.json"
            if not status_path.is_file() or path.is_symlink():
                raise ValueError(f"Cannot resolve unknown run {identity}")
            status = json.loads(status_path.read_text())
            if not status.get("finished_at") or status.get("status") == "running":
                raise ValueError(f"Cannot resolve active run {identity}")
            records.append((identity, path, status_path, status))
        for identity, path, status_path, status in records:
            evidence = {"resolved_at": now(), "resolved_by": completed_run,
                        "basis": report["resolution_basis"],
                        "sources": report.get("sources", []), "commit": report.get("commit")}
            save(path / "resolution.json", evidence)
            status.setdefault("previous_status", status["status"])
            if status.get("error"):
                status.setdefault("previous_error", status["error"])
            status.update(status="fixed", resolution=evidence, error=None,
                          summary=f"Resolved by {completed_run}: {report['resolution_basis']}")
            save(status_path, status)
            for task in jobs(state):
                if task.get("run_id") != identity or task["status"] in (
                        "queued", "running", "cancelled", "fixed"):
                    continue
                task.update(status="fixed", resolution=evidence, error=None,
                            summary=status["summary"], updated_at=now())
                save(state / "tasks" / (task["id"] + ".json"), task)
            resolved.append(identity)
    return resolved
