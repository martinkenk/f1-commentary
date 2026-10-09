"""Verified Singapore-specific coverage layered over the shared event pages."""

import content_generic
from f1lib import card, stat


F1_TYRE_ARTICLE = (
    "https://www.formula1.com/en/latest/article/"
    "what-tyres-will-the-teams-and-drivers-have-for-the-2026-singapore-grand-prix."
    "4rG7uAn2d6vveGmRlkE5RM"
)
FIA_ROOT = "https://www.fia.com/system/files/decision-document/"
FIA_HEAT = FIA_ROOT + "2026_singapore_grand_prix_-_heat_hazard_declaration.pdf"
FIA_PIRELLI = FIA_ROOT + "2026_singapore_grand_prix_-_competition_notes_-_pirelli_preview.pdf"
FIA_CIRCUIT = FIA_ROOT + (
    "2026_singapore_grand_prix_-_competition_notes_-_"
    "circuit_map_pit_lane_drawing_and_emergency_exits_map.pdf"
)
FIA_NOTES = FIA_ROOT + "2026_singapore_grand_prix_-_race_directors_competition_notes_v2.pdf"
FIA_PU = FIA_ROOT + "2026_singapore_grand_prix_-_power_unit_information.pdf"
FIA_UPGRADES = FIA_ROOT + "2026_singapore_grand_prix_-_car_presentation_submissions.pdf"


def _figure(asset, alt, caption, source_url, source_label):
    return f"""
    <figure class="track-map">
      <a href="../assets/{asset}" target="_blank" rel="noopener">
        <img src="../assets/{asset}" alt="{alt}" loading="lazy">
      </a>
      <figcaption>{caption} · <a href="{source_url}" target="_blank"
      rel="noopener">{source_label}</a></figcaption>
    </figure>"""


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)

    heat = card(
        "Heat Hazard declared",
        "<p>The FIA forecast a Heat Index above <strong>31.0°C</strong>, so the "
        "Heat Hazard measures apply to both Saturday's Sprint and Sunday's Grand "
        f"Prix. Driver-cooling and ballast provisions are therefore active. "
        f"<a href=\"{FIA_HEAT}\" target=\"_blank\" rel=\"noopener\">FIA declaration ↗</a></p>",
        "note",
    )
    fp1 = card(
        "FP1: Russell sets the benchmark",
        "<p>George Russell led the only full practice before Sprint Qualifying with "
        "<strong>1:32.274</strong>, ahead of Charles Leclerc by 0.198s and Lando "
        "Norris by 0.273s. The official 22-driver classification is on the Results "
        "page; telemetry analysis will appear only when a usable timing feed is available.</p>",
    )
    pages["overview"]["body"] = heat + fp1 + pages["overview"]["body"]
    pages["schedule"]["body"] = heat + card(
        "Sprint-weekend constraint",
        "<p>Teams had a single 60-minute practice before Sprint Qualifying. The "
        "competitive running then comprises Saturday's Sprint and Qualifying before "
        "Sunday's 62-lap, 305.337 km Grand Prix.</p>",
    ) + pages["schedule"]["body"]

    pages["tyres"].update({
        "title": "Tyres & Strategy",
        "sub": "Official Pirelli allocation, prescriptions and Singapore strategy constraints",
        "body": (
            _figure(
                "singapore_pirelli_tyres_2026.webp",
                "Official Pirelli 2026 Singapore Grand Prix tyre preview",
                "Official Pirelli event-preview graphic",
                F1_TYRE_ARTICLE,
                "Formula 1 / Pirelli source ↗",
            )
            + card(
                "C3 / C4 / C5 allocation",
                stat("Hard", "C3", "Mandatory race compound")
                + stat("Medium", "C4", "Mandatory race compound")
                + stat("Soft", "C5", "Q3 compound"),
            )
            + card(
                "FIA/Pirelli operating prescriptions",
                "<table><thead><tr><th>Tyre</th><th>Front</th><th>Rear</th>"
                "<th>Blanket</th></tr></thead><tbody>"
                "<tr><td>Slick</td><td>24.0 psi</td><td>23.0 psi</td><td>70°C</td></tr>"
                "<tr><td>Intermediate</td><td>25.0 psi</td><td>24.0 psi</td><td>70°C</td></tr>"
                "<tr><td>Wet</td><td>23.0 psi</td><td>22.0 psi</td><td>40°C</td></tr>"
                "</tbody></table><p>Maximum heating time is two hours. Slick camber "
                "limits are <strong>-3.25° front / -2.0° rear</strong>. "
                f"<a href=\"{FIA_PIRELLI}\" target=\"_blank\" rel=\"noopener\">"
                "FIA/Pirelli preview ↗</a></p>",
            )
            + _figure(
                "fia-singapore-50dfda1288b3-a50092321c3c3ba6-p2.png",
                "FIA Pirelli Singapore operating prescriptions",
                "Published compound, pressure, camber and heating prescriptions",
                FIA_PIRELLI,
                "FIA source ↗",
            )
            + card(
                "Strategy watch",
                "<p>The narrow temperature spread between C3, C4 and C5, humid "
                "night conditions and limited Sprint-weekend practice make thermal "
                "control and clean-air positioning central. C3 and C4 must each be "
                "available as the nominated mandatory race compounds; any actual "
                "race-set inventory will be published only after Pirelli releases it.</p>",
            )
        ),
    })

    straight_rows = "".join(
        f"<tr><td>{name}</td><td>{normal}</td><td>{low}</td></tr>"
        for name, normal, low in (
            ("A1", "30 m after T19", "90 m after T19"),
            ("A2", "50 m after T5", "N/A"),
            ("A3", "70 m after T9", "120 m after T9"),
            ("A4", "115 m after T13", "165 m after T13"),
            ("A5", "70 m after T15", "90 m after T15"),
        )
    )
    pages["circuit"]["body"] = (
        card(
            "2026 Straight Mode and Overtake deployment",
            "<p>The 4.927 km circuit has <strong>five Straight Mode zones</strong> "
            "and one Overtake zone. Overtake detection is 30 m after Turn 17 and "
            "activation is at the entry to Turn 17.</p>"
            "<table><thead><tr><th>Zone</th><th>Normal activation</th>"
            f"<th>Low-grip activation</th></tr></thead><tbody>{straight_rows}</tbody></table>"
            "<p>Sector lengths are 1.506 / 1.782 / 1.639 km; the speed trap is "
            f"150 m before Turn 1. <a href=\"{FIA_CIRCUIT}\" target=\"_blank\" "
            "rel=\"noopener\">FIA circuit map ↗</a></p>",
        )
        + _figure(
            "fia-singapore-115947cd46e9-8bd2227af6272a03-p2.png",
            "Official 2026 Singapore circuit map",
            "Straight Mode, Overtake, timing and marshal locations",
            FIA_CIRCUIT,
            "FIA source ↗",
        )
        + card(
            "Circuit changes",
            "<p>The pit wall has moved one metre to widen the pit lane. The main "
            "straight was resurfaced and several barriers and painted lines were "
            "realigned. Drivers who fail to negotiate Turn 18 or Turn 19 risk "
            "losing that lap and the following lap.</p>",
            "note",
        )
        + pages["circuit"]["body"]
    )

    pages["powerunit"].update({
        "title": "Power Unit",
        "sub": "Singapore energy deployment and Overtake parameters",
        "body": (
            card(
                "Energy map",
                stat("Sprint / Race", "8.5 MJ", "Without Overtake")
                + stat("Sprint / Race", "9.0 MJ", "With Overtake")
                + stat("SQ / Q / FP", "9.0 MJ", "Also non-race out-laps")
                + "<p>Power-limited distance: <strong>2,185 m</strong>. Rate limit: "
                "<strong>100 kW/s</strong>. Overtake detection/activation: "
                "<strong>4,350 m / 4,430 m</strong> at loops L21/L22 with a "
                f"1.0-second gap. <a href=\"{FIA_PU}\" target=\"_blank\" "
                "rel=\"noopener\">FIA PU information ↗</a></p>",
            )
            + card(
                "Alternative power-curve sectors",
                "<ul><li>Turns 1–5: 400–900 m</li><li>Turns 7–9: 1,750–2,150 m</li>"
                "<li>Turns 10–13: 2,600–3,000 m</li></ul>",
            )
            + _figure(
                "fia-singapore-93e36b152c67-9d0e5bdab5230430-p2.png",
                "Singapore power unit information",
                "Official PU energy and Overtake parameters",
                FIA_PU,
                "FIA source ↗",
            )
        ),
    })

    pages["upgrades"].update({
        "title": "Technical Upgrades",
        "sub": "Official FIA car-presentation submissions for Singapore",
        "body": (
            card(
                "Three teams submitted event changes",
                "<table><thead><tr><th>Team</th><th>Submission</th></tr></thead><tbody>"
                "<tr><td>McLaren</td><td>High-cooling front brake duct.</td></tr>"
                "<tr><td>Mercedes</td><td>New front wing with matching endplate, "
                "footplate and diveplane changes.</td></tr>"
                "<tr><td>Red Bull</td><td>Revised front wing for local load and an "
                "enlarged rear wheel-bodywork exit duct for cooling.</td></tr>"
                "</tbody></table>"
                f"<p><a href=\"{FIA_UPGRADES}\" target=\"_blank\" rel=\"noopener\">"
                "FIA car-presentation submissions ↗</a></p>",
            )
            + card(
                "No updates submitted",
                "<p>Ferrari, Williams, Racing Bulls, Aston Martin, Haas, Alpine, "
                "Audi and Cadillac declared no new components in the published "
                "submission. That is an explicit no-update declaration, not missing data.</p>",
                "note",
            )
            + _figure(
                "fia-singapore-753141a54714-caf5c69b36c7f1c4-p2.png",
                "Singapore car presentation submission overview",
                "Published Singapore component submissions",
                FIA_UPGRADES,
                "FIA source ↗",
            )
        ),
    })

    pages["notes"]["body"] = heat + card(
        "Race Director's operational notes",
        "<ul><li>Blue-flag pre-warning at 3.0s; light panels at 1.2s.</li>"
        "<li>Interrupted Sprint Qualifying or Qualifying periods with under "
        "90 seconds remaining will not restart.</li><li>Safety Car resumption "
        "waiting point is after Turn 13.</li><li>Safety Car deployment uses light "
        "panels and messages rather than physical yellow flags or SC boards.</li>"
        "<li>The maximum SC2-to-SC1 time is published after FP1.</li></ul>"
        f"<p><a href=\"{FIA_NOTES}\" target=\"_blank\" rel=\"noopener\">"
        "Race Director's Competition Notes V2 ↗</a></p>",
    ) + pages["notes"]["body"]
    return pages
