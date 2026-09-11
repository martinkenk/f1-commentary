"""Madrid 2026: source-checked FIA material, including Friday's upgrade filings."""
from content_generic import build_pages as build_generic, pending
from f1lib import auto_h2h, auto_penalties, card, stat, ul


FIA_BASE = "https://www.fia.com/system/files/decision-document/2026_spanish_grand_prix_-_"
FIA_MAP_URL = FIA_BASE + "competition_notes_-_circuit_map_pit_lane_drawing_and_emergency_exits_map.pdf"
FIA_PU_URL = FIA_BASE + "power_unit_information.pdf"
FIA_TYRES_URL = FIA_BASE + "competition_notes_-_pirelli_preview.pdf"
FIA_NOTES_URL = FIA_BASE + "race_directors_competition_notes.pdf"
FIA_DISPLAY_URL = FIA_BASE + "car_display_procedure.pdf"
FIA_UPGRADES_URL = FIA_BASE + "car_presentation_submissions.pdf"
FIA_UPGRADES_ASSET = "fia-spain-f5b87d349e3b-c92e9191ede7c2bb"
UPGRADE_SUBMISSIONS = (
    ("McLaren", 2, (
        ("Rear wing", "Performance - Flow Conditioning",
         "Additional rear-wing elements condition the airflow onto the mainplane and flap."),
    )),
    ("Mercedes", 4, (
        ("Rear wing", "Circuit specific - Drag Range",
         "A shorter central winglet above the flap reduces local downforce and drag "
         "to suit Madrid's lift-to-drag requirements."),
        ("Exhaust tailpipe", "Circuit specific - Drag Range",
         "An extra winglet behind the exhaust turns the exhaust flow to generate "
         "load and drag in a ratio suited to Madrid."),
        ("Front drum", "Performance - Flow Conditioning",
         "A reprofiled front lip improves flow attachment across steering angles "
         "and the airflow reaching the rear of the car."),
    )),
    ("Red Bull", 6, (
        ("Rear corner", "Reliability",
         "The more robust rear-wheel bodywork gaitor developed from Monza gains "
         "winglets behind the suspension fairings, aiming to recover earlier load "
         "while keeping the wheel bodywork sealed."),
        ("Floor bib", "Reliability",
         "Revised laminate and geometry between floor and chassis reduce local "
         "strain when the assembly deflects, aiming to prevent structural and "
         "aerodynamic-surface deterioration."),
    )),
    ("Ferrari", 8, (
        ("Rear suspension", "Performance - Local Load",
         "The rearward leg fairing of the rear upper wishbone is reprofiled, "
         "adjusting incidence and spanwise loading for a local aerodynamic gain."),
    )),
    ("Williams", 10, ()),
    ("Racing Bulls", 11, ()),
    ("Aston Martin", 12, ()),
    ("Haas", 13, ()),
    ("Audi", 14, ()),
    ("Alpine", 15, (
        ("Floor board", "Performance - Local Load",
         "An extra element on the forward floor board changes pressure distribution "
         "and flow management to generate efficient local downforce."),
    )),
    ("Cadillac", 17, (
        ("Rear wing flap", "Performance - Local Load",
         "A revised central trailing-edge winglet is reintroduced to increase rear "
         "load and improve aerodynamic stability across operating conditions."),
        ("Diffuser vane", "Performance - Local Load",
         "A small vertical turning vane on the inner trailing edge of the outboard "
         "diffuser sidewall improves outer-floor-channel performance and rear load."),
    )),
)
PIRELLI_URL = ("https://www.formula1.com/en/latest/article/"
               "what-tyres-will-the-teams-and-drivers-have-for-the-2026-spanish-grand-prix."
               "2vlcVOBnZUFRCooVcqWG7n")
PREVIEW_URL = ("https://www.formula1.com/en/latest/article/"
               "need-to-know-the-most-important-facts-stats-and-trivia-ahead-of-the-"
               "2026-spanish-grand-prix-madrid-madring.0VbYQHCnrBCibxbkwygP0")
GUIDE_URL = ("https://www.formula1.com/en/latest/article/"
             "circuit-guide-everything-you-need-to-know-about-the-madring.NF7Mh3iag3w9GUPlihwJA")
LINEUP_URL = ("https://www.formula1.com/en/latest/article/"
              "lawson-to-stay-at-red-bull-for-third-race-weekend-in-madrid-as-hadjars-"
              "recovery-continues.Bxrk9FOVDChcWCo5vxY8v")

LENGTH_NOTE = f"""
<div class="callout watch">
  <strong>Circuit-length discrepancy:</strong> the FIA circuit map (Document 6,
  version 3, 10 September) gives <strong>5.414 km</strong>; the earlier power-unit
  sheet (Document 3), Formula1.com calendar and Pirelli preview give
  <strong>5.416 km</strong>. Calendar figures elsewhere on this page retain their
  published source values; the race distance has not been recalculated from the map.
  <a href="{FIA_MAP_URL}#page=2" target="_blank" rel="noopener">Latest map</a> /
  <a href="{FIA_PU_URL}#page=2" target="_blank" rel="noopener">PU sheet</a>.
</div>
"""


def _figure(asset, alt, caption):
    return f"""<figure class="circuit-fig">
  <img src="../assets/{asset}" alt="{alt}" class="circuit-img"
       onclick="zoomImg(this)" title="Click to zoom / full screen" loading="lazy">
  <figcaption>{caption} <strong>Click to zoom / full screen.</strong></figcaption>
</figure>"""


def _upgrade_filing():
    rows, teams = [], []
    for team, page, updates in UPGRADE_SUBMISSIONS:
        areas = ", ".join(component for component, _, _ in updates) or "No updates submitted"
        rows.append(
            f'<tr><td>{team}</td><td class="num">{len(updates)}</td><td>{areas}</td>'
            f'<td><a href="{FIA_UPGRADES_URL}#page={page}" target="_blank" rel="noopener">'
            f'Page {page}</a></td></tr>')
        evidence = []
        for source_page in ([page, page + 1] if updates else [page]):
            if source_page != page:
                label = "component-location diagram"
            else:
                label = "component declaration" if updates else "nil-return declaration"
            evidence.append(_figure(
                f"{FIA_UPGRADES_ASSET}-p{source_page}.png",
                f"{team} Spanish GP {label}, FIA Document 11 page {source_page}",
                f'{team}: {label}. <a href="{FIA_UPGRADES_URL}#page={source_page}" '
                f'target="_blank" rel="noopener">FIA Document 11, page {source_page}</a>, '
                '11 September 2026.'))
        description = ul([
            f"<strong>{component}:</strong> {summary} "
            f"<em>Filed reason: {reason}.</em>"
            for component, reason, summary in updates
        ]) if updates else "<p>No updates submitted for this event.</p>"
        teams.append(card(
            f'{team} &mdash; {len(updates)} declared item{"s" if len(updates) != 1 else ""}',
            description + '<details><summary>View official declaration'
            + (" and diagram" if updates else "") + "</summary>"
            + "".join(evidence) + "</details>", "bi-tools", "accent" if updates else ""))
    total = sum(len(updates) for _, _, updates in UPGRADE_SUBMISSIONS)
    updated = sum(bool(updates) for _, _, updates in UPGRADE_SUBMISSIONS)
    return f"""
<div class="stat-row">
  {stat(str(total), "Declared items", "FIA Document 11")}
  {stat(str(updated), "Teams with updates", "of eleven teams")}
  {stat(str(len(UPGRADE_SUBMISSIONS) - updated), "Nil returns", "explicit no-update submissions")}
</div>
<div class="callout">
  <strong>Friday's confirmed filing:</strong> Mercedes has the largest list with three items;
  Red Bull's two are both filed for reliability, not as pure performance upgrades.
  McLaren, Ferrari, Alpine and Cadillac account for the other five items.
</div>
<p class="src">Source: <a href="{FIA_UPGRADES_URL}" target="_blank" rel="noopener">
FIA Document 11, Car Presentation Submissions</a>, issued 11 September 2026.
All eleven teams are included. Counts refer to declared component rows, not a
ranking of performance gains or confirmation that both cars raced every item.</p>
<h2 class="sec">Team-by-team car presentation submissions</h2>
<div class="table-wrap"><table class="data">
  <thead><tr><th>Team</th><th class="num">Items</th><th>Declared areas</th><th>FIA source</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table></div>
<h2 class="sec">What changed and why</h2>
<p>The explanations below summarise each team's stated rationale, not independently
measured lap-time gains. A nil return means no updates submitted for this event;
it does not rule out setup changes or previously introduced parts.</p>
<div class="grid cols-2">{"".join(teams)}</div>
"""


def build_pages(ctx, env):
    pages = build_generic(ctx, env)
    debut = card("A new venue, not Barcelona or Jarama", """
<p><strong>No previous Formula 1 Grand Prix has been held at the Madring.</strong>
Past winners, polesitters, race lap records and current-grid starts or best finishes
at this circuit are therefore <strong>not applicable before its debut</strong>,
not missing historical research. Simulator laps and Formula 3 testing are not F1 race records.</p>
<p>Madrid's earlier Grands Prix were at <strong>Jarama</strong>, first used in 1968
and last used for a World Championship Grand Prix in 1981. Those are different-track
history; neither Jarama nor Barcelona results should be relabelled as Madring records.</p>
""" + f'<p class="src"><a href="{GUIDE_URL}" target="_blank" rel="noopener">'
        'Formula1.com circuit guide, 10 September 2026</a>.</p>', "bi-stars", "accent")
    lineup = card("Confirmed race-driver replacements", ul([
        "<strong>Liam Lawson</strong> continues alongside Max Verstappen at Red Bull for a third weekend.",
        "<strong>Yuki Tsunoda</strong> continues alongside Arvid Lindblad at Racing Bulls.",
        "<strong>Isack Hadjar</strong> remains out while recovering from his wrist injury. "
        "The team says recovery is progressing and he will support them in Madrid; no return date is asserted here.",
        "These are race-seat substitutions, not announcements of mandatory rookie FP1 outings.",
    ]) + f'<p class="src"><a href="{LINEUP_URL}" target="_blank" rel="noopener">'
          'Formula1.com / Red Bull announcement, 7 September 2026</a>.</p>',
        "bi-people", "accent")
    team_brief = card("The form carried into Madrid", ul([
        "<strong>Mercedes:</strong> Antonelli arrives after winning at Monza from P19; "
        "the new venue tests both drivers' adaptation rather than a known circuit-specific form line.",
        "<strong>Ferrari:</strong> Hamilton and Leclerc's opening-lap Monza fight and "
        "Leclerc's separate crash frame the team's response; the published preview discusses team-order questions, not an announced new policy.",
        "<strong>McLaren:</strong> Norris beat Piastri to P4 at Monza after they were allowed to race. "
        "The previous Hungary and Zandvoort wins do not guarantee the same pace here.",
        "<strong>Red Bull:</strong> Verstappen arrives from a Monza podium, with Lawson continuing to substitute.",
        "<strong>Alpine / Racing Bulls:</strong> Gasly's Monza pole became P7 in the race, ahead of "
        "Lindblad, Colapinto and Tsunoda. Madrid's new layout gives no historical basis to carry over Alpine's Monza advantage.",
    ]) + f'<p class="src"><a href="{PREVIEW_URL}" target="_blank" rel="noopener">'
          'Formula1.com Need to Know, 10 September 2026</a>. This is pre-Madrid context, '
          'not a forecast ranking or a complete eleven-team upgrade filing.</p>',
        "bi-people", "accent")
    brief = card("Madrid: FIA facts to have ready", ul([
        '<strong>Two Straight Mode zones</strong>: after T22 and after T3. '
        'The separate Overtake detection is at entry to T22, with activation 20 m after T22.',
        '<strong>Qualifying recharge: 7.5 MJ/lap</strong>, versus 9.0 MJ in free practice. '
        'Race recharge is 8.5 MJ without Overtake and 9.0 MJ with it.',
        '<strong>C2 / C3 / C4</strong> are confirmed. Slick starting pressures are '
        '26.5 psi front / 25.5 psi rear in FIA/Pirelli Issue A.',
        '<strong>T22 can cost two lap times</strong>; the SC2-to-SC1 maximum lap time '
        'is to be communicated after FP2, not a number to guess in advance.',
    ]) + '<p class="src">FIA Documents 1, 3, 5 and 6, checked 10 September 2026. '
         '<a href="circuit.html">Circuit &amp; rules</a> / '
         '<a href="powerunit.html">Power unit</a> / <a href="tyres.html">Tyres</a>.</p>',
        "bi-file-earmark-pdf", "accent")
    pages["overview"]["sub"] = (
        "Madrid's debut: published FIA aero zones, energy limits, tyre prescriptions "
        "and race-control instructions.")
    pages["overview"]["body"] = brief + LENGTH_NOTE + lineup + team_brief + pages["overview"]["body"]
    pages["notes"]["body"] = brief + LENGTH_NOTE + lineup + pages["notes"]["body"]
    pages["facts"]["body"] = LENGTH_NOTE + debut + pages["facts"]["body"]
    pages["facts"]["body"] = pages["facts"]["body"].replace(
        pending("Past winners, polesitters and weekend-specific trivia",
                "in the official preview material for the round", "bi-bar-chart"), "")
    pages["moments"] = dict(
        kicker="Debut venue · historical context",
        title="Great Moments",
        sub="Madring has no previous Grand Prix moments; Madrid's older F1 history belongs to Jarama.",
        body=debut + card("What becomes this circuit's first chapter?", """
<p>The inaugural pole, first race winner and first official race lap record can only
be established after the relevant sessions on 11–13 September. The first event's
reports will appear on <a href="news.html">Weekend News</a> and its classifications on
<a href="results.html">Results</a>; no historical winner list is being invented.</p>
""", "bi-flag"))
    pages["rookies"]["body"] = lineup + pages["rookies"]["body"].replace(
        pending("Reserve or replacement driver changes", "as teams confirm them", "bi-people"), "")
    pages["teams"] = dict(
        kicker="Team watch · 10 September",
        title="Team Watch & News",
        sub="Verified pre-Madrid form and the confirmed Red Bull-family substitutions.",
        body=team_brief + lineup + '<p><a href="news.html">Latest team news</a> / '
             '<a href="upgrades.html">Confirmed team upgrades and car-display procedure</a>. '
             'A news story about another circuit is background, not a Madrid component declaration.</p>')
    pages["standings"]["body"] += card("Championship permutations — 10 September snapshot", """
<p><strong>Pre-Madrid reference, not a live points calculator:</strong> Antonelli
leads Russell by 66 points; Hamilton is another 10 behind Russell.</p>
<ul>
  <li>If Russell wins for 25 points and Antonelli scores zero, the gap becomes
  <strong>41 points</strong>. Madrid is a standard, non-Sprint weekend.</li>
  <li>Hamilton must outscore Russell by <strong>more than 10 points</strong> to move
  ahead outright. A net gain of exactly 10 produces a points tie, which requires
  countback rather than automatically handing Hamilton second place.</li>
  <li>These are single-round scenarios, not a claim that the championship can be
  clinched here. Check the latest totals above before reusing this dated arithmetic.</li>
</ul>
""" + f'<p class="src"><a href="{PREVIEW_URL}" target="_blank" rel="noopener">'
        'Formula1.com Need to Know, 10 September 2026</a>, current-form section; '
        '25-point win scenario follows the '
        '<a href="https://www.formula1.com/en/results/2026/drivers" target="_blank" '
        'rel="noopener">official championship scoring</a>. No fastest-lap bonus is added.</p>',
        "bi-trophy", "accent")
    pages["h2h"] = dict(
        kicker="Team-mate battles",
        title="Head-to-Head",
        sub="Season qualifying/race scorelines, with Madrid comparisons as sessions finish.",
        body=auto_h2h(ctx))

    pages["circuit"] = dict(
        kicker="FIA Document 6 / map version 3, 10 Sep",
        title="Madring Circuit Guide",
        sub="Official active-aero zones, Overtake locations, pit-lane layout and race-control notes.",
        body=f"""
<h2 class="sec">Official FIA circuit map</h2>
{_figure("spain_fia_circuit_map_2026.png",
         "FIA Madrid circuit map with two Straight Mode zones, normal and low-grip activation, Overtake lines and sectors",
         f'<a href="{FIA_MAP_URL}#page=2" target="_blank" rel="noopener">FIA Document 6, page 2</a>; map version 3, issued 10 September 2026.')}
{LENGTH_NOTE}
<div class="stat-row">
  {stat("2", "Straight Mode zones", "active aerodynamics")}
  {stat("1", "Overtake detection point", "entry to T22")}
  {stat("57", "Scheduled race laps", "Formula1.com calendar")}
</div>
<h2 class="sec">Straight Mode activation points</h2>
<div class="table-wrap"><table class="data">
  <thead><tr><th>Zone</th><th>Normal grip (red)</th><th>Low grip (blue)</th></tr></thead>
  <tbody>
    <tr><td>A1</td><td>100 m after T22</td><td>130 m after T22</td></tr>
    <tr><td>A2</td><td>40 m after T3</td><td>90 m after T3</td></tr>
  </tbody>
</table></div>
<p>Straight Mode is the active-aero system, not the electrical Overtake allowance.
The map places <strong>Overtake detection at entry to T22</strong> and
<strong>activation 20 m after T22</strong>. The PU sheet identifies loops L24/L25
but still marks their absolute lap distances <strong>TBC</strong>.</p>
<div class="grid cols-2">
  {card("Sector and timing references", ul([
      "Map sectors: <strong>1.839 / 2.049 / 1.526 km</strong>.",
      "Intermediate 1: <strong>85 m before T7</strong>; intermediate 2: <strong>40 m before T16</strong>.",
      "Speed trap: <strong>160 m before T5</strong>.",
  ]), "bi-stopwatch")}
  {card("Track limits and escape routes", ul([
      "<strong>Turn 22:</strong> during lap-time classified sessions, failing to negotiate the corner can lead the Stewards to invalidate the current and immediately following lap.",
      "<strong>T1/T2 runoff:</strong> a car missing T2 to the right of the yellow line must stay right of it and rejoin at the far end, after T2.",
      "<strong>T5/T5A runoff:</strong> stay right of the yellow line and rejoin at T6.",
      "<strong>Inside T11:</strong> rejoin to the left of the polystyrene block.",
  ]), "bi-signpost-split", "accent")}
</div>
<div class="grid cols-2">
  {card("Practice starts and the narrow pit lane", ul([
      "No practice starts at the normal pit exit or during qualifying.",
      "Cars on track at the FP2 end signal may complete <strong>two additional laps</strong>, solely to make a grid practice start on each.",
      "Race reconnaissance has a specific practice-start area before Safety Car Line 2 on the pit-exit road; the separate routing in paragraph 13.6 applies.",
      "During the race, a released car must safely merge into the fast lane as soon as possible, slowing to let existing fast-lane traffic pass if needed. All parts of the car must cross the separating line.",
  ]), "bi-cone-striped")}
  {card("Race-control details", ul([
      "The SC2-to-SC1 maximum time for qualifying and race reconnaissance will be communicated <strong>after FP2</strong>; Document 5 gives no numeric maximum yet.",
      "A double-yellow sector in free practice means deletion of that lap time.",
      "Blue-flag pre-warning: <strong>3.0 s</strong>; blue panels/cockpit lights: <strong>1.2 s</strong>.",
      "After a suspension the Safety Car leaves the pits one minute before resumption and waits <strong>before T18</strong>.",
      "Turn 12 light panels are mirrored; panel 6 has two physical panels, and panel 11 is mirrored on panel 10.",
  ]), "bi-flag")}
</div>
<p class="src">Operational rules: <a href="{FIA_NOTES_URL}" target="_blank" rel="noopener">FIA Document 5,
Race Director's Competition Notes</a>, 10 September, paragraphs 1, 2, 9, 13, 16, 22, 25&ndash;27.
These are instructions, not individual stewards' decisions.</p>
<h2 class="sec">Pit-lane and recovery reference maps</h2>
{_figure("spain_fia_pit_lane_2026.png",
         "FIA Madrid pit-lane drawing showing garages, Safety Car lines, entry and exit signals",
         f'<a href="{FIA_MAP_URL}#page=4" target="_blank" rel="noopener">FIA Document 6, page 4</a>, pit-lane drawing version 1, 10 September.')}
<details>
  <summary>Official emergency-exit and refuge map</summary>
  {_figure("spain_fia_emergency_exits_2026.png",
           "FIA Madrid emergency-exit map with left and right exits and drive-in and push-in refuges",
           f'<a href="{FIA_MAP_URL}#page=3" target="_blank" rel="noopener">FIA Document 6, page 3</a>, emergency-exit map version 1, 9 September.')}
</details>
""")

    pages["powerunit"] = dict(
        kicker="FIA Document 3, 10 Sep",
        title="Power Unit & Override",
        sub="Madrid's confirmed recharge limits and ERS-K curves, with unresolved distances explicitly marked.",
        body=f"""
<h2 class="sec">Official FIA power-and-energy sheet</h2>
{_figure("spain_fia_power_unit_2026.png",
         "FIA Madrid power-unit table: recharge by session, 3206 metre power-limited distance, ERS-K curves and exception sectors",
         f'<a href="{FIA_PU_URL}#page=2" target="_blank" rel="noopener">FIA Document 3, page 2</a>, issued 10 September 2026 at 15:53.')}
<div class="callout accent">
  <strong>Qualifying is not the FP energy allowance:</strong> maximum recharge drops
  from <strong>9.0 MJ in free practice to 7.5 MJ in qualifying</strong>, even though
  both use the Base &ndash; Overtake power curve. Recharge energy and the
  speed-dependent electrical power ceiling are separate limits.
</div>
<h2 class="sec">Maximum recharge per lap (C5.2.10)</h2>
<div class="table-wrap"><table class="data">
  <thead><tr><th>Session / condition</th><th class="num">Maximum recharge</th></tr></thead>
  <tbody>
    <tr><td>Race &mdash; Overtake not active</td><td class="num">8.5 MJ</td></tr>
    <tr><td>Race &mdash; Overtake active</td><td class="num">9.0 MJ</td></tr>
    <tr><td>Qualifying</td><td class="num">7.5 MJ</td></tr>
    <tr><td>Free practice</td><td class="num">9.0 MJ</td></tr>
    <tr><td>Out-laps other than in the race</td><td class="num">9.0 MJ</td></tr>
  </tbody>
</table></div>
<div class="grid cols-2">
  {card("Power curves and reduction rate", ul([
      "Power-limited distance: <strong>3206 m</strong>; maximum PU power-reduction rate: <strong>100 kW/s</strong> (C5.12.8).",
      "Main race overtaking zone: <strong>Base &ndash; Standard</strong> without Overtake, <strong>Base &ndash; Overtake</strong> when active.",
      "The alternative <strong>Alt 1</strong> race curve applies in <strong>T5&ndash;T22, 1500&ndash;5100 m*</strong> (C5.2.8iii). The asterisk is reproduced from the FIA table, without inventing a qualification.",
      "Every practice session, including qualifying, uses <strong>Base &ndash; Overtake</strong> throughout the lap.",
  ]), "bi-graph-up-arrow", "accent")}
  {card("Exceptions and qualifying-only windows", ul([
      "At the start of a Power Limited Pending period, up to <strong>350 kW</strong> reduction is permitted in <strong>T15&ndash;T16 (3600&ndash;3800 m)</strong>, <strong>T18&ndash;T19 (4100&ndash;4300 m)</strong> and <strong>T20&ndash;T21 (4600&ndash;4800 m)</strong>.",
      "The additional <strong>exit-T22 window, 5100&ndash;5300 m</strong>, permits 350 kW reduction in qualifying only.",
      "The <strong>MGU-K power-reduction reset at exit T22, 5200&ndash;5400 m</strong>, is also qualifying only.",
      "Bracketed windows are labelled SQ/Q in the FIA template; Madrid has a standard weekend, with no Sprint Qualifying.",
      "No higher-speed-threshold sector is specified under C5.12.7; that row contains dashes.",
  ]), "bi-lightning-charge")}
</div>
<div class="callout watch">
  <strong>Overtake: confirmed gap, unresolved absolute distances.</strong>
  The detection gap is <strong>1.0 s</strong>. The PU sheet gives detection loop
  <strong>L24</strong> and activation loop <strong>L25</strong>, but both lap-distance
  values remain <strong>TBC</strong>. The later circuit map locates detection at entry
  to T22 and activation 20 m after T22; those relative locations do not supply missing
  absolute metre values. <a href="circuit.html">View the FIA circuit map</a>.
</div>
{LENGTH_NOTE}
<p class="src">Source: <a href="{FIA_PU_URL}" target="_blank" rel="noopener">FIA Power Unit Information,
Document 3</a>. Tables and graph visually checked against the original PDF, not inferred from another circuit.</p>
<h2 class="sec">Driver-by-driver component use</h2>
<p>The driver-by-driver <a href="{FIA_BASE}pu_elements_used_per_driver_up_to_now.pdf"
target="_blank" rel="noopener">FIA PU-elements-used report</a> is now published;
its original table is reproduced in the official screenshots below. A component-use
report is not itself a penalty ruling. New-element declarations and any sanctions
must be read from their own filings; Italy's component totals are not reused.</p>
""")

    pages["tyres"] = dict(
        kicker="FIA / Pirelli Issue A",
        title="Tyres & Strategy",
        sub="Confirmed C2/C3/C4 allocation, axle-specific pressures and Pirelli's Madrid preview.",
        body=f"""
<div class="stat-row">
  {stat("C2", "Hard", "mandatory race tyre")}
  {stat("C3", "Medium", "mandatory race tyre")}
  {stat("C4", "Soft", "Q3 tyre")}
  {stat("25 s", "Estimated pit-stop loss", "Pirelli preview, not measured")}
</div>
{_figure("spain_pirelli_tyres_2026.webp",
         "Complete Pirelli Madrid preview with C2 C3 C4 compounds, tyre demands, starting pressures and camber limits",
         f'Official Pirelli event infographic from <a href="{PIRELLI_URL}" target="_blank" rel="noopener">Formula1.com</a>; uncropped, including the bottom prescription rows.')}
<div class="callout">
  <strong>Debut-venue strategy:</strong> Pirelli rates track evolution 5/5, lateral
  demand 4/5 and asphalt abrasion 2/5. Its 25-second pit-stop-loss figure is a preview
  estimate, not observed race data. Friday running is still needed to establish
  representative degradation and stint lengths.
</div>
<h2 class="sec">FIA tyre prescriptions (Document 1, Issue A)</h2>
{_figure("spain_fia_pirelli_prescriptions_2026.png",
         "FIA Pirelli Madrid Issue A with slick intermediate and wet pressures, camber, cooling curves and blanket limits",
         f'<a href="{FIA_TYRES_URL}#page=2" target="_blank" rel="noopener">FIA Document 1, page 2</a>, issued 9 September 2026 at 13:56; prescription document version 5, Issue A.')}
<div class="table-wrap"><table class="data">
  <thead><tr><th>Tyre</th><th>Axle</th><th class="num">Minimum start</th>
    <th class="num">Expected stabilised running</th><th class="num">Camber limit</th></tr></thead>
  <tbody>
    <tr><td>Slick</td><td>Front</td><td class="num">26.5 psi</td><td class="num">&ge;27.5 psi</td><td class="num">-2.75&deg;</td></tr>
    <tr><td>Slick</td><td>Rear</td><td class="num">25.5 psi</td><td class="num">&ge;26.5 psi</td><td class="num">-1.5&deg;</td></tr>
    <tr><td>Intermediate</td><td>Front</td><td class="num">28.0 psi</td><td class="num">&ge;29.0 psi</td><td class="num">-3&deg;</td></tr>
    <tr><td>Intermediate</td><td>Rear</td><td class="num">26.5 psi</td><td class="num">&ge;27.5 psi</td><td class="num">-2&deg;</td></tr>
    <tr><td>Wet</td><td>Front</td><td class="num">27.0 psi</td><td class="num">&ge;29.0 psi</td><td class="num">-3&deg;</td></tr>
    <tr><td>Wet</td><td>Rear</td><td class="num">25.0 psi</td><td class="num">&ge;27.5 psi</td><td class="num">-2&deg;</td></tr>
  </tbody>
</table></div>
<p>C2 and C3 are the designated mandatory race tyres; C4 is the Q3 tyre.
Maximum heating is <strong>two hours</strong>: up to <strong>70&deg;C</strong> for
slicks and intermediates, <strong>40&deg;C</strong> for wets. These are tyre-surface
temperatures, not blanket-controller settings. FIA/Pirelli may revise the prescriptions
during the weekend; the preview flags possible changes after FP2.</p>
{pending("Measured long-run degradation and stint strategy", "after representative practice running", "bi-graph-down")}
<h2 class="sec">Stint predictor and remaining tyre sets</h2>
<p>No Madrid F1 practice or race sample exists before Friday running. The confirmed
compound nomination and pressure prescription do not establish an optimal pit window,
degradation rate or each driver's remaining new/used sets. A lap-number strategy
prediction and a post-qualifying tyre-set table await their own evidence;
Italy's counts and stint lengths are not transferred here.</p>
""")

    pages["upgrades"] = dict(
        kicker="FIA Document 11, 11 Sep",
        title="Car Development & Upgrades",
        sub="Ten declared items across six teams, five nil returns, and every team's official submission.",
        body=_upgrade_filing() + card("Friday car presentation: confirmed procedure", ul([
            "<strong>12:00&ndash;13:00 Friday, Madrid local time (13:00&ndash;14:00 Tallinn)</strong>.",
            "One car from each team must be outside in its pit-stop position; the other must be available to view inside the garage.",
            "If only one car carries major new aerodynamic/bodywork components intended for this event, that is the car which must be displayed to media.",
            "The outside car may be used for pit-stop practice but must return to its display position when practice stops.",
        ]) + f'<p class="src"><a href="{FIA_DISPLAY_URL}" target="_blank" rel="noopener">'
              'FIA Document 4, Car Display Procedure</a>, 10 September 2026.</p>',
            "bi-tools", "accent"),
    )
    rules = card("Published race-control watchlist", ul([
        "Turn 22 can affect both the current and following lap time in lap-time classified sessions.",
        "Double-yellow sectors in free practice trigger lap-time deletion.",
        "The narrow-pit-lane merge rule requires the released car to yield to existing fast-lane traffic when necessary.",
        "The qualifying/reconnaissance SC2-to-SC1 maximum time is to be announced after FP2.",
    ]) + f'<p class="src"><a href="{FIA_NOTES_URL}" target="_blank" rel="noopener">'
          'FIA Competition Notes, Document 5</a>, 10 September. These are standing instructions, '
          'not penalties already imposed. <a href="circuit.html">Full circuit notes</a>.</p>',
        "bi-flag", "accent")
    pages["penalties"] = dict(
        kicker="FIA race control",
        title="Penalties & Stewards",
        sub="Published operating rules and the automatically updated decision tracker.",
        body=rules + auto_penalties(ctx),
    )
    pages["schedule"]["body"] += card("Heat and medical status: separate evidence", """
<p>The six FIA documents discovered on 10 September contain no Madrid Heat Hazard
declaration. A hot weather forecast is not such a declaration; Monza's 31&deg;C
trigger and cooling instructions must not be treated as a Madrid ruling.
Check subsequent FIA filings during the weekend. Hadjar's team-confirmed absence
is covered on <a href="rookies.html">Rookies &amp; Line-ups</a>; it is not an inferred
medical clearance or a prognosis.</p>
""", "bi-thermometer-sun")
    return pages
