"""Verified carry-over information; local Qatar documents remain source-dependent."""
import content_generic
from content_las_vegas import PEREZ_PENALTY
from f1lib import card


PIRELLI_NOMINATION = "https://press.pirelli.com/tyre-compounds-selected-for-the-final-three-races-of-the-season/"
QATAR_2025_RACE = (
    "https://www.formula1.com/en/latest/article/"
    "verstappen-wins-qatar-gp-as-title-battle-goes-to-abu-dhabi-with-piastri."
    "5KlYT7q8OcrJ7AnMALjkxJ"
)
CAMARA_QATAR_ANNOUNCEMENT = (
    "https://www.formula1.com/en/latest/article/"
    "haas-confirm-camara-will-drive-for-the-team-in-final-races-of-2026."
    "2wYY9ymhyqr7rXcuK6S7bj"
)


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    carryover = f"""<h2 class="sec">Verified Las Vegas carry-over</h2>
<p><strong>Sergio Perez: five-place grid penalty at his next race.</strong>
FIA Las Vegas Document 61 finds him wholly responsible for contact with
Rafael Câmara at Turn 14. Because he retired and could not serve the time
penalty, it becomes a grid drop at the next race in which he participates,
expected to be Qatar. This is not a five-second Qatar penalty.
<a href="{PEREZ_PENALTY}">Original Stewards' ruling, 21 November</a>.</p>
<p>Las Vegas PU penalties for Antonelli, Piastri, Sainz, Stroll and Bearman
belong to that event; do not carry them forward again.
<a href="../las-vegas/powerunit.html">Reviewed Vegas technical and sanction tables</a>.
Qatar's own energy limits, tyre prescriptions and upgrades must come from
Qatar publications, not copied Las Vegas figures. Published source readers
appear on the relevant pages as collection succeeds; discovery failures stay visible.</p>"""
    for slug in ("overview", "notes", "schedule"):
        pages[slug]["body"] = carryover + pages[slug]["body"]
    lineup = card(
        "Haas confirms Rafael Câmara for Qatar and Abu Dhabi",
        f"""<p>Haas confirmed on 22 November that Câmara will drive for the team
at both remaining 2026 Grands Prix, after his race outings in Brazil and Las
Vegas. The announcement also identifies him as a full-time Haas driver for
2027. This confirms Câmara's Qatar participation; it is not a complete FIA
entry list or confirmation of FP1 substitutions.
<a href="{CAMARA_QATAR_ANNOUNCEMENT}">Formula1.com, 22 November</a>.</p>""",
        "bi-person-badge", "accent",
    )
    for slug in ("overview", "rookies", "teams", "notes"):
        pages[slug]["body"] = lineup + pages[slug]["body"]
    nomination = f"""<p>Pirelli nominated <strong>C1 Hard, C2 Medium and C3 Soft</strong>
for Qatar. Its 13 November graphic marks C3 as the qualifying mandatory set
and C1 and C2 as the race mandatory sets. This nomination is not a
driver-by-driver remaining-set inventory; event prescriptions and any 2026
stint limit still require Qatar's own FIA documents.
<a href="{PIRELLI_NOMINATION}">Pirelli compound selection and graphic</a>.</p>"""
    pages["tyres"]["body"] += card("Qatar nomination and mandatory sets", nomination, "bi-record-circle", "accent")
    pages["notes"]["body"] = nomination + pages["notes"]["body"]
    pages["moments"]["body"] = pages["moments"]["body"].replace(
        content_generic.pending(
            "A curated moments list for this venue",
            "in the official preview material for the round", "bi-stars",
        ),
        card(
            "2025: a Safety Car reshapes the title fight",
            f"""<p>With a 25-lap maximum tyre stint imposed for the 2025 race,
Verstappen pitted under the early Safety Car while both McLarens stayed out.
He won ahead of Piastri and Sainz; Norris finished fourth, taking a 12-point
lead over Verstappen into the finale. The 2025 restriction is historical,
not confirmation of a 2026 limit.
<a href="{QATAR_2025_RACE}">Formula1.com race report</a>.</p>""",
            "bi-stars", "accent",
        ),
    )
    return pages
