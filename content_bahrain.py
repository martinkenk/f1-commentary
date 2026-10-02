"""2026 Bahrain Grand Prix coverage at Sepang."""
import content_generic
from f1lib import render_penalties
from upgrade_render import render_submissions


FIA_DOC_66 = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_azerbaijan_grand_prix_-_infringement_-_car_43_-_"
    "collision_with_car_10_in_turn_1.pdf"
)
F1_PENALTY_ARTICLE = (
    "https://www.formula1.com/en/latest/article/"
    "colapinto-hit-with-five-place-grid-penalty-for-bahrain-gp-in-malaysia-"
    "after-baku-collision.3gWVfzDMMr5hReiwTt1fPD"
)
F1_EVENT = "https://www.formula1.com/en/racing/2026/bahrain"
F1_AZERBAIJAN_RESULT = (
    "https://www.formula1.com/en/results/2026/races/1295/azerbaijan/race-result"
)
FIA_PU_URL = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_bahrain_grand_prix_in_malaysia_-_power_unit_information.pdf"
)
FIA_RD_NOTES_URL = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_bahrain_grand_prix_in_malaysia_-_race_directors_competition_notes.pdf"
)
FIA_CIRCUIT_MAP_URL = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_bahrain_grand_prix_in_malaysia_-_competition_notes_-_"
    "circuit_map_pit_lane_drawing_emergency_exits_map_and_red_zone.pdf"
)
FIA_TYRE_PREVIEW_URL = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_bahrain_grand_prix_in_malaysia_-_competition_notes_-_pirelli_preview.pdf"
)
FIA_ROOT = "https://www.fia.com/system/files/decision-document/2026_bahrain_grand_prix_in_malaysia_-_"
HEAT_URL = FIA_ROOT + "heat_hazard_declaration.pdf"
DISPLAY_URL = FIA_ROOT + "car_display_procedure.pdf"
VISA_URL = FIA_ROOT + "competition_visa_v2.pdf"
COMPLIANCE_URL = FIA_ROOT + "post-race_checks_on_car_number_16_2026_azerbaijan_gp.pdf"
GRID_REPORT_URL = "https://www.the-race.com/formula-1/three-drivers-facing-grid-penalties-for-f1-malaysia-return/"
MERCEDES_URL = (
    "https://www.formula1.com/en/latest/article/bring-it-on-russell-predicts-mercedes-"
    "bahrain-upgrades-could-play-in-my-favour.2MrIZO0XrStD76V1fTLAlA"
)
HISTORY_URL = "https://www.formula1.com/en/results/2009/races/844/malaysia/race-result"
UPGRADES_URL = FIA_ROOT + "car_presentation_submissions.pdf"
UPGRADES_ASSET = "fia-bahrain-48038b9202af-be68005deb6890e7"
UPGRADE_SUBMISSIONS = (
    ("McLaren", 2, (
        ("Coke/engine cover", "Circuit specific - Cooling Range",
         "New high-cooling engine-cover bodywork increases cooling massflow for Sepang and upcoming hot events."),
    )),
    ("Mercedes", 4, (
        ("Floor board", "Performance - Local Load",
         "Reprofiled horizontal elements and a new slotted vertical upper element improve pressure distribution, reduce separation and feed the rear of the car."),
        ("Floor leading edge", "Performance - Flow Conditioning",
         "Reprofiled and additional downwashing elements increase local load and outwash, improving rear-floor flow."),
        ("Floor corner", "Performance - Flow Conditioning",
         "Rearranged slots and reprofiled elements improve local load and airflow into the diffuser."),
        ("Floor body", "Performance - Local Load",
         "Reprofiled diffuser roof, sidewall and winglet seek more load and robustness across the operating range."),
        ("Rear suspension", "Performance - Local Load",
         "Reprofiled track-rod and driveshaft fairings redistribute camber to work better with the diffuser winglet and rear-drum furniture."),
        ("Rear corner", "Performance - Local Load",
         "Revised rear-drum winglet span, chord and position complement the fairings and improve rear-tyre wake control."),
        ("Rear bodywork", "Performance - Flow Conditioning",
         "Reduced volume and a steeper side-view ramp increase downwash towards the rear floor and drum."),
    )),
    ("Red Bull", 6, (
        ("Floor board", "Performance - Local Load",
         "Revised geometry above the existing floor foot adds local load while preserving flow stability behind the front tyres."),
    )),
    ("Ferrari", 8, (
        ("Diffuser", "Performance - Local Load",
         "A local outboard winglet-cascade development adds downforce across the operating range; Ferrari explicitly says it is not Sepang-specific."),
    )),
    ("Williams", 10, ()),
    ("Racing Bulls", 11, (
        ("Front wing", "Circuit specific - Balance Range",
         "A longer-chord flap for the wing introduced at Baku increases load to meet Sepang's balance requirements."),
        ("Rear wing", "Performance - Local Load",
         "Revised auxiliary/support components help the rear wing generate load more efficiently."),
    )),
    ("Aston Martin", 13, ()),
    ("Haas", 14, (
        ("Rear impact structure", "Performance - Local Load",
         "Updated geometry and an additional device provide targeted tuning of the car's characteristics for this circuit."),
    )),
    ("Audi", 16, ()),
    ("Alpine", 17, (
        ("Front corner", "Performance - Brake Cooling",
         "A trimmed front-drum exit increases brake-cooling capacity for upcoming thermally demanding tracks."),
    )),
    ("Cadillac", 19, ()),
)


def _upgrade_summary():
    return f"""
<div class="callout accent"><strong>Friday filing now confirmed:</strong>
FIA Document 12, issued 2 October at 10:03 MYT, contains <strong>14 declared
items across seven teams</strong>. Mercedes accounts for seven; Racing Bulls two;
McLaren, Red Bull, Ferrari, Haas and Alpine one each. Williams, Aston Martin,
Audi and Cadillac explicitly filed no updates. <a href="upgrades.html">Read each
team's declaration and diagram inline</a>. These are team-declared changes,
not measured lap-time gains or proof that both cars ran each part.</div>
"""

_TEAM_WATCH = [
    ("Mercedes", "Russell P1; Antonelli P5.",
     "Can both cars repeat their strong Baku points haul?"),
    ("Red Bull Racing", "Verstappen P2; Hadjar P3.",
     "Can the double-podium form put Red Bull in the win fight again?"),
    ("Ferrari", "Leclerc P4; Hamilton P6.",
     "Can Ferrari turn a pair of top-six finishes into a podium challenge?"),
    ("McLaren", "Piastri P13; Norris DNF.",
     "Can McLaren recover after leaving Baku without points?"),
    ("Racing Bulls", "Lindblad P7; Lawson P12.",
     "Can Lindblad build on seventh while Lawson moves into the points?"),
    ("Haas F1 Team", "Ocon P8; Bearman P9.",
     "Can Haas build on a two-car points finish?"),
    ("Williams", "Sainz P10; Albon DNF.",
     "Can Sainz add to his point and Albon get back to the finish?"),
    ("Audi", "Hulkenberg P11; Bortoleto P15.",
     "Can either driver turn the next finish into points?"),
    ("BWT Alpine F1 Team", "Colapinto DNF; Gasly DNF.",
     "Can Alpine complete the race after a double retirement? Colapinto also carries the confirmed five-place grid drop."),
    ("Cadillac", "Perez P14; Bottas DNF.",
     "Can both cars finish and move closer to the points?"),
    ("Aston Martin Aramco F1 Team", "Alonso DNF; Stroll DNF.",
     "Can Aston Martin avoid another double retirement?"),
]


def _carryover_notice():
    return f"""
<div class="callout accent"><strong>Confirmed grid watch:</strong>
FIA Document 66 converted Franco Colapinto's 10-second Azerbaijan Race penalty
for his Turn 1 collision with team-mate Pierre Gasly into a five-place drop at
the next race in which he participates. Formula1.com identifies that as the
Bahrain Grand Prix in Malaysia; this calendar places that event at Sepang on
4 October. This is a carry-over sanction, not a Bahrain stewards' decision.
Qualifying and the official Bahrain starting grid are still pending, so do not
state a resulting grid position.
<p class="src">Sources:
<a href="{FIA_DOC_66}" target="_blank" rel="noopener">FIA Document 66</a>;
<a href="{F1_PENALTY_ARTICLE}" target="_blank" rel="noopener">Formula1.com penalty report</a>;
<a href="{F1_EVENT}" target="_blank" rel="noopener">Formula1.com event guide</a>.</p>
</div>"""


def _team_watch_section():
    rows = "".join(
        f"<tr><th scope=\"row\">{team}</th><td>{baku}</td><td>{watch}</td></tr>"
        for team, baku, watch in _TEAM_WATCH
    )
    return f"""
<h2 class="sec">Baku to Sepang: team-by-team watch</h2>
<p class="lead-note">Baku's 26 September classification is the latest completed-race
reference before the Bahrain Grand Prix at Sepang on 4 October. Results below are
one-race form, not season totals; the Sepang prompts are questions, not predictions.</p>
<div class="table-wrap"><table class="data">
  <thead><tr><th>Team</th><th>Baku Race</th><th>Sepang watch</th></tr></thead>
  <tbody>{rows}</tbody>
</table></div>
<p class="src">Source: <a href="{F1_AZERBAIJAN_RESULT}" target="_blank" rel="noopener">
Formula1.com official Azerbaijan Race classification</a>. Colapinto's separate
carry-over sanction is detailed on this site's <a href="penalties.html">Penalties
&amp; Decisions page</a>.</p>
"""


def _tl(year, title, text):
    return (
        f'<div class="tl-item"><div class="tl-year">{year}</div>'
        f'<div class="tl-title">{title}</div><p>{text}</p></div>'
    )


_MOMENTS = [
    ("1999", "Sepang's debut — and an instant classic",
     "The Sepang International Circuit — a purpose-built Hermann Tilke design "
     "commissioned as part of Malaysia's 1990s industrialisation push — opened "
     "with the very first Malaysian Grand Prix. Michael Schumacher, returning "
     "from a broken leg suffered mid-season, drove a supporting role to help "
     "Ferrari team-mate Eddie Irvine's title bid; Irvine won as Ferrari locked "
     "out the front two places on his return."),
    ("2009", "Button wins a rain-shortened race",
     "Jenson Button won for Brawn GP as torrential rain stopped the Malaysian "
     "Grand Prix. Half points were awarded. This was Brawn's second race and "
     "second win, not its debut: the team had already won in Australia."),
    ("2012", "Alonso's charge from P8",
     "A wet-dry Malaysian GP saw Fernando Alonso climb from eighth on the grid "
     "to win for Ferrari, benefiting from timing his intermediate and slick "
     "stops around the changing conditions — a reminder of how quickly Sepang's "
     "tropical weather can rewrite a race."),
    ("2017", "Verstappen's low-key statement win",
     "Starting third, Max Verstappen took his second Grand Prix victory at "
     "what proved to be Sepang's last race on the calendar before Malaysia "
     "dropped off the schedule — a result this circuit's return to F1 in 2026 "
     "now follows almost a decade later."),
]


def _powerunit_section():
    return f"""
<h2 class="sec">FIA Power Unit Information — page 2</h2>
<figure class="circuit-fig">
  <img src="../assets/fia-bahrain-776bb5f3f154-50419bb38d97434c-p2.png"
       alt="FIA Sepang power-unit information: recharge limits, power curves, exception sectors and Overtake lines"
       class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen">
  <figcaption>Official FIA Power Unit Information, page 2, retrieved 1 October 2026.
  <a href="{FIA_PU_URL}#page=2" target="_blank" rel="noopener">Open the original PDF</a>.
  The event-specific table and diagram were visually transcribed from this page.</figcaption>
</figure>
<div class="callout watch">
  <strong>Keep recharge and deployment separate:</strong> the MJ figures below are
  maximum recharge per lap; the 100 kW/s rate and speed-dependent ERS-K curves are
  different limits. The FIA marks both absolute Overtake timing-loop distances TBC.
</div>
<h2 class="sec">Maximum recharge per lap (Article C5.2.10)</h2>
<div class="table-wrap"><table class="data">
  <thead><tr><th>Session / condition</th><th class="num">Maximum recharge</th></tr></thead>
  <tbody>
    <tr><td>Race — Overtake not active</td><td class="num">8.5 MJ</td></tr>
    <tr><td>Race — Overtake active</td><td class="num">9.0 MJ</td></tr>
    <tr><td>Qualifying</td><td class="num">7.5 MJ</td></tr>
    <tr><td>Free practice</td><td class="num">9.0 MJ</td></tr>
    <tr><td>Out-laps other than in the Race</td><td class="num">9.0 MJ</td></tr>
  </tbody>
</table></div>
<div class="grid cols-2">
  {content_generic.card("Power limits and ERS-K curves", content_generic.ul([
      "Power-limited distance: <strong>3365 m</strong>; maximum PU power-reduction rate: <strong>100 kW/s</strong> (Article C5.12.8).",
      "Sprint and Race, main Overtaking Zones: <strong>Base — Standard</strong> with Overtake inactive and <strong>Base — Overtake</strong> when active.",
      "The alternative <strong>Alt 1</strong> curve applies in <strong>T4–T7 (1550–2500 m)</strong> and <strong>T9–T14 (3100–4100 m)</strong> (Article C5.2.8iii).",
      "Every practice session, including qualifying, uses <strong>Base — Overtake</strong> throughout the lap.",
  ]), "bi-graph-up-arrow", "accent")}
  {content_generic.card("Power-reduction exceptions (Article C5.12.4)", content_generic.ul([
      "Up to <strong>350 kW</strong> reduction is permitted at the start of a Power Limited Pending period in the following windows:",
      "<strong>T1–T2 (600–750 m)</strong>; <strong>T5–T7 (1900–2500 m)</strong>; <strong>T9–T11 (3100–3400 m)</strong>; <strong>T12–T13 (3750–4000 m)</strong>.",
      "The bracketed <strong>exit T15 (5050–5300 m)</strong> entry is marked for Sprint Qualifying and Qualifying only; this calendar has a standard weekend.",
  ]), "bi-lightning-charge")}
</div>
<h2 class="sec">MGU-K reset and speed-threshold windows</h2>
<div class="grid cols-2">
  {content_generic.card("Permitted MGU-K power-reduction resets (Article C5.12.5)", content_generic.ul([
      "<strong>Exit T5: 1950–2100 m</strong>.",
      "<strong>Exit T6: 2150–2350 m</strong>.",
      "The bracketed <strong>exit T15: 5200–5500 m</strong> reset is marked for Sprint Qualifying and Qualifying only; this calendar has a standard weekend.",
  ]), "bi-lightning-charge")}
  {content_generic.card("Higher-speed-threshold sectors (Article C5.12.7)", content_generic.ul([
      "<strong>T5–T6: 1750–2200 m, 270 km/h</strong>.",
      "<strong>T12–T13: 3700–3900 m, 270 km/h</strong>.",
  ]), "bi-speedometer2")}
</div>
<div class="callout accent">
  <strong>Electrical Overtake timing:</strong> detection gap <strong>1.0 s</strong>;
  detection line <strong>5110 m (TBC), loop L18</strong>; activation line
  <strong>5160 m (TBC), loop L19</strong>. L18/L19 are timing-loop identifiers, not
  corner numbers. These distances and their TBC status are from this event's FIA PU
  sheet; the Circuit Map v4 also labels the relative Turn 15 locations.
  <a href="circuit.html">See the separate active-aero Straight Mode map.</a>
</div>
<p class="src">Source: <a href="{FIA_PU_URL}#page=2" target="_blank" rel="noopener">
FIA Power Unit Information, page 2</a>. Values and the source version were read from
the published screenshot; retrieval time is not treated as the document's issue date.</p>
"""


def _circuit_map_section():
    return f"""
<h2 class="sec">FIA Circuit Map v4 — Straight Mode and race-control lines</h2>
<figure class="circuit-fig">
  <img src="../assets/fia-bahrain-824d565e237a-0490017fd5eda554-p2.png"
       alt="FIA Sepang circuit map v4 showing normal- and low-grip Straight Mode zones, sectors, timing lines and Overtake markers"
       class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen">
  <figcaption>FIA Circuit Map v4, issued 1 October 2026, page 2.
  <a href="{FIA_CIRCUIT_MAP_URL}#page=2" target="_blank" rel="noopener">Open the original PDF</a>.
  This revised event map is separate from the Formula1.com track guide.</figcaption>
</figure>
<div class="table-wrap"><table class="data compact">
  <thead><tr><th>Straight Mode zone</th><th>Normal-grip activation</th><th>Low-grip activation</th></tr></thead>
  <tbody>
    <tr><td>A1</td><td>65 m after T15</td><td>85 m after T15</td></tr>
    <tr><td>A2</td><td>10 m after T3</td><td>50 m after T3</td></tr>
    <tr><td>A3</td><td>65 m after T8</td><td>95 m after T8</td></tr>
    <tr><td>A4</td><td>65 m after T14</td><td>80 m after T14</td></tr>
  </tbody>
</table></div>
<p>The same FIA map lists Overtake detection 45 m before the exit of T15 and
activation at the exit of T15. The separate Power Unit Information sheet gives
absolute detection and activation distances as TBC; see <a href="powerunit.html">
the event-specific energy map</a> rather than treating active-aero zones as electrical
Overtake zones.</p>
<p class="src">The map also specifies sectors of 1.435 / 1.839 / 2.269 km, I1 145 m
before T4, I2 at the entry to T10, and the speed trap 205 m before T15. Circuit
centreline length: 5.543 km. Source: FIA Circuit Map v4, page 2.</p>
"""


def _race_control_notes():
    return f"""
<h2 class="sec">Race-control notes issued 1 October</h2>
<ul>
  <li>The maximum time between SC2 and SC1 applies on every lap during and after
  qualifying, including in/out laps during race reconnaissance while pit exit is open.
  The FIA says teams will be informed of the numerical limit after FP2; do not invent
  a value.</li>
  <li>During any LTCS, failing to negotiate Turn 15 invalidates that lap time; the
  Stewards may also invalidate the immediately following lap time.</li>
  <li>If qualifying is interrupted with less than 90 seconds remaining, that period
  will not be resumed.</li>
  <li>The Race Director notes place the Article B7.2.1 detection line at Safety Car
  Line 1; the separate PU map lists its absolute L18/L19 Overtake distances as TBC.
  Keep those source labels distinct pending clarification.</li>
  <li>Passing to the right of the pit-entry bollard counts as entering the pit lane.
  On a suspended race's resumption the Safety Car waits before Turn 12.</li>
  <li>For Safety Car deployment, trackside light panels show SC; waved yellow flags
  and physical SC boards are not used at this competition. Follow the official
  deployment and lights-off messages rather than expecting the usual board procedure.</li>
</ul>
<p class="src">Sources: <a href="{FIA_RD_NOTES_URL}#page=2" target="_blank" rel="noopener">
FIA Race Director's Competition Notes, page 2</a>;
<a href="{FIA_RD_NOTES_URL}#page=5" target="_blank" rel="noopener">page 5</a>;
<a href="{FIA_RD_NOTES_URL}#page=6" target="_blank" rel="noopener">page 6</a>;
<a href="{FIA_RD_NOTES_URL}#page=7" target="_blank" rel="noopener">page 7</a>.
Read from the retrieved original-page screenshots.</p>
"""


def _tyre_prescription_section():
    return f"""
<h2 class="sec">FIA tyre prescriptions — page 2</h2>
<figure class="circuit-fig">
  <img src="../assets/fia-bahrain-d8d466a384bc-e4f79eb595c9a4c7-p2.png"
       alt="FIA Pirelli preview page showing Sepang compounds, mandatory race and Q3 tyres, pressure and camber prescriptions"
       class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen">
  <figcaption>Official FIA competition notes — Pirelli preview, page 2, retrieved
  1 October 2026. <a href="{FIA_TYRE_PREVIEW_URL}#page=2" target="_blank" rel="noopener">
  Open the original PDF</a>. These event prescriptions are distinct from Pirelli's
  full preview infographic above.</figcaption>
</figure>
<p><strong>Mandatory race tyres:</strong> C2 and C3. <strong>Q3 tyre:</strong> C4.
The compounds are C2 Hard, C3 Medium and C4 Soft; these nominations are not a
driver-by-driver new/used race-set inventory.</p>
<div class="table-wrap"><table class="data compact">
  <thead><tr><th>Tyre type</th><th>Axle</th><th class="num">Minimum starting pressure</th>
    <th class="num">Expected stabilized running pressure</th><th class="num">Camber limit</th></tr></thead>
  <tbody>
    <tr><td>Slick</td><td>Front</td><td class="num">25.0 psi</td><td class="num">≥25.5 psi</td><td class="num">−3°</td></tr>
    <tr><td>Slick</td><td>Rear</td><td class="num">24.5 psi</td><td class="num">≥25.0 psi</td><td class="num">−1.75°</td></tr>
    <tr><td>Intermediate</td><td>Front</td><td class="num">26.0 psi</td><td class="num">≥26.5 psi</td><td class="num">−3.25°</td></tr>
    <tr><td>Intermediate</td><td>Rear</td><td class="num">25.5 psi</td><td class="num">≥26.0 psi</td><td class="num">−2.25°</td></tr>
    <tr><td>Wet</td><td>Front</td><td class="num">24.0 psi</td><td class="num">≥26.5 psi</td><td class="num">−3.25°</td></tr>
    <tr><td>Wet</td><td>Rear</td><td class="num">23.5 psi</td><td class="num">≥26.0 psi</td><td class="num">−2.25°</td></tr>
  </tbody>
</table></div>
<div class="grid cols-2">
  {content_generic.card("Cold-pressure cooling curve", content_generic.ul([
      "Front: <strong>P<sub>front</sub> = (T − 70) × 0.124 + P<sub>start,front</sub></strong>.",
      "Rear: <strong>P<sub>rear</sub> = (T − 70) × 0.122 + P<sub>start,rear</sub></strong>.",
      "T is tyre tread/sidewall temperature in °C; Pstart is the minimum starting pressure for that axle.",
  ]), "bi-thermometer-half")}
  {content_generic.card("Tyre heating and verification", content_generic.ul([
      "Maximum tyre heating time is <strong>2 hours</strong>; the FIA notes refer to tread and sidewall temperatures, not blanket or controller set-points.",
      "Slicks and intermediates: maximum <strong>70°C</strong>; wets: maximum <strong>40°C</strong>.",
      "Starting pressure, cold-pressure cooling curves, re-heat pressures, EOS camber and tyre temperature/time in blankets are listed for FIA checks.",
      "These prescriptions do not supply a race-set count; the shared inventory section reports the latest source status separately.",
  ]), "bi-clipboard-check")}
</div>
<p class="src">Source: <a href="{FIA_TYRE_PREVIEW_URL}#page=2" target="_blank" rel="noopener">
FIA competition notes — Pirelli preview, page 2</a>; visually read from the original
page screenshot. Pirelli's full Formula1.com infographic remains above and is not
replaced by this FIA table.</p>
"""


def _moments_section():
    return f"""
<div class="callout">
  Sepang last hosted a round in 2017; the venue returns to the calendar for
  2026 as the new home of the Bahrain Grand Prix. Four verified moments from
  its original 1999&ndash;2017 run as the Malaysian Grand Prix, for use when
  live action goes quiet.
</div>
<div class="timeline">
  {''.join(_tl(y, t, x) for y, t, x in _MOMENTS)}
</div>
<p class="src">Sources:
<a href="{F1_EVENT}" target="_blank" rel="noopener">Formula1.com event guide</a>
(circuit history FAQ); race facts cross-checked against the checksum-verified
F1DB circuit-history record on this site's Facts &amp; Records page.
<a href="{HISTORY_URL}" target="_blank" rel="noopener">Official 2009 Malaysian results</a>.</p>
"""


def _heat_notice():
    return f"""
<div class="callout watch"><strong>FIA Heat Hazard declared for the Race.</strong>
Document 3, issued 30 September at 19:30, cites an official forecast Heat Index
greater than <strong>31.0°C</strong> at some time during the Race under Article
B1.5.10. Heat Index is not simply ambient temperature; this is an official
declaration, not a conclusion drawn from this site's weather forecast.
<a href="{HEAT_URL}" target="_blank" rel="noopener">Original declaration</a>.</div>
"""


def _pu_inventory():
    rows = (
        ("81", "Oscar Piastri", 4, 3, 3, 2, 3, 3, 4),
        ("1", "Lando Norris", 4, 3, 3, 2, 3, 4, 4),
        ("63", "George Russell", 4, 4, 4, 3, 3, 3, 5),
        ("12", "Kimi Antonelli", 5, 3, 3, 2, 4, 4, 5),
        ("3", "Max Verstappen", 4, 4, 4, 3, 3, 3, 5),
        ("6", "Isack Hadjar", 6, 6, 6, 4, 4, 4, 7),
        ("16", "Charles Leclerc", 4, 4, 4, 3, 3, 3, 6),
        ("44", "Lewis Hamilton", 4, 4, 4, 3, 3, 3, 6),
        ("23", "Alexander Albon", 5, 3, 3, 2, 3, 4, 5),
        ("55", "Carlos Sainz", 4, 4, 3, 2, 3, 4, 4),
        ("41", "Arvid Lindblad", 4, 4, 4, 2, 2, 2, 5),
        ("30", "Liam Lawson", 3, 3, 3, 2, 2, 2, 5),
        ("18", "Lance Stroll", 5, 6, 3, 5, 7, 6, 8),
        ("14", "Fernando Alonso", 5, 5, 3, 5, 7, 6, 9),
        ("31", "Esteban Ocon", 4, 4, 4, 3, 3, 3, 5),
        ("87", "Oliver Bearman", 4, 4, 4, 4, 4, 4, 4),
        ("27", "Nico Hulkenberg", 4, 4, 4, 3, 2, 2, 5),
        ("5", "Gabriel Bortoleto", 3, 3, 3, 3, 3, 3, 5),
        ("10", "Pierre Gasly", 4, 3, 3, 2, 3, 3, 5),
        ("43", "Franco Colapinto", 4, 3, 2, 2, 3, 3, 4),
        ("11", "Sergio Perez", 4, 4, 3, 3, 3, 3, 4),
        ("77", "Valtteri Bottas", 3, 3, 3, 3, 3, 3, 3),
    )
    body = "".join("<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>" for row in rows)
    return f"""
<h2 class="sec">PU elements used — Friday 08:30 snapshot</h2>
<p>FIA Document 9, issued 2 October at 08:30 MYT, records season-to-date usage,
<strong>not remaining allocation or final post-Sepang totals</strong>. Counts
alone do not establish a new event penalty; use the relevant stewards' ruling.
ICE: engine; TC: turbocharger; EXH: exhaust; MGU-K: kinetic motor-generator;
ES: energy store; PU-CE: control electronics; PU-ANC: ancillary components.</p>
<div class="table-wrap"><table class="data compact" id="sepang-pu-inventory">
<thead><tr><th>No.</th><th>Driver</th><th>ICE</th><th>TC</th><th>EXH</th>
<th>MGU-K</th><th>ES</th><th>PU-CE</th><th>PU-ANC</th></tr></thead>
<tbody>{body}</tbody></table></div>
<p class="src">All 22 rows visually reviewed against
<a href="{FIA_ROOT}pu_elements_used_per_driver_up_to_now.pdf#page=2"
target="_blank" rel="noopener">FIA Document 9, page 2</a>; the full screenshot
is in the source reader below.</p>
"""


def _reported_grid_watch():
    return f"""
<div class="callout"><strong>Reported PU grid watch — not yet event rulings:</strong>
The Race's 1 October report says Racing Bulls announced a back-of-grid start
for Arvid Lindblad after planned new PU components. Isack Hadjar said he expects
a five-place drop. Keep both separate from Colapinto's already-issued carry-over
decision: this review found no Sepang stewards' ruling specifying their elements
or final grid positions. The official decisions and starting grid take precedence.
<a href="{GRID_REPORT_URL}" target="_blank" rel="noopener">Team/driver reports</a>.</div>
"""


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    notice = _carryover_notice()
    pages["overview"]["body"] = notice + pages["overview"]["body"]
    pages["notes"]["body"] = notice + pages["notes"]["body"]
    for slug in ("overview", "schedule", "notes"):
        pages[slug]["body"] = _heat_notice() + pages[slug]["body"]
    for slug in ("overview", "notes", "powerunit"):
        pages[slug]["body"] = _reported_grid_watch() + pages[slug]["body"]

    pending_powerunit = content_generic.pending(
        "The FIA power-unit and energy-map document for this event",
        "with the event documents in the race week",
    )
    powerunit = pages["powerunit"]
    if pending_powerunit not in powerunit["body"]:
        raise ValueError("Could not locate Sepang's event-specific power-unit placeholder")
    unpublished_map_copy = (
        "for every individual event — that is where the numbers below come from once it is issued."
    )
    if unpublished_map_copy not in powerunit["body"]:
        raise ValueError("Could not locate Sepang's generic power-unit map notice")
    powerunit["body"] = powerunit["body"].replace(
        unpublished_map_copy,
        "for every individual event. The published Sepang map is transcribed below; "
        "its TBC entries remain explicit.",
        1,
    ).replace(pending_powerunit, _powerunit_section(), 1)
    powerunit["kicker"] = "FIA Power Unit Information · page 2 visually reviewed"
    powerunit["sub"] = (
        "Sepang's event-specific recharge, ERS-K and Overtake limits; TBC line distances "
        "remain as published."
    )

    pages["circuit"]["body"] += _circuit_map_section() + _race_control_notes()
    pages["tyres"]["body"] += _tyre_prescription_section()
    pages["tyres"]["body"] += """
<h2 class="sec">What the full Pirelli poster tells us</h2>
<p>The preview estimates <strong>22.5 seconds pit-stop loss</strong>, not stationary
service time. Its five-point ratings are traction 3, braking 4, tyre stress 4,
asphalt abrasion 4, asphalt grip 2, lateral demand 4 and track evolution 4.
These event-preview ratings supersede the earlier August description of medium
relative stress. Thermal management on both axles and low initial grip are the
main preparation questions.</p>
<p><strong>Strategy before practice:</strong> prepare one- and two-stop scenarios,
but do not borrow Baku's low-wear windows or label an invented stop lap as Pirelli
guidance. No event-specific race-strategy window or post-qualifying remaining-set
chart was found in this 1 October pre-practice review. Both need checking again
after running; the source-linked preview above is not a race-set inventory.</p>
"""
    pages["notes"]["body"] = (
        '<div class="callout accent"><strong>Sepang FIA power map:</strong> '
        'race recharge is 8.5 MJ with Overtake inactive / 9.0 MJ active; qualifying '
        'is 7.5 MJ, free practice and non-race out-laps 9.0 MJ. Power-limited distance '
        'is 3365 m at 100 kW/s. Detection/activation are 5110/5160 m, both TBC '
        '(L18/L19), with a 1.0 s detection gap. <a href="powerunit.html">Full map '
        'and exceptions</a>.</div>' + _race_control_notes() + pages["notes"]["body"]
    )
    team_placeholder = content_generic.pending(
        "Team-by-team weekend storylines", "in the week before the race"
    )
    if team_placeholder not in pages["teams"]["body"]:
        raise ValueError("Could not locate Sepang's pre-race team-storyline placeholder")
    pages["teams"]["body"] = pages["teams"]["body"].replace(
        team_placeholder, _team_watch_section(), 1
    )
    pages["teams"]["sub"] = (
        "Baku's latest results and evidence-led questions for the 4 October "
        "Bahrain Grand Prix at Sepang."
    )
    upgrades = f"""
<h2 class="sec">Mercedes package: the filing behind the development story</h2>
<p>Formula1.com's 1 October report quotes Russell expecting Mercedes' Sepang
upgrade package to help on more conventional circuits, after strong performance
at Baku and Monza. Document 12 now confirms seven component rows spanning the
floor, rear suspension, rear corner and rear bodywork. The intended benefits
remain team claims, not an established lap-time gain.</p>
<p class="src"><a href="{MERCEDES_URL}" target="_blank" rel="noopener">
Formula1.com: Russell on the Bahrain upgrades</a>.</p>
<h2 class="sec">Friday car display — confirmed procedure</h2>
<p>The FIA sets <strong>11:00–12:00 MYT on Friday 2 October</strong>
(<strong>06:00–07:00 Tallinn</strong>): one car from each team at its pit-stop
position, the other available inside the garage. If only one car carries the
new major aero/bodywork components, that is the car that must be shown.
This display procedure is distinct from the Car Presentation Submissions,
which are now published and transcribed above from Document 12.</p>
<p class="src"><a href="{DISPLAY_URL}#page=2" target="_blank" rel="noopener">
FIA Car Display Procedure, page 2</a>.</p>
"""
    pages["upgrades"]["body"] = _upgrade_summary() + render_submissions(
        UPGRADE_SUBMISSIONS, source_url=UPGRADES_URL, asset_prefix=UPGRADES_ASSET,
        document="FIA Document 12", event="Bahrain GP at Sepang", issued="2 October 2026, 10:03 MYT",
    ) + upgrades
    for slug in ("overview", "notes", "teams"):
        pages[slug]["body"] = _upgrade_summary() + pages[slug]["body"]
    pages["powerunit"]["body"] += f"""
<h2 class="sec">Carry-over technical check — compliant, not a penalty</h2>
<p>Document 2, dated 30 September, records that Leclerc's Car 16 was selected
after Baku for detailed checks of its ICE air-intake cooling system, wiring and
sensors. All inspected components complied with the 2026 technical regulations.
This is a post-Azerbaijan inspection published in the Sepang event folder, not a
new Sepang PU allocation list.</p>
<p class="src"><a href="{COMPLIANCE_URL}" target="_blank" rel="noopener">
FIA Technical Delegate's report, Document 2</a>.</p>
"""
    pages["powerunit"]["body"] += _pu_inventory()
    pages["schedule"]["body"] += f"""
<p>The FIA Competition Visa confirms <strong>Sunday 4 October, 15:00 MYT /
10:00 Tallinn</strong>, 56 laps of the 5.543 km Sepang circuit, with a 9 m
start-line offset. FP1/FP2 are Friday and FP3/Qualifying Saturday; this is not
a Sprint weekend. <a href="{VISA_URL}" target="_blank" rel="noopener">
Visa V2 (Document 13) and official timetable</a>.</p>
"""
    pages["notes"]["body"] = f"""
<div class="callout accent"><strong>1 October pre-practice review:</strong>
C2/C3/C4, with C2/C3 mandatory race specifications and C4 the Q3 tyre.
Slick starting pressures 25.0/24.5 psi front/rear; maximum heating 70°C for
slick/intermediate and 40°C for wet, all two hours. Pirelli estimates 22.5 s
pit-stop loss. Four Straight Mode zones are distinct from one electrical
Overtake activation line. Friday car display 11:00–12:00 MYT; race Sunday
15:00 MYT / 10:00 Tallinn. <a href="tyres.html">Tyres</a> ·
<a href="upgrades.html">Development/display</a> · <a href="circuit.html">FIA map</a>.
</div>""" + pages["notes"]["body"]
    pages["moments"] = dict(
        kicker="History",
        title="Sepang's Great Moments",
        sub="The Malaysian Grand Prix years (1999-2017) at the venue now hosting the Bahrain GP.",
        body=_moments_section(),
    )
    pages["penalties"] = dict(
        kicker="Confirmed carry-over sanction",
        title="Penalties & Decisions",
        sub="A published Azerbaijan ruling applies to this event; Bahrain-specific decisions remain source-dependent.",
        body=render_penalties(
            ctx,
            decisions=[
                dict(
                    doc="Azerbaijan Doc 66",
                    source_event="azerbaijan",
                    no="43",
                    driver="Franco Colapinto",
                    team="BWT Alpine F1 Team",
                    session="Azerbaijan Grand Prix — Race",
                    fact="Turn 1 collision with team-mate Pierre Gasly.",
                    outcome=(
                        "10-second time penalty converted to five grid places at "
                        "the next race in which the driver participates."
                    ),
                    kind="penalty",
                    source_url=FIA_DOC_66,
                )
            ],
            intro_html=notice + _reported_grid_watch(),
            fia_url=ctx.get("fia_url", ""),
        ),
    )
    pages["penalties"]["body"] += f"""
<p><strong>Event officials:</strong> stewards Gerd Ennser, Mathieu Remmerie,
Pedro Lamy and Mazen Al Hilli; Race Director Rui Marques.
<a href="{VISA_URL}" target="_blank" rel="noopener">FIA Competition Visa,
Document 13, V2</a>. Publication of a compliance report or a heat declaration does
not make it a driver penalty.</p>
"""
    return pages
