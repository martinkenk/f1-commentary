"""2026 Bahrain Grand Prix coverage at Sepang."""
import content_generic
from f1lib import render_penalties


FIA_DOC_66 = (
    "https://www.fia.com/system/files/decision-document/"
    "2026_azerbaijan_grand_prix_-_infringement_-_car_43_-_"
    "collision_with_car_10_in_turn_1.pdf"
)
F1_PENALTY_ARTICLE = (
    "https://www.formula1.com/en/latest/article/"
    "colapinto-hit-with-five-place-grid-penalty-for-bahrain-gp-in-malaysia-"
    "after-baku-collision.3gWVfzDMMr5hReiwTt1fPD"
)
F1_EVENT = "https://www.formula1.com/en/racing/2026/bahrain"


def _carryover_notice():
    return f"""
<div class="callout accent"><strong>Confirmed grid watch:</strong>
FIA Document 66 converted Franco Colapinto's 10-second Azerbaijan Race penalty
for his Turn 1 collision with team-mate Pierre Gasly into a five-place drop at
the next race in which he participates. Formula1.com identifies that as the
Bahrain Grand Prix in Malaysia; this calendar places that event at Sepang on
4 October. This is a carry-over sanction, not a Bahrain stewards' decision.
Qualifying and the official Bahrain starting grid are still pending, so do not
state a resulting grid position.
<p class="src">Sources:
<a href="{FIA_DOC_66}" target="_blank" rel="noopener">FIA Document 66</a>;
<a href="{F1_PENALTY_ARTICLE}" target="_blank" rel="noopener">Formula1.com penalty report</a>;
<a href="{F1_EVENT}" target="_blank" rel="noopener">Formula1.com event guide</a>.</p>
</div>"""


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    notice = _carryover_notice()
    pages["overview"]["body"] = notice + pages["overview"]["body"]
    pages["notes"]["body"] = notice + pages["notes"]["body"]
    pages["penalties"] = dict(
        kicker="Confirmed carry-over sanction",
        title="Penalties & Decisions",
        sub="A published Azerbaijan ruling applies to this event; Bahrain-specific decisions remain source-dependent.",
        body=render_penalties(
            ctx,
            decisions=[
                dict(
                    doc="Azerbaijan Doc 66",
                    source_event="azerbaijan",
                    no="43",
                    driver="Franco Colapinto",
                    team="BWT Alpine F1 Team",
                    session="Azerbaijan Grand Prix — Race",
                    fact="Turn 1 collision with team-mate Pierre Gasly.",
                    outcome=(
                        "10-second time penalty converted to five grid places at "
                        "the next race in which the driver participates."
                    ),
                    kind="penalty",
                    source_url=FIA_DOC_66,
                )
            ],
            intro_html=notice,
            fia_url=ctx.get("fia_url", ""),
        ),
    )
    return pages
