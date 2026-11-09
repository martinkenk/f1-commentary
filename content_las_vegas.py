"""Verified early development notes for the 2026 Las Vegas Grand Prix."""
import content_generic
from f1lib import card


MCLAREN_VEGAS_URL = (
    "https://www.formula1.com/en/latest/article/"
    "technically-a-very-interesting-race-stella-reveals-how-norris-and-mclaren-"
    "triumphed-at-interlagos.SRa4ORrmm9CcPqhwssoum"
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
    pages["notes"]["body"] = update + pages["notes"]["body"]
    return pages
