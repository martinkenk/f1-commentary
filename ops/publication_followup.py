"""Finish deployment waits using independent live evidence, without paid agents."""
import json
import re
import urllib.request

try:
    from . import agent_queue
except ImportError:
    import agent_queue

SHA = re.compile(r"[0-9a-f]{40}")


def validate_editorial_review(report, gps):
    """Require a complete source and page-level audit record."""
    import build
    if not isinstance(report.get("remaining"), list) or report["remaining"]:
        raise ValueError("Scheduled editorial audit still has outstanding work or lacks a work record")
    expected_pages = {item[0] for item in build.nav("")}
    reviews = report.get("editorial_review")
    if not isinstance(reviews, list):
        raise ValueError("Scheduled editorial audit requires editorial_review evidence")
    by_gp = {item["gp"]: item for item in reviews
             if isinstance(item, dict) and isinstance(item.get("gp"), str)}
    for gp in gps:
        item = by_gp.get(gp)
        if (not item or not isinstance(item.get("pages"), list)
                or not all(isinstance(page, str) for page in item["pages"])
                or not expected_pages.issubset(item["pages"])):
            raise ValueError(f"Scheduled editorial audit lacks all page reviews for {gp}")
        sources = item.get("sources")
        if not isinstance(sources, list) or not sources or not all(
                isinstance(url, str) and url.startswith("https://") for url in sources):
            raise ValueError(f"Scheduled editorial audit lacks HTTPS source evidence for {gp}")


def editorial_completion_error(report, gps):
    if report.get("status") not in ("healthy", "fixed"):
        return "Editorial report does not claim a completed review"
    if not isinstance(gps, list) or not gps:
        return "Editorial review targets are missing"
    try:
        validate_editorial_review(report, gps)
    except ValueError as error:
        return str(error)
    return None


def pending_report(report):
    if report.get("report_origin") == "wrapper_fallback":
        return False
    if report.get("publication_verification_required") and SHA.fullmatch(report.get("commit") or ""):
        return True
    summary = report.get("summary", "").lower()
    return (report.get("status") in ("blocked", "fixed")
            and SHA.fullmatch(report.get("commit") or "") is not None
            and any(word in summary for word in (
                "still building", "still running", "still in progress",
                "remains in progress", "remained in_progress", "deployment remains",
                "deployment is still", "not yet confirmed published",
                "not confirmed live", "not yet verified live", "publication is deferred",
                "publication is not confirmed", "publication is unconfirmed",
                "not yet confirmed live", "not yet published")))


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
        if (not status.get("finished_at") or status.get("publication")
                or status.get("status") not in ("blocked", "waiting_publication", "fixed")):
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
    candidates = waiting(state)
    if not candidates:
        return outcomes
    pushed_commits = set(checked(["git", "rev-list", "origin/main"]).splitlines())
    deployed_commits = set(checked(["git", "rev-list", deployed["head_sha"]]).splitlines()) if deployed else set()
    for path, status, report in candidates:
        commit = report["commit"]
        if commit not in pushed_commits:
            # A report may name an unpublished local commit, absent in the
            # scheduler clone. Preserve it for a safe agent continuation.
            continue
        status.setdefault("previous_status", status["status"])
        status.update(status="waiting_publication", publication_commit=commit)
        agent_queue.save(path / "status.json", status)
        latest_path = state / "latest.json"
        latest = json.loads(latest_path.read_text()) if latest_path.exists() else {}
        if latest.get("run_id") == path.name:
            agent_queue.save(latest_path, status)
        if not deployed:
            continue
        if commit not in deployed_commits:
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
        task = None
        if status.get("task_id"):
            task_id = status["task_id"]
            if not isinstance(task_id, str) or not agent_queue.JOB_ID.fullmatch(task_id):
                raise ValueError("Invalid publication task ID")
            task = json.loads((state / "tasks" / (task_id + ".json")).read_text())
        audit_error = None
        if status.get("kind") == "editorial_audit" or (task and task.get("kind") == "editorial_audit"):
            audit_error = editorial_completion_error(report, task.get("gps") if task else None)
        final_status = "blocked" if audit_error else "fixed"
        summary = f"Published repair {commit[:8]}; deployment and live routes verified automatically."
        if audit_error:
            summary += f" Editorial review remains incomplete: {audit_error}. {report.get('summary', '')}"
        else:
            summary += " Original audit and remaining source limitations are preserved in the report."
        status.update(status=final_status, publication=evidence, summary=summary)
        agent_queue.save(path / "status.json", status)
        if final_status == "fixed" and report.get("resolved_runs"):
            agent_queue.resolve_runs(state, path.name, dict(report, status="fixed"), status.get("mode"))
        latest = json.loads(latest_path.read_text()) if latest_path.exists() else {}
        if latest.get("run_id") == path.name:
            agent_queue.save(latest_path, status)
        if task:
            # Never finish a newer continuation or a job that the operator cancelled.
            if task.get("run_id") == path.name and task["status"] in ("blocked", "waiting_publication", "fixed"):
                agent_queue.update(state, task["id"], status=final_status, summary=status["summary"],
                                   publication=evidence)
        outcomes.append(evidence)
    return outcomes
