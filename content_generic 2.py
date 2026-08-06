"""
Generic Grand Prix pages — used for every event that doesn't have a bespoke
``content_<gp>.py`` module.

The point of this module is *progressive disclosure*. A race four months away
still has plenty of genuinely useful material: the circuit, the session times,
the format, the history, the power-unit rules, the talking points. What it
doesn't have is tyre allocations, rookie line-ups, upgrade filings or results.

So every page renders what is actually known and marks the rest with an explicit
"not published yet" state rather than inventing it or leaving a hole. Each
rebuild picks up whatever has since appeared, so a page fills itself in as the
weekend approaches without anyone editing this file.

Reference material comes from ``circuits.py``; hard numbers and session times
come from ``data/calendar_2026.json`` via ``calendar.py``.
"""
from f1lib import card, stat, ul
import datetime


def pending(what, when="", icon="bi-hourglass-split"):
    """The standard 'this fills in automatically' block.

    Being explicit about *what* is missing and *when* it lands is the difference
    between a page that looks unfinished and one that looks scheduled.
    """
    tail = f" Usually published {when}." if when else ""
    return (f'<div class="callout watch"><i class="bi {icon}"></i> '
            f"<strong>{what} not published yet.</strong>{tail} "
            "This section fills in automatically the next time the site is built "
            "after the source goes live.</div>")


def _fmt(value, fallback="To be confirmed"):
    return value if value else fallback


def _km(length):
    """'5.793km' -> 5.793. Returns 0.0 when the length isn't published yet."""
    try:
        return float(str(length).lower().replace("km", "").strip())
    except ValueError:
        return 0.0


def ul_or(items, fallback="<p>To be added.</p>"):
    """`ul([])` renders an empty list rather than nothing, so guard explicitly."""
    return ul(items) if items else fallback


def _corner_cards(ref):
    return "".join(
        card(name, f"<p>{desc}</p>", "bi-signpost-split")
        for name, desc in ref.get("key_corners", [])
    )


def build_pages(ctx, env):
    schedule_rows = env["schedule_rows"]
    weather_cards = env["weather_cards"]
    ref = ctx.get("ref") or {}
    cal = ctx.get("cal") or {}
    status = ctx.get("status", "future")
    sprint = bool(cal.get("is_sprint"))
    gp = ctx["name"]
    circuit = ctx["circuit"]
    tz_local = ctx["tz_local"]
    tz_east = ctx["tz_east"]
    laps = cal.get("laps") or ""
    length = cal.get("circuit_length") or ""
    distance = cal.get("race_distance") or ""
    first_gp = cal.get("first_gp") or ""
    fia_url = ctx.get("fia_url", "")
    P = {}

    fmt_line = ("<strong>Sprint weekend</strong> — one hour of practice, then Sprint "
                "Qualifying, the Sprint, Qualifying and the Grand Prix."
                if sprint else
                "Conventional weekend — three practice sessions, Qualifying and the Grand Prix.")

    # ---- OVERVIEW ----------------------------------------------------------
    if status == "past":
        ov_kicker, ov_sub = "Race weekend · complete", (
            "The weekend is done — full session results are on the Results page and "
            "the reports on Weekend News.")
    elif status == "live":
        ov_kicker, ov_sub = "Race weekend · live", (
            "The weekend is under way. Results, news and stewards' decisions refresh "
            "every time the site rebuilds.")
    else:
        ov_kicker, ov_sub = "Upcoming round", (
            "Everything known about this round so far. Weekend-specific material fills "
            "in automatically as Formula 1, Pirelli and the FIA publish it.")

    countdown = ""
    if status == "future" and cal.get("race_date"):
        day = datetime.date.fromisoformat(cal["race_date"])
        away = (day - datetime.date.today()).days
        when = f" — {away} days away" if away > 0 else ""
        countdown = (f'<div class="callout"><strong>Race day:</strong> '
                     f'{day.strftime("%A %d %B %Y")}{when}.</div>')

    P["overview"] = dict(
        kicker=ov_kicker,
        title="Weekend Overview",
        sub=ov_sub,
        body=f"""
<div class="stat-row">
  {stat(_fmt(length, "TBC"), "Circuit length", circuit)}
  {stat(_fmt(laps, "TBC"), "Race laps", _fmt(distance, "distance TBC"))}
  {stat(_fmt(first_gp, "New"), "First Grand Prix", "at this venue")}
  {stat("Sprint" if sprint else "Standard", "Format", "6 sprints in 2026" if sprint else "3 practice sessions")}
</div>

{countdown}

<div class="grid cols-2">
  {card("What the circuit demands", f"<p>{ref.get('character', 'Circuit character notes to be added.')}</p>",
        "bi-map", "accent")}
  {card("Weekend format", f"<p>{fmt_line}</p>" + ul([
     f"All session times are shown in <strong>{tz_local}</strong> and <strong>{tz_east}</strong>.",
     "Live weather is attached to each session on the Schedule &amp; Weather page.",
     "Session results appear on the Results page as soon as each session finishes.",
  ]), "bi-calendar-week")}
</div>

<div class="grid cols-2">
  {card("Storylines to prepare", ul_or(ref.get("storylines"), "<p>Storylines will be added as the round approaches.</p>"),
        "bi-broadcast")}
  {card("Overtaking picture", f"<p>{ref.get('overtaking', 'To be confirmed.')}</p>",
        "bi-arrow-left-right")}
</div>

<h2 class="sec">Session times</h2>
<div class="tablewrap"><table class="tbl">
  <thead><tr><th>Session</th><th>Day</th><th>{tz_local}</th><th>{tz_east}</th></tr></thead>
  <tbody>{schedule_rows()}</tbody>
</table></div>
""")

    # ---- CIRCUIT -----------------------------------------------------------
    asset = cal.get("track_asset")
    if asset:
        fig = f"""<figure class="circuit-fig">
  <img src="../assets/{asset}" alt="Official 2026 Formula 1 track map for {circuit} showing turn numbers and sectors"
       class="circuit-img" onclick="zoomImg(this)" title="Click to zoom / full screen">
  <figcaption><strong>Official 2026 {circuit} track map</strong> — turn numbers, sectors and the
  marked overtaking zones. <strong>Click the map to zoom / full screen.</strong>
  <span class="src">Source: Formula1.com 2026 track guide.</span></figcaption>
</figure>"""
    else:
        fig = pending("Official 2026 track map", "with the circuit guide", "bi-image")

    drs = ref.get("drs")
    drs_txt = f"{drs} zone{'s' if drs != 1 else ''}" if drs else "TBC"

    P["circuit"] = dict(
        kicker=f"{_fmt(length, 'Length TBC')} · {_fmt(laps + ' laps' if laps else '', 'laps TBC')}",
        title=f"{circuit} Circuit Guide",
        sub=ref.get("character", "Circuit guide."),
        body=f"""
<h2 class="sec">Circuit map</h2>
{fig}

<div class="stat-row">
  {stat(_fmt(length, "TBC"), "Circuit length")}
  {stat(_fmt(laps, "TBC"), "Race laps")}
  {stat(_fmt(distance, "TBC"), "Race distance")}
  {stat(drs_txt, "Overtaking zones", "DRS / straight mode")}
</div>

<h2 class="sec">Corners that matter</h2>
<div class="grid cols-3">{_corner_cards(ref) or card("Corner guide", "<p>To be added.</p>", "bi-signpost-split")}</div>

<div class="grid cols-2">
  {card("Where the passes happen", f"<p>{ref.get('overtaking', 'To be confirmed.')}</p>",
        "bi-arrow-left-right", "accent")}
  {card("What it does to the tyres", f"<p>{ref.get('tyre_notes', 'To be confirmed.')}</p>",
        "bi-record-circle")}
</div>

<h2 class="sec">Worth knowing</h2>
{card("Circuit notes", ul_or(ref.get("notes")), "bi-info-circle")}

<div class="callout">
  <strong>Lap record:</strong> {_fmt(ref.get("lap_record"), "To be confirmed")}.
  Race-control specifics — track limits, pit-entry definitions and the marked overtaking
  zones — are confirmed in the FIA event documents published on the Thursday of the
  race week; see Commentary Notes for the link.
</div>
""")

    # ---- TYRES -------------------------------------------------------------
    tyre_body = f"""
<div class="grid cols-2">
  {card("What this circuit does to a tyre", f"<p>{ref.get('tyre_notes', 'To be confirmed.')}</p>",
        "bi-record-circle", "accent")}
  {card("Why it matters here", f"<p>{ref.get('overtaking', '')}</p>"
        "<p>Where passing is hard, strategy and the undercut decide the race; where it is easy, "
        "teams can afford to run longer and recover track position on merit.</p>",
        "bi-diagram-3")}
</div>

{pending("Pirelli's compound allocation and tyre-set breakdown", "about two weeks before the race")}
{pending("Long-run degradation data", "after Friday practice", "bi-graph-down")}
"""
    P["tyres"] = dict(
        kicker="Pirelli · strategy",
        title="Tyres & Strategy",
        sub="Compound allocation, degradation and the strategic shape of the race.",
        body=tyre_body)

    # ---- ROOKIES -----------------------------------------------------------
    P["rookies"] = dict(
        kicker="Line-ups",
        title="Rookies & Line-ups",
        sub="Mandatory rookie practice outings and any driver changes for this round.",
        body=f"""
{card("The rookie rule", ul([
   "Every team must field a rookie driver in <strong>two FP1 sessions per car</strong> across the season "
   "— four rookie outings per team in total.",
   "A 'rookie' is a driver who has started no more than two World Championship Grands Prix.",
   "Teams announce their choices in the days before the event; late changes do happen.",
   "Rookie running costs the race driver a full practice session, which matters most at "
   + ("a sprint weekend like this one, where there is only one hour of practice to begin with."
      if sprint else "circuits where track time is at a premium."),
]), "bi-person-badge", "accent")}

{pending("Rookie FP1 line-ups for this round", "in the week before the event")}
{pending("Reserve or replacement driver changes", "as teams confirm them", "bi-people")}
""")

    # ---- STANDINGS ---------------------------------------------------------
    st = ctx.get("standings") or {}
    if st.get("drivers"):
        standings_body = f"""
<div class="callout"><strong>Standings as of {st.get('as_of', 'the most recent completed round')}.</strong>
  These refresh as each subsequent race is built into the hub.</div>

<div class="grid cols-2">
  <div>
    <h2 class="sec">Drivers</h2>
    <div class="tablewrap"><table class="tbl">
      <thead><tr><th>Pos</th><th>Driver</th><th>Team</th><th>Pts</th></tr></thead>
      <tbody>{st['drivers']}</tbody>
    </table></div>
  </div>
  <div>
    <h2 class="sec">Constructors</h2>
    <div class="tablewrap"><table class="tbl">
      <thead><tr><th>Pos</th><th>Team</th><th>Pts</th></tr></thead>
      <tbody>{st.get('ctors', '')}</tbody>
    </table></div>
  </div>
</div>
"""
    else:
        standings_body = pending("Championship standings", "after the most recent race", "bi-trophy")
    P["standings"] = dict(
        kicker="Championship",
        title="Championship & Form",
        sub="Where the title fight stands going into this round.",
        body=standings_body)

    # ---- TEAMS -------------------------------------------------------------
    P["teams"] = dict(
        kicker="Team watch",
        title="Team Watch & News",
        sub="Team-by-team storylines for the weekend.",
        body=f"""
{card("What to watch for here", ul_or(ref.get("storylines")),
      "bi-people", "accent")}

{pending("Team-by-team weekend storylines", "in the week before the race")}

<div class="callout">
  Weekend news from Formula1.com and The Race is collected automatically on the
  <strong>Weekend News</strong> page as soon as it is published, split into general
  stories and reports for each completed session.
</div>
""")

    # ---- UPGRADES ----------------------------------------------------------
    P["upgrades"] = dict(
        kicker="Development",
        title="Car Development & Upgrades",
        sub="Upgrade packages brought to this round, from the FIA's car presentation submissions.",
        body=f"""
{card("How this page gets filled", ul([
   "Teams must submit a <strong>car presentation</strong> to the FIA listing every changed component "
   "and the reason for the change.",
   "That document is published in the FIA event documents, normally on the <strong>Friday</strong> of the race week.",
   "Each entry gives the component, the geometric change and the intended performance effect — "
   "the most reliable upgrade source there is.",
   "Circuit-specific packages are common at " + circuit + "; general performance upgrades appear anywhere.",
]), "bi-tools", "accent")}

{pending("FIA car presentation submissions for this round", "on the Friday of the race week")}
""")

    # ---- POWER UNIT --------------------------------------------------------
    P["powerunit"] = dict(
        kicker="2026 Rules",
        title="Power Unit & Override",
        sub="The 2026 power unit and the per-event energy map that replaces DRS.",
        body=f"""
<div class="callout">
  In 2026 the electrical side of the power unit is far larger and DRS is replaced by a
  battery-boost <strong>Manual Override</strong>. The FIA publishes a power and energy map
  for every individual event — that is where the numbers below come from once it is issued.
</div>

<div class="grid cols-2">
  {card("What changed for 2026", ul([
     "Roughly a <strong>50/50 split</strong> between internal combustion and electrical power.",
     "The <strong>MGU-H is gone</strong>; the MGU-K is substantially more powerful.",
     "<strong>100% sustainable fuel</strong>.",
     "<strong>Manual Override</strong> replaces DRS as the overtaking aid — a defined extra "
     "energy allocation the chasing driver can deploy.",
     "<strong>Active aerodynamics</strong> let the cars switch between a high-downforce and a "
     "low-drag straight-line mode.",
  ]), "bi-lightning-charge", "accent")}

  {card("What to look for at this circuit", ul([
     "Deployment matters most where the full-throttle run is longest — "
     + ("a long lap like this one puts a premium on efficient energy management."
        if _km(length) >= 5.4 else
        "watch the longest straight for where the override is worth the most."),
     "Energy-rich layouts let drivers deploy more freely; energy-limited ones force lifting and coasting.",
     "The override detection and activation points are defined per circuit in the FIA document.",
     "Practice and qualifying generally run a more permissive power curve than the race — "
     "expect Sunday straight-line speed to look weaker than Saturday's.",
  ]), "bi-battery-charging")}
</div>

{pending("The FIA power-unit and energy-map document for this event",
         "with the event documents in the race week")}
""")

    # ---- FACTS -------------------------------------------------------------
    P["facts"] = dict(
        kicker="Stats",
        title="Facts, Stats & Records",
        sub=f"Reference numbers and history for {circuit}.",
        body=f"""
<div class="stat-row">
  {stat(_fmt(length, "TBC"), "Circuit length")}
  {stat(_fmt(laps, "TBC"), "Race laps")}
  {stat(_fmt(distance, "TBC"), "Race distance")}
  {stat(_fmt(first_gp, "New"), "First Grand Prix")}
</div>

<div class="grid cols-2">
  {card("Lap record", f'<p><strong>{_fmt(ref.get("lap_record"), "To be confirmed")}</strong></p>'
        "<p>Official race lap records only count laps set during the Grand Prix itself.</p>",
        "bi-stopwatch", "accent")}
  {card("Circuit notes", ul_or(ref.get("notes")), "bi-journal-text")}
</div>

{pending("Past winners, polesitters and weekend-specific trivia",
         "in the official preview material for the round", "bi-bar-chart")}
""")

    # ---- MOMENTS -----------------------------------------------------------
    P["moments"] = dict(
        kicker="History",
        title="Great Moments",
        sub=f"Memorable races and moments at {circuit}.",
        body=f"""
{card("History in brief", ul_or(
   ([f"First Grand Prix at this venue: <strong>{first_gp}</strong>."] if first_gp else [])
   + ref.get("notes", [])), "bi-stars", "accent")}

{pending("A curated moments list for this venue",
         "in the official preview material for the round", "bi-stars")}
""")

    # ---- SCHEDULE ----------------------------------------------------------
    P["schedule"] = dict(
        kicker="Timing",
        title="Schedule & Weather",
        sub=f"All sessions in {tz_local} and {tz_east}, with the live forecast attached to each.",
        body=f"""
<div class="callout">{fmt_line}</div>

<h2 class="sec">Session times</h2>
<div class="tablewrap"><table class="tbl">
  <thead><tr><th>Session</th><th>Day</th><th>{tz_local}</th><th>{tz_east}</th></tr></thead>
  <tbody>{schedule_rows()}</tbody>
</table></div>

<h2 class="sec">Weather</h2>
{weather_cards()}
""")

    # ---- NOTES -------------------------------------------------------------
    P["notes"] = dict(
        kicker="Cheat sheet",
        title="Commentator's Cheat Sheet",
        sub=f"The short version for {gp} — everything worth having to hand.",
        body=f"""
<div class="grid cols-2">
  {card("The circuit in one paragraph", f"<p>{ref.get('character', 'To be added.')}</p>",
        "bi-mic", "accent")}
  {card("Numbers to have ready", ul([
     f"Circuit length: <strong>{_fmt(length, 'TBC')}</strong>",
     f"Race: <strong>{_fmt(laps, 'TBC')} laps</strong>, {_fmt(distance, 'distance TBC')}",
     f"First Grand Prix here: <strong>{_fmt(first_gp, 'this year')}</strong>",
     f"Lap record: <strong>{_fmt(ref.get('lap_record'), 'TBC')}</strong>",
     f"Format: <strong>{'Sprint weekend' if sprint else 'Standard weekend'}</strong>",
  ]), "bi-list-ol")}
</div>

<div class="grid cols-2">
  {card("Talking points", ul_or(ref.get("storylines")), "bi-chat-quote")}
  {card("Name-check these corners", ul_or(
     [f"<strong>{n}</strong> — {d}" for n, d in ref.get("key_corners", [])]),
     "bi-signpost-split")}
</div>

<div class="callout">
  <strong>Official documents:</strong>
  {f'<a href="{fia_url}" target="_blank" rel="noopener">FIA event documents for this round</a> — '
   "race-control notes, the car presentation submissions, the power-unit map and every "
   "stewards' decision. Published through the race week."
   if fia_url else "FIA event document link to be added."}
</div>

{pending("Session-by-session commentary notes", "as the weekend runs", "bi-mic")}
""")

    return P
