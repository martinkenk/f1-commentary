"""Source-reviewed Sao Paulo Grand Prix content, refreshed during the weekend."""
import content_generic
from f1lib import card
from upgrade_render import render_submissions

FIA = "https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_"
FIA_ENTRY_LIST_URL = FIA + "entry_list.pdf"
FIA_FP2_DELETIONS_URL = FIA + "infringement_-_free_practice_2_deleted_lap_times.pdf"
FIA_CAMARA_REPRIMAND_URL = FIA + "infringement_-_car_51_-_unnecessarily_impeding_of_car_16.pdf"
FIA_SC2_SC1_URL = FIA + "race_director_notes_-_sc2_-_sc1_times.pdf"
FIA_NEW_PU_REV2_URL = FIA + "new_pu_elements_for_this_competition_0.pdf"
FIA_NEW_PU_REV2_DOC = "new_pu_elements_for_this_competition_0"
FIA_NEW_PU_REV2_P2_ASSET = "fia-brazil-af563bed0bcb-46cf930a47e6c2c0-p2"
FIA_NEW_PU_REV2_P3_ASSET = "fia-brazil-af563bed0bcb-46cf930a47e6c2c0-p3"
FIA_PEREZ_SUMMONS_URL = FIA + "summons_-_car_11_-_alleged_driving_in_an_unsafe_condition.pdf"
FIA_VERSTAPPEN_PENALTY_URL = FIA + "infringement_-_car_3_-_changes_to_pu_elements.pdf"
FIA_POST_QUALIFYING_URL = FIA + "post-qualifying_procedure.pdf"
CAMARA = "https://www.formula1.com/en/latest/article/f2-racer-camara-to-make-f1-debut-at-sao-paulo-grand-prix-as-haas-confirm-ocon-will-not-return.12Qa0tpaMZ9kgnEuGJBKFp"
FP1_LINEUP = "https://www.formula1.com/en/latest/article/which-rookie-drivers-are-getting-fp1-outings-at-the-sao-paulo-grand-prix.3DAnL1BS38Gu5KKzU70aBJ"
FP1_REPORT = "https://www.formula1.com/en/latest/article/fp1-norris-leads-antonelli-and-verstappen-in-opening-sao-paulo-gp-practice-session.3GXL3rAROwHsLxnxn9hReY"
FP3_REPORT = "https://www.formula1.com/en/latest/article/fp3-verstappen-fastest-from-antonelli-and-norris-ahead-of-sao-paulo-grand-prix.43ghT9dACzjrhxyjTBgKct"
FP1_RESULT = "https://www.formula1.com/en/results/2026/races/1299/brazil/practice/1"
THE_RACE_FP1 = "https://www.the-race.com/formula-1/what-happened-in-brazil-fp1-f1-sao-paulo/"
STORYLINES = "https://www.formula1.com/en/latest/article/its-race-week-5-storylines-were-excited-about-ahead-of-the-2026-sao-paulo-grand-prix.6Pvk4v10hKccs7IS4X667x"
MCLAREN = "https://www.formula1.com/en/latest/article/want-to-believe-that-we-can-still-make-improvements-norris-wary-of-new-mclaren-upgrades-in-sao-paulo.6NvdXqDIqBz1Mw1xveJv0k"
MCLAREN_UPDATE = "https://www.formula1.com/en/latest/article/we-seemed-to-gain-performance-norris-offers-update-on-mclarens-upgrades-in-sao-paulo.6fULeVhwADSsEp722opGBk"
RUSSELL_PENALTY = "https://www.the-race.com/formula-1/russell-serving-another-f1-engine-grid-penalty-in-brazil/"
RUSSELL_F1 = "https://www.formula1.com/en/latest/article/well-try-and-come-back-through-russell-set-for-grid-penalty-at-sao-paulo-grand-prix.6hsUcdvDTFFezGL53SAODZ"
HAMILTON_PENALTY = "https://www.the-race.com/formula-1/hamilton-set-for-brazil-grid-penalty-after-ferraris-worst-2026-friday/"
FIA_EVENT = "https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2026-2072/event/S%C3%A3o%20Paulo%20Grand%20Prix"
FIA_FP1_DOUBLE_YELLOW_URL = FIA + "infringement_-_free_practice_1_deleted_lap_times_-_double_yellow.pdf"
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
<p>The Race reports Herta picked up his final Super Licence point after FP1,
passing the 100 km running requirement when combined with his four other
qualifying FP1 outings and IndyCar results. Formula1.com explains the
requirement. This clears the point requirement but does not confirm a 2027 seat.
<a href="{FP1_LINEUP}">Formula1.com lineup</a> ·
<a href="{FP1_RESULT}">official FP1 classification</a> ·
<a href="{FP1_REPORT}">Formula1.com FP1 report</a> ·
<a href="{THE_RACE_FP1}">The Race on Herta's milestone</a> ·
<a href="{FIA_ENTRY_LIST_URL}">FIA Document 13 entry list</a>.</p>''',
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
{card("Power-unit changes reshape the grid", f'''<p>FIA Document 30 reports
new elements for Verstappen, both Ferraris, Perez and Russell. It records
Verstappen's fifth ICE, turbocharger and exhaust against four allowed, and a
sixth PU-ANC within the six-part allowance; both Ferrari drivers receive a
fifth ICE against four allowed. Perez's report lists a fifth ICE and turbo,
fourth MGU-K and fifth PU-ANC. Russell's new PU-ANC is sixth of six. These are
Technical Delegate counts, not all separate penalty rulings. Formula1.com
reported 10-place drops for Hamilton and Leclerc; the Stewards' later Document
33 imposed a 30-place drop on Verstappen for the fifth ICE, turbocharger and
exhaust. If Car 3 is classified in Qualifying, the decision specifies its
Race-grid allocation under Article B2.5.4.b.iv, superseding the earlier
back-of-grid report. Document 30 does not determine Perez's exact grid position.
Russell's separate five-place drop was imposed in Document 15. Check the
official grid before quoting any starting position.
<a href="{FIA_NEW_PU_REV2_URL}">FIA Document 30</a> ·
<a href="{FIA_VERSTAPPEN_PENALTY_URL}">FIA Document 33</a> ·
<a href="{HAMILTON_PENALTY}">Formula1.com penalty report</a> ·
<a href="{RUSSELL_FIA_PENALTY}">FIA Document 15</a>.</p>''',
     "bi-exclamation-triangle")}
{card("FP1/FP2: FIA lap-time deletions", f'''<p>Stewards'
Document 19 deletes the shown FP1 lap times for Franco Colapinto (2:05.129),
Alexander Albon (1:32.736), Luke Browning (1:33.848), Rafael Câmara (1:18.760)
and Dino Beganovic (OUT LAP) after their cars passed through a double-waved
yellow sector. This is a lap-time deletion, not a race penalty or a revised
FP1 classification. <a href="{FIA_FP1_DOUBLE_YELLOW_URL}">FIA Document 19</a>
(issued 6 November at 14:00 local).</p>
<p>Document 23 lists ten FP2 lap entries for nine drivers (Albon appears twice)
after cars did not use the track at Turns 1 and 4. The listed times are deleted;
the decision is not itself a revised FP2 classification or a race penalty.
<a href="{FIA_FP2_DELETIONS_URL}">FIA Document 23</a> ·
<a href="https://www.formula1.com/en/results/2026/races/1299/brazil/practice/2">
official FP2 classification</a>.</p>''', "bi-flag")}
{card("Stewards: Camara receives his first reprimand", f'''<p>FIA Document 25
resolves the Turn 15 summons involving Rafael Camara (Car 51) and Charles
Leclerc (Car 16). The Stewards found that Camara unnecessarily impeded Leclerc
in FP2 at 16:31; after warnings that Car 16 was on a fast lap, Car 51 moved
into the racing line and Leclerc had to take evasive action. The decision is a
driving reprimand, Camara's first of the season. It is not a grid drop or a
revised FP2 classification.
<a href="{FIA_CAMARA_REPRIMAND_URL}">FIA Document 25</a> ·
<a href="{FIA_EVENT}">FIA event documents</a>.</p>''', "bi-exclamation-triangle")}
{card("Perez summoned after FP3", f'''<p>FIA Document 31 summons Sergio Perez
(Car 11) and a Cadillac representative over the alleged unsafe condition of
Car 3 at 12:22 BRT. They were required to report to the Stewards at 13:00 BRT.
At the 16:05 UTC FIA-listing check, the Car 11 item remained the summons;
Document 33 is a separate power-unit decision for Car 3. No outcome for
Perez's summons was verified; check for a subsequent decision before describing
it. <a href="{FIA_PEREZ_SUMMONS_URL}">FIA Document 31</a> ·
<a href="{FIA_EVENT}">current FIA event listing</a>.</p>''', "bi-exclamation-triangle")}
{card("McLaren: four declared changes, early gain reported by Norris", f'''<p>FIA Document 12
lists four performance-motivated items: front wing, rear wing, beam wing and
floor furniture. The team's stated aims concern flow conditioning and local
aerodynamic load. After Friday practice, Norris said the package seemed to
gain performance; he topped FP1 and finished second in FP2. This is an early
driver assessment, not an independently measured race-long gain. The Race
reports that the front-wing concept is intended to carry into McLaren's 2027
launch specification. <a href="{FIA_UPGRADES_URL}">FIA declaration</a> ·
<a href="{MCLAREN_UPDATE}">Formula1.com: Norris on the upgrades</a> ·
<a href="https://www.the-race.com/formula-1/mclaren-2027-f1-front-wing-breaks-cover-in-brazil/">
The Race technical report</a>.</p>''', "bi-tools")}
</div>
<p><strong>Race control:</strong> FIA Race Director's Document 24 sets the
maximum interval below <strong>1:13.0</strong> between the Safety Car lines
during and after Qualifying, and on reconnaissance laps while the pit exit is
open for the Race. This is not a racing-lap maximum.
<a href="{FIA_SC2_SC1_URL}">FIA Document 24</a>.</p>"""


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
front (T−70)×0.126+Pstart; rear (T−70)×0.125+Pstart. The latest successful FIA
document discovery at 13:30 UTC contained no later Pirelli prescription.</p>
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
        ("03", "Red Bull Racing RB Ford", "Max Verstappen", "ICE", "4", "4",
         "Fifth of four; not compliant"),
        ("03", "Red Bull Racing RB Ford", "Max Verstappen", "TC", "4", "4",
         "Fifth of four; not compliant"),
        ("03", "Red Bull Racing RB Ford", "Max Verstappen", "EXH", "4", "4",
         "Fifth of four; not compliant"),
        ("03", "Red Bull Racing RB Ford", "Max Verstappen", "PU-ANC", "5", "6",
         "Sixth of six; within allowance"),
        ("16", "Ferrari", "Charles Leclerc", "ICE", "4", "4",
         "Fifth of four; not compliant"),
        ("44", "Ferrari", "Lewis Hamilton", "ICE", "4", "4",
         "Fifth of four; not compliant"),
        ("11", "Cadillac Ferrari", "Sergio Perez", "ICE", "4", "4",
         "Fifth of four; not compliant"),
        ("11", "Cadillac Ferrari", "Sergio Perez", "TC", "4", "4",
         "Fifth of four; not compliant"),
        ("11", "Cadillac Ferrari", "Sergio Perez", "MGU-K", "3", "3",
         "Fourth of three; not compliant"),
        ("11", "Cadillac Ferrari", "Sergio Perez", "PU-ANC", "4", "6",
         "Fifth of six; within allowance"),
        ("63", "Mercedes", "George Russell", "PU-ANC", "5", "6",
         "Sixth of six; within allowance"),
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
<h2 class="sec">Updated Brazil power-unit elements</h2>
<p>FIA Document 30 lists new components for five drivers for the remainder of
the competition. Its Technical Delegate identifies Verstappen's fifth ICE,
turbocharger and exhaust against four allowed; Leclerc and Hamilton's fifth
ICEs against four; and Perez's fifth ICE and turbocharger plus fourth MGU-K
against three. Each is stated as not compliant with the relevant allowance.
The same report says Verstappen's sixth PU-ANC, Perez's fifth and Russell's
sixth are within the six-part PU-ANC allowance. Component counts are not
Stewards' penalty decisions or a qualifying classification. Formula1.com
reports 10-place drops for Hamilton and Leclerc. The Stewards' later Document
33 imposes a 30-place drop on Verstappen for the fifth ICE, turbocharger and
exhaust. If Car 3 is classified in Qualifying, it specifies Race-grid
allocation under Article B2.5.4.b.iv; this supersedes the earlier
back-of-grid report. Document 30 does not determine Perez's exact position.
Russell's five-place drop is a separate Stewards' decision in Document 15.
<a href="{FIA_NEW_PU_REV2_URL}">FIA Document 30</a> ·
<a href="{FIA_VERSTAPPEN_PENALTY_URL}">FIA Document 33</a> ·
<a href="{HAMILTON_PENALTY}">Formula1.com on the grid penalties</a> ·
<a href="{RUSSELL_FIA_PENALTY}">FIA Document 15</a>.</p>
<div class="table-wrap"><table class="data compact" id="brazil-new-pu-elements">
<thead><tr><th>No.</th><th>Constructor</th><th>Driver</th><th>New element</th>
<th>Previously used</th><th>Season allowance</th><th>Technical Delegate's report</th></tr></thead>
<tbody>{new_elements_table}</tbody></table></div>
{_figure(FIA_NEW_PU_REV2_P2_ASSET,
         "FIA Document 30: new ICE, turbocharger and exhaust entries, page 2",
         FIA_NEW_PU_REV2_DOC, 2)}
{_figure(FIA_NEW_PU_REV2_P3_ASSET,
         "FIA Document 30: new MGU-K and PU-ANC entries, page 3",
         FIA_NEW_PU_REV2_DOC, 3)}
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
but this is a standard weekend. The revised sheet lists a higher-speed threshold
of <strong>240 km/h</strong> at T11 (2870–2970 m).</p>
<p>Document 28 sets the Overtake detection gap at <strong>1.0 s</strong>, with
detection at <strong>3250 m on timing loop L17</strong> and activation at
<strong>3411 m on L18</strong>. The revised sheet removes the earlier TBC on
the detection distance; metre positions and loop identifiers remain distinct.</p>
{_figure("fia-brazil-8181546ca72d-ac646baaf86f1a4c-p2",
         "FIA Document 28, revised Sao Paulo power-unit information, page 2",
         "power_unit_information_v2")}
<h2 class="sec">FP1 and FP2 technical checks</h2>
<p>FIA Technical Delegate Document 26 records checks before, during and after
Friday's sessions, including fuel-energy flow, energy-store state of charge,
ERS recharge limits, MGU-K limits, gear ratios and tyre monitoring. After FP2,
car 55 was weighed and rear-brake pressure control was checked on cars 63, 12,
16, 44, 30 and 43. Fuel and engine-oil samples from cars 43 and 23 were
analysed; the report says they were consistent with approved references and
that all listed items complied with the 2026 Technical Regulations.
<a href="{FIA}fp1_and_fp2_scrutineering.pdf#page=1">FIA Document 26, pages 1–4</a>.</p>
"""


def _circuit():
    return f"""
<h2 class="sec">Two Straight Mode zones, one Overtake activation</h2>
<p>These are separate systems, not two 2026 DRS zones. The FIA map marks normal /
low-grip Straight Mode activation at <strong>A1: 40 m after T14 / 40 m before T15</strong>;
<strong>A2: 10 m / 60 m after T3 or pit exit</strong>. Overtake detection is
20 m after T12; activation 30 m after T13. The revised Power Unit Information
(Document 28) gives the separate absolute references: detection at 3250 m on
timing loop L17 and activation at 3411 m on L18. Metres and loop identifiers
are not interchangeable.</p>
{_figure("fia-brazil-258e084acaf5-8c3658719ff72419-p2",
         "FIA Interlagos map with normal and low-grip Straight Mode zones",
         "competition_notes_-_circuit_map_pit_lane_drawing_emergency_exits_map_and_red_zone")}
<h2 class="sec">Race-control preparation</h2>
<p>FIA Race Director's Document 24, issued 6 November at 17:29, requires drivers
to stay below <strong>1:13.0</strong> between the Safety Car lines during and
after Qualifying, and on reconnaissance laps while the pit exit is open for the
Race. This is not a racing-lap maximum. The safety car waits before Turn 8 on
resumption.
Deployment uses light panels and messages rather than waved yellow flags
or physical SC boards.</p>
<p><a href="{FIA}race_directors_competition_notes.pdf">FIA Race Director's
Competition Notes, Document 6</a> ·
<a href="{FIA_SC2_SC1_URL}">Document 24</a> ·
<a href="https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2026-2072/event/S%C3%A3o%20Paulo%20Grand%20Prix">
current FIA event document listing</a>.</p>
<p>FIA circuit changes include resurfacing at T3–T5 and T8–T9; concrete
replacing grasscrete before T1/T4 and at T12 exit; new blue detection lines;
lower apex kerbs at T2/T8/T10; new debris fencing between T5–T6; adjusted
light-panel heights; and an asphalt patch at T3 exit.
<a href="{FIA}race_directors_competition_notes.pdf#page=8">Race Director's notes,
pages 2, 7–8</a>. The full source pages follow below.</p>
<p><strong>Race Director's Competition Notes V2, 7 November:</strong> cars not
performing a practice start must leave the Pit Exit Road at the earliest
opportunity, join the normal racing line and not cross back into the Pit Exit
Road. During race reconnaissance laps, drivers may cross the separating white
line only when leaving the pit lane without performing a practice start.
Overtaking on the Pit Exit Road is prohibited during Qualifying unless a car
slows with an obvious problem. These revised instructions are distinct from
the below-1:13.0 Safety Car-line limit above.
<a href="{FIA}race_directors_competition_notes_v2.pdf#page=5">FIA Competition
Notes V2, page 5</a> ·
<a href="{FIA}race_directors_competition_notes_v2.pdf#page=6">page 6</a>.</p>
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
    notes_pending = content_generic.pending(
        "Session-by-session commentary notes", "as the weekend runs", "bi-mic"
    )
    if notes_pending not in pages["notes"]["body"]:
        raise ValueError("Sao Paulo session-notes placeholder changed")
    pages["notes"]["body"] = pages["notes"]["body"].replace(
        notes_pending,
        "<p><strong>Session-by-session status:</strong> FP1, FP2 and FP3 "
        "classifications have been published. The latest official result appears "
        "in <a href=\"results.html\">Results</a>; <a href=\"news.html\">Weekend "
        "News</a> carries session reports and official updates. Recheck after "
        "each session for new material.</p>",
    )
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
<p>The FIA display window was Friday <strong>11:00–12:00 BRT /
16:00–17:00 Tallinn</strong>; it has passed. The procedure says that if just
one car has new major components, that is the car to display.
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
<a href="{FIA}timetable_v3.pdf">FIA timetable V3</a>. The FP1, FP2 and FP3
classifications are published; qualifying and race results await those sessions.
Long-run analysis depends on available timing data, and race-set counts require
a published inventory chart.</p>
<p><strong>Curfew report, 7 November:</strong> FIA Technical Delegate
Document 27 says Oracle Red Bull Racing and Aston Martin personnel were inside
the circuit during the 11.5-hour pre-FP3 curfew, from 21:00 Friday to 08:30
Saturday BRT. This was Oracle Red Bull Racing's second and Aston Martin's third
of four permitted team exceptions; the report says no action should be taken.
<a href="{FIA}curfew_0.pdf">FIA Document 27</a>.</p>"""
    pages["schedule"]["body"] += f"""
<p><strong>FIA Document 29 — Post-Qualifying Procedure:</strong> the FIA event
listing records this publication on 7 November. A direct PDF request returned
HTTP 403 during this review, so its contents have not been verified or
transcribed. This is an access limitation, not evidence that no procedure was
published. <a href="{FIA_POST_QUALIFYING_URL}">FIA Document 29</a> ·
<a href="{FIA_EVENT}">complete event listing</a>.</p>"""
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
