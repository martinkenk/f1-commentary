"""Championship standings: structured data plus the table renderers.

The standings used to live as pre-baked HTML strings, which meant the markup
could not carry anything derived — team colours, points gaps, leader deltas.
Keeping the numbers as data and generating the rows lets the tables show the
gaps a commentator actually reads out, and keeps the driver and constructor
tables consistent with each other.

Run ``python3 standings.py`` to refresh the official, timestamped snapshot.
The build reads that snapshot without needing a live standings request.
"""

import argparse
import datetime
import html
import json
from pathlib import Path
import re
import urllib.request
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
SEASON = 2026

# Official-ish 2026 team colours, used for the left rail on each row.
TEAM_COLOURS = {
    "Mercedes": "#27f4d2",
    "Ferrari": "#e8002d",
    "McLaren": "#ff8000",
    "Red Bull Racing": "#3671c6",
    "Alpine": "#00a1e8",
    "Racing Bulls": "#6692ff",
    "Haas F1 Team": "#b6babd",
    "Williams": "#1868db",
    "Audi": "#00e701",
    "Aston Martin": "#229971",
    "Cadillac": "#c8b273",
}

def snapshot_path(year=SEASON):
    return ROOT / "data" / f"standings_{year}.json"


def _text(markup):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", markup)).split())


def parse_table(page, kind, year=SEASON):
    """Read F1's rendered table, preserving official order and countback."""
    if kind not in ("drivers", "team"):
        raise ValueError(f"Unknown standings table: {kind}")
    tables = re.findall(r"<table\b[^>]*>(.*?)</table>", page, re.S)
    if len(tables) != 1:
        raise ValueError(f"Expected one {kind} standings table, got {len(tables)}")
    rows = []
    for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", tables[0], re.S):
        cells = re.findall(r"<td\b[^>]*>(.*?)</td>", row, re.S)
        if not cells:
            continue
        if len(cells) != (5 if kind == "drivers" else 3):
            raise ValueError(f"Unexpected {kind} standings columns")
        pos = int(_text(cells[0]))
        raw_points = _text(cells[-1])
        if not re.fullmatch(r"\d+(?:\.5|\.0)?", raw_points):
            raise ValueError(f"Invalid championship points: {raw_points!r}")
        points = float(raw_points)
        points = int(points) if points.is_integer() else points
        if kind == "drivers":
            driver = _text(cells[1])
            match = re.fullmatch(r"(.+)\s+([A-Z]{3})", driver)
            if not match:
                raise ValueError(f"Missing driver name/code: {driver!r}")
            rows.append([pos, match[1], match[2], _text(cells[3]), points])
        else:
            rows.append([pos, _text(cells[1]), points])
    validate_rows(rows, kind, year)
    return rows


def validate_rows(rows, kind, year=SEASON):
    teams = 11 if year >= 2026 else 10
    minimum = teams * 2 if kind == "drivers" else teams
    width = 5 if kind == "drivers" else 3
    if len(rows) < minimum or any(len(row) != width for row in rows):
        raise ValueError(f"Incomplete {kind} championship table")
    if [row[0] for row in rows] != list(range(1, len(rows) + 1)):
        raise ValueError(f"Invalid {kind} championship positions")
    if len({row[1] for row in rows}) != len(rows):
        raise ValueError(f"Duplicate {kind} championship entries")
    for index, row in enumerate(rows):
        if not all(isinstance(value, str) and value.strip() for value in row[1:-1]):
            raise ValueError(f"Missing {kind} championship identity")
        if not isinstance(row[-1], (int, float)) or row[-1] < 0:
            raise ValueError(f"Invalid {kind} championship points")
        if index and row[-1] > rows[index - 1][-1]:
            raise ValueError(f"Unordered {kind} championship points")


def load_snapshot(year=SEASON):
    path = snapshot_path(year)
    if not path.exists():
        print(f"! Championship snapshot missing: run python3 standings.py --year {year}")
        return {}
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    if snapshot["year"] != year:
        raise ValueError("Championship snapshot season mismatch")
    validate_rows(snapshot["drivers"], "drivers", year)
    validate_rows(snapshot["constructors"], "team", year)
    datetime.datetime.fromisoformat(snapshot["fetched_at"])
    if "results_round" in snapshot and (
            not isinstance(snapshot["results_round"], int) or snapshot["results_round"] < 0):
        raise ValueError("Invalid standings results-round checkpoint")
    return snapshot


def _previous_results_round(snapshot, calendar):
    if "results_round" in snapshot:
        return snapshot["results_round"]
    fetched = datetime.datetime.fromisoformat(snapshot["fetched_at"])
    return max((int(event["round"]) for event in calendar["events"]
                if datetime.date.fromisoformat(event["race_date"]) < fetched.date()),
               default=0)


def _new_race_results(snapshot, year, now=None):
    calendar_path = ROOT / "data" / f"calendar_{year}.json"
    if not calendar_path.exists():
        return []
    calendar = json.loads(calendar_path.read_text(encoding="utf-8"))
    if int(calendar.get("year", 0)) != year or not isinstance(calendar.get("events"), list):
        raise ValueError(f"Invalid {year} calendar while checking standings freshness")
    previous_fetched = datetime.datetime.fromisoformat(snapshot["fetched_at"])
    after_round = _previous_results_round(snapshot, calendar)
    now = now or datetime.datetime.now(datetime.timezone.utc)
    races = []
    for event in sorted(calendar["events"], key=lambda item: int(item["round"])):
        round_no = int(event["round"])
        if (round_no <= after_round
                or datetime.date.fromisoformat(event["race_date"]) > now.date()):
            continue
        slug = event["slug"]
        result_path = ROOT / "data" / slug / "session_results.json"
        if not result_path.exists():
            continue
        record = json.loads(result_path.read_text(encoding="utf-8"))
        identity = record.get("event", {})
        if identity.get("year") != str(year) or identity.get("gp") != slug:
            raise ValueError(f"Session-results event mismatch while checking standings: {slug}")
        race = next((block for block in record.get("sessions", [])
                     if block.get("label") == "Race"), None)
        if not race:
            continue
        fetched_at = datetime.datetime.fromisoformat(race["fetched_at"])
        if fetched_at <= previous_fetched:
            continue
        headers = [header.lower().rstrip(".") for header in race["headers"]]
        required = ("driver", "team", "pts")
        if any(column not in headers for column in required):
            raise ValueError(f"Race result lacks points for standings reconciliation: {slug}")
        driver_index, team_index, points_index = (headers.index(column) for column in required)
        driver_points, team_points, driver_names = defaultdict(float), defaultdict(float), {}
        for row in race["rows"]:
            if len(row) != len(headers):
                raise ValueError(f"Malformed race result row while checking standings: {slug}")
            match = re.fullmatch(r"(.+)\s+([A-Z]{3})", row[driver_index].strip())
            if not match:
                raise ValueError(f"Missing driver identity in race result: {slug}")
            raw_points = row[points_index].strip()
            if not re.fullmatch(r"\d+(?:\.5|\.0)?", raw_points):
                raise ValueError(f"Invalid race points in official result: {slug}")
            points = float(raw_points)
            if points:
                code = match[2]
                team = row[team_index].strip()
                driver_points[code] += points
                team_points[team] += points
                driver_names[code] = match[1]
        races.append({
            "round": round_no,
            "slug": slug,
            "name": event["name"],
            "fetched_at": fetched_at.isoformat(),
            "source_url": race["source_url"],
            "driver_points": dict(driver_points),
            "team_points": dict(team_points),
            "driver_names": driver_names,
        })
    return races


def _race_points_mismatches(previous, current, races):
    if not races:
        return []
    prior_drivers = {row[2]: row[4] for row in previous["drivers"]}
    current_drivers = {row[2]: row[4] for row in current["drivers"]}
    prior_teams = {row[1]: row[2] for row in previous["constructors"]}
    current_teams = {row[1]: row[2] for row in current["constructors"]}
    expected_drivers, expected_teams, names = defaultdict(float), defaultdict(float), {}
    for race in races:
        for code, points in race["driver_points"].items():
            expected_drivers[code] += points
            names[code] = race["driver_names"][code]
        for team, points in race["team_points"].items():
            expected_teams[team] += points
    mismatches = []
    for code, points in expected_drivers.items():
        expected = prior_drivers.get(code, 0) + points
        actual = current_drivers.get(code)
        if actual is None or actual < expected:
            label = names[code]
            mismatches.append(
                f"{label} ({code}): expected at least {expected} points after the "
                f"official Race classification, source shows {actual if actual is not None else 'no row'}")
    for team, points in expected_teams.items():
        expected = prior_teams.get(team, 0) + points
        actual = current_teams.get(team)
        if actual is None or actual < expected:
            mismatches.append(
                f"{team}: expected at least {expected} points after the official Race "
                f"classification, source shows {actual if actual is not None else 'no row'}")
    return mismatches


def _write_snapshot(path, snapshot):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def refresh(year=SEASON):
    sources = {
        "drivers": f"https://www.formula1.com/en/results/{year}/drivers",
        "constructors": f"https://www.formula1.com/en/results/{year}/team",
    }
    snapshot = {"year": year, "sources": sources}
    for key, url in sources.items():
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            page = response.read().decode("utf-8")
        snapshot[key] = parse_table(page, "drivers" if key == "drivers" else "team", year)
    snapshot["fetched_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    path = snapshot_path(year)
    if path.exists():
        previous = load_snapshot(year)
        for key in ("drivers", "constructors"):
            missing = {row[1] for row in previous[key]} - {row[1] for row in snapshot[key]}
            if missing:
                raise ValueError(f"Official {key} table lost recorded entries: {sorted(missing)}")
        races = _new_race_results(previous, year)
        mismatches = _race_points_mismatches(previous, snapshot, races)
        if mismatches:
            now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
            previous["checked_at"] = now
            previous["refresh_status"] = {
                "state": "pending",
                "checked_at": now,
                "round": races[-1]["round"],
                "event": races[-1]["name"],
                "results_url": races[-1]["source_url"],
                "mismatches": mismatches,
            }
            _write_snapshot(path, previous)
            print(f"! Official standings have not reconciled with the "
                  f"{races[-1]['name']} Race classification; retaining the last "
                  f"coherent driver/constructor snapshot.")
            for mismatch in mismatches:
                print(f"  ! {mismatch}")
            return previous
        if races:
            snapshot["results_round"] = races[-1]["round"]
        else:
            snapshot["results_round"] = _previous_results_round(previous, {
                "events": json.loads((ROOT / "data" / f"calendar_{year}.json")
                                     .read_text(encoding="utf-8"))["events"]
            })
        if previous.get("refresh_status", {}).get("state") == "pending" and not races:
            snapshot["refresh_status"] = previous["refresh_status"]
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_snapshot(path, snapshot)
    print(f"Refreshed championship: {len(snapshot['drivers'])} drivers, "
          f"{len(snapshot['constructors'])} constructors -> {path}")
    return snapshot


def _rail(team):
    """Inline custom property consumed by `tr[data-team] td.pos`."""
    colour = TEAM_COLOURS.get(team)
    return f' data-team="{team}" style="--team:{colour}"' if colour else ""


def _gap_label(pts, leader, ahead_pts, ahead_pos):
    """Sub-label under a points figure: deficit to the leader and to the car ahead.

    This is the number most often wanted mid-broadcast and it is tedious to work
    out live, so it is precomputed rather than left as mental arithmetic. The
    deficit figures are the part worth reading at a glance, so they are bolded
    and given their own colour; when both a leader-gap and an ahead-gap apply
    they are stacked on two lines (rather than joined with "·") so neither
    number gets lost against the other.
    """
    if ahead_pts is None:
        return '<span class="pts-gap pts-gap--lead">Championship leader</span>'
    if pts == 0:
        # A chain of "level with P20 / level with P21" down the bottom of the
        # table says nothing; the fact worth stating is that they are yet to score.
        return '<span class="pts-gap">Yet to score</span>'
    if ahead_pts == pts:
        return f'<span class="pts-gap">Level with P{ahead_pos}</span>'
    to_leader = leader - pts
    to_ahead = ahead_pts - pts
    leader_line = f'<span class="pts-gap"><b>−{to_leader}</b> to P1</span>'
    # For P2 the leader and the car ahead are the same, so showing both reads
    # as "−45 to P1 / −45 to P1".
    if ahead_pos == 1:
        return leader_line
    ahead_line = f'<span class="pts-gap pts-gap--ahead"><b>−{to_ahead}</b> to P{ahead_pos}</span>'
    return leader_line + ahead_line


def driver_rows(rows=None):
    """<tr> markup for the drivers' championship."""
    rows = DRIVERS if rows is None else rows
    if not rows:
        return ""
    leader = rows[0][4]
    out = []
    for i, (pos, name, code, team, pts) in enumerate(rows):
        ahead_pts = rows[i - 1][4] if i else None
        ahead_pos = rows[i - 1][0] if i else None
        gap = _gap_label(pts, leader, ahead_pts, ahead_pos)
        out.append(
            f'      <tr{_rail(team)}><td class="pos">{pos}</td>'
            f'<td class="drv">{html.escape(name)} <span class="drv-code">{html.escape(code)}</span></td>'
            f'<td class="team">{html.escape(team)}</td>'
            f'<td class="pts" data-sort="{pts}">{pts}{gap}</td></tr>')
    return "\n".join(out)


def ctor_rows(rows=None):
    """<tr> markup for the constructors' championship."""
    rows = CONSTRUCTORS if rows is None else rows
    if not rows:
        return ""
    leader = rows[0][2]
    out = []
    for i, (pos, team, pts) in enumerate(rows):
        ahead_pts = rows[i - 1][2] if i else None
        ahead_pos = rows[i - 1][0] if i else None
        gap = _gap_label(pts, leader, ahead_pts, ahead_pos)
        out.append(
            f'      <tr{_rail(team)}><td class="pos">{pos}</td>'
            f'<td class="drv">{html.escape(team)}</td>'
            f'<td class="pts" data-sort="{pts}">{pts}{gap}</td></tr>')
    return "\n".join(out)


def context(year=SEASON, now=None):
    snapshot = load_snapshot(year)
    if not snapshot:
        return {}
    fetched = datetime.datetime.fromisoformat(snapshot["fetched_at"])
    now = now or datetime.datetime.now(datetime.timezone.utc)
    stale = now - fetched > datetime.timedelta(hours=24)
    drivers = snapshot["drivers"]
    leader, second = drivers[:2]
    label = fetched.strftime("%d %b %Y, %H:%M UTC")
    notice = ('<div class="callout"><strong>Standings refresh overdue.</strong> '
              'Showing the last successful official snapshot; totals may have changed.</div>'
              if stale else "")
    refresh_status = snapshot.get("refresh_status", {})
    if refresh_status.get("state") == "pending":
        details = "; ".join(refresh_status.get("mismatches", []))
        notice += (
            '<div class="callout"><strong>Official post-race standings update pending.</strong> '
            f'The Formula1.com driver and constructor tables do not yet both reflect the '
            f'{html.escape(refresh_status.get("event", "latest"))} Race classification. '
            f'The last coherent standings snapshot from {html.escape(label)} is shown; '
            f'it is not a post-race points table. {html.escape(details)} '
            f'<a href="{html.escape(refresh_status.get("results_url", ""), quote=True)}" '
            'target="_blank" rel="noopener">Official Race classification</a>.</div>'
        )
    notice += (f'<p class="src">Official season standings retrieved {label}; '
               'these are current-season totals, not a frozen pre-race table. '
               f'<a href="{snapshot["sources"]["drivers"]}" target="_blank" rel="noopener">'
               'Formula1.com drivers</a> &middot; '
               f'<a href="{snapshot["sources"]["constructors"]}" target="_blank" rel="noopener">'
               'constructors</a>.</p>')
    return {
        "drivers": driver_rows(drivers),
        "ctors": ctor_rows(snapshot["constructors"]),
        "as_of": label,
        "summary": html.escape(
            f"{leader[1]} leads with {leader[4]} points, "
            f"{leader[4] - second[4]} ahead of {second[1]}."),
        "notice": notice,
    }


SNAPSHOT = load_snapshot() if __name__ != "__main__" else {}
DRIVERS = SNAPSHOT.get("drivers", [])
CONSTRUCTORS = SNAPSHOT.get("constructors", [])
DRIVER_ROWS = driver_rows()
CTOR_ROWS = ctor_rows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=SEASON)
    result = refresh(parser.parse_args().year)
    if result.get("refresh_status", {}).get("state") == "pending":
        raise SystemExit(1)
