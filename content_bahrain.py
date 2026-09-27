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


def _tl(year, title, text):
    return (
        f'<div class="tl-item"><div class="tl-year">{year}</div>'
        f'<div class="tl-title">{title}</div><p>{text}</p></div>'
    )


_MOMENTS = [
    ("1999", "Sepang's debut — and an instant classic",
     "The Sepang International Circuit — a purpose-built Hermann Tilke design "
     "commissioned as part of Malaysia's 1990s industrialisation push — opened "
     "with the very first Malaysian Grand Prix. Michael Schumacher, returning "
     "from a broken leg suffered mid-season, drove a supporting role to help "
     "Ferrari team-mate Eddie Irvine's title bid; Irvine won as Ferrari locked "
     "out the front two places on his return."),
    ("2009", "Button and Brawn's fairytale start",
     "Brawn GP's first race as a constructor produced pole and victory for "
     "Jenson Button, launching the underdog team (and Button) toward the 2009 "
     "world titles — one of the sport's most improbable championship runs."),
    ("2012", "Alonso's charge from P8",
     "A wet-dry Malaysian GP saw Fernando Alonso climb from eighth on the grid "
     "to win for Ferrari, benefiting from timing his intermediate and slick "
     "stops around the changing conditions — a reminder of how quickly Sepang's "
     "tropical weather can rewrite a race."),
    ("2017", "Verstappen's low-key statement win",
     "Starting third, Max Verstappen took his second Grand Prix victory at "
     "what proved to be Sepang's last race on the calendar before Malaysia "
     "dropped off the schedule — a result this circuit's return to F1 in 2026 "
     "now follows almost a decade later."),
]


def _moments_section():
    return f"""
<div class="callout">
  Sepang last hosted a round in 2017; the venue returns to the calendar for
  2026 as the new home of the Bahrain Grand Prix. Four verified moments from
  its original 1999&ndash;2017 run as the Malaysian Grand Prix, for use when
  live action goes quiet.
</div>
<div class="timeline">
  {''.join(_tl(y, t, x) for y, t, x in _MOMENTS)}
</div>
<p class="src">Sources:
<a href="{F1_EVENT}" target="_blank" rel="noopener">Formula1.com event guide</a>
(circuit history FAQ); race facts cross-checked against the checksum-verified
F1DB circuit-history record on this site's Facts &amp; Records page.</p>
"""


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    notice = _carryover_notice()
    pages["overview"]["body"] = notice + pages["overview"]["body"]
    pages["notes"]["body"] = notice + pages["notes"]["body"]
    pages["moments"] = dict(
        kicker="History",
        title="Sepang's Great Moments",
        sub="The Malaysian Grand Prix years (1999-2017) at the venue now hosting the Bahrain GP.",
        body=_moments_section(),
    )
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
