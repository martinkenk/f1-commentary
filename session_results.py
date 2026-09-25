"""Collect official session tables before deployment persists data.

Missing/failed sources retain last-good classifications, never imply no running.
The build consumes the same timestamped snapshot, including its source status.
"""
import argparse
import datetime
import json
from pathlib import Path
import re
import urllib.request

import f1lib

UTC = datetime.timezone.utc


def identity(ctx):
    return {key: str(ctx[key]) for key in ("year", "race_id", "results_slug")} | {
        "gp": ctx["dir"]}


def source_url(ctx, endpoint):
    return (f"https://www.formula1.com/en/results/{ctx['year']}/races/"
            f"{ctx['race_id']}/{ctx['results_slug']}/{endpoint}")


def session_start(ctx, label):
    target = "Qualifying" if label == "Starting Grid" else label
    session = next((s for s in ctx.get("cal", {}).get("sessions", [])
                    if s["label"] == target), None)
    if session is None:
        return None
    start = datetime.datetime.fromisoformat(
        session["date"] + "T" + session["time"] + session["gmt_offset"])
    return start + datetime.timedelta(hours=1 if label == "Starting Grid" else 0)


def validate_table(headers, rows):
    low = [header.lower().rstrip(".") for header in headers]
    if any(column not in low for column in ("pos", "no", "driver", "team")):
        raise ValueError(f"Unexpected classification columns: {headers}")
    if len(rows) < 18:
        raise ValueError(f"Incomplete classification: {len(rows)} entrants")
    numbers, codes, positions = set(), set(), []
    for row in rows:
        if len(row) != len(headers):
            raise ValueError("Misaligned classification row")
        values = dict(zip(low, row))
        name, code = f1lib._split_driver(values["driver"])
        number, pos = values["no"], values["pos"].upper()
        if (not number.isdigit() or number in numbers or not name or not code
                or code in codes or not values["team"]):
            raise ValueError("Missing or duplicate entrant identity")
        if pos.isdigit():
            if int(pos) < 1:
                raise ValueError("Invalid classification position")
            positions.append(int(pos))
        elif pos not in ("NC", "DNF", "DNS", "DSQ", "DQ"):
            raise ValueError(f"Unknown classification position: {pos}")
        numbers.add(number)
        codes.add(code)
    if positions != sorted(set(positions)):
        raise ValueError("Duplicate or unordered classification positions")
    return numbers


def parse_table(page):
    tables = re.findall(r"<table\b[^>]*>.*?</table>", page, re.S)
    if len(tables) != 1:
        raise ValueError("Official classification table is not published or is ambiguous")
    parsed = f1lib._parse_result_table(tables[0])
    if not parsed:
        raise ValueError("Official classification table is not published")
    validate_table(*parsed)
    return parsed


def load(ctx):
    path = Path(f1lib.DATA_DIR) / ctx["dir"] / "session_results.json"
    if not path.exists():
        return {}
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict) or record.get("event") != identity(ctx):
        raise ValueError(f"Session-results snapshot event mismatch: {path}")
    for block in record.get("sessions", []):
        endpoint = dict(f1lib.RESULT_SESSIONS).get(block["label"])
        start = session_start(ctx, block["label"])
        if (not endpoint or block["source_url"] != source_url(ctx, endpoint)
                or start is None or block["session_start"] != start.isoformat()):
            raise ValueError("Session-results snapshot source/session mismatch")
        validate_table(block["headers"], block["rows"])
    return record


def refresh(ctx, now=None, persist=True):
    now = now or datetime.datetime.now(UTC)
    previous = load(ctx)
    cached = {block["label"]: block for block in previous.get("sessions", [])}
    blocks, statuses = [], []
    checked = now.isoformat(timespec="seconds")
    for label, endpoint in f1lib.RESULT_SESSIONS:
        start = session_start(ctx, label)
        if start is None or now < start:
            continue
        url = source_url(ctx, endpoint)
        old = cached.get(label)
        try:
            request = urllib.request.Request(url, headers={"User-Agent": f1lib.UA})
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.url != url:
                    raise ValueError(f"Unexpected results redirect: {response.url}")
                page = response.read().decode("utf-8")
            headers, rows = parse_table(page)
            if old:
                lost = (validate_table(old["headers"], old["rows"])
                        - validate_table(headers, rows))
                if lost:
                    raise ValueError(f"Classification lost recorded entrants: {sorted(lost)}")
            blocks.append({
                "label": label, "headers": headers, "rows": rows,
                "source_url": url, "fetched_at": checked,
                "session_start": start.isoformat(), "retained": False,
            })
            statuses.append({"label": label, "state": "available", "source_url": url})
            print(f"  {ctx['dir']} {label}: {len(rows)} official entrants")
        except (OSError, ValueError) as error:
            # A missing table during running is pending, not a failed classification.
            hours = 2 if label == "Race" else 0.5 if label == "Sprint" else 1
            state = "unavailable" if old or now >= start + datetime.timedelta(hours=hours) else "pending"
            statuses.append({"label": label, "state": state, "source_url": url,
                             "error": str(error), "retained": bool(old)})
            if old:
                blocks.append(dict(old, retained=True))
            print(f"  ! {ctx['dir']} {label}: {error}; "
                  f"{'retaining last-good classification' if old else state}")
    record = {"event": identity(ctx), "checked_at": checked,
              "sessions": blocks, "statuses": statuses}
    if persist:
        path = Path(f1lib.DATA_DIR) / ctx["dir"] / "session_results.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        staging = path.with_suffix(".json.new")
        staging.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
        staging.replace(path)
    return record


def results(ctx, now=None):
    now = now or datetime.datetime.now(UTC)
    record = load(ctx) or refresh(ctx, now=now, persist=False)
    ctx["results_status"] = record.get("statuses", [])
    ctx["results_checked_at"] = record["checked_at"]
    return [block for block in record["sessions"]
            if session_start(ctx, block["label"]) <= now]


def main():
    import build
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gp", help="one registered GP; default: all started weekends")
    args = parser.parse_args()
    gps = build.season_gps()
    if args.gp:
        gps = [ctx for ctx in gps if ctx["dir"] == args.gp]
        if not gps:
            parser.error("Unknown GP")
    now = datetime.datetime.now(UTC)
    errors = False
    for ctx in gps:
        if not any(session_start(ctx, label) and session_start(ctx, label) <= now
                   for label, _ in f1lib.RESULT_SESSIONS):
            continue
        record = refresh(ctx, now=now)
        errors |= any(status["state"] == "unavailable" for status in record["statuses"])
    return int(errors)


if __name__ == "__main__":
    raise SystemExit(main())
