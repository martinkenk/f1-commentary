"""Dutch Grand Prix 2026 — page content.

Edit the prose here; structure/engine live in f1lib.py. build_pages(ctx, env)
returns {slug: {kicker,title,sub,body}} for every non-results nav page.

Sources: Formula1.com "Need to Know" preview (facts/quotes/history) and the FIA
event documents for this round — Doc 2 (Competition Notes - Pirelli Preview) and
Doc 3 (Power Unit Information), both published 19 Aug 2026. The circuit map and
tyre-compound table are lifted from those sources (see assets_src/).
"""
from f1lib import card, stat, ul, quote, news_item, render_news
from content_generic import pending, ul_or, _fmt

FIA_EVENT_URL = ("https://www.fia.com/documents/championships/"
                 "fia-formula-one-world-championship-14/season/season-2026-2072/"
                 "event/Dutch%20Grand%20Prix")


def build_pages(ctx, env):
    schedule_rows = env["schedule_rows"]
    weather_cards = env["weather_cards"]
    TZ_LOCAL_LABEL = ctx["tz_local"]
    TZ_EAST_LABEL = ctx["tz_east"]
    ref = ctx.get("ref") or {}

    PAGES = {}

    # ---- 1. OVERVIEW ----------------------------------------------------------
    PAGES["overview"] = dict(
        kicker="Round 12 · Sprint weekend",
        title="Weekend Overview",
        sub="F1 resumes after the summer break at Zandvoort — a sprint weekend, Verstappen's home "
            "race, and for now the last Dutch Grand Prix on the calendar.",
        body=f"""
    <div class="stat-row">
      {stat("4.259 km", "Lap length")}
      {stat("72", "Race laps")}
      {stat("306.587 km", "Race distance")}
      {stat("1952", "First Grand Prix")}
      {stat("Sprint", "Format", "4th sprint of 2026")}
    </div>

    <div class="callout">
      <strong>The one-line setup:</strong> Kimi Antonelli leads Lewis Hamilton by 50 points as the season
      resumes, Max Verstappen arrives on the back of consecutive podiums hoping to give the Orange Army
      something to remember at what is scheduled to be Zandvoort's last race for now, and Red Bull make a
      surprise driver change before a wheel is turned.
    </div>

    <h2 class="sec">Storylines to have loaded for FP1</h2>
    <div class="grid cols-2">
      {card("Lawson in, Hadjar out, Tsunoda back", ul([
         "Isack Hadjar will miss the race with a wrist injury sustained over the summer break.",
         "<strong>Liam Lawson</strong> is recalled to Red Bull Racing alongside Verstappen for the weekend.",
         "<strong>Yuki Tsunoda</strong> in turn gets a surprise recall to Racing Bulls in Lawson's seat.",
         "Full detail on the Rookies &amp; Line-ups page.",
      ]), "bi-people", "accent")}

      {card("Verstappen's home race — and a deal to celebrate", ul([
         "The four-time champion has back-to-back podiums from Spa and the Hungaroring.",
         "Zandvoort is scheduled to be the Dutch GP's last edition for now, so expect heavy farewell framing.",
         "Verstappen re-signed with Red Bull through 2030 in the days before the race.",
      ]), "bi-flag", "accent")}

      {card("Antonelli's title lead, and a tight chase behind", ul([
         "Antonelli holds a <strong>50-point</strong> lead over Hamilton after the summer break.",
         "Russell sits third, with Leclerc a further 22 points back in fourth.",
         "Norris took McLaren's first win of the season last time out in Hungary.",
      ]), "bi-trophy")}

      {card("Only one hour of practice", ul([
         "Sprint format means FP1 is the only practice before parc fermé locks in car set-up.",
         "Pirelli's preview flags strong wind off the North Sea as the biggest variable all weekend.",
         "Honda's revamped 'Spec 2' power unit is scheduled to debut in Aston Martin's car this weekend.",
      ]), "bi-stopwatch")}
    </div>

    <h2 class="sec">Quick session times</h2>
    <div class="table-wrap">
      <table class="data">
        <thead><tr><th>Session</th><th>Day</th><th>{TZ_LOCAL_LABEL}</th><th>{TZ_EAST_LABEL}</th></tr></thead>
        <tbody>
          {schedule_rows()}
        </tbody>
      </table>
    </div>
    <p class="src">All on-air times in Zandvoort local and Tallinn / Eastern European time. Full forecast on the Schedule &amp; Weather page.</p>
    """)

    # ---- 2. CIRCUIT -------------------------------------------------------
    PAGES["circuit"] = dict(
        kicker="4.259 km · 72 laps",
        title="Circuit Zandvoort Guide",
        sub=ref.get("character", "A banked, old-school rollercoaster squeezed into the dunes."),
        body=f"""
    <h2 class="sec">Circuit map</h2>
    <figure class="circuit-fig">
      <img src="../assets/zandvoort_circuit_map_2026.png" alt="Official 2026 Formula 1 Circuit Zandvoort map showing turn numbers, sectors, the two straight mode zones, overtake detection/activation points and the speed trap"
           class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen">
      <figcaption><strong>2026 Circuit Zandvoort map</strong> — turn numbers (1&ndash;14), the three sectors
      (S1 pink / S2 yellow / S3 blue), the two <strong>Straight Mode Zones</strong> (the pit straight before
      Turn 1, and the short link between Turn 10 and Turn 11), the <strong>Overtake Detection</strong> point
      (between Turns 12 and 13) and <strong>Overtake Activation</strong> point (approaching Turn 14), and the
      speed trap on the pit straight. <strong>Click the map to zoom / view full screen.</strong>
      <span class="src">Source: Formula1.com 2026 track guide.</span></figcaption>
    </figure>

    <div class="stat-row">
      {stat("4.259 km", "Circuit length")}
      {stat("72", "Race laps")}
      {stat("306.587 km", "Race distance")}
      {stat("2", "Straight Mode Zones", "Pit straight & T10 &rarr; T11")}
    </div>

    <h2 class="sec">Corners that matter</h2>
    <div class="grid cols-3">
      {"".join(card(name, f"<p>{desc}</p>", "bi-signpost-split") for name, desc in ref.get("key_corners", []))}
    </div>

    <div class="grid cols-2">
      {card("Where the passes happen", f"<p>{ref.get('overtaking', '')}</p>", "bi-arrow-left-right", "accent")}
      {card("What it does to the tyres", f"<p>{ref.get('tyre_notes', '')}</p>", "bi-record-circle")}
    </div>

    <h2 class="sec">Worth knowing</h2>
    {card("Circuit notes", ul_or(ref.get("notes")), "bi-info-circle")}

    <div class="callout">
      <strong>Lap record:</strong> {_fmt(ref.get("lap_record"))}. Zandvoort's first World Championship race
      was in 1952; it returned to the calendar in 2021 after a 36-year absence, and this is scheduled to be
      its last edition for now — expect plenty of farewell framing all weekend.
    </div>
    """)

    # ---- 3. TYRES -----------------------------------------------------------
    PAGES["tyres"] = dict(
        kicker="Pirelli · Doc 2",
        title="Tyres & Strategy",
        sub="Pirelli's official compound choice and tyre prescriptions for Zandvoort, from the FIA event documents.",
        body=f"""
    <div class="callout">
      <strong>FIA-confirmed:</strong> compounds for this event are the <strong>C2 (hard)</strong>,
      <strong>C3 (medium)</strong> and <strong>C4 (soft)</strong> — the same trio used at Zandvoort last year.
      Mandatory race tyres (Pirelli's Doc 2): <strong>C2</strong> and <strong>C3</strong>.
    </div>

    <h2 class="sec">Compound allocation</h2>
    <figure class="circuit-fig">
      <img src="../assets/netherlands_pirelli_compounds_2026.png" alt="FIA/Pirelli compound allocation table for the 2026 Dutch Grand Prix showing tyre codes for C2, C3, C4, Intermediate and Wet, plus the mandatory race tyres box"
           class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen">
      <figcaption><strong>Official compound &amp; mandatory-tyre table</strong> — lifted directly from the FIA's
      Competition Notes (Doc 2, Pirelli Preview) for this event.
      <span class="src">Source: FIA event documents, 19 Aug 2026.</span></figcaption>
    </figure>

    <div class="grid cols-2">
      {card("Pirelli's weekend preview", ul([
         "\u201cThe track, situated just 40 km from Amsterdam, offers a low level of grip both because of "
         "the nature of its asphalt&hellip; and because of the sand blown onto the circuit from the nearby "
         "beaches,\u201d Pirelli's preview reads &mdash; grip can shift from one session to the next.",
         "\u201cThe circuit is particularly demanding on tyres in terms of energy density, owing to its short "
         "lap length and numerous corners&hellip; the two banked turns&hellip; generate extremely high "
         "vertical and lateral forces on the tyres.\u201d",
         "Aero-downforce demand is <strong>high</strong> &mdash; \u201cvery similar to&hellip; Budapest.\u201d",
         "Sprint format means only one hour of practice to settle on a set-up before parc fermé.",
         "\u201cThe hard is likely to be the reference compound for Sunday&rsquo;s race, [while] the two "
         "softer options could both prove effective choices for Saturday&rsquo;s Sprint.\u201d",
      ]), "bi-quote", "accent")}

      {card("Pressures &amp; camber (FIA Doc 2)", ul([
         "<strong>Slicks</strong> — front min. 26.0 psi / expected &ge;27.0 psi, camber limit &minus;2.75&deg;; "
         "rear min. 25.0 psi / expected &ge;26.0 psi, camber limit &minus;1.5&deg;.",
         "<strong>Intermediates</strong> — front min. 27.5 psi / &ge;28.5 psi, camber &minus;3&deg;; "
         "rear min. 26.5 psi / &ge;27.5 psi, camber &minus;2&deg;.",
         "<strong>Wets</strong> — front min. 26.0 psi / &ge;28.5 psi, camber &minus;3&deg;; "
         "rear min. 25.0 psi / &ge;27.5 psi, camber &minus;2&deg;.",
         "Maximum tyre-blanket heating time is <strong>2 hours</strong> for all three tyre types.",
         "Cut-off for fitting tyres ahead of Sunday's race: <strong>4 hours</strong> before the start.",
      ]), "bi-thermometer-half")}
    </div>

    <div class="grid cols-2">
      {card("What this circuit does to a tyre", f"<p>{ref.get('tyre_notes', '')}</p>", "bi-record-circle")}
      {card("Why strategy matters here", f"<p>{ref.get('overtaking', '')}</p>"
            "<p>With passing so hard-won, the undercut and safety-car timing usually decide the race far more "
            "than raw pace.</p>", "bi-diagram-3")}
    </div>

    {pending("Long-run degradation data", "after Friday practice", "bi-graph-down")}
    """)

    # ---- 4. ROOKIES / LINE-UPS ----------------------------------------------
    PAGES["rookies"] = dict(
        kicker="Line-ups",
        title="Rookies & Line-ups",
        sub="A driver-swap weekend at Red Bull, plus the standing rookie-practice rule.",
        body=f"""
    {card("Red Bull's contingency plan", ul([
       "<strong>Isack Hadjar</strong> sustained a wrist injury over the summer break (first reported by "
       "De Telegraaf) and will sit out the Dutch Grand Prix.",
       "<strong>Liam Lawson</strong> is recalled to Red Bull Racing to partner Max Verstappen — his first "
       "outing in the RB22, on short notice, against his home-race team-mate.",
       "<strong>Yuki Tsunoda</strong> gets a surprise call-up in turn, racing for Racing Bulls in Lawson's "
       "regular seat.",
       "Never before in Red Bull's 22-year F1 history had the team recalled a driver it had previously "
       "let go — Lawson is the exception this weekend.",
    ]), "bi-arrow-left-right", "accent")}

    {card("The rookie rule", ul([
       "Every team must field a rookie driver in <strong>two FP1 sessions per car</strong> across the season "
       "— four rookie outings per team in total.",
       "A 'rookie' is a driver who has started no more than two World Championship Grands Prix.",
       "This is a sprint weekend, so there is only <strong>one hour of practice in total</strong> — teams "
       "must weigh any rookie outing against losing their only practice hour for the race driver.",
    ]), "bi-person-badge")}

    {pending("Confirmed rookie FP1 line-ups for this round", "in the day before the event")}
    """)

    # ---- 5. STANDINGS --------------------------------------------------------
    st = ctx.get("standings") or {}
    if st.get("drivers"):
        standings_body = f"""
    <div class="callout"><strong>Standings as of {st.get('as_of', 'the most recent completed round')}.</strong>
      Antonelli leads Hamilton by 50 points and Russell by a wider margin heading into Zandvoort, with
      Leclerc 22 points behind third-placed Russell — these refresh as each subsequent race is built into
      the hub.</div>

    <div class="standings-grid">
      <div>
        <h2 class="sec">Drivers</h2>
        <div class="table-wrap"><table class="data ranked">
          <thead><tr><th>Pos</th><th>Driver</th><th>Team</th><th class="num">Pts</th></tr></thead>
          <tbody>{st['drivers']}</tbody>
        </table></div>
      </div>
      <div>
        <h2 class="sec">Constructors</h2>
        <div class="table-wrap"><table class="data ranked">
          <thead><tr><th>Pos</th><th>Team</th><th class="num">Pts</th></tr></thead>
          <tbody>{st.get('ctors', '')}</tbody>
        </table></div>
      </div>
    </div>
    """
    else:
        standings_body = pending("Championship standings", "after the most recent race", "bi-trophy")
    PAGES["standings"] = dict(
        kicker="Championship",
        title="Championship & Form",
        sub="Antonelli holds a 50-point lead as the season resumes from the summer break.",
        body=standings_body)

    # ---- 6. TEAM WATCH --------------------------------------------------------
    PAGES["teams"] = dict(
        kicker="Team watch",
        title="Team Watch & News",
        sub="Paddock storylines to carry into the weekend, beyond the Red Bull driver swap.",
        body=f"""
    <div class="grid cols-2">
      {card("Aston Martin — Honda 'Spec 2' debut", ul([
         "Honda have detailed a revamped power unit set to debut in Aston Martin's car from this weekend.",
         "It follows recent chassis upgrades as the team tries to climb away from the back of the field.",
      ]), "bi-lightning-charge", "accent")}
      {card("Cadillac's new leadership", ul([
         "Marcin Budkowski has replaced Graeme Lowdon as Team Principal with immediate effect.",
         "Budkowski returns to the paddock after most recently serving as Executive Director at Alpine.",
      ]), "bi-people")}
      {card("Williams — Albon signs on for 2027", ul([
         "Alex Albon will stay with Williams for a sixth F1 season in 2027, presented as a contract extension.",
         "The Race understands it relates to exit clauses in his existing multi-year deal rather than a new contract.",
      ]), "bi-file-earmark-text")}
      {card("Racing Bulls / Red Bull reshuffle", ul([
         "Racing Bulls lose Lawson to the top team for the weekend but gain Tsunoda back in his place.",
         "The team sits fifth in the constructors' standings at the summer break.",
      ]), "bi-arrow-left-right")}
    </div>

    <div class="callout">
      Weekend news from Formula1.com and The Race is collected automatically on the
      <strong>Weekend News</strong> page as soon as it is published, split into general stories and
      reports for each completed session.
    </div>
    """)

    # ---- 7. UPGRADES --------------------------------------------------------
    PAGES["upgrades"] = dict(
        kicker="Development",
        title="Car Development & Upgrades",
        sub="Upgrade packages brought to Zandvoort, from the FIA's car presentation submissions.",
        body=f"""
    {card("What we know ahead of the FIA filing", ul([
       "Honda's new-specification power unit is scheduled to debut in Aston Martin's car this weekend — "
       "see the Power Unit page for the detail that's confirmed so far.",
       "Teams must submit a <strong>car presentation</strong> to the FIA listing every changed component "
       "and the reason for the change; that document is normally published on the <strong>Friday</strong> "
       "of the race week.",
    ]), "bi-tools", "accent")}

    {pending("FIA car presentation submissions for this round", "on the Friday of the race week")}
    """)

    # ---- 8. POWER UNIT --------------------------------------------------------
    PAGES["powerunit"] = dict(
        kicker="FIA Doc 3",
        title="Power Unit & Override",
        sub="The FIA's official power-and-energy map for Zandvoort — Doc 3, published 19 Aug 2026.",
        body=f"""
    <div class="callout">
      <strong>FP &amp; Qualifying energy limits, called out:</strong> the maximum recharge per lap is
      <strong>9.0 MJ in Free Practice</strong> but only <strong>7.5 MJ in Sprint Qualifying &amp; Qualifying</strong>
      — a full 1.5 MJ tighter once it matters for grid position, which is exactly why Saturday one-lap pace
      can look different from what Friday's single practice hour suggested.
    </div>

    <h2 class="sec">Maximum recharge per lap (Article C5.2.10)</h2>
    <div class="table-wrap"><table class="data">
      <thead><tr><th>Sprint &amp; Race — override not active</th><th>Sprint &amp; Race — override active</th>
      <th>Sprint Qualifying &amp; Qualifying</th><th>Free Practice</th><th>Out laps (other than Sprint/Race)</th></tr></thead>
      <tbody><tr><td>8.5 MJ</td><td>9.0 MJ</td><td>7.5 MJ</td><td>9.0 MJ</td><td>9.0 MJ</td></tr></tbody>
    </table></div>

    <div class="grid cols-2">
      {card("Overtake system (Article B7.2)", ul([
         "Detection gap: <strong>1.0 s</strong>.",
         "Detection line: <strong>3431 m</strong> into the lap (lap-distance loop L20).",
         "Activation line: <strong>3648 m</strong> into the lap (loop L21) — on the run toward Turn 10/11.",
         "Maximum PU power-reduction rate once power-limited: <strong>100 kW/s</strong> over a "
         "<strong>2411 m</strong> power-limited distance.",
      ]), "bi-lightning-charge", "accent")}
      {card("Where the exceptions apply", ul([
         "T1&ndash;T3 (350&ndash;800 m), T8&ndash;T10 (2000&ndash;2450 m) and T11&ndash;T13 (3100&ndash;3400 m) "
         "are the sectors where a Power Limited Pending reduction may exceed 150 kW (up to 350 kW).",
         "A reset of MGU-K power reduction is permitted on the exit of Turn 14 (3700&ndash;4200 m).",
         "Outside Sprint &amp; Race, every session (including Qualifying) runs the more permissive "
         "\u201cBase &ndash; Overtake\u201d power curve rather than the race-day standard map.",
      ]), "bi-battery-charging")}
    </div>

    <div class="grid cols-2">
      {card("What changed for 2026", ul([
         "Roughly a <strong>50/50 split</strong> between internal combustion and electrical power.",
         "The <strong>MGU-H is gone</strong>; the MGU-K is substantially more powerful.",
         "<strong>100% sustainable fuel</strong>.",
         "<strong>Manual Override</strong> replaces DRS as the overtaking aid — extra energy the chasing "
         "driver can call on inside the detection/activation window above.",
      ]), "bi-gear")}
      {card("Honda 'Spec 2' at Zandvoort", ul([
         "Honda have detailed an updated power unit for Aston Martin, intended to debut this weekend.",
         "It follows recent chassis upgrades as the team tries to climb clear of the back of the field.",
         "Watch the Power Unit page &amp; Team Watch for how it lands across FP1/qualifying trim.",
      ]), "bi-cpu")}
    </div>

    <p class="src">Source: FIA Formula 1 Power Unit Information to the Teams and PUMs, Document 3,
    2026 Dutch Grand Prix (19 Aug 2026). <a href="{FIA_EVENT_URL}" target="_blank" rel="noopener">FIA event documents</a>.</p>
    """)

    # ---- 9. FACTS -----------------------------------------------------------
    PAGES["facts"] = dict(
        kicker="Stats",
        title="Facts, Stats & Records",
        sub="Reference numbers and history for Circuit Zandvoort.",
        body=f"""
    <div class="stat-row">
      {stat("4.259 km", "Circuit length")}
      {stat("72", "Race laps")}
      {stat("306.587 km", "Race distance")}
      {stat("1952", "First Grand Prix")}
    </div>

    <div class="grid cols-2">
      {card("Lap record", f'<p><strong>{_fmt(ref.get("lap_record"))}</strong></p>'
            "<p>Official race lap records only count laps set during the Grand Prix itself.</p>",
            "bi-stopwatch", "accent")}
      {card("Circuit notes", ul_or(ref.get("notes")), "bi-journal-text")}
    </div>

    <h2 class="sec">Last five Dutch Grands Prix</h2>
    <div class="table-wrap"><table class="data">
      <thead><tr><th>Year</th><th>Polesitter</th><th>Winner</th></tr></thead>
      <tbody>
        <tr><td>2025</td><td>Oscar Piastri (McLaren)</td><td>Oscar Piastri (McLaren)</td></tr>
        <tr><td>2024</td><td>Lando Norris (McLaren)</td><td>Lando Norris (McLaren)</td></tr>
        <tr><td>2023</td><td>Max Verstappen (Red Bull)</td><td>Max Verstappen (Red Bull)</td></tr>
        <tr><td>2022</td><td>Max Verstappen (Red Bull)</td><td>Max Verstappen (Red Bull)</td></tr>
        <tr><td>2021</td><td>Max Verstappen (Red Bull)</td><td>Max Verstappen (Red Bull)</td></tr>
      </tbody>
    </table></div>
    <p class="src">Piastri converted pole into victory at last year's Dutch Grand Prix. Source: Formula1.com.</p>

    {quote(
        "I&rsquo;ve only done this one on a bike! Zandvoort is actually a lovely circuit that has been "
        "adapted really well for modern F1. It&rsquo;s still difficult to overtake on&hellip; but the banking "
        "makes a huge difference. You don&rsquo;t really appreciate the banking until you go around it at "
        "Turn 3&hellip; It is a nice, flowing track. You&rsquo;ve got to have commitment, particularly in the "
        "middle sector, which is undulating&hellip; because it&rsquo;s a punishing circuit as well.",
        "Jolyon Palmer, former Renault F1 driver")}
    """)

    # ---- 10. MOMENTS ----------------------------------------------------------
    PAGES["moments"] = dict(
        kicker="History",
        title="Great Moments",
        sub="Memorable races and moments at Circuit Zandvoort.",
        body=f"""
    {card("James Hunt's maiden win — 1975 Dutch Grand Prix", ul([
       "A damp track turning dry produced F1's classic tyre gamble: Hunt pitted after seven laps for slicks "
       "while pole-sitter Niki Lauda and most of the field stayed out on wets.",
       "Once the rest of the field eventually pitted, Hunt emerged in the lead — a position Lauda desperately "
       "wanted back but could never retake.",
       "It was Hunt's first Grand Prix win and the only win ever recorded by Lord Hesketh's small independent "
       "team, toppling the might of Ferrari with a fledgling underdog operation.",
    ]), "bi-stars", "accent")}

    {card("Verstappen's home dominance (2021–2023)", ul([
       "Three straight Dutch GP poles and wins for Max Verstappen from the race's 2021 return through 2023, "
       "in front of an orange-clad crowd that turns the grandstands into a genuine broadcast feature.",
       "Piastri and Norris have taken the last two editions, but Verstappen's home-race atmosphere remains "
       "the sport's loudest.",
    ]), "bi-flag")}

    {card("History in brief", ul([
       "Zandvoort's first World Championship Grand Prix was in 1952; it returned in 2021 after a 36-year absence.",
       "The 2026 race is scheduled to be one of the venue's last under its current deal — expect plenty of "
       "farewell framing across the weekend.",
    ] + ref.get("notes", [])), "bi-journal-richtext")}
    """)

    # ---- 11. SCHEDULE ----------------------------------------------------------
    PAGES["schedule"] = dict(
        kicker="Timing",
        title="Schedule & Weather",
        sub=f"All sessions in {TZ_LOCAL_LABEL} and {TZ_EAST_LABEL}, with the live forecast attached to each.",
        body=f"""
    <div class="callout"><strong>Sprint weekend</strong> — one hour of practice, then Sprint Qualifying, the
    Sprint, Qualifying and the Grand Prix.</div>

    <h2 class="sec">Session times</h2>
    <div class="table-wrap"><table class="data">
      <thead><tr><th>Session</th><th>Day</th><th>{TZ_LOCAL_LABEL}</th><th>{TZ_EAST_LABEL}</th></tr></thead>
      <tbody>{schedule_rows()}</tbody>
    </table></div>

    <h2 class="sec">Weather</h2>
    {weather_cards()}
    """)

    # ---- 12. NOTES ----------------------------------------------------------
    PAGES["notes"] = dict(
        kicker="Cheat sheet",
        title="Commentator's Cheat Sheet",
        sub="The short version for the Dutch Grand Prix — everything worth having to hand.",
        body=f"""
    <div class="grid cols-2">
      {card("The circuit in one paragraph", f"<p>{ref.get('character', '')}</p>", "bi-mic", "accent")}
      {card("Numbers to have ready", ul([
         "Circuit length: <strong>4.259 km</strong>",
         "Race: <strong>72 laps</strong>, 306.587 km",
         "First Grand Prix here: <strong>1952</strong> (returned 2021)",
         "Lap record: <strong>" + _fmt(ref.get("lap_record")) + "</strong>",
         "Format: <strong>Sprint weekend</strong> — one hour of practice only",
         "Tyres: <strong>C2 / C3 / C4</strong>, mandatory race compounds C2 &amp; C3",
      ]), "bi-list-ol")}
    </div>

    <div class="grid cols-2">
      {card("Talking points", ul_or(ref.get("storylines")) +
            ul(["Lawson recalled to Red Bull for the injured Hadjar; Tsunoda back at Racing Bulls.",
                "Verstappen re-signed with Red Bull through 2030 days before his home race.",
                "Antonelli leads Hamilton by 50 points; Norris won last time out in Hungary."]),
            "bi-chat-quote")}
      {card("Name-check these corners", ul_or(
         [f"<strong>{n}</strong> — {d}" for n, d in ref.get("key_corners", [])]),
         "bi-signpost-split")}
    </div>

    <div class="callout">
      <strong>Official documents:</strong>
      <a href="{FIA_EVENT_URL}" target="_blank" rel="noopener">FIA event documents for this round</a> —
      race-control notes, the Pirelli tyre prescriptions (Doc 2), the power-unit map (Doc 3) and every
      stewards' decision as the weekend runs.
    </div>

    {pending("Session-by-session commentary notes", "as the weekend runs", "bi-mic")}
    """)

    return PAGES
