"""Italian Grand Prix 2026 bespoke page content.

Race-week facts are drawn from Formula1.com, The Race and the FIA event hub.
Unpublished FIA values remain explicit pending states in the generic baseline.
"""
from f1lib import card, news_item, render_news, stat, ul
from content_generic import build_pages as build_generic, pending, ul_or, _fmt


FIA_EVENT_URL = ("https://www.fia.com/documents/championships/"
                 "fia-formula-one-world-championship-14/season/season-2026-2072/"
                 "event/Italian%20Grand%20Prix")


def _source(name, url):
    return f'<a href="{url}" target="_blank" rel="noopener">{name}</a>'


def build_pages(ctx, env):
    pages = build_generic(ctx, env)
    schedule_rows = env["schedule_rows"]
    weather_cards = env["weather_cards"]
    ref = ctx.get("ref") or {}
    st = ctx.get("standings") or {}

    pages["overview"] = dict(
        kicker="Round 13 · Race week",
        title="Weekend Overview",
        sub=("The Temple of Speed hosts Ferrari's home race, championship leader Kimi Antonelli's "
             "homecoming and the final European double-header opener."),
        body=f"""
<div class="stat-row">
  {stat("5.793 km", "Lap length")}
  {stat("53", "Race laps", "306.72 km")}
  {stat("1950", "First World Championship GP")}
  {stat("Standard", "Format", "3 practice sessions")}
</div>

<div class="callout">
  <strong>The one-line setup:</strong> Antonelli arrives 59 points clear but is set to start from the
  back after Mercedes' planned power-unit change; Ferrari bring a home-race low-drag programme and
  Schumacher tribute; and two-time consecutive winner Lando Norris leads McLaren's challenge.
</div>

<h2 class="sec">Storylines to have loaded for FP1</h2>
<div class="grid cols-2">
  {card("Antonelli: home hero, title leader, recovery drive", ul([
     "The Mercedes driver leads George Russell and Lewis Hamilton by <strong>59 points</strong> after finishing second at Zandvoort.",
     "Mercedes plan a full power-unit change, sending him to the back of the grid at a circuit selected for its overtaking potential.",
     "No Italian has won the Italian Grand Prix since Ludovico Scarfiotti in 1966.",
  ]), "bi-trophy", "accent")}
  {card("Ferrari and the tifosi", ul([
     "Ferrari's special livery and race suits mark 30 years since Michael Schumacher joined the team.",
     "The SF-26 gets Monza-specific low-drag changes across the floor, bodywork and rear wing.",
     "Charles Leclerc won here in 2024; Ferrari need a home response after McLaren's back-to-back wins.",
  ]), "bi-flag", "accent")}
  {card("Four rookies in FP1", ul([
     "Luke Browning for Alex Albon at Williams.",
     "Paul Aron for Pierre Gasly at Alpine.",
     "Colton Herta for Sergio Perez at Cadillac.",
     "Ayumu Iwasa for Max Verstappen at Red Bull.",
  ]), "bi-person-badge")}
  {card("Energy, not just minimum wing", ul([
     "Pirelli says simulations put 2026 lap times around <strong>two seconds faster</strong> than 2025.",
     "Long straights make recharge and deployment a central performance constraint under the new power-unit rules.",
     "McLaren expect a possible 'yo-yo effect' as cars harvest and deploy at different places around the lap.",
  ]), "bi-battery-charging")}
</div>

<h2 class="sec">Session times</h2>
<div class="table-wrap"><table class="data">
  <thead><tr><th>Session</th><th>Day</th><th>{ctx["tz_local"]}</th><th>{ctx["tz_east"]}</th></tr></thead>
  <tbody>{schedule_rows()}</tbody>
</table></div>
""")

    curated_news = [
        news_item(
            "Toto Wolff explains decision behind Monza engine penalty for Kimi Antonelli",
            "Mercedes selected Monza for a planned full power-unit change. The championship leader "
            "arrives 59 points clear after finishing second at Zandvoort.",
            _source("Formula1.com", "https://www.formula1.com/en/latest/article/"
                    "wolff-explains-decision-behind-monza-engine-penalty-for-antonelli."
                    "2kQ3tVnHJXRsloH0lmlh9I"),
            "26 Aug", "f1"),
        news_item(
            "Liam Lawson to replace Isack Hadjar again at Red Bull as Yuki Tsunoda continues to substitute for Racing Bulls in Monza",
            "Hadjar remains out while recovering from a wrist injury. Lawson gets a second RB22 "
            "weekend after scoring seventh at Zandvoort, with Tsunoda again taking the Racing Bulls seat.",
            _source("Formula1.com", "https://www.formula1.com/en/latest/article/"
                    "lawson-to-replace-hadjar-again-at-red-bull-as-tsunoda-continues-to-substitute-"
                    "for-racing-bulls-in-monza.4pI3a9wGM9uTDfK9DqRUMU"),
            "2 Sep", "f1"),
        news_item(
            "Ferrari reveal Michael Schumacher-inspired livery for home Grand Prix at Monza",
            "The one-off treatment marks 30 years since Schumacher joined Ferrari and 20 years "
            "since his final win for the team. Leclerc and Hamilton also wear tribute race suits.",
            _source("Formula1.com", "https://www.formula1.com/en/latest/article/"
                    "gallery-ferrari-reveal-schumacher-inspired-livery-for-home-grand-prix-at-monza."
                    "5burkVG8etBZzPdZrIN7bX"),
            "1 Sep", "f1"),
        news_item(
            "What tyres will the teams and drivers have for the 2026 Italian Grand Prix?",
            "Pirelli selected C3, C4 and C5. Its simulations predict laps around two seconds quicker "
            "than last year, with braking stability and traction at Rettifilo and Ascari decisive.",
            _source("Formula1.com", "https://www.formula1.com/en/latest/article/"
                    "what-tyres-will-the-teams-and-drivers-have-for-the-2026-italian-grand-prix."
                    "7nOpWdCgvCBFDGlnODs0gk"),
            "2 Sep", "f1"),
    ]
    pages["news"] = dict(
        kicker="Weekend News",
        title="Weekend News & Session Reports",
        sub="The key Monza stories first, followed by the full automatically refreshed wire feed.",
        body=render_news(ctx, curated_news, {}))

    pages["tyres"] = dict(
        kicker="Pirelli · confirmed",
        title="Tyres & Strategy",
        sub="The official C3/C4/C5 allocation and Pirelli's Monza-specific 2026 forecast.",
        body=f"""
<div class="callout">
  <strong>Confirmed:</strong> Pirelli bring the softest trio in the 2026 range:
  <strong>C3 hard, C4 medium and C5 soft</strong>. Each driver receives two hard sets,
  three mediums and eight softs, plus the wet-weather allocation.
</div>
<div class="grid cols-2">
  {card("Pirelli's 2026 read", ul([
     "Team simulations predict lap times around <strong>two seconds faster</strong> than in 2025.",
     "The front axle should see lower braking loads because the new cars approach the braking zones at reduced speed.",
     "The rear axle faces greater traction demand when full power is deployed.",
     "Braking stability and traction out of the First Chicane and Ascari are the headline performance factors.",
  ]), "bi-record-circle", "accent")}
  {card("Likely strategic shape", ul([
     "Monza is traditionally low degradation and a one-stop race, but the softest allocation broadens the undercut window.",
     "Track position is less binding than at many circuits because slipstreaming and late braking offer recovery chances.",
     "Hot conditions increase the risk of rear-tyre overheating under traction.",
     "Friday long runs will determine the real degradation picture under the new rules.",
  ]), "bi-diagram-3")}
</div>
{pending("Long-run degradation data", "after Friday practice", "bi-graph-down")}
<p class="src">Source: Formula1.com / Pirelli Italian Grand Prix tyre preview, 2 Sep 2026.</p>
""")

    pages["rookies"] = dict(
        kicker="FP1 · four rookie substitutions",
        title="Rookies & Line-ups",
        sub="Four practice swaps plus the continuing Red Bull/Racing Bulls injury cover.",
        body=f"""
<div class="grid cols-2">
  {card("Luke Browning — Williams", ul([
     "Replaces <strong>Alex Albon</strong> in FP1.",
     "Second official FP1 appearance of 2026 and sixth Williams FP1 overall.",
     "His planned Barcelona run did not count after an electrical issue; he subsequently drove in Austria.",
  ]), "bi-person-badge", "accent")}
  {card("Paul Aron — Alpine", ul([
     "Replaces <strong>Pierre Gasly</strong> in FP1.",
     "Fourth FP1 of 2026 and second for Alpine after Hungary; the first two were with Audi.",
     "Helps compare Alpine's latest package, then returns to Enstone for Friday-night simulator work.",
  ]), "bi-person-badge")}
  {card("Colton Herta — Cadillac", ul([
     "Replaces <strong>Sergio Perez</strong> in FP1.",
     "Third Cadillac FP1 after Barcelona and Hungary, and his first low-drag circuit run in the MAC-26.",
     "Combines the outing with his Formula 2 programme for Hitech.",
  ]), "bi-person-badge")}
  {card("Ayumu Iwasa — Red Bull", ul([
     "Replaces <strong>Max Verstappen</strong> in FP1.",
     "Adds rookie running to a weekend already complicated by Red Bull's temporary race-driver reshuffle.",
  ]), "bi-person-badge")}
</div>
{card("Race line-up changes", ul([
   "<strong>Liam Lawson</strong> again replaces the injured Isack Hadjar at Red Bull.",
   "<strong>Yuki Tsunoda</strong> again takes Lawson's regular Racing Bulls seat.",
   "Hadjar is taking a cautious approach to recovery from the wrist injury that also ruled him out at Zandvoort.",
]), "bi-arrow-left-right", "accent")}
""")

    if st.get("drivers"):
        standings_body = f"""
<div class="callout"><strong>Standings after the Dutch Grand Prix.</strong>
  Antonelli has 242 points, 59 ahead of both Russell and Hamilton; Russell holds second on countback.
  Norris is up to fourth after consecutive victories in Hungary and the Netherlands.</div>
<div class="standings-grid">
  <div><h2 class="sec">Drivers</h2><div class="table-wrap"><table class="data ranked">
    <thead><tr><th>Pos</th><th>Driver</th><th>Team</th><th class="num">Pts</th></tr></thead>
    <tbody>{st["drivers"]}</tbody>
  </table></div></div>
  <div><h2 class="sec">Constructors</h2><div class="table-wrap"><table class="data ranked">
    <thead><tr><th>Pos</th><th>Team</th><th class="num">Pts</th></tr></thead>
    <tbody>{st["ctors"]}</tbody>
  </table></div></div>
</div>"""
    else:
        standings_body = pending("Championship standings", "after the Dutch Grand Prix", "bi-trophy")
    pages["standings"] = dict(
        kicker="Championship · after Zandvoort",
        title="Championship & Form",
        sub="Antonelli leads by 59 points; Norris arrives on the season's first back-to-back wins.",
        body=standings_body)

    pages["teams"] = dict(
        kicker="Team watch",
        title="Team Watch & News",
        sub="The team-level stories most likely to shape the Italian Grand Prix.",
        body=f"""
<div class="grid cols-2">
  {card("Mercedes", ul([
     "Antonelli's full power-unit change is strategic rather than the result of a new failure.",
     "Monza was selected because passing opportunities reduce the likely cost of starting at the back.",
     "Russell is level with Hamilton for second in the championship, 59 points behind Antonelli.",
  ]), "bi-lightning-charge", "accent")}
  {card("Ferrari", ul([
     "Home-race Schumacher tribute livery and race suits.",
     "Low-drag floor/bodywork adaptation and removal of rear-wing hanger flaps; the FTM exhaust wing stays.",
     "A new ADUO 2 combustion-engine specification is ready, but its Monza introduction was not confirmed at publication.",
  ]), "bi-flag")}
  {card("McLaren", ul([
     "Norris arrives with consecutive pole-to-win weekends in Hungary and Zandvoort.",
     "New low-drag rear wing, first use of the rotating <strong>H-Wing</strong>, and smaller aero options to evaluate.",
     "Energy harvesting and deployment are expected to produce pace swings around the lap.",
  ]), "bi-speedometer2")}
  {card("Red Bull family", ul([
     "Lawson continues in Hadjar's Red Bull seat; Tsunoda continues at Racing Bulls.",
     "Iwasa takes Verstappen's car for FP1.",
     "Lawson scored seventh on short notice at Zandvoort and now gets a conventional three-practice weekend.",
  ]), "bi-people")}
  {card("Alpine", ul([
     "Both Gasly and Colapinto receive the upgrade package first raced on Gasly's car at Zandvoort.",
     "Aron uses FP1 to compare that package against his simulator work.",
  ]), "bi-tools")}
  {card("Williams & Cadillac", ul([
     "Browning replaces Albon at Williams for FP1.",
     "Herta replaces Perez at Cadillac and samples the MAC-26 in low-drag trim for the first time.",
  ]), "bi-person-badge")}
</div>
""")

    pages["upgrades"] = dict(
        kicker="Development · pre-event",
        title="Car Development & Upgrades",
        sub="Confirmed and reported Monza packages before the FIA car-presentation filing.",
        body=f"""
<div class="grid cols-2">
  {card("Ferrari — drag reduction beyond the wing", ul([
     "Monza-specific floor adaptation revives the single vertical floor-board element previously used in Austria and Britain.",
     "Rear-wing hanger flaps are removed; the front wing is not expected to change significantly.",
     "Ferrari retains the FTM winglet ahead of the exhaust and finds drag reduction elsewhere.",
     "The underlying Zandvoort floor/diffuser update remains the new SF-26 baseline.",
  ]), "bi-tools", "accent")}
  {card("McLaren — H-Wing debut", ul([
     "New low-drag rear-wing specification with the first race-weekend use of McLaren's rotating H-Wing.",
     "Small aero and low-drag options will be evaluated before the qualifying specification is chosen.",
     "The package follows discrete floor, bodywork, diffuser, rear-wing and wheel-rim gains across Hungary and Zandvoort.",
  ]), "bi-tools")}
  {card("Alpine — both cars upgraded", ul([
     "The package introduced on Gasly's car at Zandvoort is available to both race drivers at Monza.",
     "Aron's FP1 work provides a simulator-to-track comparison.",
  ]), "bi-tools")}
</div>
{pending("The complete FIA car-presentation submission", "on Friday of race week")}
<p class="src">Pre-event sources: Formula1.com Tech Weekly and The Race, 31 Aug–2 Sep 2026.
The FIA filing will supersede the pre-event reporting once published.</p>
""")

    pages["powerunit"] = dict(
        kicker="2026 rules · Monza focus",
        title="Power Unit & Override",
        sub="Energy management is a defining Monza variable; exact event-map values await the FIA document.",
        body=f"""
<div class="callout">
  <strong>Why it matters here:</strong> Pirelli and McLaren both identify energy management as an
  additional challenge on Monza's long straights. Cars may trade speed around the lap as they choose
  different points to recharge and deploy.
</div>
<div class="grid cols-2">
  {card("Confirmed weekend themes", ul([
     "The 2026 power unit shifts much more performance to electrical energy and removes the MGU-H.",
     "Active aero uses low-drag straight-line mode rather than the old DRS flap.",
     "Heavy braking gives harvesting opportunities, but the long full-throttle sections make deployment costly.",
     "Watch for lift-and-coast, early clipping and changing relative speed late on each straight.",
  ]), "bi-battery-charging", "accent")}
  {card("Power-unit changes", ul([
     "Antonelli is set for a full power-unit change and a back-of-grid start.",
     "Ferrari's ADUO 2 combustion-engine specification is ready, but its race-weekend introduction was not confirmed in the pre-event report.",
     "The FIA event map will define the exact recharge caps, overtake detection point and activation parameters.",
  ]), "bi-gear")}
</div>
{pending("Monza-specific FIA power-and-energy map values", "with the event documents")}
<p class="src"><a href="{FIA_EVENT_URL}" target="_blank" rel="noopener">FIA Italian Grand Prix documents</a>.</p>
""")

    pages["facts"] = dict(
        kicker="Stats",
        title="Facts, Stats & Records",
        sub="The numbers and recent history worth having ready for Monza.",
        body=f"""
<div class="stat-row">
  {stat("5.793 km", "Circuit length")}
  {stat("53", "Race laps", "306.72 km")}
  {stat("1950", "First championship GP")}
  {stat(_fmt(ref.get("lap_record")), "Race lap record")}
</div>
<div class="grid cols-2">
  {card("Monza records", ul([
     "Michael Schumacher and Lewis Hamilton share the driver record with <strong>five wins</strong> each.",
     "Ferrari are the most successful constructor at their home race.",
     "Monza has hosted every World Championship Italian GP except 1980.",
     "The preserved banking beside the modern circuit remains one of the venue's defining sights.",
  ]), "bi-trophy", "accent")}
  {card("2025 benchmark", ul([
     "Winner and polesitter: <strong>Max Verstappen</strong> for Red Bull.",
     "Verstappen's 1:18.792 pole lap set Formula 1's fastest qualifying average-speed record.",
     "Lando Norris set a 1:20.901 fastest race lap.",
  ]), "bi-stopwatch")}
</div>
<h2 class="sec">Last five Italian Grands Prix</h2>
<div class="table-wrap"><table class="data">
  <thead><tr><th>Year</th><th>Polesitter</th><th>Winner</th></tr></thead>
  <tbody>
    <tr><td>2025</td><td>Max Verstappen (Red Bull)</td><td>Max Verstappen (Red Bull)</td></tr>
    <tr><td>2024</td><td>Lando Norris (McLaren)</td><td>Charles Leclerc (Ferrari)</td></tr>
    <tr><td>2023</td><td>Carlos Sainz (Ferrari)</td><td>Max Verstappen (Red Bull)</td></tr>
    <tr><td>2022</td><td>Charles Leclerc (Ferrari)</td><td>Max Verstappen (Red Bull)</td></tr>
    <tr><td>2021</td><td>Max Verstappen (Red Bull)</td><td>Daniel Ricciardo (McLaren)</td></tr>
  </tbody>
</table></div>
""")

    pages["moments"] = dict(
        kicker="History",
        title="Great Moments",
        sub="Seven Monza stories spanning home triumph, shocks and emotional milestones.",
        body=f"""
<div class="grid cols-2">
  {card("1966 — the last Italian home winner", "<p>Ludovico Scarfiotti won for Ferrari. No Italian driver has won the Italian Grand Prix since.</p>", "bi-flag", "accent")}
  {card("1988 — Ferrari after Enzo", "<p>Gerhard Berger led Michele Alboreto in a Ferrari one-two, less than a month after Enzo Ferrari's death.</p>", "bi-heart")}
  {card("2000 — Schumacher's tears", "<p>Michael Schumacher equalled Ayrton Senna's 41 wins and broke down in the post-race press conference.</p>", "bi-trophy")}
  {card("2008 — Vettel's first win", "<p>Sebastian Vettel won a wet race from pole for Toro Rosso, becoming F1's youngest winner at the time.</p>", "bi-cloud-rain")}
  {card("2019 — Leclerc delivers", "<p>Charles Leclerc resisted Mercedes to give Ferrari its first Monza victory since 2010.</p>", "bi-flag")}
  {card("2020 — Gasly's breakthrough", "<p>Pierre Gasly won a disrupted race for AlphaTauri, holding off Carlos Sainz for his maiden victory.</p>", "bi-stars")}
  {card("2021 — Ricciardo and McLaren", "<p>Daniel Ricciardo led a McLaren one-two after Verstappen and Hamilton collided at the first chicane.</p>", "bi-stars")}
</div>
<p class="src">Source: Formula1.com, “7 memorable Italian Grand Prix moments from Monza”, 31 Aug 2026.</p>
""")

    pages["schedule"] = dict(
        kicker="Timing · forecast",
        title="Schedule & Weather",
        sub="Tallinn is one hour ahead of Monza this weekend; warm, mainly dry conditions are forecast.",
        body=f"""
<div class="callout">
  <strong>Published forecast:</strong> warm and sunny across the event, reaching up to
  <strong>34°C</strong>. Dry conditions are expected, with only a small chance of showers later Sunday.
</div>
<h2 class="sec">Session times</h2>
<div class="table-wrap"><table class="data">
  <thead><tr><th>Session</th><th>Day</th><th>{ctx["tz_local"]}</th><th>{ctx["tz_east"]}</th></tr></thead>
  <tbody>{schedule_rows()}</tbody>
</table></div>
<h2 class="sec">Live session forecast</h2>
{weather_cards()}
<p class="src">Weekend outlook: Formula1.com, 2 Sep 2026. Session cards refresh from Open-Meteo on every build.</p>
""")

    pages["notes"] = dict(
        kicker="Cheat sheet",
        title="Commentator's Cheat Sheet",
        sub="The Monza essentials, compressed for live use.",
        body=f"""
<div class="grid cols-2">
  {card("Numbers to have ready", ul([
     "5.793 km; <strong>53 laps</strong>; 306.72 km.",
     "Race lap record in the circuit library: <strong>" + _fmt(ref.get("lap_record")) + "</strong>.",
     "Pirelli: <strong>C3 / C4 / C5</strong>, the softest 2026 trio.",
     "Antonelli leads by <strong>59 points</strong> but is set for a back-of-grid start.",
     "Forecast: mainly sunny, up to <strong>34°C</strong>, small late-Sunday shower risk.",
  ]), "bi-list-ol", "accent")}
  {card("Grid and practice changes", ul([
     "Lawson for Hadjar at Red Bull; Tsunoda for Lawson at Racing Bulls.",
     "FP1: Browning/Albon, Aron/Gasly, Herta/Perez, Iwasa/Verstappen.",
     "Ferrari: Schumacher tribute plus low-drag floor/bodywork work.",
     "McLaren: H-Wing debut and low-drag options.",
  ]), "bi-people")}
</div>
<div class="grid cols-2">
  {card("The lap", f"<p>{ref.get('character', '')}</p>", "bi-mic")}
  {card("Name-check these corners", ul_or(
     [f"<strong>{name}</strong> — {desc}" for name, desc in ref.get("key_corners", [])]),
     "bi-signpost-split")}
</div>
<div class="callout">
  <strong>Official documents:</strong>
  <a href="{FIA_EVENT_URL}" target="_blank" rel="noopener">FIA Italian Grand Prix event documents</a>.
  Exact power/energy-map values, car-presentation submissions and stewards' decisions should be read
  from there as they publish.
</div>
{pending("Session-by-session commentary notes", "as the weekend runs", "bi-mic")}
""")

    return pages
