"""Short editorial briefings, with a clearly labelled automatic priority fallback."""
import datetime
import hashlib
import html
import json
import logging
from pathlib import Path
import re
import urllib.parse

UTC = datetime.timezone.utc
MAX_STORIES = 5
PROMOTIONS = re.compile(
    r"\b(betting|bets?|fantasy|quiz|tickets?|competition to win|higher or lower|"
    r"how to watch|live coverage|football|shop|merchandise)\b", re.I)
TOPICS = [
    ("Safety and line-up", r"\b(injur\w*|replac\w*|substitut\w*|medical|heat hazard|"
     r"contract|re.sign\w*|cancelled|postponed|"
     r"lawson.*(?:stay|continues)|tsunoda.*(?:return|continues))\b"),
    ("Stewards and grid", r"\b(penalt\w*|disqualif\w*|grid drop|pit.lane start|appeal)\b"),
    ("Session outcome", r"\b(wins?|victory|pole|fp[123]|qualifying results|race results|sprint results)\b"),
    ("Team relations", r"(hamilton.*leclerc|leclerc.*hamilton|ferrari.*talks|team.orders)"),
    ("Championship", r"\b(championship|title|standings|russell.*team mate)\b"),
    ("Technical and circuit", r"\b(upgrades?|power unit|aero|tyres?|pirelli|"
     r"madring|circuit.*challenges)\b"),
]


def _read(path, kind):
    if not path.exists():
        return kind()
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, kind):
        raise ValueError(f"Invalid news briefing input: {path}")
    return value


def _url(value):
    if not isinstance(value, str):
        return False
    parsed = urllib.parse.urlsplit(value)
    return (parsed.scheme == "https" and bool(parsed.hostname)
            and not parsed.username and not parsed.password)


def _timestamp(value):
    parsed = datetime.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("News briefing timestamps must include a UTC offset")
    return parsed


def validate(record):
    """Reject malformed reviewed data instead of quietly hiding its stories."""
    reviewed = _timestamp(record["reviewed_at"])
    expires = _timestamp(record["expires_at"])
    if expires <= reviewed or expires - reviewed > datetime.timedelta(hours=24):
        raise ValueError("News briefing expiry must be within 24 hours of review")
    if not re.fullmatch(r"[0-9a-f]{64}", record["feed_fingerprint"]):
        raise ValueError("News briefing needs the reviewed priority-feed fingerprint")
    if record["through_session"] not in (
            None, "Practice 1", "Practice 2", "Practice 3", "Sprint Qualifying",
            "Sprint", "Qualifying", "Race"):
        raise ValueError("Unknown briefing session checkpoint")
    items = record["items"]
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_STORIES:
        raise ValueError("Provide one to five collated news highlights")
    topics = set()
    for item in items:
        for key in ("topic", "title", "summary", "why_it_matters"):
            if not isinstance(item[key], str) or not item[key].strip():
                raise ValueError(f"Missing news highlight {key}")
        if item["topic"] in topics:
            raise ValueError("Collate duplicate topics into a single highlight")
        topics.add(item["topic"])
        date = datetime.date.fromisoformat(item["date"])
        if date > reviewed.astimezone(UTC).date():
            raise ValueError("News highlight is dated after its review")
        if not isinstance(item["sources"], list) or not item["sources"]:
            raise ValueError("A collated highlight requires source links")
        for source in item["sources"]:
            if not _url(source["url"]) or not isinstance(source["label"], str) or not source["label"].strip():
                raise ValueError("Invalid news highlight source")


def candidates(records, ctx, now):
    race_date = datetime.date.fromisoformat(ctx["race_date"])
    end = min(now.date(), race_date + datetime.timedelta(days=2))
    start = max(end - datetime.timedelta(days=7), race_date - datetime.timedelta(days=10))
    selected = []
    urls = set()
    for record in records:
        title = record.get("title", "")
        if not isinstance(title, str) or PROMOTIONS.search(title):
            continue
        raw_date = record.get("date")
        if not raw_date:
            continue
        try:
            date = datetime.date.fromisoformat(raw_date)
        except (TypeError, ValueError):
            logging.warning("Invalid date in priority news candidate: %r", raw_date)
            continue
        if not start <= date <= end:
            continue
        url = record.get("url")
        if not _url(url):
            logging.warning("Invalid URL in priority news candidate: %r", url)
            continue
        if url in urls:
            continue
        for priority, (topic, pattern) in enumerate(TOPICS):
            if re.search(pattern, title, re.I):
                if topic == "Session outcome" and ctx.get("results"):
                    priority = -1
                selected.append((priority, topic, record))
                urls.add(url)
                break
    return selected


def fingerprint(records, ctx, now):
    rows = sorted((item["url"], item["title"], item["date"], item.get("paragraphs", []))
                  for _priority, _topic, item in candidates(records, ctx, now))
    return hashlib.sha256(json.dumps(rows, ensure_ascii=False).encode("utf-8")).hexdigest()


def automatic_items(records, ctx, now):
    """Group consequential headlines; never label this as human editorial judgment."""
    groups = {}
    for priority, topic, item in candidates(records, ctx, now):
        groups.setdefault((priority, topic), []).append(item)
    selected = []
    for (_priority, topic), stories in sorted(groups.items()):
        stories.sort(key=lambda story: (story["date"], story["title"]), reverse=True)
        newest = stories[0]
        selected.append({
            "topic": topic, "title": newest["title"], "date": newest["date"],
            # Headlines only: extracted wire paragraphs can be truncated mid-sentence.
            "summary": "", "why_it_matters": "",
            "sources": [{"label": story.get("source") or "Original report", "url": story["url"]}
                        for story in stories[:3]],
        })
    return selected[:MAX_STORIES]


def select(ctx, directory, now=None):
    now = (now or datetime.datetime.now(UTC)).astimezone(UTC)
    record = _read(Path(directory) / "news_highlights.json", dict)
    records = _read(Path(directory) / "news_auto.json", list)
    reason = ""
    if record:
        validate(record)
        latest = next((block["label"] for block in reversed(ctx.get("results", []))
                       if block["label"] != "Starting Grid"), None)
        if now < _timestamp(record["reviewed_at"]):
            reason = "The editorial review timestamp is in the future."
        elif now >= _timestamp(record["expires_at"]):
            reason = "The previous editorial briefing has expired."
        elif latest and latest != record["through_session"]:
            reason = "A different session classification is now available."
        elif record["feed_fingerprint"] != fingerprint(records, ctx, now):
            reason = "The priority news feed has changed since the editorial review."
        else:
            return {"items": record["items"], "mode": "Editor-collated",
                    "reviewed_at": record["reviewed_at"], "notice": ""}
    return {"items": automatic_items(records, ctx, now),
            "mode": "Automatic priority selection", "reviewed_at": record.get("reviewed_at", ""),
            "notice": reason}


def render(ctx, directory):
    briefing = select(ctx, directory)
    if not briefing["items"] and not briefing["notice"]:
        return ""
    escape = html.escape
    cards = []
    for number, item in enumerate(briefing["items"], 1):
        links = " / ".join(
            f'<a href="{escape(source["url"], quote=True)}" target="_blank" rel="noopener">'
            f'{escape(source["label"])}</a>' for source in item["sources"])
        text = f'<p>{escape(item["summary"])}</p>' if item["summary"] else ""
        if item["why_it_matters"]:
            text += f'<p class="briefing-impact"><strong>Why it matters:</strong> {escape(item["why_it_matters"])}</p>'
        cards.append(
            f'<article class="news-item"><div class="news-meta">'
            f'<span class="news-src">{number}. {escape(item["topic"])}</span>'
            f'<time datetime="{item["date"]}">{item["date"]}</time></div>'
            f'<h3>{escape(item["title"])}</h3>{text}'
            f'<p class="src">{"Sources" if item["summary"] else "Related reporting"}: {links}</p></article>')
    notice = ""
    if briefing["notice"]:
        notice = (f'<p class="briefing-notice">{escape(briefing["notice"])} '
                  'Awaiting an updated editorial selection; the earlier briefing is not pinned.</p>')
    if briefing["mode"] == "Automatic priority selection":
        notice += ('<p class="src">Grouped source headlines, not an editor-reviewed synthesis. '
                   'Promotions are excluded; related reports may cover different developments.</p>')
    reviewed = (f' &middot; reviewed {escape(briefing["reviewed_at"])}'
                if briefing["mode"] == "Editor-collated" else "")
    return (
        '<section class="news-briefing" aria-labelledby="news-briefing-title">'
        '<div class="briefing-heading"><div><span class="hero-kicker">The on-air briefing</span>'
        '<h2 id="news-briefing-title">Top stories &amp; why they matter</h2></div>'
        '<a href="news.html#full-news">Full news feed &rarr;</a></div>'
        f'<p class="src">{briefing["mode"]}{reviewed}</p>{notice}'
        f'<div class="briefing-grid">{"".join(cards)}</div></section>')


if __name__ == "__main__":
    import argparse
    import build
    parser = argparse.ArgumentParser(description="Print the priority-feed fingerprint after editorial review.")
    parser.add_argument("--gp", required=True)
    args = parser.parse_args()
    context = next((gp for gp in build.season_gps() if gp["dir"] == args.gp), None)
    if context is None:
        parser.error(f"Unknown GP: {args.gp}")
    feed = _read(Path(build.ROOT) / "data" / args.gp / "news_auto.json", list)
    print(fingerprint(feed, context, datetime.datetime.now(UTC)))
