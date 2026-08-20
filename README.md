# F1 Commentary Hub

A good-looking, static, **multi-Grand-Prix** site to support **live TV commentary**.
Left-hand sidebar menu; every Grand Prix gets its own landing page plus **17 subpages**.

Loaded: **every remaining round of the 2026 season** — 14 Grands Prix from Belgium
(round 10) to Abu Dhabi (round 23). Hungary and Belgium have hand-written prose; the
rest are generated from the official calendar and a per-venue reference library, and
**fill themselves in** as tyre allocations, rookie line-ups, upgrade filings, FIA
documents and results are published.

> Regenerate this for any GP — before or during the weekend — with **[SKILL.md](SKILL.md)**,
> the step-by-step runbook (architecture, sources, FIA docs, weather, live results, build, verify).

## View it
Open `site/index.html` (the multi-GP hub), or serve the folder:

```bash
cd site
python3 -m http.server 8000
# then open http://localhost:8000
```

## The 17 subpages (per GP)
1. **Overview** – at-a-glance, storylines, session times, standings snapshot
2. **Weekend News** – paddock headlines + **session-by-session reports** (live top-three podiums, grows as sessions complete) + radio/quote highlights, from Formula1.com & The Race
3. **Circuit Guide** – lap-by-lap + **official 2026 circuit map (click to zoom)**, Straight-Mode zones, sectors, race-control notes
4. **Results** – live **session results** pulled from Formula1.com (fills in as FP/qualifying/the race complete)
5. **Tyres & Strategy** – Pirelli compounds, degradation, one- vs two-stop + **stint/strategy predictor**
6. **Rookies & Line-ups** – rookie outings / driver line-up notes with bios
7. **Standings & Form** – title picture, how the last race reshaped it + **championship permutations**
8. **Head-to-Head** – **team-mate qualifying/race battles** (live from timing) + 2026 season scoreline
9. **Team Watch** – team-by-team news watch
10. **Upgrades** – car development / upgrade packages
11. **Power Unit** – 2026 power-unit + energy-override data (with FP & Qualifying power limits highlighted)
12. **Penalties & Stewards** – **FIA decision-document tracker** (fines, warnings, penalties, track limits)
13. **Reliability & Pit Stops** – **DNF/finisher tracker** + **fastest pit stops** + fastest lap (live from results)
14. **Facts & Records** – lap record, poles/wins, past winners, trivia + **current-grid this-track history**
15. **Top Moments** – historic drama at the venue (timeline)
16. **Schedule & Weather** – session times in **circuit-local + Tallinn/EEST** with **live weather** (forecast + actuals)
17. **Commentary Notes** – grab-and-go cheat sheet + links to the official FIA documents

## Re-run any time during the weekend
The build is **safe to run repeatedly**. Each run wipes and regenerates `site/`, and:
- refreshes **weather** (forecast for upcoming sessions, ERA5 **actuals** for past ones),
- pulls whatever **session results** Formula1.com has published so far,
- refreshes the **Weekend News** session reports (live podiums for every completed session),
- rebuilds **Head-to-Head** and **Reliability & Pit Stops** from the live timing,
- regenerates every page from the current content + any new FIA material you've scraped.

```bash
python3 build.py
```

## Architecture
- `calendar.py` – season scraper: session times, circuit stats and official track maps
  → `data/calendar_2026.json` + `assets_src/track-<slug>.png`. Re-run when F1 confirms
  more detail; CI does it weekly.
- `circuits.py` – per-venue reference data: coordinates (for weather), circuit character,
  key corners, overtaking, tyre behaviour, lap records, talking points.
- `build.py` – driver: turns each calendar round into a GP context and builds the site.
- `f1lib.py` – engine: HTML shell, CSS, weather, live results, season index, build loop.
- `content_generic.py` – default page prose for any GP without a bespoke module.
- `content_<gp>.py` – hand-written per-GP prose (`def build_pages(ctx, env)`).
- `assets_src/` – source images (2026 circuit maps); copied to `site/assets/` on build.

Adding a race is not a manual step — it is already in the calendar. To give one
hand-written treatment, add `content_<gp>.py` and register it in `BESPOKE` in `build.py`.

### Progressive disclosure
Pages render what is actually known and mark the rest with an explicit
*"not published yet — fills in automatically"* callout rather than a gap or a guess.
Fetching is gated on race proximity (no result requests for races that haven't run, no
weather beyond Open-Meteo's 16-day horizon), so a 14-GP build still takes about 12
seconds.

## Automated LLM enrichment
`enrich.py` runs in CI (before the build) and, incrementally, summarises new
**Formula1.com / The Race** articles into news cards and structures new **FIA
decision PDFs** into penalty rows — the "LLM-type" work that used to be manual.
- Free by default via **GitHub Models** (built-in `GITHUB_TOKEN`, no secret);
  override with `LLM_ENDPOINT`/`LLM_MODEL`/`LLM_TOKEN` for e.g. Azure OpenAI.
- Curated content stays **authoritative** — auto items only fill gaps, are deduped
  against hand-written ones, and always carry a **source link + "auto" badge** so
  you can verify before saying it on air.
- The "From the wires" feed renders **newest-first**, so the day's breaking story
  (a contract extension, an injury call-up) is at the top rather than buried under
  week-old previews.
- Incremental via `data/<gp>/_seen.json`; output in `data/<gp>/*_auto.json`.
```bash
LLM_FAKE=1 python3 enrich.py --gp hungary --max 3   # offline plumbing test
LLM_TOKEN=$(gh auth token) python3 enrich.py         # real run (needs models:read)
python3 backfill_meta.py --dry-run                   # repair slug titles / missing dates
```
CI runs it Thu–Mon every 2h during a race weekend, plus twice a day on Tue/Wed so
midweek driver-market news isn't missed.
See **SKILL.md §9** for the full design.

## Times & weather
- All times shown in **circuit-local + Tallinn** — no other zones. The offset is
  computed per event from the GMT offset F1 publishes, against Tallinn's own (EEST
  until 25 Oct 2026, EET after). Fly-away sessions that land on a different **date** in
  Tallinn — every Las Vegas session does — are tagged with a red `+1d` marker.
- Weather is fetched at build time from **Open-Meteo** (no API key): the forecast for
  upcoming sessions and ERA5 **actual** conditions for completed ones, each card tagged
  accordingly. Graceful fallback if offline.

## Tech
- **Bootstrap 5.3** + **Bootstrap Icons** + **Titillium Web** (F1-style font), all via CDN
- Custom F1-inspired dark theme in `site/assets/style.css`
- Static HTML generated by the Python engine (stdlib only for the build itself)

## Sources
Editorial content collated & summarised from **Formula1.com**, **The Race**, and the
**official FIA event documents**. Live results and weather are fetched at build time.
Attributions are shown on each page.
