"""Offline, pre-weekend circuit history derived from checksum-verified F1DB.

Refresh with ``python3 circuit_history.py``. Rendering must only call context()
or load_profile(); neither performs network requests or writes files.
"""

import argparse
from collections import defaultdict
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import unicodedata
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
UTC = dt.timezone.utc
SCHEMA_VERSION = 1
BUILD_VERSION = 2
LATEST = "https://api.github.com/repos/f1db/f1db/releases/latest"
ASSET = "f1db-json-splitted.zip"
TABLES = ("races", "circuits", "grands-prix", "drivers", "constructors",
          "seasons-drivers", "races-race-results", "races-qualifying-results",
          "races-starting-grid-positions")
# Calendar location is deliberately checked independently of the GP name.
VENUES = {
    "Melbourne": "melbourne", "Shanghai": "shanghai", "Suzuka": "suzuka",
    "Miami Gardens": "miami", "Montréal": "montreal", "Monte Carlo": "monaco",
    "Barcelona": "catalunya", "Spielberg": "spielberg", "Silverstone": "silverstone",
    "Spa-Francorchamps": "spa-francorchamps", "Budapest": "hungaroring",
    "Zandvoort": "zandvoort", "Monza": "monza", "Madrid": "madring", "Baku": "baku",
    "Kuala Lumpur": "sepang", "Marina Bay": "marina-bay", "Austin": "austin",
    "Mexico City": "mexico-city", "São Paulo": "interlagos", "Las Vegas": "las-vegas",
    "Lusail": "lusail", "Yas Marina": "yas-marina",
}
GP_IDS = {"brazil": "sao-paulo", "united-arab-emirates": "abu-dhabi"}
METHOD = [
    "World Championship Grands Prix from 1950 only; no sprints or non-championship races.",
    "Only races with actual race classifications count; dates must precede both the "
    "weekend's local race date and the refresh UTC date. Edition numbers describe "
    "the scheduled event, not an assertion that it has taken place.",
    "All layouts are grouped by F1DB circuit identity. Grand Prix names are grouped "
    "by F1DB grandPrixId, across venues; F1DB may group renamed titles (e.g. "
    "Mexican/Mexico City). Venue-name breakdowns are separate.",
    "Constructors retain F1DB identities; successor brands are not merged. Starts "
    "are driver race participations and constructor car starts; shared-car results "
    "are deduplicated by car for constructors and by event for driver awards.",
    "Best finish means numeric classified race finish, not retirement order. DNS, "
    "DNQ, DNPQ and DNP are not starts. Disqualified participation is established "
    "by completed laps, shared-car evidence or independent F1DB season-start "
    "totals. Missing laps/grid metadata does not mean no start; unresolved "
    "participation rejects the refresh. Disqualified finishes never become "
    "classified best finishes.",
    "Race-result completeness is checked against separate starting-grid entry "
    "identities, classification display order and F1DB season-driver entry/start "
    "totals before publication. Independently consistent source corrections are "
    "allowed; incomplete refreshes retain the last good snapshot.",
    "Pole honours come from the official F1DB polePosition flag, not qualifying "
    "order or starting grid, including sprint weekends. Wins-from-pole denominator "
    "is completed races with a known official pole holder.",
    "Season drivers are the official local standings roster checked against F1DB "
    "season entrants, not a prediction of the lineup at any future event.",
    "Teammates cover the most recent ten completed venue Grands Prix. Qualifying "
    "uses qualifying classifications and recorded times, never the starting grid. "
    "DNS, disqualification, missing/no-time qualifying, equal positions and both "
    "unclassified are excluded; classified beats unclassified in races. Shared "
    "drives, replacement pair ambiguity and teams with more than two entrants "
    "are reported separately instead of forced into a modern two-driver pairing.",
]
NO_START = {"DNS", "DNQ", "DNPQ", "DNP"}
DISQUALIFIED = {"DSQ", "DQ", "EX"}


def _read(path):
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".tmp")
    try:
        pending.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":"))
                           + "\n", encoding="utf-8")
        pending.replace(path)
    finally:
        pending.unlink(missing_ok=True)


def _fetch(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "f1-commentary circuit history",
                      "Accept": "application/vnd.github+json" if url == LATEST else "*/*"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def _release(cache, now, force=False):
    cached = _read(cache / "release.json")
    if cached and not force:
        age = now - dt.datetime.fromisoformat(cached["checked_at"])
        if dt.timedelta() <= age < dt.timedelta(hours=6):
            return cached["release"]
    release = json.loads(_fetch(LATEST))
    if (not re.fullmatch(r"v\d{4}\.\d+\.\d+", release.get("tag_name", ""))
            or release.get("draft") or release.get("prerelease")):
        raise ValueError("Unexpected F1DB release metadata")
    dt.datetime.fromisoformat(release["published_at"].replace("Z", "+00:00"))
    _write(cache / "release.json", {"checked_at": now.isoformat(), "release": release})
    return release


def _asset_url(release, name):
    matches = [a["browser_download_url"] for a in release["assets"] if a["name"] == name]
    expected = f"https://github.com/f1db/f1db/releases/download/{release['tag_name']}/{name}"
    if matches != [expected]:
        raise ValueError(f"Missing, duplicate or unexpected F1DB asset URL: {name}")
    return expected


def _database(release, cache):
    tag = release["tag_name"]
    checksums_url = _asset_url(release, "checksums_sha256.txt")
    url = _asset_url(release, ASSET)
    checksum_path = cache / f"{tag}-checksums.txt"
    checksums = (checksum_path.read_bytes() if checksum_path.exists()
                 else _fetch(checksums_url))
    matches = re.findall(r"^([a-fA-F0-9]{64})\s+\*?" + re.escape(ASSET) + r"\s*$",
                         checksums.decode("ascii"), re.M)
    if len(matches) != 1:
        raise ValueError("F1DB checksum manifest missing unique archive digest")
    expected = matches[0].lower()
    archive_path = cache / f"{tag}-{ASSET}"
    archive = archive_path.read_bytes() if archive_path.exists() else _fetch(url)
    if hashlib.sha256(archive).hexdigest() != expected:
        raise ValueError("F1DB archive SHA256 mismatch")
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        data = {name: json.loads(bundle.read(f"f1db-{name}.json")) for name in TABLES}
    if any(not isinstance(rows, list) or not rows for rows in data.values()):
        raise ValueError("Empty or invalid F1DB table")
    cache.mkdir(parents=True, exist_ok=True)
    if not archive_path.exists():
        archive_path.write_bytes(archive)
    if not checksum_path.exists():
        checksum_path.write_bytes(checksums)
    source = {
        "name": "F1DB", "url": "https://github.com/f1db/f1db",
        "release": tag, "published_at": release["published_at"],
        "release_url": release["html_url"], "download_url": url,
        "checksum_url": checksums_url, "sha256": expected,
        "license": "CC-BY-4.0", "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "attribution": "Contains information from F1DB, licensed under CC BY 4.0.",
        "modifications": "Filtered to pre-weekend completed races and aggregated by "
                         "venue, driver, constructor and historical teammate pairing.",
    }
    return data, source


def _utc_date(event):
    sessions = [s for s in event.get("sessions", []) if s["label"] == "Race"]
    if len(sessions) == 1:
        session = sessions[0]
        start = dt.datetime.fromisoformat(
            session["date"] + "T" + session["time"] + session["gmt_offset"])
        if session["date"] != event["race_date"]:
            raise ValueError(f"Calendar race date disagrees with session: {event['slug']}")
        return start.astimezone(UTC).date().isoformat()
    if sessions:
        raise ValueError(f"Ambiguous calendar Race session: {event['slug']}")
    return event["race_date"]


def _expected(events, now):
    return [event["slug"] for event in events if _utc_date(event) < now.date().isoformat()]


def _identities(rows):
    result = {row["id"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError("Duplicate F1DB identity")
    return result


def map_events(events, races, year):
    """Exact season/round mapping, independently validated venue, GP and date."""
    mapped = {}
    for event in events:
        candidates = [r for r in races if r["year"] == year and r["round"] == event["round"]]
        if len(candidates) != 1:
            raise ValueError(f"Missing/ambiguous F1DB year+round: {event['slug']}")
        race = candidates[0]
        venue = VENUES.get(event["location"])
        if not venue or venue != race["circuitId"]:
            raise ValueError(f"Unmapped or conflicting venue: {event['slug']} / {event['location']}")
        if GP_IDS.get(event["slug"], event["slug"]) != race["grandPrixId"]:
            raise ValueError(f"Grand Prix identity mismatch: {event['slug']}")
        if race["date"] != _utc_date(event):
            raise ValueError(f"Race date mismatch: {event['slug']}")
        if event["slug"] in mapped:
            raise ValueError("Duplicate calendar slug")
        mapped[event["slug"]] = race
    return mapped


def _normal(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text).lower() if c.isalnum())


def season_drivers(data, standings, year):
    drivers = _identities(data["drivers"])
    entrants = {row["driverId"] for row in data["seasons-drivers"] if row["year"] == year}
    minimum = 22 if year >= 2026 else 20
    if (len(standings.get("drivers", [])) < minimum or standings.get("year") != year):
        raise ValueError("Official local season standings are missing or have wrong year")
    selected = []
    for row in standings["drivers"]:
        matches = [drivers[identity] for identity in entrants
                   if drivers[identity]["abbreviation"] == row[2]]
        if len(matches) != 1:
            raise ValueError(f"Ambiguous/unmapped season driver code: {row[2]}")
        driver = matches[0]
        # Official display names can omit 'Jr' but must not map by reused code alone.
        official = _normal(row[1])
        names = {_normal(driver.get(key, "")) for key in ("name", "fullName")}
        if not any(official == name or name == official + "jr" for name in names):
            raise ValueError(f"Season driver name mismatch: {row[1]}")
        selected.append({"id": driver["id"], "name": row[1], "code": row[2]})
    if len({d["id"] for d in selected}) != len(selected):
        raise ValueError("Duplicate official season driver")
    return selected


def _state(row, qualifying=False):
    if row is None:
        return "absent"
    text = str(row["positionText"]).upper()
    if text in DISQUALIFIED:
        return "dsq"
    if text in NO_START:
        return "dns"
    if qualifying and not any(row.get(key) for key in ("time", "q1", "q2", "q3")):
        return "no-time"
    return "classified" if row.get("positionNumber") is not None else "unclassified"


def _started(row):
    if "_participation" in row:
        return row["_participation"]
    text = str(row["positionText"]).upper()
    if text in NO_START:
        return False
    if text in DISQUALIFIED:
        return True if row.get("laps") else None
    return text.isdigit() or text in {"DNF", "NC"}


def reconcile_results(data):
    """Validate independent coverage and resolve participation without guessing.

    F1DB erases race/grid details for some retrospective exclusions (notably
    Tyrrell in 1984), but retains season entry/start counts. Only an all-or-none
    allocation of the remaining starts identifies individual unknown events.
    """
    rows = [{key: value for key, value in row.items() if key != "_participation"}
            for row in data["races-race-results"]]
    by_race, by_season, by_car = defaultdict(list), defaultdict(list), defaultdict(list)
    for row in rows:
        by_race[row["raceId"]].append(row)
        by_season[(row["year"], row["driverId"])].append(row)
        by_car[(row["raceId"], row["constructorId"], row["driverNumber"])].append(row)
    for race_id, entries in by_race.items():
        orders = [row["positionDisplayOrder"] for row in entries]
        if sorted(orders) != list(range(1, len(entries) + 1)):
            raise ValueError(f"Partial/invalid classification display order: {race_id}")
    identities = {(row["raceId"], row["driverId"], row["constructorId"], row["driverNumber"])
                  for row in rows}
    for grid in data["races-starting-grid-positions"]:
        identity = (grid["raceId"], grid["driverId"], grid["constructorId"], grid["driverNumber"])
        if identity not in identities:
            raise ValueError(f"Partial race classification: starting-grid entrant missing: {identity}")
    totals = {(row["year"], row["driverId"]): row for row in data["seasons-drivers"]}
    if len(totals) != len(data["seasons-drivers"]):
        raise ValueError("Duplicate F1DB season-driver totals")
    for key in set(by_season) | set(totals):
        entries = by_season.get(key, [])
        total = totals.get(key)
        if total is None or any(not isinstance(total.get(field), int) or total[field] < 0
                                for field in ("totalRaceEntries", "totalRaceStarts")):
            raise ValueError(f"Missing/invalid independent season entry/start totals: {key}")
        events = {row["raceId"] for row in entries}
        if len(events) != total["totalRaceEntries"]:
            raise ValueError(f"Partial race classification: season-entry total mismatch: {key}")
        for row in entries:
            if _started(row) is None and row.get("sharedCar"):
                car = by_car[(row["raceId"], row["constructorId"], row["driverNumber"])]
                if any(_started(peer) is True for peer in car):
                    row["_participation"] = True
        known = {row["raceId"] for row in entries if _started(row) is True}
        unknown_rows = [row for row in entries if _started(row) is None]
        unknown_events = {row["raceId"] for row in unknown_rows} - known
        remaining = total["totalRaceStarts"] - len(known)
        if remaining not in (0, len(unknown_events)):
            raise ValueError(f"Unresolved participation or inconsistent season-start total: {key}")
        for row in unknown_rows:
            if row["raceId"] in known:
                raise ValueError(f"Unresolved disqualified car participation: {key}, {row['raceId']}")
            row["_participation"] = bool(remaining)
        starts = {row["raceId"] for row in entries if _started(row) is True}
        if len(starts) != total["totalRaceStarts"]:
            raise ValueError(f"Independent season-start total mismatch: {key}")
    return rows


def compare(a, b, qualifying=False):
    states = [_state(row, qualifying) for row in (a, b)]
    positions = [row.get("positionNumber") if row else None for row in (a, b)]
    winner, reason = None, ""
    if "absent" in states:
        reason = "Missing driver in published table"
    elif any(state in {"dns", "dsq", "no-time"} for state in states):
        reason = "DNS, disqualification or no qualifying time"
    elif all(position is not None for position in positions):
        if positions[0] == positions[1]:
            reason = "Equal classification position"
        else:
            winner = int(positions[1] < positions[0])
    elif not qualifying and any(position is not None for position in positions):
        winner = int(positions[0] is None)
    else:
        reason = "Both unclassified or no comparable positions"
    return {"positions": positions, "statuses": states, "winner": winner, "reason": reason,
            "raw_positions": [row["positionText"] if row else None for row in (a, b)]}


def _evidence(race, gps):
    return {"race_id": race["id"], "year": race["year"], "date": race["date"],
            "name": gps[race["grandPrixId"]]["fullName"],
            "grand_prix_id": race["grandPrixId"], "circuit_id": race["circuitId"],
            "url": (f"https://github.com/f1db/f1db/tree/main/src/data/seasons/"
                    f"{race['year']}/races/{race['round']:02d}-{race['grandPrixId']}")}


def teammate_history(races, results, qualifying, drivers, constructors, gps, limit=10):
    scope = races[-limit:]
    pairs, excluded = {}, []
    for race in scope:
        sessions = {"Race": results[race["id"]], "Qualifying": qualifying.get(race["id"], [])}
        teams = defaultdict(lambda: defaultdict(list))
        for label, rows in sessions.items():
            for row in rows:
                teams[row["constructorId"]][label].append(row)
        for team, tables in sorted(teams.items()):
            entrants = {row["driverId"] for rows in tables.values() for row in rows}
            reason = ""
            if any(row.get("sharedCar") for rows in tables.values() for row in rows):
                reason = "Shared drive"
            elif len(entrants) != 2:
                reason = "More than two entrants or replacement pairing" if len(entrants) > 2 else "Only one entrant"
            elif any(len(rows) != len({r["driverId"] for r in rows}) for rows in tables.values()):
                reason = "Multiple cars for one driver"
            if reason:
                excluded.append({"race_id": race["id"], "year": race["year"],
                                 "team": constructors[team]["name"], "reason": reason})
                continue
            ids = tuple(sorted(entrants))
            pair = pairs.setdefault((team, ids), {
                "constructor_id": team, "team": constructors[team]["name"],
                "drivers": [{"id": identity, "name": drivers[identity]["name"],
                             "code": drivers[identity]["abbreviation"]} for identity in ids],
                "Qualifying": {"wins": [0, 0], "excluded": 0},
                "Race": {"wins": [0, 0], "excluded": 0}, "events": [],
            })
            evidence = _evidence(race, gps)
            for label in sessions:
                indexed = {row["driverId"]: row for row in tables.get(label, [])}
                comparison = compare(*(indexed.get(identity) for identity in ids),
                                     qualifying=label == "Qualifying")
                if comparison["winner"] is None:
                    pair[label]["excluded"] += 1
                else:
                    pair[label]["wins"][comparison["winner"]] += 1
                evidence[label] = comparison
            pair["events"].append(evidence)
    return {"limit": limit, "races": len(scope),
            "first_year": scope[0]["year"] if scope else None,
            "last_year": scope[-1]["year"] if scope else None,
            "pairs": list(pairs.values()), "excluded_events": excluded}


def _stats(identity, name, **extra):
    return {"id": identity, "name": name, "starts": 0, "wins": 0, "podiums": 0,
            "poles": 0, "best_finish": None, "best_years": [], "win_years": [], **extra}


def _award(stats, rows, year):
    best = min((r["positionNumber"] for r in rows if _state(r) == "classified"), default=None)
    if best is not None:
        if stats["best_finish"] is None or best < stats["best_finish"]:
            stats["best_finish"], stats["best_years"] = best, [year]
        elif best == stats["best_finish"] and year not in stats["best_years"]:
            stats["best_years"].append(year)
    if best == 1:
        stats["wins"] += 1
        if year not in stats["win_years"]:
            stats["win_years"].append(year)
    if best is not None and best <= 3:
        stats["podiums"] += 1
    if any(r.get("polePosition") is True for r in rows):
        stats["poles"] += 1


def _leaders(rows):
    maximum = max((row["wins"] for row in rows), default=0)
    return [row["id"] for row in rows if maximum and row["wins"] == maximum]


def make_profile(event, race, completed, results, qualifying, data, roster):
    circuits, gps = data["circuits"], data["grands-prix"]
    drivers, constructors = data["drivers"], data["constructors"]
    prior = [r for r in completed if r["date"] < event["race_date"]]
    venue = [r for r in prior if r["circuitId"] == race["circuitId"]]
    named = [r for r in prior if r["grandPrixId"] == race["grandPrixId"]]
    by_driver, by_constructor = {}, {}
    for driver in roster:
        by_driver[driver["id"]] = _stats(driver["id"], driver["name"],
                                        code=driver["code"], season_driver=True)
    winners, pole_races, pole_wins = [], 0, 0
    for old in venue:
        rows = results[old["id"]]
        driver_rows, car_rows = defaultdict(list), defaultdict(list)
        for row in rows:
            driver_rows[row["driverId"]].append(row)
            car_rows[(row["constructorId"], row["driverNumber"])].append(row)
        for identity, entries in driver_rows.items():
            stat = by_driver.setdefault(identity, _stats(identity, drivers[identity]["name"],
                                        code=drivers[identity]["abbreviation"], season_driver=False))
            stat["starts"] += int(any(_started(row) for row in entries))
            _award(stat, entries, old["year"])
        for (identity, _), entries in car_rows.items():
            stat = by_constructor.setdefault(identity, _stats(identity, constructors[identity]["name"]))
            stat["starts"] += int(any(_started(row) for row in entries))
            _award(stat, entries, old["year"])
        known_pole = any(row.get("polePosition") is True for row in rows)
        pole_races += int(known_pole)
        pole_wins += int(known_pole and any(row.get("polePosition") is True
                                         and row["positionNumber"] == 1 for row in rows))
        for row in rows:
            if row["positionNumber"] == 1:
                winners.append({**_evidence(old, gps), "driver_id": row["driverId"],
                                "driver": drivers[row["driverId"]]["name"],
                                "constructor_id": row["constructorId"],
                                "constructor": constructors[row["constructorId"]]["name"],
                                "grid": row.get("gridPositionNumber"),
                                "pole": row.get("polePosition")})
    for stat in by_driver.values():
        stat["history_status"] = ("no-start" if not stat["starts"] else
                                  "classified" if stat["best_finish"] is not None else "unclassified")
    driver_stats = sorted(by_driver.values(), key=lambda x: (-x["wins"], -x["podiums"], x["name"]))
    constructor_stats = sorted(by_constructor.values(), key=lambda x: (-x["wins"], -x["podiums"], x["name"]))

    def breakdown(races, field, identities, name_field):
        grouped = defaultdict(list)
        for item in races:
            grouped[item[field]].append(item["year"])
        return [{"id": identity, "name": identities[identity][name_field],
                 "count": len(years), "years": sorted(set(years)),
                 "first_year": min(years), "last_year": max(years)}
                for identity, years in sorted(grouped.items(), key=lambda item: (min(item[1]), item[0]))]

    return {
        "slug": event["slug"],
        "event": {**_evidence(race, gps), "date": event["race_date"], "round": race["round"]},
        "circuit": {"id": race["circuitId"], "name": circuits[race["circuitId"]]["fullName"]},
        "cutoff_date": event["race_date"], "completed_races": len(venue),
        "venue_edition": len(venue) + 1,
        "grand_prix": {"id": race["grandPrixId"], "name": gps[race["grandPrixId"]]["fullName"],
                       "completed_races": len(named), "edition": len(named) + 1,
                       "years": sorted({r["year"] for r in named}),
                       "venues": breakdown(named, "circuitId", circuits, "fullName")},
        "names_at_venue": breakdown(venue, "grandPrixId", gps, "fullName"),
        "first_race": _evidence(venue[0], gps) if venue else None,
        "last_race": _evidence(venue[-1], gps) if venue else None,
        "drivers": driver_stats, "constructors": constructor_stats,
        "most_driver_wins": _leaders(driver_stats),
        "most_constructor_wins": _leaders(constructor_stats),
        "recent_winners": [w for w in reversed(winners) if w["race_id"] in {r["id"] for r in venue[-10:]}],
        "wins_from_pole": {"wins": pole_wins, "races": pole_races},
        "distinct_winners": len({w["driver_id"] for w in winners}),
        "teammates": teammate_history(venue, results, qualifying, drivers, constructors, gps),
    }


def build_snapshot(data, calendar, standings, source, now):
    year, events = int(calendar["year"]), calendar["events"]
    if not events or len({event["round"] for event in events}) != len(events):
        raise ValueError("Empty or duplicate-round calendar")
    indexed = {name: _identities(data[name]) for name in ("drivers", "constructors", "circuits", "grands-prix")}
    races = _identities(data["races"])
    mapped = map_events(events, data["races"], year)
    roster = season_drivers(data, standings, year)
    results, qualifying = defaultdict(list), defaultdict(list)
    for rows, target in ((reconcile_results(data), results), (data["races-qualifying-results"], qualifying)):
        for row in rows:
            if row["raceId"] not in races:
                raise ValueError("Classification references unknown race")
            race = races[row["raceId"]]
            if row["year"] != race["year"] or row["round"] != race["round"]:
                raise ValueError("Classification season/round disagrees with race")
            if row["driverId"] not in indexed["drivers"] or row["constructorId"] not in indexed["constructors"]:
                raise ValueError("Classification references unknown driver/constructor")
            if row.get("positionNumber") is not None and (
                    not isinstance(row["positionNumber"], int) or row["positionNumber"] < 1):
                raise ValueError("Invalid numeric classification position")
            target[row["raceId"]].append(row)
    completed = []
    for race in sorted(races.values(), key=lambda r: (r["date"], r["id"])):
        if race["year"] < 1950 or race["date"] >= now.date().isoformat():
            continue
        if race["circuitId"] not in indexed["circuits"] or race["grandPrixId"] not in indexed["grands-prix"]:
            raise ValueError("Race references unknown circuit/Grand Prix")
        rows = results.get(race["id"], [])
        if not rows:
            continue
        if not any(row["positionNumber"] == 1 for row in rows):
            raise ValueError(f"Partial race classification (no winner): {race['id']}")
        if race["year"] == year:
            minimum = 22 if year >= 2026 else 20
            if len(rows) < minimum or len({r["driverId"] for r in rows}) != len(rows):
                raise ValueError(f"Partial/duplicate current-season classification: {race['id']}")
            if sum(r["positionNumber"] == 1 for r in rows) != 1:
                raise ValueError(f"Invalid current-season winner: {race['id']}")
        completed.append(race)
    completed_ids = {race["id"] for race in completed}
    expected = _expected(events, now)
    missing = [slug for slug in expected if mapped[slug]["id"] not in completed_ids]
    if missing:
        raise ValueError("Stale/partial F1DB current-season race coverage: " + ", ".join(missing))
    return {
        "schema_version": SCHEMA_VERSION, "year": year, "generated_at": now.isoformat(timespec="seconds"),
        "checked_at": now.isoformat(timespec="seconds"), "source": source, "methodology": METHOD,
        "season_drivers": roster, "coverage": {"completed_calendar_events": expected,
                                              "latest_completed_date": max((r["date"] for r in completed), default=None)},
        "profiles": {event["slug"]: make_profile(event, mapped[event["slug"]], completed,
                                                 results, qualifying, indexed, roster) for event in events},
    }


def refresh(year=2026, now=None, force=False, root=None, cache_dir=None):
    now = (now or dt.datetime.now(UTC)).astimezone(UTC)
    root = Path(root) if root is not None else ROOT
    cache = Path(cache_dir) if cache_dir is not None else root / "__pycache__" / "circuit-history"
    path = root / "data" / f"circuit_history_{year}.json"
    status_path = root / "data" / f"circuit_history_{year}_status.json"
    try:
        calendar = _read(root / "data" / f"calendar_{year}.json")
        standings = _read(root / "data" / f"standings_{year}.json")
        if int(calendar.get("year", 0)) != year:
            raise ValueError("Calendar season mismatch")
        previous = _read(path)
        fingerprint = hashlib.sha256(json.dumps(
            {"build": BUILD_VERSION, "calendar": calendar,
             "roster": sorted((r[1], r[2]) for r in standings.get("drivers", [])),
             "expected": _expected(calendar["events"], now)},
            sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        release = _release(cache, now, force)
        if (not force and previous.get("schema_version") == SCHEMA_VERSION
                and previous.get("input_sha256") == fingerprint
                and previous.get("source", {}).get("release") == release["tag_name"]):
            _write(status_path, {"ok": True, "checked_at": now.isoformat(timespec="seconds"),
                                 "release": release["tag_name"], "cached": True, "error": ""})
            return previous
        data, source = _database(release, cache)
        record = build_snapshot(data, calendar, standings, source, now)
        if previous:
            lost = set(previous.get("profiles", {})) - set(record["profiles"])
            if lost:
                raise ValueError(f"Refresh lost previously published profiles: {sorted(lost)}")
            for slug, profile in record["profiles"].items():
                old = previous.get("profiles", {}).get(slug, {})
                if (old.get("cutoff_date") == profile["cutoff_date"]
                        and old.get("circuit", {}).get("id") == profile["circuit"]["id"]
                        and old.get("completed_races", 0) > profile["completed_races"]):
                    raise ValueError(f"Refresh lost recorded venue races: {slug}")
        record["input_sha256"] = fingerprint
        _write(path, record)
        _write(status_path, {"ok": True, "checked_at": now.isoformat(timespec="seconds"),
                             "release": release["tag_name"], "cached": False, "error": ""})
        return record
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        _write(status_path, {"ok": False, "checked_at": now.isoformat(timespec="seconds"),
                             "error": str(error), "retained_last_good": path.exists()})
        raise ValueError(f"Circuit history refresh failed; last good retained: {error}") from error


def context(ctx):
    year = int(ctx.get("year", 2026))
    slug = ctx.get("dir", ctx.get("slug", ""))
    try:
        record = _read(ROOT / "data" / f"circuit_history_{year}.json")
        if not record:
            raise ValueError("Circuit history snapshot missing; run python3 circuit_history.py")
        if record.get("schema_version") != SCHEMA_VERSION or record.get("year") != year:
            raise ValueError("Circuit history snapshot schema/season mismatch")
        profile = record["profiles"].get(slug)
        if not profile:
            raise ValueError(f"Circuit history profile missing: {slug}")
        if ctx.get("race_date") and ctx["race_date"] != profile["cutoff_date"]:
            raise ValueError("Circuit history cutoff disagrees with current calendar")
        if ctx.get("round_no") and ctx["round_no"] != profile["event"]["round"]:
            raise ValueError("Circuit history round disagrees with current calendar")
        status = _read(ROOT / "data" / f"circuit_history_{year}_status.json")
        error = status.get("error", "") if status.get("ok") is False else ""
        calendar = _read(ROOT / "data" / f"calendar_{year}.json")
        if calendar:
            missing = set(_expected(calendar["events"], dt.datetime.now(UTC))) - set(
                record.get("coverage", {}).get("completed_calendar_events", []))
            if missing:
                error = "History refresh needed after completed calendar races: " + ", ".join(sorted(missing))
        return {"profile": profile, "source": record["source"], "methodology": record["methodology"],
                "error": error, "generated_at": record["generated_at"],
                "checked_at": status.get("checked_at", record["checked_at"])}
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {"profile": {}, "source": {}, "methodology": METHOD, "error": str(error)}


def load_profile(ctx):
    return context(ctx)["profile"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--force", action="store_true", help="Recheck release metadata and rebuild aggregates")
    parser.add_argument("--cache-dir", type=Path, help="Optional persistent download cache (never committed)")
    args = parser.parse_args()
    try:
        record = refresh(args.year, force=args.force, cache_dir=args.cache_dir)
    except ValueError as error:
        print(f"! {error}", file=sys.stderr)
        return 1
    print(f"Circuit history: {len(record['profiles'])} profiles, {record['source']['release']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
