"""Verified carry-over information; local Qatar documents remain source-dependent."""
import content_generic
from content_las_vegas import PEREZ_PENALTY
from f1lib import card


PIRELLI_NOMINATION = "https://press.pirelli.com/tyre-compounds-selected-for-the-final-three-races-of-the-season/"
PIRELLI_TYRE_LIMIT = "https://press.pirelli.com/in-qatar-with-the-hardest-tyre-compounds-in-the-range/"
QATAR_TYRE_LIMIT = (
    "https://www.motorsport.com/f1/news/pirelli-introduces-stint-limit-for-f1-qatar-gp-but-increases-total-from-2025/10875950/"
)
QATAR_TYRE_STRATEGY = "https://coffeecornermotorsport.com/qatar-grand-prix-2026-tyre-preview/"
QATAR_TYRE_PREVIEW = "pirelli-qatar-2026-preview.jpg"
QATAR_TYRE_INFOGRAPHIC = "pirelli-qatar-2026-technical-preview.jpg"
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
driver-by-driver remaining-set inventory.</p>
<p>On 24 November, Pirelli announced a maximum 27-lap stint per set, agreed
with the FIA, and said the race will require at least two stops. At the full
scheduled 57-lap distance, two sets cover only 54 laps. The official event
document listing remains unavailable, so its Qatar-specific prescriptions
have not been independently reviewed.
<a href="{PIRELLI_TYRE_LIMIT}">Pirelli's official Qatar tyre briefing, 24 November</a>.</p>
<p>Pirelli's linked event infographic lists slick minimum starting / expected
stabilized running pressures of 29.0 / &gt;=30.0 psi* at the front and
27.5 / &gt;=28.5 psi* at the rear, with EOS camber limits of -2.75 degrees
front and -1.50 degrees rear. The asterisk says these pressure values are
subject to change after FP2. These are Pirelli preview figures, not a
transcription from the unavailable FIA event listing. The same graphic lists
an average pit-stop loss of 26.5 seconds; do not present it as a stationary
wheel-change duration.</p>
<p>Pirelli F1 chief engineer Simone Berra's earlier Motorsport.com interview
adds that use is counted session by session, race laps behind the Safety Car
count, and remaining allowances follow Saturday running.
<a href="{QATAR_TYRE_LIMIT}">Motorsport.com report and Berra interview, 20 November</a>.
Coffee Corner Motorsport's independent 24 November preview says practice and
qualifying laps consume each set's allowance. <a href="{QATAR_TYRE_STRATEGY}">Coffee
Corner Motorsport, Qatar tyre preview</a> ·
<a href="{PIRELLI_NOMINATION}">Pirelli compound selection and graphic, 13 November</a>.</p>"""
    tyre_preview = f"""<figure class="circuit-fig">
<img class="circuit-img tyre-preview-img" src="../assets/{QATAR_TYRE_PREVIEW}"
alt="Pirelli's 2026 Qatar tyre selection: C1 Hard, C2 Medium and C3 Soft; C3 is mandatory for qualifying and C1 and C2 are mandatory for the race."
loading="lazy" onclick="zoomImg(this)">
<figcaption>Full, uncropped Pirelli Qatar 2026 compound and mandatory-set graphic.
This is not a driver-by-driver remaining-set inventory.
<a href="../assets/{QATAR_TYRE_PREVIEW}">Full-resolution image</a> ·
<a href="{PIRELLI_NOMINATION}">Pirelli source, 13 November 2026</a>.</figcaption>
</figure>"""
    tyre_infographic = f"""<figure class="circuit-fig">
<img class="circuit-img tyre-preview-img" src="../assets/{QATAR_TYRE_INFOGRAPHIC}"
alt="Full Pirelli 2026 Qatar preview infographic: Lusail circuit data, pit-stop loss, slick pressure and camber figures, and C1 Hard, C2 Medium and C3 Soft compounds."
loading="lazy" onclick="zoomImg(this)">
<figcaption>Full, uncropped Pirelli Qatar event infographic, published 24 November.
Pressure figures are marked subject to change after FP2; this is not a
driver-by-driver race-set inventory.
<a href="../assets/{QATAR_TYRE_INFOGRAPHIC}">Full-resolution image</a> ·
<a href="{PIRELLI_TYRE_LIMIT}">Pirelli source, 24 November 2026</a>.</figcaption>
</figure>"""
    pages["tyres"]["body"] += tyre_preview + tyre_infographic + card(
        "Qatar compounds and 27-lap tyre-set limit",
        nomination,
        "bi-record-circle",
        "accent",
    )
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
lead over Verstappen into the finale. That 25-lap cap was specific to 2025;
Pirelli announced a separate 27-lap limit for each set in 2026.
<a href="{QATAR_2025_RACE}">Formula1.com race report</a> ·
<a href="{PIRELLI_TYRE_LIMIT}">2026 Pirelli limit announcement</a>.</p>""",
            "bi-stars", "accent",
        ),
    )
    return pages
