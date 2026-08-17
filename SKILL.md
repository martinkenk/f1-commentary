# SKILL — F1 Commentary Hub generator

Build a good-looking, static, **multi-Grand-Prix commentary-prep site**. One hub
landing page plus, for every GP, a 17-item left sidebar leading to 17 subpages:
weekend overview, **weekend news + session reports**, circuit guide (with the
official zoomable circuit map), live **session results**, tyres + **stint/strategy
predictor**, rookies/line-ups, standings + **championship permutations**,
**team-mate head-to-head**, team watch, upgrades, power unit, **penalties &
stewards**, **reliability & pit stops**, facts + **this-track driver history**,
historic moments, schedule + **live weather**, and a commentator's cheat sheet.
Content is collated from Formula1.com, The Race, and the FIA event documents.

**This file is a runbook.** Follow it before *or during* any GP weekend and you get
the same result. The generator is **safe to re-run at any point** — it refreshes
weather, pulls in whatever session results Formula1.com has published so far, and
regenerates every page from the current content modules. Run it Thursday for the
preview, again after FP1/qualifying/the race, and each time the site fills in with
the latest data.

```bash
cd /Users/martin/Documents/code/f1-commentary
python3 build.py        # rebuild everything (safe to run repeatedly)
```

---

## 0. Architecture (what the code looks like)

The old single-file generator was split into a reusable engine + per-GP content so
new races are cheap to add and re-runs are trivial:

```
calendar.py         ← season scraper: session times, circuit stats, track maps
                       -> data/calendar_<year>.json + assets_src/track-<slug>.png
circuits.py         ← per-venue reference data: coordinates, character, corners,
                       overtaking, tyre notes, lap records, talking points
build.py            ← driver: turns the calendar into a GP dict per round and
                       calls f1lib.build_all([...])
f1lib.py            ← engine: HTML shell, CSS, weather, live results, index, build loop
content_generic.py  ← default page prose for any GP without a bespoke module
content_hungary.py  ← Hungary page prose  (def build_pages(ctx, env) -> {slug: page})
content_belgium.py  ← Belgium page prose  (same shape)
assets_src/         ← source images (circuit maps); copied to site/assets/ on build
site/               ← generated output (git-ignore or publish this)
  index.html                 ← season calendar + GP cards
  <gpdir>/*.html             ← 17 subpages per GP
  assets/style.css, *.png
```

**The whole remaining season is built automatically.** `build.py` reads
`data/calendar_2026.json` and registers every round from `FIRST_ROUND` onwards, so
adding a race is not a manual step at all — it is already there. A race only needs a
bespoke `content_<gp>.py` when you want hand-written prose; register it in the
`BESPOKE` dict and it takes over from `content_generic`.

### Progressive disclosure
A round months away still has a circuit, session times, a format and a history, and
those render immediately. Everything else — tyre allocation, rookie FP1 line-ups,
upgrade filings, the FIA power-unit map, results — renders as an explicit
*"not published yet — fills in automatically"* callout instead of a gap or a guess.
Each rebuild picks up whatever has since appeared, so pages complete themselves as
the weekend approaches. Nothing needs editing to make that happen.

Design: Bootstrap 5.3 + Bootstrap Icons + Titillium Web font, dark theme, F1-red
(`#e10600`) accents, mobile offcanvas sidebar, lightbox for the circuit map.

**Times rule:** show **circuit-local time + Tallinn only** (Tallinn = local +
`tz_offset`). No UK/US columns. `tz_offset` is computed per event in `build.py` from
the GMT offset F1 publishes for the race day, against Tallinn's own offset (EEST,
UTC+3, until 25 Oct 2026; EET, UTC+2, after). Fly-away rounds regularly land on a
different **date** in Tallinn — every Las Vegas session does — so the engine tags
those cells with a red `+1d` marker and shifts the weather lookup to match.

---

## 1. The season calendar and the GP context dict

### Refreshing the calendar
`calendar.py` is the only step that needs the network *before* a build. It scrapes
Formula1.com for every round of the season and writes `data/calendar_<year>.json`,
downloading the official detailed track map for each venue into `assets_src/`:

```bash
python3 calendar.py            # ~30s, 23 events + 23 track maps
```

Re-run it whenever F1 confirms more detail (session times and lap counts for later
rounds do change). CI runs it automatically on Mondays and on manual dispatch, and
commits any changes back to `main`. `build.py` itself never touches the network for
calendar data — it just reads the JSON, which keeps builds fast and offline-safe.

Each event records: round number (derived from **race-date chronology**, because
Formula1.com's page order is scrambled), session labels/dates/times/GMT offsets,
sprint flag, circuit length, laps, race distance, first Grand Prix, `race_id` and
`results_slug` for live results, and the track-map asset name. Fields that F1 has not
published yet are stored empty on purpose and render as "to be confirmed".

### Per-venue reference data
`circuits.py` holds what the scrape cannot give you: **coordinates** (these drive the
weather forecast, so they need to be accurate), the local-time label, and the
commentary material — circuit character, key corners, where the passes happen, tyre
behaviour, DRS zone count, lap record, trivia and storylines. Add an entry keyed by
the Formula1.com racing slug before a new venue can render a useful page.

### The GP context dict
`build.py` builds one of these per round from the calendar plus `circuits.py`; you do
not normally write them by hand:

```python
{
    "name": "Dutch Grand Prix", "year": "2026", "flag": "🇳🇱",
    "circuit": "Circuit Zandvoort", "round": "Round 12 of 23", "dir": "netherlands",
    "lat": 52.3888, "lon": 4.5409,                  # from circuits.py, for weather
    "tz_local": "Zandvoort (CEST)", "tz_east": "Tallinn (EEST)", "tz_offset": 1,
    "sessions": [                                    # (label, "Fri 21 Aug", ISO date, local HH:MM)
        ("Practice 1",        "Fri 21 Aug", "2026-08-21", "12:30"),
        ("Sprint Qualifying", "Fri 21 Aug", "2026-08-21", "16:30"),
        ("Race",              "Sun 23 Aug", "2026-08-23", "15:00"),
    ],
    "race_id": "1293", "results_slug": "netherlands",  # live Formula1.com results
    "cal": {...}, "ref": {...},                        # calendar event + circuits.py entry
    "nav": nav("Circuit Zandvoort"),                   # shared 17-item sidebar
    "pages": content_generic.build_pages,              # or a bespoke module
}
```

Knobs in `build.py`:

- `FIRST_ROUND` — the earliest round to build. Lower it to backfill finished races.
- `BESPOKE` — `{slug: build_pages}` for races with hand-written prose.
- `LATEST_STANDINGS` — championship tables carried into generic pages until each
  race supplies its own.

The shared `nav(circuit_label)` helper defines the 17 sidebar slugs. **Five are
auto-built by the engine** — `results`, `news`, `h2h`, `reliability` and `penalties` —
so content modules do not author them. All other slugs must be returned by
`build_pages`.

### Fetch gating (why a 14-GP build still takes ~12s)
`f1lib.prepare()` classifies each event as `past`, `live` or `future` from its session
dates and skips work that cannot produce anything:

- **Future events**: no result fetches at all (nothing has run).
- **More than 16 days out**: no weather fetch (beyond Open-Meteo's forecast horizon).

Without this, a full season would fire roughly 300 pointless HTTP requests per build.

### Finding `race_id` / `results_slug`
`calendar.py` resolves these automatically from the Formula1.com results index. They
appear in the URL:
```
https://www.formula1.com/en/results/<year>/races/<race_id>/<results_slug>/<endpoint>
```
Note the racing slug and the results slug differ for some events (Abu Dhabi is
`united-arab-emirates` for racing pages, `abu-dhabi` for results); `RESULTS_SLUG_FIX`
in `calendar.py` handles the exceptions.

---

## 2. Gather / refresh the sources

`web_fetch` is unreliable on JS-heavy F1.com/FIA pages — use `curl` + a small
extractor. Re-run this section whenever you rebuild to pick up new material.

### 2a. Formula1.com articles & facts
```bash
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "<article-url>" -o /tmp/art.html
```
Strip `<script>/<style>`, pull `<h1..h3> <p> <li>`, `html.unescape`. Use the need-to-know
page for facts/stats and the circuit-map image URL.

### 2b. The Race (full-text RSS — no paywall)
```bash
curl -sL "https://www.the-race.com/category/formula-1/rss/" -o /tmp/race.xml
```
The `<content:encoded>` CDATA blocks contain the **complete** articles. If a specific
piece is member-only and not in RSS, ask the user to log in via the built-in browser.

### 2c. FIA documents (PDF) — **re-check every rebuild**
The FIA keeps **publishing documents through the weekend** (revised race notes,
scrutineering, penalties, PU details). Re-scrape the event page each run and diff
against what you already have:

**When do documents appear?** The FIA creates an event's page only when it
publishes that event's *first* document — typically the Thursday of race week.
Until then the event URL returns **HTTP 500**, and the event is simply absent
from the season page's list. That 500 is the normal "not published yet" state
for a future round, not a fault; `enrich.py` reports it as an informational
line. To check whether a round has gone live, list the published events:
```bash
curl -sL -A "Mozilla/5.0" \
  "https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2026-2072" \
  | grep -oE 'event/[A-Za-z0-9%20-]+' | sort -u
```
```bash
curl -sL -A "Mozilla/5.0" "<fia-event-url>" -o /tmp/fia.html   # grab .pdf hrefs
curl -sL -A "Mozilla/5.0" "<pdf-url>" -o "fia_pdfs/<name>.pdf"
```
Extract with **python3.11** (`pypdf`, `pillow`, `pymupdf`/`fitz` installed there;
system `python3` is stdlib-only):
```bash
python3.11 - <<'PY'
from pypdf import PdfReader
for pg in PdfReader("fia_pdfs/power_unit_information.pdf").pages:
    print(pg.extract_text())
PY
```
Pull out for the pages:
- **Car Presentation Submissions** (Doc ~9, usually published Fri midday): the
  **official per-team upgrade list** — every declared updated component, its
  reason (Performance / Circuit-specific) and a short description. This is the
  authoritative source for the Upgrades page: fill the `.fia-upgrade-box`
  (mark it `confirmed`), build the per-team item-count table, and feed the
  headline into the storyline. Count rows with `^\s*\d+\s+[A-Z]` per team block
  (split on `Car Presentation – <GP>`); "No updates submitted" = nil return.
- **PU Elements Used per Driver** (Technical Delegate report): elements used so
  far per driver → **grid-penalty watch** card on the Power Unit page (flag the
  heaviest users of ICE/TC/EXH/MGU-K/ES/PU-CE/PU-ANC).
- **Power Unit / override:** override energy (e.g. 2026 8.5→9.0 MJ), deployment
  distance, **the FP and Qualifying power/energy limits** (highlight these — the user
  specifically wants them called out), power-cut zones, detection point, overtake zones.
- **Race Control notes:** track-limits corners, kerb/asphalt changes, Straight-Mode /
  override detection line, practice-start areas, SC restart point.
- **Pirelli:** nominated compounds and deg notes.

### 2d. Circuit map (2026 layout, white background)
Use the **2026** map (DRS is gone; show the **Straight Mode Zones** + overtake
detection/activation). Prefer the Formula1.com need-to-know track image, e.g.
`…/2026/Hungary/2026trackhungaroringdetailed.webp`. These are **transparent WebP** —
**composite onto solid white** or you get jagged halos on the dark theme:
```bash
python3.11 - <<'PY'
from PIL import Image
import urllib.request
urllib.request.urlretrieve("<map-url>", "/tmp/map.webp")
im = Image.open("/tmp/map.webp").convert("RGBA")
bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
bg.alpha_composite(im)
bg.convert("RGB").save("assets_src/<circuit>_circuit_map_2026.png")
PY
```
Verify the corner pixel is `(255,255,255)`. The circuit page's `<figure>` panel CSS is
white-backed and wires the map to `zoomImg()` (click → full-screen lightbox, Esc to
close). Reuse the existing markup in `content_hungary.py`'s `circuit` page.

---

## 3. Weather (live, forecast **and** actuals)

Open-Meteo, no API key. `f1lib.fetch_weather(ctx)` runs at build time and picks the
endpoint per session automatically:
- **Upcoming session** → `api.open-meteo.com/v1/forecast` (temp, precip probability, wind, code).
- **Past session** → `archive-api.open-meteo.com/v1/archive` (ERA5 **actual** conditions).

It requests `timezone=Europe/Tallinn` so hourly indices align to EEST. Each weather
card is tagged **forecast** or **actual**. ERA5 has a ~5-day lag, so a *very* recent
past session may return null → the card falls back gracefully. Offline → a "rebuild
online" note. Nothing to configure beyond `lat`/`lon` in the ctx.

---

## 4. Live session results (fills in as the weekend runs)

`f1lib.fetch_results(ctx)` fetches every session endpoint for the GP and renders only
the ones Formula1.com has published. **This is what makes re-runs valuable** — run
after FP1 and FP1 appears; run after the race and the full classification appears.

- Endpoints (`RESULT_SESSIONS` in `f1lib.py`): `practice/1`, `practice/2`,
  `practice/3`, `sprint-qualifying`, `sprint-results`, `qualifying`, `starting-grid`,
  `race-result`. **Practice uses `practice/1`, not `practice-1`** (the latter 404s).
- A completed session returns a `<table>` (`<th>` headers + `<tbody>`); an absent /
  not-yet-run session contains "No results available" and is skipped.
- Driver cells arrive as name+code concatenated, e.g. `"Kimi AntonelliANT"`; the engine
  splits them with `^(.*?)([A-Z]{3})$` into `Kimi Antonelli` + a styled `ANT` code.
- Sprint endpoints simply return "No results available" on a standard weekend, so the
  same code handles sprint and non-sprint GPs with no changes.

The Results page renders each session as a **Bootstrap pill tab** (`render_results`),
not a long stacked list — so there's no scrolling to reach the race. The tabs default
to the **most recent completed session** (e.g. the Race once it's run). Tab styling
lives in the `.results-tabs` CSS block; Bootstrap's bundle JS (already loaded in the
shell) drives the switching.

If the results page is empty, that's correct for early in the week — it's not an error.

---

## 4b. Weekend News & session reports (`news` page)

A dedicated **Weekend News** page (nav slug `news`, second in the sidebar) collates the
paddock storylines and gives a **session-by-session report that grows as the weekend
runs**. Split into two parts:

1. **Weekend headlines** — general stories from Formula1.com and The Race (paddock news,
   upgrades, calendar, support races). Authored as `news_item(...)` cards.
2. **Session by session** — one block per **completed** session (driven by the live
   results, so blocks only appear for sessions that have actually run). Each block shows a
   **live top-three podium strip** (pulled from `ctx["results"]`) plus any authored notes.

Engine helpers in `f1lib.py`:
- `news_item(title, summary, source="", when="", src_kind="")` — one card; `summary` is a
  string or list of paragraphs; `src_kind` is `''`/`'f1'`/`'race'` for the coloured source
  badge.
- `render_news(ctx, general_items, session_notes)` — composes the page. `general_items` is
  a list of `news_item` HTML; `session_notes` is `{session_label: [news_item, ...]}` and is
  **only rendered for sessions present in `ctx["results"]`**. Completed sessions with no
  authored note still get the auto podium strip, so the page never lies about what's run.
- `auto_news(ctx)` — engine fallback used when a content module doesn't author its own News
  page (build.py injects it automatically, exactly like the Results page). Produces the
  session podiums straight from results with no prose.

Authoring in `content_<gp>.py` (see `content_hungary.py`): import `news_item, render_news`,
build `general_news = [...]` and `session_news = {"Practice 1": [...], "Practice 2": [...]}`,
then `PAGES["news"] = dict(kicker=..., title=..., sub=..., body=render_news(ctx, general_news, session_news))`.

**On every re-run:** re-scrape The Race RSS (§2b) and Formula1.com latest (§2a) for new
weekend/session stories, add fresh `news_item`s to `general_news`, and add a
`session_news[label]` entry for each newly-completed session (FP3, Qualifying, Race…). Use
the exact session labels from `RESULT_SESSIONS` ("Practice 1", "Qualifying", "Race", etc.)
so notes attach to the right block. If you skip authoring a session's note, the live podium
still appears automatically.

---

## 4c. Data-driven pages: Head-to-Head, Reliability & Pit Stops, Penalties

Three more sidebar pages that fill in **live from the timing / FIA docs**. All three have an
**engine auto-fallback** (injected in `build_all`, exactly like Results/News) so any GP gets
a working page even with no curated prose; content modules layer curated context on top.

**Head-to-Head (`h2h`)** — team-mate battles for the event, `render_h2h(ctx, intro_html, tally_html)`.
Groups each completed session's classification by team and shows who beat their team-mate
(green = ahead), across up to three columns (best practice + Qualifying + Race). Pure
derivation from `ctx["results"]` — no external data. Hungary appends a hand-kept **2026 season
qualifying scoreline** table for context; refresh those numbers after each qualifying.

**Reliability & Pit Stops (`reliability`)** — `render_reliability(ctx, intro_html)`. From the
Race classification: finisher vs DNF counts and a retirements table (driver / team / lap /
reason, DNFs detected via non-numeric `Pos.` = "NC"). Plus **fastest pit stops** (ranked by
stationary time) and the **fastest lap**, both pulled from two extra endpoints fetched in
`prepare()` → `ctx["extra"]` via `fetch_extra(ctx)`: `pit-stop-summary` and `fastest-laps`.
Everything degrades gracefully before the race runs (Hungary shows the pre-race reliability
watch; Belgium shows the full data).

**Penalties & Stewards (`penalties`)** — `render_penalties(ctx, decisions, intro_html, fia_url)`.
The FIA event page can't be PDF-parsed in CI, so **author the decisions per GP**: scrape the
FIA event documents (§2c), read each *Decision / Infringement / Summons* PDF, and build a list
of dicts `{doc, no, driver, team, session, fact, outcome, kind}` where `kind` ∈
`penalty | fine | warning | reprimand | noaction | note` (drives the coloured badge + the
tally row). The engine renders the table + a source link to `ctx["fia_url"]` (set per GP in
`build.py`). Fallback (no decisions) just links to the FIA docs. **On every re-run, re-scrape
the FIA page** — new decisions (grid drops, in-race time penalties, post-race DSQs) appear
through the weekend; download the fresh *Decision*/*Infringement* PDFs, extract the ruling,
and append to the `decisions` list. Track-limits "deleted lap times" docs → `kind="note"`.

Extraction recipe (homebrew `python3.11` + `pypdf`, same as §2c): the ruling is on the
`Decision` line ("No further action", "€400 fine", "Driver: Warning", "3-place grid
penalty…"), the `Fact` line summarises the incident, and the header block gives car number,
driver, competitor and session. Keep `fia_pdfs/` gitignored — the extracted text is baked
into `content_<gp>.py`, so `build.py` never reads a PDF at build time (CI-safe).

---

## 5. Write the content module (`content_<gp>.py`)

Shape:
```python
from f1lib import (card, stat, ul, quote, news_item, render_news,
                   render_h2h, render_reliability, render_penalties)

def build_pages(ctx, env):
    schedule_rows = env["schedule_rows"]   # zero-arg, bound to this ctx
    weather_cards = env["weather_cards"]   # zero-arg, bound to this ctx
    WEATHER_OK    = env["weather_ok"]
    TZ_LOCAL_LABEL = ctx["tz_local"]
    TZ_EAST_LABEL  = ctx["tz_east"]
    PAGES = {}
    PAGES["overview"] = dict(kicker=..., title=..., sub=..., body=f"""...""")
    # ... every nav slug EXCEPT "results" (and "news" is optional — auto-built if omitted)
    return PAGES
```

Rules:
- Return a page for **every** nav slug except `results`, `news`, `h2h`, `reliability` and
  `penalties` (all engine-built if omitted). Missing any other slug raises a build error;
  that's the safety net.
- Page bodies are f-strings — **double any literal `{ }`** as `{{ }}`.
- Use the helpers `card()`, `stat()`, `ul()`, `quote()`, plus `schedule_rows()` and
  `weather_cards()` from `env`.
- **Ground every claim in scraped data.** For evergreen framing (e.g. a PU page before
  the FIA doc drops), caption it as generic and say "confirm against the FIA document"
  rather than inventing numbers.
- **Standings / results tables:** to embed a big pre-built rows block inside an
  f-string body, use plain `'''…''' + ROWS + '''…'''` concatenation (triple-single
  inside the triple-double body) so you don't fight f-string brace escaping.

#### Table markup contract
There is exactly **one** set of table class names, all defined in the CSS block in
`f1lib.py`. Invented names fail silently — the table still renders, just with raw
browser defaults, which is how 49 tables once shipped completely unstyled. If a table
looks plain, check the class name against this list first.

```html
<div class="table-wrap"><table class="data">…</table></div>
```

- `.table-wrap` — required scroll container. Never put `table.data` on the page bare.
- `.data` — the only base table class. (`tbl` / `tablewrap` do **not** exist.)
- Modifiers on the same element: `compact` (denser), `ranked`, `h2h`, `pen`, `cal-tbl`.
- `ranked` gives the top three rows medal-coloured positions. Add it only to genuinely
  ranked tables — championship order, session results, the grid. A schedule's first
  three rows are not a podium.
- Cell classes carry the alignment and emphasis: `td.pos` (position), `td.num`
  (right-aligned tabular numerals — use for points, laps, times), `td.team`,
  `td.drv`, `td.nowrap`. `th.num` right-aligns the matching header.
- Row-level team colour: `<tr data-team="Ferrari" style="--team:#e8002d">` paints the
  left rail on `td.pos`.

Standings rows are **generated, not hand-written** — see `standings.py` (`DRIVERS`,
`CONSTRUCTORS`, `driver_rows()`, `ctor_rows()`). After each race update those two
tuples only; team colours, rails and points-gap labels all derive from them.

Keep standings inside `.standings-grid`, not `.grid.cols-2`: the latter caps columns
at ~320px while `table.data` has `min-width:420px`, which forces horizontal scroll.

### Running storylines (e.g. Aston Martin upgrades)
Some threads run all weekend and deserve a **dedicated, visually distinct section**
that grows as new sources drop. The Upgrades page uses a `.storyline` block (red
left-border card with a "Storyline to follow" tag) for the **Aston Martin B-spec**
saga, merging Formula1.com facts with The Race's trackside article, plus a dashed
`.fia-upgrade-box` placeholder for the **FIA official upgrade list**.

When updating a storyline on a re-run:
- Re-scrape The Race RSS (§2b) for new pieces on that team/topic and fold the fresh
  detail into the section (keep the author + date attribution in the source line).
- When the FIA publishes its **car-presentation / technical upgrade list** for the
  event, replace the `.fia-upgrade-box` placeholder text with the confirmed parts and
  their stated purpose (performance vs. circuit-specific).
- Reuse `.storyline` / `.storyline-tag` / `.storyline-title` / `.storyline-lead` /
  `.fia-upgrade-box` (all defined in the CSS in `f1lib.py`) for any other big story.

---

## 6. Build & verify

```bash
cd /Users/martin/Documents/code/f1-commentary

# syntax-check every module (catches f-string/brace errors)
for m in build.py f1lib.py content_*.py; do
  python3 -c "import ast;ast.parse(open('$m').read())" && echo "$m OK"
done

python3 build.py            # weather + results fetched live; falls back offline

cd site && python3 -m http.server 8770 >/tmp/f1.log 2>&1 &
# check pages 200:
for f in index.html $(ls hungary/*.html belgium/*.html); do
  echo "$f -> $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8770/$f)"
done
```

Checklist:
- [ ] `index.html` lists **every** registered GP; each GP has all 17 subpages, all **200**.
- [ ] Exactly **one** `nav-link active` per page; 14 sidebar links (13 pages + "All Grands Prix").
- [ ] Circuit PNG loads (200), corner pixel white, `zoomImg` + lightbox present.
- [ ] Weather cards render, tagged forecast/actual; times local + Tallinn only.
- [ ] Results page shows whatever sessions are published (or a clean "none yet" note),
      rendered as **pill tabs** with exactly one active pane (defaults to the latest session).
- [ ] No template leakage — grep for `{{`, `PAGES[`, `__` placeholders.

Stop the temp server: `lsof -ti tcp:8770` → `kill <pid>` (numeric PID required).

---

## 7. Running this before a Grand Prix (summary)

Every remaining round of the season already exists in the hub, so the normal
pre-weekend routine is short:

```bash
python3 calendar.py     # only if session details may have changed (CI does this Mondays)
python3 enrich.py       # LLM: new articles + FIA decisions for the active window
python3 build.py        # rebuild everything; verify per §6
```

That alone gives a usable page set: circuit guide with the official map, session times
in both zones, weather once inside the 16-day window, the power-unit explainer, facts,
history, and auto-collected news, results, head-to-head, reliability and penalties.

**To promote a round to bespoke treatment** (worth it for the race you are actually
commentating):

1. Check `circuits.py` has a rich entry for the venue — that alone lifts every generic
   page.
2. Scrape its sources (§2) and, if you want a curated map, composite the **2026**
   circuit map onto white → `assets_src/<circuit>_circuit_map_2026.png` (§2d).
3. Write `content_<gp>.py` with `build_pages(ctx, env)` (§5), grounded in the scrape.
4. Register it in `BESPOKE` in `build.py` and `import content_<gp>`.
5. `python3 build.py` and verify (§6).

The engine, CSS, sidebar structure, weather and results machinery are all reused
unchanged. A bespoke module only has to return the 12 non-auto pages.

---

## 8. Hosting & version history (GitHub Pages)

The site is deployed to **GitHub Pages** at
`https://<user>.github.io/f1-commentary/`, rebuilt automatically by
`.github/workflows/deploy.yml`.

**What the workflow does on each run:**
1. `python3 build.py` on the runner — so weather + Formula1.com results are
   re-fetched live (the runner has fresh data, not your local snapshot).
2. Restores the persistent **version store** by cloning the orphan
   `site-history` branch into `public/` (first run: starts empty).
3. `python3 versioning.py site public --threshold 3 --keep 20` — merges the new
   build into the version store (see below).
4. Force-pushes `public/` back to `site-history` (single-commit mirror) and
   uploads it as the Pages artifact.

**Versioning (`versioning.py`) — rollback support:**
- Diffs the new build against the live one, **ignoring** the timestamp line and
  the injected version widget. A build is *material* if it's the first ever, the
  set of pages changed, or the normalized diff exceeds `--threshold` lines
  (default 3). Trivial rebuilds (e.g. only the "Updated …" stamp changed) are
  **not** pinned — keeps the history clean.
- Material builds are pinned as immutable, self-contained snapshots under
  `public/versions/<id>/` (id = Tallinn timestamp) and recorded in
  `public/versions.json`. Keeps the last `--keep` (default 20); prunes older.
- A **Version** dropdown is injected at the top of every page (right after
  `<main class="content">`). It only appears once **≥2** versions exist; archived
  pages also get a "Back to latest" link. So if a rebuild breaks something, pick
  the previous version from the dropdown.

**Triggers:** push to `main`, `workflow_dispatch` (manual), and a narrowed cron
`0 6-20/2 * * 4,5,6,0,1` (Thu–Mon, every 2h 06:00–20:00 UTC — the race-weekend
session window). Thursday is included deliberately: it is when the FIA publishes
a round's first documents, which is prep material for Friday running. Tighten to
specific race dates or widen as needed.
Note GitHub auto-pauses scheduled workflows after ~60 days of repo inactivity.

**Workflow requirements:** `permissions: contents: write` (to push
`site-history`) + `pages: write` + `id-token: write`; and
`concurrency.cancel-in-progress: false` so a cancelled run can't corrupt the
history push. Pushing `site-history` does **not** retrigger the workflow (the
push trigger is `branches: [main]` only).

**First-time setup (already done for this repo):** create a public repo, enable
Pages with source = "GitHub Actions", push `main`. `gh auth login --web` (device
flow) grants access without sharing a token with the build.

---

## 9. Automated LLM enrichment (hands-off, runs in CI)

The cron rebuild refreshes the **deterministic** data (weather, Formula1.com
results tables) on its own. The **LLM-type** work — summarising articles into
news cards and structuring FIA decision PDFs into penalty rows — is automated by
`enrich.py`, which runs **in the same workflow, before the build**, so no manual
trigger is needed.

**What `enrich.py` does (per GP):**
1. Scrapes candidate sources — The Race RSS, Formula1.com `/en/latest` slugs, and
   the FIA event documents page (decision PDFs only: infringement / decision /
   penalty / reprimand / fine / disqualification / protest; skips summons,
   classifications, scrutineering, etc.).
2. **Incremental & idempotent** — skips anything already recorded in
   `data/<gp>/_seen.json` (article URLs + FIA filenames), so each run only spends
   tokens on genuinely new items.
3. Calls an LLM with strict-JSON, temperature-0 prompts to (a) summarise an
   article into a 2–4 sentence news card and (b) extract `{doc, driver, team,
   session, fact, outcome, kind}` from a decision PDF (`pypdf` text).
4. Writes `data/<gp>/news_auto.json` + `data/<gp>/penalties_auto.json`.

**Relevance matching — why bodies are fetched.** A story counts for a GP when a
venue keyword (`hungary`/`hungaroring`/`budapest`, `dutch`/`zandvoort`/…) appears
in its title, URL **or body**. The body check matters: season previews, team
half-term reviews and driver-market pieces routinely discuss a circuit without
naming it in the headline, and those are prime commentary material.

The Race arrives from RSS with full text attached, but Formula1.com only gives
title+URL stubs, so for F1.com the article page is fetched *during* the relevance
test (cached per run; the seen-check runs first so processed URLs are never
re-downloaded). While that page is open, the real `headline` and `datePublished`
are read from it — the listing page has neither, and a de-hyphenated slug reads
badly on screen ("Half term report racing bulls best and worst moments…").

Keyword choice is safety-critical here: because matching now reaches article
bodies, a generic token would pull in nearly everything. `_GENERIC` strips words
like "circuit"/"grand"/"prix" from the auto-derived keyword set.

`backfill_meta.py` repairs cards stored before this existed. It always fills a
missing date, but replaces a title **only** when it is plainly slug-derived, so
the summariser's own (usually better) titles survive:
```bash
python3 backfill_meta.py --dry-run     # inspect first
python3 backfill_meta.py [--gp hungary]
```

**LLM backend — free by default:**
- Default: **GitHub Models** (`https://models.github.ai/inference`, model
  `openai/gpt-4o-mini`) using the workflow's built-in `GITHUB_TOKEN` — **zero
  secret setup**. The workflow just needs `permissions: models: read`.
- Opt-in override (e.g. Azure OpenAI): set env `LLM_ENDPOINT` (full chat-
  completions URL), `LLM_MODEL`, and `LLM_TOKEN`.
- `LLM_FAKE=1` uses deterministic heuristic fallbacks (no network) — for testing
  the fetch→diff→JSON→cache plumbing offline.

**Curated content stays authoritative (anti-hallucination):** the engine
(`f1lib.py`) *merges* the auto JSON into the curated pages — it never overwrites.
- Auto **news** cards are deduped against curated stories by normalised `<h3>`
  title; session-tagged cards drop into that session's block, the rest into a
  clearly-labelled **"From the wires"** block *below* the curated headlines. Every
  auto card carries a **source link** + an **"auto" badge** so a commentator can
  verify it live before saying it on air.
- Auto **penalties** are deduped by FIA document number; a hand-written row always
  wins over the auto one for the same doc.

**Source coverage notes (`enrich.py`):**
- **The Race** (full-text RSS) is the fuller source — the summariser gets the
  whole article. **Formula1.com gates everything past the lede behind "F1
  Unlocked" login**, so only the intro paragraphs are summarisable there (still
  enough for a headline card). Two easy-to-miss bugs are fixed: F1.com article
  URLs must keep their `.<id>` suffix (the slug-only URL 404s → empty body), and
  relevance is matched against the article **body**, not just the title/URL, so
  weekend stories that omit the GP name from the headline (e.g. a driver-focused
  penalty or PU story) are still picked up while generic/other-GP news is not.

**Run it locally:**
```bash
# offline plumbing test (no tokens, heuristic output)
LLM_FAKE=1 python3 enrich.py --gp hungary --max 3
# real GitHub Models run (needs a token with models:read)
LLM_TOKEN=$(gh auth token) python3 enrich.py --gp hungary
python3 build.py        # merges data/<gp>/*.json into the pages
```
(`enrich.py` needs `pypdf`; `build.py` stays stdlib-only and just reads the JSON.)

**Active window (important now the whole season is registered):** `enrich.py`
only processes the weekend currently running, the race that just finished, and the
next round once it is within 10 days. Enriching all 14 registered GPs would waste
tokens on races with no coverage yet and — worse — file general 2026 stories against a
Grand Prix they have nothing to do with. Override with `--all`, or target one race
with `--gp <dir>`.

**In CI (`deploy.yml`):** a "Refresh season calendar" step runs `calendar.py` on
Mondays and manual dispatches, then "Auto-enrich" (`pip install pypdf` +
`python3 enrich.py`, `continue-on-error: true` so a model outage can't break the
deploy) runs before the build, then "Persist enrichment data" commits `data/` and
`assets_src/` back to `main` with the default `GITHUB_TOKEN`. That push **does not**
retrigger the workflow (GitHub suppresses `GITHUB_TOKEN`-authored pushes), so
there is no loop — and `_seen.json` persists to make the next run incremental.

---

### Deployment size (learned the hard way)
Scaling from 2 GPs to a season took each build from 34 pages to ~240, and the Pages
deployment started timing out. Two independent causes:

- **Artifact size** — every pinned snapshot carried its own copy of all 23 circuit
  maps (42 MB artifact). Snapshots now share the live root's binary assets and
  rewrite their asset URLs accordingly; `versioning.py` also strips the duplicates
  from snapshots pinned before that change, so history heals itself. → ~7.5 MB.
- **File count** — 20 snapshots × 240 pages is ~4,800 files for the Pages backend to
  process. Retention dropped to `--keep 8`, the `.raw` diff mirror is excluded from
  the upload (it lives on the `site-history` branch, which is all it is needed for),
  and `deploy-pages` uses its maximum 10-minute timeout. A transient API failure gets
  one delayed retry.

If you add many more rounds or pages, expect to trade retention depth for deploy time
again — file count matters more than bytes.

## Tooling notes / gotchas

- **Two Pythons:** `build.py` uses **stdlib only** (system `python3`). Image/PDF work
  (Pillow, pypdf, pymupdf/fitz) needs homebrew **`python3.11`**
  (`pip3.11 install pypdf pillow pymupdf`).
- **Transparent WebP maps** must be composited onto white (`alpha_composite`), never
  `.convert("RGB")` alone — that flattens onto black and creates jagged halos.
- **The Race RSS** is the reliable, paywall-free path to full articles.
- **Re-runs are idempotent & safe:** the engine wipes and regenerates `site/` each run,
  re-fetching weather and results. Run it as often as you like across the weekend.
- **Timezones:** while both cities are on summer time, Tallinn (EEST, UTC+3) = circuit
  local (CEST, UTC+2) + 1h (`tz_offset`). Re-check if a GP sits outside CEST.
- **FIA docs are published incrementally** — re-scrape the event page every rebuild.
- **Version store lives on the `site-history` branch**, not `main`. `public/` is
  git-ignored locally; it's assembled only in CI. To reset the history, delete the
  `site-history` branch and re-run the workflow.
