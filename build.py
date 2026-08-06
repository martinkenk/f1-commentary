"""
F1 Commentary Hub — build driver.

Builds a weekend hub for every Grand Prix from ``FIRST_ROUND`` to the end of the
season. Rather than hand-writing a content module per race, the calendar scraped
by ``calendar.py`` (session times, circuit numbers, sprint format, track maps)
is combined with the reference material in ``circuits.py`` and rendered through
``content_generic``. Races that deserve bespoke treatment get it via ``BESPOKE``.

Re-run at any point across a weekend — weather, session results, news and
stewards' decisions all refresh, and pages that were waiting on a source fill
themselves in once it publishes.

    python3 build.py

Engine:   f1lib.py            (shell, CSS, weather, results, index, build)
Content:  content_<gp>.py     (bespoke per-GP prose)
          content_generic.py  (everything else, progressive disclosure)
Data:     data/calendar_2026.json  (refresh with: python3 calendar.py)
"""
import datetime
import json
import os
import urllib.parse

import f1lib
import circuits
import content_generic
import content_hungary
import content_belgium

ROOT = os.path.dirname(os.path.abspath(__file__))
SEASON = 2026

# The hub covers this round onwards. Earlier rounds are finished history and
# would only add build time; lower this to backfill them.
FIRST_ROUND = 10

# Races with hand-written prose. Everything else uses content_generic.
BESPOKE = {
    "hungary": content_hungary.build_pages,
    "belgium": content_belgium.build_pages,
}

# Standings carried into the generic pages until each race supplies its own.
LATEST_STANDINGS = {
    "drivers": content_belgium.DRIVER_ROWS,
    "ctors": content_belgium.CTOR_ROWS,
    "as_of": "the Belgian Grand Prix",
}

FLAGS = {
    "Australia": "🇦🇺", "China": "🇨🇳", "Japan": "🇯🇵", "United States": "🇺🇸",
    "Canada": "🇨🇦", "Monaco": "🇲🇨", "Spain": "🇪🇸", "Austria": "🇦🇹",
    "Great Britain": "🇬🇧", "Belgium": "🇧🇪", "Hungary": "🇭🇺",
    "Netherlands": "🇳🇱", "Italy": "🇮🇹", "Azerbaijan": "🇦🇿",
    "Singapore": "🇸🇬", "Mexico": "🇲🇽", "Brazil": "🇧🇷", "Las Vegas": "🇺🇸",
    "Qatar": "🇶🇦", "Abu Dhabi": "🇦🇪", "Miami": "🇺🇸", "Bahrain": "🇧🇭",
}
# The 2026 Bahrain Grand Prix is staged at Sepang, so the venue flag is the
# honest one to show on the card next to "Kuala Lumpur".
FLAG_BY_SLUG = {"bahrain": "🇲🇾"}

# European summer time in 2026: 29 March to 25 October.
_EU_DST = (datetime.date(2026, 3, 29), datetime.date(2026, 10, 25))


def _tallinn_offset(day):
    """UTC offset for Tallinn on a given date: +3 in EEST, +2 in EET."""
    return 3 if _EU_DST[0] <= day < _EU_DST[1] else 2


def _gmt_offset_hours(text):
    """'-05:00' -> -5.0"""
    sign = -1 if text.startswith("-") else 1
    hh, mm = text.lstrip("+-").split(":")
    return sign * (int(hh) + int(mm) / 60)


def tz_offset(event):
    """Hours to add to circuit-local time to get Tallinn time.

    Taken from the race day so a single figure covers the weekend; the engine
    flags any session that lands on a different date in Tallinn.
    """
    sessions = event.get("sessions") or []
    if not sessions:
        return 1
    race_day = datetime.date.fromisoformat(event["race_date"])
    local = _gmt_offset_hours(sessions[-1].get("gmt_offset", "+00:00"))
    off = _tallinn_offset(race_day) - local
    return int(off) if off == int(off) else off


def nav(circuit_label):
    """The shared 17-item sidebar. Slugs must match the keys a content module
    returns, except the ones the engine auto-builds (results, news, h2h,
    reliability, penalties)."""
    return [
        ("overview",  "overview.html",  "bi-speedometer2",     "Overview",         "Weekend Overview"),
        ("news",      "news.html",      "bi-newspaper",        "Weekend News",     "Weekend News & Session Reports"),
        ("circuit",   "circuit.html",   "bi-map",              "Circuit Guide",    f"{circuit_label} Circuit Guide"),
        ("results",   "results.html",   "bi-flag-fill",        "Results",          "Session Results"),
        ("tyres",     "tyres.html",     "bi-record-circle",    "Tyres & Strategy", "Tyres & Strategy"),
        ("rookies",   "rookies.html",   "bi-person-badge",     "Rookies & Line-up","Rookies & Line-ups"),
        ("standings", "standings.html", "bi-trophy",           "Standings & Form", "Championship & Form"),
        ("h2h",       "h2h.html",       "bi-arrow-left-right", "Head-to-Head",     "Team-mate Head-to-Head"),
        ("teams",     "teams.html",     "bi-people",           "Team Watch",       "Team Watch & News"),
        ("upgrades",  "upgrades.html",  "bi-tools",            "Upgrades",         "Car Development & Upgrades"),
        ("powerunit", "powerunit.html", "bi-lightning-charge", "Power Unit",       "Power Unit & Override"),
        ("penalties", "penalties.html", "bi-hammer",           "Penalties",        "Penalties & Stewards"),
        ("reliability","reliability.html","bi-wrench-adjustable","Reliability & Pits","Reliability & Pit Stops"),
        ("facts",     "facts.html",     "bi-bar-chart",        "Facts & Records",  "Facts, Stats & Records"),
        ("moments",   "moments.html",   "bi-stars",            "Top Moments",      "Great Moments"),
        ("schedule",  "schedule.html",  "bi-calendar-week",    "Schedule & Weather","Schedule & Weather"),
        ("notes",     "notes.html",     "bi-mic",              "Commentary Notes", "Commentator's Cheat Sheet"),
    ]


def fia_url(event):
    """FIA event-document URL. The page only appears in the race week, so for
    a distant round this is a forward link rather than a live one."""
    name = urllib.parse.quote(event["name"])
    return ("https://www.fia.com/documents/championships/"
            "fia-formula-one-world-championship-14/season/season-2026-2072/"
            f"event/{name}")


def sessions_for(event):
    """Calendar sessions -> the engine's (label, day-label, iso-date, HH:MM)."""
    out = []
    for s in event["sessions"]:
        day = datetime.date.fromisoformat(s["date"])
        out.append((s["label"], day.strftime("%a %-d %b"), s["date"], s["time"]))
    return out


def make_gp(event):
    slug = event["slug"]
    ref = circuits.get(slug)
    lat, lon = ref.get("coords", (0.0, 0.0))
    circuit = ref.get("circuit") or event["location"]
    label = circuit.split(",")[0]
    return {
        "name": event["name"],
        "year": str(SEASON),
        "flag": FLAG_BY_SLUG.get(slug) or FLAGS.get(event["country"], "🏁"),
        "circuit": circuit,
        "round": f'Round {event["round"]} of {event["total_rounds"]}',
        "round_no": event["round"],
        "dir": slug,
        "lat": lat, "lon": lon,
        "tz_local": ref.get("tz_local", f'{event["location"]} (local)'),
        "tz_east": ("Tallinn (EEST)"
                    if _tallinn_offset(datetime.date.fromisoformat(event["race_date"])) == 3
                    else "Tallinn (EET)"),
        "tz_offset": tz_offset(event),
        "sessions": sessions_for(event),
        "race_id": event.get("race_id") or "",
        "results_slug": event.get("results_slug", slug),
        "race_date": event["race_date"],
        "fia_url": fia_url(event),
        "nav": nav(label),
        "cal": event,
        "ref": ref,
        "standings": LATEST_STANDINGS,
        "pages": BESPOKE.get(slug, content_generic.build_pages),
    }


def season_gps():
    with open(os.path.join(ROOT, "data", f"calendar_{SEASON}.json")) as f:
        events = json.load(f)["events"]
    return [make_gp(e) for e in events if e["round"] >= FIRST_ROUND]


if __name__ == "__main__":
    f1lib.build_all(season_gps())
