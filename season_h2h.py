"""Refresh source-backed season qualifying/race teammate comparisons.

Uses every round in the calendar, not just the GPs with pages. Sprint sessions
are separate competitions and are not included. Build-time rendering is offline.
"""
import argparse
import datetime
import html
import json
from pathlib import Path
import re
import urllib.request

import f1lib

ROOT = Path(__file__).resolve().parent
UTC = datetime.timezone.utc
SESSIONS = {"Qualifying": ("qualifying", 1), "Race": ("race-result", 2)}
TEAM_ALIASES = {"Haas": "Haas F1 Team", "Red Bull": "Red Bull Racing",
                "RB": "Racing Bulls", "Kick Sauber": "Sauber"}


def _read(path):
    if not path.exists():
        return {}
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return record


def _write(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def parse_classification(page, kind):
    if kind not in SESSIONS:
        raise ValueError(f"Unsupported head-to-head session: {kind}")
    tables = re.findall(r"<table\b[^>]*>.*?</table>", page, re.S)
    if len(tables) != 1:
        raise ValueError(f"Expected one official {kind} classification table")
    parsed = f1lib._parse_result_table(tables[0])
    if parsed is None:
        raise ValueError(f"No published {kind} classification")
    headers, rows = parsed
    low = [header.lower().rstrip(".") for header in headers]
    required = ["pos", "driver", "team", "q1" if kind == "Qualifying" else "time / retired"]
    if any(header not in low for header in required):
        raise ValueError(f"Unexpected {kind} classification columns: {headers}")
    if len(rows) < 18:
        raise ValueError(f"Incomplete {kind} classification: {len(rows)} rows")
    drivers, seen, positions = [], set(), []
    for row in rows:
        if len(row) != len(headers):
            raise ValueError(f"Misaligned {kind} classification row")
        values = dict(zip(low, row))
        name, code = f1lib._split_driver(values["driver"])
        team = TEAM_ALIASES.get(values["team"], values["team"])
        if not code or code in seen or not team:
            raise ValueError(f"Invalid or duplicate driver identity: {values['driver']}")
        seen.add(code)
        raw = values["pos"].upper()
        if not raw.isdigit() and raw not in ("NC", "DNF", "DNS", "DSQ", "DQ"):
            raise ValueError(f"Unknown classification position: {raw!r}")
        position = int(raw) if raw.isdigit() else None
        if position is not None and position < 1:
            raise ValueError("Classification positions must be positive")
        if position is not None:
            positions.append(position)
        status = values.get("time / retired", "").upper()
        if raw in ("DSQ", "DQ") or re.search(r"\b(DSQ|DQ|DISQUALIFIED)\b", status):
            state = "dsq"
        elif raw == "DNS" or re.search(r"\bDNS\b", status):
            state = "dns"
        elif kind == "Qualifying" and not any(
                re.fullmatch(r"\d+:\d{2}\.\d+", values.get(segment, ""))
                for segment in ("q1", "q2", "q3")):
            state = "no-time"
        elif position is None:
            state = "unclassified"
        else:
            state = "classified"
        drivers.append({"code": code, "name": name, "team": team,
                        "position": position, "status": state,
                        "raw_position": raw})
    if len(positions) != len(set(positions)) or positions != sorted(positions):
        raise ValueError("Duplicate or unordered classification positions")
    if any(sum(driver["team"] == team for driver in drivers) > 2
           for team in {driver["team"] for driver in drivers}):
        raise ValueError("More than two entrants for a team in one session")
    return drivers


def expected_sessions(events, now):
    for event in events:
        for session in event["sessions"]:
            label = session["label"]
            if label not in SESSIONS:
                continue
            endpoint, hours = SESSIONS[label]
            start = datetime.datetime.fromisoformat(
                session["date"] + "T" + session["time"] + session["gmt_offset"])
            if now < start + datetime.timedelta(hours=hours):
                continue
            if not event.get("race_id") or not event.get("results_slug"):
                raise ValueError(f"Missing results identity for {event['slug']}")
            yield event, label, endpoint, start


def refresh(year=2026, now=None, force=False):
    now = now or datetime.datetime.now(UTC)
    calendar = _read(ROOT / "data" / f"calendar_{year}.json")
    if not calendar.get("events"):
        raise ValueError("Season calendar is missing or empty")
    path = ROOT / "data" / f"season_h2h_{year}.json"
    previous = _read(path)
    if previous and previous.get("year") != year:
        raise ValueError("Head-to-head snapshot season mismatch")
    cached = {session["key"]: session for session in previous.get("sessions", [])}
    retry = {error["key"] for error in previous.get("errors", [])}
    expected, errors = [], []
    for event, label, endpoint, start in expected_sessions(calendar["events"], now):
        key = f'{event["slug"]}/{endpoint}'
        expected.append(key)
        old = cached.get(key)
        if old and key not in retry and not force and (now - start).days > 10:
            fetched = datetime.datetime.fromisoformat(old["fetched_at"])
            if now - fetched < datetime.timedelta(days=7):
                continue
        url = (f'https://www.formula1.com/en/results/{year}/races/'
               f'{event["race_id"]}/{event["results_slug"]}/{endpoint}')
        try:
            request = urllib.request.Request(url, headers={"User-Agent": f1lib.UA})
            with urllib.request.urlopen(request, timeout=30) as response:
                page = response.read().decode("utf-8")
            drivers = parse_classification(page, label)
            if old:
                lost = {driver["code"] for driver in old["drivers"]} - {driver["code"] for driver in drivers}
                if lost:
                    raise ValueError(f"Classification lost recorded entrants: {sorted(lost)}")
            cached[key] = {
                "key": key, "round": event["round"], "gp": event["slug"],
                "name": event["name"], "label": label,
                "date": start.date().isoformat(), "url": url,
                "fetched_at": now.isoformat(timespec="seconds"), "drivers": drivers,
            }
            print(f"  {event['slug']} {label}: {len(drivers)} official entrants")
        except (OSError, ValueError) as error:
            errors.append({"key": key, "url": url, "error": str(error)})
            print(f"  ! {key}: {error}; retaining any previous classification")
    for key in sorted(cached.keys() - set(expected)):
        expected.append(key)
        errors.append({"key": key, "url": cached[key]["url"],
                       "error": "Previously collected session missing from current calendar scope"})
        print(f"  ! {key}: retaining prior session omitted by the current calendar")
    record = {"year": year, "checked_at": now.isoformat(timespec="seconds"),
              "expected": expected, "errors": errors,
              "sessions": sorted((cached[key] for key in expected if key in cached),
                                 key=lambda session: (session["round"], session["label"]))}
    _write(path, record)
    return record


def compare(a, b, label):
    if a is None or b is None:
        return None, "Missing driver in published table"
    if any(driver["status"] in ("dns", "dsq", "no-time") for driver in (a, b)):
        return None, "DNS, disqualification or no qualifying time"
    if a["position"] is not None and b["position"] is not None:
        if a["position"] == b["position"]:
            return None, "Equal classification position"
        return (0 if a["position"] < b["position"] else 1), ""
    if label == "Race" and (a["position"] is not None or b["position"] is not None):
        return (0 if a["position"] is not None else 1), ""
    return None, "Both unclassified or no comparable positions"


def aggregate(record):
    pairs = {}
    # Each event's race entrants identify a missing qualifier where possible.
    events = {}
    for session in record.get("sessions", []):
        events.setdefault(session["gp"], []).append(session)
    for sessions in events.values():
        possible = {}
        for session in sessions:
            teams = {}
            for driver in session["drivers"]:
                teams.setdefault(driver["team"], []).append(driver)
            for team, drivers in teams.items():
                if len(drivers) == 2:
                    codes = tuple(sorted(driver["code"] for driver in drivers))
                    possible[(team, codes)] = {driver["code"]: driver for driver in drivers}
        for (team, codes), identities in possible.items():
            pair = pairs.setdefault((team, codes), {
                "team": team, "drivers": [identities[code] for code in codes],
                "Qualifying": {"wins": [0, 0], "excluded": 0},
                "Race": {"wins": [0, 0], "excluded": 0}, "rounds": [],
            })
            for session in sessions:
                entrants = {driver["code"]: driver for driver in session["drivers"]
                            if driver["team"] == team}
                # Do not charge a different replacement pairing with a missed session.
                if set(entrants) - set(codes):
                    continue
                a, b = (entrants.get(code) for code in codes)
                winner, reason = compare(a, b, session["label"])
                tally = pair[session["label"]]
                if winner is None:
                    tally["excluded"] += 1
                else:
                    tally["wins"][winner] += 1
                pair["rounds"].append({
                    "gp": session["name"], "label": session["label"], "url": session["url"],
                    "positions": [driver["raw_position"] if driver else "-" for driver in (a, b)],
                    "winner": codes[winner] if winner is not None else None, "reason": reason,
                })
    return [pairs[key] for key in sorted(pairs)]


def render(year=2026):
    record = _read(ROOT / "data" / f"season_h2h_{year}.json")
    if not record:
        return ('<div class="callout watch">Season teammate data is not available yet. '
                'The scheduled official-results refresh supplies this comparison.</div>')
    if record.get("year") != year:
        raise ValueError("Head-to-head snapshot season mismatch")
    pairs = aggregate(record)
    escape = html.escape
    missing = set(record["expected"]) - {session["key"] for session in record["sessions"]}
    warning = ""
    if record["errors"] or missing:
        warning = (f'<div class="callout watch"><strong>Incomplete season refresh:</strong> '
                   f'{len(missing)} missing session(s), {len(record["errors"])} refresh error(s). '
                   'Available last-good classifications are retained; scorelines may be incomplete.</div>')
    checked = datetime.datetime.fromisoformat(record["checked_at"])
    if datetime.datetime.now(UTC) - checked > datetime.timedelta(hours=24):
        warning += '<div class="callout watch">Season comparison refresh is over 24 hours old.</div>'
    rows, details = [], []
    for index, pair in enumerate(pairs):
        a, b = pair["drivers"]
        cells = []
        for label in SESSIONS:
            tally = pair[label]
            left, right = tally["wins"]
            left_score = f'<span class="h2h-win">{left}</span>' if left > right else str(left)
            right_score = f'<span class="h2h-win">{right}</span>' if right > left else str(right)
            cells.append(
                f'<td class="num"><strong>{left_score} &ndash; {right_score}</strong>'
                f'<span class="h2h-count">{left + right} compared'
                f' / {tally["excluded"]} excluded</span></td>')
        rows.append(f'<tr><td class="tm">{escape(pair["team"])}</td>'
                    f'<td>{escape(a["name"])} <span class="drv-code">{a["code"]}</span></td>'
                    + "".join(cells)
                    + f'<td>{escape(b["name"])} <span class="drv-code">{b["code"]}</span></td>'
                    f'<td><a href="#season-pair-{index}" '
                    f'onclick="document.getElementById(\'season-pair-{index}\').open=true">Rounds</a></td></tr>')
        evidence = []
        for result in pair["rounds"]:
            outcome = result["winner"] or result["reason"]
            evidence.append(
                f'<tr><td><a href="{escape(result["url"], quote=True)}" target="_blank" rel="noopener">'
                f'{escape(result["gp"])} &middot; {result["label"]}</a></td>'
                f'<td>{escape(result["positions"][0])}</td><td>{escape(result["positions"][1])}</td>'
                f'<td>{escape(outcome)}</td></tr>')
        details.append(
            f'<details id="season-pair-{index}"><summary>{escape(pair["team"])}: '
            f'{a["code"]} / {b["code"]} &mdash; round-by-round sources</summary>'
            '<div class="table-wrap"><table class="data compact"><thead><tr>'
            f'<th>Official session</th><th>{a["code"]}</th><th>{b["code"]}</th><th>Ahead / exclusion</th>'
            f'</tr></thead><tbody>{"".join(evidence)}</tbody></table></div></details>')
    counts = {label: sum(session["label"] == label for session in record["sessions"])
              for label in SESSIONS}
    latest = max((session["date"] for session in record["sessions"]), default="none")
    return (
        f'<section class="season-h2h"><h2 class="sec">{year} season teammate comparison</h2>'
        f'<p class="lead-note">{counts["Qualifying"]} qualifying sessions and {counts["Race"]} Grands Prix '
        f'loaded through {latest}. Current season totals, not an entering-this-GP snapshot.</p>'
        f'<p class="src">Official Formula1.com classifications; last refresh {escape(record["checked_at"])}.</p>'
        + warning + '<p>Each score reads <strong>left-hand driver &ndash; right-hand driver</strong>. '
        'Qualifying uses session classification, not the penalty-adjusted starting grid. '
        'Race scores use official finishing classification, including classified retirements; a classified '
        'driver beats an unclassified driver. DNS, DSQ, no qualifying time and two unclassified drivers '
        'are excluded. This is a results comparison, not a reliability-adjusted pace measure. '
        'Sprint sessions and FP1 substitutes are not counted; replacement pairings have separate rows.</p>'
        '<div class="table-wrap"><table class="data compact h2h"><thead><tr>'
        '<th>Team</th><th>Driver A</th><th class="num">Qualifying A&ndash;B</th>'
        '<th class="num">Race A&ndash;B</th><th>Driver B</th><th>Evidence</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
        + "".join(details) + '</section>')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--force", action="store_true", help="refresh every completed session")
    args = parser.parse_args()
    snapshot = refresh(args.year, force=args.force)
    raise SystemExit(1 if snapshot["errors"] else 0)
