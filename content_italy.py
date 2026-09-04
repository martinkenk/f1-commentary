"""Italian Grand Prix 2026 bespoke page content.

Race-week facts are drawn from Formula1.com, The Race and the FIA event hub.
Unpublished FIA values remain explicit pending states in the generic baseline.
"""
from f1lib import card, news_item, render_news, render_penalties, stat, ul
from content_generic import build_pages as build_generic, pending, ul_or, _fmt


FIA_EVENT_URL = ("https://www.fia.com/documents/championships/"
                 "fia-formula-one-world-championship-14/season/season-2026-2072/"
                 "event/Italian%20Grand%20Prix")

FIA_RD_NOTES_URL = ("https://www.fia.com/system/files/decision-document/"
                     "2026_italian_grand_prix_-_race_directors_competition_notes.pdf")


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
    circuit_page = pages.get("circuit")
    if circuit_page:
        circuit_page["body"] += f"""
<h2 class="sec">Race-control notes (FIA Competition Notes, Document 5)</h2>
<div class="grid cols-2">
  {card("Track limits & escape roads", ul([
     "Failing to negotiate <strong>Turn 11</strong> (Parabolica) during any timed session invalidates that lap and the following lap.",
     "The Turn 1&ndash;2 escape road has four rows of polystyrene blocks; drivers must go around each row's end to re-join.",
     "At the Turn 4&ndash;5 escape road, drivers who go straight and pass right of the gravel must stay right of the yellow line/bollard and re-join after Turn 5.",
  ]), "bi-signpost-split", "accent")}
  {card("Circuit changes since 2025", ul([
     "New asphalt patch at Turn 2; new wall and debris fence on the left of the main straight.",
     "New negative kerbs before Turns 1, 4 and 8 (100 m brake markers) on the relevant sides.",
     "Part of the Turn 5 gravel bed (left) replaced by asphalt; new natural grass at Turn 9 apex; new fencing between Turns 10 and 11.",
  ]), "bi-cone-striped")}
</div>
<p class="src">Source: <a href="{FIA_RD_NOTES_URL}" target="_blank" rel="noopener">FIA 2026 Italian Grand Prix — Race Director's Competition Notes</a> (Document 5, issued 3 Sep 2026) via the
<a href="{FIA_EVENT_URL}" target="_blank" rel="noopener">FIA Italian Grand Prix documents hub</a>.</p>

<h2 class="sec">Where the corner names come from</h2>
<div class="grid cols-2">
  {card("Chicanes named for what they are", ul([
     "Prima Variante ('first chicane') was added in the 1972 refurbishment to cut the era's extreme speeds; it replaced the old Variante del Rettifilo, on the original start/finish straight, before a further 2000 reprofile.",
     "Seconda Variante ('second chicane') dates from further 1976 safety changes and still carries generous run-off.",
     "Variante Ascari, the final chicane before the pit straight, honours Alberto Ascari, the two-time champion killed at Monza in 1955; it was previously the Curva del Platano ('plane tree curve').",
  ]), "bi-signpost-split", "accent")}
  {card("Sweepers named for the local towns and families", ul([
     "Turn 3, now Biassono, was long known as Curva Grande ('great curve') for its shape before taking the name of a nearby town in the 1970s changes.",
     "Turns 6&ndash;7, Lesmo 1 &amp; 2, were originally Curva della Querce ('curve of the oaks') and take their modern name from the town of Lesmo.",
     "Turn 8, sometimes called Curva della Roggia after a nearby stream, is best known for the 1995 Hill/Schumacher collision.",
     "Turn 11, officially Curva Alboreto since a recent renaming for 1980s&ndash;90s driver Michele Alboreto, is still almost universally called Parabolica for its parabola-like shape.",
  ]), "bi-book")}
</div>
<p class="src">Source: <a href="https://www.formula1.com/en/latest/article/explained-how-every-corner-at-monza-got-its-name.53lIthEwI2Ko9BC8YRnuZK" target="_blank" rel="noopener">Formula1.com, "EXPLAINED: How every corner at Monza got its name"</a>.</p>
"""

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
<h2 class="sec">Pirelli's Monza preview graphic</h2>
<figure class="circuit-fig">
  <img src="../assets/italy_pirelli_tyres_2026.png" alt="Pirelli 2026 Italian Grand Prix Monza preview infographic showing circuit information, tyre stress ratings, minimum starting and stabilised running pressures, camber limits and the C3/C4/C5 compound selection"
       class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen">
  <figcaption><strong>Official Pirelli event-preview graphic</strong> — circuit data, tyre demand ratings
  (traction, braking, tyre stress, asphalt grip/abrasion, lateral, track evolution), 18&Prime; minimum
  starting/stabilised running pressures, camber limits and the confirmed C3/C4/C5 compound trio.
  <span class="src">Source: <a href="https://www.formula1.com/en/latest/article/what-tyres-will-the-teams-and-drivers-have-for-the-2026-italian-grand-prix.7nOpWdCgvCBFDGlnODs0gk" target="_blank" rel="noopener">Formula1.com</a> / Pirelli, 2 Sep 2026.</span></figcaption>
</figure>
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

<h2 class="sec">FIA tyre prescriptions (Document 3, Competition Notes — Pirelli Preview)</h2>
<div class="callout">
  <strong>Race-tyre nuance:</strong> the mandatory-race-tyre panel names only <strong>C3 and C4</strong>
  &mdash; every driver must use both compounds across the race. The softest C5 is reserved for one-lap
  pace: it is designated the <strong>Q3 tyre</strong>, so its heaviest race use is likely to come from
  drivers eliminated in Q1/Q2 rather than the top-10 runners who start on their Q2 time.
</div>
<div class="table-wrap"><table class="data compact">
  <thead><tr><th>Slick axle</th><th>Min. starting pressure</th><th>Expected stabilised pressure</th><th>Camber limit</th></tr></thead>
  <tbody>
    <tr><td class="drv">Front</td><td class="num">26.0 psi</td><td class="num">&ge;27.0 psi</td><td class="num">&minus;3&deg;</td></tr>
    <tr><td class="drv">Rear</td><td class="num">26.0 psi</td><td class="num">&ge;27.0 psi</td><td class="num">&minus;2&deg;</td></tr>
  </tbody>
</table></div>
<p class="src">Wet-weather prescriptions (for reference): intermediates run 28.0 psi minimum starting/&ge;29.0 psi
stabilised on both axles (&minus;3.25&deg; front / &minus;2.5&deg; rear camber); wets run 26.0 psi minimum
starting/&ge;29.0 psi stabilised (same camber limits as intermediates).
Source: <a href="https://www.fia.com/system/files/decision-document/2026_italian_grand_prix_-_competition_notes_-_pirelli_preview.pdf" target="_blank" rel="noopener">FIA 2026 Italian Grand Prix — Competition Notes: Pirelli Preview</a>
(Document 3, issued 2 Sep 2026) via the
<a href="{FIA_EVENT_URL}" target="_blank" rel="noopener">FIA Italian Grand Prix documents hub</a>.</p>
""")

    pages["penalties"] = dict(
        kicker="Stewards · technical",
        title="Penalties & Stewards",
        sub="No Monza stewards' decisions yet; two pre-event FIA technical filings are worth flagging.",
        body=render_penalties(
            ctx,
            intro_html=f"""
<div class="grid cols-2">
  {card("Zandvoort compliance check cleared (Document 2)", ul([
     "Car number 10 (Gasly, Alpine) was randomly selected from the top ten after the Dutch GP for extensive physical inspection of its re-programmable electronic devices and SECU.",
     "The FIA Technical Delegate found the software/source code, SECU configuration files and data offloads all compliant with the 2026 Technical Regulations.",
     "No further action; carried over from the previous round as a routine post-race technical report.",
  ]), "bi-check-circle", "accent")}
  {card("Power-unit elements used per driver (Document 9)", ul([
     "The FIA's season-to-date element count shows Antonelli on 4 ICE / 3 TC / 3 EXH / 2 MGU-K / 3 ES / 3 PU-CE / 5 PU-ANC — level with team-mate Russell on most counts.",
     "Lawson (5 ICE / 5 TC / 5 EXH) and the two Aston Martins (4 ICE / 4 TC, Stroll also on 4 MGU-K/5 ES/5 PU-CE) currently carry the highest published counts on the grid.",
     "The document lists cumulative use only; it does not itself state the per-element allocation limit or confirm which counts have triggered a penalty.",
  ]), "bi-clipboard-data")}
</div>
<p class="src">Sources: <a href="https://www.fia.com/system/files/decision-document/2026_italian_grand_prix_-_post-race_checks_on_car_number_10_2026_dutch_gp.pdf" target="_blank" rel="noopener">FIA 2026 Italian Grand Prix — Technical Delegate's Report, Post-Race Checks on Car Number 10 (2026 Dutch GP)</a> (Document 2, issued 2 Sep 2026) and
<a href="https://www.fia.com/system/files/decision-document/2026_italian_grand_prix_-_pu_elements_used_per_driver_up_to_now.pdf" target="_blank" rel="noopener">FIA 2026 Italian Grand Prix — Technical Delegate's Report, PU Elements Used per Driver up to Now</a> (Document 9, issued 4 Sep 2026), both via the
<a href="{FIA_EVENT_URL}" target="_blank" rel="noopener">FIA Italian Grand Prix documents hub</a>.</p>
""",
            fia_url=FIA_EVENT_URL,
        ))

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
     "Team-mate context: Piastri, a title contender at this point last year, hasn't won since Zandvoort 2025 and is "
     "now 55 points and three places behind Norris in the standings.",
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
  {card("Aston Martin", ul([
     "CTO Enrico Cardile says the AMR26's aero development is essentially done — no more upgrades planned beyond a stray part worth track-testing for 2027.",
     "Weight-saving programme continues, targeted for completion by the Azerbaijan round.",
     "Honda's Zandvoort Spec 2 engine (an estimated 10–30bhp step) is its last major 2026 hardware update; Alonso called it &quot;not a big improvement, to be honest&quot;.",
  ]), "bi-tools")}
</div>
<p class="src">Team-mate context: The Race, "What's gone wrong for this former F1 title contender", 2 Sep 2026.
Aston Martin/Honda development plan: The Race, "What Aston Martin revealed about 2026 (and 2027) upgrade plan", 3 Sep 2026.</p>
""")

    pages["upgrades"] = dict(
        kicker="Development · pre-event",
        title="Car Development & Upgrades",
        sub="Confirmed and reported Monza packages, plus the FIA's Friday car-presentation procedure.",
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
  {card("Aston Martin &amp; Honda — development effectively closed for 2026", ul([
     "CTO Enrico Cardile says the Hungary B-spec and its Zandvoort refinements are &quot;the last planned aero developments&quot; for the AMR26, barring a stray part worth track-testing for 2027 correlation.",
     "The team's weight-saving programme continues and should be complete by Azerbaijan (24–26 Sep), after which the car runs in final 2026 form for the rest of the season.",
     "Cardile: no design carryover into 2027 — &quot;every single part will be new,&quot; evolving this year's concept rather than repeating it.",
     "Honda brought its Spec 2 engine upgrade at Zandvoort (estimated 10–30bhp) and says that is the only major 2026 hardware update; a driveability countermeasure from Honda's Sakura base follows, plus per-event calibration tweaks only.",
  ]), "bi-tools")}
</div>
<div class="grid cols-2">
  {card("FIA car-presentation procedure (Document 7, confirmed)", ul([
     "Between 11:00 and 12:00 on Friday, one car per team must sit in its pit-stop position with the other available for viewing inside the garage.",
     "If only one car of the pair carries new major aero/bodywork components not previously run, that is the car that must be displayed to media.",
     "In adverse weather the display may move into the garage area, with awnings used if it is raining.",
  ]), "bi-camera")}
</div>

<h2 class="sec">FIA car-presentation submissions (Document 10, filed 4 Sep)</h2>
<div class="callout">
  <strong>Now confirmed:</strong> every team's mandatory geometric-change declaration is published.
  Ten of eleven teams filed new-part submissions; Audi filed none for this event.
</div>
<div class="grid cols-2">
  {card("Ferrari", ul([
     "Floor board: front floor-board elements re-optimised around a single vertical element.",
     "Mirror stay shortened and reconnected to the sidepod; rear brake-duct winglet cascade removed.",
     "RV tail gets a slotted central winglet element with trimmed side winglets.",
     "All four changes are filed as circuit-specific drag-range items for Monza.",
  ]), "bi-tools", "accent")}
  {card("McLaren", ul([
     "Rear wing: alternative straight-line-mode flap position paired with a less-loaded beam wing for a larger drag reduction — the filed description of the H-Wing debut.",
     "Floor furniture updated for better flow conditioning and a further aerodynamic/drag gain.",
  ]), "bi-tools")}
  {card("Mercedes", ul([
     "Rear wing: various winglet devices removed to reduce assembly camber and shed local downforce/drag at a ratio suited to Monza's low-drag/low-downforce ratio.",
     "Front bodywork: mirror rear stays trimmed for the same circuit-specific drag reason.",
  ]), "bi-tools")}
  {card("Red Bull", ul([
     "Rear corner: revised rear-suspension-to-wheel bodywork gaitor for reliability, with winglet junctions removed.",
     "Floor body: revised bib-edge profile filed as a Monza evaluation of an alternative geometry for more local load.",
     "Exhaust tailpipe bracket revised for reliability at Monza's specific power-unit demands.",
  ]), "bi-tools")}
</div>
<div class="grid cols-2">
  {card("Racing Bulls &amp; Williams", ul([
     "Racing Bulls: new rear wing with updated straight-mode mechanism for increased flap travel, plus a repositioned exhaust tailpipe for better centreline flow.",
     "Williams: a vertical fence added around the Halo for a circuit-specific efficiency gain, a reduced-chord front-wing-flap element for balance, and a local trim to the floor-board geometry.",
  ]), "bi-tools")}
  {card("Aston Martin, Haas &amp; Alpine", ul([
     "Aston Martin: revised front-suspension fairings for onset-flow alignment and a floor-edge update ahead of the rear tyre for local load.",
     "Haas: new front floor with revised side geometry/diffuser, new sidepod/coke-line with a narrower roll hoop and updated engine cover, plus re-optimised rear-corner fairings and realigned drum deflectors — its most extensive filing of the ten.",
     "Alpine: revised front-wing footplate vane for local load, and a straight-mode pod-fairing removal on the rear wing to suit Monza's low-drag character.",
  ]), "bi-tools")}
  {card("Cadillac &amp; Audi", ul([
     "Cadillac: updated forward floor-board stay with a higher outboard attachment point, plus a small vertical turning vane added to the outboard diffuser sidewall's inner trailing edge.",
     "Audi: no updates submitted for this event.",
  ]), "bi-tools")}
</div>
<p class="src">Pre-event sources: Formula1.com Tech Weekly and The Race, 31 Aug–2 Sep 2026.
Aston Martin/Honda development-plan detail: The Race, "What Aston Martin revealed about 2026 (and 2027) upgrade plan", 3 Sep 2026.
FIA car-presentation procedure: <a href="https://www.fia.com/system/files/decision-document/2026_italian_grand_prix_-_car_display_procedure.pdf" target="_blank" rel="noopener">FIA Document 7, issued 3 Sep 2026</a>.
Team-by-team filings: <a href="https://www.fia.com/system/files/decision-document/2026_italian_grand_prix_-_car_presentation_submissions.pdf" target="_blank" rel="noopener">FIA Document 10, Car Presentation Submissions, issued 4 Sep 2026</a> via the
<a href="{FIA_EVENT_URL}" target="_blank" rel="noopener">FIA documents hub</a>.</p>
""")

    FIA_PU_URL = ("https://www.fia.com/system/files/decision-document/"
                  "2026_italian_grand_prix_-_power_unit_information.pdf")
    pages["powerunit"] = dict(
        kicker="2026 rules · Monza focus",
        title="Power Unit & Override",
        sub="The FIA's event-specific power-and-energy map is confirmed for Monza.",
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
  ]), "bi-gear")}
</div>
<h2 class="sec">FIA event power-and-energy map (Document 8, 3 Sep)</h2>
<div class="callout watch">
  <i class="bi bi-lightbulb"></i> <strong>Monza's qualifying quirk:</strong> the maximum recharge
  permitted per lap in qualifying is just <strong>5.0 MJ</strong> &mdash; lower than every other
  session (race, free practice and even out-laps) &mdash; yet qualifying is the <em>only</em> time a
  car may run the higher "Base &ndash; Overtake" deployment curve across the <strong>whole lap</strong>
  rather than only in the marked overtaking zone. With so little energy needing to be recovered under
  braking, teams have little reason to manage harvesting on the way into the chicanes; the likely
  trade-off is less need for the early lift-and-coast/"clipping" used elsewhere to protect the recharge
  budget, so cars can carry deployment closer to the braking point at the end of each Monza straight.
  This reading follows from the numbers below; the FIA document does not itself explain the rationale.
</div>
<div class="grid cols-2">
  {card("Maximum recharge per lap (Article C5.2.10)", ul([
     "Race: <strong>7.0 MJ</strong> with overtake not active, <strong>7.5 MJ</strong> with overtake active.",
     "Qualifying (any segment): <strong>5.0 MJ</strong> &mdash; the lowest cap of any session.",
     "Free practice sessions: <strong>7.5 MJ</strong>.",
     "Out-laps other than in the race: <strong>9.0 MJ</strong>.",
  ]), "bi-lightning-charge", "accent")}
  {card("Maximum PU power reduction rate (Article C5.12.8)", ul([
     "Power-limited distance: <strong>4218 m</strong>.",
     "Rate limit: <strong>50 kW/s</strong> &mdash; this cap applies across sessions and is separate from the recharge-per-lap figures above.",
     "Sector T4&ndash;T7 (2100&ndash;2800 m) carries a maximum PU power reduction of <strong>350 kW</strong> (Article C5.12.4), with a Sprint-Qualifying/Qualifying-only alternate window at the Turn 11 exit (5050&ndash;5350 m, or 5300&ndash;5800 m where the reduction-reset rule of Article C5.12.5 applies).",
  ]), "bi-speedometer2")}
</div>
<div class="grid cols-2">
  {card("Maximum DC power of ERS-K vs. car speed (Article C5.2.8)", ul([
     "Sprint &amp; Race, main overtaking zone: <strong>Base &ndash; Standard</strong> curve (overtake not active) or <strong>Base &ndash; Overtake</strong> (overtake active).",
     "Sprint &amp; Race, everywhere else on the lap: the reduced <strong>Alt 1</strong> curve, which falls away above roughly 290&ndash;300 km/h.",
     "Any practice session, including all qualifying segments: <strong>Base &ndash; Overtake</strong> applies for the entire lap &mdash; there is no Alt 1 restriction in qualifying.",
  ]), "bi-graph-up-arrow", "accent")}
  {card("Main overtaking zone", ul([
     "Detection line at approximately <strong>5050 m</strong> (TBC), activation line at <strong>5249 m</strong> lap distance (between corners L18 and L19, the Parabolica exit onto the pit straight).",
     "Detection gap: <strong>1.0 s</strong>.",
     "The Overtake power curve gives a materially higher MGU-K DC-power ceiling than the Base/Standard curve across the 220&ndash;360 km/h band, per the FIA's published power-vs-speed chart.",
  ]), "bi-record-circle")}
</div>
<p class="src">Source: <a href="{FIA_PU_URL}" target="_blank" rel="noopener">FIA 2026 Italian Grand Prix — Power Unit Information</a> (Document 8, issued 3 Sep 2026, 20:50) via the
<a href="{FIA_EVENT_URL}" target="_blank" rel="noopener">FIA Italian Grand Prix documents hub</a>.</p>
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
<div class="grid cols-2">
  {card("This year's trophy", ul([
     "The 2026 winners lift <strong>FRAGILE</strong>, a trophy resembling a stack of cups and bowls "
     "designed by Italian artist duo vedovamazzei.",
     "It goes to the top three finishers and a representative of the winning constructor.",
     "Part of an annual initiative, launched in 2021, commissioning a different Italian artist each year.",
  ]), "bi-trophy",
  "accent")}
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
<p class="src">Trophy: The Race, "Italian GP unveils one of F1's most unusual trophies", 1 Sep 2026.</p>
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
        sub="Warm, mainly dry conditions are forecast; the FIA has declared a Heat Hazard for the race.",
        body=f"""
<div class="callout">
  <strong>Published forecast:</strong> warm and sunny across the event, reaching up to
  <strong>34°C</strong>. Dry conditions are expected, with only a small chance of showers later Sunday.
</div>
<div class="callout watch">
  <i class="bi bi-thermometer-sun"></i> <strong>FIA Heat Hazard declared (Document 4, 3 Sep, 08:24).</strong>
  The Official Weather Service forecasts a Heat Index above <strong>31.0&deg;C</strong> at some point during
  the race, triggering Article B1.5.10 driver cooling-system provisions.
  <span class="src">Source: <a href="https://www.fia.com/system/files/decision-document/2026_italian_grand_prix_-_heat_hazard_declaration.pdf" target="_blank" rel="noopener">FIA Italian Grand Prix Heat Hazard declaration</a>.</span>
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
