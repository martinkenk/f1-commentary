"""Hungarian Grand Prix 2026 — page content.

Edit the prose here; structure/engine live in f1lib.py. build_pages(ctx, env)
returns {slug: {kicker,title,sub,body}} for every non-results nav page.
"""
from f1lib import card, stat, ul, quote


def build_pages(ctx, env):
    schedule_rows = env["schedule_rows"]
    weather_cards = env["weather_cards"]
    WEATHER_OK = env["weather_ok"]
    TZ_LOCAL_LABEL = ctx["tz_local"]
    TZ_EAST_LABEL = ctx["tz_east"]

    PAGES = {}

    # ---- 1. OVERVIEW ---------------------------------------------------------
    PAGES["overview"] = dict(
        kicker="FP1 · Friday",
        title="Weekend Overview",
        sub="Everything at a glance before lights-out on the commentary desk — the last race before F1's 2026 summer break.",
        body=f"""
    <div class="stat-row">
      {stat("14", "Round of 24")}
      {stat("4.381 km", "Lap length")}
      {stat("70", "Race laps")}
      {stat("306.63 km", "Race distance")}
      {stat("14", "Corners")}
    </div>

    <div class="callout">
      <strong>The one-line setup:</strong> Kimi Antonelli arrives as championship leader and Spa winner,
      Aston Martin finally unleash their long-awaited Adrian Newey-influenced upgrade, and a slow, hot,
      twisty Hungaroring — "Monaco without the walls" — rewards downforce and tyre management over straight-line speed.
    </div>

    <h2 class="sec">Storylines to have loaded for FP1</h2>
    <div class="grid cols-2">
      {card("Antonelli's title momentum", ul([
         "Leads the drivers' standings by <strong>45 pts</strong> over Lewis Hamilton after winning at Spa (his 6th win of 2026).",
         "Working on curbing a track-limits habit — even his father Marco told him off after Spa.",
         "Mercedes has fixed the deployment software gremlin that hurt team-mate Russell in Belgium.",
      ]), "bi-trophy", "accent")}

      {card("Aston Martin's big moment", ul([
         "Rolling out a sweeping chassis/aero upgrade — new nose, revised surfaces, major weight reduction.",
         "Newey: team started the '26 car late and were 'on the back foot from the start'.",
         "Goal is simple — <em>get back racing the midfield</em> after being 2s adrift at Spa.",
      ]), "bi-tools", "accent")}

      {card("Five rookies out in FP1", ul([
         "McLaren, Mercedes, Alpine, Haas and Cadillac all sit a regular out.",
         "Fornaroli (McLaren), Vesti (Mercedes), Aron (Alpine), Hirakawa (Haas), Herta (Cadillac).",
         "Great human-interest material for the opening hour — see the Rookies page.",
      ]), "bi-person-badge")}

      {card("Upgrade war at the rear wing", ul([
         "Ferrari brings its 'Macarena' rear wing, borrowing winglet cascades from McLaren.",
         "McLaren finally trials its flip-over low-drag wing (Piastri) — test only, reverts for quali.",
         "Mercedes also runs a new rear-wing spec with extra winglets.",
      ]), "bi-airplane")}
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
    <p class="src">All on-air times in Budapest local and Tallinn / Eastern European time. Full forecast on the Schedule &amp; Weather page.</p>
    """)

    # ---- 2. CIRCUIT ----------------------------------------------------------
    PAGES["circuit"] = dict(
        kicker="Track Guide",
        title="Hungaroring Circuit Guide",
        sub="A tight, twisty 4.381 km 'kart track' on the outskirts of Budapest — one real straight, and one real overtaking spot.",
        body=f"""
    <div class="stat-row">
      {stat("4.381 km", "Circuit length")}
      {stat("14", "Corners")}
      {stat("476 m", "Pole → T1 braking")}
      {stat("20.56 s", "Pit-stop time loss")}
      {stat("69", "Overtakes in 2025")}
    </div>

    <h2 class="sec">Circuit map</h2>
    <figure class="circuit-fig">
      <img src="../assets/hungaroring_circuit_map_2026.png" alt="Official 2026 Formula 1 Hungaroring circuit map showing turn numbers, straight mode zones, overtake detection and activation points, sectors and the speed trap"
           class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen">
      <figcaption><strong>2026 Hungaroring map</strong> — turn numbers (1–14), the three sectors (S1 magenta / S2 yellow / S3 blue), the two <strong>Straight Mode Zones</strong> (red dashed — the 2026 replacement for DRS), the <strong>Overtake Detection</strong> and <strong>Overtake Activation</strong> points, and the speed trap on the pit straight. <strong>Click the map to zoom / view full screen.</strong> <span class="src">Source: Formula1.com 2026 track guide.</span></figcaption>
    </figure>

    <div class="grid cols-3">
      {card("Straight Mode Zones (2026)", ul([
         "No more DRS in 2026 — cars use <strong>Straight Mode</strong> (low-drag active aero) in designated zones.",
         "<strong>Zone 1</strong> — the pit straight into Turn 1 (main overtaking chance).",
         "<strong>Zone 2</strong> — the run between Turn 3 and Turn 4.",
         "A third dashed stretch runs along the Turn 11–12 flat-out section.",
      ]), "bi-arrow-right-square")}
      {card("Overtake system & speed trap", ul([
         "<strong>Overtake Detection</strong> sits just after Turn 13.",
         "<strong>Overtake Activation</strong> is on the exit of Turn 14 onto the main straight.",
         "The <strong>speed trap</strong> is on the pit straight — watch top-speed deltas there.",
         "Overtake energy (extra deployment) is the 2026 equivalent of the old push-to-pass.",
      ]), "bi-lightning-charge")}
      {card("2026 track changes (FIA)", ul([
         "Asphalt repairs approaching <strong>Turn 1 and Turn 12</strong>.",
         "TSP 15 moved to 10 m from the S2 line.",
         "New TSP 16 at 100 m from Turn 12.",
      ]), "bi-cone-striped")}
    </div>

    <div class="callout">
      <strong>Set-up note:</strong> Because there's only one real straight, teams run set-ups
      <em>very similar to Monaco</em> — maximum downforce, mechanical grip and traction over top speed.
      Turns 1 and 12 have been <strong>resurfaced for 2026</strong> (after last year's pit-lane and grid work).
    </div>

    <h2 class="sec">Lap-by-lap, sector by sector</h2>
    {card("Jolyon Palmer's walkthrough", f'''
    <p><strong>Sector 1</strong> — "Basically two corners: a big braking zone at Turn 1, a relatively
    straightforward right-hander but quite bumpy in the braking area, so it can induce front locking,
    before Turn 2 which is slightly downhill."</p>
    <p><strong>Sector 2</strong> — "One of those sectors where you've got to find a rhythm because out of
    pretty much every corner you need to be positioned for the next. You go from Turn 4 into 6, get a tiny
    breather, then it carries you through the sweeping section, building speed all the way."</p>
    <p><strong>Sector 3</strong> — "Sometimes the tyres start to overheat and you scramble for grip. In the
    race you've got to set up your overtake coming out of Turn 14 — that's your one chance into Turn 1, and
    if not, into Turn 2. If you don't get it done there, you're probably following for the next lap."</p>
    {quote("It's not easy to overtake in Hungary, but you can. Turn 2 lends itself to it — you can go inside or outside, so it can be hard to defend.", "Jolyon Palmer, former Renault F1 driver (via Formula1.com)")}
    ''', "bi-signpost-2", "accent")}

    <div class="grid cols-2">
      {card("Where the overtakes happen", ul([
         "<strong>Turn 1</strong> — the main passing chance at the end of the start-finish straight (476 m from pole to the braking point), aided by Straight Mode + overtake energy.",
         "<strong>Turn 2</strong> — the secondary move; inside or outside line makes it hard to defend.",
         "Track position is king — expect close-running trains if the leaders bunch up.",
      ]), "bi-arrow-left-right")}

      {card("Character & challenges", ul([
         "180° corners and constant direction changes — compared to a kart track.",
         "Bumpy braking zone into T1 can trigger front locking.",
         "Grip levels among the lowest of the season; big track evolution across the weekend as rubber goes down.",
         "Rear axle works hard on traction — key for tyre deg.",
      ]), "bi-exclamation-triangle")}
    </div>

    <div class="callout watch">
      <strong>Commentary hook:</strong> The Hungaroring's low grip + high track temps mean FP1 times will
      look slow and tumble rapidly as the track rubbers in — worth flagging so viewers don't read too much
      into early laptimes.
    </div>

    {card("FIA Race Control notes worth knowing", ul([
       "<strong>Track limits:</strong> failing to negotiate the exit of <strong>Turn 14</strong> during any timed session invalidates that lap <em>and</em> the next.",
       "<strong>Lapping:</strong> blue-flag pre-warning at 3.0 s; blue panels/lights when the faster car is within <strong>1.2 s</strong> — slower car must yield at the first opportunity.",
       "<strong>Practice starts</strong> allowed on the right-hand side of the pit-exit road; after FP2 a car may complete two extra laps to practise starts on the grid.",
       "<strong>Safety Car restart</strong> resumption point: SC leaves the pits 1 min before the resumption and waits for the field after Turn 7.",
    ]), "bi-flag-fill", "accent")}
    <p class="src">Source: FIA Race Director's Competition Notes (2026 Hungarian GP).</p>
    """)

    # ---- 3. TYRES ------------------------------------------------------------
    PAGES["tyres"] = dict(
        kicker="Pirelli",
        title="Tyres & Strategy",
        sub="The three softest compounds, the hottest track temps of the year, and a genuine one-stop vs two-stop question.",
        body=f"""
    <div class="grid cols-3">
      {card('<span class="tag-soft">C5 · Soft</span>', "<p>Softest in the range. Best one-lap grip but vulnerable to graining and thermal deg in the heat.</p>", "bi-record-circle")}
      {card('<span class="tag-med">C4 · Medium</span>', "<p>The likely race workhorse. Balances grip and durability on a low-grip surface.</p>", "bi-record-circle")}
      {card('<span class="tag-hard">C3 · Hard</span>', "<p>With very high temps, teams are likely to <strong>favour the two hardest compounds</strong> for the race.</p>", "bi-record-circle")}
    </div>

    <div class="callout">
      <strong>Pirelli's headline:</strong> Same nomination as Monaco — <strong>C3, C4, C5</strong> — ideal for a
      slow track where traction and braking stability dominate. Surface roughness is pronounced on the older
      (un-resurfaced) sections, grip is among the lowest of the year, and track evolution is significant.
    </div>

    <h2 class="sec">The strategic picture</h2>
    <div class="grid cols-2">
      {card("Degradation & heat", ul([
         "Track temps at the Hungaroring are typically the <strong>highest of the season</strong>.",
         "Thermal degradation is the main performance driver, especially on the <strong>rear axle</strong> (traction phases).",
         "<strong>Graining</strong> may appear on the softer compounds.",
      ]), "bi-thermometer-sun", "accent")}

      {card("One-stop vs two-stop", ul([
         "Deg is expected to bring one- and two-stop strategies <strong>close together</strong> on total race time.",
         "Track position matters hugely — overtaking is difficult, so undercut/track position bias the call.",
         "Pit-stop time loss ~<strong>20.56 s</strong>.",
         "With very high temps, expect a lean toward the two hardest compounds.",
      ]), "bi-diagram-3", "accent")}
    </div>

    <div class="callout watch">
      <strong>FP1/FP2 watch:</strong> Long-run pace on C3 vs C4 and how quickly the rears grain will
      effectively decide whether Sunday is a one- or two-stopper. Note who runs heavy fuel late in FP2.
    </div>
    <p class="src">Source: Pirelli weekend preview via Formula1.com.</p>
    """)


    # ---- 4. ROOKIES ----------------------------------------------------------
    PAGES["rookies"] = dict(
        kicker="FP1 Line-ups",
        title="Rookies & FP1 Line-ups",
        sub="Five of the 11 teams sit a regular out for the mandatory rookie run in the opening 60 minutes.",
        body=f"""
    <div class="callout">
      <strong>The rule:</strong> As in 2025, every full-time driver must give up their car to a rookie
      (someone with two or fewer race starts) in <strong>two practice sessions</strong> across the season.
    </div>

    <div class="table-wrap">
      <table class="data">
        <thead><tr><th>Team</th><th>Rookie</th><th>Replaces</th><th>FP1 outings</th><th>Notes</th></tr></thead>
        <tbody>
          <tr><td>McLaren</td><td>Leonardo Fornaroli</td><td>Oscar Piastri</td><td><strong>2nd</strong> (1 prior: Barcelona)</td><td>FP1 debut last month in Norris' car</td></tr>
          <tr><td>Mercedes</td><td>Frederik Vesti</td><td>Kimi Antonelli</td><td><strong>6th</strong> (5 prior since 2023)</td><td>Driving the title leader's car</td></tr>
          <tr><td>Alpine</td><td>Paul Aron</td><td>Franco Colapinto</td><td><strong>8th</strong> (7 prior)</td><td>First Alpine run of 2026 (prior outings for Sauber &amp; Audi)</td></tr>
          <tr><td>Haas</td><td>Ryo Hirakawa</td><td>Ollie Bearman</td><td><strong>2nd of 2026</strong> (after Austria)</td><td>Test &amp; reserve driver</td></tr>
          <tr><td>Cadillac</td><td>Colton Herta</td><td>Valtteri Bottas</td><td><strong>2nd</strong> (1 prior: Barcelona)</td><td>Into the MAC-26</td></tr>
        </tbody>
      </table>
    </div>
    <p class="src" style="margin-top:-.4rem">FP1 outing counts include this Hungarian GP run. Source: Formula1.com.</p>

    <h2 class="sec">Pocket bios</h2>
    <div class="grid cols-2">
      {card("Leonardo Fornaroli — McLaren", ul([
         "Italian, 21. 2025 <strong>F2 champion</strong>; McLaren Driver Development Programme &amp; reserve.",
         "<strong>2nd career FP1 outing</strong> — debut at Barcelona last month (in Norris' car); now takes over Piastri's.",
         "Also has laps in older McLaren and Haas machinery.",
      ]), "bi-person-badge", "accent")}

      {card("Frederik Vesti — Mercedes", ul([
         "Danish. Mercedes' sole reserve for 2026 after 5+ years in the programme.",
         "<strong>6th F1 practice outing</strong> (five prior since 2023); now racing IMSA sportscars.",
         "Faces the pressure of a <strong>title contender's car</strong> (as in Barcelona).",
      ]), "bi-person-badge")}

      {card("Paul Aron — Alpine", ul([
         "Estonian, 22. Third in the 2024 F2 championship.",
         "<strong>8th FP1 outing</strong> — debut with Sauber at the 2025 British GP, then Hungary, Monza, Mexico City &amp; Abu Dhabi, plus Audi runs at Barcelona &amp; Austria this year.",
         "First appearance <em>for Alpine</em> in 2026; supports Gasly and Colapinto — the latter steps aside in FP1.",
      ]), "bi-person-badge")}

      {card("Ryo Hirakawa — Haas", ul([
         "Japanese, 32. Haas test &amp; reserve driver.",
         "<strong>2nd FP1 of 2026</strong> (after Austria), taking Bearman's car.",
         "Currently races WEC with Toyota.",
      ]), "bi-person-badge")}

      {card("Colton Herta — Cadillac", ul([
         "American, 26. Cadillac test driver.",
         "<strong>2nd career FP1 outing</strong> — debut at Barcelona (in Perez' car); now into Bottas' MAC-26.",
         "Extensive IndyCar experience; moved to <strong>F2 for 2026</strong> (16th, 26 pts). Two more practice runs due this year after Hungary.",
      ]), "bi-person-badge")}

      {card("Also worth a mention", ul([
         "<strong>Jak Crawford</strong> (Aston Martin reserve, F2 runner-up 2025) has been central to the AMR26 upgrade sim work.",
         "<strong>Arvid Lindblad</strong> (Racing Bulls) — full rookie racing this year, already trading blows with Lawson.",
      ]), "bi-people")}
    </div>
    <p class="src">Source: Formula1.com &amp; The Race.</p>
    """)

    # ---- 5. STANDINGS --------------------------------------------------------
    PAGES["standings"] = dict(
        kicker="Championship",
        title="Championship & Form",
        sub="Where the title race stands after Spa — and the form lines to weave into FP1 commentary.",
        body=f"""
    <div class="grid cols-2">
      {card("Drivers' title — top of the table", f'''
      <div class="table-wrap"><table class="data">
        <thead><tr><th>Pos</th><th>Driver</th><th>Note</th></tr></thead>
        <tbody>
          <tr><td class="pos">1</td><td>Kimi Antonelli (Mercedes)</td><td>Leader · 6 wins · won at Spa</td></tr>
          <tr><td class="pos">2</td><td>Lewis Hamilton (Ferrari)</td><td><strong>45 pts</strong> behind Antonelli</td></tr>
          <tr><td class="pos">3</td><td>George Russell (Mercedes)</td><td>Just <strong>5 pts</strong> behind Hamilton</td></tr>
        </tbody>
      </table></div>
      <p class="src">Gaps per Formula1.com after the Belgian GP. Hamilton overtook Russell for 2nd at Spa.</p>
      ''', "bi-trophy", "accent")}

      {card("Constructors' — midfield fight", f'''
      <p>The eye-catcher: <strong>Racing Bulls have levelled with Alpine on points</strong> in the battle for
      6th heading into the summer break. Momentum could swing either way in Budapest.</p>
      <p>At the front, McLaren keep pushing (upgrades incoming), while Red Bull boss Laurent Mekies says the
      car is getting "stronger and stronger" after Verstappen's P3 at Spa.</p>
      ''', "bi-diagram-3", "accent")}
    </div>

    <h2 class="sec">How Spa reshaped things</h2>
    <div class="grid cols-2">
      {card("Mercedes", ul([
         "Antonelli converted pole into victory — his title lead out to 45 pts.",
         "Russell out on Lap 1 after contact with Hamilton; Mercedes traced it to a deployment/software issue (now fixed).",
         "Wolff admitted a power-unit problem contributed to Russell's opening-lap struggles.",
      ]), "bi-star")}

      {card("Ferrari", ul([
         "Leclerc P2 at Spa — in contention for the win.",
         "Hamilton relieved to score after a tricky weekend and an FP3 crash.",
         "Hamilton now 2nd in the championship, ahead of Russell.",
      ]), "bi-star")}

      {card("Red Bull", ul([
         "Verstappen P3 podium at Spa; Mekies upbeat on car direction.",
         "'Keep the momentum going' is the Red Bull line into Hungary.",
      ]), "bi-star")}

      {card("Midfield &amp; back", ul([
         "Racing Bulls level with Alpine for 6th.",
         "Cadillac has pulled clear of Aston Martin (2s+ at Spa) — but is 'a bit scared' of the AMR26 upgrade.",
         "Aston Martin's updates could reshuffle the lower midfield.",
      ]), "bi-star")}
    </div>
    <p class="src">Source: Formula1.com 'Need to Know' &amp; The Race.</p>
    """)


    # ---- 6. TEAM WATCH -------------------------------------------------------
    PAGES["teams"] = dict(
        kicker="Team News",
        title="Team Watch & News",
        sub="The paddock storylines from Hungaroring media day — the human angles to weave in between the on-track action.",
        body=f"""
    <div class="grid cols-2">
      {card("Cadillac 'a bit scared' of Aston", ul([
         "Cadillac pulled 2s+ clear of Aston Martin at Spa — but Bottas is 'a little bit scared' the AMR26 upgrade drops them to the back.",
         "Their own 2026 development brings 'no magic, nothing huge'.",
         "Perez thinks they 'haven't developed enough'; Bottas rates the rate 'good' for a new team.",
      ]), "bi-emoji-neutral")}

      {card("Racing Bulls: closer than it looks", ul([
         "Lindblad beat Lawson at Spa after a tense run through Eau Rouge and into Les Combes.",
         "Despite team-order friction, the pair get on well — 'we race hard but fair'.",
         "A two-hour-delayed easyJet to Budapest even helped bonding (Lawson got the window seat).",
      ]), "bi-people")}

      {card("Haas: not a 'fair fight'", ul([
         "Bearman leads Ocon 11–3 in qualifying and 18–3 on points — but blames parts inconsistency for a 'moving target'.",
         "Ocon says he's had 'normal car performance' at only two of 10 rounds.",
         "Haas has swapped Ocon onto a different floor, rear wing and engine for Hungary.",
      ]), "bi-shuffle")}

      {card("Antonelli's track-limits homework", ul([
         "Even after winning at Spa, his father Marco told him off for taking too many liberties.",
         "Two Raidillon track-limits offences at Spa — the only driver with more than one in the race.",
         "'If I use them when I don't need to, I might find myself in trouble.'",
      ]), "bi-cone")}

      {card("Leclerc agrees with Piastri", ul([
         "On the un-penalised Spa contact: 'I kind of agree with Oscar... it was maybe a bit too sketchy.'",
         "A rare bit of self-critique on where the racing line sits.",
      ]), "bi-chat-quote")}

      {card("Albon hunting a race engineer", ul([
         "James Urwin moves to a factory role for 2026.",
         "Albon's target Tom Hart stayed at Red Bull — expected to take over as Verstappen's race engineer from Lambiase.",
         "Williams say they have 'ideas in place'.",
      ]), "bi-headset")}
    </div>

    {card("A different kind of Mercedes upgrade — the safety car", f'''
    <p>A new all-wheel-drive <strong>Mercedes-AMG GT</strong> safety car debuts in Hungary — the 14th variant
    since 1996 — wearing a red 30th-anniversary livery. 612 hp, 317 km/h top speed, nine-speed gearbox.</p>
    {quote("It really comes into its own when cornering and accelerating.", "Bernd Maylander, safety car driver")}
    ''', "bi-car-front", "accent")}
    <p class="src">Source: The Race — 'Everything we learned on day one at F1's 2026 Hungarian GP'.</p>
    """)

    # ---- 6b. UPGRADES --------------------------------------------------------
    PAGES["upgrades"] = dict(
        kicker="Car Development",
        title="Car Development & Upgrades",
        sub="Hungary is a big upgrade weekend — headlined by Aston Martin's B-spec overhaul, plus a rear-wing arms race up and down the grid.",
        body=f"""
    <div class="storyline">
      <div class="storyline-tag"><i class="bi bi-bookmark-star-fill"></i> Storyline to follow</div>
      <h2 class="storyline-title">Aston Martin B-spec — the overhaul begins</h2>
      <p class="storyline-lead">Aston Martin's much-anticipated <strong>B-spec car</strong> starts rolling out at the
      Hungaroring — the first of a <strong>two-step upgrade split across Hungary and Zandvoort</strong>, with the
      Dutch GP step arriving alongside Honda's sole 2026 engine upgrade. This is the team's first real attempt to
      move on from what they've called "the tough times".</p>

      <div class="grid cols-2">
        {card("What's actually changed on the car", ul([
           "<strong>New-look sidepod, floor and rear wing</strong> were on the cars in the garage by Friday morning (barely visible on Thursday).",
           "A bigger <strong>'mouse hole' on the floor</strong> and a <strong>different rear-wing actuator</strong> spotted trackside.",
           "Clear modifications to the <strong>bargeboard area and sidepod profile</strong>.",
           "Chassis &amp; gearbox architecture unchanged, but <strong>weight taken out of both</strong> — forced a re-homologation and crash-test of the forward chassis.",
           "Front suspension unchanged; rear suspension slightly revised.",
           "<strong>New nose and substantially revised aero surfaces</strong> — \"a big aerodynamic package coupled with significant weight reduction,\" targeting the weight limit.",
        ]), "bi-tools", "accent")}

        {card("The two-step plan & what to watch", ul([
           "<strong>Step 1 — Hungary:</strong> new bodywork/floor/wing debut; back-to-back data vs the old spec.",
           "<strong>Step 2 — Zandvoort:</strong> the bigger step, landing with <strong>Honda's 2026 engine upgrade</strong> (see Power Unit page).",
           "A move \"in a different direction\" from extreme choices such as the car's <strong>aggressive rear ride height</strong>.",
           "Krack framed parts supply as a <strong>\"$1 million question\"</strong> — whether they'd have enough to run the package on both cars — but was \"quite confident we will be ready\".",
           "A big test of the team's <strong>data and simulation tools</strong>: no winter testing, so they won't extract everything on run one.",
        ]), "bi-diagram-3")}
      </div>

      {quote("When you bring substantial upgrades, it's something the track team will have to learn as quick as possible... We do not expect that we get everything out of it in the first run tomorrow. We need to learn how to manage this.", "Mike Krack, Chief Trackside Officer (The Race, Fri 24 Jul)")}
      {quote("We didn't start serious work on the '26 car until mid-March 2025... that left us several months behind our rivals — a huge gap to close.", "Adrian Newey")}

      <div class="callout watch">
        <strong>FP1/FP2 watch:</strong> first back-to-back numbers on the upgraded AMR26 vs its old spec — watch the
        early aero-rake and flow-viz runs, and whether both cars actually run the full package. Basic set-up work
        (ride height, rakes) will roll on over the next events, so don't expect a step-change immediately.
      </div>

      <div class="fia-upgrade-box">
        <div class="fia-upgrade-head"><i class="bi bi-file-earmark-text"></i> FIA official upgrade list</div>
        <p>When the FIA publishes its official <strong>car-presentation / technical upgrade list</strong> for this
        event, the confirmed Aston Martin parts and their stated purpose (performance vs. circuit-specific) will be
        added here alongside the trackside observations above. Re-run the build once the document is live.</p>
      </div>
      <p class="src">Sources: The Race — "First clues of Aston Martin's B-spec F1 car at Hungarian GP emerge" (Josh Suttill, 24 Jul 2026) &amp; Formula1.com. FIA upgrade-list details added when published.</p>
    </div>

    <h2 class="sec">The rear-wing arms race</h2>
    <div class="grid cols-2">
      {card("Ferrari — 'Macarena' wing", ul([
         "New winglet cascades in the legality box where the rear-wing actuator normally sits.",
         "Borrows from McLaren's Monaco solution — a triple-element series in the central area.",
         "Extra hangars above the upper element too — all aimed at <strong>more downforce</strong> for the Hungaroring.",
      ]), "bi-airplane", "green")}

      {card("McLaren — flip-over wing (finally)", ul([
         "Revised low-drag 'flip-over' wing fitted to <strong>Piastri's car</strong> for opening practice.",
         "Was pulled at the Austrian GP before the car left the garage; reworked at Woking.",
         "<strong>Test only in Hungary</strong> — reverts to the regular wing for qualifying; could debut properly at Monza.",
      ]), "bi-airplane", "green")}

      {card("Mercedes — new rear wing", ul([
         "New rear-wing spec with extra winglets on top of the upper flap.",
         "Paired with a deployment software fix after Russell's Spa woes (see Power Unit page).",
      ]), "bi-airplane", "green")}

      {card("Cadillac — brakes upgrade", ul([
         "Bolstered <strong>brakes package</strong> — Bottas said without it they'd 'most likely' not have finished at Spa.",
         "Hungaroring is brutally tough on brakes (Cadillac had both cars out by lap 4 at the Red Bull Ring).",
      ]), "bi-disc")}

      {card("Haas — parts refresh for Ocon", ul([
         "Different floor, different rear wing and different engine fitted to Ocon's car.",
         "Aimed at ending the parts-inconsistency that made the intra-team fight uneven.",
      ]), "bi-wrench-adjustable")}
    </div>
    <p class="src">Sources: Formula1.com &amp; The Race (Ferrari Macarena wing, day-one roundup). Upgrade details will be updated as FIA technical/upgrade documents are published.</p>
    """)

    # ---- 6c. POWER UNIT ------------------------------------------------------
    PAGES["powerunit"] = dict(
        kicker="2026 Rules",
        title="Power Unit & Override",
        sub="How the 2026 power units and the Manual Override deploy at the Hungaroring — including the higher practice &amp; qualifying power limits — straight from the FIA's power-unit document.",
        body=f"""
    <div class="callout">
      In 2026 the electrical side is far bigger and DRS is replaced by a battery-boost <strong>Manual Override</strong>.
      The FIA publishes a per-event power/energy map — here are the Hungary numbers for commentary.
    </div>

    <div class="stat-row">
      {stat("9.0 MJ", "FP &amp; Quali recharge", "full curve, whole lap")}
      {stat("8.5 → 9.0 MJ", "Race override energy", "not active → active")}
      {stat("350 kW", "Max PU power cut", "in defined sectors")}
      {stat("1885 m", "Override distance", "per deployment")}
      {stat("100 kW/s", "Ramp-down rate", "power-limited")}
    </div>

    <div class="grid cols-2">
      {card("Manual Override (the 'DRS replacement')", ul([
         "Extra deployment energy rises from <strong>8.5 MJ</strong> (override not active) to <strong>9.0 MJ</strong> when active.",
         "Override detection sits on <strong>Safety Car Line 1</strong> (~3974 m); activation ~4121 m.",
         "Higher-speed threshold sector T2–exit T3 (1150–1400 m): 240 km/h, 1.0 s detection gap.",
         "Main overtaking zone is the start/finish straight into Turn 1.",
      ]), "bi-lightning-charge", "accent")}

      {card("Energy management around the lap", ul([
         "<strong>Max recharge per lap</strong> and max PU power-reduction rate are capped by the FIA.",
         "Alternative (lower) power curve applies in defined sectors in Sprint &amp; Race.",
         "Power-limited ramp-down: <strong>100 kW/s</strong> — the mechanism behind Russell's Spa speed traps.",
         "Hungary is a more energy-rich layout than Spa, so deployment should be less of a limitation.",
      ]), "bi-battery-charging", "accent")}
    </div>

    {card("⚡ Practice &amp; Qualifying — higher power limits than the race", f'''
    <p>This is the big one for reading FP1/qualifying pace: <strong>in every practice session and in
    qualifying the cars run the more powerful "Base&nbsp;–&nbsp;Overtake" ERS-K deployment curve across the
    whole lap</strong>, and get the <strong>full 9.0&nbsp;MJ recharge per lap</strong>. In the Sprint &amp;
    Race they're held to the weaker "Base&nbsp;–&nbsp;Standard" / "Alt&nbsp;1" curves — and to just
    <strong>8.5&nbsp;MJ</strong> unless the driver has Manual Override active.</p>
    <p>Practical effect: <strong>qualifying and practice laptimes flatter the cars</strong> — expect a
    noticeable drop in straight-line punch on Sunday, especially outside the overtaking zones. Two extra
    power-reduction/reset windows on the exit of Turn&nbsp;14 also open up <em>only</em> in Qualifying and
    Sprint Qualifying.</p>
    ''', "bi-stopwatch", "watch")}

    <div class="table-wrap">
      <table class="data">
        <caption class="tbl-cap">Maximum recharge per lap &amp; ERS-K deployment curve by session (FIA Arts. C5.2.10 &amp; C5.2.8)</caption>
        <thead><tr><th>Session</th><th>Max recharge / lap</th><th>ERS-K power curve</th></tr></thead>
        <tbody>
          <tr class="hi"><td><strong>Free Practice (all)</strong></td><td>9.0 MJ</td><td>Base – Overtake (full curve, whole lap)</td></tr>
          <tr class="hi"><td><strong>Qualifying / Sprint Qualifying</strong></td><td>9.0 MJ</td><td>Base – Overtake (full curve, whole lap)</td></tr>
          <tr><td>Race / Sprint — override <em>not</em> active</td><td>8.5 MJ</td><td>Base – Standard (zones) · Alt 1 (rest of lap)</td></tr>
          <tr><td>Race / Sprint — override active</td><td>9.0 MJ</td><td>Base – Overtake (in main overtaking zones)</td></tr>
          <tr><td>Out laps (other than in the race)</td><td>9.0 MJ</td><td>—</td></tr>
        </tbody>
      </table>
    </div>
    <p class="src">In practice &amp; qualifying the strongest deployment map is available everywhere; the race is deliberately throttled to make energy management part of the show.</p>

    <div class="table-wrap">
      <table class="data">
        <thead><tr><th>Sector window (m)</th><th>Turns</th><th>Max PU power reduction</th></tr></thead>
        <tbody>
          <tr><td>1780–2700</td><td>T4–T9</td><td>350 kW</td></tr>
          <tr><td>3500–4000</td><td>T12–T14</td><td>350 kW</td></tr>
          <tr><td>4000–4200 (Q/SQ only)</td><td>Exit T14</td><td>350 kW</td></tr>
        </tbody>
      </table>
    </div>
    <p class="src">Source: FIA 'Power Unit Information to the Teams and PUMs' (2026 Hungarian GP, Doc 3).</p>

    {card("Mercedes' Spa power-unit gremlin — now fixed", f'''
    <p>Russell's Spa weekend was wrecked by a lack of straight-line speed vs Antonelli. The cause was buried
    deep in the PU code: his deployment was <strong>front-loaded</strong> around the lap, so he ran out of
    battery on the run to the final chicane.</p>
    <p>On Lap 1, a separate <strong>software error</strong> meant both cars under-harvested into La Source and
    had less energy down the Kemmel Straight — leaving Russell stuck at ~308 km/h and swallowed by the pack
    (feeding his clash with Hamilton). Mercedes has countermeasures in place for Hungary.</p>
    {quote("It's a huge load off my mind... now I can just focus on driving fast, on the simple things.", "George Russell (via The Race)")}
    ''', "bi-cpu", "accent")}

    {card("Honda & the manufacturer picture", ul([
       "Aston Martin's <strong>Honda</strong> engine upgrade is due at the <strong>Dutch GP</strong>, not Hungary.",
       "Honda &amp; Aston say the relationship strengthened through winter-testing struggles.",
       "The 2026 formula's heavy reliance on energy-management algorithms remains a hot driver-debate topic (Perez critical, Bortoleto in favour).",
    ]), "bi-gear-wide-connected")}
    <p class="src">Sources: The Race (Mercedes software fix, day-one roundup) &amp; Formula1.com (Aston Martin/Honda).</p>
    """)

    # ---- 7. FACTS ------------------------------------------------------------
    PAGES["facts"] = dict(
        kicker="Stats &amp; Records",
        title="Facts, Stats &amp; Records",
        sub="The number-drops and record lines to sprinkle through the broadcast.",
        body=f"""
    <div class="stat-row">
      {stat("1:16.627", "Lap record", "Hamilton, Mercedes, 2020")}
      {stat("9", "Most poles", "Lewis Hamilton")}
      {stat("8", "Most wins", "Lewis Hamilton")}
      {stat("13%", "Safety Car prob.", "last 8 races")}
      {stat("25%", "Virtual SC prob.", "last 8 races")}
    </div>

    <div class="grid cols-2">
      {card("Recent Hungarian GP winners", f'''
      <div class="table-wrap"><table class="data">
        <thead><tr><th>Year</th><th>Winner</th></tr></thead>
        <tbody>
          <tr><td>2025</td><td>Lando Norris (McLaren)</td></tr>
          <tr><td>2024</td><td>Oscar Piastri (McLaren)</td></tr>
          <tr><td>2023</td><td>Max Verstappen (Red Bull)</td></tr>
          <tr><td>2022</td><td>Max Verstappen (Red Bull)</td></tr>
          <tr><td>2021</td><td>Esteban Ocon (Alpine)</td></tr>
        </tbody>
      </table></div>
      ''', "bi-flag", "accent")}

      {card("Recent polesitters", f'''
      <div class="table-wrap"><table class="data">
        <thead><tr><th>Year</th><th>Pole</th></tr></thead>
        <tbody>
          <tr><td>2025</td><td>Charles Leclerc (Ferrari)</td></tr>
          <tr><td>2024</td><td>Lando Norris (McLaren)</td></tr>
          <tr><td>2023</td><td>Lewis Hamilton (Mercedes)</td></tr>
          <tr><td>2022</td><td>George Russell (Mercedes)</td></tr>
          <tr><td>2021</td><td>Lewis Hamilton (Mercedes)</td></tr>
        </tbody>
      </table></div>
      ''', "bi-stopwatch", "accent")}
    </div>

    <div class="grid cols-2">
      {card("Trivia to drop", ul([
         "The Hungaroring has hosted many <strong>maiden wins</strong>: Piastri (2024), Ocon (2021), Button (2006), Alonso (2003).",
         "2026 marks <strong>40 years</strong> of the Hungarian GP — F1's first venture behind the Iron Curtain (1986).",
         "Norris won from P3 on the grid in 2025.",
         "69 overtakes were completed in the 2025 race.",
      ]), "bi-lightbulb")}

      {card("Key numbers", ul([
         "Pole to Turn 1 braking point: <strong>476 m</strong>.",
         "Pit-stop time loss: <strong>~20.56 s</strong>.",
         "Race distance: 70 laps of 4.381 km.",
         "Set-ups mirror Monaco — max downforce.",
      ]), "bi-123")}
    </div>
    <p class="src">Source: Formula1.com 'Need to Know' (*probabilities from the last eight races in Hungary).</p>
    """)


    # ---- 8. MOMENTS ----------------------------------------------------------
    def _tl(year, title, text):
        return f'<div class="tl-item"><div class="tl-year">{year}</div><div class="tl-title">{title}</div><p>{text}</p></div>'

    _moments = [
        ("1989", "Mansell's Ferrari flourish",
         "Qualified a subdued 12th, then charged through. When Senna hesitated lapping Johansson at Turn 3, Mansell ducked inside to pass both in one swoop and won — at the venue where he'd clinch the 1992 title."),
        ("1997", "Hill's Arrows heartbreak",
         "Damon Hill dragged the Bridgestone-shod Arrows to a shock lead and a 34-second cushion, only for hydraulics to fail with three laps to go. Villeneuve passed on the final lap; Hill settled for second. Arrows never won a race."),
        ("1998", "Schumacher's three-stop masterstroke",
         "McLaren locked out the front row, but Ross Brawn switched Schumacher to a three-stopper. Blistering pace in the refuelling era saw him emerge from his final stop in the lead — reigniting his title bid."),
        ("2003", "Alonso's breakthrough win",
         "Pole by a quarter-second, then eased away — even lapping team-mate Trulli and champion Schumacher. At 22 he became F1's then-youngest winner and the first Spaniard to win a Grand Prix."),
        ("2006", "Button wins at last",
         "A blown engine in practice meant a 10-place penalty and P14 start. But wet weather struck Hungary for the first time; Button charged, inherited the lead when Alonso lost a wheel nut, and won by half a minute — his and Honda's first."),
        ("2007", "Drama in the pit lane",
         "The McLaren civil war: Hamilton disobeyed team orders on track, Alonso retaliated by holding him up in the pit box in Q3. Alonso took pole but got a five-place penalty; Hamilton won the race."),
        ("2014", "Ricciardo's charge",
         "A chaotic wet/dry race with Rosberg and Hamilton at opposite ends of the grid. Fresh-tyred Ricciardo passed Hamilton at Turn 2 then dived past Alonso into Turn 1 with two laps left for a famous win."),
        ("2019", "Hamilton overhauls Verstappen",
         "Verstappen took a maiden pole and led, but Mercedes gambled on a second stop. Hamilton wiped out a 15-second deficit and made the winning move with four laps to go — Verstappen the only car within a minute."),
        ("2021", "Chaos in the wet",
         "A wet Turn 1 pile-up (Bottas the culprit) collected several front-runners. Only Hamilton lined up on a drying grid after everyone else pitted; from the reshuffle, Ocon held on for a maiden win, aided by Alonso's defence on Hamilton."),
        ("2024", "A complex first for Oscar",
         "Norris qualified on top but Piastri led early. A strategy sequence put Norris ahead; McLaren told him to give the place back. He eventually did with three laps left, and Piastri took his first Grand Prix win."),
    ]

    PAGES["moments"] = dict(
        kicker="40 Years",
        title="Top 10 Magyar Moments",
        sub="Four decades of Hungarian GP drama — first-time winners, wet-weather chaos and intra-team feuds. Perfect filler for a slow FP1 hour.",
        body=f"""
    <div class="callout">
      2026 marks <strong>40 years</strong> since F1 first ventured behind the Iron Curtain to the new
      Hungaroring in 1986. Here are ten moments that defined it — ready to drop when the action goes quiet.
    </div>
    <div class="timeline">
      {''.join(_tl(y,t,x) for y,t,x in _moments)}
    </div>
    <p class="src">Source: Formula1.com — 'Top 10 magic Magyar moments'.</p>
    """)

    # ---- 9. SCHEDULE ---------------------------------------------------------
    PAGES["schedule"] = dict(
        kicker="Timing",
        title="Schedule &amp; Weather",
        sub="Session times in Budapest local and Tallinn (Eastern European) time, plus a live circuit forecast pulled at build time.",
        body=f"""
    <h2 class="sec">Full weekend schedule</h2>
    <div class="table-wrap">
      <table class="data">
        <thead><tr><th>Session</th><th>Day</th><th>{TZ_LOCAL_LABEL}</th><th>{TZ_EAST_LABEL}</th></tr></thead>
        <tbody>
          {schedule_rows()}
        </tbody>
      </table>
    </div>
    <p class="src">Times shown in Budapest local (CEST, UTC+2) and Tallinn / Eastern European time (EEST, UTC+3 = local + 1 hour).</p>

    <h2 class="sec">Circuit forecast</h2>
    {weather_cards()}
    <p class="src">{'Live forecast for the Hungaroring (47.58°N, 19.25°E) via Open-Meteo, fetched at build time. Times aligned to Tallinn / EEST.' if WEATHER_OK else 'Rebuild with an internet connection to embed the live forecast.'}</p>

    <h2 class="sec">Conditions to expect</h2>
    <div class="grid cols-2">
      {card("Typical Hungaroring weather", ul([
         "Track temperatures are usually the <strong>highest of the season</strong> — peak European summer.",
         "Heat drives <strong>thermal tyre degradation</strong>, especially on the rear axle.",
         "History warns of the wildcard: Hungary's most dramatic races (2006, 2014, 2021) came when <strong>rain</strong> arrived.",
      ]), "bi-thermometer-sun", "accent")}

      {card("Why it matters for FP1", ul([
         "Hot, low-grip surface means big lap-time evolution through the hour.",
         "Teams will chase cooling and tyre-thermal balance early.",
         "Watch cloud cover / wind — any threat of rain changes long-run plans instantly.",
      ]), "bi-cloud-sun", "accent")}
    </div>
    <div class="callout watch">
      <strong>Reminder:</strong> Always sanity-check against the live on-air forecast — the cards above are a
      snapshot from build time, and Budapest summer weather can shift quickly.
    </div>
    """)


    # ---- 10. NOTES (cheat sheet) --------------------------------------------
    PAGES["notes"] = dict(
        kicker="Cheat Sheet",
        title="Commentator's Cheat Sheet",
        sub="Grab-and-go talking points for the FP1 hour — storylines, quick stats, names and pronunciations.",
        body=f"""
    {card("Open the session with these", ul([
       "Last race before the summer break — teams still have plenty to confirm, so expect busy run plans.",
       "Antonelli leads by 45 pts and won last time at Spa — the man to frame the title picture around.",
       "Five rookies out in FP1 — <strong>don't read too much into times</strong>; different drivers, heavy programmes.",
       "Aston Martin's big upgrade debuts — first laps of the reworked, lighter AMR26.",
    ]), "bi-play-circle", "accent")}

    <div class="grid cols-2">
      {card("Rookie roll-call (who's in which car)", ul([
         "Fornaroli → <strong>Piastri's McLaren</strong>",
         "Vesti → <strong>Antonelli's Mercedes</strong>",
         "Aron → <strong>Colapinto's Alpine</strong>",
         "Hirakawa → <strong>Bearman's Haas</strong>",
         "Herta → <strong>Bottas' Cadillac</strong>",
      ]), "bi-person-badge")}

      {card("Upgrade spotting", ul([
         "Aston Martin: new nose + aero + big weight save.",
         "Ferrari: 'Macarena' rear wing (McLaren-style cascades).",
         "McLaren: flip-over wing on Piastri — <em>test only</em>.",
         "Mercedes: new rear wing + deployment software fix.",
         "Cadillac: bigger brakes package.",
         "Haas: Ocon on a new floor, rear wing &amp; engine.",
      ]), "bi-tools")}
    </div>

    <div class="grid cols-2">
      {card("Quick-fire stats", ul([
         "Lap record 1:16.627 (Hamilton, 2020).",
         "Hamilton: 8 wins &amp; 9 poles here — the Hungaroring king.",
         "One real straight; overtaking almost only at Turn 1 (Turn 2 backup).",
         "Pit loss ~20.56s · SC 13% · VSC 25%.",
         "Override energy 8.5→9.0 MJ; main zone into Turn 1.",
         "40th anniversary of the race.",
      ]), "bi-lightning")}

      {card("Names &amp; pronunciation", ul([
         "Antonelli — <em>an-toh-NELL-ee</em> (Kimi)",
         "Fornaroli — <em>for-nah-ROH-lee</em>",
         "Vesti — <em>VESS-tee</em> (Frederik)",
         "Hirakawa — <em>hee-rah-KAH-wah</em> (Ryo)",
         "Hungaroring — <em>HUNG-guh-roh-ring</em>",
         "Räikkönen, Raidillon — for the history/Spa call-backs",
      ]), "bi-mic")}
    </div>

    {card("If the track goes quiet…", ul([
       "Roll a Magyar moment (see Top 10) — 40 years of drama, from Mansell '89 to Piastri '24.",
       "Maiden-win trivia: Piastri, Ocon, Button, Alonso all broke through here.",
       "Midfield subplot: Racing Bulls level with Alpine for 6th; Cadillac 'scared' of Aston's step.",
       "Russell's Spa radio rant &amp; the deployment saga — now (he hopes) behind him.",
    ]), "bi-hourglass-split", "accent")}

    {card("Official FIA documents published (2026 Hungarian GP)", ul([
       "Power Unit Information (override energy &amp; power maps) — see Power Unit page.",
       "Race Director's Competition Notes (track limits, lapping, practice starts) — see Circuit page.",
       "Competition Notes: Pirelli Preview (tyre pressures, Q3/mandatory compounds).",
       "Circuit Map, Pit-Lane Drawing, Emergency Exits &amp; Red Zone.",
       "Car Display Procedure · Competition Visa.",
    ]), "bi-file-earmark-text")}

    <div class="callout watch">
      <strong>Golden rule for FP1:</strong> low grip + high temps + rookies = messy, unrepresentative
      timesheets. Focus the story on run plans, upgrade first impressions and long-run tyre behaviour, not headline laptimes.
    </div>
    """)

    return PAGES
