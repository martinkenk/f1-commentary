"""Reviewed Azerbaijan-specific weekend coverage.

Keep compound nominations separate from the post-qualifying set inventory
and distinguish published strategy windows from editorial interpretation.
"""

import content_generic
import f1lib
from html import escape


PREVIEW_URL = (
    "https://www.formula1.com/en/latest/article/what-tyres-will-the-teams-and-"
    "drivers-have-for-the-2026-azerbaijan-grand-prix.1UFiasleBnLs9s0hyRCpS0"
)
PREVIEW_IMAGE = "azerbaijan_pirelli_tyres_2026.webp"
STRATEGY_URL = "https://coffeecornermotorsport.com/azerbaijan-grand-prix-2026-tyre-strategy/"
STRATEGY_IMAGE = "azerbaijan-pirelli-strategies-2026.webp"
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
FIA_ROOT = "https://www.fia.com/system/files/decision-document/2026_azerbaijan_grand_prix_-_"
FIA_MAP_URL = FIA_ROOT + "competition_notes_-_circuit_map_pit_lane_drawing_emergency_exits_map_and_red_zone.pdf"
FIA_NOTES_URL = FIA_ROOT + "race_directors_competition_notes_v3.pdf"
FIA_DISPLAY_URL = FIA_ROOT + "car_display_procedure.pdf"
FIA_VISA_URL = FIA_ROOT + "competition_visa_v2.pdf"
FIA_CAR_PRESENTATION_URL = FIA_ROOT + "car_presentation_submissions.pdf"
FIA_PU_NEW_URL = FIA_ROOT + "new_pu_elements_for_this_competition.pdf"
FIA_PU_USED_URL = FIA_ROOT + "pu_elements_used_per_driver_up_to_now.pdf"
FIA_FP1_DELETED_URL = FIA_ROOT + "infringement_-_free_practice_1_deleted_lap_times.pdf"
FIA_FP1_YELLOW_URL = FIA_ROOT + "infringement_-_free_practice_1_deleted_lap_times_-_double_yellow_flags.pdf"
FIA_BOTTAS_SUMMONS_URL = FIA_ROOT + "summons_-_car_77_-_alleged_yellow_flag_infringement.pdf"
FIA_ALONSO_PENALTY_URL = FIA_ROOT + "infringement_-_car_14_-_pu_elements.pdf"
FIA_STROLL_PENALTY_URL = FIA_ROOT + "infringement_-_car_18_-_pu_elements.pdf"
FIA_SC_NOTE_URL = FIA_ROOT + "race_director_notes_-_sc2_-_sc1_times.pdf"
FIA_LAWSON_SUMMONS_URL = FIA_ROOT + "summons_-_car_30_-_alleged_impeding_by_car_44.pdf"
FIA_HAMILTON_SUMMONS_URL = FIA_ROOT + "summons_-_car_44_-_alleged_impeding_of_car_30.pdf"
FIA_HAMILTON_IMPEDING_RULING_URL = FIA_ROOT + "infringement_-_car_44_-_impeding_car_30.pdf"
FIA_ALONSO_FP3_PENALTY_URL = FIA_ROOT + "infringement_-_car_14_-_pu_element.pdf"
FIA_ALONSO_FP3_TD_URL = FIA_ROOT + "new_pu_elements_for_this_competition_0.pdf"
FIA_FP3_CLASSIFICATION_URL = FIA_ROOT + "free_practice_3_classification.pdf"
F1_ROOT = "https://www.formula1.com/en/latest/article/"
LINEUP_URL = F1_ROOT + "its-good-to-come-back-to-the-fight-hadjar-opens-up-on-new-contract-and-return-to-racing.6NzCNMkA6szXJuzSDLcx4g"
WILLIAMS_URL = F1_ROOT + "why-sainz-and-albon-remain-cautious-on-long-awaited-williams-upgrade-package.4dgoSwY5UbscNhWXSeMvnI"
OCON_URL = F1_ROOT + "definitely-a-free-agent-for-next-year-ocon-gives-update-on-haas-future-as-discussions-ongoing.5puGpQ2dMNroVXzQiV0Tgd"
FORM_URL = F1_ROOT + "need-to-know-the-most-important-facts-stats-and-trivia-ahead-of-the-2026-azerbaijan-grand-prix.3PkKCxoeboOkSc18pCB2z"
MOMENTS_URL = F1_ROOT + "f1s-wildest-azerbaijan-moments-from-10-years-of-racing-in-baku.4hKjzE3m20ov49AE4kSf0F"
TECH_URL = "https://www.the-race.com/formula-1/six-f1-tech-talking-points-at-the-azerbaijan-gp/"
AUDI_UPGRADE_URL = "https://www.the-race.com/formula-1/gary-anderson-audi-baku-f1-upgrade/"
PENALTY_ARTICLE_URL = F1_ROOT + (
    "alonso-and-stroll-set-for-grid-penalties-at-azerbaijan-gp-after-taking-new-"
    "engine-components.2uOl7HZHamxmaUqjOxejAF"
)
FP3_ARTICLE_URL = F1_ROOT + (
    "fp3-verstappen-beats-russell-and-hamilton-in-final-practice-for-azerbaijan-gp"
    ".4BuODmX7lLpgRKnIK4oMXg"
)


def source(url, label):
    return f'<p class="src">Source: <a href="{escape(url, quote=True)}" target="_blank" rel="noopener">{escape(label)}</a>.</p>'


def table(headers, rows):
    return ('<div class="table-wrap"><table class="data"><thead><tr>'
            + "".join(f"<th>{h}</th>" for h in headers)
            + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>" for row in rows)
            + "</tbody></table></div>")


def circuit_briefing():
    return f"""
<h2 class="sec">2026 Straight Mode and Overtake — different systems</h2>
<p>The FIA circuit map is <strong>version 2, issued 15 September</strong>, in the
23 September competition filing. Two active-aero Straight Mode zones do not mean
two Overtake detection points. Straight Mode reduces drag; Overtake is the
separate electrical-power aid with a <strong>1.0-second detection gap</strong>.</p>
{table(["Location", "Normal grip", "Low grip"], [
    ("Straight Mode A1", "45 m after T19", "45 m after T20"),
    ("Straight Mode A2", "110 m after T2", "160 m after T2"),
])}
<p><strong>Overtake detection:</strong> 90 m after T16.
<strong>Activation:</strong> 20 m before T17. The PU sheet identifies L20 at
4,177 m and L21 at <strong>4,270 m (TBC)</strong>; these are timing-loop identifiers,
not corner numbers. The map's relative locations do not remove the PU sheet's TBC.</p>
{table(["Timing point", "Published location / length"], [
    ("Intermediate 1 (S1)", "45 m before T5"),
    ("Intermediate 2 (S2)", "55 m before T16"),
    ("Speed trap (T)", "210 m after T20"),
    ("Sectors 1 / 2 / 3", "2.033 / 2.025 / 1.945 km"),
    ("Circuit centreline", "6.003 km"),
])}
{source(FIA_MAP_URL + "#page=2", "FIA circuit map, PDF page 2")}

<h2 class="sec">Race Director's notes — what changes the call</h2>
<p>Rui Marques's 23 September notes were reissued as <strong>Version 3 on
26 September</strong>. These are instructions, not stewards' penalties. All
seven substantive pages and their diagrams remain available in the source
gallery below.</p>
{content_generic.ul([
    "<strong>SC2–SC1 maximum time:</strong> published after FP2 (Document 27) as <strong>2:08.0</strong>. It applies on any lap <strong>during and after qualifying</strong>, including in/outlaps, and race reconnaissance with pit exit open, to avoid cars being driven unnecessarily slowly (PDF p2, §1; Doc 27).",
    "<strong>Blue flags:</strong> pre-warning at 3.0 seconds; blue panels at 1.2 seconds. Safety Car restart pacing must not involve dangerous acceleration, braking or manoeuvres once its orange lights go out (p2, §§2–3).",
    "<strong>Lap deletion:</strong> a double-yellow sector in free practice deletes that lap time. Only on-track laps count for classifications. Do not invent a Baku-specific next-lap track-limit deletion rule (p3, §§6,9).",
    "<strong>Practice starts:</strong> marked left-hand pit-exit boxes in practice/reconnaissance; two additional grid-start laps after FP2. None during qualifying or with another car stationary ahead. Race reconnaissance has a specific exception for cars not practising starts: cross onto the normal racing line at the earliest opportunity and do not cross back (pp4–5, §13).",
    "<strong>Pit-entry commitment:</strong> passing right of the dashed/continuous-line intersection counts as entering. At exit no part of a tyre may cross the separating line, subject to the specific reconnaissance procedure (p6, §15).",
    "<strong>Queueing:</strong> a whole tyre must cross beyond the far side of the fast-lane line to establish a place; blend safely at the earliest opportunity, not by driving alongside the queue in the inner lane (pp5–6, §14).",
    "<strong>Qualifying red flag:</strong> a period interrupted with less than 100 seconds remaining is not resumed (p6, §16).",
    "<strong>Race resumption:</strong> cars normally stop in the pit fast lane near the last team garage. The Safety Car leaves one minute before resumption and waits <strong>before T16</strong> (p7, §22).",
    "<strong>2026 changes:</strong> resurfaced sections at T2/T3/T4 and patches before T7 and at T19; painted kerbs removed; right-side pit-entry and T1-exit lines realigned, T15 apex line widened, blue line added on the right at T16 exit (p8, §26).",
    "<strong>Double-yellow mirroring:</strong> panel 8 onto 7 and panel 11 onto 10 (p8, §25).",
])}
{source(FIA_NOTES_URL, "FIA Race Director's Competition Notes V3, 26 September 2026, PDF pages 2–8")}
{source(FIA_SC_NOTE_URL, "FIA Document 27, Race Director's Note to Teams — SC2/SC1 Times, 24 September 2026")}
<h2 class="sec">Pitlane, emergency exits and red zone</h2>
<p>The emergency map uses <strong>red for exits on the left and green for exits
on the right</strong>, distinguishing drive-in refuges from push-in refuges
(PDF p3). The pitlane drawing shows the <strong>80 km/h</strong> limit, Safety
Car lines, the high-voltage personnel collection point and team boxes (p4).
The separate red-zone drawing is a media/access plan, not an aero-zone map (p5).</p>
<p>Pit boxes run McLaren, Mercedes, Red Bull, Ferrari, Williams, Racing Bulls,
Aston Martin, Haas, Audi, Alpine and Cadillac in the marked fast-lane direction.
Race-note diagrams additionally define where pit-entry/exit marshalling sectors
change; their blue lines are not Overtake lines.</p>
{source(FIA_MAP_URL, "FIA maps, PDF pages 3–5; notes §11 for marshalling boundaries")}
"""


def powerunit_briefing():
    return f"""
<div class="callout"><strong>Baku energy briefing — visually checked against the
FIA's event sheet, PDF page 2.</strong> Recharge is energy recovered per lap (MJ),
not deployed power (kW). Straight Mode is active aerodynamics; Overtake changes
the allowed electrical-power curve. Neither should be called a DRS zone.</div>
<h2 class="sec">Recharge and power-reduction limits</h2>
{table(["Session / condition", "Maximum recharge per lap (C5.2.10)"], [
    ("Race — Overtake inactive", "8.5 MJ"),
    ("Race — Overtake active", "9.0 MJ"),
    ("Qualifying", "8.5 MJ"),
    ("Free practice", "9.0 MJ"),
    ("Outlaps other than in the race", "9.0 MJ"),
])}
<p>Article C5.12.8: <strong>3,796 m power-limited distance</strong>;
<strong>50 kW/s rate limit</strong>. This rate is not an energy allowance.</p>
<h2 class="sec">Which power curve applies?</h2>
<p>In the race's main overtaking zones, the sheet assigns <strong>Base–Standard</strong>
with Overtake off and <strong>Base–Overtake</strong> with it on. The alternative
<strong>Alt 1</strong> curve applies in the identified other sectors below.
All practice sessions <strong>including qualifying use Base–Overtake</strong>.</p>
<p>The plotted Base–Standard ceiling is 350 kW to 290 km/h, then tapers to
100 kW at 340 km/h and zero at 345 km/h. Base–Overtake holds 350 kW to
340 km/h before falling to zero at 355 km/h. Alt 1 has a 250 kW plateau
and joins the standard taper at 310 km/h. These are regulatory ceilings
read from the plot, not measured Baku deployment or guarantees of battery availability.</p>
{table(["Rule", "Sector", "Lap distance", "Limit / meaning"], [
    ("C5.2.8iii — Alt 1", "T1–T2", "300–600 m", "Alternative race power curve"),
    ("C5.2.8iii — Alt 1", "T3–T12", "1,500–2,870 m", "Alternative race power curve"),
    ("C5.2.8iii — Alt 1", "T15–T16", "3,700–4,050 m", "Alternative race power curve"),
    ("C5.12.4 — reduction at start of power-limited pending period", "T1–T2 / T3–T12 / T15–T16", "300–600 / 1,500–2,870 / 3,700–4,050 m", "350 kW maximum in each"),
    ("C5.12.4 — qualifying only", "[Exit T16]", "[4,050–5,300 m]", "[350 kW]"),
    ("C5.12.5 — permitted reset", "Exit T19", "4,650–5,600 m", "MGUK power reduction reset"),
    ("C5.12.5 — qualifying only", "[Exit T20]", "[5,600–6,000 m]", "MGUK power reduction reset"),
    ("C5.12.7 — higher speed threshold", "—", "—", "No event-specific sector listed"),
])}
<p><strong>Square brackets mean SQ/Q-only</strong> in the source; Baku has no
Sprint Qualifying. Preserve those restrictions rather than applying the long
T16-exit exception to the race.</p>
<p><strong>Overtake:</strong> detection gap 1.0 s; detection 4,177 m / L20;
activation 4,270 m <strong>(TBC)</strong> / L21. The circuit map places them
90 m after T16 and 20 m before T17 respectively.</p>
{source(FIA_POWER_UNIT_URL + "#page=2", "FIA Power Unit Information, Articles C5.2.8/C5.2.10/C5.12 and B7.2")}
<h2 class="sec">Parts usage confirmed: Alonso and Stroll exceed their season allocation</h2>
<p>The Technical Delegate's <strong>PU-elements-used report (Document 9, 24 September, 08:30)</strong>
and the follow-up <strong>new-elements report (Document 14, 24 September, 12:34)</strong> confirm
what The Race's watch anticipated, but with different cars than reported: it is
<strong>Aston Martin's Alonso and Stroll</strong>, not Cadillac, who exceed their allocation
for this event.</p>
{content_generic.card("Alonso (car 14) — three elements over allocation",
    content_generic.ul([
        "New internal combustion engine: his <strong>5th</strong> of the 4 allowed for the season.",
        "New turbocharger: his <strong>5th</strong> of the 4 allowed.",
        "New power unit ancillary component: his <strong>9th</strong> of the 6 allowed.",
        "His new exhaust set (2nd of 4) remains within allocation.",
    ]), "bi-exclamation-triangle", "accent")}
{content_generic.card("Stroll (car 18) — four elements over allocation",
    content_generic.ul([
        "New turbocharger: his <strong>6th</strong> of the 4 allowed for the season.",
        "New energy store unit: his <strong>7th</strong> of the 3 allowed.",
        "New control electronics unit: his <strong>6th</strong> of the 3 allowed.",
        "New power unit ancillary component: his <strong>8th</strong> of the 6 allowed.",
    ]), "bi-exclamation-triangle", "accent")}
<p>Lindblad, Ocon and Perez also took new elements this event but each stays
within their season allocation (compliant per Document 14). Formula1.com's own
grid-penalty report explained the regulation: <strong>the first element exceeded at
an event carries a 10-place grid penalty, the second (and each further one) a
further 5 places, cumulative at the same event.</strong> The Stewards have now
issued their own rulings confirming that arithmetic exactly: <strong>Document 20
drops Alonso 25 grid positions</strong> (10 for the first exceeded element, plus
5 each for the second and third — the Stewards' own reasoning credits three
exceeded elements, one more than Formula1.com's article implied) and
<strong>Document 21 drops Stroll 20 places</strong> (5 for each of his four
exceeded elements). Both penalties apply "for the next Race in which the driver
participates" and are subject to Article B2.5.4b.iv grid allocation if the car
is classified in Qualifying — see the automatic tracker below for the Stewards'
own documents.</p>
{source(FIA_PU_NEW_URL + "#page=2", "FIA Document 14, New PU Elements for this Competition, PDF pages 2–4")}
{source(FIA_PU_USED_URL + "#page=2", "FIA Document 9, PU Elements Used per Driver up to now")}
{source(FIA_ALONSO_PENALTY_URL, "FIA Document 20, Infringement — Car 14 — PU Elements, 24 September 2026")}
{source(FIA_STROLL_PENALTY_URL, "FIA Document 21, Infringement — Car 18 — PU Elements, 24 September 2026")}
{source(PENALTY_ARTICLE_URL, "Formula1.com — Alonso and Stroll set for grid penalties, 24 September 2026")}

{content_generic.card("Update, FP3: Alonso takes a fourth exceeded element",
    "<p>The Technical Delegate's <strong>Document 33 (25 September, 12:43)</strong> reports "
    "Alonso's Aston Martin fitted a new energy store unit during FP3 — his <strong>7th of the "
    "3 allowed</strong> for the season, one more element over allocation than Document 14 had "
    "confirmed. The Stewards' <strong>Document 34</strong> imposes a further "
    "<strong>5-place grid drop</strong> for this fourth exceeded element, on top of the "
    "already-confirmed Document 20 penalty. <strong>Alonso's cumulative grid penalty for this "
    "event is now 30 places</strong> (25 + 5), still subject to Article B2.5.4b.iv grid "
    "allocation if the car is classified in Qualifying. Bottas's new exhaust set, also logged in "
    "Document 33, remains within his season allocation.</p>",
    "bi-exclamation-triangle", "accent")}
{source(FIA_ALONSO_FP3_TD_URL + "#page=2", "FIA Document 33, Technical Delegate's Report, PDF page 2, 25 September 2026")}
{source(FIA_ALONSO_FP3_PENALTY_URL, "FIA Document 34, Infringement — Car 14 — PU Element, 25 September 2026")}

{content_generic.card("Race-day update: Verstappen's new PU elements remain compliant",
    "<p>The Technical Delegate's <strong>Document 55 (26 September)</strong> records "
    "new ICE, turbocharger, exhaust and PU ancillary components for Max Verstappen. "
    "They bring his ICE, turbocharger and exhaust use to four of four permitted "
    "elements each, and his PU ancillary components to five of six. The report "
    "marks all four compliant under Article B8.2.2; it does not add a grid penalty.</p>"
    + source(FIA_ROOT + "new_pu_elements_for_this_competition_1.pdf#page=2",
             "FIA Document 55, Technical Delegate's Report, PDF pages 2–3"),
    "bi-info-circle", "accent")}
"""


def team_briefing():
    rows = [
        ("Mercedes", "Kimi Antonelli / George Russell", "Antonelli won Monza and Madrid; Russell is pursuing his teammate. Baku tests whether that recent form survives the long deployment-limited straight.", FORM_URL),
        ("Ferrari", "Charles Leclerc / Lewis Hamilton", "Hamilton's Madrid brake issue is the reliability follow-up; Leclerc's engine evaluation remains a reported plan, not a confirmed Baku grid drop.", TECH_URL),
        ("McLaren", "Lando Norris / Oscar Piastri", "Norris won Hungary and Zandvoort; Piastri needs a response after Madrid. The Race reports the low-drag H-wing's return and another package for evaluation; watch cold fronts/brakes into T1.", TECH_URL),
        ("Red Bull", "Max Verstappen / Isack Hadjar", "Hadjar returns after three missed rounds and has renewed for 2027. He says the wrist will still be painful; do not describe his return as pain-free.", LINEUP_URL),
        ("Racing Bulls", "Liam Lawson / Arvid Lindblad", "Lawson returns from his Red Bull stand-in spell; Tsunoda goes back to reserve. Keep Lawson–Lindblad comparisons separate from the replacement pairings.", F1_ROOT + "hadjar-to-make-racing-return-with-red-bull-at-azerbaijan-gp.1ddPnUSDEze0V9MCiQ9d2U"),
        ("Alpine", "Pierre Gasly / Franco Colapinto", "Madrid narrowed the fight with Racing Bulls for fifth. Follow whether that midfield momentum transfers to Baku rather than extrapolating from the different Madrid layout.", FORM_URL),
        ("Haas", "Esteban Ocon / Oliver Bearman", "Ocon says he is a free agent for 2027 with discussions continuing. Bearman expects to stay, but neither statement is a completed contract announcement; the team seeks an end to its points drought.", OCON_URL),
        ("Audi", "Nico Hulkenberg / Gabriel Bortoleto", "Hulkenberg's Madrid point kept the chase of Haas alive. FIA Document 11 lists 14 Audi component entries for Baku, including a new front wing and nose, floor/diffuser and rear-wing package. Gary Anderson's airflow analysis is an interpretation, not a measured performance gain.", FORM_URL),
        ("Williams", "Carlos Sainz / Alex Albon", "A lighter chassis and delayed FW48 package arrive. Weight reduction is the main target, with smaller balance changes; both drivers caution against treating simulated gains as delivered lap time.", WILLIAMS_URL),
        ("Aston Martin", "Fernando Alonso / Lance Stroll", "The Race reports lighter components rather than another Budapest-scale overhaul. Parts unchanged in appearance may not appear in the aerodynamic submission list.", TECH_URL),
        ("Cadillac", "Valtteri Bottas / Sergio Perez", "Perez is reported to receive the newer Ferrari engine first, alongside small aerodynamic changes. Establish installation and reliability in practice; do not assign Bottas the same specification without evidence.", TECH_URL),
    ]
    qualifying = content_generic.card(
        "Qualifying snapshot — Russell on pole, Antonelli out in Q1",
        "<p>George Russell took pole in 1:42.526, 0.837s ahead of Charles Leclerc, "
        "with Oscar Piastri third. Isack Hadjar qualified fourth, while Kimi "
        "Antonelli was classified 16th after his Turn 1 crash in Q1. The official "
        "Formula1.com starting grid now places Carlos Sainz 14th after his "
        "five-place penalty and Sergio Perez 20th after his three-place penalty.</p>"
        + source("https://www.formula1.com/en/results/2026/races/1295/azerbaijan/qualifying",
                 "Formula1.com official qualifying classification")
        + source("https://www.formula1.com/en/results/2026/races/1295/azerbaijan/starting-grid",
                 "Formula1.com official starting grid"),
        "bi-flag",
        "accent",
    )
    return ('<p class="lead-note">Post-qualifying team context, 25 September. '
            'The preview notes below are retained as background; completed-session '
            'results and penalties take precedence.</p>'
            + qualifying
            + "".join(
                content_generic.card(
                    team + " — " + drivers,
                    f"<p>{text}</p>"
                    + source(url, "23 September preview / driver reporting")
                    + (source(FIA_CAR_PRESENTATION_URL,
                              "FIA Document 11, 24 September 2026")
                       + source(AUDI_UPGRADE_URL,
                                "Gary Anderson, The Race, 25 September 2026")
                       if team == "Audi" else ""),
                    "bi-people",
                )
                for team, drivers, text, url in rows
            ))


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
    standings = pages.get("standings")
    if standings:
        standings["body"] += f"""
<h2 class="sec">Championship permutations</h2>
<p class="lead-note">Dated <strong>post-Madrid, 22 September</strong> scenarios
from Formula1.com's data team, not live championship totals or a race prediction.
The current official tables above take precedence after further racing.
Nine Grands Prix and the Singapore Sprint offered 233 points:
9 × 25 + 8, with <strong>no fastest-lap bonus</strong>.</p>
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
      "both Singapore Sprint and Grand Prix while Russell scores zero. His 375 "
      "would then be 164 clear of Russell, with 150 available after Singapore. "
      "To clinch the title there, <strong>every other rival must also finish "
      "Singapore more than 150 points behind</strong>; Russell scoring zero alone "
      "does not exclude a Hamilton or Norris challenge.</p>"
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

<p><strong>FP1 line-up checked:</strong> all 22 drivers in the official Practice 1
classification match the event's race-entry line-up; no rookie substitute was
listed for the session. This does not turn reserve-driver appearances earlier
in the season into Baku entries.</p>
{source("https://www.formula1.com/en/results/2026/races/1295/azerbaijan/practice/1",
        "Formula1.com Practice 1 classification, 25 September 2026")}

<p class="src">Sources: <a href="https://www.formula1.com/en/latest/article/hadjar-to-make-racing-return-with-red-bull-at-azerbaijan-gp.1ddPnUSDEze0V9MCiQ9d2U" target="_blank" rel="noopener">Formula1.com — Hadjar to make racing return with Red Bull at Azerbaijan GP</a> and
<a href="https://www.the-race.com/formula-1/isack-hadjar-injury-return-where-every-red-bull-f1-driver-stands/" target="_blank" rel="noopener">The Race — Where every Red Bull driver stands as Hadjar returns</a>, both 22 September 2026.</p>
"""
    pages["tyres"]["body"] = f"""
<div class="grid cols-2">
  {content_generic.card(
      "2026 nominated compounds",
      "<p><strong>C3 Hard · C4 Medium · C5 Soft</strong> are the compounds "
      "nominated for this Azerbaijan Grand Prix weekend. <strong>C3 and C4 "
      "are the mandatory race tyres; C5 is the Q3 tyre.</strong></p>"
      "<p>For a dry race, the two-compound requirement includes at least one "
      "mandatory race specification: it does not mean every driver must use "
      "both C3 and C4. A C4/C5 strategy is therefore not ruled out.</p>"
      "<p>This is the published weekend nomination, not a count of each "
      "driver's remaining new or used sets.</p>",
      "bi-record-circle",
      "accent",
  )}
  {content_generic.card(
      "Race-set inventory",
      "<p>The <a href='#race-tyre-availability'>shared inventory above</a> carries "
      "the complete Pirelli race-set chart, its source status and a visually reviewed "
      "new/used table when the transcription matches the current image revision. "
      "These are pre-race sets, not sets remaining after the finish.</p>",
      "bi-table",
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
<p><strong>C3 and C4</strong> are the mandatory race tyres, <strong>not C5</strong>.
Maximum heating is <strong>two hours</strong>, up to <strong>70&deg;C for slicks
and intermediates</strong> and <strong>40&deg;C for wets</strong>.
These are actual tyre tread/sidewall temperatures, not blanket-controller settings.
FIA/Pirelli may revise the prescriptions during the weekend.</p>

<div class="callout"><strong>Post-qualifying tyre evidence:</strong> Pirelli's
comments reproduced by Coffee Corner Motorsport report very low degradation,
no graining on Thursday and strong track evolution. Warm-up, particularly at
the front axle, remains important. Its Friday assessment favours a one-stop
using Medium and Soft, with Hard an alternative after an early neutralisation.
These are attributed engineering observations, <strong>not a per-driver fitted
degradation dataset</strong>; practice classification times cannot supply one.</div>
{source(STRATEGY_URL, "Coffee Corner Motorsport, 25 September: Pirelli Thursday/Friday comments and complete race graphics; reviewed 26 September")}
"""
    pages["tyres"]["body"] += f"""
<h2 class="sec">What Pirelli's complete preview means</h2>
<p>The graphic's <strong>19.5-second average pit-stop loss is a preview estimate</strong>,
not a measured stationary stop or pitlane elapsed time. Its five-point ratings are
traction 5, braking 4, tyre stress 3, asphalt grip 2, abrasion 1, lateral demand 1
and track evolution 5. Low abrasion does not remove the challenge of keeping
front tyres and brakes warm on the long run to T1.</p>
<p>Pirelli expects low degradation and a likely one-stop race, with C5 potentially
capable of long stints and C3 possibly less attractive. Early graining and low grip
can improve as rubber goes down; the resurfaced T2/T3/T4 sections are not expected
by Pirelli to dominate tyre behaviour. These are preview expectations, not practice measurements.</p>
{source(PREVIEW_URL, "Pirelli preview reproduced by Formula1.com, 22 September; full graphic above")}
<h2 class="sec">Published Pirelli strategy windows — 51 laps</h2>
<figure class="circuit-fig">
  <img src="../assets/{STRATEGY_IMAGE}" class="circuit-img"
       alt="Complete Pirelli Baku 2026 possible race strategies: Medium to Soft laps 26 to 32, Soft to Hard laps 16 to 22, Medium to Hard laps 21 to 27; pit-stop loss 19.5 seconds"
       loading="lazy" role="button" tabindex="0" onclick="zoomImg(this)"
       onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();zoomImg(this)}}">
  <figcaption><strong>Pirelli Motorsport — possible race strategies</strong>,
  reproduced by <a href="{STRATEGY_URL}" target="_blank" rel="noopener">Coffee Corner Motorsport,
  25 September 2026</a>. Complete original with compound key and credit.
  <a href="../assets/{STRATEGY_IMAGE}" target="_blank" rel="noopener">Full-resolution graphic</a>;
  click or press Enter to zoom.</figcaption>
</figure>
{table(["Published one-stop route", "Pirelli stop window", "Commentary interpretation"], [
    ("C4 Medium → C5 Soft", "Laps 26–32", "The softer-compound route favoured in Pirelli's post-qualifying assessment; 19–25 laps remain after the stop."),
    ("C5 Soft → C3 Hard", "Laps 16–22", "Earlier switch to a long Hard stint; warm-up and traffic still matter."),
    ("C4 Medium → C3 Hard", "Laps 21–27", "Hard-compound alternative, rather than assuming every car must finish on Soft."),
])}
<p>The windows above are transcribed from the published graphic, replacing the
earlier illustrative planner. The <strong>19.5-second average pit-stop loss</strong>
is Pirelli's estimate, not a measured stationary stop. The graphic shows possible
dry-race strategies, not guarantees of tyre life or instructions for every car.
Weather, neutralisations, traffic and each driver's inventory can change the choice.</p>
<p><strong>Other options:</strong> the accompanying article discusses Soft to Medium
with a laps 18–24 window, but that route/window is <strong>not on Pirelli's
three-route graphic</strong>. Treat it as separately attributed article guidance,
not another line from the chart. An early neutralisation may make Hard attractive;
no fixed stop lap or Safety Car probability is asserted.</p>
{source(STRATEGY_URL, "Coffee Corner Motorsport, 25 September 2026; Pirelli strategy and race-set graphics visually reviewed 26 September")}
<h2 class="sec">What the published set inventory changes</h2>
<p>In the reviewed 25 September race-set chart, <strong>Russell and Antonelli are
the only drivers without a new Medium</strong>: each has one used C4. Russell
has two new Softs and Antonelli four. A Medium-first plan for either Mercedes
therefore starts on a used set; the chart does not state how many laps it has done.</p>
<p><strong>Sainz has no new Soft</strong> and four used C5 sets. Piastri, Norris,
Gasly and Colapinto each have one new Soft; Leclerc, Hamilton, Verstappen and
Hadjar each have two. Bearman has three new Softs. All 22 drivers have one new
Hard, and everyone except the Mercedes pair has one new Medium. See the
revision-checked table above for every new/used count; these are options, not
confirmed starting-tyre choices.</p>
"""
    pages["powerunit"]["title"] = "Power Unit & Overtake"
    pages["powerunit"]["sub"] = "Baku recharge limits, power curves, sector exceptions and the separate Overtake aid."
    pages["powerunit"]["body"] = powerunit_briefing()
    # The generic DRS-era stat/callout must not contradict the reviewed 2026 map.
    pages["circuit"]["body"] = pages["circuit"]["body"].replace("Overtaking zones", "Straight Mode zones")
    pages["circuit"]["body"] = pages["circuit"]["body"].replace("DRS / straight mode", "Active aero · not Overtake")
    pages["circuit"]["body"] = pages["circuit"]["body"].replace(
        "Race-control specifics — track limits, pit-entry definitions and the marked overtaking\n"
        "  zones — are confirmed in the FIA event documents published on the Thursday of the\n"
        "  race week; see Commentary Notes for the link.",
        "The 23 September FIA notes and maps are interpreted below; do not confuse\n"
        "  Straight Mode activation with the separate Overtake detection/activation.")
    pages["circuit"]["body"] += circuit_briefing()
    pages["teams"]["body"] = team_briefing()
    pages["rookies"]["body"] += f"""
{content_generic.card("Hadjar's return is not a pain-free recovery",
    "<p>The Frenchman says the small wrist fracture did not need surgery and his simulator test went well, "
    "but expects discomfort to continue. His Red Bull contract now runs through 2027. "
    "Watch confidence under Baku braking loads, not an invented medical diagnosis.</p>"
    + source(LINEUP_URL, "Formula1.com, Hadjar's own account, 23 September"), "bi-person-badge")}
{content_generic.card("Arvid Lindblad — the 2026 debutant",
    "<p>Racing Bulls' British rookie progressed through Red Bull's junior programme and became "
    "the youngest race winner in both F3 and F2. He had two Red Bull FP1 outings in 2025. "
    "This season's rookie status is not the same as eligibility for a mandatory rookie FP1 slot "
    "after more than two Grand Prix starts.</p>"
    + source("https://www.formula1.com/en/drivers/arvid-lindblad", "Formula1.com driver biography"), "bi-person-badge")}
<p>The FIA's published <strong>entry list (Document 12, 24 September, 10:15)</strong>
confirms all 22 cars with Hadjar back at Red Bull (car 6) and Lawson at Racing
Bulls (car 30); there is still no separate FP1 rookie-substitution notice in the
listing. The race pairings on <a href="teams.html">Team Watch</a> follow this
confirmed entry list; the 23-driver season standings include reserve/replacement
appearances and must not be used as a 23-car Baku entry list.</p>
{source(FIA_ROOT + "entry_list.pdf", "FIA Document 12, Entry List, 24 September 2026")}
"""
    pages["upgrades"]["body"] = f"""
<h2 class="sec">FIA car-presentation submissions (Document 11) — six of eleven teams filed updates</h2>
<p>The FIA Media Delegate's <strong>24 September, 09:50</strong> filing collates each team's own
declared bodywork/aerodynamic component changes for this event. <strong>Mercedes, Ferrari,
Aston Martin, Haas and Alpine submitted no updates</strong> for Baku; the following six did.</p>
<div class="grid cols-2">
{content_generic.card("McLaren — new bodywork package (8 components)",
    content_generic.ul([
        "Revised sidepod inlet shape, engine cover/coke line and an alternative sidepod shape, all for improved flow conditioning.",
        "New cooling-louvre layout to suit the bodywork; revised floor edge and diffuser for more local load.",
        "Revised rear-suspension fairings and an alternative straight-line-mode rear-wing flap position for a larger drag reduction.",
    ]), "bi-tools", "accent")}
{content_generic.card("Red Bull — floor, sidepod and cooling revisions (5 components)",
    content_generic.ul([
        "Revised floor and diffuser geometry for more local load while maintaining flow stability.",
        "New floor/sidepod split line and revised cooling louvres and mirror geometry.",
        "Revised halo-fairing turning vane for downstream flow conditioning.",
    ]), "bi-tools")}
{content_generic.card("Williams — the reported FW48 floor package, now filed (5 components)",
    content_generic.ul([
        "Updated floor bodywork assembly: new leading-edge devices, floor body and floor-corner geometry for more local and underfloor load.",
        "Revised tail geometry to suit the new floor; reprofiled front brake-duct flow conditioning.",
        "Revised rear-suspension cladding orientation and modified rear brake-duct furniture.",
        "This confirms the delayed package Albon and Sainz previewed as a floor/balance update, now with FIA-declared geometry.",
    ]), "bi-tools", "accent")}
{content_generic.card("Racing Bulls — new front wing and corner package (3 components)",
    content_generic.ul([
        "New front-wing assembly for a cleaner flow field feeding the rest of the car.",
        "New brake duct and front lip, plus profile changes to the front-suspension legs.",
    ]), "bi-tools")}
{content_generic.card("Audi — full new front wing, floor and rear-wing package (14 listed components)",
    content_generic.ul([
        "Full new front wing and nose fairing, with revised front-suspension covers to match.",
        "New floor body, leading-edge devices and diffuser \u2014 all new surfaces for a consistent load increase.",
        "New bodywork/halo fairing, rear-suspension covers/brake-duct furniture and a new rear-wing/beam-wing assembly.",
    ]), "bi-tools")}
{content_generic.card("Cadillac — front-corner and diffuser refinements (3 components)",
    content_generic.ul([
        "Updated brake-cooling inlet/exit duct profiles and matching front-suspension fairing surfaces.",
        "Revised diffuser winglet lower-edge geometry for more local load.",
    ]), "bi-tools")}
</div>
{source(FIA_CAR_PRESENTATION_URL, "FIA Document 11, Car Presentation Submissions, 24 September 2026")}
<h2 class="sec">Parc Fermé component replacements (Document 57)</h2>
<p>The Technical Delegate's <strong>26 September report</strong> lists parts
replaced or changed during Parc Fermé on the previous day and race morning.
Every listed replacement was approved after a written team request under
Article B3.5.4. This compliance report is separate from the upgrade declarations
above and is not, by itself, evidence of a defect or reliability failure.</p>
{content_generic.ul([
    "<strong>Mercedes, Car 12 (Antonelli):</strong> front suspension, brake caliper and friction material, steering column and rack, forward plank section, front brake duct, and front-wing/nosebox assembly.",
    "<strong>Red Bull, Car 03 (Verstappen):</strong> left- and right-hand fuel lift-pump assemblies plus new ICE, turbocharger, exhaust and PU ancillary components; the separate Document 55 report records those PU elements as compliant.",
    "<strong>Racing Bulls, Car 41 (Lindblad):</strong> previously used ICE, turbocharger and exhaust reinstalled with associated parameter changes, plus a new right-hand cooling radiator.",
    "<strong>Audi, Car 27 (Hulkenberg):</strong> gearbox assembly and control hydraulics, BBW and rear-brake friction material, with associated parameter changes and gearbox-oil heat-exchanger fittings and hoses.",
])}
{source(FIA_ROOT + "parts_and_parameters_been_replaced_and_or_changed_during_parc_ferme.pdf",
        "FIA Document 57, Technical Delegate's Report, 26 September 2026, PDF pages 1–3")}
<h2 class="sec">Published development reporting, cross-checked against the filing</h2>
{content_generic.card("Audi's Baku package: Gary Anderson's technical analysis",
    "<p>The Race's 25 September visual analysis describes changes across the front wing, "
    "sidepods and cooling outlets, floor/diffuser, suspension and rear wing. Its expected "
    "airflow effects are technical interpretation, not measured lap-time gains or an "
    "official team performance claim.</p>"
    + source(AUDI_UPGRADE_URL, "Gary Anderson, The Race, 25 September 2026"),
    "bi-tools")}
{content_generic.card("Williams: lighter FW48 chassis and balance work",
    "<p>The delayed Baku package centres on weight reduction with smaller changes intended to help balance. "
    "Albon and Sainz both caution that a paper or simulator gain is not automatically delivered on track. "
    "The Race reports a new manufacturing approach, but its detailed method has not been disclosed. "
    "Document 11 above now confirms this is a floor/tail/corner package, not merely a chassis change.</p>"
    + source(WILLIAMS_URL, "Formula1.com, 23 September")
    + source(TECH_URL, "The Race technical preview, 23 September"), "bi-tools", "accent")}
<p>The same technical preview reports McLaren's low-drag H-wing return plus further
evaluation parts (matching Document 11's rear-wing/bodywork entries above), lighter
Aston Martin components (Aston Martin filed no Document 11 update this event), and
small Cadillac aero changes (matching the front-corner/diffuser entries above).
Where the attributed press report and the FIA filing disagree in scope, the FIA
document is the declared component list; the press report is context on intent.</p>
{source(TECH_URL, "The Race, six Baku technical talking points")}
<h2 class="sec">Car display is Thursday, not the usual Friday</h2>
<p>The FIA procedure schedules <strong>Thursday 24 September, 11:00–12:00 Baku /
10:00–11:00 Tallinn</strong>. One car per team is displayed at its pit-stop position,
the other available in the garage. If only one carries the new major aero/bodywork
components, that is the car to display. Adverse-weather arrangements may move the
display into the garage. Still photographers stay in the fast lane; TV crews may
film in the working lane.</p>
{source(FIA_DISPLAY_URL + "#page=2", "FIA car display procedure, 23 September, PDF page 2")}
"""
    pages["moments"]["body"] = f"""
<p class="lead-note">Ten years since the 2016 debut, not ten completed races:
before this weekend Baku hosted nine Grands Prix, including the 2016 European GP;
there was no 2020 edition. 2026 is scheduled as the tenth Baku race and ninth
Azerbaijan GP. The sourced historical record book is on <a href="facts.html">Facts</a>.</p>
<div class="grid cols-2">
{content_generic.card("2017 — Ricciardo wins the chaos", "<p>A three-car braking move into T1 helped Ricciardo recover from an early stop. Vettel's penalty after contact with Hamilton and Hamilton's loose headrest transformed the lead battle.</p>", "bi-stars")}
{content_generic.card("2018 — teammates collide, Bottas loses out", "<p>Ricciardo and Verstappen eliminated each other at T1. Later, Bottas's puncture while leading left Hamilton to win. Neither incident establishes a probability for this year's strategy.</p>", "bi-stars")}
{content_generic.card("2019 — the castle catches Leclerc", "<p>Leclerc crashed at T8 in Q2. He later took four consecutive Baku poles in 2021–2024, but qualifying success and a race win remain different records.</p>", "bi-stars")}
{content_generic.card("2021 — a two-lap restart changes everything", "<p>Verstappen's tyre failure brought a red flag; Hamilton then ran wide at the restart with the wrong brake setting. Perez took the victory. These are historical events, not diagnoses of the 2026 tyres.</p>", "bi-stars")}
{content_generic.card("2024 — a late podium fight ends in the wall", "<p>Perez and Sainz collided after T2 on the penultimate lap while fighting around Leclerc. Piastri won the Grand Prix.</p>", "bi-stars")}
{content_generic.card("2025 — six qualifying red flags", "<p>Albon, Hulkenberg and Colapinto triggered stoppages in Q1, Bearman in Q2, then Leclerc and Piastri in Q3. Piastri's difficult weekend continued with an opening-lap race exit.</p>", "bi-stars")}
</div>
{source(MOMENTS_URL, "Formula1.com historical retrospective, 21 September 2026")}
"""
    pages["reliability"]["body"] = content_generic.card(
        "Carry-over watch, not a Baku outcome",
        "<p>Hamilton retired in Madrid with a reported brake issue. The Race also highlights "
        "front tyre/brake cooling into Baku T1 and Cadillac's reported Perez engine installation. "
        "The Grand Prix has not run yet, so race retirements, race fastest lap and pit-stop "
        "outcomes remain pending; the automatic tables below are authoritative as results publish.</p>"
        + source(FORM_URL, "Formula1.com pre-weekend form")
        + source(TECH_URL, "The Race technical preview"), "bi-tools"
    ) + pages["reliability"]["body"]
    brief = f"""
<div class="callout"><strong>25 September post-qualifying update:</strong> standard
Thursday–Saturday weekend, not a Sprint. FP1–FP3 and Qualifying are complete;
the race is Saturday 26 September at
<strong>15:00 Baku / 14:00 Tallinn</strong>. See <a href="results.html">Results</a>
for the session classifications and published starting grid, and
<a href="penalties.html">Penalties</a> for the confirmed qualifying rulings.
The official starting grid is now available from Formula1.com.</div>
<div class="callout"><strong>26 September race-day tyre update:</strong> the
Pirelli race-set chart and all 22 new/used rows are now reviewed. Its published
one-stop windows are Medium–Soft laps 26–32, Soft–Hard 16–22 and Medium–Hard
21–27. The Mercedes pair have no new Medium; Antonelli has four new Softs,
Russell two, and Sainz none. <a href="tyres.html">Full charts, inventory and
source-backed strategy guidance</a>; these are not confirmed starting tyres.</div>
{content_generic.card("The verified essentials",
    content_generic.ul([
        "Hadjar returns to Red Bull; Lawson returns to Racing Bulls; Tsunoda reverts to reserve. Hadjar expects some wrist pain and has renewed for 2027.",
        "C3 Hard / C4 Medium / C5 Soft; mandatory race tyres are C3/C4. Slick/intermediate maximum heating 70°C; wet 40°C, all for no more than two hours.",
        "Two Straight Mode zones, but one Overtake detection/activation pair. Low-grip A1 starts after T20, later than normal A1 after T19.",
        "Recharge: race 8.5/9.0 MJ with Overtake off/on; qualifying 8.5 MJ, FP/outlaps 9.0 MJ. L21 activation remains 4,270 m (TBC).",
        "Russell took pole in 1:42.526, 0.837s clear of Leclerc; Piastri was third. Antonelli was classified 16th after his Q1 Turn 1 crash. See the official qualifying classification for all 22.",
        "The official starting grid lists Sainz 14th after a five-place drop and Perez 20th after a three-place drop; the separate sanctions are confirmed in FIA Documents 49 and 48.",
        "Alonso's cumulative grid penalty for this event is now <strong>30 places</strong>: the confirmed 25-place Document 20 ruling plus a further 5 places (Document 34) for a fourth exceeded PU element found during FP3. Stroll's 20-place Document 21 penalty is unchanged.",
        "Six of eleven teams (McLaren, Red Bull, Williams, Racing Bulls, Audi, Cadillac) filed FIA car-presentation updates \u2014 Williams' package confirms the reported FW48 floor work. Car display was Thursday 11:00–12:00 Baku.",
        "SC2–SC1 maximum time confirmed post-FP2 (Doc 27): 2:08.0 between the Safety Car lines.",
        "Race-day Documents 55 and 57: Verstappen's new PU elements are within allocation; the Parc Fermé report lists the major approved component replacements, separately from declared upgrades.",
        "The Turn 19 FP2 impeding incident is resolved: Document 29 gives Hamilton (Car 44) a driving reprimand for impeding Lawson's Car 30; no separate ruling was published against Lawson's own summons.",
    ]) + '<p><a href="rookies.html">Line-up sources</a> · <a href="tyres.html">Pirelli/FIA prescriptions</a> · '
    '<a href="circuit.html">Map and race-control interpretation</a> · <a href="powerunit.html">PU sheet</a> · '
    '<a href="upgrades.html">Development sources</a></p>', "bi-mic", "accent")}
"""
    st = ctx.get("standings") or {}
    live_standings = (
        f'<div class="callout"><strong>Current championship:</strong> {st.get("summary", "Official update pending")} '
        f'<a href="standings.html">Both tables and source freshness</a> ({st.get("as_of", "unavailable")}).</div>'
    )
    pages["overview"]["body"] = brief + live_standings + pages["overview"]["body"]
    race_available = any(
        block.get("label") == "Race" for block in (ctx.get("results") or [])
    )
    if race_available:
        session_status = (
            "<p><strong>Session-by-session status:</strong> the official Race "
            "classification is published. See <a href=\"results.html\">Results</a> "
            "for the source-linked table and <a href=\"news.html\">Weekend News</a> "
            "for post-race reports.</p>"
        )
    else:
        session_status = (
            "<p><strong>Session-by-session status:</strong> official Practice 1, "
            "Practice 2, Practice 3 and Qualifying classifications are published. "
            "The Race classification remains pending until the official result is "
            "available. See <a href=\"results.html\">Results</a> for source-linked "
            "tables and <a href=\"news.html\">Weekend News</a> for the latest reports.</p>"
        )
    notes_body = pages["notes"]["body"].replace(
        content_generic.pending(
            "Session-by-session commentary notes", "as the weekend runs", "bi-mic"
        ),
        session_status,
    )
    pages["notes"]["body"] = brief + live_standings + notes_body
    pages["schedule"]["body"] += f"""
<p><strong>Calendar check:</strong> the Saturday race moves practice to Thursday
and qualifying to Friday. Baku is UTC+4 and Tallinn is EEST (UTC+3), so Tallinn
is one hour earlier throughout this weekend. The session table is calendar-driven.</p>
<p><strong>Heat Hazard:</strong> no declaration was identified in the 50-PDF FIA
event listing checked after Qualifying on 25 September. A weather forecast
alone is not a declaration; do not infer mandatory cooling measures from temperature.</p>
{source(FORM_URL, "Formula1.com weekend schedule; FIA listing for declarations")}
<p>The FIA's <strong>Competition Visa V2 (Document 7, 23 September, 19:08)</strong>
contains Appendix B3 version 3 and timetable version 3. These independently
confirm all five F1 session starts in the table. Saturday's listed 15:00 start
is the formation-lap start; its 17:00 finish is approximate, not a promise
that the race runs for two hours.</p>
{source(FIA_VISA_URL + "#page=7", "FIA visa timetable, PDF pages 7–9")}
<p><strong>Parc fermé cover-on note (Document 44):</strong> the Race Director's
25 September, 17:23 note reminds all teams that every qualifying car must be
covered and ready for FIA seals by 19:04, under Article B3.4.3a. This is a
routine procedural reminder, not a new sporting decision.</p>
{source(FIA_ROOT + "covers-on_time.pdf", "FIA Document 44, Note to Teams, 25 September 2026")}
<p><strong>Curfew exceptions (Document 32):</strong> the Technical Delegate's
25 September report notes Ferrari used its second of four permitted curfew
exceptions (overnight personnel in the paddock, 24–25 September) and Racing
Bulls/Cadillac each used their third of four; no action was required in either
case. This is a routine compliance record, not a Baku-specific reliability or
sporting concern.</p>
{source(FIA_ROOT + "curfew_amended.pdf", "FIA Document 32, Technical Delegate's Report, 25 September 2026")}
"""
    pages["penalties"] = dict(
        kicker="Stewards & race control", title="Penalties & Decisions",
        sub="Alonso's cumulative grid penalty is 30 places (Docs 20+34), Stroll's is 20 (Doc 21), Sainz drops five places (Doc 49) and Perez three (Doc 48); the official starting grid is published.",
        body=f1lib.render_penalties(
            ctx,
            decisions=[
                dict(doc="Doc 22", no="44", driver="Lewis Hamilton", team="Scuderia Ferrari HP",
                     session="Free Practice 2",
                     fact="Summoned to appear before the Stewards at 17:30 over an alleged breach of "
                          "Article B4.1.1 of the FIA F1 Regulations — Car 44 allegedly impeding Car 30 "
                          "at Turn 19, 16:33.",
                     outcome="Superseded by Document 29 below — the Stewards found Hamilton at fault "
                             "and issued a driving reprimand.",
                     kind="note", source_url=FIA_HAMILTON_SUMMONS_URL),
                dict(doc="Doc 23", no="30", driver="Liam Lawson", team="Visa Cash App Racing Bulls F1 Team",
                     session="Free Practice 2",
                     fact="Summoned to appear before the Stewards at 17:30 over an alleged breach of "
                          "Article 27 of the Race Director's Competition Notes (V2) and/or Article "
                          "B4.1.1 — the counterpart summons to Car 44's, same Turn 19 incident.",
                     outcome="No separate ruling document for Car 30 has appeared in the FIA listing — "
                             "only Document 29 (Car 44) was published. Treat Lawson's own summons as "
                             "resolved without a further sanction pending a document that says otherwise, "
                             "not confirmed dismissed by name.",
                     kind="note", source_url=FIA_LAWSON_SUMMONS_URL),
                dict(doc="Doc 48", no="11", driver="Sergio Perez", team="Cadillac Formula 1 Team",
                     session="Qualifying",
                     fact="Car 11 drove at reduced speed on the racing line through Turns 18, 19 and 20, "
                          "forcing Oscar Piastri to lift on a flying lap after two radio warnings.",
                     outcome="Three-place grid penalty for the next Sprint/Race. Formula1.com's "
                             "published starting grid lists Perez 20th after the separate Aston Martin "
                             "engine penalties.",
                     kind="penalty",
                     source_url=FIA_ROOT + "infringement_-_car_11_-_impeding_car_81.pdf"),
                dict(doc="Doc 49", no="55", driver="Carlos Sainz", team="Atlassian Williams F1 Team",
                     session="Qualifying",
                     fact="The Stewards found Sainz failed to reduce speed under the single yellow in "
                          "Marshalling Sector 4 despite the visible signal and a team warning.",
                     outcome="Five-place grid penalty and two penalty points (four in the preceding "
                             "12 months). Formula1.com's published starting grid lists Sainz 14th.",
                     kind="penalty",
                     source_url=FIA_ROOT + "infringement_-_car_55_-_failure_to_slow_for_yellow_flags_0.pdf"),
            ],
            intro_html=f"""
<div class="callout accent"><strong>Four driver-specific grid sanctions now shape the published starting order.</strong>
Document 20 dropped <strong>Alonso 25 grid places</strong> and Document 21 drops
<strong>Stroll 20 grid places</strong>, both "for the next Race in which the driver
participates" and both matching the cumulative arithmetic reported before the
rulings — see <a href="powerunit.html">Power Unit &amp; Overtake</a> for the
component-by-component breakdown. A fourth exceeded PU element found during FP3
(a new energy store unit) brought <strong>Document 34</strong>, a further
<strong>5-place drop</strong>: <strong>Alonso's cumulative grid penalty for this
event is now 30 places.</strong> Separately, <strong>Bottas's yellow-flag summons
(Document 15) has been resolved with no penalty</strong> (Document 19): the
Stewards found the overtake could not reasonably have been avoided once the flag
was shown. <strong>The Turn 19 impeding incident is now also resolved: Document 29
gives Hamilton (Car 44) a driving reprimand</strong> for impeding Lawson's Car 30 —
his counterpart summons (Document 23) has no separate published ruling, so treat
Lawson's own case as closed without further sanction rather than confirmed
dismissed by name. After Qualifying, <strong>Document 48 gives Perez a
three-place penalty</strong> for impeding Piastri, and <strong>Document 49 drops
Sainz five places and adds two penalty points</strong> for failing to slow under
a yellow flag. The official Formula1.com starting grid lists Sainz 14th, Perez
20th, Alonso 21st and Stroll 22nd; these are source-published grid positions,
not a hand-calculated order.</div>
"""))
    pages["penalties"]["body"] += f"""
<h2 class="sec">Officials and document status</h2>
<p><strong>Competition Visa V2, Document 7:</strong> FIA stewards Gerd Ennser,
Loïc Bacquelaine, Khatuna Julakidze and Derek Warwick; ASN-appointed steward
Danil Solomin. Race Director and Safety Delegate Rui Marques; Technical Delegate
Jo Bauer; Sporting Delegate Tim Malyon; Deputy Race Director Paul Burns.
The visa names the officials; it is not an infringement decision.</p>
{source(FIA_VISA_URL + "#page=4", "FIA Competition Visa V2, Appendix B3, PDF pages 4–5")}
<p>The FIA event listing contained <strong>50 PDFs after Qualifying</strong>,
including the provisional starting grid, final qualifying classification,
post-qualifying procedure, scrutineering, lap-time deletions and the new
Qualifying decisions. <strong>Document 48</strong> penalises Perez for impeding
Piastri; <strong>Document 49</strong> penalises Sainz for failing to slow under
a yellow flag. Their complete FIA pages and original-PDF links are attached to
the same sortable decision rows above. Formula1.com's starting-grid table is
available; no separate final-grid PDF was present in this FIA listing at refresh.</p>
{source(FIA_HAMILTON_IMPEDING_RULING_URL, "FIA Document 29, Infringement — Car 44 — Impeding Car 30, 24 September 2026")}
{source(FIA_ALONSO_FP3_PENALTY_URL, "FIA Document 34, Infringement — Car 14 — PU Element, 25 September 2026")}
{source(FIA_ROOT + "infringement_-_car_11_-_impeding_car_81.pdf", "FIA Document 48, Infringement — Car 11 — Impeding Car 81, 25 September 2026")}
{source(FIA_ROOT + "infringement_-_car_55_-_failure_to_slow_for_yellow_flags_0.pdf", "FIA Document 49, Infringement — Car 55 — Failure to Slow for Yellow Flags, 25 September 2026")}
<p>Document 2 clears the inspected front-suspension items on Russell's Madrid
car; it is a compliance report, not a Baku sanction.
See <a href="reliability.html">Reliability</a> for its scope and
<a href="circuit.html">Circuit</a> for the race-control instructions.</p>
"""
    return pages
