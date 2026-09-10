---
name: f1-commentary-coverage
description: Refresh, audit, repair and publish evidence-backed Grand Prix commentary coverage, including FIA PDFs, screenshots, Pirelli artwork, standings and historical feature parity.
---

# F1 Commentary Hub: periodic coverage editor

This is the portable operating runbook for this repository. Read it on every
scheduled run, then **do the work**, not merely summarize what ought to change.
Use the current UTC date and the checked-out calendar, never a date remembered
from an earlier conversation. Last comprehensive Italy/Spain audit: **10 September
2026**. The examples in section 10 are dated evidence, not defaults for other GPs.

The output is a useful, sourced on-air briefing, not just 17 nonempty HTML files.
A linked document does not mean its contents have been covered. An automatic
screenshot does not mean the numerical transcription is correct.

## 1. External-agent contract and scheduling

Run from a checkout of `martinkenk/f1-commentary`; no particular username,
operating system, absolute path, model provider or agent product is required.
Python 3.12 is the CI reference. The build itself uses the standard library.
Optional collection dependencies are listed in section 3.

An external scheduler can invoke its chosen agent with this prompt:

> Read and execute the repository's SKILL.md. Select all active GP coverage and
> the recent post-race follow-up using today's UTC date. Refresh available
> sources, inspect all 17 rendered surfaces and their subfeatures, compare with
> earlier bespoke GPs, fix missing-but-published and stale material, and preserve
> explicit pending/conflicting/inapplicable states. Complete the source, image
> and deployment checks in the skill. Do not stop because a coverage PR exists.
> Report the GPs audited, changes made, source failures, remaining pending
> material, and whether the changes are merely proposed or actually live.
> Publication policy: REVIEW (open/update a scoped PR; do not merge).

Set that last policy to **PUBLISH** only when the repository owner explicitly
authorizes that external agent to commit/push approved work or merge its own
reviewed coverage PR. In PUBLISH mode follow section 9 through live verification.
Do not invent command-line flags for an unspecified agent provider. The scheduler
supplies the prompt, checkout, credentials and a **single-run lock**. Schedule
jobs after session finishes as well as before the weekend; use the UTC cadences
below as defaults. GitHub schedules are best-effort, not exact-time guarantees.

Before modifying anything, inspect `git status`, the current branch, recent
commits, open coverage PRs and the latest deployment/audit runs. Preserve others'
edits. Use a dedicated clean checkout/worktree for unattended work; do not reset,
stash away or overwrite somebody else's work. Fetch latest main before starting.
Never run two writers against the same data/asset checkout.

**Scope:** `enrich.active_gps()` uses UTC and selects every live weekend, the next
GP once its first session is within 10 days, and the most recently completed GP.
The latter remains selected even during a long break. Audit its post-race claims
especially in the first seven days. Use explicit `--gp` for an older correction;
do not run all-season article enrichment by default. Inventory **all** registered
rounds periodically, but do not attach today's generic news to distant events.

**Existing automation, already enabled on main:**

| Workflow | UTC schedule | Publication behavior |
|---|---|---|
| `deploy.yml` | Thu-Mon 06:00-20:00 every 2h; Tue/Wed 08:00 and 16:00; main pushes; manual dispatch | Collects data/assets, commits them, builds and publishes directly |
| `critical-race-coverage.md` / `.lock.yml` | Sun/Mon/Thu/Fri/Sat 05:23, 11:23, 17:23, 21:23; Tue/Wed 08:23, 17:23; manual dispatch | Researches and fixes editorial coverage in draft PRs; review/merge still required |

**An open PR must never suppress an audit.** Choose the event before matching a
PR. An Italy PR cannot block Spain. Inspect its branch, diff, body and sources.
For a matching same-repository PR, preserve its edits and add new scoped changes.
The built-in workflow's safe-output patch generator uses
`origin/<PR-head>..<local-tip>`: **do not merge main onto the PR head**. That would
send unrelated engine/workflow commits through the content allowlist and fail.
Audit/test a temporary integration worktree combining latest main and the PR;
transfer only the newly needed allowed edits back to the PR head, then use
`push_to_pull_request_branch` and `update_pull_request`. Report conflicts.
Only emit a no-op after a real audit, and distinguish pending review from live.
The coverage workflow permits patches up to **10 MiB**, the pinned compiler's
maximum (the default 4 MiB can reject a valid image backfill). Prefer the normal
deployment's committed automatic media. If a new automatic FIA backfill exceeds
that limit, commit verified discovery URLs but not an oversized media manifest/
image set; deployment renders the discovered public PDFs. Never commit a media
manifest pointing at uncommitted images, and report any remaining source block.

## 2. Architecture and inventory

`build.py` reads `data/calendar_2026.json`, uses chronological rounds from
`FIRST_ROUND`, creates contexts and calls `f1lib.build_all`. Currently there are
**14 GPs / 238 subpages**, plus the season index. `BESPOKE` registers Belgium,
Hungary, Netherlands, Italy and Spain; other rounds inherit `content_generic.py`.
New calendar rounds need no hand-written module unless their prose outgrows the
generic content. `circuits.py` supplies venue coordinates, character and history.

| File/surface | Responsibility |
|---|---|
| `calendar.py` | F1 calendar, local session times, race/result IDs, statistics, official maps |
| `standings.py` | Atomic official driver **and** constructor snapshot; derived gaps and freshness |
| `enrich.py`, `backfill_meta.py` | Complete FIA discovery, decision/article extraction, retries and news metadata |
| `fia_media.py` | Source-faithful PDF screenshot download/render/cache; no invented interpretation |
| `fastf1_analysis.py`, `assets_src/pace-chart.js` | Optional lap/long-run/telemetry analysis and interactive charts |
| `f1lib.py` | Shared HTML/CSS, source galleries, results, weather, news/H2H/reliability/penalties |
| `content_<gp>.py` | Reviewed event-specific stories, tables, decisions, strategy and context |
| `coverage_inventory.py` | Offline JSON inventory of data/assets, missing pages, broken local images and source status |
| `versioning.py` | Material-change history, shared assets, version picker |
| `assets_src/` | Committed source assets, copied to `site/assets/` |
| `site/`, `public/` | Generated build/history output; never hand-edit or commit on main |

Run `python3 coverage_inventory.py --all --check` **after building**. The report
lists each module, available JSON shapes/counts, event assets, discovery errors,
PDFs without automatic screenshots and broken image references. `--check` fails
for missing pages/broken local images, **not** for legitimately pending sources.
An uncached PDF can have a manual figure; verify it before adding duplicates.
The inventory cannot certify factual/editorial completeness.

Earlier reference modules are feature examples, not current fact sources:
Hungary has especially rich strategy, season H2H, track-history and context;
Belgium has completed-event/results/reliability patterns; Netherlands has sprint,
replacement-lineup and heat-hazard examples. Italy has detailed FIA PU usage,
tyre-set inventory, upgrade submissions and FastF1 analysis. Spain is a **new
Madrid venue**, not Barcelona: inherited Spanish GP history is not Madrid history.
Do not downgrade a new bespoke module to generic placeholders where these
features are applicable and published.

The 10 September offline inventory found the following committed source coverage
(counts are records, **not** independent verified facts; regenerate the inventory
instead of treating these numbers as a future completeness target):

| GP | News cards | Penalty records | FIA listing / automatic images |
|---|---:|---:|---|
| Belgium | 21 | 24 | Older curated sources/assets; no new-style discovery manifest |
| Hungary | 120 | 15 | Older curated sources/assets; no new-style discovery manifest |
| Netherlands | 213 | 25 | Older curated sources/assets; no new-style discovery manifest |
| Italy | 204 | 25 | 70 PDFs discovered; 12 categorized PDFs / 50 substantive screenshot pages |
| Spain | 40 | 0 | 6 PDFs discovered; 5 categorized PDFs / 15 substantive screenshot pages |
| Azerbaijan through Abu Dhabi (nine rounds) | 0 | 0 | Generic/reference pages and map assets; no local enrichment yet |

Only Italy had `fastf1_pace.json` at that audit. Older rich prose does not imply
that all corresponding structured datasets exist. Hungary's approximate season
H2H/scenarios are not a reusable verified season-results database. A missing
older FIA manifest does not mean its already-curated official content is absent.
Hungary's stint presentation uses `.strat-grid`, `.strat-card`, `.stint`, `.seg`
and `.prob`; its historic moments use a local `_tl` helper. These are presentation
patterns, not fitted models. Italy's stored long runs cover FP1/FP2/FP3/Q, not Race;
they contain clean-lap counts, compound, tyre-life bounds, mean time and consistency.

### Stored data contracts

| Record | Shape / meaning |
|---|---|
| `calendar_<year>.json` | Object with `events`; each has slug, chronological round, dates/sessions, sprint, race_id/results_slug, circuit stats/map |
| `standings_<year>.json` | Official timestamped driver/constructor snapshot and source URLs; use `standings.context(SEASON)` rather than duplicate point constants |
| `<gp>/news_auto.json` | Array: title, summary, source URL, source kind, session label, display `when`, sortable ISO `date` |
| `<gp>/penalties_auto.json` | Array of document/no/driver/team/session/fact/outcome/kind and source URL |
| `<gp>/_seen.json` | Incremental successful-extraction identities; not a list of successfully covered facts |
| `<gp>/fia_documents.json` | Last-good `retrieved_at`, source URL, complete `documents` with filename/URL |
| `<gp>/fia_discovery_status.json` | Latest discovery attempt, success/failure/error; independent of retained last-good listing |
| `<gp>/fia_media.json` | `checked_at`, `discovery_retrieved_at`, documents with URL/filename/categories/SHA256/fetched_at/page+asset pairs, and per-URL errors |
| `<gp>/fastf1_pace.json` | Session analysis, driver identity, fastest/optimal laps, qualifying segments, long runs, tyre stints, speed/delta traces |

Inspect actual keys in the current code/data before writing a new consumer.
Missing optional timing is normal before running, not license to fabricate it.
Corrupt JSON is a real error and must not silently become "nothing published."

## 3. Refresh sequence

First run existing commands with the available interpreter. Install dependencies
only if missing or intentionally setting up a new worker. Use a virtualenv
outside tracked source, or the CI environment; no machine-specific Python 3.11
assumption. Collection needs `pypdf`, screenshot rendering needs `pymupdf`,
FastF1 needs `fastf1 pandas numpy`. Pillow is optional for manual image conversion.
Do not add these as mandatory imports to the standard-library build.

```bash
python3 standings.py
python3 calendar.py --maps-only
LLM_FAKE=1 python3 enrich.py --max 25
python3 fia_media.py
python3 fastf1_analysis.py --active
python3 backfill_meta.py
python3 build.py
python3 coverage_inventory.py --all --check
```

Run full `python3 calendar.py` on Mondays, manual deployment dispatches or known
schedule/statistic changes. Existing maps refresh within 10 days before / 7 days
after the race, rather than being cached forever. An explicit media backfill is
`python3 fia_media.py --gp italy`; article/decision collection also supports
`--gp <slug>` and `--all` (use the latter sparingly).

`LLM_FAKE=1` is the production deterministic extractor, not a claim the data is
fictional. Optional external inference uses `LLM_ENDPOINT` (full compatible
chat-completions URL), `LLM_MODEL`, `LLM_TOKEN`. Only use an owner-approved provider;
never commit tokens or send repository/secrets to an arbitrary service.

Check **each** step's outcome. A failed discovery must not prevent rendering
already-known public PDFs or publishing unrelated successful updates. CI records
warnings, preserves last-good records, and continues for optional upstream
failures. Never append `|| true` and call a failed refresh complete. Record source
URL, attempt time, failure and retained snapshot; retry later.

Standings updates are all-or-nothing across both official tables. Minimum 2026
validation is 22 drivers/11 constructors, ordered unique positions/entries and no
loss of prior reserve-driver entries. Never sum driver totals to infer constructor
points. Tables and all current headline/gap prose use the same context `summary`,
`as_of`, `notice`, driver and constructor rows. More than 24h old warns visibly.
Current season totals are not historical "entering this GP" standings.

## 4. Sources, FIA PDFs and images

Primary sources first: FIA decisions/technical papers, Formula1.com official
results/calendar and reports, Pirelli, official team/driver announcements. The Race
provides attributed analysis and its public RSS. Open actual source URLs, including
the complete Formula1.com article `.<id>` suffix; slug-only URLs can 404.
Article bodies/JSON-LD often carry headline/datePublished not present in listings.
Access varies per article: do not assume everything past the lede is gated, and
do not bypass access controls. Summarize facts and short necessary attributed
quotations; do not copy whole articles.

### Complete FIA discovery

The current 2026 event URL is:

`https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2026-2072/event/<URL-encoded GP name>`

Use the event page, then the season-index fallback implemented in `enrich.py`.
Do not assume this season ID will apply next year. Enumerate **every PDF**, not
just filenames containing penalty/decision. Discovery and extraction are separate.
Compare URL, filename, document number, publication time, version and all
substantive pages against both existing prose and figures. A citation alone is
not completion; a familiar URL may hold a revised PDF.

**HTTP 403 or 500 is not proof of non-publication.** FIA listings have been blocked
on GitHub runners while the same local listing and already-known public PDF URLs
work. Keep last-good discovery, visibly report its failure, and try normal public
fallbacks; never bypass a block or guess filenames to claim discovery. Missing,
not yet discovered, blocked, conflicting and genuinely unpublished are different.

| Document family | Required treatment |
|---|---|
| Power Unit Information | PU tables/curves and unusual event-specific constraints, with original screenshots |
| PU elements used / new elements | Before/after/allowed counts, date/session scope, allowance watches; actual penalties separately sourced |
| Circuit/pitlane/emergency/red-zone maps | Zoomable substantive diagrams; Straight Mode, Overtake, timing lines and revisions |
| Race Director notes / SC2-SC1 | Track limits, starts, exits/rejoins, SC rules, maximum times when actually published |
| Pirelli preview/prescriptions | Compounds, axle/type pressures/camber, blankets, mandatory race and Q3 tyres |
| Car presentation submissions | Every team's component list, count, rationale, nil returns; screenshots of **all** teams |
| Car display procedure | Display times/logistics only; not evidence of submitted upgrades |
| Decisions/infringements | Fact, ruling, consequences, source PDF, subsequent revisions/appeals |
| Summons, classifications, scrutineering, visas, entry lists, heat declarations | Classify individually; summons is not a penalty, entry lists can matter for line-ups, heat is not inferred from forecast |

Administrative paperwork need not become filler. Diagrams **must not be skipped**
because text extraction is empty. Show what is legible; do not invent garage order.

### Automatic screenshots and visual transcription

`fia_media.py` reads the saved listing, fetches categorized official HTTPS FIA
PDFs (including same-URL revisions), validates PDF bytes/redirects, and renders
opaque PNGs at 2x using **`import pymupdf`**, not the unrelated `fitz` package.
It skips only a recognizable first-page FIA publication cover on multi-page
documents; all substantive pages are retained. Limits are 20 MiB/PDF, 40 pages,
8 million rendered pixels/page; oversize/encrypted/failed inputs report errors.

Assets are `fia-<gp>-<URL hash>-<PDF hash>-p<N>.png`. Unchanged files reuse
images; missing images regenerate; changed hashes create new filenames. Retain
old hashed assets because history shares them. Do not overwrite old screenshots
or purge apparently unused binaries without checking all retained versions.
The manifest associates each image with its PDF hash, page and fetch time.
Its revision counter ensures a revised same-URL PDF is not hidden behind an
older curated image; only a figure using the new hashed image suppresses it.
Retrieval time is **not** the FIA issue date.

`f1lib.shell()` appends category-specific source galleries after curated content
on circuit/PU/tyres/upgrades, including generic pages. First unseen document opens;
others use expandable details, lazy images and the existing lightbox.
A curated `<figure>` citing the same PDF `#page=N` (or caption page N) suppresses
that duplicate. A bare prose link does not. Cite each page accurately: do not
make a single figure claim it represents every page of a multi-page filing.
The complete PDF/source index remains alongside curated coverage.

Before transcribing **any** numeric FIA table, view the actual screenshot and
match row, column, unit, session/article, footnote and document revision.
Plain PDF text can reorder columns. Preserve signs, ranges, TBC and asterisks.
Do not conflate recharge with deployment; kW with MJ; metres with timing-loop
identifiers; starting with running pressure; normal with low-grip mode; or a
part-use report with a penalty ruling. Explain a distinctive constraint on air,
but label proposed engineering rationale as inference, not an FIA statement.
Automatic images never automatically verify old numerical prose.

### Pirelli artwork is a separate requirement

For every active GP, find Formula1.com's **"What tyres will the teams and drivers
have for the YEAR GRAND PRIX?"** article. Inspect inline body images, not just its
hero/social metadata. Download the complete event-preview infographic from
`media.formula1.com` using the source URL found there, without center/16:9 crop
transforms. Typical `<round>-<country><year>-preview-en` filenames are clues, not
permission to guess. Preserve every row, pressures and compound key.

Save an event/year-specific file in `assets_src/` with the actual media format,
credit/link the article and use zoomable `circuit-fig` / `circuit-img` markup.
Verify the full image visually. A cropped FIA pressure table is **not** a
substitute when the complete Pirelli graphic exists; show the FIA prescriptions
as a separate, newer/precise source. If no graphic is confirmed, record pending.
Transparent map WebPs need white compositing, not simple RGB conversion onto black.
FIA PNG rendering is already opaque. Keep map legends, mode lines and labels.

## 5. The 17-page coverage contract

Every row includes **subfeatures** to audit. Give each a state: current/populated,
stale, missing-but-published, pending after source review, blocked, conflicting,
or inapplicable. Fix all relevant published gaps, not just one showcase table.

| Page | Required coverage and parity |
|---|---|
| Overview | Current phase, key storylines, venue facts, local/Tallinn sessions, consistent current points; after race, stop predicting a result already known |
| News | Curated important stories, newest-first wires, source/date, completed-session reports and live podiums; promote major breaking stories above minor feed items |
| Circuit | Current official layout/map; every Straight Mode and Overtake point, normal/low-grip differences, sectors/speed trap, corners, overtaking, pitlane/emergency diagrams, race-control notes |
| Results | All published classifications, latest-completed active tab, starting grid; available FastF1 lap/optimal/Q-segment/long-run/speed/delta analysis |
| Tyres | Full Pirelli infographic, FIA prescriptions, nominated/mandatory compounds, wear/evolution, sourced pit-loss estimate, strategy alternatives, stint predictor, official new/used race-set inventory when published |
| Rookies | Actual event entrants, FP1 substitutes and replaced drivers, meaningful bios/context; race lineup is not identical to FP1 or season standings |
| Standings | Both official tables, readable leader/previous gaps, freshness, form with date; useful mathematically correct permutations with explicit scenario/points rules |
| H2H | Event practice/qualifying/race comparisons from results plus sourced season qualifying/race scoreline when available; define sprint/DNS/substitute counting |
| Teams | All teams' relevant event-specific watch items, drivers, form, context and sourced developments; no generic repeated filler |
| Upgrades | FIA submissions for every team, component counts/descriptions/reasons and nil returns, display procedure, follow-up technical storylines; distinguish declared items from speculation |
| Power unit | Recharge by race off/on/Q/FP/outlap; power-limited distance/rate and curves, sector exceptions, detection/activation/gap, TBCs; usage/new-parts reports and separately linked sanctions |
| Penalties | Actual decisions, fines/warnings/no-action, deleted laps, grid/pitlane consequences and later changes; auto data must remain integrated with curated rows |
| Reliability | Race finishers/retirements, only sourced causes, fastest laps, pit-stop table and whether timing means stationary or pitlane elapsed; separate current watch from known outcome |
| Facts | Correct venue/layout/length/records, recent winners, current-grid this-track history; debut venue history is inapplicable, not Barcelona data copied into Madrid |
| Moments | Concrete sourced historic venue moments with dates/results; debut venues use clearly labelled inaugural context rather than invented races |
| Schedule | Actual sprint/standard format, circuit-local and Tallinn only, date rollover, DST, weather forecast/actual labels and missing-data state; heat-hazard rules require FIA declaration |
| Notes | Compact updated on-air cheat sheet surfacing the important technical/tyre/lineup/standings/penalty changes and source links; synchronize with detailed pages |

Strategies/stints are commentary scenarios, not measured forecasts. State lap
windows, compound assumptions, stops and disruption/rain caveats. Championship
scenarios must use the current scoring regulations (including sprint points),
not assume a fastest-lap bonus: [F1 confirmed its removal from 2025](https://www.formula1.com/en/latest/article/fastest-lap-point-to-be-scrapped-in-2025-after-latest-fia-world-motor-sport.4pUjDzWnGRN7KVWENLc1BY).
The former Hungary 26-point example was corrected to 25; a 45-point lead is
safe from being overturned in one standard race, not a season-title clinch.
Do not label a hypothetical pre-race scenario as
the race's actual championship swing. Do not hand-update current points.

Historical parity does **not** require manufacturing data: Madrid has no prior
venue GP wins; pre-FP1 Spain has no event timing, race pit stops or race-used sets.
Keep useful context and an explicit source-based pending/inapplicable state.

## 6. Shared helper and content conventions

`build_pages(ctx, env)` returns `{slug: {kicker, title, sub, body}}`. The context
contains event calendar/reference/standings, source URL, sessions, navigation,
and prepared `results` / `extra`. `env` binds `schedule_rows`, `weather_cards`,
`weather_ok`. Build a bespoke module by extending generic pages where useful and
registering its callable in `build.BESPOKE`.

The engine fills absent `results`, `news`, `h2h`, `reliability`, `penalties`;
other 12 pages are required. **Overriding an auto page must preserve its helper**,
otherwise new data can silently stop appearing on an apparently richer page.

| Helper | Important contract |
|---|---|
| `render_news(ctx, general_items, session_notes)` | Curated headlines plus auto wires; notes keyed by exact session label render only for completed sessions |
| `news_item(...)`, `news_sort_key(card)` | ISO `date` sorts, `when` displays; descending; undated last; curated titles dedupe normalized auto titles |
| `render_h2h(ctx, intro_html="", tally_html="")` | Event classifications are live; season tallies are a separately sourced editorial input |
| `render_reliability(ctx, intro_html="")` | Race retirement/finisher data and `ctx["extra"]` pitstops/fastestlaps; no pre-race invented results |
| `render_penalties(ctx, decisions, intro_html, fia_url)` | Curated rows win by document number; keep real auto source URLs and late decisions |
| `render_tyre_availability(ctx, ..., official=None, compounds=None, source_url="")` | Official inventory renders even without FastF1; compounds are `(hard, medium, soft)` labels, not initial set counts |
| `render_fia_documents`, `render_fia_media` | Shared source panels/galleries, not a replacement for verified event prose |

Official tyre inventory shape is `{code: (soft_new, soft_used, medium_new,
medium_used, hard_new, hard_used)}`. Counts are nonnegative integers. The helper's
`hard=2, medium=3, soft=8` arguments are initial **set counts**, not C-numbers.
Supply event compounds and a source URL. Do not hard-code Italy attribution or
C3/C4/C5 for future venues. Event results/timing supply driver identities; no
invented team assignments from an unrelated/current roster.

FastF1's `FreshTyre` can double-count sets reused across sessions. Its estimate
is never an official remaining inventory. Prefer FIA/Pirelli/team published
race-set graphics, map FP1 substitutes to the race driver's allocation, and do
not say an official report is unpublished merely because it is not loaded.
FastF1 analysis is optional and must not hide independently available FIA data.
Preserve the `calendar.py` stdlib-shadowing workaround in `fastf1_analysis.py`.
Do not imply absent timing means a completed session did not happen.

HTML uses `<div class="table-wrap"><table class="data">`; `tbl` / `tablewrap`
do not exist. Available modifiers: `compact`, `ranked`, `h2h`, `pen`, `cal-tbl`.
Use `pos`, `num`, `team`, `drv`, `nowrap` cells and `.standings-grid`.
Only actual rankings get medal styling. Reuse `.storyline` and
`.fia-upgrade-box.confirmed` for developed team narratives and verified filings.
Escape literal braces in f-strings; escape untrusted text/attributes.
Images use `circuit-fig`, `circuit-img`, `onclick="zoomImg(this)"`, useful alt text
and source/page captions. Verify dark-theme contrast, white maps, mobile scrolling
and lightbox closing with Esc. Do not invent CSS class names.

## 7. Live results, weather and extraction gotchas

Results use `/en/results/<year>/races/<race_id>/<results_slug>/<endpoint>`.
Practice is `practice/1`, not `practice-1`; also qualifying, starting-grid,
race-result, sprint-qualifying and sprint-results. Slugs can differ from racing
calendar slugs (Abu Dhabi is an example). Future events skip results requests;
an absent table alone is not an authoritative cancellation or no-running claim.
Tabs default to the latest completed session. Driver strings such as
`Kimi AntonelliANT` are split into name/code. Preserve all published entrants.
The pit-stop summary contains both **Time of Day** and **Time**. Select the exact
`Time` column, not the first `time` prefix match; otherwise clock times get ranked
and displayed as seconds. These are pit-lane elapsed durations, not stationary
wheel changes or net pit loss. Source stationary records independently.

Weather is Open-Meteo, using actual venue coordinates, hourly indices aligned
to `Europe/Tallinn`. Future sessions use forecasts within the 16-day horizon;
past sessions use ERA5 archive estimates, normally delayed around five days.
Label forecast versus actual/archive; missing recent archive values are not
observed dry weather. Show circuit-local plus Tallinn (EEST/EET as appropriate),
including date rollover (e.g. Las Vegas `+1d`), never a blanket European +1h.

The Race RSS can contain full public text; member-only material may not.
Formula1.com metadata upgrade must occur both for URL/title relevance matches
and body matches. Generic "circuit"/"grand"/"prix" keywords must not capture every
article. Retain full article IDs. `backfill_meta.py` repairs missing dates and
obvious slug titles, preserving editorial titles. Check stored card position/date
before declaring a news story absent: poor ordering previously buried breaking
lineup/contract news below promotions.

`_seen.json` records successful extraction, not attempts. Legacy seen records
are reconciled against actual output citations; failed PDFs/articles retry.
Unextractable betting promotions/live blogs may remain failures; do not mark
them successful or invent summaries. Curated news/penalties win deduplication,
but an inaccurate curated row must itself be corrected.

## 8. Validation and evidence

Run the smallest existing targeted regression tests while editing; before
publishing an integrated multi-surface change:

```bash
python3 -m unittest discover -p 'test_*.py'
python3 build.py
python3 coverage_inventory.py --all --check
git diff --check
```

Inspect all 17 pages of each changed GP, not just the source module. Compare
headlines/tables with authoritative sources and all applicable section 5 features.
Check Italy/Spain corrections against section 10. Confirm images are visible,
uncropped, correct page/version, local files exist and duplicate figures are
suppressed. The index must show every registered GP; each page has 17 GP nav links,
one active item, and the separate all-GPs link. Results have one active latest tab.
Check for leaked template syntax, stale "awaiting"/"before the race" statements,
wrong venue/team names and archived timestamps mislabelled as current.

For browser inspection run `python3 -m http.server 8000 --directory site` in a
managed foreground/background session. Verify it responds, view desktop/mobile
pages and lightboxes, then terminate that specific server process/session.
Do not leave unmanaged background servers or raw PDF scratch files in the repo.

Only when workflow source changes, compile it with the installed GitHub Agentic
Workflows extension:

```bash
gh aw compile critical-race-coverage --no-check-update
```

Commit both Markdown and generated lock file; do not hand-edit the lock.
Inspect generated diff and allowlists. The coverage agent itself may edit only
its permitted content/data/assets/tests, not grant itself workflow permissions.

## 9. Publication, version history and diagnosing stalls

In REVIEW mode open/update a scoped `[coverage]` PR with audited GP(s), facts
fixed, real sources, pending/conflicting/blocked material and evidence. Be clear
it is not deployed. In owner-authorized PUBLISH mode review the final diff,
commit only intended files, synchronize concurrent bot changes safely and push
main (or merge the authorized PR). Never force-push main or blindly merge arbitrary
pending PR code. Include the repository's requested coauthor trailer when applicable.

Track the deployment for **that commit**, not any older green run:

```bash
gh run list --workflow deploy.yml --limit 5
gh run view <run-id>
gh run watch <run-id> --exit-status
```

Inspect optional-step warnings even if the overall run is green. Verify actual
live changed pages and new images under
`https://martinkenk.github.io/f1-commentary/`; match distinctive text/asset URLs.
A successful build or push alone is not publication. To rerun an existing deployed
revision use `gh workflow run deploy.yml`; editorial audits can likewise be
manually dispatched by their compiled workflow name/file.

CI persists data/assets to main before building. Its `GITHUB_TOKEN` push does not
trigger another workflow, so no loop. The deploy concurrency group serializes
runs without cancelling an in-progress history update. Concurrent outside pushes
can still require reconciling a rejected data push; do not solve this by forcing.

Version history lives on orphan `site-history`, not main. Production uses:

`python3 versioning.py site public --threshold 3 --keep 8`

Timestamps/version widgets are ignored for material-change detection. Archived
HTML shares root binary assets; content-hashed FIA revisions preserve old images.
Keep eight snapshots in production; CLI defaults may differ. `.raw` is a history
diff mirror excluded from Pages upload. File count caused past deployment
timeouts: 20 x ~240 pages was too much. Pages gets a 10-minute timeout and one
delayed retry. Do not casually increase retention or duplicate every image into
every version. Do not delete history to hide a failure.

When automation seems broken, inspect **outcome and logs**, not just schedule:
was the workflow enabled, delayed, source-blocked, parsing incorrectly, marking
failures seen, reusing old maps, stuck behind a PR, or publishing a stale checkout?
Was the new material merely linked, transcribed but not illustrated, or proposed
in a draft PR never merged? These are distinct fixes. Older gh-aw runs also hit
sandbox network/proxy failures; check actual allowed host/connectivity errors
rather than repeatedly changing prose. Do not weaken access controls.

## 10. Dated Italy / Spain source lessons (10 September 2026)

Use these to catch regressions, not as values for other circuits or later documents.
Reopen originals on subsequent audits. Italy raced **6 September**; Spain/Madrid
is **13 September**, not another Barcelona round.

**Italy:** FIA Doc 8 PU page 2: race recharge 7.0/7.5 MJ (Overtake off/on),
Q 5.0, FP 7.5, non-race outlap 9.0; power-limited distance 4218 m, 50 kW/s.
FP **and** Q use Base-Overtake. Alt 1 is identified T4-T7 / 2100-2800 m, not
blanket all other straights. Detection 5050 m remains TBC, L18; activation
5249 m, L19; gap 1.0s. L18/L19 are loops, not corners. Show four Straight Mode
zones from the official map.
Doc 26 (4 September, 18:01) requires **below 1:42.0 between the Safety Car lines**
during **and after** qualifying and during race reconnaissance when the pit exit
is open. The old coverage PR omitted "during"; use the actual note, not its diff.

Doc 9 PU usage is a **4 September pre-running** snapshot, not post-race totals.
Doc 33 (`new_pu_elements_for_this_competition_1.pdf`, 5 September 12:40)
has two substantive pages, **2 and 3**. Lawson previous/new/allowed:
ICE/TC/EXH 5/6/4; MGU-K 3/4/3; PU-ANC 6/7/6. Doc 41's 35-place penalty
and Doc 57's later parc-ferme pitlane start are distinct. Alonso Doc 56
pitlane start covers sixth ES, sixth PU-CE and fifth MGU-K.
Ferrari Doc 18 ancillary elements were sixth, not first.
The full car-presentation submission includes every team, not just its first page.

**Spain:** Six FIA papers were discovered on 10 September: Doc 1 Pirelli preview,
visa, Doc 3 PU, Doc 4 display procedure, Doc 5 race notes, Doc 6 maps.
Map has substantive circuit/emergency/pitlane pages 2/3/4. Notes have nine
substantive pages. Display procedure is not the yet-to-be-filed team upgrade list.

PU: race recharge 8.5/9.0 MJ, Q 7.5, FP/outlap 9.0; 3206 m, 100 kW/s.
Alt 1 T5-T22 / 1500-5100 m* (preserve unexplained asterisk).
350 kW exceptions: T15-T16 3600-3800, T18-T19 4100-4300,
T20-T21 4600-4800. Q-only exit-T22 reduction 5100-5300 and reset 5200-5400.
Gap 1.0s, loops L24/L25; both absolute Overtake distances **TBC**.

Map v3 is **5.414 km**, sectors 1.839/2.049/1.526; PU/Pirelli/calendar say
**5.416 km**. Show the discrepancy; do not silently recompute the published
57 laps / 308.524 km. Two Straight Mode zones: A1 100m after T22
(low grip 130m), A2 40m after T3 (low grip 90m). Overtake detection is
entry T22, activation 20m after T22; these relative locations do not resolve
the PU sheet's absolute TBCs. Timing: I1 85m before T7, I2 40m before T16,
speed trap 160m before T5.

C2 hard / C3 medium / C4 soft; C2/C3 mandatory race, C4 Q3.
FIA starting / expected running / camber: slick F 26.5 / >=27.5 / -2.75 deg,
R 25.5 / >=26.5 / -1.5; inter F 28 / >=29 / -3, R 26.5 / >=27.5 / -2;
wet F 27 / >=29 / -3, R 25 / >=27.5 / -2. Maximum blanket time 2h,
slick/inter 70 C, wet 40 C (actual tyre-surface temperatures).
Pirelli's 25s pit loss is an **estimate**, not measured; evolution 5/5,
lateral demand 4/5, abrasion 2/5. Full artwork is `14-es26-preview-en.webp`
from the event's Formula1.com tyre article, not a cropped FIA table.

Race notes: T22 can delete current/following classified laps; SC2-SC1 maximum
to follow FP2 (no known number yet); double-yellow FP lap deletion; blue warning
3.0s / panels 1.2s; two extra FP2 grid-start laps; no normal pit-exit/Q starts,
specific race-recon exception in 13.6; narrow-pitlane merge rules; SC resumption
waits before T18; prescribed T1/T2 and T5/T5A runoff routes and T11 block rejoin.
Display Fri 12:00-13:00 Madrid / 13:00-14:00 Tallinn; race Sun 15:00 / 16:00.
No prior Madrid GP winners, venue records or actual 2026 race-set inventory before
running: explicitly distinguish those from general Spanish GP heritage.

The standings snapshot at this audit showed Antonelli 267, Russell 201
(66 behind), Hamilton 191; Mercedes 468. These are a dated example only:
future runs must fetch the official tables, not preserve these numbers in prose.
