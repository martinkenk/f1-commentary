"""
F1 Commentary Hub — reusable engine (GP-agnostic).

Holds every part of the site that does not change from race to race:
HTML shell + sidebar, stylesheet, live/near-real-time weather, live session
results (fetched from Formula1.com), the multi-GP landing index, and the build
driver. Per-Grand-Prix content lives in the content_<gp>.py modules; each is
wired up in build.py.
"""
import os, re, html, shutil, json, datetime, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "site")
BUILD_STAMP = datetime.datetime.now().strftime("%a %d %b %Y, %H:%M")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36")
# How far ahead Open-Meteo's forecast reaches. Beyond this a weather request
# just returns nothing, so a full-season build skips it rather than paying for
# a round trip per session.
WEATHER_HORIZON_DAYS = 16
# Championship year. Used to turn a card's short display date ("20 Aug") into
# something sortable when it predates the ISO `date` field.
SEASON = 2026


# --------------------------------------------------------------------------
# Small HTML helpers
# --------------------------------------------------------------------------
def card(title, inner, icon="bi-info-circle", cls=""):
    return f"""<div class="info-card {cls}">
  <h3><i class="bi {icon}"></i> {title}</h3>
  {inner}
</div>"""

def stat(value, label, sub=""):
    subhtml = f'<span class="stat-sub">{sub}</span>' if sub else ""
    return f'<div class="stat"><div class="stat-val">{value}</div><div class="stat-lbl">{label}</div>{subhtml}</div>'

def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def quote(text, who):
    return f'<blockquote class="quote">{text}<footer>— {who}</footer></blockquote>'


# --------------------------------------------------------------------------
# Auto-enrichment data layer.
#
# enrich.py (run on a schedule in CI, or locally) uses an LLM to summarise new
# articles and to turn new FIA decision PDFs into structured records, writing
# them to data/<gp>/news_auto.json and data/<gp>/penalties_auto.json. The engine
# merges those in automatically at build time. Curated content authored in the
# content_<gp>.py modules always wins; auto items only *fill gaps* (deduped by
# headline / FIA document number) and always carry a link back to the source.
# --------------------------------------------------------------------------
DATA_DIR = os.path.join(ROOT, "data")


def _load_auto(ctx, name):
    """Load data/<gp>/<name>.json as a list, or [] if missing/invalid."""
    path = os.path.join(DATA_DIR, ctx.get("dir", ""), name + ".json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _norm_title(t):
    t = re.sub(r"<[^>]+>", "", t or "")
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def _doc_num(doc):
    m = re.search(r"(\d+)", doc or "")
    return int(m.group(1)) if m else 9999


_MONTHS = ("jan", "feb", "mar", "apr", "may", "jun",
           "jul", "aug", "sep", "oct", "nov", "dec")


def news_sort_key(card):
    """Sortable publication date for an auto news card, oldest -> newest.

    Cards carry an ISO ``date`` for sorting and a short display ``when``
    ("20 Aug"). ``when`` alone is useless as a key: it sorts lexically, so
    "12 Aug" lands before "6 Aug" and any September story before every August
    one. Older cards predate the ``date`` field, so fall back to parsing
    ``when`` against the season year rather than dropping them to the bottom.

    Undated cards sort *last* here — with newest-first rendering that puts
    them at the end, where an item of unknown age belongs, instead of above
    the day's breaking news.
    """
    iso = (card.get("date") or "").strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", iso):
        return iso
    m = re.match(r"^\s*(\d{1,2})\s+([A-Za-z]{3})", card.get("when") or "")
    if m and m.group(2).lower() in _MONTHS:
        month = _MONTHS.index(m.group(2).lower()) + 1
        return f"{SEASON}-{month:02d}-{int(m.group(1)):02d}"
    return ""


def _auto_news_card(c):
    """Render one LLM-summarised news card, with a link back to the source."""
    src, kind, url = c.get("source", ""), c.get("src_kind", ""), c.get("url", "")
    paras = "".join(f"<p>{p}</p>" for p in (c.get("paragraphs") or []))
    meta = []
    if src:
        link = (f'<a href="{url}" target="_blank" rel="noopener">{src}</a>' if url else src)
        meta.append(f'<span class="news-src {kind}">{link}</span>')
    if c.get("when"):
        meta.append(f'<span class="news-when">{c["when"]}</span>')
    meta.append('<span class="news-auto" title="Summarised automatically from the source article">auto</span>')
    return (f'<div class="news-item"><h3>{c.get("title","")}</h3>'
            f'<div class="news-meta">{"".join(meta)}</div>{paras}</div>')


# --------------------------------------------------------------------------
# Live weather (Open-Meteo, no key). Forecast for upcoming/ongoing sessions,
# historical archive for sessions that are already in the past — so the skill
# can be run at ANY point across the weekend and always shows the best data.
# --------------------------------------------------------------------------
_WMO = {
    0: ("Clear", "bi-sun"), 1: ("Mainly clear", "bi-sun"),
    2: ("Partly cloudy", "bi-cloud-sun"), 3: ("Overcast", "bi-clouds"),
    45: ("Fog", "bi-cloud-fog2"), 48: ("Rime fog", "bi-cloud-fog2"),
    51: ("Light drizzle", "bi-cloud-drizzle"), 53: ("Drizzle", "bi-cloud-drizzle"),
    55: ("Heavy drizzle", "bi-cloud-drizzle"),
    61: ("Light rain", "bi-cloud-rain"), 63: ("Rain", "bi-cloud-rain"),
    65: ("Heavy rain", "bi-cloud-rain-heavy"),
    71: ("Light snow", "bi-cloud-snow"), 73: ("Snow", "bi-cloud-snow"), 75: ("Heavy snow", "bi-cloud-snow"),
    80: ("Rain showers", "bi-cloud-rain"), 81: ("Showers", "bi-cloud-rain"),
    82: ("Violent showers", "bi-cloud-rain-heavy"),
    95: ("Thunderstorm", "bi-cloud-lightning-rain"),
    96: ("Storm + hail", "bi-cloud-lightning-rain"), 99: ("Storm + hail", "bi-cloud-lightning-rain"),
}


def _hours_offset(hhmm, hours):
    h, m = map(int, hhmm.split(":"))
    return f"{(h + hours) % 24:02d}:{m:02d}"


def _east(date, hhmm, hours):
    """Circuit-local date/time -> Eastern European (Tallinn) date/time.

    Returns ``(iso_date, "HH:MM", day_delta)``. The day delta matters: a Las
    Vegas session at 20:00 local is 06:00 the *following* morning in Tallinn, so
    both the on-screen time and the weather lookup have to move with it.
    """
    h, m = map(int, hhmm.split(":"))
    base = datetime.datetime.fromisoformat(f"{date}T{h:02d}:{m:02d}")
    east = base + datetime.timedelta(hours=hours)
    return east.date().isoformat(), east.strftime("%H:%M"), (east.date() - base.date()).days


def _east_cell(date, hhmm, hours):
    """Tallinn time for a table cell, flagged when it falls on another day."""
    _d, t, delta = _east(date, hhmm, hours)
    if delta:
        return f'{t} <span class="daymark">{delta:+d}d</span>'
    return t


def _fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def fetch_weather(ctx):
    """Return {session_name -> {temp,pop,wind,desc,icon,actual}} or {} on failure.

    Hourly data is requested in the Eastern-European (Tallinn) timezone so the
    indices line up with the on-air clock. Past sessions use the ERA5 archive
    (actual conditions); upcoming ones use the forecast.
    """
    lat, lon = ctx["lat"], ctx["lon"]
    off = ctx.get("tz_offset", 1)
    tz = "Europe%2FTallinn"
    today = datetime.date.today()
    out = {}
    for name, _wd, date, local_hhmm in ctx["sessions"]:
        try:
            d = datetime.date.fromisoformat(date)
        except ValueError:
            continue
        past = d < today
        east_date, east_hhmm, _delta = _east(date, local_hhmm, off)
        th = int(east_hhmm.split(":")[0])
        key = f"{east_date}T{th:02d}:00"
        try:
            if past:
                url = ("https://archive-api.open-meteo.com/v1/archive"
                       f"?latitude={lat}&longitude={lon}"
                       "&hourly=temperature_2m,precipitation,weathercode,wind_speed_10m"
                       f"&timezone={tz}&start_date={east_date}&end_date={east_date}")
            else:
                url = ("https://api.open-meteo.com/v1/forecast"
                       f"?latitude={lat}&longitude={lon}"
                       "&hourly=temperature_2m,precipitation_probability,weathercode,wind_speed_10m"
                       f"&timezone={tz}&start_date={east_date}&end_date={east_date}")
            data = _fetch_json(url)
            H = data["hourly"]
            if key not in H["time"]:
                continue
            i = H["time"].index(key)
            code = H["weathercode"][i]
            desc, icon = _WMO.get(code, ("--", "bi-thermometer-half"))
            temp = H["temperature_2m"][i]
            wind = H["wind_speed_10m"][i]
            if past:
                pr = (H.get("precipitation") or [None])[i]
                pop = None
                pop_txt = (f"{pr:.1f} mm" if pr is not None else "-")
            else:
                pop = (H.get("precipitation_probability") or [None])[i]
                pop_txt = (f"{pop}%" if pop is not None else "-")
            out[name] = {
                "temp": round(temp) if temp is not None else "-",
                "pop": pop, "pop_txt": pop_txt,
                "wind": round(wind) if wind is not None else "-",
                "desc": desc, "icon": icon, "actual": past,
            }
        except Exception:
            continue
    return out


def schedule_rows(ctx):
    off = ctx.get("tz_offset", 1)
    rows = []
    for name, wd, date, local in ctx["sessions"]:
        rows.append(
            f"<tr><td>{name}</td><td>{wd}</td>"
            f"<td>{local}</td><td>{_east_cell(date, local, off)}</td></tr>"
        )
    return "\n".join(rows)


def weather_cards(ctx):
    weather = ctx.get("weather") or {}
    off = ctx.get("tz_offset", 1)
    if not weather:
        return (
            '<div class="callout watch"><strong>Live weather unavailable at build time.</strong> '
            "Confirm conditions on air, then rebuild with an internet connection to embed "
            "the per-session forecast/actuals.</div>"
        )
    cards = []
    for name, wd, date, local in ctx["sessions"]:
        w = weather.get(name)
        if not w:
            continue
        wet = (w["pop"] is not None and w["pop"] >= 40) or (
            w["actual"] and w["pop_txt"] not in ("-", "0.0 mm"))
        cls = "wx-wet" if wet else ""
        tag = "actual" if w["actual"] else "forecast"
        cards.append(f"""<div class="wx-card {cls}">
      <div class="wx-head"><i class="bi {w['icon']}"></i> {name} <span class="wx-tag">{tag}</span></div>
      <div class="wx-day">{wd} · {local} / {_east_cell(date, local, off)}</div>
      <div class="wx-temp">{w['temp']}°C</div>
      <div class="wx-desc">{w['desc']}</div>
      <div class="wx-meta"><span><i class="bi bi-droplet"></i> {w['pop_txt']}</span>
        <span><i class="bi bi-wind"></i> {w['wind']} km/h</span></div>
    </div>""")
    return f'<div class="wx-grid">{"".join(cards)}</div>'


# --------------------------------------------------------------------------
# Live session results (Formula1.com). Only sessions that have actually run
# return a table, so this naturally fills in as the weekend progresses.
# --------------------------------------------------------------------------
# (label, url-endpoint)
RESULT_SESSIONS = [
    ("Practice 1", "practice/1"),
    ("Practice 2", "practice/2"),
    ("Practice 3", "practice/3"),
    ("Sprint Qualifying", "sprint-qualifying"),
    ("Sprint", "sprint-results"),
    ("Qualifying", "qualifying"),
    ("Starting Grid", "starting-grid"),
    ("Race", "race-result"),
]


def _clean(cell):
    txt = html.unescape(re.sub(r"<[^>]+>", " ", cell))
    return re.sub(r"\s+", " ", txt).replace("\xa0", " ").strip()


def _split_driver(name):
    # "Kimi AntonelliANT" -> ("Kimi Antonelli", "ANT")
    m = re.match(r"^(.*?)([A-Z]{3})$", name)
    if m and " " in m.group(1):
        return m.group(1).strip(), m.group(2)
    return name, ""


def _parse_result_table(t):
    ths = [_clean(x) for x in re.findall(r"<th[^>]*>(.*?)</th>", t, re.S)]
    ths = [x for x in ths if x]
    body = re.search(r"<tbody[^>]*>(.*?)</tbody>", t, re.S)
    if not body:
        return None
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", body.group(1), re.S):
        cells = [_clean(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        cells = [c for c in cells if c != ""]
        if cells:
            rows.append(cells)
    if not ths or not rows:
        return None
    return ths, rows


def fetch_results(ctx):
    """Return ordered list of {label, headers, rows} for sessions that have run."""
    if not ctx.get("race_id") or not ctx.get("results_slug"):
        return []
    out = []
    for label, ep in RESULT_SESSIONS:
        url = (f"https://www.formula1.com/en/results/{ctx['year']}/races/"
               f"{ctx['race_id']}/{ctx['results_slug']}/{ep}")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15) as r:
                if r.status != 200:
                    continue
                t = r.read().decode("utf-8", "ignore")
        except Exception:
            continue
        if "No results available" in t:
            continue
        parsed = _parse_result_table(t)
        if not parsed:
            continue
        headers, rows = parsed
        out.append({"label": label, "headers": headers, "rows": rows})
    return out


def _fetch_one_table(ctx, endpoint):
    """Fetch and parse a single Formula1.com results endpoint, or None."""
    if not ctx.get("race_id") or not ctx.get("results_slug"):
        return None
    url = (f"https://www.formula1.com/en/results/{ctx['year']}/races/"
           f"{ctx['race_id']}/{ctx['results_slug']}/{endpoint}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            if r.status != 200:
                return None
            t = r.read().decode("utf-8", "ignore")
    except Exception:
        return None
    if "No results available" in t:
        return None
    parsed = _parse_result_table(t)
    if not parsed:
        return None
    headers, rows = parsed
    return {"headers": headers, "rows": rows}


def fetch_extra(ctx):
    """Pit-stop summary + fastest laps — used by the Reliability & Pits page."""
    return {
        "pitstops": _fetch_one_table(ctx, "pit-stop-summary"),
        "fastestlaps": _fetch_one_table(ctx, "fastest-laps"),
    }


_DRIVER_COL = None
def _result_table(block):
    headers, rows = block["headers"], block["rows"]
    ncol = len(headers)
    thead = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for row in rows:
        row = (row + [""] * ncol)[:ncol]
        cells = []
        for h, val in zip(headers, row):
            low = h.lower()
            if low.startswith("driver"):
                nm, code = _split_driver(val)
                val = f"{nm} <span class='drv-code'>{code}</span>" if code else nm
            if low.startswith("pos") or low.startswith("grid"):
                cls = " class='pos'"
            elif low.startswith(("team", "car")):
                cls = " class='team'"
            elif low.startswith(("pts", "points", "laps")):
                cls = " class='num'"
            else:
                cls = ""
            cells.append(f"<td{cls}>{val}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    # Results are position-ordered, so the top three earn medal colours.
    ranked = " ranked" if headers and headers[0].lower().startswith(("pos", "grid")) else ""
    return f"""<div class="table-wrap"><table class="data{ranked}">
  <thead><tr>{thead}</tr></thead>
  <tbody>{''.join(body)}</tbody>
</table></div>"""


def _slugify(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def render_results(ctx):
    results = ctx.get("results") or []
    if not results:
        return (
            '<div class="callout watch"><strong>No sessions have been completed yet.</strong> '
            "This page fills in automatically — rerun the build after each practice, qualifying "
            "or the race and the official Formula1.com results will appear here.</div>"
        )
    done = ", ".join(b["label"] for b in results)
    intro = (f'<div class="callout"><strong>Completed so far:</strong> {done}. '
             "Results are pulled live from Formula1.com at build time — rerun during the "
             "weekend to refresh as more sessions finish. Pick a session below.</div>")

    # Default to the most recent completed session (last in chronological order).
    active_idx = len(results) - 1
    tabs, panes = [], []
    for i, b in enumerate(results):
        sid = f"res-{_slugify(b['label'])}"
        is_active = (i == active_idx)
        tabs.append(
            f'<li class="nav-item" role="presentation">'
            f'<button class="nav-link{" active" if is_active else ""}" id="{sid}-tab" '
            f'data-bs-toggle="pill" data-bs-target="#{sid}" type="button" role="tab" '
            f'aria-controls="{sid}" aria-selected="{"true" if is_active else "false"}">'
            f'{b["label"]}</button></li>'
        )
        panes.append(
            f'<div class="tab-pane fade{" show active" if is_active else ""}" id="{sid}" '
            f'role="tabpanel" aria-labelledby="{sid}-tab" tabindex="0">'
            f'<h2 class="sec">{b["label"]}</h2>{_result_table(b)}</div>'
        )

    return (
        intro
        + '<ul class="nav nav-pills results-tabs" role="tablist">'
        + "".join(tabs)
        + '</ul><div class="tab-content">'
        + "".join(panes)
        + "</div>"
        + render_pace_analysis(ctx)
    )


# --------------------------------------------------------------------------
# FastF1 pace analysis (data/<gp>/fastf1_pace.json, written by
# fastf1_analysis.py from real lap timing + telemetry — see that script's
# docstring). Purely additive: renders nothing if the file is absent, so it
# is safe to call unconditionally from render_results() for every GP.
# --------------------------------------------------------------------------
def _load_pace(ctx):
    path = os.path.join(DATA_DIR, ctx.get("dir", ""), "fastf1_pace.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("sessions") or [] if isinstance(data, dict) else []
    except Exception:
        return []


def _pace_table(rows, cols):
    """cols: list of (key, header, formatter-or-None)."""
    thead = "".join(f"<th>{h}</th>" for _key, h, _fmt in cols)
    body = []
    for r in rows:
        cells = []
        for key, _h, fmt in cols:
            val = r.get(key)
            if fmt:
                val = fmt(val, r)
            cells.append(f"<td>{val if val is not None else '—'}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return (f'<div class="table-wrap"><table class="data compact">'
            f'<thead><tr>{thead}</tr></thead><tbody>{"".join(body)}</tbody></table></div>')


def render_pace_analysis(ctx):
    sessions = _load_pace(ctx)
    if not sessions:
        return ""
    out = ['<h2 class="sec">Pace analysis (FastF1 telemetry)</h2>',
           '<div class="callout"><strong>Built from real lap timing and car telemetry</strong> '
           "via <a href=\"https://docs.fastf1.dev/\" target=\"_blank\" rel=\"noopener\">FastF1</a>: "
           "each driver's fastest lap vs. the theoretical lap built from their own best sector "
           "times, best clean long-run pace by tyre stint (slowest lap of each stint dropped as "
           "an outlier), and speed/delta traces around the lap for the fastest runners. Click a "
           "driver in a chart's legend to isolate or hide their trace, or use the fullscreen "
           "button for a bigger view.</div>"]

    def _driver_cell(v, r):
        code = r.get("code", "")
        return f"{v} <span class='drv-code'>{code}</span>" if code else v

    def _gap(v, _r):
        if v is None:
            return "on the pace"
        return f"+{v:.3f}s"

    def _speed(v, _r):
        return f"{v:.1f} km/h" if v is not None else None

    def _avg(v, _r):
        if v is None:
            return None
        m, s = divmod(v, 60)
        return f"{int(m)}:{s:06.3f}"

    tabs, panes = [], []
    for i, s in enumerate(sessions):
        sid = f"pace-{_slugify(s['label'])}"
        is_active = (i == len(sessions) - 1)
        tabs.append(
            f'<li class="nav-item" role="presentation">'
            f'<button class="nav-link{" active" if is_active else ""}" id="{sid}-tab" '
            f'data-bs-toggle="pill" data-bs-target="#{sid}" type="button" role="tab" '
            f'aria-controls="{sid}" aria-selected="{"true" if is_active else "false"}">'
            f'{s["label"]}</button></li>')

        pane = [f'<h3 class="sec">{s["label"]} &mdash; fastest laps vs. theoretical optimal</h3>']
        if s.get("narrative"):
            pane.append(ul(s["narrative"]))
        if s.get("fastest"):
            pane.append(_pace_table(s["fastest"], [
                ("driver", "Driver", _driver_cell),
                ("team", "Team", None),
                ("lap_time", "Fastest lap", None),
                ("optimal_time", "Theoretical optimal", None),
                ("gap_to_optimal", "Time left on table", _gap),
                ("top_speed", "Speed trap", _speed),
            ]))
        charts_needed = False
        traces = s.get("traces") or {}
        for kind, title, ylabel_title in (
            ("speed", "Speed vs. distance, fastest laps", "Speed trace"),
            ("delta", "Gap to the outright fastest lap, around the lap", "Delta trace"),
        ):
            block = traces.get(kind)
            if not block or not block.get("series"):
                continue
            if not charts_needed:
                pane.append('<div class="pace-chart-grid">')
                charts_needed = True
            chart_id = f"{sid}-{kind}"
            payload = dict(
                distance=traces.get("distance"),
                unit=block.get("unit"),
                series=block.get("series"),
            )
            if kind == "delta":
                payload["refCode"] = block.get("ref_code")
            payload_json = json.dumps(payload).replace("</", "<\\/")
            pane.append(
                f'<figure class="pace-chart" data-chart-id="{chart_id}">'
                f'<figcaption class="pace-chart-head"><span>{title}</span>'
                f'<button type="button" class="pace-chart-expand" title="View fullscreen">'
                f'<i class="bi bi-arrows-fullscreen"></i> Fullscreen</button></figcaption>'
                f'<div class="pace-chart-canvas-wrap"><canvas class="pace-chart-canvas"></canvas></div>'
                f'<div class="pace-chart-legend"></div>'
                f'</figure>'
                f'<script type="application/json" class="pace-chart-data" data-for="{chart_id}">'
                f'{payload_json}</script>'
            )
        if charts_needed:
            pane.append('</div>')
        if s.get("long_runs"):
            pane.append('<h3 class="sec">Long-run pace (clean laps, outlier dropped)</h3>')
            pane.append(_pace_table(s["long_runs"], [
                ("driver", "Driver", _driver_cell),
                ("team", "Team", None),
                ("compound", "Compound", None),
                ("laps", "Laps", None),
                ("avg_time", "Avg. clean lap", _avg),
                ("std_dev", "Consistency (σ)", lambda v, _r: f"{v:.3f}s" if v is not None else None),
            ]))
        panes.append(
            f'<div class="tab-pane fade{" show active" if is_active else ""}" id="{sid}" '
            f'role="tabpanel" aria-labelledby="{sid}-tab" tabindex="0">{"".join(pane)}</div>')

    out.append('<ul class="nav nav-pills results-tabs" role="tablist">' + "".join(tabs) + "</ul>")
    out.append('<div class="tab-content">' + "".join(panes) + "</div>")
    out.append('<script src="../assets/pace-chart.js" defer></script>')
    return "".join(out)


# --------------------------------------------------------------------------
# Weekend News helpers
# --------------------------------------------------------------------------
def news_item(title, summary, source="", when="", src_kind=""):
    """One news card. `summary` may be a string or list of paragraphs.
    src_kind: '' | 'f1' | 'race' controls the source-badge colour."""
    if isinstance(summary, (list, tuple)):
        para = "".join(f"<p>{p}</p>" for p in summary)
    else:
        para = f"<p>{summary}</p>"
    meta = []
    if source:
        meta.append(f'<span class="news-src {src_kind}">{source}</span>')
    if when:
        meta.append(f'<span class="news-when">{when}</span>')
    meta_html = f'<div class="news-meta">{"".join(meta)}</div>' if meta else ""
    return (f'<div class="news-item"><h3>{title}</h3>{meta_html}{para}</div>')


def news_list(items):
    return '<div class="news-list">' + "".join(items) + "</div>"


def session_podium(ctx, label, top=3):
    """Return a small podium strip (P1-P3 + fastest lap count) for a completed
    session, pulled from the live results, or '' if the session hasn't run."""
    for b in (ctx.get("results") or []):
        if b["label"] != label:
            continue
        headers = [h.lower() for h in b["headers"]]
        try:
            di = next(i for i, h in enumerate(headers) if h.startswith("driver"))
        except StopIteration:
            return ""
        ti = next((i for i, h in enumerate(headers) if h.startswith("time") or "gap" in h), None)
        pods = []
        medals = ["🥇", "🥈", "🥉"]
        for n, row in enumerate(b["rows"][:top]):
            nm, _ = _split_driver(row[di]) if di < len(row) else (row[-1], "")
            gap = f" <span class='pill'>{row[ti]}</span>" if ti is not None and ti < len(row) else ""
            mk = medals[n] if n < len(medals) else f"P{n+1}"
            pods.append(f'<span class="pod">{mk} <b>{nm}</b>{gap}</span>')
        return '<div class="sess-podium">' + "".join(pods) + "</div>"
    return ""


def completed_labels(ctx):
    return [b["label"] for b in (ctx.get("results") or [])]


def render_news(ctx, general_items, session_notes):
    """Compose the Weekend News page.
    general_items : list of news_item() HTML strings (weekend-wide stories).
    session_notes : dict {session_label: [news_item html, ...]} — only rendered
                    for sessions that have actually run (per live results).
                    Sessions that are complete but have no authored notes get an
                    auto podium summary so the page always reflects reality.

    LLM-summarised cards from data/<gp>/news_auto.json are merged in automatically:
    curated headlines come first, then any wire stories not already covered."""
    done = completed_labels(ctx)

    # Merge in auto-summarised wire cards (curated content wins on dedup).
    curated_titles = set()
    for h in list(general_items) + [x for v in session_notes.values() for x in v]:
        m = re.search(r"<h3>(.*?)</h3>", h)
        if m:
            curated_titles.add(_norm_title(m.group(1)))
    auto_general, auto_by_session = [], {}
    for c in _load_auto(ctx, "news_auto"):
        if _norm_title(c.get("title", "")) in curated_titles:
            continue
        sess = c.get("session", "")
        if c.get("kind") == "session" and sess in done:
            auto_by_session.setdefault(sess, []).append(c)
        else:
            auto_general.append(c)
    # Newest first. The wire feed runs to dozens of cards by race day, and a
    # commentator scanning it wants today's driver-market bombshell at the top,
    # not last week's preview — stored order is oldest-first, which buried
    # exactly the stories the page exists to surface.
    auto_general.sort(key=news_sort_key, reverse=True)

    out = []
    out.append('<h2 class="sec">Weekend headlines</h2>')
    out.append('<p class="lead-note">Editor-curated stories from around the paddock so far this weekend '
               '(Formula1.com &amp; The Race). Refreshed every time the site is rebuilt.</p>')
    out.append(news_list(general_items) if general_items
               else '<div class="callout watch">No general news collated yet.</div>')

    # Auto-summarised wire feed in its own clearly-labelled block, so the curated
    # analysis leads and the machine-summarised source links read as a supplement.
    if auto_general:
        out.append('<h2 class="sec">From the wires <span class="wire-tag">auto-summarised</span></h2>')
        out.append('<p class="lead-note">Every other weekend article picked up automatically from '
                   'Formula1.com &amp; The Race, summarised by an LLM. Each card links to the '
                   'source so you can verify before air.</p>')
        out.append(news_list([_auto_news_card(c) for c in auto_general]))

    out.append('<h2 class="sec">Session by session</h2>')
    if not done:
        out.append('<div class="callout watch"><strong>No sessions have run yet.</strong> '
                   "Session reports appear here automatically as each practice, qualifying "
                   "and the race is completed — rerun the build during the weekend to refresh.</div>")
        return "".join(out)

    out.append('<p class="lead-note">A block appears for every session that has been completed. '
               'Top three come live from the official timing.</p>')
    for label in done:
        out.append(f'<div class="sess-head"><h3 class="sec" style="margin:0">{label}</h3>'
                   f'<span class="badge-done">Completed</span></div>')
        out.append(session_podium(ctx, label))
        cards = list(session_notes.get(label) or []) + \
            [_auto_news_card(c) for c in auto_by_session.get(label, [])]
        if cards:
            out.append(news_list(cards))
        else:
            out.append('<p class="src">Timing above is live from Formula1.com — '
                       'see the Results page for the full classification.</p>')
    return "".join(out)


def auto_news(ctx):
    """Engine fallback used when a GP's content module doesn't author its own
    News page. Produces a session-by-session summary straight from results."""
    return render_news(ctx, general_items=[], session_notes={})


# --------------------------------------------------------------------------
# Head-to-Head (teammate battles) — derived live from the session results
# --------------------------------------------------------------------------
def _block(ctx, label):
    for b in (ctx.get("results") or []):
        if b["label"] == label:
            return b
    return None


def _col(headers, *starts):
    low = [h.lower() for h in headers]
    for i, h in enumerate(low):
        if any(h.startswith(s) for s in starts):
            return i
    return None


def _classified(block):
    """Return ordered list of dicts {pos, dnf, no, name, code, team} for a block."""
    h = block["headers"]
    pi, ni, di, ti = _col(h, "pos"), _col(h, "no"), _col(h, "driver"), _col(h, "team")
    out = []
    for n, row in enumerate(block["rows"]):
        pos_raw = row[pi] if pi is not None and pi < len(row) else str(n + 1)
        dnf = not pos_raw.strip().isdigit()
        pos = int(pos_raw) if pos_raw.strip().isdigit() else 99 + n
        name, code = _split_driver(row[di]) if di is not None and di < len(row) else (row[-1], "")
        out.append({
            "pos": pos, "dnf": dnf,
            "no": row[ni] if ni is not None and ni < len(row) else "",
            "name": name, "code": code,
            "team": row[ti] if ti is not None and ti < len(row) else "",
        })
    return out


def _teams_from(block):
    """Group a classified block by team -> [drivers ordered by position]."""
    teams = {}
    for d in _classified(block):
        teams.setdefault(d["team"], []).append(d)
    for v in teams.values():
        v.sort(key=lambda x: x["pos"])
    return teams


def render_h2h(ctx, intro_html="", tally_html=""):
    """Teammate head-to-head for this event, built from whatever sessions have run."""
    order = ["Qualifying", "Race", "Practice 3", "Practice 2", "Practice 1"]
    labels = [l for l in order if _block(ctx, l)]
    if not labels:
        return (intro_html + '<div class="callout watch"><strong>No sessions have run yet.</strong> '
                "Teammate head-to-heads fill in automatically from the official timing as each "
                "session is completed.</div>")
    # choose up to 3 columns, prefer Qualifying + Race + best practice
    cols = []
    for l in ("Practice 3", "Practice 2", "Practice 1"):
        if l in labels:
            cols.append(l); break
    for l in ("Qualifying", "Race"):
        if l in labels:
            cols.append(l)
    cols = cols[-3:]

    # union of teams across chosen sessions
    all_teams = {}
    for l in cols:
        for team in _teams_from(_block(ctx, l)):
            all_teams.setdefault(team, True)

    head = "".join(f"<th>{l}</th>" for l in cols)
    rows = []
    for team in sorted(all_teams):
        cells = [f"<td class='tm'>{team}</td>"]
        for l in cols:
            pair = _teams_from(_block(ctx, l)).get(team, [])
            if len(pair) < 2:
                if len(pair) == 1:
                    d = pair[0]
                    tag = "DNF" if d["dnf"] else f"P{d['pos']}"
                    cells.append(f"<td>{d['code']} <span class='muted'>{tag}</span></td>")
                else:
                    cells.append("<td class='muted-cell'>—</td>")
                continue
            a, b = pair[0], pair[1]
            atag = "DNF" if a["dnf"] else f"P{a['pos']}"
            btag = "DNF" if b["dnf"] else f"P{b['pos']}"
            cells.append(
                f"<td><span class='h2h-win'>{a['code']} <span class='muted'>{atag}</span></span>"
                f" <span class='h2h-v'>›</span> {b['code']} <span class='muted'>{btag}</span></td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    tbl = (f'<div class="table-wrap"><table class="data compact h2h"><thead><tr>'
           f'<th>Team</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    note = ('<p class="src">Green driver = ahead of their team-mate in that session '
            '(qualifying position, or race classification). Built live from Formula1.com timing.</p>')
    return intro_html + tally_html + tbl + note


def auto_h2h(ctx):
    return render_h2h(ctx)


# --------------------------------------------------------------------------
# Reliability & Pit Stops — DNF tracker + pit-stop / fastest-lap rankings
# --------------------------------------------------------------------------
def render_reliability(ctx, intro_html=""):
    out = [intro_html] if intro_html else []
    race = _block(ctx, "Race") or _block(ctx, "Sprint")
    extra = ctx.get("extra") or {}

    if race:
        drivers = _classified(race)
        h = race["headers"]
        ri = _col(h, "time", "retired")
        li = _col(h, "laps")
        finishers = [d for d in drivers if not d["dnf"]]
        dnfs = [d for d in drivers if d["dnf"]]
        out.append('<h2 class="sec">Race reliability</h2>')
        out.append('<div class="stat-row">'
                   + stat(str(len(finishers)), "Classified finishers")
                   + stat(str(len(dnfs)), "Retirements (DNF)")
                   + stat(str(len(drivers)), "Started") + '</div>')
        if dnfs:
            rws = []
            for d in dnfs:
                idx = next((i for i, r in enumerate(race["rows"])
                            if (r[_col(h, "no")] if _col(h, "no") is not None else "") == d["no"]), None)
                laps = race["rows"][idx][li] if (idx is not None and li is not None and li < len(race["rows"][idx])) else ""
                why = race["rows"][idx][ri] if (idx is not None and ri is not None and ri < len(race["rows"][idx])) else "DNF"
                rws.append(f"<tr><td class='tm'>{d['name']} <span class='drv-code'>{d['code']}</span></td>"
                           f"<td>{d['team']}</td><td class='num'>{laps}</td><td>{why}</td></tr>")
            out.append('<div class="table-wrap"><table class="data compact"><thead><tr>'
                       '<th>Driver</th><th>Team</th><th>Lap</th><th>Retired</th></tr></thead>'
                       f'<tbody>{"".join(rws)}</tbody></table></div>')
        else:
            out.append('<div class="callout watch">Every starter was classified — a clean, full-distance race.</div>')
    else:
        out.append('<div class="callout watch"><strong>The race hasn\'t run yet.</strong> '
                   "Retirements and finisher counts appear here automatically once the race "
                   "classification is published.</div>")

    # Pit stops
    ps = extra.get("pitstops")
    if ps:
        h = ps["headers"]
        di, ti, tti, si, li = (_col(h, "driver"), _col(h, "time"), _col(h, "total"),
                               _col(h, "stops"), _col(h, "lap"))
        # fastest single stationary stop = min 'Time'
        def to_f(x):
            try:
                return float(x)
            except Exception:
                return 999.0
        ranked = sorted(ps["rows"], key=lambda r: to_f(r[ti]) if ti is not None and ti < len(r) else 999.0)
        out.append('<h2 class="sec">Fastest pit stops</h2>')
        out.append('<p class="lead-note">Quickest stationary times of the race (pit crew performance, '
                   'not counting the pit-lane drive-through).</p>')
        rws = []
        for n, r in enumerate(ranked[:10]):
            nm, code = _split_driver(r[di]) if di is not None and di < len(r) else (r[-1], "")
            t = r[ti] if ti is not None and ti < len(r) else ""
            lap = r[li] if li is not None and li < len(r) else ""
            cls = " class='upcoming'" if n == 0 else ""
            rws.append(f"<tr{cls}><td class='pos'>{n+1}</td>"
                       f"<td class='tm'>{nm} <span class='drv-code'>{code}</span></td>"
                       f"<td class='num'>{t}s</td><td class='num'>L{lap}</td></tr>")
        out.append('<div class="table-wrap"><table class="data compact"><thead><tr>'
                   '<th>#</th><th>Driver</th><th>Stationary</th><th>Lap</th></tr></thead>'
                   f'<tbody>{"".join(rws)}</tbody></table></div>')

    # Fastest lap
    fl = extra.get("fastestlaps")
    if fl and fl["rows"]:
        h = fl["headers"]
        di, ti, li, ai = _col(h, "driver"), _col(h, "time"), _col(h, "lap"), _col(h, "avg")
        top = fl["rows"][0]
        nm, code = _split_driver(top[di]) if di is not None and di < len(top) else (top[-1], "")
        t = top[ti] if ti is not None and ti < len(top) else ""
        lap = top[li] if li is not None and li < len(top) else ""
        avg = top[ai] if ai is not None and ai < len(top) else ""
        out.append('<h2 class="sec">Fastest lap of the race</h2>')
        out.append(card(f"{nm} — {t}",
                        f"<p>Set on lap {lap} at an average of {avg} km/h. The fastest-lap point goes "
                        "to a top-10 finisher; watch for a late free-stop 'fastest lap' grab if a car has "
                        "a spare set of softs and a pit-window cushion.</p>", "bi-stopwatch", "accent"))

    if not race and not ps and not fl:
        pass
    return "".join(out)


def auto_reliability(ctx):
    return render_reliability(ctx)


# --------------------------------------------------------------------------
# Penalties & Stewards — FIA decision-document tracker
# --------------------------------------------------------------------------
_PEN_KIND = {
    "penalty": ("pen-bad", "Penalty"),
    "warning": ("pen-warn", "Warning"),
    "fine": ("pen-warn", "Fine"),
    "reprimand": ("pen-warn", "Reprimand"),
    "noaction": ("pen-ok", "No action"),
    "note": ("pen-note", "Note"),
}


def render_penalties(ctx, decisions=None, intro_html="", fia_url=""):
    """decisions: list of dicts {doc, session, driver, team, no, fact, outcome, kind, when}.
    Auto-extracted FIA decisions from data/<gp>/penalties_auto.json are merged in
    (deduped by document number); curated entries take precedence."""
    out = [intro_html] if intro_html else []
    decisions = list(decisions or [])
    seen = {_doc_num(d.get("doc", "")) for d in decisions}
    for a in _load_auto(ctx, "penalties_auto"):
        if _doc_num(a.get("doc", "")) not in seen:
            decisions.append(a)
            seen.add(_doc_num(a.get("doc", "")))
    decisions.sort(key=lambda d: _doc_num(d.get("doc", "")))
    if not decisions:
        out.append('<div class="callout watch"><strong>No stewards\' decisions logged yet.</strong> '
                   "This tracker is populated from the FIA event decision documents on each rebuild — "
                   "summons, infringements, penalties, fines and 'no further action' rulings.</div>")
        if fia_url:
            out.append(f'<p class="src">Source: <a href="{fia_url}" target="_blank" rel="noopener">'
                       f'FIA — {ctx.get("name", "event")} documents</a>.</p>')
        return "".join(out)

    # tally
    npen = sum(1 for d in decisions if d.get("kind") == "penalty")
    nfine = sum(1 for d in decisions if d.get("kind") == "fine")
    nwarn = sum(1 for d in decisions if d.get("kind") in ("warning", "reprimand"))
    nno = sum(1 for d in decisions if d.get("kind") == "noaction")
    out.append('<div class="stat-row">'
               + stat(str(npen), "Penalties")
               + stat(str(nfine), "Fines")
               + stat(str(nwarn), "Warnings / reprimands")
               + stat(str(nno), "No further action") + '</div>')

    rws = []
    for d in decisions:
        cls, badge = _PEN_KIND.get(d.get("kind", "note"), _PEN_KIND["note"])
        who = d.get("driver", "")
        if d.get("no"):
            who = f"<strong>#{d['no']}</strong> {who}"
        if d.get("team"):
            who += f"<br><span class='muted'>{d['team']}</span>"
        rws.append(
            f"<tr><td class='doc'>{d.get('doc','')}</td>"
            f"<td>{who}</td>"
            f"<td>{d.get('session','')}</td>"
            f"<td>{d.get('fact','')}</td>"
            f"<td><span class='pen-badge {cls}'>{badge}</span> {d.get('outcome','')}</td></tr>")
    out.append('<div class="table-wrap"><table class="data pen"><thead><tr>'
               '<th>Doc</th><th>Driver</th><th>Session</th><th>Matter</th><th>Ruling</th>'
               '</tr></thead><tbody>' + "".join(rws) + '</tbody></table></div>')
    if fia_url:
        out.append(f'<p class="src">Source: <a href="{fia_url}" target="_blank" rel="noopener">'
                   f'FIA — {ctx.get("name", "event")} documents</a> (stewards\' decisions).</p>')
    return "".join(out)


def auto_penalties(ctx):
    return render_penalties(ctx, [], fia_url=ctx.get("fia_url", ""))


# --------------------------------------------------------------------------
# Page shell (sidebar + hero + body). GP context drives all labels/nav.
# --------------------------------------------------------------------------
def shell(ctx, active_slug, page_title, hero_kicker, hero_title, hero_sub, body_html, depth=1):
    GP = ctx
    base = "../" * depth
    items = []
    for slug, fname, icon, short, _long in ctx["nav"]:
        cls = "active" if slug == active_slug else ""
        items.append(
            f'<a class="nav-link {cls}" href="{base}{GP["dir"]}/{fname}">'
            f'<i class="bi {icon}"></i><span>{short}</span></a>'
        )
    nav_html = "\n".join(items)

    return f"""<!doctype html>
<html lang="en" data-bs-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title} · F1 Commentary Hub</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700;900&display=swap" rel="stylesheet">
<link href="{base}assets/style.css" rel="stylesheet">
</head>
<body>
<button class="btn btn-danger d-lg-none menu-toggle" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar">
  <i class="bi bi-list"></i> Menu
</button>

<div class="layout">
  <aside class="sidebar offcanvas-lg offcanvas-start" tabindex="-1" id="sidebar">
    <div class="offcanvas-header d-lg-none">
      <h5 class="mb-0">Menu</h5>
      <button type="button" class="btn-close" data-bs-dismiss="offcanvas" data-bs-target="#sidebar"></button>
    </div>
    <div class="offcanvas-body flex-column p-0">
      <a class="brand" href="{base}index.html">
        <span class="brand-mark">F1</span>
        <span class="brand-text">Commentary<br>Hub</span>
      </a>
      <div class="gp-badge">
        <span class="gp-flag">{GP['flag']}</span>
        <span>
          <strong>{GP['name']}</strong><br>
          <small>{GP['year']} · {GP['round']}</small>
        </span>
      </div>
      <nav class="side-nav">
        {nav_html}
      </nav>
      <div class="side-foot">
        <!--VERSION_SLOT-->
        <a href="{base}index.html" class="nav-link"><i class="bi bi-grid"></i><span>All Grands Prix</span></a>
        <p class="sources">Sources: Formula1.com · The Race<br>Updated {BUILD_STAMP}</p>
      </div>
    </div>
  </aside>

  <main class="content">
    <header class="hero">
      <div class="hero-kicker">{hero_kicker}</div>
      <h1>{hero_title}</h1>
      <p class="hero-sub">{hero_sub}</p>
    </header>
    <div class="page-body">
      {body_html}
    </div>
    <footer class="page-footer">
      <p>Built for live TV commentary prep · {GP['flag']} {GP['name']} {GP['year']}.
      Editorial content collated &amp; summarised from
      <a href="https://www.formula1.com/" target="_blank" rel="noopener">Formula1.com</a> and
      <a href="https://www.the-race.com/" target="_blank" rel="noopener">The Race</a>.</p>
    </footer>
  </main>
</div>

<div id="lightbox" class="lightbox" onclick="this.classList.remove('open')">
  <span class="lightbox-close" aria-label="Close">&times;</span>
  <img id="lightbox-img" src="" alt="Zoomed circuit map">
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
function zoomImg(el){{
  var lb=document.getElementById('lightbox');
  document.getElementById('lightbox-img').src=el.src;
  lb.classList.add('open');
}}
document.addEventListener('keydown',function(e){{
  if(e.key==='Escape'){{var lb=document.getElementById('lightbox');if(lb)lb.classList.remove('open');}}
}});
</script>
</body>
</html>"""



# --------------------------------------------------------------------------
# Multi-GP landing index
# --------------------------------------------------------------------------
def render_index(gps):
    """Landing page: a season calendar with the next race highlighted.

    With a full season registered a flat grid of cards stops being useful, so
    events are grouped into completed, current and upcoming and the one to open
    next is called out explicitly.
    """
    today = datetime.date.today()
    for ctx in gps:
        ctx.setdefault("status", event_status(ctx, today))

    live = [c for c in gps if c["status"] == "live"]
    upcoming = [c for c in gps if c["status"] == "future"]
    past = [c for c in gps if c["status"] == "past"]
    highlight = (live or upcoming or past[-1:] or gps)[0] if gps else None

    def gp_card(ctx, badge=""):
        first = ctx["nav"][0][1]
        cls = "gp-card" + (" gp-now" if ctx is highlight else "")
        tag = f'<span class="gp-badge">{badge}</span>' if badge else ""
        return f"""<a class="{cls}" href="{ctx['dir']}/{first}">
      <div class="flag">{ctx['flag']}</div>
      <h3>{ctx['name']} {ctx['year']}{tag}</h3>
      <div class="meta">{ctx['circuit']} · {ctx['round']}</div>
      <div class="go">Open weekend hub <i class="bi bi-arrow-right"></i></div>
    </a>"""

    def row(ctx):
        first = ctx["nav"][0][1]
        when = ctx.get("race_date", "")
        try:
            when = datetime.date.fromisoformat(when).strftime("%a %d %b")
        except (ValueError, TypeError):
            pass
        state = {"past": "Completed", "live": "Under way", "future": "Upcoming"}[ctx["status"]]
        sprint = ' <span class="gp-badge">Sprint</span>' if (ctx.get("cal") or {}).get("is_sprint") else ""
        return (f'<tr class="cal-{ctx["status"]}"><td class="pos">{ctx.get("round_no", "")}</td>'
                f'<td class="drv">{ctx["flag"]} <a href="{ctx["dir"]}/{first}">{ctx["name"]}</a>{sprint}</td>'
                f'<td class="team">{ctx["circuit"]}</td><td class="nowrap">{when}</td>'
                f'<td><span class="state state-{ctx["status"]}">{state}</span></td></tr>')

    sections = []
    if live:
        sections.append('<h2 class="sec">This weekend</h2>'
                        f'<div class="gp-grid">{"".join(gp_card(c, "Live") for c in live)}</div>')
    if upcoming:
        nxt = upcoming[:3]
        sections.append('<h2 class="sec">Next up</h2>'
                        f'<div class="gp-grid">{"".join(gp_card(c) for c in nxt)}</div>')
    if past:
        sections.append('<h2 class="sec">Completed</h2>'
                        f'<div class="gp-grid">{"".join(gp_card(c) for c in reversed(past))}</div>')

    body = f"""
    {''.join(sections)}

    <h2 class="sec">Season calendar</h2>
    <div class="table-wrap"><table class="data cal-tbl">
      <thead><tr><th>Rd</th><th>Grand Prix</th><th>Circuit</th><th>Race day</th><th>Status</th></tr></thead>
      <tbody>{''.join(row(c) for c in gps)}</tbody>
    </table></div>

    <div class="callout" style="margin-top:26px">
      <strong>How to use this hub:</strong> pick a Grand Prix, then a section from the
      left sidebar. Everything is collated and summarised for live commentary from
      Formula1.com, The Race and the official FIA documents. Session <strong>results</strong>
      and <strong>weather</strong> refresh every time the build is rerun across the weekend,
      and pages for future rounds fill themselves in as tyre allocations, rookie line-ups,
      upgrade filings and FIA documents are published.
    </div>
    """
    nav_items = "\n".join(
        f'<a class="nav-link" href="{c["dir"]}/{c["nav"][0][1]}">'
        f'<i class="bi bi-flag"></i><span>{c["flag"]} {c["name"]}</span></a>'
        for c in gps
    )
    return f"""<!doctype html>
<html lang="en" data-bs-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>F1 Commentary Hub</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700;900&display=swap" rel="stylesheet">
<link href="assets/style.css" rel="stylesheet">
</head>
<body>
<button class="btn btn-danger d-lg-none menu-toggle" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar">
  <i class="bi bi-list"></i> Menu
</button>
<div class="layout">
  <aside class="sidebar offcanvas-lg offcanvas-start" tabindex="-1" id="sidebar">
    <div class="offcanvas-header d-lg-none">
      <h5 class="mb-0">Menu</h5>
      <button type="button" class="btn-close" data-bs-dismiss="offcanvas" data-bs-target="#sidebar"></button>
    </div>
    <div class="offcanvas-body flex-column p-0">
      <a class="brand" href="index.html"><span class="brand-mark">F1</span><span class="brand-text">Commentary<br>Hub</span></a>
      <nav class="side-nav"><div class="nav-section">Grands Prix</div>{nav_items}</nav>
      <div class="side-foot"><!--VERSION_SLOT--><p class="sources">Sources: Formula1.com · The Race · FIA<br>Updated {BUILD_STAMP}</p></div>
    </div>
  </aside>
  <main class="content">
    <header class="hero">
      <div class="hero-kicker">Live TV Commentary Prep</div>
      <h1>F1 Commentary Hub</h1>
      <p class="hero-sub">Collated, summarised weekend intelligence — built for the commentary box.</p>
    </header>
    <div class="page-body">{body}</div>
    <footer class="page-footer"><p>Editorial content collated &amp; summarised from
      <a href="https://www.formula1.com/" target="_blank" rel="noopener">Formula1.com</a>,
      <a href="https://www.the-race.com/" target="_blank" rel="noopener">The Race</a> and the FIA.</p></footer>
  </main>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body></html>"""


# --------------------------------------------------------------------------
# Stylesheet
# --------------------------------------------------------------------------
CSS = r"""
:root{
  --f1-red:#e10600; --f1-red-dark:#b30500;
  --bg:#0e0e14; --bg2:#15151f; --panel:#1c1c28; --panel2:#232333;
  --line:#2c2c3c; --ink:#f4f4f8; --muted:#a0a0b4;
  --hun-green:#477050; --hun-red:#cd2a3e; --sidebar-w:290px;
}
*{box-sizing:border-box}
body{
  margin:0;font-family:'Titillium Web',system-ui,Arial,sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.6;
}
a{color:#ff8a86;text-decoration:none}
a:hover{color:#ffb3b0}

/* Layout */
.layout{display:flex;min-height:100vh}
.content{flex:1;min-width:0;padding:0 clamp(18px,4vw,56px) 60px;max-width:1180px}
.menu-toggle{position:fixed;top:14px;right:14px;z-index:1090;font-weight:700}

/* Sidebar */
.sidebar{
  width:var(--sidebar-w);flex:0 0 var(--sidebar-w);
  background:linear-gradient(180deg,#14141d 0%,#101017 100%);
  border-right:1px solid var(--line);position:sticky;top:0;height:100vh;
}
.sidebar .offcanvas-body{height:100%;display:flex}
.brand{display:flex;align-items:center;gap:12px;padding:22px 22px 14px;color:var(--ink)}
.brand:hover{color:#fff}
.brand-mark{
  background:var(--f1-red);color:#fff;font-weight:900;font-size:20px;
  padding:6px 10px;border-radius:8px;letter-spacing:1px;line-height:1;
}
.brand-text{font-weight:700;font-size:15px;line-height:1.05;text-transform:uppercase;letter-spacing:.5px}
.gp-badge{
  display:flex;align-items:center;gap:12px;margin:6px 16px 10px;padding:12px 14px;
  background:var(--panel);border:1px solid var(--line);border-radius:12px;
  border-left:4px solid var(--hun-red);
}
.gp-flag{font-size:26px;line-height:1}
.gp-badge small{color:var(--muted)}
.side-nav{display:flex;flex-direction:column;gap:2px;padding:8px 12px;overflow-y:auto;flex:1}
.side-nav .nav-link,.side-foot .nav-link{
  display:flex;align-items:center;gap:12px;color:var(--muted);
  padding:10px 14px;border-radius:10px;font-weight:600;font-size:15px;
}
.side-nav .nav-link i{font-size:18px;width:20px;text-align:center}
.side-nav .nav-link:hover{background:var(--panel);color:var(--ink)}
.side-nav .nav-link.active{
  background:linear-gradient(90deg,rgba(225,6,0,.22),rgba(225,6,0,.02));
  color:#fff;border-left:3px solid var(--f1-red);padding-left:11px;
}
.side-foot{padding:12px;border-top:1px solid var(--line)}
.sources{color:#6d6d82;font-size:12px;margin:10px 4px 0}

/* Hero */
.hero{
  padding:34px 0 22px;margin-bottom:26px;border-bottom:1px solid var(--line);
  background:
    radial-gradient(1200px 200px at 0% -40%,rgba(225,6,0,.18),transparent 60%);
}
.hero-kicker{
  display:inline-block;text-transform:uppercase;letter-spacing:2px;font-weight:700;
  font-size:12px;color:#fff;background:var(--f1-red);padding:4px 12px;border-radius:20px;
}
.hero h1{font-weight:900;font-size:clamp(28px,4.4vw,46px);margin:14px 0 6px;letter-spacing:-.5px}
.hero-sub{color:var(--muted);font-size:18px;margin:0;max-width:70ch}

/* Cards & grids */
.grid{display:grid;gap:18px}
.grid.cols-2{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.grid.cols-3{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.info-card{
  background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:20px 22px;margin-bottom:18px;
}
.info-card h3{
  font-weight:700;font-size:18px;margin:0 0 12px;display:flex;align-items:center;gap:10px;
}
.info-card h3 i{color:var(--f1-red)}
.info-card.accent{border-left:4px solid var(--f1-red)}
.info-card.green{border-left:4px solid var(--hun-green)}
.info-card ul{margin:0;padding-left:20px}
.info-card li{margin-bottom:6px}
.info-card li::marker{color:var(--f1-red)}

/* Stats */
.stat-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin:0 0 6px}
.stat{
  background:var(--panel2);border:1px solid var(--line);border-radius:12px;
  padding:16px;text-align:center;
}
.stat-val{font-weight:900;font-size:26px;color:#fff;line-height:1.1}
.stat-lbl{color:var(--muted);font-size:13px;text-transform:uppercase;letter-spacing:.5px;margin-top:4px}
.stat-sub{display:block;color:#6d6d82;font-size:12px;margin-top:2px}

/* Tables */
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;margin-bottom:18px;background:var(--panel)}
table.data{width:100%;border-collapse:collapse;min-width:420px}
table.data th,table.data td{padding:10px 14px;text-align:left;border-bottom:1px solid var(--line)}
table.data thead th{
  background:var(--panel2);color:#fff;font-size:13px;text-transform:uppercase;
  letter-spacing:.5px;
  /* Standings run to 20+ rows, so keep the header visible while scrolling. */
  position:sticky;top:0;z-index:2;box-shadow:inset 0 -1px 0 var(--line);
}
/* Zebra striping does the heavy lifting for scanning across a wide row. */
table.data tbody tr:nth-child(even){background:rgba(255,255,255,.022)}
table.data tbody tr:last-child td{border-bottom:none}
table.data tbody tr:hover{background:rgba(255,255,255,.06)}
table.data tbody tr.hi{background:rgba(225,6,0,.14)}
table.data tbody tr.hi:hover{background:rgba(225,6,0,.20)}
table.data tbody tr.hi td{border-bottom-color:rgba(225,6,0,.35)}
table.data caption.tbl-cap{caption-side:top;text-align:left;color:var(--muted);font-size:13px;padding:0 0 8px;font-style:italic}

/* Position column: fixed-width badge so the numbers form a clean left rail. */
table.data td.pos{
  font-weight:800;color:var(--muted);width:52px;text-align:center;
  font-variant-numeric:tabular-nums;
}
/* The top three of any ranked table (championship, session results, grid) get
   medal colours; everything else stays quiet so it doesn't compete with the
   driver names. Opt-in via `.ranked` — a schedule's first three rows are not a
   podium, so this must not apply to every table. */
table.data.ranked tbody tr:nth-child(1) td.pos{color:#e8c14a}
table.data.ranked tbody tr:nth-child(2) td.pos{color:#c8ccd4}
table.data.ranked tbody tr:nth-child(3) td.pos{color:#cd8544}

/* Numeric columns align right on a common decimal rail. */
table.data td.num,table.data th.num{text-align:right;font-variant-numeric:tabular-nums}
table.data td.pts{
  text-align:right;font-weight:800;color:#fff;
  font-variant-numeric:tabular-nums;white-space:nowrap;
}
table.data td.pts .pts-gap{
  display:block;font-size:12.5px;font-weight:500;color:var(--muted);
  margin-top:3px;line-height:1.4;letter-spacing:.1px;
}
/* The deficit number is the figure worth reading at a glance, so it gets a
   warm, brighter tone and tabular numerals; the "to P__" reference stays
   quiet so the eye lands on the number first. */
table.data td.pts .pts-gap b{color:#ff9d6c;font-weight:700;font-variant-numeric:tabular-nums}
/* Gap to the leader is the headline stat; gap to the car directly ahead is
   secondary context, so it is a touch smaller/quieter on its own line. */
table.data td.pts .pts-gap--ahead{font-size:11.5px;color:#84849a;margin-top:0}
table.data td.pts .pts-gap--ahead b{color:#e0a684}
table.data td.pts .pts-gap--lead{color:#e8c14a;font-weight:700}
/* Team name is secondary information next to the driver. */
table.data td.team{color:var(--muted)}
table.data td.drv{font-weight:600;color:#fff;white-space:nowrap}

/* A thin team-colour rail makes team grouping readable at a glance. */
table.data td.pos{border-left:3px solid transparent}
table.data tr[data-team] td.pos{border-left-color:var(--team,transparent)}

/* Standings layout: the drivers' table has four columns and needs more room
   than the constructors' three, so this is deliberately not an even 2-up split.
   The generic `.grid.cols-2` forced both into ~320px columns, which pushed the
   420px-min tables into horizontal scroll — the main reason they read badly. */
.standings-grid{display:grid;gap:18px;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr)}
@media (max-width:1180px){.standings-grid{grid-template-columns:minmax(0,1fr)}}
.standings-grid table.data{min-width:0}
.standings-grid .table-wrap{margin-bottom:0}

/* Status pills in the season calendar. */
.state{
  display:inline-block;font-size:11px;font-weight:700;text-transform:uppercase;
  letter-spacing:.4px;padding:3px 9px;border-radius:999px;border:1px solid var(--line);
  color:var(--muted);background:var(--panel2);white-space:nowrap;
}
.state-live{color:#fff;background:var(--f1-red);border-color:var(--f1-red)}
.state-future{color:#8fd0ff;border-color:#2b4d66;background:rgba(60,140,200,.12)}
.state-past{color:#8a8a9e}
td.nowrap{white-space:nowrap}

/* Results session tabs */
.results-tabs{gap:8px;margin:0 0 18px;flex-wrap:wrap}
.results-tabs .nav-link{
  background:var(--panel2);border:1px solid var(--line);color:var(--muted);
  font-weight:700;font-size:14px;padding:8px 16px;border-radius:20px;
}
.results-tabs .nav-link:hover{color:#fff;border-color:var(--f1-red)}
.results-tabs .nav-link.active{
  background:var(--f1-red);border-color:var(--f1-red);color:#fff;
}

/* Storyline block (e.g. Aston Martin B-spec) */
.storyline{
  border:1px solid var(--f1-red);border-left-width:5px;border-radius:14px;
  background:linear-gradient(180deg,rgba(225,6,0,.10),rgba(225,6,0,.02));
  padding:22px 24px;margin:0 0 26px;
}
.storyline-tag{
  display:inline-block;background:var(--f1-red);color:#fff;font-weight:700;
  font-size:12px;letter-spacing:.6px;text-transform:uppercase;
  padding:4px 12px;border-radius:20px;margin-bottom:12px;
}
.storyline-title{margin:0 0 8px;font-weight:900;color:#fff}
.storyline-lead{color:var(--muted);font-size:16px;margin-bottom:18px}
.fia-upgrade-box{
  border:1px dashed var(--line);border-radius:12px;background:var(--panel2);
  padding:14px 18px;margin-top:16px;
}
.fia-upgrade-head{font-weight:700;color:#fff;margin-bottom:6px}
.fia-upgrade-head .bi{color:var(--f1-red);margin-right:6px}
.fia-upgrade-box p{margin:0;color:var(--muted);font-size:14px}
.fia-upgrade-box.confirmed{border-style:solid;border-color:var(--hun-green);
  background:linear-gradient(180deg,rgba(71,112,80,.16),var(--panel2))}
.fia-upgrade-box.confirmed .fia-upgrade-head{color:#8fe0a4}
.fia-upgrade-box.confirmed .fia-upgrade-head .bi{color:#8fe0a4}
.fia-upgrade-box .table-wrap{margin:12px 0 8px}
.fia-upgrade-box p+p{margin-top:8px}

/* Quotes & badges */
.quote{
  border-left:4px solid var(--f1-red);background:var(--panel2);
  margin:0 0 14px;padding:14px 18px;border-radius:0 12px 12px 0;font-style:italic;
}
.quote footer{margin-top:8px;color:var(--muted);font-style:normal;font-weight:600}
.pill{display:inline-block;background:var(--panel2);border:1px solid var(--line);
  border-radius:20px;padding:3px 12px;font-size:13px;font-weight:600;margin:0 6px 6px 0;color:var(--muted)}
.pill.hot{border-color:var(--f1-red);color:#ff8a86}
.tag-soft{color:#ff3b3b}.tag-med{color:#ffd21e}.tag-hard{color:#e0e0e0}

/* Timeline (moments) */
.timeline{position:relative;margin-left:8px;padding-left:26px;border-left:2px solid var(--line)}
.tl-item{position:relative;margin-bottom:22px}
.tl-item::before{content:"";position:absolute;left:-34px;top:4px;width:14px;height:14px;
  background:var(--f1-red);border-radius:50%;border:3px solid var(--bg)}
.tl-year{font-weight:900;color:#fff;font-size:20px}
.tl-title{font-weight:700;color:#ff8a86;margin-bottom:4px}

/* Callout */
.callout{background:linear-gradient(90deg,rgba(225,6,0,.12),transparent);
  border:1px solid var(--line);border-left:4px solid var(--f1-red);
  border-radius:12px;padding:16px 20px;margin-bottom:18px}
.callout.watch{border-left-color:var(--hun-green)}
.callout.accent{border-left-color:var(--hun-green);background:linear-gradient(90deg,rgba(0,166,80,.1),transparent)}
.callout.alert{border-left-color:var(--f1-red)}
.src{color:#6d6d82;font-size:13px;font-style:italic}

/* Index landing */
.gp-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-top:10px}
.gp-card{display:block;background:var(--panel);border:1px solid var(--line);border-radius:16px;
  padding:24px;color:var(--ink);transition:transform .15s,border-color .15s}
.gp-card:hover{transform:translateY(-3px);border-color:var(--f1-red);color:var(--ink)}
.gp-card .flag{font-size:40px}
.gp-card h3{font-weight:900;margin:10px 0 2px}
.gp-card .meta{color:var(--muted);font-size:14px}
.gp-card .go{margin-top:14px;color:#ff8a86;font-weight:700}
.subgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin-top:8px}
.subgrid a{display:flex;align-items:center;gap:10px;background:var(--panel);border:1px solid var(--line);
  border-radius:10px;padding:12px 14px;color:var(--ink);font-weight:600}
.subgrid a:hover{border-color:var(--f1-red);color:#fff}
.subgrid a i{color:var(--f1-red);font-size:18px}

.page-footer{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);color:#6d6d82;font-size:14px}
h2.sec{font-weight:800;font-size:24px;margin:30px 0 14px;padding-bottom:6px;border-bottom:2px solid var(--f1-red);display:inline-block}
@media(max-width:991px){
  .sidebar{position:fixed;height:100%}
  .content{padding-top:64px}
}

/* Circuit diagram + lightbox */
.circuit-fig{margin:0 0 18px;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;text-align:center}
.circuit-img{max-width:100%;height:auto;border-radius:10px;background:#fff;cursor:zoom-in;
  transition:transform .15s,box-shadow .15s}
.circuit-img:hover{transform:scale(1.01);box-shadow:0 0 0 3px rgba(225,6,0,.35)}
.circuit-fig figcaption{color:var(--muted);font-size:14px;margin-top:12px;text-align:left}
figure.chart{margin:0 0 18px;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px;text-align:center}
figure.chart img{max-width:100%;height:auto;border-radius:8px;background:#fff}
figure.chart figcaption{color:var(--muted);font-size:13px;margin-top:8px}

/* Interactive FastF1 pace-trace charts */
.pace-chart-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:18px;margin-bottom:20px}
.pace-chart{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px}
.pace-chart-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 8px;
  color:var(--ink);font-weight:700;font-size:14px}
.pace-chart-expand{background:transparent;border:1px solid var(--line);border-radius:8px;color:var(--muted);
  font-size:12px;padding:5px 10px;cursor:pointer;transition:border-color .15s,color .15s}
.pace-chart-expand:hover{border-color:var(--f1-red);color:#fff}
.pace-chart-canvas-wrap{width:100%}
.pace-chart-canvas-wrap-full{height:70vh}
.pace-chart-canvas{display:block;width:100%}
.pace-chart-legend{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.pace-chip{display:inline-flex;align-items:center;gap:6px;background:rgba(148,163,184,.12);
  border:1px solid var(--line);border-radius:999px;padding:4px 10px;font-size:12px;color:var(--ink);
  cursor:pointer;transition:opacity .15s,border-color .15s}
.pace-chip.off{opacity:.35}
.pace-chip:hover{border-color:var(--f1-red)}
.pace-chip-all{font-weight:700;color:var(--muted)}
.pace-chip-swatch{width:16px;height:0;border-top:3px solid var(--swatch-color,#999);display:inline-block}
.pace-chip-swatch.dashed{border-top-style:dashed}
.pace-chart-fullscreen .pace-chart-expand{display:none}
.pace-chart-modal{position:fixed;inset:0;z-index:2100;display:none;align-items:center;justify-content:center;
  background:rgba(0,0,0,.92);padding:32px}
.pace-chart-modal.open{display:flex}
.pace-chart-modal-body{width:min(1100px,94vw);max-height:92vh;overflow:auto}
.pace-chart-modal-body .pace-chart-fullscreen{width:100%}
.pace-chart-modal-close{position:absolute;top:16px;right:26px;color:#fff;font-size:44px;line-height:1;
  cursor:pointer;font-weight:700;background:transparent;border:0}
.lightbox{position:fixed;inset:0;z-index:2000;display:none;align-items:center;justify-content:center;
  background:rgba(0,0,0,.92);padding:24px;cursor:zoom-out}
.lightbox.open{display:flex}
.lightbox img{max-width:96vw;max-height:92vh;border-radius:8px;background:#fff}
.lightbox-close{position:absolute;top:16px;right:26px;color:#fff;font-size:44px;line-height:1;cursor:pointer;font-weight:700}

/* Weather cards */
.wx-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin-bottom:8px}
.wx-card{background:var(--panel2);border:1px solid var(--line);border-radius:14px;padding:16px;text-align:center}
.wx-card.wx-wet{border-color:#3b7dd8;box-shadow:inset 0 0 0 1px rgba(59,125,216,.4)}
.wx-head{font-weight:700;font-size:15px;display:flex;align-items:center;justify-content:center;gap:8px}
.wx-head i{color:var(--f1-red);font-size:22px}
.wx-card.wx-wet .wx-head i{color:#5b9bff}
.wx-day{color:var(--muted);font-size:12px;margin:4px 0 8px}
.daymark{display:inline-block;font-size:10px;font-weight:800;vertical-align:top;
  background:var(--f1-red);color:#fff;border-radius:4px;padding:1px 4px;margin-left:3px}
.wx-temp{font-weight:900;font-size:30px;color:#fff;line-height:1}
.wx-desc{color:var(--ink);font-size:14px;margin-top:2px}
.wx-meta{display:flex;justify-content:center;gap:14px;margin-top:10px;color:var(--muted);font-size:13px}
.wx-meta i{color:#5b9bff}
"""


CSS += r"""
.drv-code{
  color:var(--muted);font-size:11px;font-weight:700;letter-spacing:.4px;
  background:var(--panel2);border:1px solid var(--line);border-radius:4px;
  padding:1px 5px;margin-left:4px;vertical-align:1px;
}
.wx-tag{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);
  border:1px solid var(--line);border-radius:6px;padding:1px 6px;margin-left:6px;vertical-align:middle}
.gp-grid{display:flex;flex-wrap:wrap;gap:20px}
.gp-card{flex:1 1 280px}
.gp-now{border-color:var(--f1-red);box-shadow:0 0 0 2px rgba(225,6,0,.25)}
.gp-badge{display:inline-block;font-size:11px;font-weight:800;text-transform:uppercase;
  letter-spacing:.5px;background:var(--f1-red);color:#fff;border-radius:5px;
  padding:2px 6px;margin-left:8px;vertical-align:middle}
.cal-tbl td a{color:var(--ink);font-weight:600}
.cal-tbl td a:hover{color:#ff8a86}
.cal-past{opacity:.55}
.cal-live td{background:rgba(225,6,0,.10)}
.nav-section{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:1px;
  padding:16px 22px 6px}

/* Version history bar (injected post-build by versioning.py) */
.version-bar{
  display:flex;align-items:center;gap:10px;flex-wrap:wrap;
  background:var(--panel2);border-bottom:1px solid var(--line);
  padding:8px 22px;font-size:13px;color:var(--muted);
  position:sticky;top:0;z-index:50;
}
.version-bar label{font-weight:700;color:var(--ink);display:flex;align-items:center;gap:6px;margin:0}
.version-bar label .bi{color:var(--f1-red)}
.version-bar select{
  background:var(--bg);color:var(--ink);border:1px solid var(--line);
  border-radius:8px;padding:4px 10px;font-size:13px;font-weight:600;max-width:min(70vw,360px);
}
.version-bar select:hover{border-color:var(--f1-red)}
.version-archived{
  color:#ffd21e;font-weight:700;display:inline-flex;align-items:center;gap:6px;
}
.version-archived .bi{color:#ffd21e}
.version-bar .version-latest-link{margin-left:auto;color:var(--f1-red);font-weight:700;text-decoration:none}
.version-bar .version-latest-link:hover{text-decoration:underline}
/* When placed in the sidebar footer: stack vertically, full width, no sticky bar */
.side-foot .version-bar{
  position:static;background:transparent;border-bottom:0;
  padding:0 0 10px;margin:0 0 10px;border-bottom:1px solid var(--line);
  flex-direction:column;align-items:stretch;gap:6px;font-size:12px;
}
.side-foot .version-bar select{max-width:100%;width:100%}
.side-foot .version-bar .version-latest-link{margin-left:0}

/* Rookie FP1 career-breakdown tables */
.lead-note{color:var(--muted);font-size:14px;margin:-4px 0 16px;max-width:70ch}
.bio-meta{margin:0 0 10px;font-size:13px;color:var(--muted);display:flex;align-items:center;flex-wrap:wrap;gap:2px}
.data.compact th,.data.compact td{padding:5px 9px;font-size:13px}
.data.compact td.pos{font-weight:700;color:var(--muted);width:1.6rem;text-align:center}
.data tr.upcoming{background:rgba(205,42,62,.14)}
.data tr.upcoming td{font-weight:600}
.data .tw{display:inline-block;margin-left:6px;font-size:10px;font-weight:800;letter-spacing:.04em;
  text-transform:uppercase;color:#fff;background:var(--f1-red);border-radius:5px;padding:1px 6px;vertical-align:middle}
.data td.muted-cell{color:var(--muted);font-style:italic;font-size:12px;text-align:center}

/* Weekend News */
.news-list{display:flex;flex-direction:column;gap:14px;margin:6px 0 4px}
.news-item{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--f1-red);
  border-radius:10px;padding:14px 18px}
.news-item h3{font-size:17px;font-weight:800;margin:0 0 6px;line-height:1.3}
.news-item p{margin:0 0 8px;color:#d6d6e2;font-size:14.5px}
.news-item p:last-child{margin-bottom:0}
.news-meta{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:0 0 8px;font-size:12px;color:var(--muted)}
.news-src{display:inline-block;font-weight:800;letter-spacing:.03em;text-transform:uppercase;
  font-size:10.5px;border-radius:5px;padding:2px 7px;background:var(--panel2);border:1px solid var(--line);color:#cfcfe0}
.news-src.f1{background:rgba(225,6,0,.16);border-color:rgba(225,6,0,.5);color:#ff8a86}
.news-src.race{background:rgba(70,112,80,.18);border-color:rgba(70,112,80,.6);color:#8fdca3}
.news-when{font-style:italic}
.news-auto{display:inline-block;font-weight:800;letter-spacing:.05em;text-transform:uppercase;font-size:9.5px;
  border-radius:5px;padding:2px 6px;background:rgba(120,110,200,.16);border:1px solid rgba(140,130,220,.5);color:#b9b2ee}
.news-src a{color:inherit;text-decoration:none}
.news-src a:hover{text-decoration:underline}
.wire-tag{display:inline-block;vertical-align:middle;margin-left:10px;font-size:10px;font-weight:800;
  letter-spacing:.05em;text-transform:uppercase;border-radius:5px;padding:2px 7px;
  background:rgba(120,110,200,.16);border:1px solid rgba(140,130,220,.5);color:#b9b2ee}
.sess-head{display:flex;align-items:center;gap:10px;margin:22px 0 10px}
.sess-head .badge-done{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.04em;
  color:#fff;background:var(--hun-green);border-radius:6px;padding:2px 9px}
.sess-podium{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 10px}
.sess-podium .pod{background:var(--panel2);border:1px solid var(--line);border-radius:8px;
  padding:5px 11px;font-size:13px}
.sess-podium .pod b{color:var(--f1-red)}

/* Head-to-Head */
.data td.tm{font-weight:700;color:#fff}
.data td.num{text-align:right;font-variant-numeric:tabular-nums}
.data .muted{color:var(--muted);font-size:11px;font-weight:600}
.h2h .h2h-win{color:#8fdca3;font-weight:800}
.h2h .h2h-v{color:var(--muted);margin:0 2px}
.data.h2h td{white-space:nowrap}

/* Penalties & Stewards */
.data.pen td{vertical-align:top;font-size:13.5px}
.data.pen td.doc{font-weight:800;color:var(--muted);white-space:nowrap;width:56px}
.pen-badge{display:inline-block;font-size:10.5px;font-weight:800;letter-spacing:.03em;
  text-transform:uppercase;border-radius:5px;padding:2px 7px;margin-right:4px;color:#fff}
.pen-badge.pen-bad{background:var(--f1-red)}
.pen-badge.pen-warn{background:#c8860a}
.pen-badge.pen-ok{background:var(--hun-green)}
.pen-badge.pen-note{background:var(--panel2);border:1px solid var(--line);color:#cfcfe0}

/* Strategy predictor */
.strat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:6px 0}
.strat-card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.strat-card h4{margin:0 0 6px;font-size:14px;color:#fff}
.strat-card .stint{display:flex;gap:4px;margin:8px 0 6px;flex-wrap:wrap}
.strat-card .seg{flex:1;min-width:34px;text-align:center;font-size:11px;font-weight:800;
  border-radius:5px;padding:4px 2px;color:#111}
.seg.s-soft{background:#ff3b3b;color:#fff}.seg.s-med{background:#ffd21e}.seg.s-hard{background:#e8e8e8}
.strat-card .prob{font-size:12px;color:var(--muted)}
"""


# --------------------------------------------------------------------------
# Build driver
# --------------------------------------------------------------------------
def event_status(ctx, today=None):
    """Classify a GP as 'past', 'live' or 'future' from its session dates.

    'live' means the weekend has started but the race hasn't happened yet, which
    is when the hub is actually used on air. Anything with no parsable dates is
    treated as live so it never silently stops fetching.
    """
    today = today or datetime.date.today()
    dates = []
    for _n, _wd, date, _t in ctx.get("sessions", []):
        try:
            dates.append(datetime.date.fromisoformat(date))
        except (ValueError, TypeError):
            continue
    if not dates:
        return "live"
    if today < min(dates):
        return "future"
    if today > max(dates):
        return "past"
    return "live"


def days_to_start(ctx, today=None):
    """Days until the first session, negative once the weekend has started."""
    today = today or datetime.date.today()
    dates = []
    for _n, _wd, date, _t in ctx.get("sessions", []):
        try:
            dates.append(datetime.date.fromisoformat(date))
        except (ValueError, TypeError):
            continue
    return (min(dates) - today).days if dates else 0


def prepare(ctx):
    """Fetch live weather + results for a GP and attach to its context.

    With a full season registered this runs for 20-plus events, so the network
    work is gated on how close the race actually is: there are no results to
    fetch before a car has turned a wheel, and Open-Meteo's forecast only
    reaches about 16 days ahead. Skipping those cases keeps a full-season build
    to a sane number of requests without changing what any page renders.
    """
    ctx.setdefault("tz_offset", 1)
    status = ctx.setdefault("status", event_status(ctx))
    ahead = days_to_start(ctx)

    if status == "future" and ahead > WEATHER_HORIZON_DAYS:
        ctx["weather"] = {}
    else:
        ctx["weather"] = fetch_weather(ctx)
    ctx["weather_ok"] = bool(ctx["weather"])

    if status == "future":
        ctx["results"] = []
        ctx["extra"] = {"pitstops": None, "fastestlaps": None}
    else:
        ctx["results"] = fetch_results(ctx)
        ctx["extra"] = fetch_extra(ctx)
    return ctx


def build_all(gps):
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets"))

    with open(os.path.join(OUT, "assets", "style.css"), "w") as f:
        f.write(CSS)

    src_assets = os.path.join(ROOT, "assets_src")
    if os.path.isdir(src_assets):
        for fn in os.listdir(src_assets):
            shutil.copy2(os.path.join(src_assets, fn), os.path.join(OUT, "assets", fn))

    total = 0
    for ctx in gps:
        prepare(ctx)
        os.makedirs(os.path.join(OUT, ctx["dir"]), exist_ok=True)
        env = {
            "schedule_rows": lambda c=ctx: schedule_rows(c),
            "weather_cards": lambda c=ctx: weather_cards(c),
            "weather": ctx["weather"], "weather_ok": ctx["weather_ok"],
        }
        pages = ctx["pages"](ctx, env)
        # auto-inject the live Results page if the nav asks for it
        if any(slug == "results" for slug, *_ in ctx["nav"]) and "results" not in pages:
            done = len(ctx["results"])
            pages["results"] = dict(
                kicker="Live timing",
                title="Session Results",
                sub=("Official Formula1.com results for every completed session — "
                     f"{done} session(s) in so far."),
                body=render_results(ctx),
            )
        # auto-inject a Weekend News page if the nav asks and content omits one
        if any(slug == "news" for slug, *_ in ctx["nav"]) and "news" not in pages:
            pages["news"] = dict(
                kicker="Weekend News",
                title="Weekend News & Session Reports",
                sub=("Session-by-session reports built live from the official results — "
                     "rerun during the weekend to refresh as more sessions finish."),
                body=auto_news(ctx),
            )
        # auto-inject data-driven pages when the nav asks and content omits them
        if any(slug == "h2h" for slug, *_ in ctx["nav"]) and "h2h" not in pages:
            pages["h2h"] = dict(
                kicker="Team-mate battles",
                title="Head-to-Head",
                sub="Team-mate qualifying and race head-to-heads for this event, built live from the timing.",
                body=auto_h2h(ctx),
            )
        if any(slug == "reliability" for slug, *_ in ctx["nav"]) and "reliability" not in pages:
            pages["reliability"] = dict(
                kicker="Reliability & Pits",
                title="Reliability & Pit Stops",
                sub="Retirements, finisher counts and pit-stop rankings — filled in from the official results.",
                body=auto_reliability(ctx),
            )
        if any(slug == "penalties" for slug, *_ in ctx["nav"]) and "penalties" not in pages:
            pages["penalties"] = dict(
                kicker="Stewards",
                title="Penalties & Stewards",
                sub="Every stewards' decision, infringement, fine and penalty from the FIA event documents.",
                body=auto_penalties(ctx),
            )
        for slug, fname, icon, short, long in ctx["nav"]:
            p = pages[slug]
            htmlpage = shell(ctx, slug, p["title"], p["kicker"], p["title"], p["sub"], p["body"], depth=1)
            with open(os.path.join(OUT, ctx["dir"], fname), "w") as f:
                f.write(htmlpage)
            total += 1
        print(f"  {ctx['flag']} {ctx['name']}: {len(ctx['nav'])} pages "
              f"({ctx['weather_ok'] and 'weather OK' or 'no weather'}, "
              f"{len(ctx['results'])} result set(s))")

    with open(os.path.join(OUT, "index.html"), "w") as f:
        f.write(render_index(gps))

    # Marker so GitHub Pages serves the output verbatim (no Jekyll processing).
    open(os.path.join(OUT, ".nojekyll"), "w").close()

    print(f"Built index.html + {total} subpages across {len(gps)} GP(s) into {OUT}/")
