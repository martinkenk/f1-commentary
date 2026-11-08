"""Source-reviewed Mexico City post-race team and commentary notes."""
import content_generic
from f1lib import card

F1 = "https://www.formula1.com/en"
FP1_RESULT = F1 + "/results/2026/races/1298/mexico/practice/1"
RACE_RESULT = F1 + "/results/2026/races/1298/mexico/race-result"
DRIVER_STANDINGS = F1 + "/results/2026/drivers"
TEAM_STANDINGS = F1 + "/results/2026/team"
ANTONELLI = (
    F1 + "/latest/article/mexico-city-lowdown-all-the-key-moments-as-antonelli-"
    "secures-maiden-title-and-verstappen-denies-ferrari-victory.3mPqECWFPlJsdg4jUOZUXz"
)
VERSTAPPEN = (
    F1 + "/latest/article/verstappen-on-the-opportunistic-move-that-earned-him-"
    "fantastic-win-at-mexico-city-gp.5C4UF8HgiJdAGfZeXRBbpB"
)
LECLERC = (
    F1 + "/latest/article/leclerc-concedes-he-deserved-penalty-over-hamilton-"
    "clash-in-mexico-city-gp.4rYJb2xww8myo1gtgBV5pV"
)
PIASTRI = (
    F1 + "/latest/article/piastri-loses-p7-after-being-handed-post-race-penalty-"
    "at-mexico-city-gp.5dk3wHeak2yu7xWF0OhsRt"
)
ALPINE = (
    F1 + "/latest/article/alpines-gasly-and-colapinto-stripped-of-mexico-city-gp-"
    "points-after-post-race-penalties.2wLfobQHufuH1L1aMYPl7h"
)
PIRELLI = (
    "https://press.pirelli.com/the-champions-podium-verstappen-wins-in-mexico-"
    "as-kimi-secures-the-title/"
)
FIA_CAR_PRESENTATION = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_mexico_city_grand_prix_-_car_presentation_submissions.pdf"
)
FIA_POWER_UNIT = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_mexico_city_grand_prix_-_power_unit_information.pdf"
)
MOMENT_2019 = (
    F1 + "/latest/article/mexican-grand-prix-2019-report-and-highlights."
    "2GCUEuCYRquG0pcZeGZuYz"
)
MOMENT_2021 = (
    F1 + "/latest/article/verstappen-extends-championship-lead-after-jumping-"
    "both-mercedes-at-the.5MuxQBFZyfPdlnwaJDT0j0"
)
MOMENT_2024 = (
    F1 + "/latest/article/sainz-surges-to-mexico-victory-ahead-of-norris-and-"
    "leclerc-as-verstappen-hit.3duSNduH2cxC7K91WDSXda"
)


def _is_post_race(ctx):
    return ctx.get("status") == "past" and any(
        result.get("label") == "Race" for result in ctx.get("results", [])
    )


def _teams():
    return f"""
<h2 class="sec">Mexico City: team and title consequences</h2>
<div class="grid cols-2">
{card("Antonelli seals the Drivers' title", f'''<p>Kimi Antonelli finished
third and clinched the 2026 Drivers' Championship. At the post-race standings
snapshot he had 380 points, ahead of Max Verstappen on 261 and Lewis Hamilton
on 259. Mercedes leads Ferrari in the Constructors' standings, 630–504.
<a href="{ANTONELLI}">Formula1.com race lowdown</a> ·
<a href="{DRIVER_STANDINGS}">official Drivers' standings</a> ·
<a href="{TEAM_STANDINGS}">official Constructors' standings</a>.</p>''',
     "bi-trophy", "accent")}
{card("Verstappen wins from fifth", f'''<p>Max Verstappen took his sixth
Mexico City Grand Prix victory, finishing 0.799 seconds ahead of Hamilton.
The final classification gives Antonelli third and Leclerc fourth.
<a href="{VERSTAPPEN}">Verstappen on the race-winning move</a> ·
<a href="{RACE_RESULT}">official race classification</a>.</p>''', "bi-flag-fill")}
{card("Post-race penalties changed the order", f'''<p>Leclerc's five seconds
for leaving the track and gaining a lasting advantage left him fourth.
Piastri's ten-second collision penalty dropped him to 13th in the final
classification. Gasly received a stop-and-go for double yellows, while
Colapinto received ten seconds for failing to slow sufficiently under a
single yellow; both Alpines finished outside the points.
<a href="{LECLERC}">Leclerc on his penalty</a> ·
<a href="{PIASTRI}">Piastri decision report</a> ·
<a href="{ALPINE}">Alpine penalties</a> ·
<a href="{RACE_RESULT}">final classification</a>.</p>''',
     "bi-hammer")}
{card("The red flag reshaped tyre use", f'''<p>Pirelli reports Verstappen
changed from Medium to Soft on lap 27, then took another Soft under the red
flag. Antonelli ran his opening Soft stint to lap 43 before switching to
Medium, then also used Soft after the stoppage. Pirelli said a one-stop would
otherwise have been the most competitive option.
<a href="{PIRELLI}">Pirelli's race analysis</a>.</p>''',
     "bi-record-circle")}
</div>"""


def _notes():
    return f"""
<h2 class="sec">Race-weekend briefing — final facts</h2>
<div class="callout accent">
  <strong>Headline:</strong> Verstappen won the 71-lap race from fifth on the
  grid; Antonelli finished third and secured the Drivers' title. The final
  winning margin over Hamilton was 0.799 seconds.
</div>
<h3>On-air talking points</h3>
<ul>
  <li><strong>Title:</strong> Antonelli became champion with third place; use
  the current standings page for the post-race points snapshot.</li>
  <li><strong>Tyres:</strong> Pirelli says the red flag changed the actual
  stints. Do not describe the pre-race one-stop forecast as the strategy every
  driver followed.</li>
  <li><strong>Stewards:</strong> Leclerc's five seconds, Piastri's ten seconds,
  Gasly's stop-and-go and Colapinto's ten seconds are separate decisions with
  different incidents; the official final classification reflects them.</li>
  <li><strong>Classification:</strong> Ryo Hirakawa scored the final point in
  tenth for Haas; five entries are listed NC.</li>
</ul>
<p class="src">Sources: <a href="{ANTONELLI}">Formula1.com Mexico City race
lowdown</a> · <a href="{RACE_RESULT}">official final classification</a> ·
<a href="{PIRELLI}">Pirelli race analysis</a>. See <a href="results.html">Results</a>
for all sessions and <a href="penalties.html">Penalties</a> for the FIA rulings.</p>
"""


def _rookies():
    return f"""
<h2 class="sec">Mexico City FP1 substitutions</h2>
<p>Comparing the official FP1 and Race classifications by team identifies nine
temporary substitutions in first practice. The FP1 drivers below did not appear
in the Grand Prix classification:</p>
<div class="table-wrap"><table class="data">
<thead><tr><th>Team</th><th>FP1 driver</th><th>Race driver replaced</th></tr></thead>
<tbody>
<tr><td>Mercedes</td><td>Frederik Vesti</td><td>George Russell</td></tr>
<tr><td>Red Bull Racing</td><td>Ayumu Iwasa</td><td>Max Verstappen</td></tr>
<tr><td>Racing Bulls</td><td>Nikola Tsolov</td><td>Liam Lawson</td></tr>
<tr><td>Alpine</td><td>Gabriele Mini</td><td>Franco Colapinto</td></tr>
<tr><td>McLaren</td><td>Leonardo Fornaroli</td><td>Lando Norris</td></tr>
<tr><td>Aston Martin</td><td>Jak Crawford</td><td>Lance Stroll</td></tr>
<tr><td>Williams</td><td>Luke Browning</td><td>Alexander Albon</td></tr>
<tr><td>Audi</td><td>Freddie Slater</td><td>Gabriel Bortoleto</td></tr>
<tr><td>Cadillac</td><td>Colton Herta</td><td>Valtteri Bottas</td></tr>
</tbody></table></div>
<p class="src">Compared from the official Formula1.com
<a href="{FP1_RESULT}">FP1 classification</a> and
<a href="{RACE_RESULT}">Race classification</a>.</p>
"""


def _moments():
    return f"""
<h2 class="sec">Selected Mexico City Grand Prix moments</h2>
<p>These are race episodes at the Autódromo Hermanos Rodríguez, sourced to
Formula1.com's contemporary reports; they are not country-wide Mexican GP
statistics.</p>
<div class="grid cols-2">
{card("2019 — Hamilton's one-stop victory", f'''<p>Lewis Hamilton won from
third after making a 48-lap hard-tyre stint work, taking his second Mexico
victory and Mercedes' 100th win as a constructor.</p>
<p class="src"><a href="{MOMENT_2019}">Formula1.com race report, 27 October
2019</a>.</p>''', "bi-stopwatch", "accent")}
{card("2021 — Verstappen's Turn 1 move", f'''<p>Starting third, Max Verstappen
went around the outside of both Mercedes into Turn 1 and led on the opening
lap. He won ahead of Lewis Hamilton, with Sergio Pérez becoming the first
Mexican driver to take a Formula 1 podium at his home race.</p>
<p class="src"><a href="{MOMENT_2021}">Formula1.com race report, 7 November
2021</a>.</p>''', "bi-flag-fill")}
{card("2024 — Sainz retakes the lead", f'''<p>Carlos Sainz lost the lead to
Max Verstappen at the start, then reclaimed it on lap 9. He went on to win
by 4.705 seconds over Lando Norris; Verstappen's two time penalties shaped
the fight behind them.</p>
<p class="src"><a href="{MOMENT_2024}">Formula1.com race report, 27 October
2024</a>.</p>''', "bi-trophy")}
</div>"""


def _published_fia_note(document, url, detail):
    return f"""
<h2 class="sec">{document}</h2>
<div class="callout watch">
  <strong>Published source; event-specific interpretation pending.</strong>
  The FIA event files include {detail}. This page has not yet transcribed or
  independently verified the document's event-specific details; the absence
  of a summary here does not mean that no changes or data were published.
  <a href="{url}">Open the original FIA PDF</a>.
</div>
"""


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    pages["moments"]["sub"] = (
        "Three sourced race episodes from the Mexico City circuit."
    )
    pages["moments"]["body"] = _moments()
    if _is_post_race(ctx):
        pages["teams"]["sub"] = (
            "The title outcome, decisive team results and post-race stewarding."
        )
        pages["teams"]["body"] = _teams()
        pages["notes"]["sub"] = (
            "Final classification, championship outcome, tyre context and stewarding."
        )
        pages["notes"]["body"] = _notes()
        pages["rookies"]["sub"] = (
            "The nine FP1 substitutions confirmed by the official session classifications."
        )
        pages["rookies"]["body"] = (
            pages["rookies"]["body"]
            .replace(
                content_generic.pending(
                    "Rookie FP1 line-ups for this round",
                    "in the week before the event",
                ),
                "",
            )
            .replace(
                content_generic.pending(
                    "Reserve or replacement driver changes",
                    "as teams confirm them",
                    "bi-people",
                ),
                "",
            )
            + _rookies()
        )
        pages["upgrades"]["sub"] = (
            "The FIA submission is published; its team-by-team details still need review."
        )
        pages["upgrades"]["body"] = pages["upgrades"]["body"].replace(
            content_generic.pending(
                "FIA car presentation submissions for this round",
                "on the Friday of the race week",
            ),
            _published_fia_note(
                "Mexico City car presentation submissions",
                FIA_CAR_PRESENTATION,
                "the Car Presentation Submissions PDF",
            ),
        )
        pages["powerunit"]["sub"] = (
            "The FIA event document is published; its event-specific values are not transcribed."
        )
        pages["powerunit"]["body"] = pages["powerunit"]["body"].replace(
            content_generic.pending(
                "The FIA power-unit and energy-map document for this event",
                "with the event documents in the race week",
            ),
            _published_fia_note(
                "Mexico City power-unit information",
                FIA_POWER_UNIT,
                "the Power Unit Information PDF",
            ),
        )
    return pages
