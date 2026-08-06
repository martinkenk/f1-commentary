"""
Per-venue reference data — the *known-now* editorial layer.

Formula1.com gives us the calendar, the session times and the hard circuit
numbers (see ``calendar.py``). What it doesn't give us is the commentary
material: what the place actually demands of a car, where the passes happen,
which corners to name-check, and the trivia that fills a quiet lap. That lives
here, keyed by the Formula1.com racing slug.

Everything in this file is stable, season-independent knowledge, so it can be
written well ahead of a race weekend. The volatile material — tyre compounds,
rookie FP1 line-ups, upgrades, penalties, weather — is deliberately *not* here;
that gets filled in automatically as each event approaches.

`coords` are the circuit centres and drive the weather forecast, so they need to
be right to a few hundred metres.
"""

CIRCUITS = {
    # ------------------------------------------------- already covered in full
    # These two have bespoke content modules, so only the fields the build
    # driver needs (name, coordinates, local-time label) are kept here.
    "belgium": {
        "circuit": "Circuit de Spa-Francorchamps",
        "coords": (50.4372, 5.9714),
        "tz_local": "Spa (CEST)",
        "character": (
            "The longest lap on the calendar — a high-speed, high-commitment run through "
            "the Ardennes forest, with its own weather system."
        ),
        "lap_record": "1:44.701 — Sergio Perez, 2024",
    },
    "hungary": {
        "circuit": "Hungaroring, Budapest",
        "coords": (47.5789, 19.2486),
        "tz_local": "Budapest (CEST)",
        "character": (
            "Tight, twisty and relentless — often described as Monaco without the walls. "
            "Track position is everything and the heat punishes both cars and drivers."
        ),
        "lap_record": "1:16.627 — Lewis Hamilton, 2020",
    },

    # ---------------------------------------------------------------- upcoming
    "netherlands": {
        "circuit": "Circuit Zandvoort",
        "coords": (52.3888, 4.5409),
        "tz_local": "Zandvoort (CEST)",
        "character": (
            "A banked, old-school rollercoaster squeezed into the dunes. Narrow, "
            "relentlessly cambered and almost entirely blind — the corners fall away "
            "and climb back at you, and the wind off the North Sea changes the balance "
            "session to session."
        ),
        "key_corners": [
            ("Turn 3 — Hugenholtzbocht", "Steeply banked (18°) hairpin; cars can run two abreast on different lines, which is what makes the banking more than a gimmick."),
            ("Turns 7–8 — Scheivlak", "Fast, downhill, blind right. Genuinely intimidating and the corner drivers talk about all weekend."),
            ("Turn 14 — Arie Luyendijkbocht", "The final banked (18°) right that launches the cars onto the pit straight — get it wrong and the DRS run to Turn 1 is lost."),
        ],
        "overtaking": (
            "Hard. Effectively one real passing place — into Turn 1 out of the banked "
            "final corner, with DRS. Track position and the undercut usually decide it, "
            "which is why strategy and safety-car timing carry so much weight here."
        ),
        "tyre_notes": (
            "High-energy, continuous loading with very little straight-line rest, so "
            "front-left and rear temperatures build. Graining on the softer compounds is "
            "the usual complaint; track evolution across the weekend is strong."
        ),
        "drs": 2,
        "lap_record": "1:11.097 — Lewis Hamilton, 2021",
        "notes": [
            "Zandvoort's first World Championship Grand Prix was in 1952; it returned in 2021 after a 36-year absence.",
            "The 2026 race is scheduled to be one of the venue's last under its current deal — expect plenty of farewell framing.",
            "Grandstands are famously orange and the crowd noise is a genuine broadcast feature.",
        ],
        "storylines": [
            "A sprint weekend: only one hour of practice before parc fermé, so set-up mistakes are expensive.",
            "Wind direction off the sea is the single biggest set-up variable — ask about it in every session.",
        ],
    },
    "italy": {
        "circuit": "Autodromo Nazionale Monza",
        "coords": (45.6156, 9.2811),
        "tz_local": "Monza (CEST)",
        "character": (
            "The Temple of Speed. The lowest-downforce configuration of the year: long "
            "straights, heavy braking into chicanes, and the fastest average speed on the "
            "calendar. Cars are trimmed out to the point of being nervous under braking."
        ),
        "key_corners": [
            ("Turns 1–2 — Variante del Rettifilo", "Huge braking zone from ~340 km/h. The classic passing spot and the classic lap-one flashpoint."),
            ("Turns 4–5 — Variante della Roggia", "Second-best passing chance; a late lunge here often decides a place."),
            ("Turns 6–7 — Lesmo 1 & 2", "Quick, blind, unforgiving rights where a trimmed car feels its lack of downforce."),
            ("Turn 11 — Parabolica (Curva Alboreto)", "Long, loaded right onto the main straight — exit speed here sets up the overtake into Turn 1."),
        ],
        "overtaking": (
            "Among the easiest on the calendar. Two long DRS runs into heavy braking zones "
            "mean slipstream trains, late lunges and genuine multi-car battles. Track "
            "position matters far less than usual."
        ),
        "tyre_notes": (
            "Low lateral energy but severe braking loads; usually the softest end of the "
            "range and often a straightforward one-stop. Rear locking and flat-spots under "
            "braking are the thing to watch."
        ),
        "drs": 2,
        "lap_record": "1:21.046 — Rubens Barrichello, 2004",
        "notes": [
            "Monza has hosted a Grand Prix in every World Championship season bar one (1980) since 1950.",
            "Barrichello's 2004 lap remains one of the longest-standing records in the sport.",
            "The old banking still stands beside the current circuit and is a reliable piece of colour.",
        ],
        "storylines": [
            "Ferrari's home race — the tifosi and the podium reaction are part of the broadcast.",
            "Low-downforce packages expose power-unit deployment differences more than anywhere else.",
        ],
    },
    "spain": {
        "circuit": "Madring, Madrid",
        "coords": (40.4653, -3.6156),
        "tz_local": "Madrid (CEST)",
        "character": (
            "Brand new for 2026 — a part-street, part-permanent lap around the IFEMA "
            "exhibition grounds, including a banked corner. Nobody has real race running "
            "here, so every reference point, tyre number and strategy call is provisional."
        ),
        "key_corners": [
            ("Turn 1", "First heavy braking zone off the start straight; the obvious opening-lap risk point."),
            ("The banked corner (Turn 12 area)", "A ~24° banked turn, the headline design feature — expect multiple lines and unusual loadings."),
            ("Final sector", "Tighter, street-style stop-start section where traction and kerb-riding decide the lap."),
        ],
        "overtaking": (
            "Unknown in practice. The layout is designed with long acceleration zones into "
            "slow corners to promote passing, but first-year circuits routinely disappoint — "
            "treat any confident prediction with scepticism on air."
        ),
        "tyre_notes": (
            "No historic data. Expect Pirelli to nominate conservatively for the debut and "
            "for teams to spend Friday hunting basic warm-up and graining answers."
        ),
        "drs": None,
        "lap_record": "No record yet — first Grand Prix",
        "notes": [
            "Madrid takes over as Spain's championship round; Barcelona-Catalunya also appears on the 2026 calendar earlier in the year.",
            "First Grand Prix: 2026. Every lap set in the race weekend is, by definition, a lap record.",
            "A debut venue means the FIA circuit notes and track-limits definitions are worth reading closely before FP1.",
        ],
        "storylines": [
            "Anything can be called a 'first' here — first pole, first lap record, first winner.",
            "Watch for track evolution: green, dusty new asphalt usually means enormous lap-time gains across the weekend.",
        ],
    },
    "azerbaijan": {
        "circuit": "Baku City Circuit",
        "coords": (40.3725, 49.8533),
        "tz_local": "Baku (AZT)",
        "character": (
            "A contradiction: a 2.2 km flat-out blast along the seafront bolted onto a "
            "medieval old-town section barely wide enough for one car. Teams must choose "
            "between straight-line speed and the confidence to run close to the walls."
        ),
        "key_corners": [
            ("Turn 1", "Tight left after the start; a regular first-lap incident spot."),
            ("Turns 8–12 — the castle section", "The narrowest point on the calendar (~7.6 m) — walls on both sides and no room to correct."),
            ("Turn 16 into the main straight", "Exit here defines the whole 2.2 km run to the line; the single most important corner of the lap."),
        ],
        "overtaking": (
            "Excellent. The enormous DRS-assisted straight into a tight Turn 1 braking zone "
            "creates late lunges and slipstream chess. Low-drag cars can pass; high-downforce "
            "cars have to defend."
        ),
        "tyre_notes": (
            "Low abrasion but severe warm-up difficulty — getting the fronts switched on for "
            "a single lap is the classic Baku headache, especially in qualifying."
        ),
        "drs": 2,
        "lap_record": "1:43.009 — Charles Leclerc, 2019",
        "notes": [
            "Baku has produced some of the most chaotic races of the modern era; safety cars are close to a statistical certainty.",
            "First Grand Prix: 2016 (as the European Grand Prix), 2017 onwards as the Azerbaijan Grand Prix.",
            "Wind off the Caspian regularly swings the balance between sectors.",
        ],
        "storylines": [
            "Safety-car probability is high enough to be a genuine strategy input, not just a talking point.",
            "The straight rewards efficient 2026 deployment — a good yardstick for power-unit form.",
        ],
    },
    "bahrain": {
        "circuit": "Sepang International Circuit, Malaysia",
        "coords": (2.7608, 101.7382),
        "tz_local": "Kuala Lumpur (MYT)",
        "character": (
            "The Bahrain Grand Prix, staged in Malaysia — Sepang returns to the calendar as "
            "the host venue. Wide, sweeping and punishing: long fast corners, two enormous "
            "straights, extreme heat and humidity, and the constant threat of tropical rain."
        ),
        "key_corners": [
            ("Turns 1–2", "A wide, decreasing-radius right-left that invites side-by-side running off the line."),
            ("Turns 5–6", "Fast, sustained loading — a real test of front-end stability and tyre temperature."),
            ("Turn 15 — final hairpin", "Slow, heavy braking at the end of the back straight; the primary overtaking spot."),
        ],
        "overtaking": (
            "Very good. Two long straights, each ending in a slow corner, with DRS. Sepang "
            "historically produces genuine multi-lap battles rather than single-move passes."
        ),
        "tyre_notes": (
            "Historically one of the toughest tyre circuits on the calendar: high track "
            "temperatures, abrasive surface and long-duration corners drive thermal "
            "degradation. Expect conservative compound choices and multi-stop racing."
        ),
        "drs": 2,
        "lap_record": "1:34.080 — Juan Pablo Montoya, 2004 (Malaysian GP)",
        "notes": [
            "The event is officially the 'Formula 1 Gulf Air Bahrain Grand Prix in Malaysia' — the Bahrain race relocated for 2026.",
            "Sepang last held a Formula 1 round in 2017; it was a calendar fixture from 1999.",
            "Afternoon tropical downpours are a genuine and frequent feature, not a rarity.",
        ],
        "storylines": [
            "A returning circuit with no current-generation data — reference points and tyre behaviour are effectively new.",
            "Heat and humidity make driver cooling and hydration a legitimate story, as does brake and PU cooling.",
        ],
    },
    "singapore": {
        "circuit": "Marina Bay Street Circuit",
        "coords": (1.2914, 103.8640),
        "tz_local": "Singapore (SGT)",
        "character": (
            "The most physically demanding race of the year. A bumpy, humid, walled night "
            "race run at close to 100% humidity, where concentration fades before the tyres "
            "do. Maximum downforce, minimum margin for error."
        ),
        "key_corners": [
            ("Turn 1 — Sheares", "Heavy braking off the start straight; the main passing opportunity."),
            ("Turns 13–16", "Quick, walled sequence that punishes any imprecision immediately."),
            ("Turn 14", "Traditional late-braking lunge point where the leaders often get held up by traffic."),
        ],
        "overtaking": (
            "Difficult. Track position is close to decisive, so qualifying and the undercut "
            "dominate. Safety cars have historically been near-inevitable and are the most "
            "reliable source of position change."
        ),
        "tyre_notes": (
            "Traction and braking dominate; low average speed keeps energy moderate but the "
            "surface is bumpy and warm-up on restarts matters enormously."
        ),
        "drs": 3,
        "lap_record": "1:29.525 — Daniel Ricciardo, 2024",
        "notes": [
            "First held in 2008 as Formula 1's first night race.",
            "Races here regularly run close to the two-hour limit.",
            "Driver weight loss across the race is among the highest of the season — a reliable colour point.",
        ],
        "storylines": [
            "A sprint weekend in 2026, which compresses set-up time on a circuit that traditionally needs the most.",
            "Safety-car timing is the single biggest strategic variable of the night.",
        ],
    },
    "united-states": {
        "circuit": "Circuit of The Americas, Austin",
        "coords": (30.1328, -97.6411),
        "tz_local": "Austin (CDT)",
        "character": (
            "A greatest-hits layout: a steep uphill run to a blind first corner, an "
            "Esses sequence lifted from Silverstone's Maggotts-Becketts, and a stadium "
            "section. Notoriously bumpy from ground movement, which hurts stiff modern cars."
        ),
        "key_corners": [
            ("Turn 1", "Steep uphill, blind apex, huge braking zone — the signature corner and a major passing spot."),
            ("Turns 3–6 — the Esses", "Fast direction changes that reward aerodynamic platform control."),
            ("Turn 12", "End of the long back straight; the second, and often best, overtaking place."),
        ],
        "overtaking": (
            "Good. Two DRS zones feeding heavy braking zones (Turns 1 and 12) create "
            "repeatable passing opportunities and frequent position swaps."
        ),
        "tyre_notes": (
            "High energy through the Esses combined with traction demands in the stadium "
            "section; blistering and graining both appear. Bumps add to the tyre workload."
        ),
        "drs": 2,
        "lap_record": "1:36.169 — Charles Leclerc, 2019",
        "notes": [
            "First Grand Prix: 2012.",
            "Track bumps have previously been severe enough to prompt resurfacing work and driver complaints — always worth checking the Friday reaction.",
            "A sprint venue in several recent seasons; check the 2026 format before assuming practice running.",
        ],
        "storylines": [
            "Ride quality over the bumps is a real differentiator between the 2026 cars.",
            "The uphill Turn 1 launch makes the start one of the most watchable of the year.",
        ],
    },
    "mexico": {
        "circuit": "Autódromo Hermanos Rodríguez, Mexico City",
        "coords": (19.4042, -99.0907),
        "tz_local": "Mexico City (CST)",
        "character": (
            "Raced at 2,240 m altitude — the thinnest air of the season. Roughly a quarter "
            "less aerodynamic downforce for the same wing angle, so teams run maximum wing "
            "and still slide. Cooling is the defining engineering problem of the weekend."
        ),
        "key_corners": [
            ("Turn 1", "End of one of the longest full-throttle runs on the calendar; enormous braking zone and the main passing place."),
            ("Turns 7–11 — Esses", "Quick sequence where the lack of downforce is most obvious."),
            ("Turns 12–13 — the Foro Sol stadium", "Slow, tight section through the grandstand — visually spectacular, technically a traction test."),
        ],
        "overtaking": (
            "Good into Turn 1, helped by the very long approach and a big tow effect in "
            "thin air. Elsewhere it is harder than the layout suggests."
        ),
        "tyre_notes": (
            "Low grip and low downforce mean sliding, which drives thermal degradation "
            "despite modest cornering loads. Warm-up and braking (also compromised by thin "
            "air) are recurring problems."
        ),
        "drs": 3,
        "lap_record": "1:17.774 — Valtteri Bottas, 2021",
        "notes": [
            "First Grand Prix: 1963; returned to the calendar in 2015.",
            "Altitude cuts engine cooling efficiency and brake cooling alike — bodywork is opened up more than anywhere else.",
            "The Foro Sol stadium section gives the loudest crowd atmosphere of the year.",
        ],
        "storylines": [
            "Cooling-driven bodywork compromises can shuffle the competitive order.",
            "Long full-throttle run makes deployment strategy unusually visible.",
        ],
    },
    "brazil": {
        "circuit": "Autódromo José Carlos Pace, Interlagos",
        "coords": (-23.7036, -46.6997),
        "tz_local": "São Paulo (BRT)",
        "character": (
            "Short, anti-clockwise, hilly and permanently interesting. Barely 4.3 km, so the "
            "field is compressed and traffic is constant. Weather is famously volatile — "
            "sun and a downpour within the same hour is normal."
        ),
        "key_corners": [
            ("Turns 1–2 — Senna S", "Downhill left-hander at the end of the main straight; the classic overtaking spot and a lap-one flashpoint."),
            ("Turn 4 — Descida do Lago", "Downhill left where cars can run side by side."),
            ("Subida dos Boxes", "The long, climbing final sequence onto the pit straight — exit speed here sets up the next lap's pass."),
        ],
        "overtaking": (
            "Very good. A long uphill straight with DRS into a downhill braking zone, plus "
            "several secondary opportunities. Interlagos reliably produces genuine racing."
        ),
        "tyre_notes": (
            "Anti-clockwise loading stresses the right-hand tyres and the neck. The surface "
            "is bumpy and the short lap means high stint lap counts and traffic management."
        ),
        "drs": 2,
        "lap_record": "1:10.540 — Valtteri Bottas, 2018",
        "notes": [
            "First Grand Prix: 1973.",
            "Anti-clockwise, one of only a handful on the calendar.",
            "The circuit has decided multiple World Championships and the crowd knows it.",
        ],
        "storylines": [
            "Rain probability is high enough that a wet-weather plan is essential preparation.",
            "Late-season championship maths often becomes live here.",
        ],
    },
    "las-vegas": {
        "circuit": "Las Vegas Strip Circuit",
        "coords": (36.1147, -115.1728),
        "tz_local": "Las Vegas (PST)",
        "character": (
            "A cold, late-night, very low-downforce blast down the Strip. Enormous top "
            "speeds and almost no corners of consequence — the whole weekend is defined by "
            "the struggle to get tyres into their working range on a cold street surface."
        ),
        "key_corners": [
            ("Turn 1", "Tight left immediately after the start; first-lap chaos point."),
            ("Turns 5–7", "The slow sequence before the Strip — traction out of here defines the long straight."),
            ("Turn 14", "End of the Strip; the heaviest braking zone and the primary overtaking place."),
        ],
        "overtaking": (
            "Good, thanks to a very long full-throttle stretch into a slow corner. Slipstream "
            "effects are large because everyone runs skinny wings."
        ),
        "tyre_notes": (
            "The defining issue is cold: graining and warm-up dominate, and track temperature "
            "keeps falling through the night. Getting temperature into the fronts on an out-lap "
            "is genuinely difficult."
        ),
        "drs": 2,
        "lap_record": "1:34.876 — Oscar Piastri, 2024",
        "notes": [
            "First Grand Prix: 2023 (the modern Strip circuit).",
            "Sessions run very late local time — a scheduling quirk worth explaining on air for European viewers.",
            "Cold-weather running makes it one of the least representative weekends of the year for form.",
        ],
        "storylines": [
            "Track temperature falling through the session changes the tyre picture in real time.",
            "Low-downforce trim exaggerates power-unit and deployment differences.",
        ],
    },
    "qatar": {
        "circuit": "Lusail International Circuit",
        "coords": (25.4900, 51.4542),
        "tz_local": "Lusail (AST)",
        "character": (
            "A fast, flowing, medium-to-high-speed loop originally built for motorcycles. "
            "Almost no slow corners and very high sustained lateral loads — physically brutal "
            "and historically the hardest race of the year on tyre construction."
        ),
        "key_corners": [
            ("Turn 1", "Heavy braking off the main straight; the main passing opportunity."),
            ("Turns 6–7", "Fast, sustained loading that generates the tyre stress the circuit is known for."),
            ("Turns 12–14", "Quick final sequence onto the straight; exit speed sets up the DRS run."),
        ],
        "overtaking": (
            "Moderate. The main straight offers a genuine chance, but the flowing middle "
            "sector makes following closely difficult and rewards clean air."
        ),
        "tyre_notes": (
            "The headline issue: sustained high-speed loading has previously forced mandatory "
            "maximum stint lengths. Expect tyre-life limits to be a central strategic story, "
            "and check the FIA event notes for any imposed stint cap."
        ),
        "drs": 1,
        "lap_record": "1:22.384 — Lando Norris, 2024",
        "notes": [
            "First Grand Prix: 2021.",
            "Run at night under lights, with big day-to-night track temperature swings.",
            "Previous editions have required enforced maximum stint lengths on tyre-safety grounds.",
        ],
        "storylines": [
            "Any FIA-mandated stint limit turns the race into a fixed-stop sprint — check the documents.",
            "Late-season championship permutations are often decided in this closing triple-header.",
        ],
    },
    "united-arab-emirates": {
        "circuit": "Yas Marina Circuit, Abu Dhabi",
        "coords": (24.4672, 54.6031),
        "tz_local": "Abu Dhabi (GST)",
        "character": (
            "The season finale, run into the dusk so that track temperature drops steadily "
            "through the race. Reprofiled in 2021 into a faster, more flowing lap with "
            "banked corners; still fundamentally a traction-and-braking circuit."
        ),
        "key_corners": [
            ("Turns 5–6", "End of the first long straight — the strongest overtaking opportunity."),
            ("Turns 9 and the banked left", "Faster, flowing sequence introduced in the 2021 reprofile."),
            ("Final sector", "Tight, walled, low-speed section where traction and kerb use decide the lap."),
        ],
        "overtaking": (
            "Improved since the reprofile but still not easy; the long straights into heavy "
            "braking zones are where it happens, helped by two DRS zones."
        ),
        "tyre_notes": (
            "Falling track temperature through the race means graining early and better grip "
            "later — the classic Yas Marina strategy question is when to give up track position."
        ),
        "drs": 2,
        "lap_record": "1:26.103 — Max Verstappen, 2021",
        "notes": [
            "First Grand Prix: 2009.",
            "The day-to-night transition is the defining feature: qualifying conditions match the start of the race, not the end.",
            "As the finale, it carries every remaining championship, contract and farewell storyline of the season.",
        ],
        "storylines": [
            "Season finale — title, constructors' places and driver farewells all converge here.",
            "Falling temperatures make the second half of the race quicker; expect late strategy gambles.",
        ],
    },
}


def get(slug):
    """Reference data for a racing slug, or {} when we have none yet."""
    return CIRCUITS.get(slug, {})
