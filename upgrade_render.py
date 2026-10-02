"""Render reviewed team declarations with page-specific inline document readers."""
from html import escape

from f1lib import card, stat, ul


def render_submissions(submissions, *, source_url, asset_prefix, document, event, issued):
    rows, teams = [], []
    for team, page, updates in submissions:
        team = escape(team)
        areas = ", ".join(escape(component) for component, _, _ in updates) or "No updates submitted"
        rows.append(
            f'<tr><td>{team}</td><td class="num">{len(updates)}</td><td>{areas}</td>'
            f'<td><a href="#upgrade-submission-{page}" data-document-reader '
            f'data-reader-title="{team} - {escape(document)}" '
            f'aria-label="Read {team} submission, FIA page {page}">Read page {page}</a></td></tr>')
        evidence = []
        for source_page in ([page, page + 1] if updates else [page]):
            label = ("component-location diagram" if source_page != page else
                     "component declaration" if updates else "nil-return declaration")
            evidence.append(
                '<figure class="circuit-fig">'
                f'<img src="../assets/{escape(asset_prefix)}-p{source_page}.png" '
                f'alt="{team} {escape(event)} {label}, {escape(document)} page {source_page}" '
                'class="circuit-img" loading="lazy" onclick="zoomImg(this)" '
                'title="Click to zoom / full screen">'
                f'<figcaption>{team}: {label}. <a href="{escape(source_url)}#page={source_page}" '
                f'target="_blank" rel="noopener">{escape(document)}, page {source_page}</a>, '
                f'{escape(issued)}. Click to zoom / full screen.</figcaption></figure>')
        description = ul([
            f"<strong>{escape(component)}:</strong> {escape(summary)} "
            f"<em>Filed reason: {escape(reason)}.</em>"
            for component, reason, summary in updates
        ]) if updates else "<p>No updates submitted for this event.</p>"
        teams.append(card(
            f'{team} &mdash; {len(updates)} declared item{"s" if len(updates) != 1 else ""}',
            description + f'<details id="upgrade-submission-{page}"><summary>View official declaration'
            + (" and diagram" if updates else "") + "</summary>"
            + "".join(evidence) + "</details>", "bi-tools", "accent" if updates else ""))
    total = sum(len(updates) for _, _, updates in submissions)
    updated = sum(bool(updates) for _, _, updates in submissions)
    return f"""
<div class="stat-row">
  {stat(str(total), "Declared items", escape(document))}
  {stat(str(updated), "Teams with updates", f"of {len(submissions)} teams")}
  {stat(str(len(submissions) - updated), "Nil returns", "explicit no-update submissions")}
</div>
<p class="src">Source: <a href="{escape(source_url)}" target="_blank" rel="noopener">
{escape(document)}, Car Presentation Submissions</a>, issued {escape(issued)}.
All eleven teams are included. Counts refer to declared component rows, not a
ranking of performance gains or confirmation that both cars raced every item.</p>
<h2 class="sec">Team-by-team car presentation submissions</h2>
<p>Choose <strong>Read page</strong> to view the team's official declaration here,
with its diagram where supplied. The reader supports zoom and keeps the original
PDF available as a separate source link.</p>
<div class="table-wrap"><table class="data">
  <thead><tr><th>Team</th><th class="num">Items</th><th>Declared areas</th><th>FIA source</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table></div>
<h2 class="sec">What changed and why</h2>
<p>The explanations below summarise each team's stated rationale, not independently
measured lap-time gains. A nil return means no updates submitted for this event;
it does not rule out setup changes or previously introduced parts.</p>
<div class="grid cols-2">{"".join(teams)}</div>
"""
