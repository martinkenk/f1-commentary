"""Source-reviewed Mexico City post-race team and commentary notes."""
import content_generic
from f1lib import card

F1 = "https://www.formula1.com/en"
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


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    if _is_post_race(ctx):
        pages["teams"]["sub"] = (
            "The title outcome, decisive team results and post-race stewarding."
        )
        pages["teams"]["body"] = _teams()
        pages["notes"]["sub"] = (
            "Final classification, championship outcome, tyre context and stewarding."
        )
        pages["notes"]["body"] = _notes()
    return pages
