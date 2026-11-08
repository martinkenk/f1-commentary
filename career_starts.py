"""Source-dated career start rankings and explicitly conditional milestones."""
import argparse
import datetime as dt
from html import escape
import json
from pathlib import Path

import circuit_history as history

ROOT = Path(__file__).resolve().parent
ARTICLE = ("https://www.formula1.com/en/latest/article/"
           "rivals-pay-tribute-as-lewis-hamilton-reaches-400-formula-1-starts-at-sao-paulo-grand-prix."
           "7ahLqNwTWm8Nze2o9hteZB")


def rank(rows, starts):
    return 1 + sum(row["starts"] > starts for row in rows)


def milestone(row, rows, active, races_per_year):
    higher = [other for other in rows if other["starts"] > row["starts"]]
    if not higher:
        return "Already leads this source snapshot."
    target = min(higher, key=lambda other: (other["starts"], other["name"]))
    extra = target["starts"] - row["starts"] + 1
    if target["id"] in active:
        return (f"{extra} more starts than {target['name']} to pass: no catch if both "
                "start every race. A retirement or missed starts would be required.")
    return (f"{extra} further starts to pass {target['name']}'s fixed {target['starts']} "
            f"({extra / races_per_year:.1f} seasons at {races_per_year} GPs/year). "
            "Assumes that rival's total stays fixed and every future race is started.")


def snapshot(data, source, grid, year):
    participants = {row["driverId"] for row in data["seasons-drivers"] if row["year"] == year}
    current = []
    missing = []
    header = grid["headers"].index("Driver")
    for row in grid["rows"]:
        code = row[header][-3:]
        matches = [driver for driver in data["drivers"]
                   if driver["id"] in participants and driver["abbreviation"] == code]
        if not matches:
            identity = "grid-" + code
            current.append(identity)
            missing.append({"id": identity, "name": row[header][:-4], "starts": None})
            continue
        if len(matches) != 1:
            raise ValueError(f"Cannot identify current entrant {row[header]}")
        current.append(matches[0]["id"])
    if len(current) != len(set(current)) or len(current) != 22:
        raise ValueError("Expected the complete unique 22-driver Brazil race grid")
    rows = []
    for driver in data["drivers"]:
        value = driver["totalRaceStarts"]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"Invalid career starts for {driver['id']}")
        if value or driver["id"] in current:
            rows.append({"id": driver["id"], "name": driver["name"], "starts": value})
    last = max(row["date"] for row in data["races"] if any(
        result["raceId"] == row["id"] for result in data["races-race-results"]))
    if last != "2026-11-01":
        raise ValueError("The Brazil milestone requires the pre-Brazil, through-Mexico snapshot")
    source = dict(source, modifications="Career-start totals retained; ranked and combined "
                  "with Brazil grid identities and conditional passing projections.")
    return {"checked_at": dt.datetime.now(history.UTC).isoformat(), "source": source,
            "through_date": last, "current_grid_source": grid["source_url"],
            "current_grid": current, "drivers": rows, "missing_totals": missing}


def render(ctx, root=ROOT):
    path = Path(root) / "data/career_starts_2026.json"
    value = json.loads(path.read_text())
    rows = sorted(value["drivers"], key=lambda row: (-row["starts"], row["name"]))
    active = set(value["current_grid"])
    calendar = json.loads((Path(root) / "data/calendar_2026.json").read_text())
    races_per_year = len(calendar["events"])
    selected = [row for row in rows if rank(rows, row["starts"]) <= 30 or row["id"] in active]
    table = []
    for row in selected:
        current = row["id"] in active
        name = escape(row["name"]) + (" <strong>(Brazil grid)</strong>" if current else "")
        projection = escape(milestone(row, rows, active, races_per_year)) if current else "Fixed historical comparison"
        table.append(f'<tr><td class="pos">{rank(rows, row["starts"])}</td><td class="drv">{name}</td>'
                     f'<td class="num">{row["starts"]}</td><td>{projection}</td></tr>')
    for row in value["missing_totals"]:
        table.append(f'<tr><td>Unranked</td><td class="drv">{escape(row["name"])} '
                     '<strong>(Brazil grid)</strong></td><td>Not verified</td>'
                     '<td>Absent from this F1DB release; no invented zero or projection.</td></tr>')
    return f"""<section id="career-starts">
<h2 class="sec">Hamilton's 400th Grand Prix: endurance at the top</h2>
<p>Formula1.com's 8 November feature identifies Sao Paulo as Lewis Hamilton's
<strong>400th F1 start</strong>: 20 uninterrupted seasons since his 2007 McLaren
debut, seven world titles, and competitive pace still demonstrated by his Mexico
pole the previous weekend. Those achievements describe longevity and performance,
not a forecast of his Brazil result. Former teammate Fernando Alonso welcomes
him to the 400-start club; Antonelli and Russell point to his sustained motivation.
<a href="{ARTICLE}">Official F1 milestone feature and rivals' tributes</a>.</p>
<p><strong>Source-date caveat:</strong> the ranking below is F1DB {escape(value['source']['release'])},
through {escape(value['through_date'])}, <strong>before Brazil</strong>. Hamilton
has 399 starts in that snapshot; Brazil is the reported 400th, not added to the
historical table before a classification. F1 calls Brazil Alonso's 445th start,
while this F1DB snapshot already records 445 through Mexico: a one-start
source disagreement remains explicit, not silently adjusted.</p>
<h3>Most Grand Prix starts: top 30 ranks plus every Brazil entrant</h3>
<p>Race starts, not entries, qualifying appearances or sprints. Drivers on the
current Brazil race grid are highlighted, including replacements. Ties share
rank. Projections are required starts to <strong>pass</strong>, not merely tie;
{races_per_year} Grands Prix/year is this calendar's illustrative rate, not a
future calendar or contract prediction. Active rivals' totals also increase.</p>
<div class="table-wrap"><table class="data compact">
<thead><tr><th>Rank</th><th>Driver</th><th>Career starts</th><th>What would move a current driver up?</th></tr></thead>
<tbody>{''.join(table)}</tbody></table></div>
<p class="src">Derived from <a href="{escape(value['source']['release_url'], quote=True)}">F1DB release</a>,
<a href="{escape(value['source']['checksum_url'], quote=True)}">verified SHA-256 archive</a>;
<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.
Totals retained from F1DB; ranking and conditional projections calculated here.
Current entrants: <a href="{escape(value['current_grid_source'], quote=True)}">official Brazil grid</a>.
Source cutoff is not today's date. <a href="{ARTICLE}">F1's independently dated milestone account</a>.</p></section>"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, required=True)
    args = parser.parse_args()
    release = history._release(args.cache_dir, dt.datetime.now(history.UTC))
    data, source = history._database(release, args.cache_dir)
    sessions = json.loads((ROOT / "data/brazil/session_results.json").read_text())["sessions"]
    grid = next(item for item in sessions if item["label"] == "Starting Grid")
    history._write(ROOT / "data/career_starts_2026.json", snapshot(data, source, grid, 2026))
