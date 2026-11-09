"""Source-reviewed Sao Paulo Grand Prix content, refreshed during the weekend."""
import content_generic
import career_starts
from f1lib import card, render_penalties
from upgrade_render import render_submissions

FIA = "https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_"
FIA_ENTRY_LIST_URL = FIA + "entry_list.pdf"
FIA_FP2_DELETIONS_URL = FIA + "infringement_-_free_practice_2_deleted_lap_times.pdf"
FIA_FP3_DELETIONS_URL = FIA + "infringement_-_free_practice_3_deleted_lap_times.pdf"
FIA_BEARMAN_UNSAFE_RELEASE_URL = FIA + "infringement_-_car_87_-_unsafe_release.pdf"
FIA_LECLERC_COLLISION_URL = FIA + "infringement_-_car_16_-_causing_a_collision.pdf"
FIA_ANTONELLI_UNSAFE_RELEASE_URL = FIA + "infringement_-_car_12_-_unsafe_release.pdf"
FIA_RACE_SCRUTINEERING_URL = FIA + "race_scrutineering.pdf"
FIA_CAMARA_REPRIMAND_URL = FIA + "infringement_-_car_51_-_unnecessarily_impeding_of_car_16.pdf"
FIA_SC2_SC1_URL = FIA + "race_director_notes_-_sc2_-_sc1_times.pdf"
FIA_NEW_PU_REV2_URL = FIA + "new_pu_elements_for_this_competition_0.pdf"
FIA_NEW_PU_REV2_DOC = "new_pu_elements_for_this_competition_0"
FIA_NEW_PU_REV2_P2_ASSET = "fia-brazil-af563bed0bcb-46cf930a47e6c2c0-p2"
FIA_NEW_PU_REV2_P3_ASSET = "fia-brazil-af563bed0bcb-46cf930a47e6c2c0-p3"
FIA_NEW_PU_REV3_URL = FIA + "new_pu_elements_for_this_competition_2.pdf"
FIA_NEW_PU_REV3_DOC = "new_pu_elements_for_this_competition_2"
FIA_NEW_PU_REV3_P2_ASSET = "fia-brazil-a3dc392ee3d3-5c2a48565dbe63dd-p2"
FIA_NEW_PU_REV3_P3_ASSET = "fia-brazil-a3dc392ee3d3-5c2a48565dbe63dd-p3"
FIA_PEREZ_SUMMONS_URL = FIA + "summons_-_car_11_-_alleged_driving_in_an_unsafe_condition.pdf"
FIA_PEREZ_PU_PENALTY_URL = FIA + "infringement_-_car_11_-_changes_to_pu_elements.pdf"
FIA_BORTOLETO_PU_PENALTY_URL = FIA + "infringement_-_car_5_-_changes_to_pu_elements.pdf"
FIA_LINDBLAD_PU_PENALTY_URL = FIA + "infringement_-_car_41_-_changes_to_pu_elements.pdf"
FIA_FINAL_STARTING_GRID_URL = FIA + "final_starting_grid.pdf"
FIA_FINAL_RACE_CLASSIFICATION_URL = FIA + "final_race_classification.pdf"
FIA_CHAMPIONSHIP_POINTS_URL = FIA + "championship_points.pdf"
F1_RACE_RESULTS = "https://www.formula1.com/en/results/2026/races/1299/brazil/race-result"
F1_RACE_REPORT = (
    "https://www.formula1.com/en/latest/article/"
    "norris-beats-verstappen-in-wet-sao-paulo-gp-thriller-as-mercedes-win-"
    "constructors-championship.7JN7MXLZf5lk5l0C3gfKGI"
)
FIA_PARC_FERME_PARTS_URL = (
    FIA + "parts_and_parameters_been_replaced_and_or_changed_during_parc_ferme.pdf"
)
FIA_PARC_FERME_PARTS_DOC = "parts_and_parameters_been_replaced_and_or_changed_during_parc_ferme"
FIA_PEREZ_UNSAFE_URL = FIA + "infringement_-_car_11_-_driving_in_an_unsafe_condition.pdf"
FIA_VERSTAPPEN_PENALTY_URL = FIA + "infringement_-_car_3_-_changes_to_pu_elements.pdf"
FIA_LECLERC_PENALTY_URL = FIA + "infringement_-_car_16_-_changes_to_pu_element.pdf"
FIA_HAMILTON_PENALTY_URL = FIA + "infringement_-_car_44_-_changes_to_pu_element.pdf"
FIA_HAMILTON_NEW_PU_URL = FIA + "new_pu_elements_for_this_competition_1.pdf"
FIA_HAMILTON_ADDITIONAL_PENALTY_URL = FIA + "infringement_-_car_44_-_additional_changes_to_pu_elements.pdf"
FIA_GARAGE_DOORS_URL = FIA + "garage_doors.pdf"
FIA_POST_QUALIFYING_URL = FIA + "post-qualifying_procedure.pdf"
FIA_PRE_RACE_URL = FIA + "pre-race_procedure.pdf"
FIA_POST_RACE_URL = FIA + "post-race_procedure.pdf"
FIA_BEARMAN_REVERSAL_URL = FIA + "infringement_-_car_87_-_reversing_in_the_pit_lane.pdf"
FIA_QUALIFYING_DELETIONS_URL = FIA + "infringement_-_qualifying_deleted_lap_times.pdf"
FIA_STROLL_DOUBLE_YELLOW_URL = FIA + "infringement_-_qualifying_deleted_lap_times_-_double_yellow.pdf"
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
F1_PU_PENALTIES = "https://www.formula1.com/en/latest/article/hamilton-leclerc-and-verstappen-set-for-sao-paulo-grand-prix-penalties-after-power-unit-changes.7B5CuFFCN1F6Txc8YwcEhd"
HAMILTON_F1_UPDATE = "https://www.formula1.com/en/latest/article/hamilton-set-to-start-at-back-of-the-grid-after-further-penalty-ahead-of-sao-paulo-grand-prix.5SFs44M6cNSDvUBCWE9FWZ"
FIA_EVENT = "https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2026-2072/event/S%C3%A3o%20Paulo%20Grand%20Prix"
THE_RACE_QUALIFYING = "https://www.the-race.com/formula-1/brazilian-gp-qualifying-red-flagged-almost-immediately-due-to-rain/"
F1_QUALIFYING_RESULTS = "https://www.formula1.com/en/results/2026/races/1299/brazil/qualifying"
F1_STARTING_GRID = "https://www.formula1.com/en/results/2026/races/1299/brazil/starting-grid"
THE_RACE_PROVISIONAL_GRID = "https://www.the-race.com/formula-1/f1-2026-brazilian-grand-prix-starting-grid-with-four-penalties-copy/"
PIRELLI_FP2_STRATEGY = "https://press.pirelli.com/soft-delivers-at-interlagos-as-antonelli-sets-the-pace/"
PIRELLI_POST_QUALI_STRATEGY = "https://press.pirelli.com/from-full-wets-to-inters-in-qualifying-norris-takes-pole-in-so-paulo/"
PIRELLI_RACE_REPORT = "https://press.pirelli.com/from-pole-to-victory-norris-triumphs-in-so-paulo-on-intermediates/"
PIRELLI_RACE_STINTS_IMAGE = "https://content.presspage.com/uploads/2363/af8b70c7-f963-4389-889f-011824967ebd/1920_20-br26-race2-en.jpg?10000"
PIRELLI_RACE_PIT_STOPS_IMAGE = "https://content.presspage.com/uploads/2363/5305ca7b-8ad4-404c-939a-8c2123fc0990/1920_20-br26-pitstop-en.jpg?10000"
CCM_BRAZIL_STRATEGY = "https://coffeecornermotorsport.com/brazil-grand-prix-2026-tyre-strategy/"
BRAZIL_STRATEGY_IMAGE = (
    "https://coffeecornermotorsport.com/wp-content/uploads/2026/11/"
    "Brazil_2026_Expected_Pit_Stop_Strategies_CCM_CORRECTED.webp"
)
BRAZIL_STRATEGY_ASSET = "brazil-tyre-strategy-2026.webp"
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


def _strategy_figure():
    return f"""<figure class="circuit-fig">
<img src="../assets/{BRAZIL_STRATEGY_ASSET}"
alt="Four illustrative 71-lap São Paulo tyre strategies with pit windows: Soft–Medium–Soft on laps 17–23 and 42–48; Medium–Hard–Soft on 23–29 and 50–56; Soft–Hard–Soft on 16–22 and 44–50; Medium–Hard one-stop on 28–34."
class="circuit-img tyre-preview-img" loading="lazy" role="button" tabindex="0"
onclick="zoomImg(this)" onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();zoomImg(this)}}"
title="Click to zoom / full screen">
<figcaption>Four pre-race 71-lap strategy options. <a href="{CCM_BRAZIL_STRATEGY}"
target="_blank" rel="noopener">Coffee Corner Motorsport's full article</a>;
strategy data credited to Pirelli Motorsport. Secondary reproduction. Click to zoom.</figcaption></figure>"""


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
{card("Mercedes clinches constructors' title in Sao Paulo", f'''<p>Formula1.com
reports Mercedes secured the 2026 Constructors' Championship in Brazil.
Antonelli had already clinched the Drivers' title in Mexico. The linked
standings page carries the current official championship totals; the
pre-race three-point scenario is now settled.
<a href="{F1_RACE_REPORT}">Formula1.com race report</a> ·
<a href="https://www.formula1.com/en/results/2026/team">official
Constructors' standings</a>.</p>''', "bi-trophy", "accent")}
{card("Power-unit penalties shaped Brazil's starting order", f'''<p>FIA Document 30 reports
new elements for Verstappen, both Ferraris, Perez and Russell. It records
Verstappen's fifth ICE, turbocharger and exhaust against four allowed, and a
sixth PU-ANC within the six-part allowance; both Ferrari drivers receive a
fifth ICE against four allowed. Perez's report lists a fifth ICE and turbo,
fourth MGU-K and fifth PU-ANC. Russell's new PU-ANC is sixth of six. These are
Technical Delegate counts, not all separate penalty rulings. The
<a href="{FIA}pu_elements_used_per_driver_up_to_now.pdf">season-to-date usage
report (Document 8)</a> is a separate earlier snapshot, not an event-specific
parts declaration. The FIA filings do not establish whether the planned ADUO
specification is arriving. Formula1.com
reported 10-place drops for Hamilton and Leclerc; the Stewards' later Document
33 imposed a 30-place drop on Verstappen for the fifth ICE, turbocharger and
exhaust. Verstappen qualified 16th and the official Starting Grid placed him
21st. A separate Document 39 imposes a 30-place drop on Perez for his fifth
ICE, fifth turbocharger and fourth MGU-K; Perez qualified 21st and the official
Starting Grid placed him 22nd.
Document 30's fifth PU-ANC for Perez is within that element's allowance.
Stewards' Documents 35 and 37 impose 10-place drops for Leclerc (Car 16) and
Hamilton (Car 44), respectively, for their fifth ICEs. FIA Document 42 then
lists Hamilton's sixth ICE, fifth turbocharger and exhaust, fourth energy store,
fourth control electronics unit and MGU-K, and seventh PU-ANC. Document 43
imposes a further 65-place drop for those changes, in addition to Document
37's 10 places, a cumulative 75-place penalty. Car 44 qualified 11th and the
official Starting Grid placed Hamilton 20th.
The Race's provisional order lists
Hamilton 20th; the official Formula1.com Starting Grid now also lists him 20th.
Use that published classification rather than the earlier provisional order.
This later FIA filing supersedes the earlier team statement that Hamilton
would start from the back without specifying component counts. Russell's
separate five-place drop followed his sixth ICE (sixth against four allowed)
in Document 15.
The Technical Delegate's later Document 55 reports Lindblad's seventh ICE and
sixth turbocharger (four allowed each), plus Bortoleto's sixth energy store and
sixth PU-CE (three allowed each); it states all four are not compliant. This is
a component report, not a Stewards' penalty decision. Separate Stewards'
Documents 56 and 57 impose 10-place drops for Lindblad (seventh ICE, sixth TC)
and Bortoleto (sixth ES, sixth PU-CE).
<a href="{FIA_NEW_PU_REV2_URL}">FIA Document 30</a> ·
<a href="{FIA_NEW_PU_REV3_URL}">FIA Document 55</a> ·
<a href="{FIA_LINDBLAD_PU_PENALTY_URL}">FIA Document 56</a> ·
<a href="{FIA_BORTOLETO_PU_PENALTY_URL}">FIA Document 57</a> ·
<a href="{FIA_NEW_PU_URL}">previous new-elements report, Document 14</a> ·
<a href="{FIA_VERSTAPPEN_PENALTY_URL}">FIA Document 33</a> ·
<a href="{FIA_PEREZ_PU_PENALTY_URL}">FIA Document 39</a> ·
<a href="{FIA_LECLERC_PENALTY_URL}">FIA Document 35</a> ·
<a href="{FIA_HAMILTON_PENALTY_URL}">FIA Document 37</a> ·
<a href="{FIA_HAMILTON_NEW_PU_URL}">FIA Document 42</a> ·
<a href="{FIA_HAMILTON_ADDITIONAL_PENALTY_URL}">FIA Document 43</a> ·
<a href="{F1_PU_PENALTIES}">Formula1.com on the penalties</a> ·
<a href="{HAMILTON_F1_UPDATE}">Formula1.com on Hamilton's later replacement</a> ·
<a href="{HAMILTON_PENALTY}">The Race on Hamilton's penalty</a> ·
<a href="{THE_RACE_PROVISIONAL_GRID}">The Race's provisional post-penalty order</a> ·
<a href="{F1_STARTING_GRID}">Formula1.com final Starting Grid</a> ·
<a href="{RUSSELL_FIA_PENALTY}">FIA Document 15</a> ·
<a href="{RUSSELL_PENALTY}">The Race report on Russell</a>.</p>''',
     "bi-exclamation-triangle")}
{card("FIA practice lap-time deletions", f'''<p>Stewards'
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
official FP2 classification</a>.</p>
<p>FIA Document 36 also deletes two listed FP3 lap times after the cars did
not use the track at Turns 1 and 4: Rafael Camara (Car 51), 1:34.799 at
11:35:37, and Max Verstappen (Car 3), 1:52.648 at 11:57:43. This ruling
deletes those entries; it is not itself a revised FP3 classification.
<a href="{FIA_FP3_DELETIONS_URL}">FIA Document 36</a>.</p>
<p>FIA Document 44 lists eight deleted Qualifying lap-time entries affecting
Rafael Câmara, Gabriel Bortoleto, Lance Stroll, Carlos Sainz, Oliver Bearman
and Sergio Perez. Document 46 separately deletes Stroll's 1:42.680 lap for a
double-waved-yellow sector. These are lap-time decisions, not additional grid
penalties or replacements for the official qualifying classification.
<a href="{FIA_QUALIFYING_DELETIONS_URL}">FIA Document 44</a> ·
<a href="{FIA_STROLL_DOUBLE_YELLOW_URL}">FIA Document 46</a>.</p>''', "bi-flag")}
{card("Stewards: Camara receives his first reprimand", f'''<p>FIA Document 25
resolves the Turn 15 summons involving Rafael Camara (Car 51) and Charles
Leclerc (Car 16). The Stewards found that Camara unnecessarily impeded Leclerc
in FP2 at 16:31; after warnings that Car 16 was on a fast lap, Car 51 moved
into the racing line and Leclerc had to take evasive action. The decision is a
driving reprimand, Camara's first of the season. It is not a grid drop or a
revised FP2 classification.
<a href="{FIA_CAMARA_REPRIMAND_URL}">FIA Document 25</a> ·
<a href="{FIA_EVENT}">FIA event documents</a>.</p>''', "bi-exclamation-triangle")}
{card("Cadillac warned after Perez throws loose cockpit item", f'''<p>FIA
Document 40 resolves the unsafe-condition summons for Sergio Perez (Car 11).
After reviewing in-car video, the Stewards found he threw a small plastic
cable organiser that had come loose from the seat belt out of the car during
FP3. Cadillac received a formal warning: the Stewards said throwing material
onto the track during a live session was inappropriate, even though the item
was small and unlikely to damage another car or injure a driver. This is not
a grid penalty. <a href="{FIA_PEREZ_UNSAFE_URL}">FIA Document 40</a> ·
<a href="{FIA_PEREZ_SUMMONS_URL}">resolved summons, Document 31</a>.</p>''',
     "bi-exclamation-triangle")}
{card("FIA issues a severe-weather garage notice", f'''<p>Race Director
Document 38 says that, due to anticipated severe weather, all teams are
allowed to close their garage doors. It is an operational precaution, not an
announcement of a session delay. <a href="{FIA_GARAGE_DOORS_URL}">FIA
Document 38</a> · <a href="{FIA_EVENT}">FIA event documents</a>.</p>''',
     "bi-cloud-rain")}
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
    strategy_rows = (
        ("1 · preferred dry route", "Soft → Medium → Soft", "17–23; 42–48"),
        ("2", "Medium → Hard → Soft", "23–29; 50–56"),
        ("3", "Soft → Hard → Soft", "16–22; 44–50"),
        ("4 · one-stop", "Medium → Hard", "28–34"),
    )
    strategy_table = "".join(
        "<tr>" + "".join(f"<td>{value}</td>" for value in row) + "</tr>"
        for row in strategy_rows
    )
    return f"""
<h2 class="sec">FIA tyre prescriptions</h2>
<p>C3 Hard / C4 Medium / C5 Soft. Mandatory race specifications: <strong>C3/C4</strong>;
Q3 tyre: <strong>C5</strong>. These are nominations, not remaining race-set counts.
The reviewed chart below is the pre-race remaining-set snapshot, taken after
Qualifying; it is not a live post-race inventory.</p>
<div class="table-wrap"><table class="data" id="brazil-tyre-limits">
<thead><tr><th>Type</th><th>Axle</th><th>Minimum start (psi)</th>
<th>Expected stabilized (psi)</th><th>Camber limit</th></tr></thead><tbody>{table}</tbody></table></div>
<p>Maximum heating: two hours, 70°C slick/intermediate and 40°C wet, measured
at tread and sidewall rather than the blanket controller. Cold-pressure curves:
front (T−70)×0.126+Pstart; rear (T−70)×0.125+Pstart. These figures are from
FIA Competition Notes, Document 2, version 5 issue A; check the current event
listing and screenshot gallery for revisions.</p>
<p>Pirelli's full poster estimates <strong>22.5 seconds pit-stop loss</strong>.
Traction, braking, stress, abrasion, grip and lateral demand are all 3/5;
track evolution is 5/5. Resurfacing between Turns 3–5 and 8–9 makes Friday's
long runs important. Last year's effective two-stop race is historical context,
not the source for 2026 strategy windows.</p>
<h2 class="sec">Race strategy in the wet-dry-wet race</h2>
<p>Formula1.com's race report describes a wet-dry-wet 71-lap Grand Prix.
Hamilton was first to switch to Softs at the end of Lap 14; Norris, Russell
and Hadjar stopped at the end of Lap 16, followed by Antonelli and Verstappen
on Lap 17. Norris made another stop on Lap 49. When rain returned, Russell
and Alonso were first to switch to Intermediates at Lap 61, then the field
followed. FIA Document 81 records the final classification after 71 laps and
305.879 km, matching the current Formula1.com result table.
<a href="{F1_RACE_REPORT}">Formula1.com race report and pit-stop chronology</a> ·
<a href="{FIA_EVENT}">FIA event listing</a> ·
<a href="{FIA_FINAL_RACE_CLASSIFICATION_URL}">FIA Document 81, final classification</a> ·
<a href="{F1_RACE_RESULTS}">Formula1.com Race classification</a>.</p>
<p>Pirelli's 8 November race report confirms that each driver who started used
Intermediates and Softs. Norris's Soft stints lasted 33 and 13 laps; Russell
and Leclerc each kept one Soft set for 45 laps before using a second set for
the final ten. Pirelli's race graphic records 914 Soft laps (64%) and 521
Intermediate laps (36%); the longest Intermediate stint was 17 laps for
Colapinto, Gasly, Antonelli, Verstappen and Alonso. The separate pit-stop
graphic records 58 stops. Pirelli attributes the varied choices to changing
weather: track temperature reached only 16°C, with mainly thermal degradation
and some graining on the drying surface; wear became the main factor to manage.
These are observed race outcomes, separate from the pre-race projections below.
<a href="{PIRELLI_RACE_REPORT}">Pirelli's official post-race report</a> ·
<a href="{PIRELLI_RACE_STINTS_IMAGE}">Pirelli race tyre-use graphic</a> ·
<a href="{PIRELLI_RACE_PIT_STOPS_IMAGE}">Pirelli pit-stop graphic</a>.</p>
<h2 class="sec">Pre-race strategy forecast (for comparison)</h2>
<p>Pirelli's 7 November report says Qualifying used Full Wets in Q1, then
Intermediates from Q2 through Q3. This describes qualifying tyre use, not the
drivers' remaining race sets; the report's Saturday graphic is a session summary.
Pirelli's report put the race-day rain chance at 60% when published; that is a dated forecast,
not a live weather reading. These dry-race projections did not describe the
wet-dry-wet race. For a dry race, Pirelli revised its pre-weekend
simulations using Friday FP2 as the only representative long-run data: its
preferred route is two stops, with two stints on Soft and one on Medium. Pirelli
estimates this about three seconds quicker than strategies using all three
available slick compounds; a Hard stint with two Soft stints increases total
time, while a one-stop is estimated around ten seconds slower than the best
two-stop. It also says an undercut may be decisive, especially when switching
to a softer compound. These are Pirelli estimates, not measured outcomes; the
Pirelli report itself gives no lap windows. Coffee Corner Motorsport's separate
chart, credited to Pirelli Motorsport, plots four scenarios; these are
illustrative windows, not measured pit stops:</p>
<div class="table-wrap"><table class="data" id="brazil-strategy-options">
<thead><tr><th>Option</th><th>Compound route</th><th>Pit window (lap)</th></tr></thead>
<tbody>{strategy_table}</tbody></table></div>
{_strategy_figure()}
<p>The separate pre-race remaining-set graphic is a Pirelli Motorsport chart reproduced by
Coffee Corner Motorsport. It shows one new C3 Hard and one new C4 Medium for
each of the 22 entrants; the ten drivers who reached Q3 have four new C5 Softs
and the other twelve have five. Its used-slick columns are dashes, consistent
with the article's post-qualifying inventory note and Pirelli's confirmation
that Qualifying used only wet-weather tyres. This is the remaining race
inventory before the Race, not a claim that slicks were unused in practice.
The verified table
is image-bound and lists all six new/used cells for every driver.
<a href="{PIRELLI_POST_QUALI_STRATEGY}">Pirelli's post-qualifying assessment</a> ·
<a href="{PIRELLI_FP2_STRATEGY}">Friday FP2 analysis</a> ·
<a href="{CCM_BRAZIL_STRATEGY}">Coffee Corner Motorsport's full article and graphic</a> ·
<a href="{F1_QUALIFYING_RESULTS}">official Qualifying</a> ·
<a href="{F1_STARTING_GRID}">official Starting Grid</a>.</p>
{_figure("fia-brazil-8188298e7b47-84d11f15335e159e-p2",
         "Sao Paulo tyre prescriptions, version 5 issue A", "competition_notes_-_pirelli_preview")}
"""


def _strategy_brief():
    return f"""<p>Formula1.com's report describes a wet-dry-wet 71-lap race:
Hamilton was first to switch to Softs at the end of Lap 14; Norris, Russell
and Hadjar stopped at the end of Lap 16, followed by Antonelli and Verstappen
on Lap 17. Norris made another stop on Lap 49. Rain returned at Lap 61, when
Russell and Alonso first changed to Intermediates and the field followed.
The pre-race dry strategy projections are retained on
<a href="tyres.html">Tyres &amp; Strategy</a> as historical estimates, not
the race's actual route. FIA Document 81 confirms the final classification
after 71 laps and 305.879 km, in agreement with Formula1.com.
<a href="{F1_RACE_REPORT}">Formula1.com race report</a> ·
<a href="{FIA_FINAL_RACE_CLASSIFICATION_URL}">FIA Document 81, final classification</a> ·
<a href="{F1_RACE_RESULTS}">Race classification</a> ·
<a href="{FIA_EVENT}">FIA event listing</a> ·
<a href="tyres.html">Pre-race forecast and image-bound tyre-set record</a>.</p>"""


def _powerunit():
    new_elements = (
        ("03", "Red Bull Racing RB Ford", "Max Verstappen", "ICE", "4", "4",
         "Fifth of four; not compliant", "30"),
        ("03", "Red Bull Racing RB Ford", "Max Verstappen", "TC", "4", "4",
         "Fifth of four; not compliant", "30"),
        ("03", "Red Bull Racing RB Ford", "Max Verstappen", "EXH", "4", "4",
         "Fifth of four; not compliant", "30"),
        ("03", "Red Bull Racing RB Ford", "Max Verstappen", "PU-ANC", "5", "6",
         "Sixth of six; within allowance", "30"),
        ("16", "Ferrari", "Charles Leclerc", "ICE", "4", "4",
         "Fifth of four; not compliant", "30"),
        ("44", "Ferrari", "Lewis Hamilton", "ICE", "4", "4",
         "Fifth of four; not compliant", "30"),
        ("11", "Cadillac Ferrari", "Sergio Perez", "ICE", "4", "4",
         "Fifth of four; not compliant", "30"),
        ("11", "Cadillac Ferrari", "Sergio Perez", "TC", "4", "4",
         "Fifth of four; not compliant", "30"),
        ("11", "Cadillac Ferrari", "Sergio Perez", "MGU-K", "3", "3",
         "Fourth of three; not compliant", "30"),
        ("11", "Cadillac Ferrari", "Sergio Perez", "PU-ANC", "4", "6",
         "Fifth of six; within allowance", "30"),
        ("63", "Mercedes", "George Russell", "PU-ANC", "5", "6",
         "Sixth of six; within allowance", "30"),
        ("44", "Ferrari", "Lewis Hamilton", "ICE", "5", "4",
         "Sixth of four; not compliant", "42"),
        ("44", "Ferrari", "Lewis Hamilton", "TC", "4", "4",
         "Fifth of four; not compliant", "42"),
        ("44", "Ferrari", "Lewis Hamilton", "EXH", "4", "4",
         "Fifth of four; not compliant", "42"),
        ("44", "Ferrari", "Lewis Hamilton", "ES", "3", "3",
         "Fourth of three; not compliant", "42"),
        ("44", "Ferrari", "Lewis Hamilton", "PU-CE", "3", "3",
         "Fourth of three; not compliant", "42"),
        ("44", "Ferrari", "Lewis Hamilton", "MGU-K", "3", "3",
         "Fourth of three; not compliant", "42"),
        ("44", "Ferrari", "Lewis Hamilton", "PU-ANC", "6", "6",
         "Seventh of six; not compliant", "42"),
        ("41", "Racing Bulls RB Ford", "Arvid Lindblad", "ICE", "6", "4",
         "Seventh of four; not compliant", "55"),
        ("41", "Racing Bulls RB Ford", "Arvid Lindblad", "TC", "5", "4",
         "Sixth of four; not compliant", "55"),
        ("05", "Audi", "Gabriel Bortoleto", "ES", "5", "3",
         "Sixth of three; not compliant", "55"),
        ("05", "Audi", "Gabriel Bortoleto", "PU-CE", "5", "3",
         "Sixth of three; not compliant", "55"),
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
Stewards' Documents 35 and 37 impose 10-place drops for Leclerc (Car 16) and
Hamilton (Car 44), respectively, for their fifth ICEs. The Stewards' later Document
33 imposes a 30-place drop on Verstappen for the fifth ICE, turbocharger and
exhaust. Verstappen qualified 16th and the official Starting Grid placed him
21st. The Technical Delegate's Document 30 did not determine Perez's exact
position; the later Stewards' Document 39 imposes a 30-place drop for Perez's
fifth ICE, fifth turbocharger and fourth MGU-K. Perez qualified 21st and the
official Starting Grid placed him 22nd.
Document 30's fifth PU-ANC for Perez remains within that element's allowance.
The later FIA Technical Delegate's Document 42 reports Hamilton's sixth ICE,
fifth TC and EXH, fourth ES, PU-CE and MGU-K, and seventh PU-ANC. The source
states each is beyond its season allowance. The Stewards' Document 43 imposes
a further 65-place drop for these parts, in addition to Document 37's 10-place
drop for the fifth ICE. Car 44 qualified 11th; the official Formula1.com
Starting Grid places Hamilton 20th. The Race's earlier post-penalty order
was provisional; use the official table for starting positions. This
component-by-component FIA report supersedes the earlier team statement that
Hamilton would start from the back without detailed counts.
The separate Document 15 imposes a five-place drop for Russell's sixth ICE
(sixth against four allowed).
The Technical Delegate's 8 November Document 55 reports Arvid Lindblad's
seventh ICE and sixth turbocharger (four allowed each), and Gabriel Bortoleto's
sixth energy store and sixth PU-CE (three allowed each). It states all four
elements are not compliant, although the replacements were approved by the
Technical Delegate. It is not a Stewards' penalty decision and does not
establish a grid penalty. FIA Technical Delegate Document 58 also lists the
new Car 41 ICE and TC and Car 5 ES and PU-CE among approved parc-fermé
replacements; it is a technical report, not a penalty decision. Separate
Stewards' Documents 56 and 57 each impose a 10-place drop for this Race.
FIA Document 59's final Starting Grid applies both penalties: Lindblad starts
18th and Bortoleto 19th. The Formula1.com snapshot retrieved at 16:09 UTC still
showed Lindblad 12th. The official Starting Grid page checked at 18:40 UTC now
agrees with Document 59, including Stroll 16th, Bottas 17th, Lindblad 18th and
Bortoleto 19th. A results collector snapshot at 18:36 UTC briefly reverted
Lindblad to 12th; keep Results bound to the hash-reviewed FIA grid so a
transient cache response cannot replace it.
<a href="{FIA_NEW_PU_REV2_URL}">FIA Document 30</a> ·
<a href="{FIA_NEW_PU_REV3_URL}">FIA Document 55</a> ·
<a href="{FIA_PARC_FERME_PARTS_URL}">FIA Document 58</a> ·
<a href="{FIA_LINDBLAD_PU_PENALTY_URL}">FIA Document 56</a> ·
<a href="{FIA_BORTOLETO_PU_PENALTY_URL}">FIA Document 57</a> ·
<a href="{FIA_FINAL_STARTING_GRID_URL}#page=2">FIA Document 59, final Starting Grid</a> ·
<a href="{FIA_VERSTAPPEN_PENALTY_URL}">FIA Document 33</a> ·
<a href="{FIA_PEREZ_PU_PENALTY_URL}">FIA Document 39</a> ·
<a href="{FIA_LECLERC_PENALTY_URL}">FIA Document 35</a> ·
<a href="{FIA_HAMILTON_PENALTY_URL}">FIA Document 37</a> ·
<a href="{F1_PU_PENALTIES}">Formula1.com on the grid penalties</a> ·
<a href="{HAMILTON_F1_UPDATE}">Formula1.com on Hamilton's later replacement</a> ·
<a href="{RUSSELL_FIA_PENALTY}">FIA Document 15</a>.</p>
<div class="table-wrap"><table class="data compact" id="brazil-new-pu-elements">
<thead><tr><th>No.</th><th>Constructor</th><th>Driver</th><th>New element</th>
<th>Previously used</th><th>Season allowance</th><th>Report status</th>
<th>FIA document</th></tr></thead>
<tbody>{new_elements_table}</tbody></table></div>
{_figure("fia-brazil-066498a702e5-2829a7a6b78737f0-p2",
         "FIA Document 42: Hamilton's additional new ICE, turbocharger and exhaust, page 2",
         "new_pu_elements_for_this_competition_1", 2)}
{_figure("fia-brazil-066498a702e5-2829a7a6b78737f0-p3",
         "FIA Document 42: Hamilton's additional new energy store, control electronics, MGU-K and PU-ANC, page 3",
         "new_pu_elements_for_this_competition_1", 3)}
<p><a href="{FIA_HAMILTON_ADDITIONAL_PENALTY_URL}">FIA Document 43</a>
records the additional 65-place penalty and the rule for allocating a Race-grid
position. The official Starting Grid places Hamilton 20th; the full two-page
decision remains available in the Penalties reader.</p>
{_figure(FIA_NEW_PU_REV2_P2_ASSET,
         "FIA Document 30: new ICE, turbocharger and exhaust entries, page 2",
         FIA_NEW_PU_REV2_DOC, 2)}
{_figure(FIA_NEW_PU_REV2_P3_ASSET,
         "FIA Document 30: new MGU-K and PU-ANC entries, page 3",
         FIA_NEW_PU_REV2_DOC, 3)}
{_figure(FIA_NEW_PU_REV3_P2_ASSET,
         "FIA Document 55: Lindblad and Bortoleto new power-unit elements, page 2",
         FIA_NEW_PU_REV3_DOC, 2)}
{_figure(FIA_NEW_PU_REV3_P3_ASSET,
         "FIA Document 55: Bortoleto new control-electronics unit, page 3",
         FIA_NEW_PU_REV3_DOC, 3)}
<p>FIA Document 14's earlier report lists Rafael Câmara's fifth PU-ANC within
the six-element allowance. Document 30 does not add a new element for Car 51;
this is an earlier declaration, not a separate penalty.
<a href="{FIA_NEW_PU_URL}">FIA Document 14</a>.</p>
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
<h2 class="sec">FP3 and qualifying technical checks</h2>
<p>FIA Technical Delegate Document 49 records checks during FP3 and
Qualifying, including energy-store and ERS limits, MGU-K limits, engine and
fuel systems, tyre pressures and use, and aerodynamic components on cars 30
and 87. Fuel and oil samples were analysed, and the report says all listed
items complied with the 2026 Technical Regulations. It also lists the FIA
Standard ECU software versions used by each team; no individual version is
transcribed here.
<a href="{FIA}fp3_and_qualifying_scrutineering.pdf">FIA Document 49, all five
pages</a>.</p>
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
        "<p><strong>Session-by-session status:</strong> Official classifications "
        "are published for FP1, FP2, FP3, Qualifying and Race. "
        "The latest official result appears "
        "in <a href=\"results.html\">Results</a>; <a href=\"news.html\">Weekend "
        "News</a> carries session reports and official updates. Check those "
        "pages for any subsequent official corrections.</p>",
    )
    pages["notes"]["body"] += f"""
<p><strong>Qualifying steward decision:</strong> FIA Document 41 says Oliver
Bearman (Car 87) reversed in the pit lane under its own power. The Stewards
imposed a driving reprimand, his second of the season; this ruling is not a
grid penalty. <a href="{FIA_BEARMAN_REVERSAL_URL}">Read the FIA decision</a>.
See the published Qualifying result and penalty-adjusted official Starting
Grid under <a href="results.html">Results</a>.</p>
<p><strong>Qualifying lap deletions:</strong> FIA Document 44 lists eight
deleted lap-time entries affecting Rafael Câmara, Gabriel Bortoleto, Lance
Stroll, Carlos Sainz, Oliver Bearman and Sergio Perez. Document 46 separately
deletes Stroll's 1:42.680 lap for a double-waved-yellow sector. These are
lap-time decisions, not additional grid penalties or replacements for the
official qualifying classification.
<a href="{FIA_QUALIFYING_DELETIONS_URL}">FIA Document 44</a> ·
<a href="{FIA_STROLL_DOUBLE_YELLOW_URL}">FIA Document 46</a>.</p>"""
    pages["notes"]["body"] += f"""
<p><strong>Hamilton's revised power-unit penalty:</strong> FIA Document 42
lists Car 44's sixth ICE, fifth TC and EXH, fourth ES, PU-CE and MGU-K, and
seventh PU-ANC. Document 43 adds a 65-place drop to Document 37's earlier
10-place penalty (75 places cumulatively). Car 44 qualified 11th and the
official Formula1.com Starting Grid places Hamilton 20th.
<a href="{FIA_HAMILTON_NEW_PU_URL}">Document 42</a> ·
<a href="{FIA_HAMILTON_ADDITIONAL_PENALTY_URL}">Document 43</a> ·
<a href="{F1_QUALIFYING_RESULTS}">official Qualifying</a> ·
<a href="{F1_STARTING_GRID}">official Starting Grid</a> ·
<a href="{THE_RACE_PROVISIONAL_GRID}">The Race's provisional order</a>.</p>"""
    pages["notes"]["body"] += f"""
<p><strong>Later power-unit report:</strong> FIA Technical Delegate Document 55
reports Arvid Lindblad's seventh ICE and sixth turbocharger (four allowed each),
and Gabriel Bortoleto's sixth energy store and sixth PU-CE (three allowed each).
It states all four elements are not compliant despite approving their
replacement. This technical report is not a Stewards' penalty decision; no grid
penalty is inferred from Document 55 itself. Separate Stewards' Documents 56
and 57 impose 10-place drops for Lindblad (seventh ICE, sixth TC) and Bortoleto
(sixth ES, sixth PU-CE).
<a href="{FIA_NEW_PU_REV3_URL}">FIA Document 55, published 8 November</a> ·
<a href="{FIA_LINDBLAD_PU_PENALTY_URL}">FIA Document 56</a> ·
<a href="{FIA_BORTOLETO_PU_PENALTY_URL}">FIA Document 57</a> ·
<a href="powerunit.html">Power Unit analysis</a>.</p>"""
    pages["notes"]["body"] += f"""
<p><strong>Late grid-penalty check:</strong> A stored Formula1.com Starting Grid
snapshot retrieved at 16:09 UTC still listed Lindblad 12th. The official
Starting Grid page checked at 18:40 UTC agrees with FIA Document 59: Stroll
16th, Bottas 17th, Lindblad 18th and Bortoleto 19th. A collector snapshot at
18:36 UTC briefly reverted to the earlier order; Results remains bound to the
hash-reviewed FIA grid. Starting positions remain separate from qualifying
results. FIA Document 81 later records the final Race classification after
71 laps and 305.879 km; it confirms Norris, Verstappen and Hadjar in the top
three, Stroll as DNF and Bottas as DNS, with the post-race penalties applied.
The current Formula1.com table agrees.
<a href="{FIA_FINAL_STARTING_GRID_URL}#page=2">FIA Document 59, page 2</a> ·
<a href="{FIA_FINAL_RACE_CLASSIFICATION_URL}">FIA Document 81</a> ·
<a href="{F1_STARTING_GRID}">Formula1.com Starting Grid snapshot</a> ·
<a href="{F1_RACE_RESULTS}">Formula1.com Race results</a>. Related PU-penalty decisions:
<a href="{FIA_LINDBLAD_PU_PENALTY_URL}">FIA Document 56</a> ·
<a href="{FIA_BORTOLETO_PU_PENALTY_URL}">FIA Document 57</a>.</p>"""
    pages["notes"]["body"] += f"""
<p><strong>Post-race Stewards' decisions:</strong> FIA Document 67 gives
Alexander Albon a five-second time penalty and two penalty points (three for
the preceding 12 months) for rejoining at Turn 3 in front of Car 10, which had
to brake. Document 64 reprimands Lance Stroll for not crossing the pit-exit
white line at the earliest opportunity on reconnaissance laps. Documents 65
and 66 take no further action against Lewis Hamilton and Sergio Perez: the
Stewards found Hamilton returned the position after leaving the track while
avoiding Car 87, and Perez slowed appropriately for the double-yellow flags.
Document 71 gives Nico Hulkenberg a 10-second time penalty for leaving the
track and gaining a lasting advantage while overtaking Car 43 at Turn 1. FIA
Document 81 later confirms Hulkenberg 10th in the final classification after
that penalty. The Penalties page retains each same-row FIA reader.
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_infringement_-_car_23_-_rejoining_the_track_unsafely.pdf">Document 67</a> ·
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_infringement_-_car_18_-_failure_to_follow_race_directors_instruction_-_practice_start.pdf">Document 64</a> ·
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_decision_-_car_44_-_alleged_leaving_the_track_and_gaining_an_advantage.pdf">Document 65</a> ·
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_decision_-_car_11_-_alleged_failure_to_slow_under_yellow_flags.pdf">Document 66</a> ·
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_infringement_-_car_27_-_leaving_the_track_and_gaining_an_advantage.pdf">Document 71</a>.</p>"""
    pages["notes"]["body"] += f"""
<p><strong>Latest post-race FIA updates (discovery checked 21:34 UTC):</strong>
Document 80 resolves Documents 68 and 69: Kimi Antonelli received five seconds
added to Race time after Car 12 was released into Franco Colapinto's path. The
Stewards noted the slippery surface and that Antonelli had to take steps to avoid
a collision. Document 79 resolves Documents 72 and 73: Charles Leclerc received
five seconds added to Race time for contact with Liam Lawson's Car 30 at Turn 12.
The Stewards found the contact disrupted Car 30 and helped Car 16 overtake it
five corners later; wet conditions and the minor contact mitigated the penalty
from ten seconds. Document 78 resolves Documents 74 and 75: Oliver Bearman
received five seconds added to Race time after Car 87 was released into
Leclerc's path and forced Car 16 to brake and take evasive action. Document 76
lists 22 deleted Race lap-time entries across ten drivers for not using the
track at Turns 1, 2, 3, 4, 7 and 8; these are lap deletions, not additional time
penalties. Technical Delegate Document 77 reports that the checked cars and
items, including Car 23's additional post-race throttle-pedal assembly
inspection, complied with the 2026 Technical Regulations. FIA Document 81 is
the final classification after 71 laps and 305.879 km; it applies the three
five-second penalties and matches Formula1.com's current 22-entrant result.
FIA Document 82 records the championship points after Brazil, including 390
for Antonelli and 652 for Mercedes.
<a href="{FIA_ANTONELLI_UNSAFE_RELEASE_URL}">Document 80</a> ·
<a href="{FIA_LECLERC_COLLISION_URL}">Document 79</a> ·
<a href="{FIA_BEARMAN_UNSAFE_RELEASE_URL}">Document 78</a> ·
<a href="{FIA_FINAL_RACE_CLASSIFICATION_URL}">Document 81, final classification</a> ·
<a href="{FIA_CHAMPIONSHIP_POINTS_URL}">Document 82, championship points</a> ·
<a href="{FIA + 'infringement_-_race_deleted_lap_times.pdf'}">Document 76</a> ·
<a href="{FIA_RACE_SCRUTINEERING_URL}">Document 77</a> ·
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_summons_-_car_12_-_alleged_unsafe_release.pdf">Document 68</a> ·
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_summons_-_car_43_-_alleged_unsafe_release_by_car_12.pdf">Document 69</a> ·
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_summons_-_car_16_-_alleged_causing_a_collision.pdf">Document 72</a> ·
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_summons_-_car_30_-_alleged_causing_a_collision.pdf">Document 73</a> ·
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_summons_-_car_87_-_alleged_unsafe_release.pdf">Document 74</a> ·
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_summons_-_car_16_-_alleged_unsafe_release_by_car_87.pdf">Document 75</a> ·
<a href="{F1_RACE_RESULTS}">Formula1.com Race results table</a>.</p>"""
    pages["rookies"]["body"] = _lineup() + pages["rookies"]["body"].replace(
        content_generic.pending("Rookie FP1 line-ups for this round", "in the week before the event"), ""
    ).replace(content_generic.pending(
        "Reserve or replacement driver changes", "as teams confirm them", "bi-people"), "")
    pages["teams"]["body"] = _lineup() + _teams()
    long_run_pending = content_generic.pending(
        "Long-run degradation data", "after Friday practice", "bi-graph-down"
    )
    if long_run_pending in pages["tyres"]["body"]:
        pages["tyres"]["body"] = pages["tyres"]["body"].replace(
            long_run_pending,
            "<p><strong>Published tyre analysis:</strong> Pirelli's Friday FP2 "
            "report found consistent Soft performance, no graining and similar "
            "abrasion across compounds, with rear-right wear a factor over longer "
            "stints. Its post-qualifying strategy assessment is summarized below. "
            "No driver-by-driver practice long-run table is transcribed here.</p>",
        )
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
    pages["upgrades"]["body"] += f"""
<h2 class="sec">Parc-fermé replacement report</h2>
<p>FIA Technical Delegate Document 58, dated 8 November, lists approved
replacements for 12 cars across Mercedes, Red Bull Racing, Ferrari, Williams,
Racing Bulls, Aston Martin, Haas, Audi and Cadillac. These are parts changed
during parc fermé after written team requests under Article B3.5.4, not
performance-upgrade claims. The report lists new ICE and TC for Car 41 and new
ES and PU-CE for Car 5; it is not a Stewards' penalty decision. The separate
10-place drops are in Documents 56 and 57.
<a href="{FIA_PARC_FERME_PARTS_URL}">Original FIA Document 58</a>.</p>
{_figure("fia-brazil-6b37cfed4f17-d33f7f0159074489-p1",
         "FIA Technical Delegate Document 58: parc-fermé replacements, page 1",
         FIA_PARC_FERME_PARTS_DOC, 1)}
{_figure("fia-brazil-6b37cfed4f17-d33f7f0159074489-p2",
         "FIA Technical Delegate Document 58: parc-fermé replacements, page 2",
         FIA_PARC_FERME_PARTS_DOC, 2)}
{_figure("fia-brazil-6b37cfed4f17-d33f7f0159074489-p3",
         "FIA Technical Delegate Document 58: parc-fermé replacements, page 3",
         FIA_PARC_FERME_PARTS_DOC, 3)}"""
    pages["schedule"]["body"] += f"""
<p><strong>Standard weekend, not Sprint:</strong> Friday FP1 12:30 and FP2 16:00;
Saturday FP3 11:30 and Qualifying was scheduled for 15:00; the Race started
Sunday at 14:00 (all BRT). Add five hours for Tallinn (EET): Race
<strong>19:00 Sunday 8 November</strong>. FIA Timetable V5 supersedes V4 and
extends the third Brazil Junior Trophy race from 20 to 25 minutes plus one lap
(08:50–09:20 BRT). The Grand Prix started at 14:00 BRT; the official
classification records 71 laps and 305.879 km in 1:35:23.504.
<a href="{FIA}timetable_v5.pdf#page=2">Timetable V5, page 2</a>.
The Race reports that Qualifying was delayed by 1h25 and red-flagged almost
immediately in heavy rain. Formula1.com's official
classification now lists all 22 qualifiers: Lando Norris took pole in 1:27.470,
0.204s ahead of George Russell. FIA Document 50's final Qualifying
classification confirms the 22-car order. The FIA's later Document 59 is the final Starting Grid,
issued at 13:00 BRT; it applies the 10-place penalties in Documents 56 and 57,
placing Lindblad 18th and Bortoleto 19th. The Formula1.com Starting Grid
snapshot retrieved at 16:09 UTC still listed Lindblad 12th. A current official
Starting Grid check at 18:40 UTC now matches FIA Document 59 (Lindblad 18th,
Bortoleto 19th; Stroll 16th, Bottas 17th). The collector briefly received a
stale order at 18:36 UTC, so Results remains pinned to the hash-reviewed final
grid. FIA Document 81 now records the final 22-car Race classification after
71 laps and 305.879 km; it confirms Norris, Verstappen and Hadjar in the top
three, with Stroll DNF and Bottas DNS. The current Formula1.com result table
matches this final order.
Do not substitute starting positions for qualifying results. Document 51 was
provisional and predates the final grid. The Race's earlier post-penalty order
was provisional and is superseded by Document 59. See
<a href="notes.html">Notes</a> and <a href="penalties.html">Penalties</a> for
the source comparison.
<a href="{FIA_LINDBLAD_PU_PENALTY_URL}">FIA Document 56</a> ·
<a href="{FIA_BORTOLETO_PU_PENALTY_URL}">FIA Document 57</a> ·
<a href="{FIA_FINAL_STARTING_GRID_URL}#page=2">FIA Document 59, page 2</a> ·
<a href="{FIA_FINAL_RACE_CLASSIFICATION_URL}">FIA Document 81, final Race classification</a> ·
<a href="{FIA_CHAMPIONSHIP_POINTS_URL}">FIA Document 82, championship points</a> ·
<a href="{F1_RACE_RESULTS}">Formula1.com Race results</a>.
<a href="{THE_RACE_QUALIFYING}">The Race's qualifying report</a> ·
<a href="{THE_RACE_PROVISIONAL_GRID}">The Race's earlier provisional order</a> ·
<a href="{F1_QUALIFYING_RESULTS}">official Qualifying results</a> ·
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_final_qualifying_classification.pdf#page=2">FIA Document 50, final Qualifying classification p. 2</a> ·
<a href="{F1_STARTING_GRID}">official Starting Grid</a> ·
<a href="https://www.fia.com/system/files/decision-document/2026_sao_paulo_grand_prix_-_provisional_starting_grid.pdf#page=2">FIA Document 51, provisional Starting Grid p. 2</a> ·
<a href="{THE_RACE_PROVISIONAL_GRID}">The Race's provisional order</a> ·
<a href="{FIA_EVENT}">live FIA event documents</a>. FP1, FP2 and FP3
classifications and Qualifying are published, and the final Race
classification is published. FIA Document 82 records the updated
championship points. The pre-race Pirelli race-set chart covers
all 22 drivers; its image-bound transcription records the allocation before
the start on <a href="tyres.html">Tyres &amp; Strategy</a>.</p>
<p><strong>Curfew report, 7 November:</strong> FIA Technical Delegate
Document 27 says Oracle Red Bull Racing and Aston Martin personnel were inside
the circuit during the 11.5-hour pre-FP3 curfew, from 21:00 Friday to 08:30
Saturday BRT. This was Oracle Red Bull Racing's second and Aston Martin's third
of four permitted team exceptions; the report says no action should be taken.
<a href="{FIA}curfew_0.pdf">FIA Document 27</a>.</p>"""
    pages["schedule"]["body"] += f"""
<p><strong>Qualifying parc-fermé deadline:</strong> FIA Race Director
Document 47, issued at 18:23 on Saturday, required every car used in Qualifying
to be covered and ready for FIA seals by 19:27 local time under Regulation
B3.4.3a. <a href="{FIA}covers-on_time.pdf">FIA Document 47</a>.</p>"""
    pages["schedule"]["body"] += f"""
<p><strong>FIA Media Delegate's Document 29 — Post-Qualifying Procedure:</strong>
if the top three take the chequered flag at the end of Q3, they return to the
pit lane at the 1–3 boards, then are weighed by the FIA in full race gear.
Post-qualifying interviews take place in Parc Fermé; access to the designated
area is limited to mechanics, officials and pre-approved media, not driver
physios or team PR. The top three then complete the photo, press-conference and TV-pen sequence.
Drivers eliminated in Q1/Q2, those classified 4th–10th in Q3 and eligible
drivers who did not participate in Q1 must attend the required TV-pen
interviews immediately after weighing; drivers must not drink or increase
their weight before it is recorded. Top-ten drivers report directly to the FIA
scales on leaving their cars, and drivers who stop on track (unless sent to
the Medical Centre) are weighed before returning to their teams.
The parc-fermé layout is on page 4.
<a href="{FIA_POST_QUALIFYING_URL}#page=2">FIA Document 29, procedure</a> ·
<a href="{FIA_POST_QUALIFYING_URL}#page=4">parc-fermé diagram</a> ·
<a href="{FIA_EVENT}">complete FIA event listing</a>.</p>"""
    pages["schedule"]["body"] += f"""
<p><strong>Race-day anthem procedure:</strong> The FIA Media Delegate's
8 November pre-race procedure said drivers should move to the anthem position
at 13:40 BRT and be in place by 13:42; the national anthem was scheduled for
13:44, with drivers in race suits. It reiterates that all drivers must be at
the front of the grid no less than 16 minutes before the scheduled formation
lap. The accompanying diagram shows the anthem setup; these are instructions,
not a report of compliance.
<a href="{FIA_PRE_RACE_URL}#page=2">FIA pre-race procedure, page 2</a> ·
<a href="{FIA_PRE_RACE_URL}#page=3">anthem-position diagram, page 3</a>.</p>
<p><strong>Post-race procedure:</strong> The FIA Media Delegate's 8 November
procedure directs the top three to return to the Pit Lane after the chequered
flag, where the 1–3 boards are at the entrance, then be weighed by the FIA in
full race attire; water is available after weighing. Their post-race interviews
take place in Parc Fermé before the cooldown-room and podium sequence. Drivers
classified fourth or lower proceed to the TV pen after weighing; the document
also covers media commitments for retirees. Its final page diagrams the
Parc Fermé and race podium layout. This is procedure, not a penalty or
confirmation that any individual complied.
<a href="{FIA_POST_RACE_URL}#page=2">FIA post-race procedure, pages 2–3</a> ·
<a href="{FIA_POST_RACE_URL}#page=4">Parc Fermé diagram, page 4</a>.</p>"""
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
    pages["overview"]["body"] += f"""
<h2 class="sec">Race strategy recap</h2>
{card("Observed wet-dry-wet strategy", _strategy_brief(), "bi-compass", "accent")}"""
    pages["notes"]["body"] += f"""
<h2 class="sec">Race strategy recap</h2>
{_strategy_brief()}
<p><strong>FIA race-day procedure:</strong> Drivers were instructed to move
to the national-anthem position at 13:40 BRT, be in place by 13:42, and remain
in race suits for the 13:44 anthem. After the race, the top three were to return
to the Pit Lane for weighing before Parc Fermé interviews and the podium;
fourth and lower finishers were to go to the TV pen after weighing. These are
the Media Delegate's instructions, not penalty findings or a compliance report.
<a href="{FIA_PRE_RACE_URL}#page=2">Pre-race procedure</a> ·
<a href="{FIA_POST_RACE_URL}#page=2">Post-race procedure</a>.</p>"""
    pages["facts"]["body"] += career_starts.render(ctx)
    pages["overview"]["body"] += f"""<h2 class="sec">Hamilton's 400th start</h2>
<p>Twenty consecutive seasons, seven titles, and still taking poles:
Formula1.com marks Hamilton's 400th Grand Prix at Sao Paulo.
<a href="facts.html#career-starts">Career-start ranking, current drivers and
conditional milestones</a> &middot;
<a href="{career_starts.ARTICLE}">Official milestone feature</a>.</p>"""
    pages["notes"]["body"] += """<p><strong>Hamilton milestone:</strong>
Formula1.com identifies Brazil as his 400th start after 20 consecutive seasons.
Use the <a href="facts.html#career-starts">dated career-start ranking</a> for
on-air comparisons; entries and sprints are not Grand Prix starts, and active
rivals continue accumulating starts.</p>"""
    pages["powerunit"]["body"] += f"""
<h2 class="sec">Race scrutineering — FIA Document 77</h2>
<p>The Technical Delegate's report records race-weekend checks of the cars,
power-unit systems, fuel and oil, followed by post-race weight and component
inspections. Car 23 was selected for an additional throttle-pedal assembly
inspection; the report states that all checked items and car weights complied
with the 2026 Technical Regulations. This is a technical inspection report,
not a Stewards' ruling. The five substantive pages are available in the FIA
document gallery below.
<a href="{FIA_RACE_SCRUTINEERING_URL}">FIA Document 77</a>.</p>"""
    pages["penalties"] = {
        "kicker": "Stewards",
        "title": "Penalties & Stewards",
        "sub": "Every stewards' decision, infringement, fine and penalty from the FIA event documents.",
        "body": render_penalties(ctx, [
            {
                "doc": "Doc 78",
                "no": "87",
                "driver": "Oliver Bearman",
                "team": "TGR Haas F1 Team",
                "session": "Race",
                "fact": "Car 87 was released in an unsafe manner into the path of Car 16, forcing Charles Leclerc to brake and take evasive action.",
                "outcome": "5 second time penalty (5 seconds added to elapsed Race time).",
                "kind": "penalty",
                "source_pdf": "2026_sao_paulo_grand_prix_-_infringement_-_car_87_-_unsafe_release.pdf",
                "source_url": FIA_BEARMAN_UNSAFE_RELEASE_URL,
            },
            {
                "doc": "Doc 79",
                "no": "16",
                "driver": "Charles Leclerc",
                "team": "Scuderia Ferrari HP",
                "session": "Race",
                "fact": "Car 16 made contact with Liam Lawson's Car 30 at Turn 12; the Stewards found the contact disrupted Car 30 and helped Car 16 overtake it five corners later.",
                "outcome": "5 second time penalty (5 seconds added to elapsed Race time); wet conditions and the minor contact mitigated the penalty from ten seconds.",
                "kind": "penalty",
                "source_pdf": "2026_sao_paulo_grand_prix_-_infringement_-_car_16_-_causing_a_collision.pdf",
                "source_url": FIA_LECLERC_COLLISION_URL,
            },
            {
                "doc": "Doc 80",
                "no": "12",
                "driver": "Kimi Antonelli",
                "team": "Mercedes-AMG PETRONAS F1 Team",
                "session": "Race",
                "fact": "Car 12 was released in an unsafe manner into Franco Colapinto's Car 43 path; Antonelli had to take steps to avoid a collision on the slippery surface.",
                "outcome": "5 second time penalty (5 seconds added to elapsed Race time).",
                "kind": "penalty",
                "source_pdf": "2026_sao_paulo_grand_prix_-_infringement_-_car_12_-_unsafe_release.pdf",
                "source_url": FIA_ANTONELLI_UNSAFE_RELEASE_URL,
            },
        ], fia_url=FIA_EVENT),
    }
    return pages
