---
name: Critical race coverage
on:
  workflow_dispatch:
  schedule:
    - cron: "23 5,11,17,21 * * 0,1,4,5,6"
    - cron: "23 8,17 * * 2,3"
permissions:
  contents: read
  issues: read
  pull-requests: read
  copilot-requests: write
tools:
  edit: true
  web-fetch:
  bash: [":*"]
  github:
    mode: gh-proxy
network:
  allowed:
    - defaults
    - github
    - python
    - www.formula1.com
    - media.formula1.com
    - www.the-race.com
    - www.fia.com
    - www.pirelli.com
    - press.pirelli.com
    - api.open-meteo.com
    - archive-api.open-meteo.com
safe-outputs:
  # Multi-page FIA/Pirelli evidence can exceed the default 4 MiB patch limit.
  max-patch-size: 10240
  push-to-pull-request-branch:
    target: "*"
    required-title-prefix: "[coverage] "
    fallback-as-pull-request: false
    allowed-files:
      - "content_*.py"
      - "circuits.py"
      - "build.py"
      - "test_*.py"
      - "data/**/*.json"
      - "assets_src/**"
    protected-files: blocked
  update-pull-request:
    target: "*"
    required-title-prefix: "[coverage] "
    title: true
    body: true
  create-pull-request:
    title-prefix: "[coverage] "
    draft: true
    close-older-pull-requests: false
    expires: 7d
    allowed-files:
      - "content_*.py"
      - "circuits.py"
      - "standings.py"
      - "build.py"
      - "test_*.py"
      - "data/**/*.json"
      - "assets_src/**"
    protected-files: request_review
---

# Critical race coverage editor

Act as a skeptical Formula 1 commentary editor. Keep the current or next Grand
Prix as complete as published evidence allows. This is not an article-summary
task: inspect the whole information surface, identify what the regular scraper
and build have missed, and make the bounded repository improvements yourself.
**Read and execute `SKILL.md` first.** It is the authoritative portable runbook,
including the 17-page subfeature matrix, source schemas, failure semantics,
historical parity and dated Italy/Spain regression examples. This workflow uses
its REVIEW policy: deterministic data/screenshots auto-publish separately;
editorial PR changes still require review/merge. Do not claim otherwise.

## Avoid duplicate work

Use `gh pr list` to inspect open `[coverage]` pull requests, including their
body, changed files and head branch. **An open PR must never skip the audit.**
Choose the GP first; a pending Italy PR must not block Spain or later rounds.
For the same GP, fetch and check out its existing same-repository coverage branch.
Do **not** merge main's commits onto that branch: the safe-output incremental
patch would include unrelated engine/workflow files and fail the file allowlist.
Instead create a temporary integration worktree from latest `origin/main`, merge
the coverage branch there, and use that worktree for the audit and validation.
Apply only the new, allowed content/data/asset edits back to the PR head and
commit them there (no integration merge commits). Preserve its existing edits.
Use
`push_to_pull_request_branch` with its PR number, then `update_pull_request` to
refresh the evidence/pending-items summary. Do not push directly or force-push.
If there is no matching PR, start from main and create one.
If the integration merge conflicts, report the concrete blocker rather than claiming coverage
is complete. Only emit `noop` after actually auditing and finding no new gaps;
state separately what is still awaiting review and therefore not deployed.

## Determine scope

1. Read `data/calendar_2026.json`, `build.py`, `circuits.py`,
   `content_generic.py`, the relevant `content_<gp>.py` when present, and the
   active GP's `data/<gp>/*_auto.json`.
2. Use the current UTC date and session dates to select:
   - a live race weekend, otherwise
   - the next race when it is within 10 days, otherwise
   - the most recently completed race for post-event corrections.
3. Also check the most recently completed GP within seven days for stale
   pre-race claims, final classifications and later FIA decisions.
4. Run `python3 standings.py`, `python3 calendar.py --maps-only`, `python3 season_h2h.py`,
   `LLM_FAKE=1 python3 enrich.py --max 25`, `python3 fia_media.py`, and
   `python3 backfill_meta.py`. Install `pypdf`/`pymupdf` only if absent. Inspect
   each outcome: a failed listing must not prevent rendering saved public PDF
   URLs. Keep last-good records and report source errors; do not hide them.
5. Run `python3 build.py`, then `python3 coverage_inventory.py --all --check`.
   Inspect all 17 generated pages for each active GP. Review existing FastF1 data
   and completed-session gaps; the deployment's timing refresh is independent.
   Inventory all registered GPs, but do not enrich distant events with current news.
6. Compare applicable **subfeatures** against Hungary, Belgium and Netherlands,
   not just page counts. Include stint predictor, official race tyre-set inventory,
   season H2H, championship scenarios, current-grid venue history, concrete moments,
   rookies/replacements, heat declarations, upgrades and post-race updates. Preserve
   their live helpers. For a debut venue, document inapplicability rather than
   inventing history. An unavailable local dataset is not proof of non-publication.

## Research critically

Search current material from Formula1.com, the FIA event documents, Pirelli,
The Race, and official team or driver announcements. Prefer primary sources.
Every factual addition must be traceable to a URL you actually opened.

### Required collated top-news briefing

On every run, refresh `data/<gp>/news_highlights.json` for each active GP using
the priority-news contract in `SKILL.md`. Open sources and collate three to five
consequential developments, one card per topic, with a concise synthesis,
why-it-matters explanation, date and all supporting links. Rank importance, not
just recency; exclude promotions and combine duplicate coverage. Include actual
session outcomes, changed line-ups/sanctions and major team/technical developments.

Set honest review/expiry timestamps (at most 24h), the latest on-track
`through_session`, and the fingerprint from `python3 news_briefing.py --gp <slug>`
after reviewing refreshed data. Do not renew a fingerprint/timestamp without reading
the changed evidence. Normal builds expire stale selections and use labelled
automatic priority headlines until reviewed prose is merged. Confirm the collated
briefing leads both Overview and Weekend News, with the complete feed preserved.
Document missing sources and any new priority reporting not covered by the PR.

Audit every supported surface:

1. overview and key storylines
2. weekend news and completed-session reports
3. circuit map, corners, zones and race-control notes
4. session results
5. tyre allocation, pressures, degradation and strategy
6. rookie FP1 and replacement line-ups
7. current standings, form and meaningful permutations
8. team-mate context
9. team-by-team watch items
10. upgrades and FIA car-presentation filings
11. event-specific power-unit and energy-map values
12. penalties and stewards' documents
13. reliability and pit-stop information
14. facts, records, recent winners and current-grid history
15. curated historic moments
16. schedule and weather
17. concise commentary notes

Standings are a deterministic source refresh, not manually maintained constants.
Compare both tables and any leader/gap prose with the timestamped
`data/standings_2026.json` and its Formula1.com sources. Do not call current
totals "after Zandvoort" once Monza has run, or let a pre-race editorial headline
contradict the current table. Preserve historical context only when dated.

Season teammate scores likewise come from `season_h2h.py`, not hand-written
approximations. Check both qualifying and race tallies, compared/excluded counts,
replacement-driver pairings and the expandable official-source evidence. Preserve
the counting policy in `SKILL.md`; keep the event comparison below the season
table, including on upcoming GP pages. Use `--force` if an older ruling changes
classification; report retained/missing sources rather than inventing a score.

For each surface classify the state as populated, stale, missing-but-published,
pending after source review, blocked, conflicting, or inapplicable. Improve all
material missing-but-published fields that can be handled in one coherent PR.
Correct stale facts tightly coupled to those additions.

### Required Pirelli tyre artwork (every GP, every audit)

**Every** round's Tyres & Strategy page needs Pirelli's official event-preview
infographic, not just the round currently being audited in depth. Each time
this workflow runs, in addition to the primary GP under audit, spot-check the
Tyres & Strategy page of any other GP within the active window (the live/next
race — see "Determine scope" above) for this graphic; treat it as missing
whenever the round's own tyre-preview article has been published but the page
has no infographic, or is carrying a lower-quality FIA-table substitute while
the real Formula1.com graphic is now available.

For each round, look for its Formula1.com article titled in the form **"What
tyres will the teams and drivers have for the YEAR GRAND PRIX?"**. The 2026
Italian Grand Prix (Monza) example is:

`https://www.formula1.com/en/latest/article/what-tyres-will-the-teams-and-drivers-have-for-the-2026-italian-grand-prix.7nOpWdCgvCBFDGlnODs0gk`

Open the rendered article and inspect the images inside the article body rather
than relying on page metadata or assuming the social/hero image is the useful
one. The graphic normally appears after the compound-allocation paragraphs and
its alt text or source filename follows a pattern such as
`<round>-<country><year>-preview-en.jpg` — the round number and country/year
code are specific to each GP (derive them from that event's own article; do
not assume another round's values). For Monza 2026 the inline image is
`13-it26-preview-en.jpg` (served by `media.formula1.com` as
`13-it26-preview-en.webp`, and the *unresized* asset — request the URL without
a `t_16by9Centre,c_lfill` crop transform, e.g. `.../q_auto/<version>/fom-website/<year>/<Country>/<round>-<cc><yy>-preview-en.webp`
— to avoid clipping the bottom rows of the table). Locate that complete
Pirelli event-preview graphic, which includes the circuit information, tyre
demands, pressures and selected compounds. When it is published:

1. Download the highest-resolution suitable version from Formula1.com's media
   host into `assets_src/`, using a stable event-specific filename such as
   `<gp>_pirelli_tyres_<year>.<ext>`. Keep the extension consistent with the
   actual response content type.
2. Verify the downloaded file is the complete Formula1.com/Pirelli event
   infographic, not the article hero photograph, a logo, placeholder, previous
   event's artwork, or a cropped substitute from an FIA PDF. Use an FIA/Pirelli
   document image only when the rendered Formula1.com article genuinely has no
   inline event-preview graphic.
3. Add it to the Tyres & Strategy page as a zoomable `<figure>` using the
   existing `circuit-fig` / `circuit-img` pattern, meaningful alt text, and a
   caption linking to and crediting the Formula1.com/Pirelli article.
4. Confirm the build copies the file to `site/assets/`, the rendered image URL
   resolves locally, and the figure is visible on the generated tyres page.

If the article or information graphic is not yet published, keep that item
explicitly pending; do not substitute unrelated artwork or invent an asset.

### Enumerate every FIA decision document, not just the familiar categories

The FIA documents hub for a GP (the pattern already used as `FIA_EVENT_URL` in
the bespoke content modules) accumulates decision documents throughout the
week, and new categories appear without warning — do not assume the set is
limited to the Race Director's Competition Notes, Power Unit Information, Car
Display Procedure and Heat Hazard declaration types already covered by
earlier audits. Each run:

1. Fetch the event's documents hub page and extract every
   `.../decision-document/<slug>.pdf` link (`curl -s -A "Mozilla/5.0" <hub URL>
   | grep -oE 'href="[^"]*decision-document[^"]*"'`), or use `web-fetch` with
   `raw: true` if `curl` is unavailable in-sandbox.
2. Diff that list against saved discovery/media manifests and the source URLs,
   figures and interpreted content in the GP's module. Treat an unrepresented
   substantive page as a candidate gap even if the PDF is already linked.
   Same-URL PDF revisions also count. HTTP 403/500 is a retrieval failure, not
   evidence the FIA has not published anything. Use the normal season-index
   fallback and saved known public URLs; never guess filenames or bypass blocks.
3. Open each candidate. Skip pure administrative paperwork with no
   commentary-relevant content (e.g. competition visas; entry lists can matter
   for changed line-ups). Routine
   technical/compliance reports (e.g. a Technical Delegate's post-race
   compliance check carried over from the previous round) are worth a single
   concise line on the Penalties or Reliability page when genuinely new
   information, but do not force one in if there is nothing worth saying.
4. Render and include all substantive circuit/pit-lane/emergency/red-zone maps
   and technical/report pages. Diagrams cannot be skipped because text extraction
   is empty. `fia_media.py` and shared galleries automate these images, preserving
   revisions and avoiding already-curated page duplicates. Verify actual rendered
   output, legends and captions. Do not guess pit-box order or garage assignments.
5. Tyre-specific FIA "Competition Notes" documents (titled along the lines of
   "Competition Notes — Pirelli Preview") contain the official prescribed
   starting/stabilised pressures and camber limits per axle and per compound
   type (slicks/intermediates/wets), plus which compounds are the mandatory
   race tyres versus the Q3-only tyre. Add this to the Tyres & Strategy page
   alongside the Formula1.com/Pirelli graphic — it is a distinct, citable
   source even when the graphic is already present.

### Verify FIA PDF tables visually before transcribing numbers

FIA power-unit/energy-map and tyre-prescription documents pack several
tables with similarly-shaped numeric bands (megajoules, kilowatts, metres,
psi) into a dense one- or two-page layout. Plain-text PDF extraction can
silently reorder rows/columns relative to the visual table, which previously
caused a published error: qualifying's distinct (and unusually low) recharge
cap was merged into the wrong article's figures. Before writing any FIA
numeric table into a page:

1. Render the actual page as an image (`pip install pymupdf` if not already
   available — the `python` network entry already covers this — then
   `page.get_pixmap(matrix=pymupdf.Matrix(2,2), alpha=False).save("page.png")`
   with `import pymupdf`, or inspect the `fia_media.py` output)
   and view it, rather than trusting raw extracted text order.
2. Match every number to its row label (session/article) and column header
   exactly as they appear in the rendered image.
3. Actively look for a value that is notably different from the other
   sessions/rounds for the same parameter (for example, a session with a much
   lower recharge cap, or a sector with a materially different power-curve
   rule). When you find one, call it out explicitly as a "why this matters
   here" highlight on the relevant page rather than only listing it inside a
   flat bullet — that is usually the detail worth having ready on air. Keep
   any causal explanation you add clearly framed as informed inference
   (e.g. "the likely reason is..."), since the FIA documents state limits,
   not rationale.

## Editing rules

- Follow `SKILL.md` and existing content-module conventions.
- The pinned compiler permits at most 10 MiB per patch. If an automatic FIA
  screenshot backfill exceeds it, commit the verified discovery URLs, not a
  `fia_media.json` referring to uncommitted images; the normal deployment renders
  those public PDFs. Keep temporary screenshots for visual verification and do
  not duplicate media already committed on main. Report any remaining fetch block.
- Prefer a bespoke `content_<gp>.py` module when race-week material has outgrown
  the generic page. Register it in `build.py` when required.
- Keep curated prose concise and useful on air.
- Cite sources in the rendered content where the existing design supports it.
- Never invent an exact number, FIA parameter, quotation, result or forecast.
- Keep an explicit pending state when the authoritative source is not live.
- Do not edit generated `site/` or unrelated races.
- Do not change workflow files, dependencies, or the site engine.

## Validate

Run:

```bash
python3 -m py_compile build.py circuits.py standings.py content_generic.py content_*.py
python3 -m unittest discover -p 'test_*.py'
python3 build.py
python3 coverage_inventory.py --all --check
git diff --check
```

Then inspect every generated page for the selected GP. Confirm new facts are
visible, superseded placeholders are gone, all source links are valid, and all
17 pages still generate.

If nothing material is missing, emit `noop` with a concise coverage summary.
Otherwise create or update one draft pull request describing:

- the GP audited
- published gaps filled
- authoritative sources used
- information intentionally left pending
- blocked sources, conflicting values and inapplicable historical features
- feature-parity gaps checked and full-source screenshot/Pirelli artwork coverage
- validation performed
