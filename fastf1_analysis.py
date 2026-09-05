"""FastF1-powered session pace analysis.

Pulls real lap timing + car telemetry for completed sessions of the current
season via the FastF1 library (https://docs.fastf1.dev/) and distils it into
a small JSON summary per session:

  * Fastest-lap leaderboard, each driver's *theoretical optimal lap* (their
    own best sector times added together) and the gap between the two —
    this surfaces whether a driver's headline time actually reflected their
    true pace, or whether they left time on the table in one sector.
  * Long-run ("race sim") pace: laps grouped by stint, restricted to
    green-flag, non-in/out laps, with the single slowest lap of each stint
    dropped as an outlier before averaging — a rough proxy for what teams
    call "clean average pace" on a given tyre.
  * A speed-vs-distance and delta-vs-fastest-lap trace for the session's top
    drivers' fastest laps, downsampled onto a shared distance grid and
    shipped as plain JSON (not a static image) so the Results page can
    render it as an interactive, per-driver-toggleable, zoom-to-fullscreen
    chart (see assets_src/pace-chart.js).

Output, per event directory (e.g. data/italy/fastf1_pace.json):
    {
      "generated_at": "...",
      "sessions": [
        {
          "session": "FP1", "label": "Practice 1",
          "fastest": [ {code, driver, team, lap_time, optimal_time,
                        gap_to_optimal, top_speed}, ... ]  # sorted by pace
          "long_runs": [ {code, driver, team, stint, compound, laps,
                           avg_time, std_dev, tyre_life_start,
                           tyre_life_end}, ... ]
          "traces": {"distance": [...],
                     "speed": {"unit": "km/h", "series": [{code, driver,
                               team, color, dash, values}, ...]},
                     "delta": {"unit": "s", "ref_code": "...",
                               "series": [...]}}
          "narrative": ["...", ...]
        }, ...
      ]
    }

Needs `pip install fastf1 pandas numpy` (not part of build.py's stdlib
runtime — this script is run separately, like enrich.py, and commits its
JSON output for the stdlib-only build to pick up and render).

IMPORTANT: this repo has a top-level ``calendar.py`` which shadows the
stdlib ``calendar`` module that FastF1's dependencies need. We drop the
script's own directory from ``sys.path`` before importing fastf1 so the
real stdlib module resolves, then restore it to import repo-local modules.
"""
import sys, os, json, argparse, datetime, statistics

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE in sys.path:
    sys.path.remove(_HERE)
if "" in sys.path:
    sys.path.remove("")

import fastf1  # noqa: E402
import fastf1.plotting  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, _HERE)
import standings  # noqa: E402

ROOT = _HERE
CACHE_DIR = os.path.join(ROOT, ".fastf1_cache")
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

# FastF1 session identifier -> (display label, matches calendar.py session label)
SESSION_MAP = [
    ("FP1", "Practice 1"),
    ("FP2", "Practice 2"),
    ("FP3", "Practice 3"),
    ("Q", "Qualifying"),
    ("R", "Race"),
]

TOP_N_CHART_DRIVERS = 5


def _code_team(code, fallback_map=None):
    for _, drv, drv_code, team, _pts in standings.DRIVERS:
        if drv_code == code:
            return drv, team
    if fallback_map and code in fallback_map:
        return fallback_map[code]
    return code, "Unknown"


def _session_driver_map(session):
    """Abbreviation -> (FullName, TeamName) for drivers not in standings.py
    (e.g. reserve/stand-in drivers running practice sessions)."""
    mapping = {}
    try:
        results = session.results
        if results is not None and not results.empty:
            for _, row in results.iterrows():
                abbr = row.get("Abbreviation")
                if abbr:
                    mapping[abbr] = (row.get("FullName") or abbr, row.get("TeamName") or "Unknown")
    except Exception:
        pass
    return mapping


def _team_color(team):
    return standings.TEAM_COLOURS.get(team, "#999999")


def _fmt_td(td):
    if td is None or pd.isna(td):
        return None
    total = td.total_seconds()
    m, s = divmod(total, 60)
    return f"{int(m)}:{s:06.3f}"


def _session_already_run(cal_session, now):
    """True once a session's scheduled end (start + a generous buffer) has passed."""
    try:
        start = datetime.datetime.fromisoformat(f"{cal_session['date']}T{cal_session['time']}"
                                                 f"{cal_session.get('gmt_offset', '+00:00')}")
    except Exception:
        return False
    buffer_min = 130 if cal_session["label"] != "Race" else 210
    return now >= start + datetime.timedelta(minutes=buffer_min)


def analyse_session(year, round_no, code, label, event_name, slug):
    try:
        session = fastf1.get_session(year, round_no, code)
        session.load(telemetry=True, laps=True, weather=False, messages=False)
    except Exception as e:
        print(f"    · {label}: not available yet ({e})")
        return None
    laps = session.laps
    if laps is None or laps.empty:
        print(f"    · {label}: no lap data")
        return None
    drv_map = _session_driver_map(session)

    fastest_rows = []
    for code_, drv_laps in laps.groupby("Driver"):
        best = drv_laps.pick_fastest()
        if best is None or pd.isna(best.get("LapTime")):
            continue
        s1 = drv_laps["Sector1Time"].min()
        s2 = drv_laps["Sector2Time"].min()
        s3 = drv_laps["Sector3Time"].min()
        optimal = None
        if pd.notna(s1) and pd.notna(s2) and pd.notna(s3):
            optimal = s1 + s2 + s3
        top_speed = drv_laps["SpeedST"].max()
        if pd.isna(top_speed):
            top_speed = drv_laps["SpeedFL"].max()
        drv_name, team = _code_team(code_, drv_map)
        fastest_rows.append(dict(
            code=code_, driver=drv_name, team=team,
            lap_time=_fmt_td(best["LapTime"]),
            lap_time_s=best["LapTime"].total_seconds(),
            optimal_time=_fmt_td(optimal),
            gap_to_optimal=(round((best["LapTime"] - optimal).total_seconds(), 3)
                            if optimal is not None else None),
            top_speed=(round(float(top_speed), 1) if pd.notna(top_speed) else None),
        ))
    fastest_rows.sort(key=lambda r: r["lap_time_s"])
    for r in fastest_rows:
        del r["lap_time_s"]

    # Long-run pace: green-flag laps, no in/out laps, grouped by stint.
    long_runs = []
    try:
        clean = laps.pick_wo_box().pick_track_status("1")
    except Exception:
        clean = laps
    for (code_, stint), grp in clean.groupby(["Driver", "Stint"]):
        times = grp["LapTime"].dropna()
        if len(times) < 4:
            continue
        secs = sorted(t.total_seconds() for t in times)
        if len(secs) < 4:
            continue
        # Drop laps well outside the stint's own pace (traffic/aborted laps
        # that green-flag/pit filters don't catch) before trimming the
        # single slowest remaining lap as the standard outlier.
        threshold = secs[0] * 1.15
        filtered = [s for s in secs if s <= threshold]
        if len(filtered) < 4:
            filtered = secs
        trimmed = filtered[:-1] if len(filtered) > 4 else filtered
        avg = statistics.mean(trimmed)
        std = statistics.pstdev(trimmed) if len(trimmed) > 1 else 0.0
        compound = grp["Compound"].mode()
        compound = compound.iloc[0] if not compound.empty else "?"
        drv_name, team = _code_team(code_, drv_map)
        long_runs.append(dict(
            code=code_, driver=drv_name, team=team, stint=int(stint),
            compound=compound, laps=len(secs),
            tyre_life_start=int(grp["TyreLife"].min()) if pd.notna(grp["TyreLife"].min()) else None,
            tyre_life_end=int(grp["TyreLife"].max()) if pd.notna(grp["TyreLife"].max()) else None,
            avg_time=round(avg, 3), std_dev=round(std, 3),
        ))
    long_runs.sort(key=lambda r: r["avg_time"])

    traces = _make_trace_data(laps, fastest_rows, code)
    narrative = _narrative(fastest_rows, long_runs, event_name, label)
    narrative += _news_context(fastest_rows, long_runs, slug)

    return dict(session=code, label=label, fastest=fastest_rows,
                long_runs=long_runs, traces=traces, narrative=narrative)


TRACE_POINTS = 300


def _make_trace_data(laps, fastest_rows, code):
    """Downsampled speed + delta-to-fastest traces (onto a shared distance
    grid) for the top N drivers, as a small embeddable JSON payload. A
    client-side canvas chart (assets_src/pace-chart.js) renders this
    interactively — toggle individual drivers on/off, view fullscreen — which
    a static PNG can't offer."""
    top = fastest_rows[:TOP_N_CHART_DRIVERS]
    if len(top) < 2:
        return None

    telemetries = {}
    ref_code = None
    for row in top:
        drv_code = row["code"]
        drv_laps = laps.pick_driver(drv_code)
        best = drv_laps.pick_fastest()
        try:
            tel = best.get_telemetry().add_distance()
        except Exception:
            continue
        telemetries[drv_code] = tel
        if ref_code is None:
            ref_code = drv_code
    if not telemetries or ref_code is None or len(telemetries) < 2:
        return None

    import numpy as np
    max_dist = float(telemetries[ref_code]["Distance"].max())
    grid = np.linspace(0, max_dist, TRACE_POINTS)
    ref_t = np.interp(grid, telemetries[ref_code]["Distance"].to_numpy(),
                       telemetries[ref_code]["Time"].dt.total_seconds().to_numpy())

    seen_teams = {}
    speed_series, delta_series = [], []
    for row in top:
        drv_code = row["code"]
        if drv_code not in telemetries:
            continue
        tel = telemetries[drv_code]
        n_seen = seen_teams.get(row["team"], 0)
        seen_teams[row["team"]] = n_seen + 1
        dash = n_seen > 0
        color = _team_color(row["team"])
        speed_vals = np.interp(grid, tel["Distance"].to_numpy(), tel["Speed"].to_numpy())
        speed_series.append(dict(
            code=drv_code, driver=row["driver"], team=row["team"],
            color=color, dash=dash,
            values=[round(float(v), 1) for v in speed_vals],
        ))
        t_vals = np.interp(grid, tel["Distance"].to_numpy(),
                            tel["Time"].dt.total_seconds().to_numpy())
        delta_vals = t_vals - ref_t
        delta_series.append(dict(
            code=drv_code, driver=row["driver"], team=row["team"],
            color=color, dash=dash,
            values=[round(float(v), 3) for v in delta_vals],
        ))

    return dict(
        distance=[round(float(d), 1) for d in grid],
        speed=dict(unit="km/h", series=speed_series),
        delta=dict(unit="s", ref_code=ref_code, series=delta_series),
    )


def _narrative(fastest_rows, long_runs, event_name, label):
    notes = []
    if fastest_rows:
        top = fastest_rows[0]
        notes.append(f"{top['driver']} set the pace in {label} with a {top['lap_time']}.")
        biggest_gap = max((r for r in fastest_rows if r["gap_to_optimal"] is not None),
                           key=lambda r: r["gap_to_optimal"], default=None)
        if biggest_gap and biggest_gap["gap_to_optimal"] and biggest_gap["gap_to_optimal"] > 0.1:
            notes.append(
                f"{biggest_gap['driver']} left the most time on the table: their fastest lap "
                f"({biggest_gap['lap_time']}) was {biggest_gap['gap_to_optimal']:.3f}s slower than "
                f"the theoretical lap built from their own best sectors "
                f"({biggest_gap['optimal_time']}), so there is more pace in the car than the "
                "lap time shows.")
        fastest_speed = max((r for r in fastest_rows if r["top_speed"]),
                             key=lambda r: r["top_speed"], default=None)
        if fastest_speed:
            notes.append(f"{fastest_speed['driver']} had the highest speed-trap reading, "
                         f"{fastest_speed['top_speed']:.1f} km/h.")
    if long_runs:
        best_pace = long_runs[0]
        notes.append(
            f"On long runs, {best_pace['driver']}'s {best_pace['compound']}-tyre stint "
            f"(stint {best_pace['stint']}, {best_pace['laps']} laps) had the best clean average "
            f"pace at {best_pace['avg_time']:.3f}s/lap (slowest lap of the stint dropped as an "
            "outlier).")
    return notes


def _news_context(fastest_rows, long_runs, slug):
    """Look for a news article that speaks to *why* the fastest/quickest-gaining
    driver or their team is on form this weekend, and surface it as a citation
    so the pace stats aren't just numbers in isolation."""
    news_path = os.path.join(ROOT, "data", slug, "news_auto.json")
    if not os.path.exists(news_path):
        return []
    try:
        articles = json.load(open(news_path))
    except Exception:
        return []

    subjects = []
    if fastest_rows:
        top = fastest_rows[0]
        subjects.append((top["driver"], top["team"], "pace"))
    if long_runs:
        best = long_runs[0]
        if not subjects or best["driver"] != subjects[0][0]:
            subjects.append((best["driver"], best["team"], "long-run pace"))

    notes = []
    seen_articles = set()
    for driver_name, team, angle in subjects:
        surname = driver_name.split()[-1] if driver_name else ""
        if not surname:
            continue
        for art in articles:
            if art.get("url") in seen_articles:
                continue
            haystacks = [art.get("title", "")] + art.get("paragraphs", [])
            hit = next((h for h in haystacks
                        if surname.lower() in h.lower() and
                        (team or "").split()[0].lower() in h.lower()), None)
            if not hit and any(surname.lower() in h.lower() for h in haystacks[:1]):
                hit = haystacks[0]
            if hit:
                snippet = hit.strip()
                if len(snippet) > 220:
                    snippet = snippet[:217].rsplit(" ", 1)[0] + "..."
                notes.append(
                    f"Context on {driver_name}'s {angle}: \u201c{snippet}\u201d "
                    f"(\u2014 {art.get('title')}, {art.get('source', 'news')}).")
                seen_articles.add(art.get("url"))
                break
    return notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gp", help="Only analyse this event slug (e.g. italy)")
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--active", action="store_true",
                     help="Only analyse the live/just-finished GP (for scheduled CI runs, "
                          "to avoid re-processing the whole season every run)")
    args = ap.parse_args()

    cal_path = os.path.join(ROOT, "data", f"calendar_{args.year}.json")
    if not os.path.exists(cal_path):
        print(f"No calendar file at {cal_path}")
        return
    cal = json.load(open(cal_path))
    now = datetime.datetime.now(datetime.timezone.utc)

    active_slugs = None
    if args.active:
        import build  # noqa: E402  (repo-local import, safe post sys.path fix-up)
        import f1lib  # noqa: E402
        today = datetime.date.today()
        gps = list(build.season_gps())
        for c in gps:
            c.setdefault("status", f1lib.event_status(c, today))
        live = [c for c in gps if c["status"] == "live"]
        past = [c for c in gps if c["status"] == "past"]
        active_slugs = {c["dir"] for c in (live + past[-1:])}
        print(f"Active GP(s) for this run: {sorted(active_slugs) or '(none)'}")

    for event in cal["events"]:
        slug = event["slug"]
        if args.gp and slug != args.gp:
            continue
        if active_slugs is not None and slug not in active_slugs:
            continue
        gp_dir = os.path.join(ROOT, "data", slug)
        if not os.path.isdir(gp_dir):
            continue
        round_no = event["round"]
        sessions_by_label = {s["label"]: s for s in event["sessions"]}
        print(f"→ {event['name']} (round {round_no})")
        out_sessions = []
        for code, label in SESSION_MAP:
            cal_session = sessions_by_label.get(label)
            if not cal_session or not _session_already_run(cal_session, now):
                continue
            print(f"  · analysing {label} ({code}) ...")
            result = analyse_session(args.year, round_no, code, label, event["name"], slug)
            if result:
                out_sessions.append(result)
        if not out_sessions:
            print("  (no completed sessions with usable data yet)")
            continue
        out_path = os.path.join(gp_dir, "fastf1_pace.json")
        json.dump(dict(generated_at=now.isoformat(), sessions=out_sessions),
                   open(out_path, "w"), indent=2)
        print(f"  ✓ wrote {out_path} ({len(out_sessions)} session(s))")


if __name__ == "__main__":
    main()
