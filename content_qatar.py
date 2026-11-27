"""Verified carry-over information; local Qatar documents remain source-dependent."""
import content_generic
from content_las_vegas import (
    FINAL_CLASSIFICATION,
    HAMILTON_TRACK_LIMITS,
    LECLERC_PENALTY_REPORT,
    PEREZ_PENALTY,
)
from f1lib import auto_news, card, news_page_subtitle, render_penalties
from upgrade_render import render_submissions


PIRELLI_NOMINATION = "https://press.pirelli.com/tyre-compounds-selected-for-the-final-three-races-of-the-season/"
PIRELLI_TYRE_LIMIT = "https://press.pirelli.com/in-qatar-with-the-hardest-tyre-compounds-in-the-range/"
QATAR_TYRE_LIMIT = (
    "https://www.motorsport.com/f1/news/pirelli-introduces-stint-limit-for-f1-qatar-gp-but-increases-total-from-2025/10875950/"
)
QATAR_TYRE_ALLOCATION = (
    "https://www.formula1.com/en/latest/article/"
    "what-tyres-will-the-formula-1-teams-and-drivers-have-for-the-2026-qatar-grand-prix."
    "7JllCRweDY5sW1N9LzdkLm"
)
QATAR_TYRE_LIMIT_EXPLAINER = (
    "https://www.formula1.com/en/latest/article/"
    "explained-why-theres-a-27-lap-limit-on-tyres-for-the-qatar-grand-prix."
    "4oeu38BqJh1h7llxUeILBe"
)
QATAR_TYRE_STRATEGY = "https://coffeecornermotorsport.com/qatar-grand-prix-2026-tyre-preview/"
QATAR_TYRE_COUNTING = "https://coffeecornermotorsport.com/qatar-grand-prix-tyre-limit-2026/"
QATAR_TRACK_MAP = "https://media.formula1.com/image/upload/f_auto/q_auto/v1751632421/common/f1/2026/track/2026tracklusaildetailed.png"
QATAR_TIMETABLE = "https://www.formula1.com/en/latest/article/formula-1-qatar-airways-qatar-grand-prix-2026.3XJyoYSnpJEcuZovstTdcG"
QATAR_TYRE_PREVIEW = "pirelli-qatar-2026-preview.jpg"
QATAR_2025_RACE = (
    "https://www.formula1.com/en/latest/article/"
    "verstappen-wins-qatar-gp-as-title-battle-goes-to-abu-dhabi-with-piastri."
    "5KlYT7q8OcrJ7AnMALjkxJ"
)
QATAR_2021_PUNCTURES = (
    "https://www.formula1.com/en/latest/article/"
    "pirelli-boss-isola-explains-qatar-tyre-issues-that-saw-bottas-russell-and."
    "10WNRRptmywRBmvNRL7Wb4"
)
QATAR_2021_NORRIS_PUNCTURE = (
    "https://www.formula1.com/en/latest/article/"
    "we-should-have-outscored-ferrari-says-norris-after-late-tyre-issue-costs-him."
    "5mtdD6imPkZUAQADtWbkUx"
)
QATAR_2021_PIRELLI_FINDINGS = (
    "https://www.formula1.com/en/latest/article/"
    "pirelli-share-initial-findings-from-qatar-grand-prix-tyre-issue."
    "4a7a2sny3wCTCW6exjhnnP"
)
QATAR_2023_TYRE_LIMIT = (
    "https://www.motorsport.com/f1/news/"
    "fia-mandates-maximum-18-lap-stints-in-qatar-gp-due-to-tyre-issues/10530448/"
)
QATAR_2024_TYRE_FAILURES = (
    "https://www.the-race.com/formula-1/"
    "what-pirelli-told-f1-teams-lewis-hamilton-carlos-sainz-qatar-failures/"
)
QATAR_2025_HADJAR_PUNCTURE = (
    "https://www.formula1.com/en/video/"
    "the-front-wing-broke-hadjar-explains-his-late-puncture-in-qatar.1850238257586160104"
)
CAMARA_QATAR_ANNOUNCEMENT = (
    "https://www.formula1.com/en/latest/article/"
    "haas-confirm-camara-will-drive-for-the-team-in-final-races-of-2026."
    "2wYY9ymhyqr7rXcuK6S7bj"
)
QATAR_FP1_ANNOUNCEMENT = "https://x.com/AstonMartinF1/status/2125575387375948173"
QATAR_RACE_WEEK_STORYLINES = (
    "https://www.formula1.com/en/latest/article/"
    "its-race-week-5-storylines-were-excited-about-ahead-of-the-2026-qatar-grand-prix."
    "1bXINUYO8R8X3K7DjINr1A"
)
QATAR_RUSSELL_VERSTAPPEN_FOLLOWUP = (
    "https://www.formula1.com/en/latest/article/"
    "it-was-quite-amusing-russell-shares-his-reaction-to-verstappens-las-vegas-comments."
    "6sv6Xkop4lBcCxge8ZgxXv"
)
QATAR_FERRARI_FOLLOWUP = (
    "https://www.formula1.com/en/latest/article/"
    "were-all-disappointed-leclerc-and-hamilton-address-aftermath-of-las-vegas-clash."
    "34d9bV1J0varyAnDCWPAjU"
)
QATAR_MERCEDES_ENERGY_FOLLOWUP = (
    "https://www.the-race.com/formula-1/"
    "everything-we-learned-on-day-one-of-f1s-2026-qatar-grand-prix/"
)
QATAR_THURSDAY_PRESS_CONFERENCE = (
    "https://www.fia.com/news/f1-2026-qatar-grand-prix-thursday-press-conference-transcript"
)
QATAR_LINDBLAD_FOLLOWUP = (
    "https://www.formula1.com/en/latest/article/"
    "lindblad-left-trying-to-hold-back-tears-after-las-vegas-spin-as-he-reflects-on-"
    "emotional-social-media-post.6eGFigwGZhsbeR31PHHf4j"
)
FERRARI_VASSEUR_REPORT = (
    "https://www.formula1.com/en/latest/article/"
    "its-a-lack-of-respect-vasseur-calls-latest-hamilton-leclerc-clash-in-las-vegas-"
    "unacceptable.5NGehhmEEtLqzDKxm7bi4z"
)
FIA_VEGAS_LECLERC_COLLISION = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_las_vegas_grand_prix_-_infringement_-_car_16_-_causing_a_collision_with_car_44.pdf"
)
BEARMAN_HAAS_SEAT = (
    "https://www.formula1.com/en/latest/article/"
    "bearman-to-continue-with-haas-for-2027-as-he-completes-next-years-grid."
    "dRq9fWh9OGjhXuShgGnqE"
)
HAAS_BEARMAN_ANNOUNCEMENT = (
    "https://www.haasf1team.com/news/"
    "tgr-haas-f1-team-confirms-ollie-bearman-2027-fia-formula-1-world-championship"
)
FIA_QATAR_VISA = "https://www.fia.com/system/files/decision-document/2026_qatar_grand_prix_-_competition_visa.pdf"
FIA_QATAR_POWER_UNIT = "https://www.fia.com/system/files/decision-document/2026_qatar_grand_prix_-_power_unit_information.pdf"
FIA_QATAR_PU_USAGE = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_qatar_grand_prix_-_pu_elements_used_per_driver_up_to_now.pdf"
)
FIA_QATAR_SELF_SCRUTINEERING = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_qatar_grand_prix_-_self_scrutineering.pdf"
)
FIA_QATAR_CURFEW = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_qatar_grand_prix_-_curfew.pdf"
)
FIA_QATAR_TYRE_NOTES = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_qatar_grand_prix_-_competition_notes_-_pirelli_preview_v2.pdf"
)
FIA_QATAR_F1_CIRCUIT_MAP = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_qatar_grand_prix_-_competition_notes_-_circuit_map_pit_lane_drawing_emergency_exits_map_and_red_zone.pdf"
)
FIA_QATAR_F1_CIRCUIT_MAP_IMAGE = (
    "fia-qatar-32198d476fbc-d4e6898c25a3e5e9-p2.png"
)
FIA_QATAR_RACE_DIRECTOR_NOTES = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_qatar_grand_prix_-_race_directors_competition_notes_v2.pdf"
)
FIA_QATAR_SUPPORT_CIRCUIT_MAP = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_lusail_event_-_circuit_map_-_lusail_2026.pdf"
)
FIA_QATAR_CAR_DISPLAY = "https://www.fia.com/system/files/decision-document/2026_qatar_grand_prix_-_car_display_procedure.pdf"
FIA_QATAR_ENTRY_LIST = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_qatar_grand_prix_-_entry_list.pdf"
)
FIA_QATAR_CAR_PRESENTATION = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_qatar_grand_prix_-_car_presentation_submissions.pdf"
)
FIA_QATAR_CAR_PRESENTATION_ASSET = (
    "fia-qatar-7ac412c052cb-259a83f98d072bc8"
)
UPGRADE_SUBMISSIONS = (
    ("McLaren", 2, ()),
    ("Mercedes", 3, ()),
    ("Red Bull Racing", 4, ()),
    ("Ferrari", 5, ()),
    ("Williams", 6, ()),
    ("Racing Bulls", 7, ()),
    ("Aston Martin", 8, ()),
    ("Haas", 9, ()),
    ("Audi", 10, (
        (
            "Front Corner",
            "Performance - Flow Conditioning",
            "The revised lower front brake-duct deflector is described as improving "
            "flow-field quality delivered to the rest of the car.",
        ),
    )),
    ("Alpine", 12, ()),
    ("Cadillac", 13, ()),
)
FIA_QATAR_PEREZ_SUMMONS = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_qatar_grand_prix_-_summons_-_car_11_-_late_attendance_of_the_thursday_press_conference.pdf"
)
FIA_APPEAL_HEARING = "https://www.fia.com/news/international-court-appeal-hearing-november-25-2026"
FIA_ITALY_DOC69 = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_italian_grand_prix_-_decision_-_car_22_-_alleged_start_procedure_infringement.pdf"
)
FIA_VEGAS_DOC66 = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_las_vegas_grand_prix_-_championship_points.pdf"
)
PEREZ_PENALTY_ARTICLE = (
    "https://www.formula1.com/en/latest/article/"
    "perez-hit-with-five-place-penalty-in-qatar-after-camara-clash-during-las-vegas-grand-prix."
    "30GG7oJuJ1As0MrkavmStN"
)
FIA_COST_CAP_REVIEW = (
    "https://www.fia.com/news/"
    "fia-completes-its-review-compliance-2025-fia-formula-1-financial-regulations"
)
FIA_WILLIAMS_ABA = (
    "https://www.fia.com/news/"
    "accepted-breach-agreement-between-williams-grand-prix-engineering-limited-and-fia-breach-fia"
)
FIA_WILLIAMS_ABA_SUMMARY = (
    "https://www.fia.com/sites/default/files/"
    "summary_aba_for_public_disclosure_-_wgpe_0.pdf"
)
FIA_ALPINE_ABA = (
    "https://www.fia.com/news/"
    "accepted-breach-agreement-between-alpine-racing-limited-and-fia-procedural-breach-fia-formula-1"
)
FIA_ALPINE_ABA_SUMMARY = (
    "https://www.fia.com/sites/default/files/"
    "summary_aba_for_public_disclosure_-_alpine_1.pdf"
)
F1_COST_CAP_REPORT = (
    "https://www.formula1.com/en/latest/article/"
    "fia-confirm-williams-minor-overspend-breach-in-2025-cost-cap-review."
    "12rGorQ1pzc6aH0LX2WdLZ"
)


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    upgrade_summary = card(
        "Qatar FIA filing: Audi declares one front-corner update",
        f"""<p>FIA Document 12 lists one declared item across all eleven teams:
Audi's revised lower front brake-duct deflector, filed for performance /
flow conditioning. The description says it improves flow-field quality
delivered to the rest of the car; this is the team's stated rationale, not an
independently measured gain. Ten teams explicitly submitted no updates for
Qatar. Audi's component-location diagram is on page 11.
<a href="{FIA_QATAR_CAR_PRESENTATION}#page=10">Audi declaration, page 10</a> ·
<a href="{FIA_QATAR_CAR_PRESENTATION}#page=11">component diagram, page 11</a> ·
<a href="upgrades.html">Full team-by-team filing and readers</a>.</p>""",
        "bi-tools", "accent",
    )
    circuit = f"""<h2 class="sec">2026 FIA Straight Mode and Overtake points</h2>
<p>The current FIA Formula 1 circuit map (version 1, issued 24 November)
lists separate normal-grip and low-grip Straight Mode activation points:
<strong>A1</strong>, 40 m after Turn 16 / 10 m after Pit Exit (normal) and
100 m after Turn 16 / 10 m after Pit Exit (low grip);
<strong>A2</strong>, 60 m after Turn 3 (normal) and 120 m after Turn 3
(low grip); <strong>A3</strong>, 70 m after Turn 10 (normal) and N/A (low
grip); <strong>A4</strong>, 70 m after Turn 15 (normal) and 110 m after
Turn 15 (low grip). These are Straight Mode points, not electrical Overtake
thresholds.</p>
<p>The separate FIA Overtake system detects at the exit of Turn 16 and
activates 40 m after Turn 16. The FIA power-unit map expresses those same
points as <strong>5,020 m / L24</strong> and
<strong>5,078 m / L25/SC1</strong>, with a 1.0-second detection gap. Loop
labels and lap distances are alternate references for Overtake; they are not
Straight Mode zones. The map shows no separate low-grip-specific Overtake
points.
<a href="{FIA_QATAR_F1_CIRCUIT_MAP}#page=2">FIA Formula 1 circuit map, page 2</a> ·
<a href="{FIA_QATAR_POWER_UNIT}#page=2">FIA Power Unit Information, page 2</a> ·
<a href="{QATAR_TRACK_MAP}">Formula1.com 2026 circuit map</a>.</p>"""
    circuit += f"""<figure class="circuit-fig">
<img class="circuit-img" src="../assets/{FIA_QATAR_F1_CIRCUIT_MAP_IMAGE}"
alt="Official FIA 2026 Formula 1 Qatar circuit map showing the track layout, Straight Mode zones, Overtake points, sectors and marshal posts"
loading="lazy" onclick="zoomImg(this)">
<figcaption>FIA 2026 Qatar Grand Prix circuit map, version 1 issued 24 November 2026,
page 2. <a href="{FIA_QATAR_F1_CIRCUIT_MAP}#page=2">Original FIA PDF, page 2</a>.</figcaption>
</figure>"""
    qatar_fia_map_note = f"""<div class="callout accent"><strong>F1 Overtake:</strong>
detection is at the exit of Turn 16 and activation is 40 m after Turn 16.
The map's separate Straight Mode points are not DRS or Overtake points.
The separately discovered Lusail Event Document 5 is a Formula 2 map
(F2 logo), not the Formula 1 circuit map; its DRS markers do not describe
the 2026 F1 system.
<a href="{FIA_QATAR_F1_CIRCUIT_MAP}#page=2">FIA F1 map</a> ·
<a href="{FIA_QATAR_SUPPORT_CIRCUIT_MAP}#page=2">separate FIA support-series map</a>.</div>"""
    qatar_race_director_note = f"""<div class="callout accent"><strong>FIA Race Director's competition notes, Document 14 V2, 27 November:</strong>
the maximum time between the second and first Safety Car Lines for qualifying
and race reconnaissance laps will be notified after FP2. During the race,
teams receive a lapping pre-warning at 3.0 s; blue panels are shown at 1.2 s,
and the lapped driver must yield at the first opportunity. At Turn 16, a
track-limits infringement invalidates that lap and the immediately following
lap. <a href="{FIA_QATAR_RACE_DIRECTOR_NOTES}#page=2">Race Director's notes, page 2</a> ·
<a href="{FIA_QATAR_RACE_DIRECTOR_NOTES}#page=6">track limits, page 6</a>.</div>"""
    pages["circuit"]["body"] += circuit
    pages["circuit"]["body"] += qatar_race_director_note
    powerunit = f"""<h2 class="sec">Qatar FIA power-and-energy map</h2>
<p>The FIA sheet identifies a <strong>5.419 km</strong> lap, standard format
and 27–29 November. Under Article C5.2.10, maximum recharge per lap is
<strong>8.0 MJ</strong> in the race with Overtake inactive,
<strong>8.5 MJ</strong> in the race with Overtake active,
<strong>6.5 MJ</strong> in qualifying, <strong>8.5 MJ</strong> in free
practice and <strong>9.0 MJ</strong> on out laps other than in the race.
These are recharge limits, not deployment allowances.</p>
<p>Article C5.12.8 sets the power-limited distance at <strong>3,108 m</strong>
and the maximum reduction rate at <strong>100 kW/s</strong>. For Sprint and
Race, the map assigns Base–Standard without Overtake and Base–Overtake with
Overtake in the main zones, with Alt 1 elsewhere; all practice sessions,
including qualifying, use Base–Overtake. This is the FIA's ERS-K power curve,
not an active-aero Straight Mode setting.</p>
<p>Alternative-curve windows under C5.2.8iii are T1–T2 (750–1,050 m),
T4–T10 (1,700–3,100 m) and T12–T14 (3,750–4,150 m). Under C5.12.4, the
350 kW power-reduction exceptions are T1–T2 (750–1,050 m), T4–T6
(1,700–2,150 m), T9–T10 (2,880–3,100 m) and T12–T16 (3,750–4,800 m);
the bracketed Exit T16 window is 4,900–5,300 m. The sheet marks bracketed
windows for Sprint Qualifying and Qualifying; Qatar is a standard-format
weekend, so they do not add a Sprint session.</p>
<p>Reset windows under C5.12.5 are Exit T12 (3,750–4,050 m), Exit T14
(4,150–4,300 m), Exit T15 (4,450–4,650 m) and bracketed Exit T16
(5,050–5,400 m). The higher-speed threshold under C5.12.7 is
<strong>310 km/h</strong> at T12–T14 (3,650–4,200 m). Overtake uses a
<strong>1.0-second</strong> detection gap, with detection at
<strong>5,020 m / L24</strong> and activation at
<strong>5,078 m / L25/SC1</strong>. Distances are lap metres; loop labels are
not turn numbers. See the complete map in the FIA source reader below.
<a href="{FIA_QATAR_POWER_UNIT}#page=2">Original FIA document, page 2</a>.</p>"""
    pending_powerunit = content_generic.pending(
        "The FIA power-unit and energy-map document for this event",
        "with the event documents in the race week",
    )
    powerunit_body = pages["powerunit"]["body"]
    generic_curve_copy = (
        "Practice and qualifying generally run a more permissive power curve than the race — "
        "expect Sunday straight-line speed to look weaker than Saturday's."
    )
    generic_document_copy = "that is where the numbers below come from once it is issued."
    if (
        pending_powerunit not in powerunit_body
        or generic_curve_copy not in powerunit_body
        or generic_document_copy not in powerunit_body
    ):
        raise ValueError("Could not locate Qatar's generic power-unit copy")
    pages["powerunit"]["body"] = powerunit_body.replace(
        pending_powerunit, powerunit, 1
    ).replace(
        generic_curve_copy,
        "The FIA map assigns Base–Overtake to practice and qualifying, while the race "
        "uses different curves inside and outside its main Overtake zones; compare "
        "the published curves rather than assuming a Sunday speed penalty.",
        1,
    ).replace(
        generic_document_copy,
        "Qatar's published event map is summarized below.",
        1,
    )
    pages["powerunit"]["body"] += f"""<p><strong>Reported Mercedes energy-management update:</strong>
The Race's 26 November Qatar report says Kimi Antonelli described a safety
feature Mercedes added after his Las Vegas battery-deployment loss, intended
to make the system more robust. This is an attributed team software change,
not a revision to the FIA's published recharge limits or power map, and its
effect at Qatar has not yet been demonstrated.
<a href="{QATAR_MERCEDES_ENERGY_FOLLOWUP}">The Race's Qatar day-one report</a>.</p>"""
    pu_usage = [
        ("81", "McLaren Mercedes", "Oscar Piastri", 5, 4, 3, 2, 3, 3, 6),
        ("01", "McLaren Mercedes", "Lando Norris", 4, 4, 4, 2, 3, 4, 6),
        ("63", "Mercedes", "George Russell", 6, 5, 5, 4, 4, 4, 6),
        ("12", "Mercedes", "Kimi Antonelli", 6, 4, 4, 2, 4, 4, 6),
        ("03", "Red Bull Racing RB Ford", "Max Verstappen", 5, 5, 5, 3, 3, 3, 6),
        ("06", "Red Bull Racing RB Ford", "Isack Hadjar", 8, 7, 7, 4, 4, 4, 8),
        ("16", "Ferrari", "Charles Leclerc", 5, 4, 4, 3, 3, 3, 6),
        ("44", "Ferrari", "Lewis Hamilton", 6, 5, 5, 4, 4, 4, 7),
        ("23", "Atlassian Williams Mercedes", "Alexander Albon", 5, 4, 4, 2, 3, 4, 5),
        ("55", "Atlassian Williams Mercedes", "Carlos Sainz", 4, 5, 4, 2, 3, 4, 5),
        ("41", "Racing Bulls RB Ford", "Arvid Lindblad", 7, 6, 5, 2, 3, 3, 6),
        ("30", "Racing Bulls RB Ford", "Liam Lawson", 5, 5, 5, 2, 3, 3, 7),
        ("18", "Aston Martin Aramco Honda", "Lance Stroll", 6, 7, 3, 5, 9, 8, 9),
        ("14", "Aston Martin Aramco Honda", "Fernando Alonso", 5, 6, 4, 5, 7, 6, 9),
        ("51", "Haas Ferrari", "Rafael Câmara", 4, 4, 4, 3, 3, 3, 6),
        ("87", "Haas Ferrari", "Oliver Bearman", 5, 5, 5, 5, 4, 4, 5),
        ("27", "Audi", "Nico Hülkenberg", 4, 4, 4, 3, 3, 3, 5),
        ("05", "Audi", "Gabriel Bortoleto", 5, 5, 5, 4, 6, 6, 7),
        ("10", "Alpine Mercedes", "Pierre Gasly", 4, 4, 4, 2, 3, 3, 5),
        ("43", "Alpine Mercedes", "Franco Colapinto", 5, 4, 3, 2, 3, 4, 5),
        ("11", "Cadillac Ferrari", "Sergio Perez", 5, 5, 4, 4, 3, 3, 5),
        ("77", "Cadillac Ferrari", "Valtteri Bottas", 5, 5, 4, 4, 4, 4, 5),
    ]
    pu_usage_rows = "".join(
        "<tr>"
        f'<td class="num">{number}</td><td class="team">{team}</td>'
        f'<td class="drv">{driver}</td>'
        + "".join(f'<td class="num">{count}</td>' for count in counts)
        + "</tr>"
        for number, team, driver, *counts in pu_usage
    )
    pages["powerunit"]["body"] += f"""<h2 class="sec" id="qatar-pu-usage">PU elements used before Qatar running</h2>
<p>FIA Technical Delegate Document 8, published on 27 November before the
weekend's first practice, lists the power-unit elements each of the 22 drivers
has used so far this season. These are season-to-date counts, not Qatar-specific
allocations or penalty decisions; any sanction is reported separately by the
stewards.</p>
<div class="table-wrap"><table class="data compact">
<thead><tr><th>No.</th><th>Constructor</th><th>Driver</th><th>ICE</th><th>TC</th>
<th>EXH</th><th>MGU-K</th><th>ES</th><th>PU-CE</th><th>PU-ANC</th></tr></thead>
<tbody>{pu_usage_rows}</tbody></table></div>
<p>Counts are transcribed from the exact-hash, visually reviewed FIA report.
<a href="{FIA_QATAR_PU_USAGE}#page=2">Document 8, page 2</a>.</p>"""
    carryover = f"""<h2 class="sec">Verified Las Vegas carry-over</h2>
<p><strong>Sergio Perez: five-place grid penalty at his next race.</strong>
FIA Las Vegas Document 61 finds him wholly responsible for contact with
Rafael Câmara at Turn 14. Because he retired and could not serve the time
penalty, it becomes a grid drop at the next race in which he participates,
expected to be Qatar. This is not a five-second Qatar penalty.
<a href="{PEREZ_PENALTY}">Original Stewards' ruling, 21 November</a>.</p>
<p>Las Vegas PU penalties for Antonelli, Piastri, Sainz, Stroll and Bearman
belong to that event; do not carry them forward again.
<a href="../las-vegas/powerunit.html">Reviewed Vegas technical and sanction tables</a>.
Qatar's own energy limits, tyre prescriptions and upgrades must come from
Qatar publications, not copied Las Vegas figures. Published source readers
appear on the relevant pages as collection succeeds; discovery failures stay visible.</p>"""
    for slug in ("overview", "notes", "schedule"):
        pages[slug]["body"] = carryover + pages[slug]["body"]
    pages["notes"]["body"] += f"""<p><strong>PU-use baseline:</strong>
FIA Document 8 lists season-to-date elements used by all 22 drivers before
Qatar running. It is not a local penalty list; see the full table and source
reader on <a href="powerunit.html#qatar-pu-usage">Power Unit</a>.</p>"""
    pages["schedule"]["body"] += f"""<p><strong>Self-scrutineering:</strong>
FIA Document 9 reports that all 11 teams submitted completed declaration forms
before 21:52 on 26 November. This confirms the filing only, not a technical
inspection result.
<a href="{FIA_QATAR_SELF_SCRUTINEERING}">Original FIA Document 9</a>.</p>"""
    pages["penalties"] = dict(
        kicker="Confirmed carry-over sanction",
        title="Penalties & Stewards",
        sub=("Las Vegas Document 61 applies a five-place grid drop to Sergio Perez "
             "at this event; it is not a Qatar stewards' decision."),
        body=render_penalties(
            ctx,
            decisions=[
                dict(
                    doc="Qatar Doc 5",
                    source_event="qatar",
                    no="11",
                    driver="Sergio Perez",
                    team="Cadillac Formula 1 Team",
                    session="Qatar Grand Prix — Stewards' hearing",
                    fact="Alleged late attendance at the Thursday Press Conference.",
                    outcome=(
                        "The driver and team representative are summoned for 18:30 local "
                        "on Friday 27 November. This is an allegation, not a finding or "
                        "penalty; no ruling is recorded in this summons."
                    ),
                    kind="note",
                    source_url=FIA_QATAR_PEREZ_SUMMONS,
                ),
                dict(
                    doc="Las Vegas Doc 61",
                    source_event="las-vegas",
                    no="11",
                    driver="Sergio Perez",
                    team="Cadillac Formula 1 Team",
                    session="Las Vegas Grand Prix — Race",
                    fact=("Turn 14 collision with Rafael Câmara; the stewards found "
                          "Perez wholly responsible."),
                    outcome=(
                        "The 10-second time penalty was converted after his retirement "
                        "into five grid places at the next race in which he participates "
                        "(Qatar)."
                    ),
                    kind="penalty",
                    source_url=PEREZ_PENALTY,
                )
            ],
            intro_html=(
                '<div class="callout accent"><strong>Confirmed carry-over:</strong> '
                'Las Vegas Document 61 is the source of this Qatar grid sanction; '
                'Formula1.com confirms it applies here. This is not a Qatar ruling; '
                'Qatar-specific decisions remain separate and source-dependent. '
                f'<a href="{PEREZ_PENALTY_ARTICLE}">Official Formula1.com report</a>.</div>'
                f'<div class="callout"><strong>Qatar Document 10: no action.</strong> '
                'The Technical Delegate reported Alpine car-operating personnel '
                'inside the circuit during a curfew period, identified as the team’s '
                'second of six permitted exceptions for 2026; the report says no '
                'action should be taken. This is not a driver penalty. '
                f'<a href="{FIA_QATAR_CURFEW}">Original FIA report</a>.</div>'
            ),
            fia_url=ctx.get("fia_url", ""),
        ),
    )
    lineup = card(
        "Haas confirms Rafael Câmara for Qatar and Abu Dhabi",
        f"""<p>Haas confirmed on 22 November that Câmara will drive for the team
at both remaining 2026 Grands Prix, after his race outings in Brazil and Las
Vegas. The announcement also identifies him as a full-time Haas driver for
2027. FIA Document 11 lists 20 race entrants and separately names Jak Crawford
as eligible to take part in FP1 under regulations B1.7.3 and B1.7.4; he is not
a 21st race entrant.
<a href="{CAMARA_QATAR_ANNOUNCEMENT}">Formula1.com, 22 November</a> ·
<a href="{FIA_QATAR_ENTRY_LIST}#page=2">FIA entry list, page 2</a>.</p>""",
        "bi-person-badge", "accent",
    )
    qatar_fp1 = card(
        "Aston Martin confirms Jak Crawford for Qatar FP1",
        f"""<p>FIA Document 11 lists Crawford separately from the 20 race entrants
as eligible to participate in FP1 under regulations B1.7.3 and B1.7.4.
Aston Martin confirmed that he will drive Fernando Alonso's car in Friday's
session after limited running in Las Vegas. This is a practice substitution,
not a race-entry change.
<a href="{FIA_QATAR_ENTRY_LIST}#page=2">FIA entry list, page 2</a> ·
<a href="{QATAR_FP1_ANNOUNCEMENT}">Aston Martin's official announcement</a>.</p>""",
        "bi-person-badge", "accent",
    )
    ferrari_story = card(
        "Ferrari's Las Vegas tension carries into Qatar",
        f"""<p>Formula1.com's 25 November Qatar preview also revisits the Ferrari
collision in Las Vegas: Charles Leclerc hit team-mate Lewis Hamilton during
their Turn 7 fight. FIA Document 60 found Leclerc wholly responsible and
imposed a 10-second penalty; team principal Fred Vasseur described the
incident as unacceptable. At Thursday's FIA press conference, Leclerc said
the team needed a solution, accepted responsibility for the Vegas clash, and
declined to disclose whether the rules of engagement would change. This does
not confirm new team rules or a Qatar sanction. Formula1.com reports Hamilton
finished seventh after serving a separate 10-second penalty; the final
classification is consistent with that result. In a 26 November media-day
report, Hamilton said securing second in the Constructors' Championship is
Ferrari's immediate priority, that the drivers remain free to race, and that
improvements to their processes and communication will be discussed over
winter. The FIA press conference also records Leclerc denying a contractual
number-one clause; this does not establish operational race instructions.
These are updates to ongoing discussions, not a new team rule.
<a href="{QATAR_RACE_WEEK_STORYLINES}">Formula1.com Qatar preview</a> ·
<a href="{FIA_VEGAS_LECLERC_COLLISION}">FIA Las Vegas Document 60</a> ·
<a href="{FERRARI_VASSEUR_REPORT}">Vasseur's post-race comments</a> ·
<a href="{QATAR_THURSDAY_PRESS_CONFERENCE}">FIA Thursday press-conference transcript, 26 November</a> ·
<a href="{QATAR_FERRARI_FOLLOWUP}">Formula1.com, Leclerc and Hamilton's Qatar media-day comments, 26 November</a> ·
<a href="{HAMILTON_TRACK_LIMITS}">FIA Document 54</a> ·
<a href="{FINAL_CLASSIFICATION}">FIA final Document 65</a> ·
<a href="{LECLERC_PENALTY_REPORT}">Formula1.com final-result account</a>.</p>""",
        "bi-people", "accent",
    )
    verstappen_russell_story = card(
        "Russell and Verstappen move on from their Las Vegas exchange",
        f"""<p>Formula1.com's 26 November Qatar media-day report says Russell
found some of Verstappen's post-race comments "quite amusing", but is moving
on and does not want to continue the off-track exchange. Verstappen said
there was nothing else to add and that his focus was a good Qatar weekend.
These are attributed comments, not a prediction of how they will race each
other here.
<a href="{QATAR_RUSSELL_VERSTAPPEN_FOLLOWUP}">Formula1.com, 26 November</a>.</p>""",
        "bi-people", "accent",
    )
    bearman_story = card(
        "Haas confirms Bearman will continue into 2027",
        f"""<p>On 26 November, TGR Haas confirmed that Oliver Bearman signed a
new deal to continue with the team in 2027, completing next year's driver
grid. This supersedes the 25 November report that his contract was still
being finalised. It confirms his future seat, not a change to the 2026 Qatar
entry list; Bearman remains a Haas driver this weekend.
<a href="{HAAS_BEARMAN_ANNOUNCEMENT}">TGR Haas official announcement</a> ·
<a href="{BEARMAN_HAAS_SEAT}">Formula1.com report</a>.</p>""",
        "bi-person-badge", "accent",
    )
    hadjar_front_wing_story = card(
        "Red Bull reinforces Hadjar's front wing after Las Vegas failure",
        f"""<p>In the FIA's Thursday press-conference transcript, Isack Hadjar
said the front-wing failure that ended his Las Vegas race remains under
investigation. He said the team reinforced the assembly for Qatar and expects
it to prevent a repeat. This is the driver's update, not a confirmed
engineering root cause.
<a href="{QATAR_THURSDAY_PRESS_CONFERENCE}">FIA Thursday press-conference transcript, 26 November</a>.</p>""",
        "bi-tools", "accent",
    )
    alonso_honda_story = card(
        "Honda checks Alonso's reported Las Vegas engine problem",
        f"""<p>Fernando Alonso stopped late in the Las Vegas race after reporting
an engine problem. Honda's trackside representative Shintaro Orihara told
The Race that its data and maintenance inspections had not identified an
engine issue, and that Honda would check again on Friday in Qatar. Neither
the cause of Alonso's report nor a Qatar failure has been established.
<a href="{QATAR_MERCEDES_ENERGY_FOLLOWUP}">The Race's Qatar day-one report, 26 November</a>.</p>""",
        "bi-tools", "accent",
    )
    cost_cap_story = card(
        "FIA resolves 2025 financial-regulation cases for Williams and Alpine",
        f"""<p>The FIA's 25 November 2026 review covered 11 team submissions:
the 10 teams that raced in 2025 plus newcomer Cadillac. Nine were compliant
with the 2025 financial regulations; Williams had a minor overspend and
procedural breach, while Alpine had a procedural breach. All five power-unit
manufacturers were compliant. The Williams agreement says the unintentional
overspend was £627,000 (0.48%) and found no sporting advantage. Its 12-month sporting
sanction subtracts 1.5 percentage points from the coefficient used to set
restricted wind-tunnel and CFD allowances (for example, 90% becomes 88.5%);
this is not a Qatar grid or race penalty. The Alpine agreement requires a
financial penalty and investigation costs, but no sporting penalty. The
public summaries do not state either financial-penalty amount.
<a href="{FIA_COST_CAP_REVIEW}">FIA's 2025 compliance review</a> ·
<a href="{FIA_WILLIAMS_ABA}">Williams accepted breach agreement</a> ·
<a href="{FIA_WILLIAMS_ABA_SUMMARY}">Williams public summary</a> ·
<a href="{FIA_ALPINE_ABA}">Alpine accepted breach agreement</a> ·
<a href="{FIA_ALPINE_ABA_SUMMARY}">Alpine public summary</a> ·
<a href="{F1_COST_CAP_REPORT}">Formula1.com report</a>.</p>""",
        "bi-info-circle", "accent",
    )
    for slug in ("overview", "rookies", "notes"):
        pages[slug]["body"] = lineup + pages[slug]["body"]
    pages["rookies"]["body"] = pages["rookies"]["body"].replace(
        content_generic.pending(
            "Rookie FP1 line-ups for this round", "in the week before the event"
        ),
        qatar_fp1,
        1,
    )
    pages["rookies"]["body"] = pages["rookies"]["body"].replace(
        content_generic.pending(
            "Reserve or replacement driver changes", "as teams confirm them", "bi-people"
        ),
        "",
        1,
    )
    pages["rookies"]["body"] += card(
        "Lindblad reflects on his Las Vegas retirement",
        f"""<p>Formula1.com reported on 26 November that Lindblad was upset
after a Safety Car-period spin ended his Las Vegas race while he was running
near the front. He said he is now trying to focus on Qatar and Abu Dhabi.
This is the driver's account of the disappointment, not a confirmed technical
cause for the spin.
<a href="{QATAR_LINDBLAD_FOLLOWUP}">Formula1.com interview, 26 November</a>.</p>""",
        "bi-person-badge", "accent",
    )
    pages["news"] = dict(
        kicker="Weekend News",
        title="Weekend News & Session Reports",
        sub=news_page_subtitle(ctx),
        body=cost_cap_story + auto_news(ctx),
    )
    pages["teams"]["body"] = (
        lineup + cost_cap_story + verstappen_russell_story + ferrari_story + bearman_story
        + hadjar_front_wing_story + alonso_honda_story + pages["teams"]["body"]
    )
    pages["notes"]["body"] = cost_cap_story + pages["notes"]["body"]
    pages["notes"]["body"] = alonso_honda_story + pages["notes"]["body"]
    pages["notes"]["body"] = hadjar_front_wing_story + pages["notes"]["body"]
    pages["notes"]["body"] = verstappen_russell_story + pages["notes"]["body"]
    pending_team_storylines = content_generic.pending(
        "Team-by-team weekend storylines", "in the week before the race"
    )
    if pending_team_storylines not in pages["teams"]["body"]:
        raise ValueError("Could not locate Qatar's generic pending team-storyline copy")
    pages["teams"]["body"] = pages["teams"]["body"].replace(
        pending_team_storylines, upgrade_summary, 1
    )
    nomination = f"""<p>Pirelli nominated <strong>C1 Hard, C2 Medium and C3 Soft</strong>
for Qatar. Its 13 November graphic marks C3 as the qualifying mandatory set
and C1 and C2 as the race mandatory sets. This nomination is not a
driver-by-driver remaining-set inventory.</p>
<p>Two Formula1.com articles published on 25 November give different
per-driver slick allocations. Its 10:05 UTC tyre guide says two C1 Hard,
three C2 Medium and eight C3 Soft sets, and says an extra Soft is reserved
for drivers reaching Q3. The 10:43 UTC explainer instead says each driver
gets 13 sets: two C1 Hard, four C2 Medium and seven C3 Soft. Pirelli's
24 November release confirms the compounds but does not state these
per-driver totals, so the exact allocation is conflicting and remains
unresolved here. Formula1.com also says a dry race requires two different
slick compounds. These are allocation reports, not post-qualifying
remaining-set counts.
<a href="{QATAR_TYRE_ALLOCATION}">Formula1.com tyre guide, 10:05 UTC</a> ·
<a href="{QATAR_TYRE_LIMIT_EXPLAINER}">Formula1.com explainer, 10:43 UTC</a>.</p>
<p>On 24 November, Pirelli announced a maximum 27-lap stint per set, agreed
with the FIA, and said the race will require at least two stops. At the full
scheduled 57-lap distance, two sets cover only 54 laps. The FIA's Qatar
competition notes (Document 13, Pirelli Preview V2 / Issue B, page 2)
independently specify the same limit.
<a href="{PIRELLI_TYRE_LIMIT}">Pirelli's official Qatar tyre briefing, 24 November</a>.</p>
<p>Document 13 V2 clarifies the 27-lap cap's cumulative count across all track
sessions, including laps under the Safety Car or Virtual Safety Car. For the
Race, count each lap started after the start signal and before the
end-of-session signal; reconnaissance and formation laps before the start and
laps after the end signal do not count. In every other session, any lap started
counts, including post-session laps to return to the pits and practice-start
laps. A lap started but not completed counts in full, and a mixed set takes the
mileage of its highest-mileage tyre. Document 14 V2 repeats this rule and
clarifies that a set exceeding its limit because pit entry was closed must
be changed at the earliest safe opportunity after it reopens; when both
cars of a team exceed the limit this way, at least one must pit at that
opportunity. The second car may pass pit entry once before entering.
Formula1.com's 25 November explainer describes the earlier rule.
<a href="{QATAR_TYRE_LIMIT_EXPLAINER}">Formula1.com, 25 November explainer</a> ·
<a href="{FIA_QATAR_TYRE_NOTES}#page=2">FIA Document 13 V2, page 2</a> ·
<a href="{FIA_QATAR_RACE_DIRECTOR_NOTES}#page=7">FIA Document 14 V2, page 7</a>.</p>
<p>The FIA's official Qatar competition notes (Document 13 V2 / Issue B,
page 2) repeat the earlier pressure and compound values. Minimum starting
and expected stabilized pressures are in psi:</p>
<div class="table-wrap"><table class="data compact">
<thead><tr><th>Compound</th><th>Front start</th><th>Front stabilized</th><th>Front camber</th><th>Rear start</th><th>Rear stabilized</th><th>Rear camber</th></tr></thead>
<tbody>
<tr><th>Slicks</th><td>29.0</td><td>&gt;=30.0</td><td>-2.75 degrees</td><td>27.5</td><td>&gt;=28.5</td><td>-1.50 degrees</td></tr>
<tr><th>Intermediates</th><td>30.0</td><td>&gt;=31.0</td><td>-3 degrees</td><td>27.5</td><td>&gt;=28.5</td><td>-2 degrees</td></tr>
<tr><th>Wets</th><td>28.5</td><td>&gt;=31.0</td><td>-3 degrees</td><td>25.5</td><td>&gt;=28.5</td><td>-2 degrees</td></tr>
</tbody></table></div>
<p>The sheet also specifies C1 and C2 as mandatory race tyres, C3 as the Q3 tyre,
and caps each set at 27 laps across all sessions and tyre history.
Pirelli's separate 24 November event infographic
shows the same pressure figures, marks them subject to change after FP2, and
lists an average pit-stop loss of 26.5 seconds; do not present that as a
stationary wheel-change duration. These event prescriptions do not resolve the
conflicting Formula1.com reports of driver-by-driver set allocations.
<a href="{FIA_QATAR_TYRE_NOTES}#page=2">FIA Document 13 V2 - Pirelli Preview, page 2</a> ·
<a href="{PIRELLI_TYRE_LIMIT}">Pirelli's official Qatar tyre briefing, 24 November</a>.</p>
<p>Pirelli F1 chief engineer Simone Berra's earlier Motorsport.com interview
adds details about session-by-session tyre use and remaining allowances after
Saturday running.
<a href="{QATAR_TYRE_LIMIT}">Motorsport.com report and Berra interview, 20 November</a>.
Coffee Corner Motorsport's independent 24 November preview says practice and
qualifying laps consume each set's allowance. <a href="{QATAR_TYRE_STRATEGY}">Coffee
Corner Motorsport, Qatar tyre preview</a> ·
<a href="{PIRELLI_NOMINATION}">Pirelli compound selection and graphic, 13 November</a>.</p>"""
    strategy = f"""<h2 class="sec">Two-stop examples — not a prediction</h2>
<p>For a full 57-lap dry race, a fresh Medium / fresh Hard / fresh Medium
could stop after laps 19 and 38: three 19-lap race stints. An early Safety
Car stop after lap 7 could instead be followed by a stop after lap 34:
7 / 27 / 23 laps, if each set has enough allowance left. These are arithmetic
examples, not measured optimum windows or a claim that those sets remain
available. A shortened race, Safety Car, rain, tyre wear or a changed rule
can alter the plan; a dry race also requires two different slick compounds.</p>
<p>Each set's earlier session use reduces its remaining allowance. FIA
Documents 13 and 14 V2 clarify that post-session laps to return to the pits
and practice-start laps count against the cap, while reconnaissance and
formation laps before the race start do not. If pit entry closure causes a
set to exceed the cap, it must be changed at the earliest safe opportunity
after pit entry reopens. Use the official post-Saturday remaining-lap
information before applying either example.
<a href="{QATAR_TYRE_LIMIT_EXPLAINER}">Formula1.com counting-rule explainer</a> ·
<a href="{FIA_QATAR_TYRE_NOTES}#page=2">FIA Document 13 V2, page 2</a> ·
<a href="{FIA_QATAR_RACE_DIRECTOR_NOTES}#page=7">FIA Document 14 V2, page 7</a> ·
<a href="{QATAR_TYRE_COUNTING}">Coffee Corner Motorsport counting report</a> ·
<a href="{QATAR_TYRE_LIMIT}">Pirelli engineer on remaining laps</a>.</p>"""
    tyre_preview = f"""<figure class="circuit-fig">
<img class="circuit-img tyre-preview-img" src="../assets/{QATAR_TYRE_PREVIEW}"
alt="Pirelli's 2026 Qatar tyre selection: C1 Hard, C2 Medium and C3 Soft; C3 is mandatory for qualifying and C1 and C2 are mandatory for the race."
loading="lazy" onclick="zoomImg(this)">
<figcaption>Full, uncropped Pirelli Qatar 2026 compound and mandatory-set graphic.
This is not a driver-by-driver remaining-set inventory.
<a href="../assets/{QATAR_TYRE_PREVIEW}">Full-resolution image</a> ·
<a href="{PIRELLI_NOMINATION}">Pirelli source, 13 November 2026</a>.</figcaption>
</figure>"""
    pages["tyres"]["body"] += tyre_preview + (
        "<p>Pirelli's 24 November preview marks the starred pressure figures "
        "as subject to change after FP2.</p>"
    ) + card(
        "Qatar compounds and 27-lap tyre-set limit",
        nomination,
        "bi-record-circle",
        "accent",
    ) + strategy + card(
        "Known Qatar Grand Prix punctures",
        f"""<p>Selected documented race incidents at Lusail, not a complete
inventory. These had different reported causes and should not be treated as
predictions for this year's race.</p>
<ul>
<li><strong>2021 — Valtteri Bottas (Mercedes):</strong> front-left puncture
on lap 33; he later retired.</li>
<li><strong>2021 — Lando Norris (McLaren):</strong> front-left puncture
forced a second stop on lap 49; he recovered to ninth.
<a href="{QATAR_2021_NORRIS_PUNCTURE}">Formula1.com: Norris</a>.</li>
<li><strong>2021 — George Russell (Williams):</strong> front-left puncture
on lap 50; he finished 17th.</li>
<li><strong>2021 — Nicholas Latifi (Williams):</strong> front-left puncture
on lap 52; he retired.
<a href="{QATAR_2021_PUNCTURES}">Formula1.com: Bottas and Williams</a>.</li>
<li><strong>2024 — Lewis Hamilton (Mercedes) and Carlos Sainz (Ferrari):</strong>
both suffered front-left failures in the race. The Race reported in February
2025 that Pirelli's investigation attributed them to excessive wear. Pressure
was already dropping before Bottas struck Alex Albon's mirror, so those
failures should not be attributed to that mirror debris.
<a href="{QATAR_2024_TYRE_FAILURES}">The Race: Pirelli's findings</a>.</li>
<li><strong>2025 — Isack Hadjar (Racing Bulls):</strong> a late front-left
puncture cost him a likely sixth place and ended his race. Hadjar attributed
it to a broken front wing, not to tyre wear.
<a href="{QATAR_2025_RACE}">Formula1.com race report</a> ·
<a href="{QATAR_2025_HADJAR_PUNCTURE}">Hadjar's account</a>.</li>
</ul>
<p><strong>Why the concern:</strong> Pirelli's initial 2021 investigation
linked the four failures mainly to repeated high-speed kerb loading and
sidewall damage.
<a href="{QATAR_2021_PIRELLI_FINDINGS}">Formula1.com: Pirelli's initial findings</a>.
In 2023, analysis found sidewall separation after track running; the FIA and
Pirelli imposed an 18-lap total-life limit per set, including prior use.
That is a separate safety measure, not another named puncture.
<a href="{QATAR_2023_TYRE_LIMIT}">Motorsport.com: 2023 FIA decision</a>.</p>""",
        "bi-record-circle",
    )
    pages["notes"]["body"] = (
        qatar_fia_map_note + qatar_race_director_note + bearman_story
        + qatar_fp1 + nomination + strategy + ferrari_story
        + pages["notes"]["body"]
    )
    pages["schedule"]["body"] += f"""
<h2 class="sec">Support-race and car-presentation watch</h2>
<p>The FIA competition visa dates the race for 29 November 2026 at 19:00
local (18:00 Tallinn), lists Lusail's lap length as 5.419 km and confirms
57 race laps. The FIA stewards are Garry Connelly and Mathieu Remmerie.
The timetable remains subject to the stewards' approval and published
appendices.
<a href="{FIA_QATAR_VISA}">FIA 2026 Qatar competition visa</a>.</p>
<p>The Formula1.com timetable lists F1 car presentation on Friday 15:00–16:00
local (14:00–15:00 Tallinn). F2 qualifying follows FP1 at 18:00 Friday
(17:00 Tallinn); its Sprint is Saturday 19:15 (18:15 Tallinn), and its
Feature Race Sunday 15:00 (14:00 Tallinn). The F1 weekend is standard, not
a Sprint weekend. Times are subject to change.
<a href="{QATAR_TIMETABLE}">Official full timetable</a>.</p>"""
    car_display = f"""<h2 class="sec">FIA car-display procedure — Document 4</h2>
<p>For Friday 27 November, the FIA requires one car from each team to be
positioned in its pit-stop position between 15:00 and 16:00 local; the other
car is to be available for viewing inside the garage. If only one car carries
major aerodynamic or bodywork components not run at a previous Competition
or TCC and intended for this event, that is the car to display. The outside
car may be used for pit-stop practice, but must return to the same position
when practice is not taking place. The notice also sets out an adverse-weather
procedure. This governs the media display, not team upgrade declarations, and
is distinct from the car-presentation submissions recorded in FIA Document 12.
<a href="{FIA_QATAR_CAR_DISPLAY}#page=2">Original FIA Document 4, page 2</a>.</p>"""
    pages["upgrades"]["sub"] = (
        "FIA Document 12: one Audi item and explicit nil returns from ten other teams."
    )
    upgrades_pending = content_generic.pending(
        "FIA car presentation submissions for this round", "on the Friday of the race week"
    )
    if upgrades_pending not in pages["upgrades"]["body"]:
        raise ValueError("Could not locate Qatar's pending FIA upgrade-submission copy")
    pages["upgrades"]["body"] = pages["upgrades"]["body"].replace(
        upgrades_pending,
        render_submissions(
            UPGRADE_SUBMISSIONS,
            source_url=FIA_QATAR_CAR_PRESENTATION,
            asset_prefix=FIA_QATAR_CAR_PRESENTATION_ASSET,
            document="FIA Document 12",
            event="Qatar Grand Prix",
            issued="27 November 2026",
        ),
        1,
    )
    pages["upgrades"]["body"] += car_display
    pages["schedule"]["body"] += f"""
<p>The FIA's Document 4 confirms the Friday car-display window is 15:00–16:00
local (14:00–15:00 Tallinn) and requires each team's display car at its pit-stop
position. It is a presentation procedure, not an upgrade submission.
<a href="{FIA_QATAR_CAR_DISPLAY}#page=2">FIA Document 4, page 2</a>.</p>"""
    pages["schedule"]["body"] += f"""
<p><strong>FIA entry list, Document 11:</strong> it lists 20 race entrants and
separately names Jak Crawford as eligible for FP1 under regulations B1.7.3 and
B1.7.4. Aston Martin confirmed he will drive Fernando Alonso's car; this is a
practice substitution, not a twenty-first race entry.
<a href="{FIA_QATAR_ENTRY_LIST}#page=2">Official entry list, page 2</a> ·
<a href="{QATAR_FP1_ANNOUNCEMENT}">Aston Martin confirmation</a>.</p>"""
    curfew_report = f"""<h2 class="sec">FIA curfew report — Document 10</h2>
<p>Issued to the stewards on 27 November, the Technical Delegate's report says
BWT Alpine Formula One Team personnel associated with car operation were inside
the circuit during a 13-hour curfew period from 22:30 on Wednesday 25 November
to 11:30 on Thursday 26 November. The period was 42 to 29 hours before the
scheduled start of P1. This was Alpine's second of six permitted individual
exceptions for the 2026 season, so the report says no action should be taken;
it records no driver penalty.
<a href="{FIA_QATAR_CURFEW}">Original FIA Document 10</a>.</p>"""
    pages["schedule"]["body"] += curfew_report
    pages["notes"]["body"] = curfew_report + pages["notes"]["body"]
    pages["notes"]["body"] = car_display + pages["notes"]["body"]
    pages["notes"]["body"] = upgrade_summary + pages["notes"]["body"]
    pages["overview"]["body"] += upgrade_summary
    pages["moments"]["body"] = pages["moments"]["body"].replace(
        content_generic.pending(
            "A curated moments list for this venue",
            "in the official preview material for the round", "bi-stars",
        ),
        card(
            "2025: a Safety Car reshapes the title fight",
            f"""<p>With a 25-lap maximum tyre stint imposed for the 2025 race,
Verstappen pitted under the early Safety Car while both McLarens stayed out.
He won ahead of Piastri and Sainz; Norris finished fourth, taking a 12-point
lead over Verstappen into the finale. That 25-lap cap was specific to 2025;
Pirelli announced a separate 27-lap limit for each set in 2026.
<a href="{QATAR_2025_RACE}">Formula1.com race report</a> ·
<a href="{PIRELLI_TYRE_LIMIT}">2026 Pirelli limit announcement</a>.</p>""",
            "bi-stars", "accent",
        ),
    )
    return pages
