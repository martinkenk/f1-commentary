"""Independent GitHub-side check: a stopped/offline host cannot report its own outage."""
import argparse
import datetime as dt
import json
import re
import subprocess


def assess(body, now):
    match = re.search(r"```json\n(.*?)\n```", body, re.S)
    if not match:
        return "Scheduler has not published a machine-readable heartbeat."
    record = json.loads(match[1])
    stamp = dt.datetime.fromisoformat(record["heartbeat_at"])
    if stamp.tzinfo is None or stamp > now + dt.timedelta(minutes=5):
        return "Invalid scheduler heartbeat timestamp."
    if now - stamp > dt.timedelta(minutes=90):
        return f"Scheduler heartbeat is stale: {stamp.isoformat()}. Check f1-calendar.timer and host availability."
    if record.get("errors"):
        return "Scheduler reports unresolved failures; see the health issue."
    return ""


def api(endpoint, *args):
    result = subprocess.run(["gh", "api", endpoint, *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue", type=int, required=True)
    args = parser.parse_args()
    endpoint = f"repos/martinkenk/f1-commentary/issues/{args.issue}"
    issue = api(endpoint)
    problem = assess(issue["body"], dt.datetime.now(dt.timezone.utc))
    if problem and not problem.startswith("Scheduler reports"):
        comments = api(endpoint + "/comments?per_page=100")
        message = "External watchdog alert: " + problem
        if not any(comment["body"] == message for comment in comments):
            api(endpoint + "/comments", "--method", "POST", "-f", f"body={message}")
    print(problem or "Scheduler heartbeat is fresh and has no unresolved failures.")
    return int(bool(problem))


if __name__ == "__main__":
    raise SystemExit(main())
