"""Source-reviewed Sao Paulo Grand Prix content, refreshed after FP1."""
import content_generic
from f1lib import card
from upgrade_render import render_submissions

FIA = "https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_"
CAMARA = "https://www.formula1.com/en/latest/article/f2-racer-camara-to-make-f1-debut-at-sao-paulo-grand-prix-as-haas-confirm-ocon-will-not-return.12Qa0tpaMZ9kgnEuGJBKFp"
FP1_LINEUP = "https://www.formula1.com/en/latest/article/which-rookie-drivers-are-getting-fp1-outings-at-the-sao-paulo-grand-prix.3DAnL1BS38Gu5KKzU70aBJ"
FP1_REPORT = "https://www.formula1.com/en/latest/article/fp1-norris-leads-antonelli-and-verstappen-in-opening-sao-paulo-gp-practice-session.3GXL3rAROwHsLxnxn9hReY"
FP1_RESULT = "https://www.formula1.com/en/results/2026/races/1299/brazil/practice/1"
THE_RACE_FP1 = "https://www.the-race.com/formula-1/what-happened-in-brazil-fp1-f1-sao-paulo/"
STORYLINES = "https://www.formula1.com/en/latest/article/its-race-week-5-storylines-were-excited-about-ahead-of-the-2026-sao-paulo-grand-prix.6Pvk4v10hKccs7IS4X667x"
MCLAREN = "https://www.formula1.com/en/latest/article/want-to-believe-that-we-can-still-make-improvements-norris-wary-of-new-mclaren-upgrades-in-sao-paulo.6NvdXqDIqBz1Mw1xveJv0k"
FERRARI = "https://www.formula1.com/en/latest/article/hamilton-wants-ferrari-talks-ahead-of-sao-paulo-grand-prix-after-intra-team-battle-with-leclerc.3JXGpQWTdOA2a9PiH7NL8X"
RUSSELL_PENALTY = "https://www.the-race.com/formula-1/russell-serving-another-f1-engine-grid-penalty-in-brazil/"
RUSSELL_F1 = "https://www.formula1.com/en/latest/article/well-try-and-come-back-through-russell-set-for-grid-penalty-at-sao-paulo-grand-prix.6hsUcdvDTFFezGL53SAODZ"
FIA_EVENT = "https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2026-2072/event/S%C3%A3o%20Paulo%20Grand%20Prix"
FIA_UPGRADES_URL = FIA + "car_presentation_submissions.pdf"
FIA_UPGRADES_ASSET = "fia-brazil-d82872895e6d-eaf9202e01277f4e"
FIA_NEW_PU_URL = FIA + "new_pu_elements_for_this_competition.pdf"
FIA_NEW_PU_ASSET = "fia-brazil-46906038b849-b706ad97554d079c-p2"
RUSSELL_FIA_PENALTY = FIA + "infringement_-_car_63_-_changes_to_pu_element.pdf"
UPGRADE_SUBMISSIONS = (
    ("McLaren", 2, (
        ("Front Wing", "Performance - Flow Conditioning",
         "A new front-wing design aims to improve flow conditioning towards the floor and bodywork."),
        ("Rear Wing", "Performance - Local Load",
         "A new rear-wing assembly is designed to increase aerodynamic load efficiently in all conditions."),
        ("Beam Wing", "Performance - Flow Conditioning",
         "A new beam wing is intended to improve interaction and flow conditioning with the new rear wing."),
        ("Floor Furniture", "Performance - Flow Conditioning",
         "A small floor-furniture modification aims to improve flow conditioning and floor aerodynamic performance."),
    )),
    ("Mercedes", 4, ()),
    ("Red Bull", 5, ()),
    ("Ferrari", 6, ()),
    ("Williams", 7, ()),
    ("Racing Bulls", 8, ()),
    ("Aston Martin", 9, ()),
    ("Haas", 10, ()),
    ("Audi", 11, ()),
    ("Alpine", 12, ()),
    ("Cadillac", 13, ()),
)


def _figure(asset, title, document, page=2):
    return f"""<figure class="circuit-fig">
<img src="../assets/{asset}.png" alt="{title}" class="circuit-img" loading="lazy"
onclick="zoomImg(this)" title="Click to zoom / full screen">
<figcaption>{title}. <a href="{FIA}{document}.pdf#page={page}" target="_blank"
rel="noopener">FIA original, page {page}</a>. Click to zoom.</figcaption></figure>"""


def _lineup():
    return f"""
<h2 class="sec">Confirmed driver changes</h2>
<div class="grid cols-2">
{card("Six rookie stand-ins in FP1", f'''<p>Formula1.com's lineup and the
official classification show six drivers took the regular seats for Friday's
one-hour FP1:</p><ul><li><strong>McLaren:</strong> Leonardo Fornaroli for Oscar Piastri</li>
<li><strong>Ferrari:</strong> Dino Beganovic for Charles Leclerc</li>
<li><strong>Williams:</strong> Luke Browning for Carlos Sainz</li>
<li><strong>Audi:</strong> Freddie Slater for Nico Hulkenberg</li>
<li><strong>Alpine:</strong> Gabriele Mini for Pierre Gasly</li>
<li><strong>Cadillac:</strong> Colton Herta for Sergio Perez</li></ul>
<p>Herta completed the 100 km needed for his final Super Licence point during
FP1, as reported by The Race; Formula1.com explains the requirement. This
clears the point requirement but does not confirm a 2027 race seat.
<a href="{FP1_LINEUP}">Formula1.com lineup</a> ·
<a href="{FP1_RESULT}">official FP1 classification</a> ·
<a href="{FP1_REPORT}">Formula1.com FP1 report</a> ·
<a href="{THE_RACE_FP1}">The Race on Herta's milestone</a>.</p>''',
     "bi-person-badge", "accent")}
{card("Haas: Rafael Camara's race debut", f'''<p>Rafael Camara partners Oliver
Bearman for the <strong>whole Sao Paulo weekend</strong>, not merely FP1.
Haas says Esteban Ocon will not return to its race seat in 2026. Mexico stand-in
Ryo Hirakawa has World Endurance Championship commitments this weekend.
Camara's early promotion is confirmed for Brazil only; do not assume he will
contest the remaining 2026 races. <a href="{CAMARA}">Haas announcement via Formula1.com,
3 November</a>.</p>''', "bi-person-badge", "accent")}
</div>"""


def _teams():
    return f"""
<h2 class="sec">Team and grid storylines</h2>
<div class="grid cols-2">
{card("Mercedes: constructors' title still in play", f'''<p>Antonelli clinched
the Drivers' Championship in Mexico. The latest official standings still show
Mercedes leading Ferrari <strong>630–504 (126 points)</strong>. Formula1.com's
pre-weekend scenario says gaining three points on Ferrari in Brazil clinches
the constructors' title; practice awards no points, and the title is not yet
settled.
<a href="{STORYLINES}">Official title scenario</a>.</p>''', "bi-trophy", "accent")}
{card("Mercedes: Russell receives a five-place drop", f'''<p>FIA Document 14
reports a new ICE for Russell at the twentieth competition: it is his sixth
against four allowed and the Technical Delegate says it is not compliant with
Sporting Regulation B8.2.2(a). The Stewards' separate Document 15 now imposes
a five-place drop for the next race in which Russell participates. The
season-to-date usage report (Document 8) is not an event-specific parts
declaration or the penalty decision.
<a href="{FIA_NEW_PU_URL}">FIA Document 14</a> ·
<a href="{RUSSELL_FIA_PENALTY}">FIA Document 15</a> ·
<a href="{RUSSELL_F1}">Formula1.com report</a> ·
<a href="{RUSSELL_PENALTY}">The Race report</a>. The FIA filings do not
establish whether the planned ADUO specification is arriving.</p>''',
     "bi-exclamation-triangle")}
{card("Ferrari: Hamilton's Thursday comments", f'''<p>On Thursday 5 November,
Hamilton said face-to-face talks with Leclerc about their Mexico battle had
not yet taken place. That reports what he said then; it does not establish
whether they later spoke or whether team rules changed.
<a href="{FERRARI}">Formula1.com's 5 November report</a>.</p>''', "bi-people")}
{card("McLaren: four declared changes, gains unproven", f'''<p>FIA Document 12
lists four performance-motivated items: front wing, rear wing, beam wing and
floor furniture. The team's stated aims concern flow conditioning and local
aerodynamic load; these are design intentions, not measured gains. The Race
reports that the front-wing concept is intended to carry into McLaren's 2027
launch specification. <a href="{FIA_UPGRADES_URL}">FIA declaration</a> ·
<a href="https://www.the-race.com/formula-1/mclaren-2027-f1-front-wing-breaks-cover-in-brazil/">
The Race technical report</a>.</p>''', "bi-tools")}
</div>"""


def _tyres():
    rows = (
        ("Slick", "Front", "27.0", "≥28.0", "−3.00°"),
        ("Slick", "Rear", "26.5", "≥27.5", "−1.75°"),
        ("Intermediate", "Front", "28.0", "≥29.0", "−3.25°"),
        ("Intermediate", "Rear", "27.5", "≥28.5", "−2.25°"),
        ("Wet", "Front", "26.5", "≥29.0", "−3.25°"),
        ("Wet", "Rear", "25.5", "≥28.5", "−2.25°"),
    )
    table = "".join("<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>" for row in rows)
    return f"""
<h2 class="sec">FIA tyre prescriptions</h2>
<p>C3 Hard / C4 Medium / C5 Soft. Mandatory race specifications: <strong>C3/C4</strong>;
Q3 tyre: <strong>C5</strong>. These are nominations, not remaining race-set counts.
The initial weekend allocation is two hard, three medium and eight soft sets
per driver; post-qualifying availability must be sourced separately.</p>
<div class="table-wrap"><table class="data" id="brazil-tyre-limits">
<thead><tr><th>Type</th><th>Axle</th><th>Minimum start (psi)</th>
<th>Expected stabilized (psi)</th><th>Camber limit</th></tr></thead><tbody>{table}</tbody></table></div>
<p>Maximum heating: two hours, 70°C slick/intermediate and 40°C wet, measured
at tread and sidewall rather than the blanket controller. Cold-pressure curves:
front (T−70)×0.126+Pstart; rear (T−70)×0.125+Pstart. Check revisions after FP2.</p>
<p>Pirelli's full poster estimates <strong>22.5 seconds pit-stop loss</strong>.
Traction, braking, stress, abrasion, grip and lateral demand are all 3/5;
track evolution is 5/5. Resurfacing between Turns 3–5 and 8–9 makes Friday's
long runs important. Last year's effective two-stop race is historical context,
not a verified 2026 strategy window.</p>
{_figure("fia-brazil-8188298e7b47-84d11f15335e159e-p2",
         "Sao Paulo tyre prescriptions, version 5 issue A", "competition_notes_-_pirelli_preview")}
"""


def _powerunit():
    new_elements = (
        ("63", "Mercedes", "George Russell", "ICE", "5", "4",
         "Sixth used; not compliant with B8.2.2(a)"),
        ("51", "Haas Ferrari", "Rafael Câmara", "PU-ANC", "5", "6",
         "One of six allowed; compliant with B8.2.2(g)"),
    )
    new_elements_table = "".join(
        "<tr>" + "".join(f"<td>{value}</td>" for value in row) + "</tr>"
        for row in new_elements
    )
    usage_rows = (
        ("81", "Oscar Piastri", 4, 3, 3, 2, 3, 3, 5),
        ("01", "Lando Norris", 4, 3, 3, 2, 3, 4, 5),
        ("63", "George Russell", 5, 5, 5, 4, 4, 4, 5),
        ("12", "Kimi Antonelli", 5, 3, 3, 2, 4, 4, 6),
        ("03", "Max Verstappen", 4, 4, 4, 3, 3, 3, 5),
        ("06", "Isack Hadjar", 8, 7, 7, 4, 4, 4, 8),
        ("16", "Charles Leclerc", 4, 4, 4, 3, 3, 3, 6),
        ("44", "Lewis Hamilton", 4, 4, 4, 3, 3, 3, 6),
        ("23", "Alexander Albon", 5, 3, 3, 2, 3, 4, 5),
        ("55", "Carlos Sainz", 4, 4, 3, 2, 3, 4, 5),
        ("41", "Arvid Lindblad", 6, 5, 5, 2, 3, 3, 6),
        ("30", "Liam Lawson", 5, 5, 5, 2, 3, 3, 7),
        ("18", "Lance Stroll", 6, 7, 3, 5, 8, 7, 9),
        ("14", "Fernando Alonso", 5, 6, 3, 5, 7, 6, 9),
        ("50", "Ryo Hirakawa", 4, 4, 4, 3, 3, 3, 5),
        ("87", "Oliver Bearman", 4, 4, 4, 4, 4, 4, 4),
        ("27", "Nico Hulkenberg", 4, 4, 4, 3, 3, 3, 5),
        ("05", "Gabriel Bortoleto", 5, 5, 5, 4, 5, 5, 7),
        ("10", "Pierre Gasly", 4, 3, 3, 2, 3, 3, 5),
        ("43", "Franco Colapinto", 5, 3, 2, 2, 3, 4, 5),
        ("11", "Sergio Perez", 4, 4, 4, 3, 3, 3, 4),
        ("77", "Valtteri Bottas", 5, 5, 4, 4, 4, 4, 5),
    )
    usage_table = "".join(
        "<tr>" + "".join(f"<td>{value}</td>" for value in row) + "</tr>"
        for row in usage_rows
    )
    return f"""
<h2 class="sec">Brazil's new power-unit elements</h2>
<p>FIA Document 14, published at 16:33 CET on 6 November, lists Russell's
sixth ICE and Rafael Câmara's new PU-ANC. The Technical Delegate states that
Russell's ICE is not compliant with B8.2.2(a), while Câmara's PU-ANC is within
the six-element allowance under B8.2.2(g). This report is not the Stewards'
penalty decision. The Stewards' separate Document 15 imposes a five-place
drop for the next race in which Russell participates.
<a href="{RUSSELL_FIA_PENALTY}">Read Document 15</a>.</p>
<div class="table-wrap"><table class="data compact" id="brazil-new-pu-elements">
<thead><tr><th>No.</th><th>Constructor</th><th>Driver</th><th>New element</th>
<th>Previously used</th><th>Season allowance</th><th>Technical Delegate's report</th></tr></thead>
<tbody>{new_elements_table}</tbody></table></div>
{_figure(FIA_NEW_PU_ASSET, "FIA Document 14: Brazil new power-unit elements, page 2",
         "new_pu_elements_for_this_competition")}
<h2 class="sec">Season-to-date power-unit usage</h2>
<p>The FIA Technical Delegate's report dated <strong>6 November</strong> lists
the number of each element used by the 22 race-entered drivers so far this
season. It was retrieved at 14:30 UTC, before the scheduled 15:30 UTC start of
FP1, so it is a pre-running snapshot. These are usage totals, not a declaration
of which new parts are fitted for Brazil. Russell's five ICEs in that snapshot
are the parts used before the new sixth ICE listed in Document 14; the usage
report is not an event-specific new-parts declaration or a penalty decision.</p>
<div class="table-wrap"><table class="data compact" id="brazil-pu-usage">
<thead><tr><th>No.</th><th>Driver</th><th>ICE</th><th>TC</th><th>EXH</th>
<th>MGU-K</th><th>ES</th><th>PU-CE</th><th>PU-ANC</th></tr></thead>
<tbody>{usage_table}</tbody></table></div>
{_figure("fia-brazil-9c06be5d7cce-e6a9731048b45159-p2",
         "FIA season-to-date power-unit elements used report, 6 November",
         "pu_elements_used_per_driver_up_to_now")}
<h2 class="sec">Published Sao Paulo energy map</h2>
<div class="table-wrap"><table class="data" id="brazil-energy-limits">
<thead><tr><th>Session / condition</th><th>Maximum recharge per lap</th></tr></thead>
<tbody><tr><td>Race, Overtake inactive / active</td><td>8.0 / 8.5 MJ</td></tr>
<tr><td>Qualifying</td><td>6.5 MJ</td></tr>
<tr><td>Free practice</td><td>8.5 MJ</td></tr>
<tr><td>Out-laps outside the race</td><td>9.0 MJ</td></tr></tbody></table></div>
<p>Power-limited distance <strong>2278 m</strong>, reduction-rate limit
<strong>100 kW/s</strong>. Alt 1 applies at T6–T12 (2000–3150 m). Up to 350 kW
initial reduction is permitted at T6–T10 (2000–2700 m), T11–T12 (2900–3150 m)
and the bracketed exit T12 window (3200–4300 m). Reset windows are exit T11
(2900–3050 m) and bracketed exit T14 (3700–4300 m). Bracketed entries are
qualifying-only here: the generic FIA template also names Sprint Qualifying,
but this is a standard weekend. No higher-speed-threshold sector is listed.</p>
<p>Overtake detection gap <strong>1.0 s</strong>; detection <strong>3250 m (TBC),
L17</strong>, activation <strong>3411 m, L18</strong>. Keep the published TBC
qualification; do not convert it into a confirmed distance.</p>
{_figure("fia-brazil-70a86f7aabae-b034c0e63a20560d-p2",
         "Sao Paulo power-unit information and exceptions", "power_unit_information")}
"""


def _circuit():
    return f"""
<h2 class="sec">Two Straight Mode zones, one Overtake activation</h2>
<p>These are separate systems, not two 2026 DRS zones. The FIA map marks normal /
low-grip Straight Mode activation at <strong>A1: 40 m after T14 / 40 m before T15</strong>;
<strong>A2: 10 m / 60 m after T3 or pit exit</strong>. Overtake detection is
20 m after T12; activation 30 m after T13. The energy map's lap-distance
detection remains TBC.</p>
{_figure("fia-brazil-258e084acaf5-8c3658719ff72419-p2",
         "FIA Interlagos map with normal and low-grip Straight Mode zones",
         "competition_notes_-_circuit_map_pit_lane_drawing_emergency_exits_map_and_red_zone")}
<h2 class="sec">Race-control preparation</h2>
<p>The maximum SC2–SC1 time for qualifying/reconnaissance laps is to be
announced after FP2. The safety car waits before Turn 8 on resumption.
Deployment uses light panels and messages rather than waved yellow flags
or physical SC boards. An FP1 VSC test is planned after the final practice
start, until all cars return to the pits.</p>
<p>FIA circuit changes include resurfacing at T3–T5 and T8–T9; concrete
replacing grasscrete before T1/T4 and at T12 exit; new blue detection lines;
lower apex kerbs at T2/T8/T10; new debris fencing between T5–T6; adjusted
light-panel heights; and an asphalt patch at T3 exit.
<a href="{FIA}race_directors_competition_notes.pdf#page=8">Race Director's notes,
pages 2, 7–8</a>. The full source pages follow below.</p>
"""


def _upgrade_filing():
    return """
<div class="callout">
  <strong>FIA Document 12:</strong> McLaren lists four declared components;
  the other ten teams each submitted an explicit nil return. The filing states
  team rationales, not independently measured performance gains.
</div>
""" + render_submissions(
        UPGRADE_SUBMISSIONS, source_url=FIA_UPGRADES_URL,
        asset_prefix=FIA_UPGRADES_ASSET, document="FIA Document 12",
        event="Brazilian GP", issued="6 November 2026, 15:32 CET")


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    for slug in ("overview", "notes"):
        pages[slug]["body"] = _lineup() + _teams() + pages[slug]["body"]
    pages["rookies"]["body"] = _lineup() + pages["rookies"]["body"].replace(
        content_generic.pending("Rookie FP1 line-ups for this round", "in the week before the event"), ""
    ).replace(content_generic.pending(
        "Reserve or replacement driver changes", "as teams confirm them", "bi-people"), "")
    pages["teams"]["body"] = _lineup() + _teams()
    pages["tyres"]["body"] += _tyres()
    pending = content_generic.pending(
        "The FIA power-unit and energy-map document for this event",
        "with the event documents in the race week")
    if pending not in pages["powerunit"]["body"]:
        raise ValueError("Sao Paulo power-unit placeholder changed")
    pages["powerunit"]["body"] = pages["powerunit"]["body"].replace(pending, _powerunit()).replace(
        "for every individual event — that is where the numbers below come from once it is issued.",
        "for every individual event. Sao Paulo's published map is transcribed below.")
    pages["circuit"]["body"] += _circuit()
    pages["upgrades"]["body"] = _teams() + f"""
<h2 class="sec">Friday display and component submissions</h2>
<p>The FIA display is Friday <strong>11:00–12:00 BRT / 16:00–17:00 Tallinn</strong>.
If just one car has new major components, that is the car to display.
<a href="{FIA}car_display_procedure.pdf#page=2">Official procedure</a>.</p>
<p>The FIA's <strong>Car Display Procedure</strong> is separate from the
all-team <strong>Car Presentation Submissions</strong>. Document 12 was
published at 15:32 CET on 6 November, after the earlier 14:00 and 14:29 UTC
listing checks. Its team-by-team declarations and explicit nil returns are
transcribed below; the full substantive PDF pages, including McLaren's
location diagram, remain available in the expandable readers.</p>""" + _upgrade_filing()
    pages["schedule"]["body"] += f"""
<p><strong>Standard weekend, not Sprint:</strong> Friday FP1 12:30 and FP2 16:00;
Saturday FP3 11:30 and Qualifying 15:00; Sunday Race 14:00 (all BRT).
Add five hours for Tallinn (EET): race <strong>19:00 Sunday 8 November</strong>.
<a href="{FIA}timetable_v3.pdf">FIA timetable V3</a>. Session results,
long-run analysis and the race-set inventory cannot be populated before the
relevant sessions and source publications.</p>"""
    pages["moments"]["body"] = """
<h2 class="sec">Local winners and the circuit's evolution</h2>
<div class="grid cols-2">
""" + card("1973–74: Fittipaldi's home victories",
        "<p>Emerson Fittipaldi won the first two World Championship races at Interlagos.</p>",
        "bi-trophy") + card("1975: Carlos Pace wins at home",
        "<p>Another Sao Paulo driver, Carlos Pace, won in 1975. The circuit was named "
        "in his honour in 1985.</p>", "bi-trophy") + card("1990: the modern Interlagos",
        "<p>After the Brazilian race moved between Interlagos and Jacarepagua, "
        "Interlagos became its permanent home following shortening and resurfacing "
        "for 1990. Do not confuse all Brazilian GP editions with races at this venue.</p>",
        "bi-map") + """</div>
<p class="src">Source: <a href="https://www.formula1.com/en/latest/article/circuit-guide-everything-you-need-to-know-about-the-autodromo-jose-carlos-pace.409YTahcP9tBxfYEkjAeoD">
Formula1.com circuit guide, 5 November 2026</a>. See <a href="facts.html">Facts
and Records</a> for the source-backed pre-weekend driver, winner and constructor tables.</p>"""
    return pages
