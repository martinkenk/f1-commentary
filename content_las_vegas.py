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
HAAS_URL = (
    "https://www.formula1.com/en/latest/article/"
    "haas-confirm-camara-to-race-for-the-team-in-las-vegas-as-hirakawa-returns-"
    "for-fp1-appearance.2as7TuSF4UHgXczZlu4245"
)
HAAS_RACE_URL = (
    "https://www.the-race.com/formula-1/"
    "vegas-gives-camara-chance-to-put-messy-debut-behind-him/"
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
    haas = card(
        "Haas: Camara stays for Las Vegas, Hirakawa returns for FP1",
        f"""<p>Haas confirmed on 16 November that Rafael Camara will race again
after his São Paulo debut, with Ryo Hirakawa back in Ollie Bearman's car for
FP1. Camara's debut was brought forward from 2027 after Haas split with
Esteban Ocon; the team's announcement committed only to Las Vegas, and The
Race notes the later rounds are less clear because Camara leads F2 by seven
points over Nikola Tsolov. The Race's review put Camara about a tenth a lap
slower than Bearman across two soft stints in Brazil, with the caveat that
Bearman's race was compromised. <a href="{HAAS_URL}" target="_blank"
rel="noopener">Formula1.com</a> · <a href="{HAAS_RACE_URL}" target="_blank"
rel="noopener">The Race</a>.</p>""",
        "bi-person-badge",
        "accent",
    )
    pending = content_generic.pending(
        "Team-by-team weekend storylines", "in the week before the race"
    )
    pages["teams"]["body"] = pages["teams"]["body"].replace(
        pending,
        haas + update + content_generic.pending(
            "Further team-specific weekend details",
            "as event statements and filings are reviewed",
        ),
    )
    pages["upgrades"]["body"] = update + pages["upgrades"]["body"]
    pages["notes"]["body"] = championships + haas + update + pages["notes"]["body"]
    return pages
