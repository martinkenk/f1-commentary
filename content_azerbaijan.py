"""Reviewed Azerbaijan-specific preview coverage.

The public preview names the weekend's nominated compounds, but it does not
provide the post-qualifying new/used race-set inventory. Keep those two facts
separate on the Tyres page.
"""

import content_generic


PREVIEW_URL = (
    "https://www.formula1.com/en/latest/article/what-tyres-will-the-teams-and-"
    "drivers-have-for-the-2026-azerbaijan-grand-prix.1UFiasleBnLs9s0hyRCpS0"
)
PREVIEW_IMAGE = "azerbaijan_pirelli_tyres_2026.webp"

FIA_TYRES_URL = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_azerbaijan_grand_prix_-_competition_notes_-_pirelli_preview.pdf"
)
FIA_TYRES_ASSET = "fia-azerbaijan-4ba2e0fed786-be2a9031410066a5-p2.png"


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    pages["rookies"]["body"] = f"""
{content_generic.card(
    "The rookie rule",
    content_generic.ul([
        "Every team must field a rookie driver in <strong>two FP1 sessions per car</strong> across the "
        "season &mdash; four rookie outings per team in total.",
        "A 'rookie' is a driver who has started no more than two World Championship Grands Prix.",
        "Teams announce their choices in the days before the event; late changes do happen.",
    ]),
    "bi-person-badge",
)}

{content_generic.card(
    "Confirmed: Red Bull's first-choice line-up returns",
    "<p><strong>Isack Hadjar returns to the Red Bull cockpit for this Azerbaijan Grand Prix</strong>, "
    "having recovered from the fractured wrist he suffered in gym training over the summer break. "
    "He missed Zandvoort, Monza and Madrid while Liam Lawson stepped up from Racing Bulls into the "
    "vacant Red Bull seat, with Yuki Tsunoda covering Lawson's Racing Bulls cockpit during that "
    "spell.</p>"
    "<p>With Hadjar declared fit, <strong>Lawson returns to Racing Bulls and Tsunoda reverts to his "
    "reserve-driver role</strong>, restoring Red Bull/Racing Bulls' regular pairing for Baku.</p>",
    "bi-people",
    "accent",
)}

{content_generic.pending("Rookie FP1 line-ups for this round", "in the week before the event")}

<p class=\"src\">Sources: <a href=\"https://www.formula1.com/en/latest/article/hadjar-to-make-racing-return-with-red-bull-at-azerbaijan-gp.1ddPnUSDEze0V9MCiQ9d2U\" target=\"_blank\" rel=\"noopener\">Formula1.com &mdash; Hadjar to make racing return with Red Bull at Azerbaijan GP</a> and
<a href=\"https://www.the-race.com/formula-1/isack-hadjar-injury-return-where-every-red-bull-f1-driver-stands/\" target=\"_blank\" rel=\"noopener\">The Race &mdash; Where every Red Bull driver stands as Hadjar returns</a>, both 22 September 2026.</p>
"""
    pages["tyres"]["body"] = f"""
<div class="grid cols-2">
  {content_generic.card(
      "2026 nominated compounds",
      "<p><strong>C3 Hard · C4 Medium · C5 Soft</strong> are the compounds "
      "nominated for this Azerbaijan Grand Prix weekend &mdash; C3/C4/C5 are the "
      "mandatory race tyres, with C5 doubling as the Q3-only tyre.</p>"
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
  <img src="../assets/{PREVIEW_IMAGE}"
       alt="Pirelli 2026 Azerbaijan Grand Prix Baku preview infographic showing circuit information, "
            "tyre stress ratings and the C3/C4/C5 compound selection"
       class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen" loading="lazy">
  <figcaption><strong>Official Pirelli event preview</strong> &mdash; circuit information, tyre demands
  and the C3/C4/C5 compound selection. Source: <a href="{PREVIEW_URL}" target="_blank" rel="noopener">
  Formula1.com &mdash; "What tyres will the teams and drivers have for the 2026 Azerbaijan Grand Prix?"</a>,
  published 22 September 2026. <strong>Click to zoom / full screen.</strong></figcaption>
</figure>

<h2 class="sec">FIA tyre prescriptions (Document 1, Issue A)</h2>
<figure class="circuit-fig">
  <img src="../assets/{FIA_TYRES_ASSET}"
       alt="FIA Azerbaijan Competition Notes Pirelli Preview page with slick, intermediate and wet "
            "pressures, camber limits and heating times"
       class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen" loading="lazy">
  <figcaption><a href="{FIA_TYRES_URL}#page=2" target="_blank" rel="noopener">FIA Document 1, page 2</a>,
  issued 22 September 2026 at 11:40; prescription document version 5, Issue A.
  <strong>Click to zoom / full screen.</strong></figcaption>
</figure>
<div class="table-wrap"><table class="data">
  <thead><tr><th>Tyre</th><th>Axle</th><th class="num">Minimum start</th>
    <th class="num">Expected stabilised running</th><th class="num">Camber limit</th></tr></thead>
  <tbody>
    <tr><td>Slick</td><td>Front</td><td class="num">27.5 psi</td><td class="num">&ge;28.0 psi</td><td class="num">-3&deg;</td></tr>
    <tr><td>Slick</td><td>Rear</td><td class="num">27.5 psi</td><td class="num">&ge;28.0 psi</td><td class="num">-1.75&deg;</td></tr>
    <tr><td>Intermediate</td><td>Front</td><td class="num">28.5 psi</td><td class="num">&ge;29.0 psi</td><td class="num">-3.25&deg;</td></tr>
    <tr><td>Intermediate</td><td>Rear</td><td class="num">28.5 psi</td><td class="num">&ge;29.0 psi</td><td class="num">-2.25&deg;</td></tr>
    <tr><td>Wet</td><td>Front</td><td class="num">26.5 psi</td><td class="num">&ge;29.0 psi</td><td class="num">-3.25&deg;</td></tr>
    <tr><td>Wet</td><td>Rear</td><td class="num">26.0 psi</td><td class="num">&ge;29.0 psi</td><td class="num">-2.25&deg;</td></tr>
  </tbody>
</table></div>
<p>C3 and C4 are mandatory race tyres alongside C5; C5 is also the Q3-only tyre.
Maximum heating is <strong>two hours</strong>, up to <strong>70&deg;C</strong> for slicks and
<strong>40&deg;C</strong> for intermediates/wets — tyre-surface temperatures, not blanket-controller
settings. FIA/Pirelli may revise the prescriptions during the weekend.</p>

{content_generic.pending("Long-run degradation data", "after Friday practice",
                         "bi-graph-down")}
"""
    return pages
