"""Madrid 2026: FIA material checked against the published PDFs on 10 September."""
from content_generic import build_pages as build_generic, pending
from f1lib import auto_penalties, card, stat, ul


FIA_BASE = "https://www.fia.com/system/files/decision-document/2026_spanish_grand_prix_-_"
FIA_MAP_URL = FIA_BASE + "competition_notes_-_circuit_map_pit_lane_drawing_and_emergency_exits_map.pdf"
FIA_PU_URL = FIA_BASE + "power_unit_information.pdf"
FIA_TYRES_URL = FIA_BASE + "competition_notes_-_pirelli_preview.pdf"
FIA_NOTES_URL = FIA_BASE + "race_directors_competition_notes.pdf"
FIA_DISPLAY_URL = FIA_BASE + "car_display_procedure.pdf"
PIRELLI_URL = ("https://www.formula1.com/en/latest/article/"
               "what-tyres-will-the-teams-and-drivers-have-for-the-2026-spanish-grand-prix."
               "2vlcVOBnZUFRCooVcqWG7n")

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


def build_pages(ctx, env):
    pages = build_generic(ctx, env)
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
    pages["overview"]["body"] = brief + LENGTH_NOTE + pages["overview"]["body"]
    pages["notes"]["body"] = brief + LENGTH_NOTE + pages["notes"]["body"]
    pages["facts"]["body"] = LENGTH_NOTE + pages["facts"]["body"]

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
<p>The six documents discovered on 10 September include the event energy sheet, but
not a driver-by-driver PU-usage or new-elements report. Those counts and any resulting
penalties remain awaiting their own filings; Italy's component totals are not reused.</p>
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
""")

    pages["upgrades"] = dict(
        kicker="FIA Document 4, 10 Sep",
        title="Car Development & Upgrades",
        sub="Car-display procedure is published; team-by-team component submissions are a separate filing.",
        body=card("Friday car presentation: confirmed procedure", ul([
            "<strong>12:00&ndash;13:00 Friday, Madrid local time (13:00&ndash;14:00 Tallinn)</strong>.",
            "One car from each team must be outside in its pit-stop position; the other must be available to view inside the garage.",
            "If only one car carries major new aerodynamic/bodywork components intended for this event, that is the car which must be displayed to media.",
            "The outside car may be used for pit-stop practice but must return to its display position when practice stops.",
        ]) + f'<p class="src"><a href="{FIA_DISPLAY_URL}" target="_blank" rel="noopener">'
              'FIA Document 4, Car Display Procedure</a>, 10 September 2026.</p>',
            "bi-tools", "accent")
        + pending("Team-by-team car presentation submissions", "with the Friday car display")
        + "<p>The display procedure does not identify individual upgrades. Component descriptions "
          "will be added from the teams' actual submissions, not inferred from this timetable.</p>",
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
    return pages
