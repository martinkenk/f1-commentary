"""Finish deployment waits using independent live evidence, without paid agents."""
import json
import re
import urllib.request

try:
    from . import agent_queue
except ImportError:
    import agent_queue

SHA = re.compile(r"[0-9a-f]{40}")


def pending_report(report):
    if report.get("report_origin") == "wrapper_fallback":
        return False
    summary = report.get("summary", "").lower()
    return (report.get("status") == "blocked"
            and SHA.fullmatch(report.get("commit") or "") is not None
            and any(word in summary for word in (
                "still building", "still running", "still in progress",
                "remains in progress", "remained in_progress", "deployment remains",
                "deployment is still", "not yet confirmed published",
                "not confirmed live", "not yet verified live", "publication is deferred",
                "not yet published")))


def waiting(state, limit=40):
    directory = state / "runs"
    if not directory.exists():
        return []
    result = []
    for path in sorted(directory.iterdir(), reverse=True)[:limit]:
        if not agent_queue.RUN_ID.fullmatch(path.name) or path.is_symlink():
            continue
        status_path, report_path = path / "status.json", path / "report.json"
        if not status_path.exists() or not report_path.exists():
            continue
        status = json.loads(status_path.read_text())
        if not status.get("finished_at") or status.get("status") not in ("blocked", "waiting_publication"):
            continue
        report = json.loads(report_path.read_text())
        if pending_report(report):
            result.append((path, status, report))
    return result


def reconcile(state, runs, live, gps, checked, now):
    """A later successful descendant deployment may also publish an earlier fix."""
    deployed = next((run for run in runs if live and str(run["id"]) == str(live.get("run_id"))
                     and run["status"] == "completed" and run.get("conclusion") == "success"), None)
    outcomes = []
    verified_routes = {}
    for path, status, report in waiting(state):
        commit = report["commit"]
        status.update(status="waiting_publication", publication_commit=commit)
        agent_queue.save(path / "status.json", status)
        latest_path = state / "latest.json"
        latest = json.loads(latest_path.read_text()) if latest_path.exists() else {}
        if latest.get("run_id") == path.name:
            agent_queue.save(latest_path, status)
        if not deployed:
            continue
        ancestor = checked(["git", "merge-base", commit, deployed["head_sha"]])
        if ancestor != commit:
            continue
        changes = checked(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit]).splitlines()
        affected = [ctx for ctx in gps if any(
            name == f"content_{ctx['dir']}.py" or name.startswith(f"data/{ctx['dir']}/")
            for name in changes)]
        if not affected:
            affected = gps[:1]
        routes = []
        for ctx in affected:
            if ctx["dir"] not in verified_routes:
                verified_routes[ctx["dir"]] = []
                # Validate actual rendered routes, not just workflow colour or health HTTP 200.
                for page in ("overview", "news", "powerunit", "notes"):
                    url = f"https://martinkenk.github.io/f1-commentary/{ctx['dir']}/{page}.html"
                    request = urllib.request.Request(url, headers={"User-Agent": "f1-publication-verifier"})
                    with urllib.request.urlopen(request, timeout=15) as response:
                        body = response.read(2 * 1024 * 1024)
                        if response.status != 200 or b"</html>" not in body.lower():
                            raise ValueError(f"Published route failed validation: {url}")
                    verified_routes[ctx["dir"]].append(url)
            routes.extend(verified_routes[ctx["dir"]])
        evidence = {"verified_at": now.isoformat(), "commit": commit,
                    "deployment_commit": deployed["head_sha"], "run_id": deployed["id"],
                    "deployment_url": deployed["html_url"], "routes": routes,
                    "live_generated_at": live["generated_at"],
                    "remaining_live_findings": live.get("findings", [])}
        agent_queue.save(path / "publication.json", evidence)
        status.update(status="fixed", previous_status="blocked", publication=evidence,
                      summary=f"Published repair {commit[:8]}; deployment and live routes verified automatically. "
                              "Original audit and remaining source limitations are preserved in the report.")
        agent_queue.save(path / "status.json", status)
        latest = json.loads(latest_path.read_text()) if latest_path.exists() else {}
        if latest.get("run_id") == path.name:
            agent_queue.save(latest_path, status)
        if status.get("task_id"):
            task_path = state / "tasks" / (status["task_id"] + ".json")
            task = json.loads(task_path.read_text())
            # Never finish a newer continuation or a job that the operator cancelled.
            if task.get("run_id") == path.name and task["status"] in ("blocked", "waiting_publication"):
                agent_queue.update(state, task["id"], status="fixed", summary=status["summary"],
                                   publication=evidence)
        outcomes.append(evidence)
    return outcomes
