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
      - "data/**/*.json"
      - "assets_src/**"
    protected-files: request_review
---

# Critical race coverage editor

Act as a skeptical Formula 1 commentary editor. Keep the current or next Grand
Prix as complete as published evidence allows. This is not an article-summary
task: inspect the whole information surface, identify what the regular scraper
and build have missed, and make the bounded repository improvements yourself.

## Avoid duplicate work

Use `gh pr list` to check for an open pull request whose title starts with
`[coverage]`. If one exists, emit `noop` explaining that the previous audit is
still awaiting review. Do not create competing coverage pull requests.

## Determine scope

1. Read `data/calendar_2026.json`, `build.py`, `circuits.py`,
   `content_generic.py`, the relevant `content_<gp>.py` when present, and the
   active GP's `data/<gp>/*_auto.json`.
2. Use the current UTC date and session dates to select:
   - a live race weekend, otherwise
   - the next race when it is within 10 days, otherwise
   - the most recently completed race for post-event corrections.
3. Run `python3 build.py` and inspect all 17 generated pages under
   `site/<gp>/`. Treat rendered output, not merely source files, as the coverage
   contract.

## Research critically

Search current material from Formula1.com, the FIA event documents, Pirelli,
The Race, and official team or driver announcements. Prefer primary sources.
Every factual addition must be traceable to a URL you actually opened.

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

For each surface classify the state mentally as populated, stale,
missing-but-published, genuinely-not-published, or conflicting. Improve all
material missing-but-published fields that can be handled in one coherent PR.
Correct stale facts tightly coupled to those additions.

### Required Pirelli tyre artwork

For the Tyres & Strategy surface, always look for the round-specific
Formula1.com article titled in the form **"What tyres will the teams and
drivers have for the YEAR GRAND PRIX?"**. The 2026 Italian Grand Prix example
is:

`https://www.formula1.com/en/latest/article/what-tyres-will-the-teams-and-drivers-have-for-the-2026-italian-grand-prix.7nOpWdCgvCBFDGlnODs0gk`

Open the rendered article and inspect the images inside the article body rather
than relying on page metadata or assuming the social/hero image is the useful
one. The graphic normally appears after the compound-allocation paragraphs and
its alt text or source filename follows a pattern such as
`<round>-<country><year>-preview-en.jpg`. For Monza 2026 the inline image is
`13-it26-preview-en.jpg` (served by `media.formula1.com` as
`13-it26-preview-en.webp`). Locate that complete Pirelli event-preview graphic,
which includes the circuit information, tyre demands, pressures and selected
compounds. When it is published:

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

## Editing rules

- Follow `SKILL.md` and existing content-module conventions.
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
python3 build.py
git diff --check
```

Then inspect every generated page for the selected GP. Confirm new facts are
visible, superseded placeholders are gone, all source links are valid, and all
17 pages still generate.

If nothing material is missing, emit `noop` with a concise coverage summary.
Otherwise create one draft pull request describing:

- the GP audited
- published gaps filled
- authoritative sources used
- information intentionally left pending
- validation performed
