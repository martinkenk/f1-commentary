"""Championship standings: structured data plus the table renderers.

The standings used to live as pre-baked HTML strings, which meant the markup
could not carry anything derived — team colours, points gaps, leader deltas.
Keeping the numbers as data and generating the rows lets the tables show the
gaps a commentator actually reads out, and keeps the driver and constructor
tables consistent with each other.

Update ``DRIVERS`` / ``CONSTRUCTORS`` after a race; everything else follows.
"""

# Official-ish 2026 team colours, used for the left rail on each row.
TEAM_COLOURS = {
    "Mercedes": "#27f4d2",
    "Ferrari": "#e8002d",
    "McLaren": "#ff8000",
    "Red Bull Racing": "#3671c6",
    "Alpine": "#00a1e8",
    "Racing Bulls": "#6692ff",
    "Haas F1 Team": "#b6babd",
    "Williams": "#1868db",
    "Audi": "#00e701",
    "Aston Martin": "#229971",
    "Cadillac": "#c8b273",
}

# (position, driver, three-letter code, team, points)
DRIVERS = [
    (1, "Kimi Antonelli", "ANT", "Mercedes", 204),
    (2, "Lewis Hamilton", "HAM", "Ferrari", 159),
    (3, "George Russell", "RUS", "Mercedes", 154),
    (4, "Charles Leclerc", "LEC", "Ferrari", 126),
    (5, "Lando Norris", "NOR", "McLaren", 103),
    (6, "Oscar Piastri", "PIA", "McLaren", 92),
    (7, "Max Verstappen", "VER", "Red Bull Racing", 91),
    (8, "Isack Hadjar", "HAD", "Red Bull Racing", 60),
    (9, "Pierre Gasly", "GAS", "Alpine", 42),
    (10, "Liam Lawson", "LAW", "Racing Bulls", 39),
    (11, "Arvid Lindblad", "LIN", "Racing Bulls", 22),
    (12, "Franco Colapinto", "COL", "Alpine", 19),
    (13, "Oliver Bearman", "BEA", "Haas F1 Team", 18),
    (14, "Gabriel Bortoleto", "BOR", "Audi", 10),
    (15, "Carlos Sainz", "SAI", "Williams", 6),
    (16, "Alexander Albon", "ALB", "Williams", 5),
    (17, "Esteban Ocon", "OCO", "Haas F1 Team", 3),
    (18, "Fernando Alonso", "ALO", "Aston Martin", 1),
    (19, "Nico Hulkenberg", "HUL", "Audi", 0),
    (20, "Valtteri Bottas", "BOT", "Cadillac", 0),
    (21, "Sergio Perez", "PER", "Cadillac", 0),
    (22, "Lance Stroll", "STR", "Aston Martin", 0),
]

# (position, team, points)
CONSTRUCTORS = [
    (1, "Mercedes", 358),
    (2, "Ferrari", 285),
    (3, "McLaren", 195),
    (4, "Red Bull Racing", 151),
    (5, "Alpine", 61),
    (6, "Racing Bulls", 61),
    (7, "Haas F1 Team", 21),
    (8, "Williams", 11),
    (9, "Audi", 10),
    (10, "Aston Martin", 1),
    (11, "Cadillac", 0),
]


def _rail(team):
    """Inline custom property consumed by `tr[data-team] td.pos`."""
    colour = TEAM_COLOURS.get(team)
    return f' data-team="{team}" style="--team:{colour}"' if colour else ""


def _gap_label(pts, leader, ahead_pts, ahead_pos):
    """Sub-label under a points figure: deficit to the leader and to the car ahead.

    This is the number most often wanted mid-broadcast and it is tedious to work
    out live, so it is precomputed rather than left as mental arithmetic.
    """
    if ahead_pts is None:
        return '<span class="pts-gap">championship leader</span>'
    if pts == 0:
        # A chain of "level with P20 / level with P21" down the bottom of the
        # table says nothing; the fact worth stating is that they are yet to score.
        return '<span class="pts-gap">yet to score</span>'
    if ahead_pts == pts:
        return f'<span class="pts-gap">level with P{ahead_pos}</span>'
    to_leader = leader - pts
    to_ahead = ahead_pts - pts
    # For P2 the leader and the car ahead are the same, so showing both reads
    # as "−45 to P1 · −45 to P1".
    if ahead_pos == 1:
        return f'<span class="pts-gap">−{to_leader} to P1</span>'
    return (f'<span class="pts-gap">−{to_leader} to P1 · '
            f'−{to_ahead} to P{ahead_pos}</span>')


def driver_rows():
    """<tr> markup for the drivers' championship."""
    leader = DRIVERS[0][4]
    out = []
    for i, (pos, name, code, team, pts) in enumerate(DRIVERS):
        ahead_pts = DRIVERS[i - 1][4] if i else None
        ahead_pos = DRIVERS[i - 1][0] if i else None
        gap = _gap_label(pts, leader, ahead_pts, ahead_pos)
        out.append(
            f'      <tr{_rail(team)}><td class="pos">{pos}</td>'
            f'<td class="drv">{name} <span class="drv-code">{code}</span></td>'
            f'<td class="team">{team}</td>'
            f'<td class="pts">{pts}{gap}</td></tr>')
    return "\n".join(out)


def ctor_rows():
    """<tr> markup for the constructors' championship."""
    leader = CONSTRUCTORS[0][2]
    out = []
    for i, (pos, team, pts) in enumerate(CONSTRUCTORS):
        ahead_pts = CONSTRUCTORS[i - 1][2] if i else None
        ahead_pos = CONSTRUCTORS[i - 1][0] if i else None
        gap = _gap_label(pts, leader, ahead_pts, ahead_pos)
        out.append(
            f'      <tr{_rail(team)}><td class="pos">{pos}</td>'
            f'<td class="drv">{team}</td>'
            f'<td class="pts">{pts}{gap}</td></tr>')
    return "\n".join(out)


DRIVER_ROWS = driver_rows()
CTOR_ROWS = ctor_rows()
