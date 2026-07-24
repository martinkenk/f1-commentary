"""Belgian Grand Prix 2026 — page content.

Data-driven pages (results, standings, schedule) are grounded in live
Formula1.com data pulled at build time; evergreen pages (circuit, facts,
moments) use verified reference facts. Session results appear on the auto-built
Results page. Edit prose here; the engine lives in f1lib.py.
"""
from f1lib import card, stat, ul, quote

DRIVER_ROWS = """      <tr><td class="pos">1</td><td>Kimi Antonelli <span class="drv-code">ANT</span></td><td>Mercedes</td><td>204</td></tr>
      <tr><td class="pos">2</td><td>Lewis Hamilton <span class="drv-code">HAM</span></td><td>Ferrari</td><td>159</td></tr>
      <tr><td class="pos">3</td><td>George Russell <span class="drv-code">RUS</span></td><td>Mercedes</td><td>154</td></tr>
      <tr><td class="pos">4</td><td>Charles Leclerc <span class="drv-code">LEC</span></td><td>Ferrari</td><td>126</td></tr>
      <tr><td class="pos">5</td><td>Lando Norris <span class="drv-code">NOR</span></td><td>McLaren</td><td>103</td></tr>
      <tr><td class="pos">6</td><td>Oscar Piastri <span class="drv-code">PIA</span></td><td>McLaren</td><td>92</td></tr>
      <tr><td class="pos">7</td><td>Max Verstappen <span class="drv-code">VER</span></td><td>Red Bull Racing</td><td>91</td></tr>
      <tr><td class="pos">8</td><td>Isack Hadjar <span class="drv-code">HAD</span></td><td>Red Bull Racing</td><td>60</td></tr>
      <tr><td class="pos">9</td><td>Pierre Gasly <span class="drv-code">GAS</span></td><td>Alpine</td><td>42</td></tr>
      <tr><td class="pos">10</td><td>Liam Lawson <span class="drv-code">LAW</span></td><td>Racing Bulls</td><td>39</td></tr>
      <tr><td class="pos">11</td><td>Arvid Lindblad <span class="drv-code">LIN</span></td><td>Racing Bulls</td><td>22</td></tr>
      <tr><td class="pos">12</td><td>Franco Colapinto <span class="drv-code">COL</span></td><td>Alpine</td><td>19</td></tr>
      <tr><td class="pos">13</td><td>Oliver Bearman <span class="drv-code">BEA</span></td><td>Haas F1 Team</td><td>18</td></tr>
      <tr><td class="pos">14</td><td>Gabriel Bortoleto <span class="drv-code">BOR</span></td><td>Audi</td><td>10</td></tr>
      <tr><td class="pos">15</td><td>Carlos Sainz <span class="drv-code">SAI</span></td><td>Williams</td><td>6</td></tr>
      <tr><td class="pos">16</td><td>Alexander Albon <span class="drv-code">ALB</span></td><td>Williams</td><td>5</td></tr>
      <tr><td class="pos">17</td><td>Esteban Ocon <span class="drv-code">OCO</span></td><td>Haas F1 Team</td><td>3</td></tr>
      <tr><td class="pos">18</td><td>Fernando Alonso <span class="drv-code">ALO</span></td><td>Aston Martin</td><td>1</td></tr>
      <tr><td class="pos">19</td><td>Nico Hulkenberg <span class="drv-code">HUL</span></td><td>Audi</td><td>0</td></tr>
      <tr><td class="pos">20</td><td>Valtteri Bottas <span class="drv-code">BOT</span></td><td>Cadillac</td><td>0</td></tr>
      <tr><td class="pos">21</td><td>Sergio Perez <span class="drv-code">PER</span></td><td>Cadillac</td><td>0</td></tr>
      <tr><td class="pos">22</td><td>Lance Stroll <span class="drv-code">STR</span></td><td>Aston Martin</td><td>0</td></tr>"""
CTOR_ROWS = """      <tr><td class="pos">1</td><td>Mercedes</td><td>358</td></tr>
      <tr><td class="pos">2</td><td>Ferrari</td><td>285</td></tr>
      <tr><td class="pos">3</td><td>McLaren</td><td>195</td></tr>
      <tr><td class="pos">4</td><td>Red Bull Racing</td><td>151</td></tr>
      <tr><td class="pos">5</td><td>Alpine</td><td>61</td></tr>
      <tr><td class="pos">6</td><td>Racing Bulls</td><td>61</td></tr>
      <tr><td class="pos">7</td><td>Haas F1 Team</td><td>21</td></tr>
      <tr><td class="pos">8</td><td>Williams</td><td>11</td></tr>
      <tr><td class="pos">9</td><td>Audi</td><td>10</td></tr>
      <tr><td class="pos">10</td><td>Aston Martin</td><td>1</td></tr>
      <tr><td class="pos">11</td><td>Cadillac</td><td>0</td></tr>"""


def build_pages(ctx, env):
    schedule_rows = env["schedule_rows"]
    weather_cards = env["weather_cards"]
    WEATHER_OK = env["weather_ok"]
    TZ_LOCAL_LABEL = ctx["tz_local"]
    TZ_EAST_LABEL = ctx["tz_east"]
    PAGES = {}

    # ---- OVERVIEW --------------------------------------------------------
    PAGES["overview"] = dict(
        kicker="Race weekend · complete",
        title="Weekend Overview",
        sub="Kimi Antonelli converts pole into a maiden Spa win as Mercedes stretch their title lead. Full session results on the Results page.",
        body=f"""
<div class="stat-row">
  {stat("P1", "Antonelli", "pole &rarr; win")}
  {stat("+1.9s", "Leclerc P2", "Ferrari")}
  {stat("P3", "Verstappen", "Red Bull")}
  {stat("44", "Laps", "308.054 km")}
</div>

<div class="grid cols-2">
  {card("How the race went", ul([
     "<strong>Kimi Antonelli</strong> led from pole to flag for his first Spa victory and a big momentum boost at the top of the standings.",
     "<strong>Charles Leclerc</strong> shadowed him home 1.9s back; <strong>Max Verstappen</strong> completed the podium ~11.6s adrift.",
     "<strong>Lewis Hamilton</strong> (P4) and <strong>Oscar Piastri</strong> (P5) headed the chasing pack.",
     "<strong>Lando Norris</strong> qualified P3 but a grid drop shuffled him back; he recovered to P7.",
  ]), "bi-flag-fill", "accent")}
  {card("Why it matters", ul([
     "Antonelli extends his championship lead to <strong>204 pts</strong> &mdash; 45 clear of Hamilton.",
     "<strong>Mercedes</strong> stretch out front in the constructors' on <strong>358 pts</strong>.",
     "Ferrari's double score (Leclerc P2, Hamilton P4) keeps them second in both tables.",
     "Next up: the <strong>Hungarian GP</strong> &mdash; a total contrast to Spa's power-track profile.",
  ]), "bi-graph-up-arrow")}
</div>

<div class="callout">
  <strong>One-liner:</strong> Spa rewarded a clean, controlled drive &mdash; Antonelli never looked
  troubled once he held the lead into La Source. The story now is whether anyone can stop the
  Mercedes charge as the paddock heads to Budapest.
</div>
""")

    # ---- CIRCUIT ---------------------------------------------------------
    PAGES["circuit"] = dict(
        kicker="7.004 km · 19 turns",
        title="Spa-Francorchamps Circuit Guide",
        sub="The longest lap on the calendar &mdash; a proper old-school power-and-commitment track through the Ardennes forest.",
        body=f"""
<h2 class="sec">Circuit map</h2>
<figure class="circuit-fig">
  <img src="../assets/spa_circuit_map_2026.png" alt="2026 Formula 1 Spa-Francorchamps circuit map with turn numbers, straight mode zones, overtake detection and activation points, sectors and speed trap"
       class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen">
  <figcaption><strong>2026 Spa-Francorchamps map</strong> &mdash; turns 1&ndash;19, the three sectors
  (S1 magenta / S2 yellow / S3 blue), the <strong>Straight Mode Zones</strong> (red dashed &mdash; the
  2026 replacement for DRS), the <strong>Overtake Detection</strong> and <strong>Overtake
  Activation</strong> points, and the speed trap. <strong>Click the map to zoom / full screen.</strong>
  <span class="src">Source: Formula1.com 2026 track guide.</span></figcaption>
</figure>

<div class="grid cols-3">
  {card("The signature sequence", ul([
     "<strong>Eau Rouge / Raidillon</strong> (T2&ndash;T4) &mdash; flat-out uphill compression, one of the great corners in the sport.",
     "Leads straight onto the <strong>Kemmel Straight</strong>, the prime overtaking spot.",
     "<strong>Straight Mode</strong> (2026's low-drag mode) makes the Kemmel run even more of a slipstream battle.",
  ]), "bi-arrow-up-right")}
  {card("Sectors", ul([
     "<strong>S1</strong> &mdash; start-finish, La Source hairpin, Eau Rouge and the Kemmel blast.",
     "<strong>S2</strong> &mdash; the fast, flowing middle sector (Les Combes to Pouhon to Stavelot).",
     "<strong>S3</strong> &mdash; the run home through the quicker stuff to the Bus Stop chicane.",
  ]), "bi-sign-intersection")}
  {card("Overtaking & straight mode", ul([
     "<strong>Overtake Detection</strong> near the final chicane; <strong>Activation</strong> onto the pit straight.",
     "Two designated Straight Mode Zones (pit straight + Kemmel).",
     "The <strong>speed trap</strong> sits on the Kemmel &mdash; huge top-speed deltas in the tow.",
  ]), "bi-lightning-charge")}
</div>

<div class="callout">
  <strong>Weather wildcard:</strong> Spa's 7 km lap crosses its own micro-climates &mdash; it can be
  bone dry at the pits and pouring at Stavelot. Always keep a radar on air here.
</div>

<div class="grid cols-2">
  {card("Key numbers", ul([
     "Circuit length: <strong>7.004 km</strong> (longest on the calendar).",
     "Race distance: <strong>308.054 km</strong> over <strong>44 laps</strong>.",
     "First World Championship GP: <strong>1950</strong>.",
     "Lap record: <strong>1:44.701</strong> &mdash; Sergio Perez (2024).",
  ]), "bi-123", "accent")}
  {card("Commentary hooks", ul([
     "Eau Rouge is flat in a modern F1 car &mdash; the drama is the commitment and the compression, not lift-off.",
     "Track position matters less than at Hungary: long lap + Kemmel = real overtaking.",
     "Tyre warm-up through the fast sector is a recurring talking point in cool Ardennes air.",
  ]), "bi-mic")}
</div>
<p class="src">Circuit facts: Formula1.com.</p>
""")

    # ---- TYRES -----------------------------------------------------------
    PAGES["tyres"] = dict(
        kicker="Pirelli",
        title="Tyres & Strategy",
        sub="A long lap, low average grip in the cool, and the ever-present threat of rain make Spa a strategist's minefield.",
        body=f"""
<div class="grid cols-2">
  {card("Why Spa is different", ul([
     "The <strong>longest lap</strong> of the year means fewer laps and each stop costs a big chunk of race distance.",
     "Cool Ardennes temperatures make <strong>tyre warm-up</strong> and graining the headline, not thermal deg.",
     "High-speed corners (Pouhon, Blanchimont) put sustained energy through the tyres.",
     "Rain can flip the strategy instantly &mdash; intermediate and wet calls define Spa races.",
  ]), "bi-record-circle", "accent")}
  {card("Typical strategy picture", ul([
     "Spa usually favours a <strong>one-stop</strong> in the dry, with the medium/hard the workhorses.",
     "The long pit-lane loss encourages track-position plays and undercut/overcut timing battles.",
     "Safety Car probability is meaningful given the fast, weather-exposed layout.",
     "Always have the wet-weather crossover lap in mind for on-air strategy talk.",
  ]), "bi-diagram-3")}
</div>
<div class="callout watch">
  <strong>On air:</strong> confirm Pirelli's exact compound nomination for the weekend and the
  live track/air temps before locking in any strategy narrative &mdash; Spa punishes assumptions.
</div>
""")

    # ---- ROOKIES / LINE-UPS ---------------------------------------------
    PAGES["rookies"] = dict(
        kicker="Grid watch",
        title="Rookies & Line-ups",
        sub="The 2026 grid's newer names and who's carrying momentum into the Ardennes.",
        body=f"""
<div class="grid cols-2">
  {card("Names to watch", ul([
     "<strong>Kimi Antonelli</strong> (Mercedes) &mdash; no longer a rookie in results terms: a Spa win and the championship lead.",
     "<strong>Arvid Lindblad</strong> (Racing Bulls) &mdash; qualified a strong P7 at Spa; one of the standout younger drivers.",
     "<strong>Gabriel Bortoleto</strong> (Audi) &mdash; in the points fight, scored at Spa.",
     "<strong>Franco Colapinto</strong> (Alpine) &mdash; rebuilding form in the midfield.",
  ]), "bi-person-badge", "accent")}
  {card("Context", ul([
     "Belgium was a standard (non-sprint) weekend, so the younger drivers had full practice running.",
     "Spa's demands &mdash; commitment through Eau Rouge, energy management on the Kemmel &mdash; expose experience gaps quickly.",
     "Watch how the newer names handle changeable weather, historically where Spa reputations are made.",
  ]), "bi-info-circle")}
</div>
<p class="src">Grid context from Formula1.com session results.</p>
""")

    # ---- STANDINGS -------------------------------------------------------
    PAGES["standings"] = dict(
        kicker="After Belgium",
        title="Championship & Form",
        sub="The title picture after Round 13 &mdash; Antonelli and Mercedes in command.",
        body=f"""
<div class="stat-row">
  {stat("204", "Antonelli", "championship leader")}
  {stat("45", "Lead over P2", "Hamilton on 159")}
  {stat("358", "Mercedes", "constructors' leader")}
  {stat("73", "Merc margin", "over Ferrari")}
</div>

<div class="grid cols-2">
  {card("Drivers' Championship", '''
  <div class="table-wrap"><table class="data">
    <thead><tr><th>Pos</th><th>Driver</th><th>Team</th><th>Pts</th></tr></thead>
    <tbody>
''' + DRIVER_ROWS + '''
    </tbody>
  </table></div>
  ''', "bi-trophy", "accent")}

  {card("Constructors' Championship", '''
  <div class="table-wrap"><table class="data">
    <thead><tr><th>Pos</th><th>Team</th><th>Pts</th></tr></thead>
    <tbody>
''' + CTOR_ROWS + '''
    </tbody>
  </table></div>
  ''', "bi-people-fill", "accent")}
</div>
<p class="src">Standings: Formula1.com, after the 2026 Belgian Grand Prix.</p>
""")

    # ---- TEAM WATCH ------------------------------------------------------
    PAGES["teams"] = dict(
        kicker="Form guide",
        title="Team Watch & News",
        sub="Where each team sits leaving Spa, based on the weekend's results and the championship order.",
        body=f"""
<div class="grid cols-2">
  {card("Mercedes &mdash; front-runners", ul([
     "Antonelli won from pole; Russell qualified and started P3.",
     "Clear leaders in both championships leaving Spa.",
  ]), "bi-star-fill", "accent")}
  {card("Ferrari &mdash; best of the rest", ul([
     "Leclerc P2, Hamilton P4 &mdash; a strong double score.",
     "Second in the constructors', chasing Mercedes.",
  ]), "bi-star")}
  {card("Red Bull", ul([
     "Verstappen salvaged a P3 podium; Hadjar backed it up in the points.",
     "Fourth in the constructors', ahead of a tight midfield.",
  ]), "bi-lightning")}
  {card("McLaren", ul([
     "Piastri P5, Norris recovering to P7 after a grid drop from P3 in qualifying.",
     "Third in the constructors' but off the top two's pace at Spa.",
  ]), "bi-cone-striped")}
</div>
<p class="src">Based on Formula1.com Belgian GP results and 2026 standings.</p>
""")

    # ---- UPGRADES --------------------------------------------------------
    PAGES["upgrades"] = dict(
        kicker="Car development",
        title="Car Development & Upgrades",
        sub="Spa is the calendar's classic low-drag test &mdash; the reference weekend for skinny-wing efficiency.",
        body=f"""
<div class="callout">
  Spa's long full-throttle sections make it the <strong>lowest-downforce setup weekend</strong>
  outside Monza. Teams trim rear wings hard and chase straight-line efficiency, trading some
  cornering load for Kemmel-straight speed.
</div>
<div class="grid cols-2">
  {card("What to look for", ul([
     "Trimmed / low-downforce rear wings and beam-wing choices.",
     "The eternal Spa compromise: wing level vs. wet-weather insurance.",
     "Cooling and brake-duct choices for the long lap and heavy braking at the chicanes.",
  ]), "bi-tools", "accent")}
  {card("Commentary note", ul([
     "Setup direction here doesn't carry to Hungary &mdash; the two tracks are opposite ends of the downforce range.",
     "Confirm any team-specific upgrade parts against the FIA car-presentation documents when published.",
  ]), "bi-info-circle")}
</div>
""")

    # ---- POWER UNIT ------------------------------------------------------
    PAGES["powerunit"] = dict(
        kicker="2026 Rules",
        title="Power Unit & Override",
        sub="Spa is one of the most power- and energy-sensitive tracks of the year &mdash; exactly where the 2026 formula is most exposed.",
        body=f"""
<div class="callout">
  In 2026 the electrical side of the power unit is far bigger and DRS is replaced by a
  battery-boost <strong>Manual Override</strong> plus low-drag <strong>Straight Mode</strong>.
  Spa's long full-throttle stretches make <strong>energy deployment and harvesting</strong> a
  defining performance factor.
</div>
<div class="grid cols-2">
  {card("Why Spa stresses the PU", ul([
     "Two long near-full-throttle runs (up the hill to Les Combes, and the Kemmel Straight) drain deployment.",
     "Getting caught <strong>power-limited</strong> before the speed trap is the 2026 equivalent of running out of DRS.",
     "Harvesting through the fast middle sector is limited, so lap-energy budgeting is tight.",
  ]), "bi-lightning-charge", "accent")}
  {card("On air", ul([
     "Watch for cars 'parking' on the straight as energy runs out &mdash; a recurring 2026 talking point.",
     "Straight Mode + Manual Override into Les Combes is the key overtaking combination.",
     "Pull the event-specific FIA <em>Power Unit Information</em> document for the exact override energy, power-cut sectors and detection lines when it's published.",
  ]), "bi-battery-charging")}
</div>
<p class="src">2026 power-unit framework per FIA regulations; confirm event-specific figures against the FIA Power Unit Information document.</p>
""")

    # ---- FACTS -----------------------------------------------------------
    PAGES["facts"] = dict(
        kicker="Stats & Records",
        title="Facts, Stats & Records",
        sub="The number-drops for the broadcast.",
        body=f"""
<div class="stat-row">
  {stat("7.004 km", "Lap length", "longest of the year")}
  {stat("1:44.701", "Lap record", "Perez, 2024")}
  {stat("1950", "First GP", "F1 championship")}
  {stat("44", "Race laps", "308.054 km")}
</div>
<div class="grid cols-2">
  {card("Spa in brief", ul([
     "One of the original 1950 World Championship venues.",
     "The longest circuit on the current calendar at 7.004 km.",
     "Home of Eau Rouge/Raidillon &mdash; the sport's most famous corner sequence.",
     "Notorious for split-track weather across its 7 km.",
  ]), "bi-bar-chart", "accent")}
  {card("2026 Belgian GP result", ul([
     "Winner: <strong>Kimi Antonelli</strong> (Mercedes), from pole.",
     "P2 <strong>Charles Leclerc</strong> (+1.952s), P3 <strong>Max Verstappen</strong> (+11.586s).",
     "Full classification on the <strong>Results</strong> page.",
  ]), "bi-flag-fill")}
</div>
<p class="src">Facts: Formula1.com.</p>
""")

    # ---- MOMENTS ---------------------------------------------------------
    PAGES["moments"] = dict(
        kicker="History",
        title="Great Spa Moments",
        sub="Evergreen Ardennes drama to draw on during quiet spells.",
        body=f"""
<div class="grid cols-2">
  {card("Classics to reference", ul([
     "<strong>2000</strong> &mdash; Hakkinen's double-pass on Schumacher (and a lapped Zonta) at Les Combes.",
     "<strong>1998</strong> &mdash; the huge first-lap pile-up in the rain, then Hill/Schumacher chaos.",
     "<strong>1992</strong> &mdash; Schumacher's first F1 win, at the track where he later dominated.",
     "<strong>2021</strong> &mdash; the rain-shortened 'race' behind the Safety Car; half points awarded.",
  ]), "bi-stars", "accent")}
  {card("Why Spa delivers", ul([
     "Eau Rouge and the Kemmel Straight reward bravery and slipstreaming in equal measure.",
     "The weather turns Spa into a lottery more often than any other venue.",
     "Long lap = big lead swings and genuine overtaking, unlike tighter modern circuits.",
  ]), "bi-clock-history")}
</div>
""")

    # ---- SCHEDULE & WEATHER ---------------------------------------------
    PAGES["schedule"] = dict(
        kicker="Timing",
        title="Schedule & Weather",
        sub="All times in Spa local (CEST) and Tallinn (EEST). Weather shows actual conditions for completed sessions.",
        body=f"""
<div class="table-wrap">
  <table class="data">
    <thead><tr><th>Session</th><th>Day</th><th>{TZ_LOCAL_LABEL}</th><th>{TZ_EAST_LABEL}</th></tr></thead>
    <tbody>
      {schedule_rows()}
    </tbody>
  </table>
</div>

<h2 class="sec">Conditions</h2>
{weather_cards()}
<p class="src">{'Conditions via Open-Meteo, fetched at build time. Past sessions show actual (ERA5) data; upcoming sessions show the forecast. Times aligned to Tallinn / EEST.' if WEATHER_OK else 'Rebuild with an internet connection to embed weather.'}</p>
""")

    # ---- NOTES -----------------------------------------------------------
    PAGES["notes"] = dict(
        kicker="Cheat sheet",
        title="Commentator's Cheat Sheet",
        sub="Grab-and-go talking points for the Belgian GP.",
        body=f"""
<div class="grid cols-2">
  {card("Result headlines", ul([
     "Antonelli: pole-to-flag win, now 204 pts and 45 clear at the top.",
     "Leclerc P2 / Hamilton P4 &mdash; Ferrari's double score.",
     "Verstappen P3; Norris recovered to P7 after a grid drop.",
  ]), "bi-flag-fill", "accent")}
  {card("Track talking points", ul([
     "7.004 km, 19 turns, 44 laps &mdash; the longest lap of the year.",
     "Eau Rouge/Raidillon is flat; the story is commitment and compression.",
     "Kemmel Straight + Straight Mode + Manual Override = the overtaking combo.",
     "Weather can differ across the lap &mdash; keep a radar handy.",
  ]), "bi-mic")}
</div>
<div class="callout watch">
  <strong>Golden rule:</strong> at Spa, never over-commit to a strategy narrative &mdash; one rain
  cell over Stavelot can rewrite the race in a single lap.
</div>
""")

    return PAGES
