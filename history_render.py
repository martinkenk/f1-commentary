"""Offline, attributed circuit record books shared by every GP page."""
import html
import urllib.parse

import circuit_history
from f1lib import card, stat


PAGES = {"overview", "circuit", "facts", "h2h"}


def _e(value):
    return html.escape(str(value))


def _link(url, label):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc:
        return _e(label)
    return f'<a href="{_e(url)}" target="_blank" rel="noopener">{_e(label)}</a>'


def ordinal(number):
    suffix = "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def _years(values):
    return ", ".join(str(value) for value in values) or "None"


def _table(headers, rows, *, filterable=False, table_id=""):
    def cell(value):
        if isinstance(value, tuple):
            text, sort_key = value
            return f'<td data-sort="{_e(sort_key)}">{text}</td>'
        return f"<td>{value}</td>"

    classes = "data compact" + (" filterable" if filterable else "")
    identity = f' id="{_e(table_id)}"' if table_id else ""
    return (f'<div class="table-wrap"><table class="{classes}"{identity}><thead><tr>'
            + "".join(f'<th scope="col">{_e(header)}</th>' for header in headers)
            + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(cell(value) for value in row) + "</tr>" for row in rows)
            + "</tbody></table></div>")


def _credit(record, ctx):
    source = record.get("source", {})
    release = source.get("release", "release")
    return (
        '<p class="src">Derived from '
        + _link(source.get("release_url", "https://github.com/f1db/f1db/releases"), f"F1DB {release}")
        + " &middot; "
        + _link("https://creativecommons.org/licenses/by/4.0/", "CC BY 4.0")
        + f'. World Championship Grands Prix before {_e(ctx["race_date"])}; '
        'this weekend and sprints excluded. Venue totals combine all F1DB layouts '
        'of this circuit. GP editions follow F1DB identities: some renamed titles share '
        'one historical series. These are pre-weekend records, not live all-time totals.'
        + (f' Source last checked {_e(record["checked_at"])}.' if record.get("checked_at") else "")
        + '</p>'
    )


def _edition(profile, ctx):
    gp = profile["grand_prix"]
    verb = "was" if ctx.get("status") == "past" else "is scheduled to be"
    return (
        f'The {_e(ctx["year"])} event {verb} the <strong>{ordinal(profile["venue_edition"])} '
        f'World Championship Grand Prix at this venue</strong> and the '
        f'<strong>{ordinal(gp["edition"])} {_e(gp["name"])} across all venues</strong>.'
    )


def _leader_card(profile, key, rows_key, title):
    leaders = [row for row in profile[rows_key] if row["id"] in profile[key]]
    if not leaders:
        return card(title, "<p>No previous Grand Prix winners at this venue.</p>", "bi-trophy")
    body = "<ul>" + "".join(
        f'<li><strong>{_e(row["name"])}</strong>: {_e(row["wins"])} wins'
        f'<span class="history-years">{_e(_years(row["win_years"]))}</span></li>'
        for row in leaders
    ) + "</ul>"
    return card(title, body, "bi-trophy", "accent")


def _summary(profile, ctx):
    breakdown = _table(["Grand Prix name / series at this venue", "Completed editions", "Years"], [
        [_e(row["name"]), _e(row["count"]), _e(_years(row["years"]))]
        for row in profile["names_at_venue"]
    ]) if profile["names_at_venue"] else (
        '<div class="callout watch">A debut venue: no earlier World Championship Grands Prix '
        'before this weekend. Other circuits in the same country are not this track.</div>'
    )
    gp = profile["grand_prix"]
    first, last = profile.get("first_race"), profile.get("last_race")
    range_note = (
        '<p class="history-note">First race here: '
        + _link(first["url"], f'{first["year"]} {first["name"]}')
        + ". Most recent before this weekend: "
        + _link(last["url"], f'{last["year"]} {last["name"]}') + ".</p>"
        if first and last else ""
    )
    pole = profile.get("wins_from_pole", {"wins": 0, "races": 0})
    pole_stat = (stat(f'{pole["wins"]} / {pole["races"]}', "Wins from pole",
                      "races with a known official polesitter") if pole["races"] else "")
    venues = profile["grand_prix"].get("venues", [])
    gp_venues = (
        '<details><summary>Where this named Grand Prix has been held</summary>'
        + _table(["Venue", "Completed editions", "Years"], [
            [_e(row["name"]), _e(row["count"]), _e(_years(row["years"]))]
            for row in venues
        ]) + '<p class="history-note">F1DB event identities can group renamed titles '
        '(for example Mexican/Mexico City). This is a championship '
        'series count, not a literal sponsor-title count.</p></details>'
        if len(venues) > 1 else ""
    )
    return (
        '<h2 class="sec">Circuit history &amp; Grand Prix editions</h2>'
        f'<p class="history-note"><strong>Pre-weekend record book:</strong> results before '
        f'{_e(ctx["race_date"])}. This event&rsquo;s result is not included.</p>'
        f'<p class="lead-note">{_edition(profile, ctx)}</p>'
        '<div class="stat-row">'
        + stat(str(profile["completed_races"]), "Previous races here", "all Grand Prix names")
        + stat(str(gp["completed_races"]), "Previous GP-series editions", "across all venues")
        + stat(str(len([row for row in profile["drivers"] if row["wins"]])), "Different winning drivers",
               "before this weekend")
        + pole_stat + "</div>" + range_note + breakdown + gp_venues
        + '<div class="history-records">'
        + _leader_card(profile, "most_driver_wins", "drivers", "Most driver wins here")
        + _leader_card(profile, "most_constructor_wins", "constructors", "Most constructor wins here")
        + "</div>"
    )


def _driver_table(drivers, table_id):
    rows = []
    for driver in drivers:
        code = (f' <span class="drv-code">{_e(driver["code"])}</span>'
                if driver.get("code") else "")
        best = driver["best_finish"]
        finish = (f'P{_e(best)}<span class="history-years">{_e(_years(driver["best_years"]))}</span>'
                  if best is not None else
                  "No previous start" if not driver["starts"] else "No classified finish")
        rows.append([
            f'<strong>{_e(driver["name"])}</strong>{code}',
            _e(driver["starts"]), _e(driver["wins"]), _e(driver["podiums"]),
            _e(driver["poles"]), (finish, best if best is not None else ""),
        ])
    return _table(["Driver", "Starts", "Wins", "Podiums", "Poles", "Best classified finish"],
                  rows, filterable=True, table_id=table_id)


def _records(profile, ctx):
    current = [row for row in profile["drivers"] if row["season_driver"]]
    drivers = (
        '<h2 class="sec" id="driver-track-records">Driver track records</h2>'
        f'<p>Venue records before {_e(ctx["race_date"])}. {_e(ctx["year"])} season drivers, '
        'including replacements; not a prediction of this '
        'event&rsquo;s confirmed line-up. Records follow the driver across teams. '
        'Filter by name or select driver chips to compare.</p>'
        + _driver_table(current, "history-season-drivers")
        + '<details><summary>All drivers with a previous race start at this circuit</summary>'
        + _driver_table([row for row in profile["drivers"] if row["starts"]],
                        "history-all-drivers")
        + '</details><p class="history-note">A numeric classified result can include a late '
        'retirement. No previous start and no classified finish are different. Official poles '
        'are not necessarily qualifying P1 or starting-grid P1 in every era; shared result '
        'credits remain with each credited driver.</p>'
    )
    constructors = (
        '<details><summary>Constructor record book</summary>'
        + _table(["Constructor", "Car starts", "Wins", "Podiums", "Poles"], [
            [_e(row["name"]), _e(row["starts"]), _e(row["wins"]), _e(row["podiums"]), _e(row["poles"])]
            for row in profile["constructors"]
        ], filterable=True)
        + '<p class="history-note">F1DB constructor identities are retained; predecessor and '
        'successor brands are not silently merged. Driver wins do not belong to their current '
        'team when achieved with another constructor.</p></details>'
    )
    return drivers + constructors


def _recent_winners(profile):
    if not profile.get("recent_winners"):
        return ""
    return (
        '<h2 class="sec">Recent winners &amp; starting positions</h2>'
        '<p>The most recent completed editions before this weekend. Starting grid is race '
        'context, not qualifying position. Shared winners retain their individual credits.</p>'
        + _table(["Edition / source", "Winner", "Constructor", "Started", "Official pole"], [
            [
                _link(row["url"], f'{row["year"]} {row["name"]}'),
                _e(row["driver"]), _e(row["constructor"]),
                (f'P{row["grid"]}' if isinstance(row["grid"], int) and row["grid"] > 0
                 else "Not recorded" if row["grid"] is None else _e(row["grid"])),
                "Yes" if row["pole"] else "No",
            ]
            for row in profile["recent_winners"]
        ])
    )


def _methodology(record):
    source = record.get("source", {})
    return (
        '<details><summary>Source provenance &amp; counting rules</summary>'
        '<p>Source release published ' + _e(source.get("published_at", "date unavailable")) + ". "
        + _link(source.get("download_url", "https://github.com/f1db/f1db/releases"),
                "Download the source dataset")
        + " &middot; "
        + _link(source.get("checksum_url", "https://github.com/f1db/f1db/releases"),
                "Published SHA-256 checksums")
        + ".</p><ul>"
        + "".join(f"<li>{_e(rule)}</li>" for rule in record.get("methodology", []))
        + "</ul></details>"
    )


def _teammates(profile):
    history = profile["teammates"]
    current_drivers = {driver["id"] for driver in profile["drivers"] if driver["season_driver"]}
    pairs = [pair for pair in history["pairs"]
             if any(driver["id"] in current_drivers for driver in pair["drivers"])]
    out = ['<h2 class="sec">Previous teammate battles at this circuit</h2>']
    out.append(
        f'<p>Up to the last {_e(history["limit"])} completed venue Grands Prix before this weekend; '
        f'{_e(history["races"])} editions in scope. Actual teammates for each edition, '
        'not today&rsquo;s line-up projected into the past. Only pairings with at least one '
        'driver on the current-season roster are shown; former teammates can still appear. '
        'Qualifying uses its own '
        'classification, not the race grid. Scorelines show who placed ahead, not pure pace.</p>'
    )
    if not pairs:
        out.append('<div class="callout watch">No comparable previous teammate pairings involving '
                   'a current-season driver in this scope.</div>')
    else:
        rows = []
        for pair in pairs:
            a, b = pair["drivers"]
            cells = [_e(pair["team"]), f'{_e(a["name"])} / {_e(b["name"])}']
            for session in ("Qualifying", "Race"):
                tally = pair[session]
                cells.append(f'<strong>{tally["wins"][0]} &ndash; {tally["wins"][1]}</strong>'
                             f'<span class="history-years">{tally["excluded"]} excluded</span>')
            rows.append(cells)
        out.append(_table(["Constructor", "Driver A / Driver B", "Qualifying A-B", "Race A-B"],
                          rows, filterable=True, table_id="history-teammates"))
        out.append('<details><summary>Per-edition results and exclusions</summary>')
        for pair in pairs:
            a, b = pair["drivers"]
            out.append(f'<h3>{_e(pair["team"])}: {_e(a["name"])} / {_e(b["name"])}</h3>')
            evidence = []
            for event in pair["events"]:
                cells = [_link(event["url"], f'{event["year"]} {event["name"]}')]
                for session in ("Qualifying", "Race"):
                    detail = event.get(session)
                    if not detail:
                        cells.append("Not available")
                        continue
                    positions = " / ".join(str(position) if position is not None else "-"
                                           for position in detail.get("raw_positions", detail["positions"]))
                    states = " / ".join(detail["statuses"])
                    cells.append(_e(positions) + f'<span class="history-years">{_e(states)}</span>'
                                 + (f'<span class="history-years">{_e(detail["reason"])}</span>'
                                    if detail.get("reason") else ""))
                evidence.append(cells)
            out.append(_table(["Edition", "Qualifying A / B", "Race A / B"], evidence))
        out.append("</details>")
    visible_events = {(pair["team"], event["race_id"]) for pair in pairs for event in pair["events"]}
    excluded = [event for event in history.get("excluded_events", [])
                if (event["team"], event["race_id"]) in visible_events]
    if excluded:
        out.append('<details><summary>Unpaired / shared-drive / multi-entry exclusions</summary><ul>')
        for event in excluded:
            out.append(f'<li>{_e(event["year"])} &middot; {_e(event["team"])}: '
                       f'{_e(event["reason"])} (race {_e(event["race_id"])}).</li>')
        out.append("</ul></details>")
    out.append('<p class="history-note">DNS, DSQ, missing/no-time qualifying and incomparable '
               'results are excluded. A classified driver beats an unclassified teammate; '
               'two unclassified drivers are not assigned a winner. Shared drives and '
               'multi-entry teams are not forced into modern two-car comparisons.</p>')
    return "".join(out)


def render(ctx, page):
    if page not in PAGES or not ctx.get("race_date"):
        return ""
    record = circuit_history.context(ctx)
    profile = record.get("profile")
    error = record.get("error")
    warning = (f'<div class="callout watch"><strong>Circuit-history source notice.</strong> {_e(error)}</div>'
               if error else "")
    if not profile:
        return ('<section class="circuit-history" id="circuit-history">' + warning
                + '<p>Historical circuit records are unavailable in this snapshot. '
                'Missing data is not evidence that this is a debut venue.</p></section>')
    if page == "overview":
        body = ('<div class="callout"><strong>Venue &amp; event:</strong> '
                + _edition(profile, ctx)
                + ' <a href="circuit.html#circuit-history">Name changes &amp; records</a>.</div>')
    elif page == "h2h":
        body = _teammates(profile)
    else:
        body = _summary(profile, ctx)
        if page == "facts":
            body += _records(profile, ctx) + _recent_winners(profile) + _methodology(record)
        body += ('<nav class="history-links" aria-label="Circuit record book">'
                 '<a href="facts.html#driver-track-records">Driver best finishes &amp; full record book</a>'
                 '<a href="h2h.html#circuit-history">Historical teammate comparisons</a></nav>')
    return ('<section class="circuit-history" id="circuit-history">'
            + warning + body + _credit(record, ctx) + "</section>")
