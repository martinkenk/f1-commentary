"""Verified carry-over information; local Qatar documents remain source-dependent."""
import content_generic
from content_las_vegas import PEREZ_PENALTY


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
    return pages
