"""Reviewed Azerbaijan-specific preview coverage.

The public preview names the weekend's nominated compounds, but it does not
provide the post-qualifying new/used race-set inventory. Keep those two facts
separate on the Tyres page.
"""

import content_generic


PREVIEW_URL = "https://coffeecornermotorsport.com/azerbaijan-grand-prix-2026-tyre-preview/"
PREVIEW_IMAGE = (
    "https://coffeecornermotorsport.com/wp-content/uploads/2026/09/"
    "1920_15-az26-preview-en-1.webp"
)


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    pages["tyres"]["body"] = f"""
<div class="grid cols-2">
  {content_generic.card(
      "2026 nominated compounds",
      "<p><strong>C3 Hard · C4 Medium · C5 Soft</strong> are the compounds "
      "nominated for this Azerbaijan Grand Prix weekend.</p>"
      "<p>This is the published weekend nomination, not a count of each "
      "driver's remaining new or used sets.</p>",
      "bi-record-circle",
      "accent",
  )}
  {content_generic.card(
      "Race-set inventory",
      "<p>No verified post-qualifying race-set chart has been published or "
      "collected yet. The new/used set counts will be added only after a "
      "full event-matched chart is visually reviewed.</p>",
      "bi-hourglass-split",
  )}
</div>

<figure class="circuit-fig">
  <img src="{PREVIEW_IMAGE}"
       alt="Azerbaijan Grand Prix 2026 Pirelli tyre preview showing C3 Hard, C4 Medium and C5 Soft"
       class="circuit-img" loading="lazy">
  <figcaption><strong>Published tyre preview</strong> — the full graphic shows the
  C3/C4/C5 nomination and Baku tyre context. Secondary reproduction credited to
  Pirelli Motorsport by <a href="{PREVIEW_URL}" target="_blank" rel="noopener">
  Coffee Corner Motorsport</a>; it is not the remaining-set inventory.</figcaption>
</figure>

<p class="src">Source: <a href="{PREVIEW_URL}" target="_blank" rel="noopener">
Coffee Corner Motorsport — Azerbaijan Grand Prix 2026 Tyre Preview</a>,
published 22 September 2026. The source's 2025 comparison and strategy commentary
are retained as context only; no historical figures are used as 2026 inventory.</p>

{content_generic.pending("Long-run degradation data", "after Friday practice",
                         "bi-graph-down")}
"""
    return pages
