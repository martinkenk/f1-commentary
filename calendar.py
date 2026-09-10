"""
Scrape the official Formula1.com calendar into ``data/calendar_<year>.json``.

This is the *known-now* layer of the season: every Grand Prix, its round number,
its circuit, and the exact session schedule (including sprint formats), pulled
straight from Formula1.com. It is deliberately a **separate, re-runnable step**
from the build:

    python3 calendar.py            # refresh the whole season
    python3 calendar.py --year 2026

`build.py` only *reads* the committed JSON, so the site build stays fast and
stdlib-only even if Formula1.com is unreachable. Re-run this whenever the
calendar shifts (relocated races, revised session times) — the diff is committed
like any other data change.

Session times are stored as circuit-local wall-clock plus the UTC offset that
applies on that date, which is what the engine needs to render the local /
Tallinn pair correctly even across the October DST changeover.
"""
import argparse
import datetime
import json
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15")

# Racing-page slug -> results-page slug, where Formula1.com uses different ones.
RESULTS_SLUG_FIX = {"united-arab-emirates": "abu-dhabi"}

# Sessions we care about, normalised to the labels the engine and the
# Formula1.com results endpoints use.
SESSION_LABELS = {
    "Practice 1": "Practice 1",
    "Practice 2": "Practice 2",
    "Practice 3": "Practice 3",
    "Sprint Qualifying": "Sprint Qualifying",
    "Sprint Shootout": "Sprint Qualifying",
    "Sprint": "Sprint",
    "Qualifying": "Qualifying",
    "Race": "Race",
}


def _get(url, timeout=30, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    return raw if binary else raw.decode("utf-8", "ignore")


def _unescape(page):
    """Formula1.com embeds its payload as escaped JSON inside <script> tags."""
    return page.replace('\\"', '"').replace("\\\\", "\\")


def _stat(text, label):
    """Pull a circuit stat that Formula1.com renders as '<label> <value>'.

    `text` must already have its tags stripped. Values legitimately go missing
    for events that aren't fully published yet (a relocated round may not have a
    lap count), so an empty string is a normal result, not an error — the site
    renders those as 'to be confirmed'.
    """
    m = re.search(re.escape(label) + r"\s+([0-9][0-9.,]*\s*(?:km)?)", text)
    return m.group(1).strip() if m else ""


def track_image(page, year):
    """URL of the official detailed track map, if present."""
    m = re.search(rf"https://media\.formula1\.com/[^\"'\\ ]*common/f1/{year}/track/"
                  rf"[a-z0-9]+detailed\.png", page)
    return m.group(0) if m else ""


def race_ids(year):
    """{results_slug: race_id} from the results index."""
    try:
        page = _get(f"https://www.formula1.com/en/results/{year}/races")
    except Exception as e:
        print(f"! results index unavailable: {e}")
        return {}
    out = {}
    for rid, slug in re.findall(
            rf"/en/results/{year}/races/(\d+)/([a-z0-9-]+)/", page):
        out.setdefault(slug, rid)
    return out


def calendar_slugs(year):
    """Racing-page slugs for the season, excluding testing events."""
    page = _get(f"https://www.formula1.com/en/racing/{year}")
    slugs = []
    for m in re.findall(rf"/en/racing/{year}/([a-z0-9-]+)", page):
        if m not in slugs and "testing" not in m:
            slugs.append(m)
    return slugs


def scrape_event(year, slug):
    """Return one event dict, or None if the page can't be parsed."""
    try:
        page = _unescape(_get(f"https://www.formula1.com/en/racing/{year}/{slug}"))
    except Exception as e:
        print(f"  ! {slug}: {e}")
        return None

    def field(key):
        m = re.search(re.escape(f'"{key}"') + r'\s*:\s*"([^"]{0,120})"', page)
        return m.group(1).strip() if m else ""

    block = re.search(r'"meetingSessions"\s*:\s*\[(.*?)\]', page, re.S)
    sessions = []
    if block:
        for raw in re.findall(r'\{"session":.*?\}', block.group(1)):
            try:
                d = json.loads(raw)
            except Exception:
                continue
            label = SESSION_LABELS.get(d.get("description", "").strip())
            if not label or not d.get("startTime"):
                continue
            date, _, clock = d["startTime"].partition("T")
            sessions.append({
                "label": label,
                "date": date,
                "time": clock[:5],
                "gmt_offset": d.get("gmtOffset", ""),
                "timezone": d.get("timezone", ""),
            })
    if not sessions:
        print(f"  ! {slug}: no sessions found")
        return None
    sessions.sort(key=lambda s: (s["date"], s["time"]))

    name = field("meetingName") or slug.replace("-", " ").title()
    text = re.sub(r"<[^>]+>", " ", page)
    return {
        "slug": slug,
        "results_slug": RESULTS_SLUG_FIX.get(slug, slug),
        "name": name,
        "official_name": field("meetingOfficialName"),
        "country": field("meetingCountryName"),
        "location": field("meetingLocation"),
        "circuit_length": _stat(text, "Circuit Length"),
        "laps": _stat(text, "Number of Laps"),
        "race_distance": _stat(text, "Race Distance"),
        "first_gp": _stat(text, "First Grand Prix"),
        "track_image": track_image(page, year),
        "sessions": sessions,
        "is_sprint": any(s["label"] == "Sprint" for s in sessions),
        "race_date": next((s["date"] for s in sessions if s["label"] == "Race"),
                          sessions[-1]["date"]),
    }


def fetch_track_maps(events, year, failures=None):
    """Download each official track map into assets_src/ so the built site is
    self-contained (the build itself never reaches out for images)."""
    out_dir = os.path.join(ROOT, "assets_src")
    os.makedirs(out_dir, exist_ok=True)
    got = 0
    for ev in events:
        url = ev.get("track_image")
        if not url:
            continue
        fname = f"track-{ev['slug']}.png"
        path = os.path.join(out_dir, fname)
        ev["track_asset"] = fname
        days_to_race = (datetime.date.fromisoformat(ev["race_date"])
                        - datetime.datetime.now(datetime.timezone.utc).date()).days
        if os.path.exists(path) and not -7 <= days_to_race <= 10:
            got += 1
            continue
        try:
            raw = _get(url, timeout=45, binary=True)
            if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("track-map response is not a PNG")
            temporary = path + ".tmp"
            with open(temporary, "wb") as f:
                f.write(raw)
            os.replace(temporary, path)
            got += 1
            print(f"  + track map: {fname} ({len(raw) // 1024} kB)")
        except (OSError, ValueError) as e:
            print(f"  ! track map {ev['slug']}: {e}")
            if failures is not None:
                failures.append(f"{ev['slug']}: {e}")
            if not os.path.exists(path):
                ev["track_asset"] = ""
    return got


def build(year, failures=None):
    print(f"Scraping the {year} Formula 1 calendar…\n")
    ids = race_ids(year)
    events = []
    for slug in calendar_slugs(year):
        ev = scrape_event(year, slug)
        if not ev:
            continue
        ev["race_id"] = ids.get(ev["results_slug"], "")
        events.append(ev)
        flag = "S" if ev["is_sprint"] else " "
        print(f"  {flag} {ev['race_date']}  {ev['name']:28} "
              f"{len(ev['sessions'])} sessions  id={ev['race_id'] or '?'}")

    # Round numbers come from the actual chronology, not page order.
    events.sort(key=lambda e: e["race_date"])
    for i, ev in enumerate(events, 1):
        ev["round"] = i
        ev["total_rounds"] = len(events)

    print("\nTrack maps:")
    maps = fetch_track_maps(events, year, failures)

    os.makedirs(DATA, exist_ok=True)
    path = os.path.join(DATA, f"calendar_{year}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"year": str(year), "events": events}, f,
                  ensure_ascii=False, indent=2)
        f.write("\n")
    sprints = sum(1 for e in events if e["is_sprint"])
    print(f"\nWrote {len(events)} events ({sprints} sprint weekends, "
          f"{maps} track maps) -> {os.path.relpath(path, ROOT)}")
    return events


def load(year):
    """Read the committed calendar. Returns [] if it hasn't been scraped yet."""
    try:
        with open(os.path.join(DATA, f"calendar_{year}.json"), encoding="utf-8") as f:
            return json.load(f).get("events", [])
    except Exception:
        return []


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--year", default="2026")
    ap.add_argument("--maps-only", action="store_true",
                    help="refresh existing calendar maps, including active-event revisions")
    args = ap.parse_args()
    failures = []
    if args.maps_only:
        events = load(args.year)
        if not events:
            raise SystemExit("No calendar available for track-map refresh")
        fetch_track_maps(events, args.year, failures)
    else:
        build(args.year, failures)
    if failures:
        raise SystemExit(f"{len(failures)} track-map refresh(es) failed; prior assets retained")
