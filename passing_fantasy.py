"""Validated race-only aggregates from the public F1 Fantasy application feeds."""
import datetime as dt
import hashlib
import json
import re

from circuit_history import _normal


BASE = "https://fantasy.formula1.com"
CONFIG = BASE + "/feeds/apps/web_config.json"
SCHEDULE = BASE + "/feeds/schedule/raceday_en.json"
RULES = BASE + "/feeds/translations/web/en.json"
SERIES_ID = "f1-fantasy"
SOURCE = {
    "name": "Official F1 Fantasy scoring overtakes",
    "url": BASE + "/en/statistics/details?tab=driver&filter=overTakepoints",
    "rules_url": RULES,
    "kind": "automatic",
    "methodology": (
        "F1 Fantasy-defined legal on-track passes, excluding a passed car entering/in the "
        "pit lane, suffering car failure or going unreasonably slowly. The rules do not "
        "promise to exclude lap one. Race scoring events only, not positions gained or "
        "Sprint points; not comparable with lap-one-excluded community counts."
    ),
    "attribution": (
        "Factual race aggregates from the official Formula 1 Fantasy scoring feeds. "
        "Scores may be revised after validation; these are not FIA overtaking statistics. "
        "No open redistribution license was established for the source."
    ),
}
# A definition change must be reviewed before appending to the same series.
RULE = ("** Overtakes are considered valid when one driver legally passes another on track, "
        "and the driver passed was not entering or in the pit lane or suffering a car failure "
        "or going unreasonably slow.")
VENUE_ALIASES = {
    "melbourne": ("Albert Park Grand Prix Circuit",),
    "zandvoort": ("Circuit Zandvoort",),
    "las-vegas": ("Las Vegas Strip Circuit",),
}


def _integer(value, label):
    if type(value) is not int or value < 1:
        raise ValueError(f"Invalid Fantasy {label}")
    return value


def _timestamp(value):
    stamp = dt.datetime.fromisoformat(value)
    if stamp.tzinfo is None:
        raise ValueError("Fantasy session timestamp has no timezone")
    return stamp


def _score(record):
    """Absent bonus means zero only in a complete, reconciled scored race record."""
    stats = record["StatsWise"]
    if not isinstance(stats, list) or not stats:
        raise ValueError("Missing Fantasy race scoring breakdown")
    values = {}
    for stat in stats:
        if not isinstance(stat, dict) or not isinstance(stat.get("Event"), str):
            raise ValueError("Invalid Fantasy scoring event schema")
        event, value = stat["Event"].strip(), stat["Value"]
        if (not event or event in values or type(value) not in (int, float)
                or not float(value).is_integer()):
            raise ValueError("Duplicate or invalid Fantasy scoring event")
        values[event] = value
        if "overtake" in event.lower() and event != "race overtake bonus":
            raise ValueError("Fantasy overtaking event changed; review required")
    # The public feed omits Total when the reconciled score is exactly zero.
    if (values.get("Total", 0) != sum(v for k, v in values.items() if k != "Total")
            or len({"Race Position", "Race not classified", "Race disqualified"} & values.keys()) != 1):
        raise ValueError("Incomplete or unreconciled Fantasy race score")
    bonuses = [stat for stat in stats if stat["Event"].strip() == "race overtake bonus"]
    if not bonuses:
        return 0
    frequency = bonuses[0]["Frequency"]
    if (not isinstance(frequency, str) or not re.fullmatch(r"0|[1-9]\d*", frequency)
            or int(frequency) != bonuses[0]["Value"]):
        raise ValueError("Invalid Fantasy overtake frequency/scoring rule")
    return int(frequency)


def collect(fetch, data, now):
    """Require every completed race's actual F1DB entrants, including replacements."""
    evidence = []

    def get(url):
        text = fetch(url)
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise ValueError("Invalid Fantasy JSON object")
        evidence.append({"url": url, "sha256": hashlib.sha256(text.encode()).hexdigest()})
        return payload

    tour = _integer(get(CONFIG)["tourId"], "tour ID")
    rules = get(RULES)
    rule = rules.get("rules_title_9_intro_5")
    if not isinstance(rule, str) or " ".join(rule.split()) != RULE:
        raise ValueError("Fantasy overtaking definition changed; review required")
    schedule = get(SCHEDULE)["Data"]["Value"]
    statistics_url = BASE + f"/feeds/statistics/drivers_{tour}.json"
    statistics = get(statistics_url)["Data"]
    year = now.year
    if statistics["season"] != str(year):
        raise ValueError("Fantasy statistics are not for the current season")
    categories = [s for s in statistics["statistics"] if s["config"]["key"] == "overTakepoints"]
    if len(categories) != 1:
        raise ValueError("Missing/duplicate Fantasy overtake participant list")
    players = categories[0]["participants"]
    if not isinstance(players, list) or not players or len(players) > 60:
        raise ValueError("Invalid Fantasy participant list")
    player_names = {}
    for player in players:
        identity, name = player["playerid"], player["playername"]
        if (not isinstance(identity, str) or not re.fullmatch(r"[1-9]\d*", identity)
                or identity in player_names or not isinstance(name, str) or not name.strip()):
            raise ValueError("Duplicate/invalid Fantasy player identity")
        player_names[identity] = name

    db_races = {r["id"]: r for r in data["races"]
                if r["year"] == year and r["date"] <= now.date().isoformat()}
    entrants = {}
    for row in data["races-race-results"]:
        if row["raceId"] in db_races:
            entrants.setdefault(row["raceId"], set()).add(row["driverId"])
    circuits = {c["id"]: c for c in data["circuits"]}
    races, seen_sessions, matched = {}, set(), set()
    if not isinstance(schedule, list) or not schedule:
        raise ValueError("Missing Fantasy schedule")
    for session in schedule:
        if session["SessionType"] != "Race":
            continue
        if session["TourId"] != tour or session["Season"] != str(year):
            raise ValueError("Fantasy schedule season/tour mismatch")
        identity = _integer(session["RaceId"], "race session ID")
        if identity in seen_sessions:
            raise ValueError("Duplicate Fantasy race session")
        seen_sessions.add(identity)
        start = _timestamp(session["SessionStartDateISO8601"])
        end = _timestamp(session["SessionEndDateISO8601"])
        if start >= end:
            raise ValueError("Invalid Fantasy session interval")
        if session["MatchStatus"] != "4":
            continue
        if end > now:
            raise ValueError("Fantasy claims a future race is completed")
        date = start.astimezone(dt.timezone.utc).date().isoformat()
        candidates = []
        for race_id in entrants:
            race = db_races[race_id]
            circuit = circuits[race["circuitId"]]
            names = [circuit["name"], circuit["fullName"],
                     *VENUE_ALIASES.get(circuit["id"], ())]
            if date == race["date"] and _normal(session["CircuitOfficialName"]) in {
                    _normal(name) for name in names}:
                candidates.append(race)
        if len(candidates) != 1 or candidates[0]["id"] in matched:
            raise ValueError(f"No unique completed F1DB venue/date for Fantasy session {identity}")
        race = candidates[0]
        matched.add(race["id"])
        races[identity] = (session, race)
    if matched != entrants.keys():
        raise ValueError("Fantasy schedule omits a completed F1DB race")

    drivers = {d["id"]: d for d in data["drivers"]}
    scores = {identity: {} for identity in races}
    for player_id, name in player_names.items():
        url = BASE + f"/feeds/popup/playerstats_{player_id}.json"
        player = get(url)["Value"]
        if (type(player["PlayerId"]) is not int or player["PlayerId"] != int(player_id)
                or player["PlayerSkill"] != 1 or not isinstance(player["MatchWiseStats"], list)):
            raise ValueError("Fantasy player response identity/type mismatch")
        seen = set()
        for meeting in player["MatchWiseStats"]:
            if meeting["TourId"] != tour:
                continue
            for record in meeting["RaceDayWise"]:
                if record["Season"] != str(year) or record["SessionType"] != "Race":
                    continue
                identity = _integer(record["RaceDayId"], "player race session ID")
                if identity not in races:
                    if record["MatchStatus"] == "4" and record["IsPlayed"] == 1:
                        raise ValueError("Scored Fantasy race absent from completed schedule")
                    continue
                if identity in seen:
                    raise ValueError("Duplicate Fantasy player race record")
                seen.add(identity)
                if record["IsPlayed"] not in (0, 1):
                    raise ValueError("Invalid Fantasy participation flag")
                if record["IsPlayed"] == 0:
                    continue
                session, race = races[identity]
                if (record["MatchStatus"] != "4"
                        or record["CircuitOfficialName"] != session["CircuitOfficialName"]
                        or _timestamp(record["SessionStartDate"]) !=
                        _timestamp(session["SessionStartDateISO8601"])):
                    raise ValueError("Fantasy player session identity/completion mismatch")
                candidates = [
                    driver_id for driver_id in entrants[race["id"]]
                    if any(_normal(drivers[driver_id].get(key, "")) in
                           {_normal(name), _normal(name) + "jr"} for key in ("name", "fullName"))
                ]
                if len(candidates) != 1:
                    raise ValueError(f"Unmapped Fantasy race entrant: {name}")
                driver_id = candidates[0]
                if driver_id in scores[identity]:
                    raise ValueError(f"Duplicate Fantasy entries for race driver {driver_id}")
                scores[identity][driver_id] = _score(record)

    rows = []
    for identity, (session, race) in races.items():
        if scores[identity].keys() != entrants[race["id"]]:
            missing = entrants[race["id"]] - scores[identity].keys()
            raise ValueError(f"Incomplete Fantasy entrants for {race['date']}: {sorted(missing)}")
        rows.append({
            "series_id": SERIES_ID, "race_id": race["id"], "date": race["date"],
            "circuit_id": race["circuitId"], "overtakes": sum(scores[identity].values()),
            "source_url": SOURCE["url"], "schedule_url": SCHEDULE,
            "tour_id": tour, "season": year, "session_id": identity,
            "participants": len(scores[identity]), "scoring_state": "subject-to-revision",
        })
    return rows, {"tour_id": tour, "season": year, "feeds": evidence}
