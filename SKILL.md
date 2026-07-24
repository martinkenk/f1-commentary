# SKILL — F1 Commentary Hub generator

Build a good-looking, static, **multi-Grand-Prix commentary-prep site**. One hub
landing page plus, for every GP, a 13-item left sidebar leading to 13 subpages:
weekend overview, circuit guide (with the official zoomable circuit map), live
**session results**, tyres, rookies/line-ups, standings, team watch, upgrades,
power unit, facts, historic moments, schedule + **live weather**, and a
commentator's cheat sheet. Content is collated from Formula1.com, The Race, and the
FIA event documents.

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
build.py            ← thin driver: registers each GP (metadata, sessions, sources)
                       and calls f1lib.build_all([...])
f1lib.py            ← engine: HTML shell, CSS, weather, live results, index, build loop
content_hungary.py  ← Hungary page prose  (def build_pages(ctx, env) -> {slug: page})
content_belgium.py  ← Belgium page prose  (same shape)
assets_src/         ← source images (circuit maps); copied to site/assets/ on build
site/               ← generated output (git-ignore or publish this)
  index.html                 ← multi-GP hub
  <gpdir>/*.html             ← 13 subpages per GP
  assets/style.css, *.png
```

**One GP = one dict in `build.py` + one `content_<gp>.py` module.** The engine never
changes when you add a race.

Design: Bootstrap 5.3 + Bootstrap Icons + Titillium Web font, dark theme, F1-red
(`#e10600`) accents, mobile offcanvas sidebar, lightbox for the circuit map.

**Times rule:** show **circuit-local time + Tallinn / EEST only** (Tallinn = local +
`tz_offset`, which is +1h while both are on summer time). No UK/US columns.

---

## 1. The GP context dict (`build.py`)

Each GP is a plain dict. Copy an existing one (e.g. `HUNGARY`) and edit:

```python
HUNGARY = {
    "name": "Hungarian Grand Prix", "year": "2026", "flag": "🇭🇺",
    "circuit": "Hungaroring, Budapest", "round": "Round 14 of 24", "dir": "hungary",
    "lat": 47.5789, "lon": 19.2486,                 # for the weather API
    "tz_local": "Budapest (CEST)", "tz_east": "Tallinn (EEST)", "tz_offset": 1,
    "sessions": [                                    # (label, "Fri 24 Jul", ISO date, local HH:MM)
        ("Practice 1", "Fri 24 Jul", "2026-07-24", "13:30"),
        ("Qualifying", "Sat 25 Jul", "2026-07-25", "16:00"),
        ("Race",       "Sun 26 Jul", "2026-07-26", "15:00"),
    ],
    "race_id": "1291", "results_slug": "hungary",    # for live Formula1.com results
    "nav": nav("Hungaroring"),                       # shared 13-item sidebar
    "pages": content_hungary.build_pages,            # the content module
}
```

Then register it: `f1lib.build_all([HUNGARY, BELGIUM, ...])`.

The shared `nav(circuit_label)` helper defines the 13 sidebar slugs. **`results` is
special** — the engine builds that page itself from live data, so content modules do
**not** author a `results` page. All other slugs must be returned by `build_pages`.
(The rendered sidebar shows 14 links = 13 pages + an "All Grands Prix" home link.)

### Finding `race_id` / `results_slug`
Formula1.com results live at:
```
https://www.formula1.com/en/results/<year>/races/<race_id>/<results_slug>/<endpoint>
```
Open the race's results page on Formula1.com and read `race_id` (a number, e.g.
Hungary 2026 = `1291`, Belgium = `1290`) and the slug from the URL. If you can't find
them yet (early in the week), leave the results page empty — it will simply say "no
sessions completed" until the data exists, and fill in on the next rebuild.

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

## 5. Write the content module (`content_<gp>.py`)

Shape:
```python
from f1lib import card, stat, ul, quote

def build_pages(ctx, env):
    schedule_rows = env["schedule_rows"]   # zero-arg, bound to this ctx
    weather_cards = env["weather_cards"]   # zero-arg, bound to this ctx
    WEATHER_OK    = env["weather_ok"]
    TZ_LOCAL_LABEL = ctx["tz_local"]
    TZ_EAST_LABEL  = ctx["tz_east"]
    PAGES = {}
    PAGES["overview"] = dict(kicker=..., title=..., sub=..., body=f"""...""")
    # ... every nav slug EXCEPT "results"
    return PAGES
```

Rules:
- Return a page for **every** nav slug except `results` (engine-built). Missing a slug
  raises a build error; that's the safety net.
- Page bodies are f-strings — **double any literal `{ }`** as `{{ }}`.
- Use the helpers `card()`, `stat()`, `ul()`, `quote()`, plus `schedule_rows()` and
  `weather_cards()` from `env`.
- **Ground every claim in scraped data.** For evergreen framing (e.g. a PU page before
  the FIA doc drops), caption it as generic and say "confirm against the FIA document"
  rather than inventing numbers.
- **Standings / results tables:** to embed a big pre-built rows block inside an
  f-string body, use plain `'''…''' + ROWS + '''…'''` concatenation (triple-single
  inside the triple-double body) so you don't fight f-string brace escaping.

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
- [ ] `index.html` lists **every** registered GP; each GP has all 13 subpages, all **200**.
- [ ] Exactly **one** `nav-link active` per page; 14 sidebar links (13 pages + "All Grands Prix").
- [ ] Circuit PNG loads (200), corner pixel white, `zoomImg` + lightbox present.
- [ ] Weather cards render, tagged forecast/actual; times local + Tallinn only.
- [ ] Results page shows whatever sessions are published (or a clean "none yet" note),
      rendered as **pill tabs** with exactly one active pane (defaults to the latest session).
- [ ] No template leakage — grep for `{{`, `PAGES[`, `__` placeholders.

Stop the temp server: `lsof -ti tcp:8770` → `kill <pid>` (numeric PID required).

---

## 7. Adding the next GP (summary)

1. Composite its **2026** circuit map onto white → `assets_src/<circuit>_circuit_map_2026.png` (§2d).
2. Scrape its sources (§2) and note `race_id` / `results_slug` (§1).
3. Add a `content_<gp>.py` with `build_pages(ctx, env)` (§5), grounded in the scrape.
4. Add the GP dict in `build.py`, `import content_<gp>`, and include it in `build_all([...])`.
5. `python3 build.py` and verify (§6).

The engine, CSS, sidebar structure, weather and results machinery are all reused
unchanged.

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
`0 6-20/2 * * 5,6,0,1` (Fri/Sat/Sun/Mon, every 2h 06:00–20:00 UTC — the race-
weekend session window). Tighten to specific race dates or widen as needed.
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
