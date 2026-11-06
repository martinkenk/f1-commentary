"""Machine-readable publication evidence and calendar-relative coverage expectations.

An expectation is a review deadline, not a claim that an upstream has published.
Never replace missing source data with inferred results or technical values.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path

import news_briefing
import race_tyres
import session_results

UTC = dt.timezone.utc
DURATIONS = {"Practice 1": 60, "Practice 2": 60, "Practice 3": 60,
             "Sprint Qualifying": 45, "Sprint": 30, "Qualifying": 60,
             "Race": 120, "Starting Grid": 0}


def timestamp(value):
    result = dt.datetime.fromisoformat(value)
    if result.tzinfo is None:
        raise ValueError(f"Timestamp has no timezone: {value}")
    return result.astimezone(UTC)


def session_end(ctx, label):
    start = session_results.session_start(ctx, label)
    return start + dt.timedelta(minutes=DURATIONS[label]) if start else None


def digest(headers, rows):
    return hashlib.sha256(json.dumps([headers, rows], ensure_ascii=False).encode()).hexdigest()


def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else ({} if default is None else default)


def record_collection(root, outcomes, scope="", now=None):
    """A results-only build must not erase the last failed news/FIA collection."""
    path = Path(root) / "data/collection_status.json"
    record = read(path)
    checked = (now or dt.datetime.now(UTC)).isoformat()
    for source, outcome in outcomes.items():
        if outcome in ("success", "failure"):
            record[source] = {"outcome": outcome, "gp": scope, "checked_at": checked}
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(record, indent=2) + "\n")
    temporary.replace(path)


def report(gps, root, now=None):
    now = now or dt.datetime.now(UTC)
    root = Path(root)
    events, findings, expected_rounds = {}, [], {}

    def problem(gp, kind, message):
        findings.append({"gp": gp, "kind": kind, "message": message})

    for ctx in gps:
        gp = ctx["dir"]
        directory = root / "data" / gp
        starts = [session_results.session_start(ctx, s["label"])
                  for s in ctx["cal"]["sessions"]]
        first, finish = min(starts), max(starts) + dt.timedelta(hours=2)
        race_end = session_end(ctx, "Race")
        if race_end and now >= race_end + dt.timedelta(minutes=30):
            year = ctx["year"]
            expected_rounds[year] = max(expected_rounds.get(year, 0), ctx["round_no"])
        active = first - dt.timedelta(days=7) <= now <= finish + dt.timedelta(days=2)
        record = read(directory / "session_results.json")
        blocks = record.get("sessions", [])
        evidence = {}
        for block in blocks:
            session_results.validate_table(block["headers"], block["rows"])
            evidence[block["label"]] = {
                "digest": digest(block["headers"], block["rows"]),
                "fetched_at": block["fetched_at"], "retained": block.get("retained", False)}
        events[gp] = {"sessions": evidence, "results_checked_at": record.get("checked_at")}
        if not active:
            continue
        if now >= first - dt.timedelta(hours=24) and not ctx.get("ref", {}).get("tyre_preview_asset"):
            problem(gp, "editorial", "Pirelli preview poster/compound nomination needs source review")
        for label, _ in session_results.f1lib.RESULT_SESSIONS:
            end = session_end(ctx, label)
            if end and now >= end + dt.timedelta(minutes=15) and label not in evidence:
                problem(gp, "results", f"{label} overdue since {(end + dt.timedelta(minutes=15)).isoformat()}")
        for status in record.get("statuses", []):
            if status["state"] == "unavailable":
                problem(gp, "source_error", f"{status['label']}: {status.get('error', 'unavailable')}")
        briefing = news_briefing.select(dict(ctx, results=blocks), directory, now)
        if briefing["mode"] != "Editor-collated":
            problem(gp, "editorial", briefing["notice"] or "No current reviewed news briefing")
        discovery = read(directory / "fia_discovery_status.json")
        if discovery.get("ok") is False:
            problem(gp, "source_error", f"FIA discovery failed: {discovery.get('error', discovery)}")
        media = read(directory / "fia_media.json")
        for error in media.get("errors", []):
            problem(gp, "source_error", f"FIA screenshot collection: {error}")
        documents = read(directory / "fia_documents.json").get("documents", [])
        cached_urls = {doc["url"] for doc in media.get("documents", []) if doc.get("pages")}
        for doc in documents:
            if doc.get("categories") and doc["url"] not in cached_urls:
                problem(gp, "source_error", f"Published FIA document lacks screenshots: {doc['filename']}")
        filenames = " ".join(d["filename"].lower() for d in documents)
        # Soft deadlines: a missing document triggers source investigation, not fabrication.
        for name, tokens, due in (
            ("circuit map", ("circuit_map",), first - dt.timedelta(hours=24)),
            ("tyre prescriptions", ("pirelli",), first - dt.timedelta(hours=24)),
            ("power-unit information", ("power_unit_information",), first - dt.timedelta(hours=2)),
            ("upgrade submissions", ("car_presentation_submissions",), first),
        ):
            if now >= due and not any(token in filenames for token in tokens):
                problem(gp, "expected_source",
                        f"Check publication/collection of {name}; expected by {due.isoformat()}")
        receipt = read(directory / "coverage_review.json")
        reviewed = receipt.get("fia_sha256", {})
        for doc in media.get("documents", []):
            if reviewed.get(doc["url"]) != doc["sha256"]:
                problem(gp, "editorial", f"New/revised FIA document needs interpretation: {doc['filename']}")
        qualifying = session_end(ctx, "Qualifying")
        if qualifying and now >= qualifying + dt.timedelta(hours=1):
            tyre_context = race_tyres.context(ctx, root=root)
            tyres, status = tyre_context["snapshot"], tyre_context["status"]
            if status.get("error"):
                problem(gp, "source_error", f"Race tyre collection: {status['error']}")
            if not tyres:
                problem(gp, "expected_source",
                        f"Race tyre inventory/strategy due for source review; collection: {status.get('state', 'not checked')}")
            else:
                verified = session_results.f1lib.reviewed_race_tyres(ctx, tyres, data_dir=root / "data")
                if verified["state"] != "verified":
                    problem(gp, "editorial", verified["message"])
            strategy = receipt.get("race_strategy", {})
            if (not strategy.get("sources") or not strategy.get("reviewed_at")
                    or timestamp(strategy["reviewed_at"]) < qualifying):
                problem(gp, "editorial", "Post-qualifying race strategy source review is due")
    for year, completed in expected_rounds.items():
        standings = read(root / "data" / f"standings_{year}.json")
        if standings.get("results_round", 0) < completed:
            problem("season", "standings", f"Standings checkpoint is behind completed round {completed}")
    collection = json.loads(os.environ.get("F1_COLLECTION", "{}"))
    last_checks = read(root / "data/collection_status.json")
    for source, outcome in collection.items():
        scope = os.environ.get("F1_COLLECTION_GP", "")
        previous = last_checks.get(source, {})
        if (outcome in ("success", "failure")
                and (previous.get("outcome") != outcome or previous.get("gp") != scope)):
            last_checks[source] = {"outcome": outcome, "gp": scope,
                                   "checked_at": now.isoformat()}
    for source, check in last_checks.items():
        if check["outcome"] == "failure":
            problem(check.get("gp") or "collection", "source_error",
                    f"{source} collector failed; retained data is not fresh")
    return {"generated_at": now.isoformat(), "run_id": os.environ.get("GITHUB_RUN_ID"),
            "refresh_key": os.environ.get("F1_REFRESH_KEY", ""),
            "refresh_mode": os.environ.get("F1_REFRESH_MODE", ""),
            "collection_gp": os.environ.get("F1_COLLECTION_GP", ""),
            "collection": collection,
            "last_collection_checks": last_checks,
            "events": events, "findings": findings}


def main():
    import build
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--record-collection", action="store_true")
    args = parser.parse_args()
    if args.record_collection:
        record_collection(build.ROOT, json.loads(os.environ["F1_COLLECTION"]),
                          os.environ.get("F1_COLLECTION_GP", ""))
        return
    value = report(build.season_gps(), build.ROOT)
    text = json.dumps(value, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
