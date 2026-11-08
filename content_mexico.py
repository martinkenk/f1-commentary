"""Source-reviewed Mexico City post-race team and commentary notes."""
import content_generic
from f1lib import card
from upgrade_render import render_submissions

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
FIA_CAR_PRESENTATION_ASSET = "fia-mexico-d1520eedea5a-b0abaa12d28b6685"
FIA_POWER_UNIT = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_mexico_city_grand_prix_-_power_unit_information.pdf"
)
FIA_PU_NEW_ELEMENTS = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_mexico_city_grand_prix_-_new_pu_elements_for_this_competition.pdf"
)
FIA_PU_NEW_ELEMENTS_ASSET = "fia-mexico-3f0fbf619a75-f196acf88eb5435b"
FIA_PU_USAGE = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_mexico_city_grand_prix_-_pu_elements_used_per_driver_up_to_now.pdf"
)
FIA_PU_USAGE_ASSET = "fia-mexico-c5ff79ffe336-b9eec32c5df1ef25"
FIA_BOTTAS_PU_PENALTY = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_mexico_city_grand_prix_-_infringement_-_car_77_-_pu_elements.pdf"
)
FIA_POWER_UNIT_ASSET = "fia-mexico-0ae7e9fb9e0e-dffe8a06feb5a324"
FIA_VERSTAPPEN_LAWSON_SUMMONS = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_mexico_city_grand_prix_-_summons_-_car_3_-_turn_14_incident_with_car_30.pdf"
)
FIA_LAWSON_VERSTAPPEN_SUMMONS = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_mexico_city_grand_prix_-_summons_-_car_30_-_turn_14_incident_with_car_3.pdf"
)
FIA_VERSTAPPEN_LAWSON_DECISION = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_mexico_city_grand_prix_-_infringement_-_car_3_-_turn_14_incident_with_car_30_.pdf"
)
FIA_LAWSON_VERSTAPPEN_DECISION = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_mexico_city_grand_prix_-_infringement_-_car_30_-_turn_14_incident_with_car_3_.pdf"
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

UPGRADE_SUBMISSIONS = (
    ("McLaren", 2, (
        ("Cooling Louvres", "Circuit specific - Cooling Range",
         "Extended forwards and reshaped to address Mexico's power-unit cooling challenges."),
    )),
    ("Mercedes", 4, ()),
    ("Red Bull", 5, (
        ("Engine Cover", "Reliability",
         "Larger cooling-exit louvres."),
        ("Sidepod", "Performance - Local Load",
         "Revised the sidepod and floor split line."),
    )),
    ("Ferrari", 7, (
        ("Engine Cover", "Circuit specific - Cooling Range",
         "Circuit-specific engine-cover cooling change."),
        ("Cooling Louvres", "Circuit specific - Cooling Range",
         "Circuit-specific cooling-louvre change."),
    )),
    ("Williams", 9, ()),
    ("Racing Bulls", 10, (
        ("Coke/Engine Cover", "Circuit specific - Cooling Range",
         "Circuit-specific coke/engine-cover cooling change."),
        ("Cooling Louvres", "Circuit specific - Cooling Range",
         "Circuit-specific cooling-louvre change."),
    )),
    ("Aston Martin", 12, ()),
    ("Haas", 13, ()),
    ("Audi", 14, (
        ("Rear Corner", "Performance - Local Load",
         "Updated rear brake-duct deflector."),
    )),
    ("Alpine", 16, (
        ("Exhaust Tailpipe", "Reliability",
         "Reprofiled tailpipe vane."),
    )),
    ("Cadillac", 18, ()),
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
  <li><strong>FP2 stewards:</strong> Docs 33–34 found that Max Verstappen and
  Liam Lawson made unnecessary, “clumsy” moves from the Turn 12 entry to the
  Turn 14 apex. Each received a one-place drop for the next race and one
  penalty point; their respective 12-month totals were one and four.
  Docs 23–24 were the summonses, not the penalties.
  <a href="{FIA_VERSTAPPEN_LAWSON_DECISION}">Doc 33</a> ·
  <a href="{FIA_LAWSON_VERSTAPPEN_DECISION}">Doc 34</a> ·
  <a href="{FIA_VERSTAPPEN_LAWSON_SUMMONS}">Doc 23</a> ·
  <a href="{FIA_LAWSON_VERSTAPPEN_SUMMONS}">Doc 24</a>.</li>
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


def _fia_figure(asset, alt, source, page):
    return f"""<figure class="circuit-fig">
  <img src="../assets/{asset}.png" alt="{alt}" class="circuit-img"
       loading="lazy" onclick="zoomImg(this)" title="Click to zoom / full screen">
  <figcaption>{alt}. <a href="{source}#page={page}" target="_blank"
       rel="noopener">Original FIA PDF, page {page}</a>. Click to zoom.</figcaption>
</figure>"""


def _power_unit_summary():
    readers = (
        ("mexico-power-unit-map", "Mexico City power-unit information", (
            _fia_figure(
                FIA_POWER_UNIT_ASSET + "-p2",
                "FIA Mexico City power and energy limits, sectors and Overtake lines",
                FIA_POWER_UNIT,
                2,
            ),
        )),
        ("mexico-new-pu-elements", "Mexico City new power-unit elements", (
            _fia_figure(
                FIA_PU_NEW_ELEMENTS_ASSET + "-p2",
                "Bottas new ICE, turbocharger and MGU-K report",
                FIA_PU_NEW_ELEMENTS,
                2,
            ),
            _fia_figure(
                FIA_PU_NEW_ELEMENTS_ASSET + "-p3",
                "Mexico City new energy-store and control-electronics report",
                FIA_PU_NEW_ELEMENTS,
                3,
            ),
        )),
        ("mexico-pu-usage", "Mexico City season-to-date power-unit usage", (
            _fia_figure(
                FIA_PU_USAGE_ASSET + "-p2",
                "FIA season-to-date power-unit element counts by driver",
                FIA_PU_USAGE,
                2,
            ),
        )),
    )
    controls = "".join(
        f'<p class="src"><a href="#{target}" data-document-reader '
        f'data-reader-title="{title}">Read {title}</a> · '
        f'<a href="{source}" target="_blank" rel="noopener">Original FIA PDF</a></p>'
        f'<details id="{target}"><summary>{title}</summary>{"".join(figures)}</details>'
        for target, title, figures, source in (
            (readers[0][0], readers[0][1], readers[0][2], FIA_POWER_UNIT),
            (readers[1][0], readers[1][1], readers[1][2], FIA_PU_NEW_ELEMENTS),
            (readers[2][0], readers[2][1], readers[2][2], FIA_PU_USAGE),
        )
    )
    return f"""
<h2 class="sec">Mexico City power and energy limits</h2>
<p>The FIA power-unit information sheet describes a <strong>4.304 km</strong> circuit. Maximum
recharge is <strong>8.5 MJ/lap</strong> in qualifying, <strong>9.0 MJ</strong>
in free practice and non-race out-laps, and <strong>8.5 / 9.0 MJ</strong> in
the race with Overtake inactive / active. The power-limited distance is
<strong>2,101 m</strong> at a <strong>100 kW/s</strong> reduction rate.</p>
<p>For Sprint and Race, the FIA labels the main Overtaking Zones
Base-Standard with Overtake inactive and Base-Overtake when active; other lap
sections use Alt 1. In practice, including qualifying, the sheet specifies
Base-Overtake. The separate Straight Mode markings are active-aero zones, not
electrical Overtake lines.</p>
<p>The alternative power curve applies at T4–T10 (2,000–2,900 m) and
T12–T16 (3,600–3,950 m). The 350 kW reduction exceptions cover T5–T6
(2,100–2,200 m), T7–T10 (2,550–2,900 m), and T12–T16 / Exit T16
(3,550–3,940 m and 3,950–4,300 m). A reset is permitted at Exit T17
(4,050–4,300 m); the T8–T9 higher-speed threshold is 250 km/h over
2,600–2,800 m. Overtake uses a 1.0 s detection gap, detection at 3,871 m
(L20), and activation at 4,051 m (L21 / SC1).</p>
<h2 class="sec">Power-unit elements and separate sanction</h2>
<p>The new-elements report lists Valtteri Bottas's fifth ICE and turbocharger,
and fourth MGU-K, energy store and control electronics; each exceeds its
season allowance in the FIA report. Stewards' Document 17 separately imposed
a 50-place drop for the next Race
(<a href="{FIA_BOTTAS_PU_PENALTY}" target="_blank" rel="noopener">original ruling</a>).
The usage snapshot and penalty are separate records; see the
<a href="penalties.html">Penalties page</a> for the ruling.</p>
<p class="src">Sources: FIA Power Unit Information, New Power Unit Elements,
Power Unit Elements Used and Stewards' Document 17. Distances and values above
are transcribed from the retained FIA screenshots; the complete source pages
and original PDFs follow.</p>
{controls}
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
            "All eleven FIA team declarations, stated rationales and explicit nil returns."
        )
        pages["upgrades"]["body"] = render_submissions(
            UPGRADE_SUBMISSIONS,
            source_url=FIA_CAR_PRESENTATION,
            asset_prefix=FIA_CAR_PRESENTATION_ASSET,
            document="Mexico City Grand Prix",
            event="Mexico City Grand Prix",
            issued="issue date not stated on the retained pages",
        )
        pages["powerunit"]["sub"] = (
            "FIA event energy limits, Overtake points and driver power-unit changes."
        )
        pages["powerunit"]["body"] = _power_unit_summary()
    return pages
