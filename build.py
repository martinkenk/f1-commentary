"""
F1 Commentary Hub — build driver.

Registers each Grand Prix (metadata + sessions + live-data sources + its content
module) and builds the whole multi-GP site. Re-run at any point across a weekend:
weather and session results refresh automatically, new content is picked up.

    python3 build.py

Engine:   f1lib.py         (shell, CSS, weather, results, index, build)
Content:  content_<gp>.py  (per-GP page prose)
"""
import f1lib
import content_hungary
import content_belgium

# Shared 13-item sidebar. Slugs (except "results", auto-built by the engine)
# must match the keys returned by each content module's build_pages().
def nav(circuit_label):
    return [
        ("overview",  "overview.html",  "bi-speedometer2",     "Overview",         "Weekend Overview"),
        ("circuit",   "circuit.html",   "bi-map",              "Circuit Guide",    f"{circuit_label} Circuit Guide"),
        ("results",   "results.html",   "bi-flag-fill",        "Results",          "Session Results"),
        ("tyres",     "tyres.html",     "bi-record-circle",    "Tyres & Strategy", "Tyres & Strategy"),
        ("rookies",   "rookies.html",   "bi-person-badge",     "Rookies & Line-up","Rookies & Line-ups"),
        ("standings", "standings.html", "bi-trophy",           "Standings & Form", "Championship & Form"),
        ("teams",     "teams.html",     "bi-people",           "Team Watch",       "Team Watch & News"),
        ("upgrades",  "upgrades.html",  "bi-tools",            "Upgrades",         "Car Development & Upgrades"),
        ("powerunit", "powerunit.html", "bi-lightning-charge", "Power Unit",       "Power Unit & Override"),
        ("facts",     "facts.html",     "bi-bar-chart",        "Facts & Records",  "Facts, Stats & Records"),
        ("moments",   "moments.html",   "bi-stars",            "Top Moments",      "Great Moments"),
        ("schedule",  "schedule.html",  "bi-calendar-week",    "Schedule & Weather","Schedule & Weather"),
        ("notes",     "notes.html",     "bi-mic",              "Commentary Notes", "Commentator's Cheat Sheet"),
    ]

HUNGARY = {
    "name": "Hungarian Grand Prix", "year": "2026", "flag": "🇭🇺",
    "circuit": "Hungaroring, Budapest", "round": "Round 14 of 24", "dir": "hungary",
    "lat": 47.5789, "lon": 19.2486,
    "tz_local": "Budapest (CEST)", "tz_east": "Tallinn (EEST)", "tz_offset": 1,
    "sessions": [
        ("Practice 1", "Fri 24 Jul", "2026-07-24", "13:30"),
        ("Practice 2", "Fri 24 Jul", "2026-07-24", "17:00"),
        ("Practice 3", "Sat 25 Jul", "2026-07-25", "12:30"),
        ("Qualifying", "Sat 25 Jul", "2026-07-25", "16:00"),
        ("Race",       "Sun 26 Jul", "2026-07-26", "15:00"),
    ],
    "race_id": "1291", "results_slug": "hungary",
    "nav": nav("Hungaroring"),
    "pages": content_hungary.build_pages,
}

BELGIUM = {
    "name": "Belgian Grand Prix", "year": "2026", "flag": "🇧🇪",
    "circuit": "Circuit de Spa-Francorchamps", "round": "Round 13 of 24", "dir": "belgium",
    "lat": 50.4372, "lon": 5.9714,
    "tz_local": "Spa (CEST)", "tz_east": "Tallinn (EEST)", "tz_offset": 1,
    "sessions": [
        ("Practice 1", "Fri 17 Jul", "2026-07-17", "13:30"),
        ("Practice 2", "Fri 17 Jul", "2026-07-17", "17:00"),
        ("Practice 3", "Sat 18 Jul", "2026-07-18", "12:30"),
        ("Qualifying", "Sat 18 Jul", "2026-07-18", "16:00"),
        ("Race",       "Sun 19 Jul", "2026-07-19", "15:00"),
    ],
    "race_id": "1290", "results_slug": "belgium",
    "nav": nav("Spa-Francorchamps"),
    "pages": content_belgium.build_pages,
}

if __name__ == "__main__":
    f1lib.build_all([HUNGARY, BELGIUM])
