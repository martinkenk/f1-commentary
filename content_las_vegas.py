"""Verified early development notes for the 2026 Las Vegas Grand Prix."""
import content_generic
from f1lib import card


MCLAREN_VEGAS_URL = (
    "https://www.formula1.com/en/latest/article/"
    "technically-a-very-interesting-race-stella-reveals-how-norris-and-mclaren-"
    "triumphed-at-interlagos.SRa4ORrmm9CcPqhwssoum"
)
ANTONELLI_TITLE_URL = (
    "https://www.formula1.com/en/latest/article/"
    "antonelli-crowned-youngest-ever-f1-champion-as-verstappen-wins-eventful-"
    "mexico-git-grand-prix.xpMMeef0KmRURs9IDs3LH"
)
MERCEDES_TITLE_URL = (
    "https://www.formula1.com/en/latest/article/"
    "norris-beats-verstappen-in-wet-sao-paulo-gp-thriller-as-mercedes-win-"
    "constructors-championship.7JN7MXLZf5lk5l0C3gfKGI"
)


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    update = card(
        "McLaren says more parts are planned for Las Vegas",
        f"""<p>Team Principal Andrea Stella said the Interlagos package will be
complemented by more parts at Las Vegas, forming a foundation for McLaren's
2027 car. His interview did not identify the components or their intended
effect. This is a team statement, not an FIA filing. <a href="{MCLAREN_VEGAS_URL}"
target="_blank" rel="noopener">Formula1.com, 9 November</a>.</p>""",
        "bi-tools",
        "accent",
    )
    championships = card(
        "Both 2026 championships are settled",
        f"""<p>Kimi Antonelli clinched the Drivers' Championship with third place
in Mexico City on 1 November. Mercedes secured the Constructors' title in São
Paulo on 8 November, where George Russell finished fourth and Antonelli fifth.
The Las Vegas weekend is no longer a title-decider; focus on race wins and the
remaining finishing positions. <a href="{ANTONELLI_TITLE_URL}" target="_blank"
rel="noopener">Formula1.com on Antonelli's title</a> ·
<a href="{MERCEDES_TITLE_URL}" target="_blank" rel="noopener">Formula1.com on
Mercedes' title</a>.</p>""",
        "bi-trophy",
        "accent",
    )
    pending = content_generic.pending(
        "Team-by-team weekend storylines", "in the week before the race"
    )
    pages["teams"]["body"] = pages["teams"]["body"].replace(
        pending,
        update + content_generic.pending(
            "Further team-specific weekend details",
            "as event statements and filings are reviewed",
        ),
    )
    pages["upgrades"]["body"] = update + pages["upgrades"]["body"]
    pages["notes"]["body"] = championships + update + pages["notes"]["body"]
    return pages
