"""Operator-facing explanations and narrowly scoped recovery instructions."""


def explain(status, report=None):
    report = report or {}
    value = status.get("status", "")
    text = " ".join(str(status.get(key) or "") for key in (
        "summary", "error", "authentication_required", "publication_deferred")).lower()
    if value in ("fixed", "healthy", "read_only", "cancelled"):
        return None
    if value == "running":
        return {"kind": "running", "cause": "The agent is still working.",
                "next_step": "No intervention needed. Reports and output refresh automatically.",
                "automatic": True, "action": None}
    if value in ("waiting", "waiting_publication") or "operator job remains queued" in text:
        publication = value == "waiting_publication"
        return {"kind": value, "cause": "The repair is pushed but live publication is not yet verified."
                if publication else "Another publisher is using the repository.",
                "next_step": "The calendar will verify the successful deployment and finish this run."
                if publication else "The existing queued job will start when the publisher is idle.",
                "automatic": True, "action": None}
    if any(word in text for word in ("authentication", "auth login", "not logged", "credentials")):
        return {"kind": "authentication", "cause": "The service user is not authenticated.",
                "next_step": "Open the browser terminal as the service user. Run "
                             "`gh auth login --hostname github.com`, `gh auth setup-git`, and "
                             "`copilot login --device-code` for the missing login. "
                             "Credentials are never copied or requested by this UI.",
                "automatic": False, "action": "terminal", "label": "Open login terminal"}
    if any(word in text for word in ("permission denial", "permission denied", "approval", "agent blocker")):
        return {"kind": "permission", "cause": "A permission or operator approval boundary stopped the run.",
                "next_step": "Review the exact denied operation in the output using the browser terminal. "
                             "Resolve only the required approval; do not grant unrestricted access. "
                             "Verify an unattended smoke run before clearing a blocker.",
                "automatic": False, "action": "terminal", "label": "Review approval in terminal"}
    if any(word in text for word in ("access-restricted", "freewall", "upstream outage", "source unavailable")):
        return {"kind": "source_access", "cause": "The source is unavailable or access-restricted.",
                "next_step": "Automatic collection retries continue while last-good data and the warning "
                             "remain visible. An agent cannot bypass access restrictions or invent missing "
                             "evidence; recovery depends on source availability.",
                "automatic": True, "action": None}
    if value in ("timed_out", "agent_failed", "failed", "interrupted", "blocked"):
        return {"kind": "retained_work", "cause": status.get("error") or status.get("summary")
                or report.get("summary") or "The agent did not finish its task.",
                "next_step": "Resume with a focused recovery instruction: inspect retained edits and the "
                             "original report, verify any deployment first, and finish only remaining work. "
                             "No reset, duplicate publication, or repeated full audit.",
                "automatic": False, "action": "recover", "label": "Resume safely",
                "confirmation": "Queue a recovery agent for this run? It will inspect retained work and "
                                "finish the outstanding task under the existing permissions and writer lock."}
    return None


def prompt(run_id):
    return (
        f"Recover run {run_id} safely; this is a focused continuation, not a new coverage sweep. "
        "Read that run's status.json, report.json, publication.json if present, and last agent output. "
        "First inspect git status and unpublished commits; preserve all retained edits. Check whether "
        "the original repair is already published before doing anything else. Verify actual live "
        "evidence and do not repeat completed research, rewrite verified content, or publish twice. "
        "If only publication is pending, provide its exact full commit and deployment URL in the "
        "report so automatic verification can finish it. If unfinished edits need completion, "
        "validate and finish only the original remaining scope when authorized. Never bypass a "
        "permission/source denial, alter credentials/authority, reset work, or install operator "
        "services. Write the required report for THIS invocation before the budget expires.")
