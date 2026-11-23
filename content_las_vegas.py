"""Source-reviewed Las Vegas technical information and post-race briefing."""
from html import escape
import content_generic
from f1lib import card
from upgrade_render import render_submissions


FIA_ROOT = "https://www.fia.com/system/files/decision-document/2026_las_vegas_grand_prix_-_"
FIA_POWER_UNIT = FIA_ROOT + "power_unit_information.pdf"
FIA_USAGE = FIA_ROOT + "pu_elements_used_per_driver_up_to_now.pdf"
FIA_NEW = FIA_ROOT + "new_pu_elements_for_this_competition.pdf"
FIA_UPGRADES = FIA_ROOT + "car_presentation_submissions.pdf"
FIA_PIRELLI = FIA_ROOT + "competition_notes_-_pirelli_preview_v3.pdf"
PEREZ_PENALTY = FIA_ROOT + "infringement_-_car_11_-_causing_a_collision_with_car_51.pdf"
FP1_REPORT = ("https://www.formula1.com/en/latest/article/"
              "fp1-wet-conditions-limit-running-in-first-practice-at-las-vegas-grand-prix."
              "7H085JgIW1k8jM3ysejVqJ")
RACE_RESULT = "https://www.formula1.com/en/results/2026/races/1300/las-vegas/race-result"

UPGRADE_SUBMISSIONS = [
    ("McLaren", 2, [
        ("Floor Furniture", "Performance - Flow Conditioning", "New floor board and floor edge target floor loading."),
        ("Floor Furniture", "Performance - Flow Conditioning", "Rear floor furniture changes condition diffuser flow."),
    ]),
    ("Mercedes", 4, [
        ("Rear Wing", "Circuit specific - Drag Range", "Removed winglet devices reduce drag for Las Vegas."),
        ("Front Bodywork", "Circuit specific - Drag Range", "Trimmed mirror rear stay reduces camber and loading."),
        ("Rear Corner", "Performance - Local Load", "Repositioned rear-corner winglets target the local load requirement."),
        ("Engine Cover", "Cooling Range", "Narrower rear exit matches the event cooling requirement."),
    ]),
    ("Red Bull", 6, [
        ("Front Wing Endplate", "Performance - Local Load", "Lower, shorter dive-plane protects downstream flow stability."),
    ]),
    ("Ferrari", 8, [
        ("Floor Board", "Circuit specific - Drag Range", "Optimised floor-board elements and a single vertical element reduce drag, with some downforce reduction."),
    ]),
    ("Williams", 10, []),
    ("Racing Bulls", 11, [
        ("Floor Board", "Circuit specific - Drag Range", "Shorter-chord board elements reduce floor-generated load."),
        ("Rear Corner", "Circuit specific - Drag Range", "Alternative drum-winglet arrangement reduces load for efficiency."),
        ("Front Wing", "Circuit specific - Balance Range", "Reduced flap chord and incidence extend the low-balance range."),
    ]),
    ("Aston Martin", 13, []),
    ("Haas", 14, [
        ("Rear Wing", "Performance - Drag reduction", "Revised Straight Mode deployment arrangement with associated geometry changes."),
    ]),
    ("Audi", 16, [
        ("Rear Corner", "Circuit Specific - Drag Range", "Revised rear brake-duct deflector matches the circuit efficiency requirement."),
    ]),
    ("Alpine", 18, []),
    ("Cadillac", 19, []),
]

# 19 November report, before the event's newly declared components.
PU_USAGE = [
    ("81", "Oscar Piastri", 4, 3, 3, 2, 3, 3, 5),
    ("1", "Lando Norris", 4, 3, 3, 2, 3, 4, 5),
    ("63", "George Russell", 6, 5, 5, 4, 4, 4, 6),
    ("12", "Kimi Antonelli", 5, 3, 3, 2, 4, 4, 6),
    ("3", "Max Verstappen", 5, 5, 5, 3, 3, 3, 6),
    ("6", "Isack Hadjar", 8, 7, 7, 4, 4, 4, 8),
    ("16", "Charles Leclerc", 5, 4, 4, 3, 3, 3, 6),
    ("44", "Lewis Hamilton", 6, 5, 5, 4, 4, 4, 7),
    ("23", "Alexander Albon", 5, 3, 3, 2, 3, 4, 5),
    ("55", "Carlos Sainz", 4, 4, 3, 2, 3, 4, 5),
    ("41", "Arvid Lindblad", 7, 6, 5, 2, 3, 3, 6),
    ("30", "Liam Lawson", 5, 5, 2, 2, 3, 3, 7),
    ("18", "Lance Stroll", 6, 7, 3, 5, 8, 7, 9),
    ("14", "Fernando Alonso", 5, 6, 3, 5, 7, 6, 9),
    ("51", "Rafael Câmara", 4, 4, 4, 3, 3, 3, 6),
    ("87", "Oliver Bearman", 4, 4, 4, 4, 4, 4, 4),
    ("27", "Nico Hulkenberg", 4, 4, 4, 3, 3, 3, 5),
    ("5", "Gabriel Bortoleto", 5, 5, 5, 4, 6, 6, 7),
    ("10", "Pierre Gasly", 4, 3, 3, 2, 3, 3, 5),
    ("43", "Franco Colapinto", 5, 3, 2, 2, 3, 4, 5),
    ("11", "Sergio Perez", 5, 5, 4, 4, 3, 3, 5),
    ("77", "Valtteri Bottas", 5, 5, 4, 4, 4, 4, 5),
]


def _figure(asset, source, page, caption):
    return (f'<figure class="circuit-fig"><img src="../assets/{asset}-p{page}.png" '
            f'alt="{escape(caption)}" class="circuit-img" loading="lazy" onclick="zoomImg(this)">'
            f'<figcaption>{escape(caption)}. <a href="{source}#page={page}">Original PDF, '
            f'page {page}</a>. Click to zoom.</figcaption></figure>')


def _powerunit():
    rows = "".join("<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row)
                   + "</tr>" for row in PU_USAGE)
    return f"""
<h2 class="sec">Las Vegas FIA power and energy map</h2>
<p>FIA Power Unit Information: 6.201 km, standard format, 19–21 November.
Maximum <strong>recharge</strong> per lap is <strong>8.0 MJ</strong> in the race
without Overtake, <strong>8.5 MJ</strong> with Overtake, <strong>6.0 MJ</strong> in
qualifying, <strong>8.5 MJ</strong> in free practice and <strong>9.0 MJ</strong>
on out laps other than in the race. These are recharge limits, not deployment allowances.</p>
<p>Article C5.12.8: power-limited distance <strong>4448 m</strong>, reduction-rate
limit <strong>50 kW/s</strong>. Main overtaking-zone curves are Base–Standard
without Overtake and Base–Overtake with it; elsewhere the race uses Alt 1.
Practice including qualifying uses Base–Overtake. The complete curves and
exception windows remain in the original diagram below.</p>
<p>Alternative-curve sectors: T1–T3, 300–500 m; T5–T12, 1520–3150 m.
Power-reduction exceptions permit 350 kW at T1–T3 (300–500 m), T7–T9
(2000–2200 m), T10–T11 (2670–3100 m), plus [Exit T14, 5100–5700 m].
Reset windows: Exit T3, 540–800 m; [Exit T16, 5700–6200 m]. Brackets apply
only in SQ/Q as the source specifies; they do not establish a Sprint session
at this standard-format event. Higher-speed thresholds are 240 km/h at T3–T4
(450–620 m) and 310 km/h at T10–T12 (2550–3100 m).</p>
<p><strong>Overtake:</strong> 1.0-second detection gap, detection at
<strong>5299 m / L19</strong>, activation at <strong>5400 m / L20</strong>.
Loop labels are not turn numbers. Straight Mode is active aero, separate from
the Overtake energy system; do not describe the map's SM markings as extra
Overtake activation lines.</p>
{_figure("fia-las-vegas-a1e5fd5704ed-06d0a2b4c9220ec2", FIA_POWER_UNIT, 2, "FIA Las Vegas power-unit map, visually reviewed")}
<h2 class="sec">Season usage entering Las Vegas</h2>
<p>The Technical Delegate's <strong>19 November</strong> table is the
pre-addition baseline, not a post-race total and not itself a penalty ruling.
ICE = engine; TC = turbo; EXH = exhaust; MGU-K = kinetic motor-generator;
ES = energy store; PU-CE = control electronics; PU-ANC = ancillary component.</p>
<div class="table-wrap"><table class="data compact"><thead><tr>
<th>No.</th><th>Driver</th><th>ICE</th><th>TC</th><th>EXH</th><th>MGU-K</th>
<th>ES</th><th>PU-CE</th><th>PU-ANC</th></tr></thead><tbody>{rows}</tbody></table></div>
{_figure("fia-las-vegas-2ff6e2a73f1d-0de7b2288d26e13d", FIA_USAGE, 2, "Technical Delegate season-usage baseline, 19 November")}
<h2 class="sec">New components and separately imposed grid sanctions</h2>
<p>Document 14 declares new ICEs for Piastri (previously 4), Antonelli (5) and
Bearman (4); new TCs for Piastri, Norris, Antonelli, Albon, Gasly and Colapinto
(each previously 3), and Sainz and Bearman (4). New exhausts: Norris,
Antonelli, Albon, Sainz, Alonso and Gasly (3), Bearman (4), Colapinto (2).
Bearman also adds an MGU-K (4); Stroll an ES (8) and PU-CE (7).
Piastri and Norris add PU-ANCs (5), and Bearman adds one (4).
Parentheses mean <em>previously used</em>, not the new ordinal.</p>
<div class="table-wrap"><table class="data"><thead><tr><th>Driver</th><th>New ordinal</th>
<th>Stewards' decision</th></tr></thead><tbody>
<tr><td>Piastri</td><td>5th ICE</td><td><a href="{FIA_ROOT}infringement_-_car_81_-_changes_to_pu_element.pdf">Doc 16: 10 places</a></td></tr>
<tr><td>Antonelli</td><td>6th ICE</td><td><a href="{FIA_ROOT}infringement_-_car_12_-_changes_to_pu_element.pdf">Doc 17: 5 places</a></td></tr>
<tr><td>Sainz</td><td>5th TC</td><td><a href="{FIA_ROOT}infringement_-_car_55_-_changes_to_pu_element.pdf">Doc 18: 10 places</a></td></tr>
<tr><td>Stroll</td><td>9th ES; 8th PU-CE</td><td><a href="{FIA_ROOT}infringement_-_car_18_-_changes_to_pu_elements.pdf">Doc 19: 10 places</a></td></tr>
<tr><td>Bearman</td><td>5th ICE, TC, EXH and MGU-K</td><td><a href="{FIA_ROOT}infringement_-_car_87_-_changes_to_pu_elements.pdf">Doc 20: 35 places</a></td></tr>
</tbody></table></div>
<p>These are Las Vegas sanctions for the next race in which each driver
participated, not new Qatar penalties. Use the actual <a href="results.html">
starting grid</a>, not arithmetic subtraction from qualifying.</p>
{''.join(_figure("fia-las-vegas-4306f3b83583-64fd82ee490939fc", FIA_NEW, page, "FIA Document 14 new PU elements") for page in (2, 3, 4))}
"""


MCLAREN_VEGAS_URL = (
    "https://www.formula1.com/en/latest/article/"
    "technically-a-very-interesting-race-stella-reveals-how-norris-and-mclaren-"
    "triumphed-at-interlagos.SRa4ORrmm9CcPqhwssoum"
)
ANTONELLI_TITLE_URL = (
    "https://www.formula1.com/en/latest/article/"
    "antonelli-crowned-youngest-ever-f1-champion-as-verstappen-wins-eventful-"
    "mexico-git-grand-prix.xpMMeef0KmRURs9IDs3LH"
)
MERCEDES_TITLE_URL = (
    "https://www.formula1.com/en/latest/article/"
    "norris-beats-verstappen-in-wet-sao-paulo-gp-thriller-as-mercedes-win-"
    "constructors-championship.7JN7MXLZf5lk5l0C3gfKGI"
)


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    pages["rookies"]["body"] = card(
        "Actual Las Vegas FP1 substitutions",
        f"""<p>Dino Beganovic drove Lewis Hamilton's Ferrari, Ryo Hirakawa replaced
Oliver Bearman at Haas, and Jak Crawford took Fernando Alonso's Aston Martin.
These are practice substitutions, not changes to the race line-up. Rain limited
the hour to installation running with no official timed laps.
<a href="{FP1_REPORT}">Official completed-session report</a>.</p>""",
        "bi-person-badge", "accent")
    update = card(
        "McLaren says more parts are planned for Las Vegas",
        f"""<p>Team Principal Andrea Stella said the Interlagos package will be
complemented by more parts at Las Vegas, forming a foundation for McLaren's
2027 car. His interview did not identify the components or their intended
effect. This is a team statement, not an FIA filing. <a href="{MCLAREN_VEGAS_URL}"
target="_blank" rel="noopener">Formula1.com, 9 November</a>.</p>""",
        "bi-tools",
        "accent",
    )
    championships = card(
        "Both 2026 championships are settled",
        f"""<p>Kimi Antonelli clinched the Drivers' Championship with third place
in Mexico City on 1 November. Mercedes secured the Constructors' title in São
Paulo on 8 November, where George Russell finished fourth and Antonelli fifth.
The Las Vegas weekend is no longer a title-decider; focus on race wins and the
remaining finishing positions. <a href="{ANTONELLI_TITLE_URL}" target="_blank"
rel="noopener">Formula1.com on Antonelli's title</a> ·
<a href="{MERCEDES_TITLE_URL}" target="_blank" rel="noopener">Formula1.com on
Mercedes' title</a>.</p>""",
        "bi-trophy",
        "accent",
    )
    pending = content_generic.pending(
        "Team-by-team weekend storylines", "in the week before the race"
    )
    pages["teams"]["body"] = pages["teams"]["body"].replace(
        pending,
        update + content_generic.pending(
            "Further team-specific weekend details",
            "as event statements and filings are reviewed",
        ),
    )
    pages["upgrades"]["body"] = render_submissions(
        UPGRADE_SUBMISSIONS, source_url=FIA_UPGRADES,
        asset_prefix="fia-las-vegas-2033bd1bf5b6-90bbeb5438e3a5c1",
        document="FIA Car Presentation Submissions", event="Las Vegas",
        issued="19 November 2026") + update
    pages["powerunit"]["body"] = _powerunit()
    pages["tyres"]["body"] += f"""
<h2 class="sec">Pre-race strategy context, not a race-set inventory</h2>
<p>Pirelli's 16 November preview favoured one stop on paper, with all three
compounds potentially usable. Cold tyres after the pit exit weakened the
traditional undercut. Its complete infographic gives an average pit-stop loss
of 21 seconds; this is a preview estimate, not stationary stop time.
The graphic's 20–22 November header does not override the official calendar's
19–21 November local sessions. The newer FIA V3 prescriptions below take
precedence over the preview. No driver-by-driver remaining sets or actual
race stints are inferred from either source.
<a href="https://press.pirelli.com/the-night-time-challenge-of-las-vegas/">Pirelli preview</a>.</p>
<h2 class="sec">Reviewed Pirelli prescriptions — V3 / Issue C</h2>
<p>C3/C4/C5; mandatory race compounds C3 and C4, Q3 compound C5.
Minimum starting pressures, front/rear: slick 27.5/28.0 psi; intermediate
29.0/29.0 psi; wet 29.0/28.5 psi. Expected stabilised minima: slick
28.0/28.5 psi, intermediate and wet 29.5/29.5 psi. Camber limits,
front/rear: slick −3°/−1.75°, intermediate and wet −3.25°/−2.25°.
Maximum tyre heating: slick/intermediate 70°C, wet 60°C, at most two hours.
These are prescriptions, not the driver-by-driver remaining race-set inventory.</p>
{_figure("fia-las-vegas-d7c138a1cb75-e5af5f2c22303676", FIA_PIRELLI, 2, "Pirelli prescriptions V3, document version 5 Issue C")}"""
    pages["notes"]["body"] = championships + update + pages["notes"]["body"]
    recap = f"""<h2 class="sec">Las Vegas result and Qatar carry-over</h2>
<p>Max Verstappen won from Lando Norris (+0.639s) and Oscar Piastri (+1.529s).
Antonelli qualified first but did not start on pole after his PU sanction.
<a href="{RACE_RESULT}">Official race classification</a> ·
<a href="results.html">All session tables and actual starting grid</a>.</p>
<p>FP1 finished with <strong>no timed laps</strong> in wet conditions: installation
running is not a classification. <a href="{FP1_REPORT}">Official FP1 report</a>.</p>
<p><strong>Qatar watch:</strong> FIA Document 61 gives Sergio Perez a five-place
drop at his next race after contact with Rafael Câmara at Turn 14. He retired,
so the unserved time penalty became a grid sanction.
<a href="{PEREZ_PENALTY}">Stewards' ruling</a> · <a href="../qatar/notes.html">Qatar briefing</a>.</p>"""
    for slug in ("overview", "notes"):
        pages[slug]["body"] = recap + pages[slug]["body"]
    return pages
