"""Reviewed Azerbaijan-specific preview coverage.

The public preview names the weekend's nominated compounds, but it does not
provide the post-qualifying new/used race-set inventory. Keep those two facts
separate on the Tyres page.
"""

import content_generic
import f1lib


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
FIA_COMPLIANCE_URL = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_azerbaijan_grand_prix_-_post-race_checks_on_car_number_63_"
    "2026_spanish_gp.pdf"
)
FIA_POWER_UNIT_URL = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_azerbaijan_grand_prix_-_power_unit_information.pdf"
)


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    compliance_card = content_generic.card(
        "Madrid post-race compliance check cleared (FIA Document 2)",
        content_generic.ul([
            "Car 63 (George Russell, Mercedes) was randomly selected from "
            "the top ten after the Spanish Grand Prix for extended physical "
            "inspection of the front suspension assembly.",
            "The FIA checked the dampers, suspension fairings and geometry, "
            "uprights and wheel hubs, sensor identification and connections, "
            "data logging, sensor homologation and FIA-F1-DOC-001 submissions.",
            "All inspected items complied with the 2026 Formula One Technical "
            "Regulations. This is a routine report carried over from Madrid, "
            "not evidence of a Baku-specific reliability concern.",
        ]) + (
            f'<p class="src">Source: <a href="{FIA_COMPLIANCE_URL}" '
            'target="_blank" rel="noopener">FIA Document 2, Technical '
            "Delegate's Report</a>, issued 22 September 2026.</p>"
        ),
        "bi-clipboard-check",
        "accent",
    )
    pages["reliability"] = dict(
        kicker="Reliability & Pits",
        title="Reliability & Pit Stops",
        sub="Retirements, finisher counts and pit-stop rankings — filled in from the official results.",
        body=compliance_card + f1lib.auto_reliability(ctx),
    )
    powerunit = pages.get("powerunit")
    if powerunit:
        powerunit_pending = content_generic.pending(
            "The FIA power-unit and energy-map document for this event",
            "with the event documents in the race week",
        )
        powerunit_card = content_generic.card(
            "Azerbaijan energy map (FIA Document)",
            content_generic.ul([
                "Race recharge is <strong>8.5 MJ</strong> with Overtake inactive and "
                "<strong>9.0 MJ</strong> with Overtake active; qualifying and free "
                "practice are 8.5 MJ and 9.0 MJ respectively.",
                "The power-limited distance is <strong>3,796 m</strong> and the "
                "rate limit is <strong>50 kW/s</strong>.",
                "The Overtake detection line is at <strong>4,177 m</strong> "
                "(L20); the activation line is <strong>4,270 m</strong> "
                "(L21, TBC).",
            ])
            + (
                f'<p class="src">Source: <a href="{FIA_POWER_UNIT_URL}" '
                'target="_blank" rel="noopener">FIA power-unit information '
                "for the 2026 Azerbaijan Grand Prix</a>, page 2. "
                "The activation distance remains labelled TBC in the source.</p>"
            ),
            "bi-lightning-charge",
            "accent",
        )
        powerunit["body"] = powerunit["body"].replace(
            powerunit_pending,
            powerunit_card,
        )
    standings = pages.get("standings")
    if standings:
        standings["body"] += f"""
<h2 class="sec">Championship permutations</h2>
<p class="lead-note">Formula1.com's 22 September data-team analysis puts the
mathematics in context after Madrid; these are sourced scenarios, not a race
prediction.</p>
<div class="grid cols-2">
  {content_generic.card(
      "Who is still mathematically alive",
      "<p><strong>Antonelli leads Russell by 81 points and Hamilton by 101.</strong> "
      "Eight other drivers remain mathematically in contention: Russell, Hamilton, "
      "Lando Norris, Charles Leclerc, Max Verstappen, Oscar Piastri, Isack Hadjar "
      "and Liam Lawson.</p>"
      "<p>If Antonelli scores no more points and no rival exceeds his current 292, "
      "the earliest possible rival titles are São Paulo for Russell, Las Vegas for "
      "Hamilton, Norris and Leclerc, and Qatar for Verstappen and Piastri.</p>",
      "bi-trophy", "accent")}
  {content_generic.card(
      "Earliest Antonelli clinch scenarios",
      "<p>In the most aggressive scenario, Antonelli wins Azerbaijan, Bahrain and "
      "both Singapore Sprint and Grand Prix while Russell scores zero; that would "
      "clinch the title at Singapore (Round 17).</p>"
      "<p>Using each driver's season median finish instead, F1's data team puts "
      "the earliest projected clinch at Mexico (Round 19). These scenarios use "
      "the official scoring structure and are not guaranteed outcomes.</p>",
      "bi-calendar-check", "accent")}
</div>
<p class="src">Source: <a href="https://www.formula1.com/en/latest/article/points-permutations-when-is-the-earliest-antonelli-could-win-the-world-championship.24UKT2fsQl4GmC5DMrmYUy" target="_blank" rel="noopener">Formula1.com — POINTS PERMUTATIONS</a>, published 22 September 2026.</p>
"""
    pages["rookies"]["body"] = f"""
{content_generic.card(
    "Confirmed: Red Bull's first-choice line-up returns",
    "<p><strong>Isack Hadjar returns to the Red Bull cockpit for this Azerbaijan Grand Prix</strong> "
    "after recovering from the fractured wrist that kept him out of Zandvoort, Monza and Madrid. "
    "Liam Lawson returns to Racing Bulls and Yuki Tsunoda reverts to his reserve-driver role.</p>",
    "bi-people",
    "accent",
)}

{content_generic.pending("Rookie FP1 line-ups for this round", "in the week before the event")}

<p class="src">Sources: <a href="https://www.formula1.com/en/latest/article/hadjar-to-make-racing-return-with-red-bull-at-azerbaijan-gp.1ddPnUSDEze0V9MCiQ9d2U" target="_blank" rel="noopener">Formula1.com — Hadjar to make racing return with Red Bull at Azerbaijan GP</a> and
<a href="https://www.the-race.com/formula-1/isack-hadjar-injury-return-where-every-red-bull-f1-driver-stands/" target="_blank" rel="noopener">The Race — Where every Red Bull driver stands as Hadjar returns</a>, both 22 September 2026.</p>
"""
    pages["tyres"]["body"] = f"""
<div class="grid cols-2">
  {content_generic.card(
      "2026 nominated compounds",
      "<p><strong>C3 Hard · C4 Medium · C5 Soft</strong> are the compounds "
      "nominated for this Azerbaijan Grand Prix weekend &mdash; C3/C4/C5 are "
      "the mandatory race tyres, with C5 also the Q3-only tyre.</p>"
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
       alt="Pirelli 2026 Azerbaijan Grand Prix Baku preview infographic showing circuit information, tyre stress ratings and the C3/C4/C5 compound selection"
       class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen" loading="lazy">
  <figcaption><strong>Official Pirelli event preview</strong> &mdash; circuit information, tyre demands
  and the C3/C4/C5 compound selection. Source: <a href="{PREVIEW_URL}" target="_blank" rel="noopener">
  Formula1.com — "What tyres will the teams and drivers have for the 2026 Azerbaijan Grand Prix?"</a>,
  published 22 September 2026. <strong>Click to zoom / full screen.</strong></figcaption>
</figure>

<h2 class="sec">FIA tyre prescriptions (Document 1, Issue A)</h2>
<figure class="circuit-fig">
  <img src="../assets/{FIA_TYRES_ASSET}"
       alt="FIA Azerbaijan Pirelli preview page with slick, intermediate and wet pressures, camber limits and heating times"
       class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen" loading="lazy">
  <figcaption><a href="{FIA_TYRES_URL}#page=2" target="_blank" rel="noopener">FIA Document 1, page 2</a>,
  issued 22 September 2026; <strong>click to zoom / full screen.</strong></figcaption>
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
<p>C3 and C4 are mandatory race tyres alongside C5; maximum heating is <strong>two hours</strong>,
up to <strong>70&deg;C</strong> for slicks and <strong>40&deg;C</strong> for intermediates/wets.
FIA/Pirelli may revise the prescriptions during the weekend.</p>

{content_generic.pending("Long-run degradation data", "after Friday practice",
                         "bi-graph-down")}
"""
    return pages
