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
        th, _tm = map(int, _hours_offset(local_hhmm, off).split(":"))
        key = f"{date}T{th:02d}:00"
        try:
            if past:
                url = ("https://archive-api.open-meteo.com/v1/archive"
                       f"?latitude={lat}&longitude={lon}"
                       "&hourly=temperature_2m,precipitation,weathercode,wind_speed_10m"
                       f"&timezone={tz}&start_date={date}&end_date={date}")
            else:
                url = ("https://api.open-meteo.com/v1/forecast"
                       f"?latitude={lat}&longitude={lon}"
                       "&hourly=temperature_2m,precipitation_probability,weathercode,wind_speed_10m"
                       f"&timezone={tz}&start_date={date}&end_date={date}")
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
    for name, wd, _date, local in ctx["sessions"]:
        rows.append(
            f"<tr><td>{name}</td><td>{wd}</td>"
            f"<td>{local}</td><td>{_hours_offset(local, off)}</td></tr>"
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
    for name, wd, _date, local in ctx["sessions"]:
        w = weather.get(name)
        if not w:
            continue
        wet = (w["pop"] is not None and w["pop"] >= 40) or (
            w["actual"] and w["pop_txt"] not in ("-", "0.0 mm"))
        cls = "wx-wet" if wet else ""
        tag = "actual" if w["actual"] else "forecast"
        cards.append(f"""<div class="wx-card {cls}">
      <div class="wx-head"><i class="bi {w['icon']}"></i> {name} <span class="wx-tag">{tag}</span></div>
      <div class="wx-day">{wd} · {local} / {_hours_offset(local, off)}</div>
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
            if h.lower().startswith("driver"):
                nm, code = _split_driver(val)
                val = f"{nm} <span class='drv-code'>{code}</span>" if code else nm
            cls = " class='pos'" if h.lower().startswith("pos") else ""
            cells.append(f"<td{cls}>{val}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"""<div class="table-wrap"><table class="data">
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
    )


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
    cards = []
    for ctx in gps:
        first = ctx["nav"][0][1]
        cards.append(f"""<a class="gp-card" href="{ctx['dir']}/{first}">
      <div class="flag">{ctx['flag']}</div>
      <h3>{ctx['name']} {ctx['year']}</h3>
      <div class="meta">{ctx['circuit']} · {ctx['round']}</div>
      <div class="go">Open weekend hub <i class="bi bi-arrow-right"></i></div>
    </a>""")
    body = f"""
    <div class="gp-grid">{''.join(cards)}</div>

    <div class="callout" style="margin-top:26px">
      <strong>How to use this hub:</strong> pick a Grand Prix, then a section from the
      left sidebar. Everything is collated and summarised for live commentary from
      Formula1.com, The Race and the official FIA documents. Session <strong>results</strong>
      and <strong>weather</strong> refresh every time the build is rerun across the weekend.
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
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;margin-bottom:18px}
table.data{width:100%;border-collapse:collapse;min-width:420px}
table.data th,table.data td{padding:10px 14px;text-align:left;border-bottom:1px solid var(--line)}
table.data thead th{background:var(--panel2);color:#fff;font-size:13px;text-transform:uppercase;letter-spacing:.5px}
table.data tbody tr:hover{background:rgba(255,255,255,.03)}
table.data tbody tr.hi{background:rgba(225,6,0,.14)}
table.data tbody tr.hi:hover{background:rgba(225,6,0,.20)}
table.data tbody tr.hi td{border-bottom-color:rgba(225,6,0,.35)}
table.data caption.tbl-cap{caption-side:top;text-align:left;color:var(--muted);font-size:13px;padding:0 0 8px;font-style:italic}
table.data td.pos{font-weight:900;color:var(--f1-red);width:40px}

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
.wx-temp{font-weight:900;font-size:30px;color:#fff;line-height:1}
.wx-desc{color:var(--ink);font-size:14px;margin-top:2px}
.wx-meta{display:flex;justify-content:center;gap:14px;margin-top:10px;color:var(--muted);font-size:13px}
.wx-meta i{color:#5b9bff}
"""


CSS += r"""
.drv-code{color:var(--muted);font-size:12px;font-weight:700}
.wx-tag{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);
  border:1px solid var(--line);border-radius:6px;padding:1px 6px;margin-left:6px;vertical-align:middle}
.gp-grid{display:flex;flex-wrap:wrap;gap:20px}
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
"""


# --------------------------------------------------------------------------
# Build driver
# --------------------------------------------------------------------------
def prepare(ctx):
    """Fetch live weather + results for a GP and attach to its context."""
    ctx.setdefault("tz_offset", 1)
    ctx["weather"] = fetch_weather(ctx)
    ctx["weather_ok"] = bool(ctx["weather"])
    ctx["results"] = fetch_results(ctx)
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
