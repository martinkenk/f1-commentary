"""United States Grand Prix coverage layered over the shared event pages."""

import content_generic

F1_TYRE_ARTICLE = (
    "https://www.formula1.com/en/latest/article/"
    "what-tyres-will-the-teams-and-drivers-have-for-the-2026-united-states-grand-prix."
    "44LKddYSbUJK1LxMAa6VLI"
)


def _figure(asset, alt, caption, source_url, source_label):
    return f"""
    <figure class="circuit-fig">
      <img src="../assets/{asset}" alt="{alt}" loading="lazy"
        class="circuit-img tyre-preview-img" role="button" tabindex="0"
        onclick="zoomImg(this)" title="Click to zoom / full screen"
        onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();zoomImg(this)}}">
      <figcaption>{caption}. <strong>Click to zoom / full screen.</strong> ·
      <a href="{source_url}" target="_blank"
      rel="noopener">{source_label}</a></figcaption>
    </figure>"""


def build_pages(ctx, env):
    pages = content_generic.build_pages(ctx, env)
    pages["tyres"]["body"] = (
        _figure(
            "united-states_pirelli_tyres_2026.webp",
            "Official Pirelli 2026 United States Grand Prix tyre preview: circuit "
            "information, tyre demands, pressures and selected compounds",
            "Official Pirelli event-preview graphic",
            F1_TYRE_ARTICLE,
            "Formula 1 / Pirelli source ↗",
        )
        + pages["tyres"]["body"]
    )
    return pages
