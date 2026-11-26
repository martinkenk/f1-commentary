"""Verified carry-over information; local Qatar documents remain source-dependent."""
import content_generic
from content_las_vegas import (
    FINAL_CLASSIFICATION,
    HAMILTON_TRACK_LIMITS,
    LECLERC_PENALTY_REPORT,
    PEREZ_PENALTY,
)
from f1lib import auto_news, card, news_page_subtitle, render_penalties


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
FIA_QATAR_TYRE_NOTES = "https://www.fia.com/system/files/decision-document/2026_qatar_grand_prix_-_competition_notes_-_pirelli_preview.pdf"
FIA_QATAR_F1_CIRCUIT_MAP = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_qatar_grand_prix_-_competition_notes_-_circuit_map_pit_lane_drawing_emergency_exits_map_and_red_zone.pdf"
)
FIA_QATAR_F1_CIRCUIT_MAP_IMAGE = (
    "fia-qatar-32198d476fbc-d4e6898c25a3e5e9-p2.png"
)
FIA_QATAR_RACE_DIRECTOR_NOTES = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_qatar_grand_prix_-_race_directors_competition_notes.pdf"
)
FIA_QATAR_SUPPORT_CIRCUIT_MAP = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_lusail_event_-_circuit_map_-_lusail_2026.pdf"
)
FIA_QATAR_CAR_DISPLAY = "https://www.fia.com/system/files/decision-document/2026_qatar_grand_prix_-_car_display_procedure.pdf"
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
    qatar_race_director_note = f"""<div class="callout accent"><strong>FIA Race Director's competition notes, 26 November:</strong>
the maximum time between the second and first Safety Car Lines for qualifying
and race reconnaissance laps will be notified after FP2. During the race,
teams receive a lapping pre-warning at 3.0 s; blue panels are shown at 1.2 s,
and the lapped driver must yield at the first opportunity. At Turn 16, a
track-limits infringement invalidates that lap and the immediately following
lap. <a href="{FIA_QATAR_RACE_DIRECTOR_NOTES}#page=2">Race Director's notes, page 2</a> ·
<a href="{FIA_QATAR_RACE_DIRECTOR_NOTES}#page=6">track limits, page 6</a>.</div>"""
    pages["circuit"]["body"] += circuit
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
            ),
            fia_url=ctx.get("fia_url", ""),
        ),
    )
    lineup = card(
        "Haas confirms Rafael Câmara for Qatar and Abu Dhabi",
        f"""<p>Haas confirmed on 22 November that Câmara will drive for the team
at both remaining 2026 Grands Prix, after his race outings in Brazil and Las
Vegas. The announcement also identifies him as a full-time Haas driver for
2027. This confirms Câmara's Qatar participation; it does not establish a
rookie FP1 substitution or the complete event entry list.
<a href="{CAMARA_QATAR_ANNOUNCEMENT}">Formula1.com, 22 November</a>.</p>""",
        "bi-person-badge", "accent",
    )
    qatar_fp1 = card(
        "Aston Martin confirms Jak Crawford for Qatar FP1",
        f"""<p>On 25 November, Aston Martin confirmed that Crawford will drive
Fernando Alonso's car in Friday's FP1 after limited running in Las Vegas. This
confirms one FP1 substitution, not the complete event entry list or the other
teams' rookie appearances.
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
    pages["news"] = dict(
        kicker="Weekend News",
        title="Weekend News & Session Reports",
        sub=news_page_subtitle(ctx),
        body=cost_cap_story + auto_news(ctx),
    )
    pages["teams"]["body"] = (
        lineup + cost_cap_story + verstappen_russell_story + ferrari_story + bearman_story
        + hadjar_front_wing_story + pages["teams"]["body"]
    )
    pages["notes"]["body"] = cost_cap_story + pages["notes"]["body"]
    pages["notes"]["body"] = hadjar_front_wing_story + pages["notes"]["body"]
    pages["notes"]["body"] = verstappen_russell_story + pages["notes"]["body"]
    pending_team_storylines = content_generic.pending(
        "Team-by-team weekend storylines", "in the week before the race"
    )
    team_upgrade_pending = content_generic.pending(
        "FIA car presentation submissions for this round",
        "on the Friday of the race week",
    )
    if pending_team_storylines not in pages["teams"]["body"]:
        raise ValueError("Could not locate Qatar's generic pending team-storyline copy")
    pages["teams"]["body"] = pages["teams"]["body"].replace(
        pending_team_storylines, team_upgrade_pending, 1
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
competition notes (Doc 2, page 2) independently specify the same 27-lap
limit; the document and its screenshot are linked below.
<a href="{PIRELLI_TYRE_LIMIT}">Pirelli's official Qatar tyre briefing, 24 November</a>.</p>
<p>Formula1.com's 25 November explainer quotes Pirelli's counting details:
the 27-lap maximum is cumulative across sessions, including Safety Car and
Virtual Safety Car laps; all race laps from the start signal to the
chequered flag count. In other track sessions, a lap started but not
completed counts as a full lap, and a set assembled from tyres with
different mileage takes the higher mileage. Reconnaissance, formation and
post-race laps are excluded. This report is consistent with the separately
reviewed 27-lap FIA/Pirelli Qatar prescription.
<a href="{QATAR_TYRE_LIMIT_EXPLAINER}">Formula1.com, 25 November explainer</a>.</p>
<p>The FIA's official Qatar competition notes (Doc 2, page 2) specify slick
minimum starting / expected stabilized running pressures of
29.0 / &gt;=30.0 psi at the front and 27.5 / &gt;=28.5 psi at the rear,
with camber limits of -2.75 degrees
front and -1.50 degrees rear. The same FIA sheet sets C1 and C2 as mandatory
race tyres, C3 as the Q3 tyre, and caps each set at 27 laps across all sessions
and tyre history. Pirelli's separate 24 November event infographic
shows the same pressure figures, marks them subject to change after FP2, and
lists an average pit-stop loss of 26.5 seconds; do not present that as a
stationary wheel-change duration. These event prescriptions do not resolve the
conflicting Formula1.com reports of driver-by-driver set allocations.
<a href="{FIA_QATAR_TYRE_NOTES}#page=2">FIA Competition Notes - Pirelli Preview, page 2</a> ·
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
<p>Each set's earlier session use reduces its remaining allowance.
Formula1.com's 25 November explainer reports that all race laps from the
start signal to the chequered flag count; in other sessions, a started but
unfinished lap counts in full, and mixed-mileage sets take the higher tyre
mileage. Reconnaissance, formation and post-race laps are excluded. These
are the reported Pirelli counting rules and match the reviewed FIA/Pirelli
event prescription; use post-Saturday official remaining-lap information
before applying either example.
<a href="{QATAR_TYRE_LIMIT_EXPLAINER}">Formula1.com counting-rule explainer</a> ·
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
    ) + strategy
    pages["notes"]["body"] = (
        qatar_fia_map_note + qatar_race_director_note + bearman_story
        + nomination + strategy + ferrari_story
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
does not establish that any new components have been submitted.
<a href="{FIA_QATAR_CAR_DISPLAY}#page=2">Original FIA Document 4, page 2</a>.</p>"""
    pages["upgrades"]["sub"] = (
        "FIA car-presentation filings, parts changes and display logistics for Qatar."
    )
    pages["upgrades"]["body"] += car_display
    pages["schedule"]["body"] += f"""
<p>The FIA's Document 4 confirms the Friday car-display window is 15:00–16:00
local (14:00–15:00 Tallinn) and requires each team's display car at its pit-stop
position. It is a presentation procedure, not an upgrade submission.
<a href="{FIA_QATAR_CAR_DISPLAY}#page=2">FIA Document 4, page 2</a>.</p>"""
    pages["notes"]["body"] = car_display + pages["notes"]["body"]
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
