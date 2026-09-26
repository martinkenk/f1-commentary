"""Collect public pre-race inventory graphics, never infer remaining tyre counts.

The image is the evidence. ``available`` means a complete source graphic was
downloaded and decoded, not that its numbers have been transcribed or verified.
Importing this module and calling context() never uses the network or FastF1.
Collection requires Pillow for WebP; PNG/JPEG can also use PyMuPDF. PDF,
SVG, animated images and protected/embedded API charts are not supported.
"""
import argparse
import datetime as dt
import hashlib
import html
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import re
import struct
import urllib.error
import urllib.parse
import urllib.request
import unicodedata
import uuid
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ASSET_DIR = ROOT / "assets_src"
F1_LATEST = "https://www.formula1.com/en/latest/all.html"
# This feed is advertised by rel=alternate in the publisher's public HTML.
SECONDARY_FEED = "https://coffeecornermotorsport.com/feed/"
SEEDS = {
    (2026, "spain"): [
        "https://coffeecornermotorsport.com/spanish-grand-prix-2026-tyre-strategy/",
    ],
    (2026, "italy"): [
        "https://coffeecornermotorsport.com/italian-grand-prix-2026-tyre-strategy/",
    ],
}
PAGE_HOSTS = {"www.formula1.com", "formula1.com", "coffeecornermotorsport.com"}
IMAGE_HOSTS = PAGE_HOSTS | {"media.formula1.com"}
STATES = {"available", "not_found", "access_restricted", "error"}
MAX_PAGE = 6 * 1024 * 1024
MAX_IMAGE = 12 * 1024 * 1024
CHART_PATTERN = re.compile(
    r"race[\s_-]*sets|tyres?\s+available\s+for\s+(?:the\s+)?race"
    r"|tyre\s+sets\s+available\s+for\s+(?:the\s+)?race", re.I)


class SourceError(ValueError):
    """An unsupported or invalid public source; never an empty inventory."""


class AccessRestricted(SourceError):
    """A publication exists but cannot be retrieved without access."""


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def safe_url(url, image=False):
    if not isinstance(url, str) or any(ord(c) < 33 for c in url) or "\\" in url:
        raise SourceError("Invalid source URL")
    try:
        parsed = urllib.parse.urlsplit(url)
        valid = (parsed.scheme == "https" and parsed.hostname in
                 (IMAGE_HOSTS if image else PAGE_HOSTS)
                 and parsed.port in (None, 443)
                 and parsed.username is None and parsed.password is None)
    except ValueError as exc:
        raise SourceError("Invalid source URL") from exc
    if not valid:
        raise SourceError(f"Source URL is not on the public HTTPS allowlist: {url}")
    return url


class _PublicRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, image):
        super().__init__()
        self.image = image

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        safe_url(newurl, self.image)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, image=False):
    """Bounded public fetch; redirects cannot escape the source allowlist."""
    safe_url(url, image)
    limit = MAX_IMAGE if image else MAX_PAGE
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.build_opener(_PublicRedirect(image)).open(
                request, timeout=30) as response:
            safe_url(response.geturl(), image)
            length = response.headers.get("Content-Length")
            if length and (not length.isdigit() or int(length) > limit):
                raise SourceError("Source exceeds download size limit")
            data = response.read(limit + 1)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise AccessRestricted(f"Public source returned HTTP {exc.code}") from exc
        raise SourceError(f"Public source returned HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SourceError(f"Source fetch failed: {exc}") from exc
    if not data or len(data) > limit:
        raise SourceError("Empty source or download size limit exceeded")
    return data


def _text(data):
    try:
        return data.decode("utf-8-sig")
    except (AttributeError, UnicodeDecodeError) as exc:
        raise SourceError("Unsupported source text encoding") from exc


class Article(HTMLParser):
    """Keep image-local evidence separate from unrelated article/sidebar images."""
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.images = []
        self.figure = None
        self.caption = False
        self.anchor = ""
        self.link = None
        self.links = []
        self.title_parts = []
        self.in_title = False
        self.scripts = []
        self.in_json = False
        self.feed(text)
        self.title = self.meta.get("og:title") or " ".join(self.title_parts).strip()
        self.published = self.meta.get("article:published_time", "")
        for script in self.scripts:
            try:
                obj = json.loads(script)
            except json.JSONDecodeError:
                continue
            for item in _json_objects(obj):
                kinds = item.get("@type", [])
                if isinstance(kinds, str):
                    kinds = [kinds]
                if isinstance(kinds, list) and any(
                        kind in kinds for kind in ("Article", "NewsArticle", "BlogPosting")):
                    self.published = self.published or item.get("datePublished", "")
                    self.title = self.title or item.get("headline", "")

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            self.meta[a.get("property") or a.get("name", "")] = a.get("content", "")
        elif tag == "title":
            self.in_title = True
        elif tag == "script" and a.get("type") == "application/ld+json":
            self.in_json = True
            self.scripts.append("")
        elif tag == "figure":
            self.figure = {"caption": "", "images": []}
        elif tag == "figcaption":
            self.caption = True
        elif tag == "a":
            self.anchor = a.get("href", "")
            self.link = {"url": self.anchor, "text": ""}
            self.links.append(self.link)
        elif tag in ("object", "embed", "iframe"):
            self.links.append({"url": a.get("data") or a.get("src", ""),
                               "text": a.get("title", "")})
        elif tag == "img":
            image = {"attrs": a, "link": self.anchor, "figure": self.figure}
            self.images.append(image)
            if self.figure is not None:
                self.figure["images"].append(image)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script":
            self.in_json = False
        elif tag == "figure":
            self.figure = None
        elif tag == "figcaption":
            self.caption = False
        elif tag == "a":
            self.anchor = ""
            self.link = None

    def handle_data(self, text):
        if self.in_title:
            self.title_parts.append(text)
        if self.in_json:
            self.scripts[-1] += text
        if self.caption and self.figure is not None:
            self.figure["caption"] += text + " "
        if self.link is not None:
            self.link["text"] += text + " "


def _json_objects(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _json_objects(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _json_objects(value)


def _identity(ctx):
    if not isinstance(ctx, dict) or not isinstance(ctx.get("cal", {}), dict):
        raise SourceError("Invalid calendar context")
    slug = ctx.get("dir")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise SourceError("Invalid GP slug")
    year = ctx.get("year")
    if isinstance(year, bool) or not isinstance(year, (str, int)):
        raise SourceError("Invalid event year")
    try:
        year = int(year)
        date = dt.date.fromisoformat(ctx.get("race_date") or ctx.get("cal", {}).get("race_date", ""))
    except (ValueError, TypeError) as exc:
        raise SourceError("Invalid event year/race date") from exc
    if date.year != year:
        raise SourceError("Event year and race date disagree")
    return year, slug, date


def _normal(text):
    text = unicodedata.normalize("NFKD", html.unescape(str(text))).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _has(text, phrase):
    return f" {_normal(phrase)} " in f" {_normal(text)} "


def _event_name(ctx, text):
    name = ctx.get("name") or ctx.get("cal", {}).get("name", "")
    return bool(name) and (_has(text, name) or _has(text, name.replace("Grand Prix", "GP")))


def _venues(ctx):
    # Calendar relocation overrides are intentional: never accept Barcelona or
    # Sakhir merely because the national Grand Prix name matches.
    year, slug, _ = _identity(ctx)
    special = {
        (2026, "spain"): ["madrid", "madring"],
        (2026, "bahrain"): ["sepang", "kuala lumpur"],
    }
    if (year, slug) in special:
        return special[year, slug]
    cal = ctx.get("cal") or {}
    names = [cal.get("location", ""), ctx.get("circuit", "")]
    aliases = {"italy": ["monza"], "azerbaijan": ["baku"],
               "las-vegas": ["las vegas"]}
    return [name for name in names + aliases.get(slug, []) if name]


def _published(value):
    if not isinstance(value, str):
        raise SourceError("Unsupported publication timestamp type")
    try:
        stamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SourceError("Missing or unsupported article publication date") from exc
    if stamp.tzinfo is None:
        raise SourceError("Publication timestamp must include a timezone")
    return stamp


def _check_article(ctx, article):
    year, _, race_day = _identity(ctx)
    stamp = _published(article.published)
    sessions = (ctx.get("cal") or {}).get("sessions", [])
    race = next((s for s in sessions if s.get("label") == "Race"), {})
    # Compare local event dates, not UTC dates (Las Vegas races on Saturday).
    local = stamp.astimezone(ZoneInfo(race["timezone"])) if race.get("timezone") else stamp
    if not race_day - dt.timedelta(days=3) <= local.date() <= race_day:
        raise SourceError("Article publication is outside the pre-race date window")
    if stamp.year != year or not _event_name(ctx, article.title):
        raise SourceError("Article event/year does not match the calendar")
    title_years = set(re.findall(r"\b20\d{2}\b", article.title))
    if title_years and title_years != {str(year)}:
        raise SourceError("Article title refers to another season")


def _restricted(text):
    return bool(re.search(
        r'["\']?(?:isAccessibleForFree)["\']?\s*:\s*false'
        r'|["\']?(?:isProtected|isFreewallVisible)["\']?\s*:\s*true',
        text.replace('\\"', '"'), re.I))


def chart_links(ctx, page_url, text, previous=None):
    if _restricted(text):
        raise AccessRestricted("Published article is access-restricted; no login or protected API attempted")
    article = Article(text)
    _check_article(ctx, article)
    charts = []
    for image in article.images:
        a = image["attrs"]
        caption = (image["figure"] or {}).get("caption", "")
        evidence = " ".join([a.get("alt", ""), a.get("title", ""), caption])
        urls = []
        # Prefer a linked original, then the largest actually exposed srcset.
        link = image["link"]
        if link and re.search(r"\.(?:webp|png|jpe?g)(?:\?|$)", link, re.I):
            urls.append(link)
        variants = []
        for part in (a.get("data-srcset") or a.get("srcset", "")).split(","):
            match = re.fullmatch(r"\s*(\S+)\s+(\d+)w\s*", part)
            if match:
                variants.append((int(match[2]), match[1]))
        urls.extend(url for _, url in sorted(variants, reverse=True))
        urls.extend(a.get(key, "") for key in ("data-src", "src"))
        urls = [urllib.parse.urljoin(page_url, u) for u in urls
                if u and not u.startswith("data:")]
        if not urls or not CHART_PATTERN.search(evidence + " " + " ".join(urls)):
            continue
        if re.search(r"post[\s-]*race|stint\s+(?:summary|chart)|qualifying\s+summary", evidence, re.I):
            continue
        year, _, _ = _identity(ctx)
        chart_years = set(re.findall(r"\b20\d{2}\b", evidence + " " + urls[0]))
        if chart_years and chart_years != {str(year)}:
            raise SourceError("Race chart refers to another season")
        if not _event_name(ctx, evidence):
            raise SourceError("Race chart has no matching calendar event evidence")
        if not _has(evidence, "pirelli"):
            raise SourceError("Race chart lacks exposed Pirelli creator attribution")
        expected_sha = None
        if not any(_has(evidence, venue) for venue in _venues(ctx)):
            # Reuse validated image evidence only for the identical source and bytes.
            cached = previous["chart"] if previous and previous["source"]["url"] == page_url else None
            if (not cached or cached["url"] != urls[0]
                    or not any(_has(cached.get("evidence", ""), venue) for venue in _venues(ctx))):
                raise SourceError("Race chart has no matching calendar venue evidence")
            evidence = cached["evidence"]
            expected_sha = cached["sha256"]
        url = safe_url(urls[0], image=True)
        if not any(chart["url"] == url for chart in charts):
            chart = {"url": url, "evidence": evidence.strip()}
            if expected_sha:
                chart["expected_sha256"] = expected_sha
            charts.append(chart)
    if not charts and any(CHART_PATTERN.search(link["url"] + " " + link["text"])
                          for link in article.links):
        raise SourceError("Unsupported linked/embedded race inventory format; no public raster chart exposed")
    return article, charts


def raster_info(data, decode=True):
    """Identify bytes, not suffix/MIME. Decode full raster before publishing."""
    if not isinstance(data, bytes) or not 32 <= len(data) <= MAX_IMAGE:
        raise SourceError("Invalid raster payload size/type")
    if data.startswith(b"\x89PNG\r\n\x1a\n") and data[12:16] == b"IHDR":
        ext = "png"
        width, height = struct.unpack(">II", data[16:24])
    elif data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        ext = "webp"
        if struct.unpack("<I", data[4:8])[0] + 8 != len(data):
            raise SourceError("Truncated WebP payload")
        kind = data[12:16]
        if kind == b"VP8X":
            if data[20] & 2:
                raise SourceError("Animated WebP is not a static inventory graphic")
            width = 1 + int.from_bytes(data[24:27], "little")
            height = 1 + int.from_bytes(data[27:30], "little")
        elif kind == b"VP8 " and data[23:26] == b"\x9d\x01\x2a":
            width, height = (v & 0x3fff for v in struct.unpack("<HH", data[26:30]))
        elif kind == b"VP8L" and data[20] == 0x2f:
            bits = int.from_bytes(data[21:25], "little")
            width, height = (bits & 0x3fff) + 1, ((bits >> 14) & 0x3fff) + 1
        else:
            raise SourceError("Unsupported WebP raster header")
    elif data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9"):
        ext = "jpg"
        width = height = 0
        offset = 2
        while offset + 4 <= len(data):
            if data[offset] != 0xff:
                break
            marker = data[offset + 1]
            size = int.from_bytes(data[offset + 2:offset + 4], "big")
            if marker in (0xc0, 0xc1, 0xc2) and size >= 7 and offset + 9 <= len(data):
                height, width = struct.unpack(">HH", data[offset + 5:offset + 9])
                break
            if size < 2:
                break
            offset += size + 2
    else:
        raise SourceError("Unsupported source image format (only static PNG, JPEG and WebP)")
    if not (600 <= width <= 12000 and 300 <= height <= 12000 and width * height <= 40_000_000):
        raise SourceError("Image dimensions are unsafe or too small for a full inventory chart")
    if decode:
        try:
            from PIL import Image, UnidentifiedImageError
        except ImportError:
            if ext == "webp":
                raise SourceError("Pillow is required to decode WebP race charts; PyMuPDF does not support WebP")
            try:
                import pymupdf
            except ImportError as exc:
                raise SourceError("Pillow or PyMuPDF is required to validate downloaded race charts") from exc
            try:
                pix = pymupdf.Pixmap(data)
            except (RuntimeError, ValueError, pymupdf.mupdf.FzErrorBase) as exc:
                raise SourceError(f"Raster cannot be decoded: {exc}") from exc
            dimensions = (pix.width, pix.height)
        else:
            try:
                with Image.open(io.BytesIO(data)) as image:
                    if getattr(image, "n_frames", 1) != 1:
                        raise SourceError("Animated raster is not a static inventory graphic")
                    image.verify()
                with Image.open(io.BytesIO(data)) as image:
                    image.load()
                    dimensions = image.size
            except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
                raise SourceError(f"Raster cannot be decoded: {exc}") from exc
        if dimensions != (width, height):
            raise SourceError("Decoded raster dimensions disagree with its header")
    return ext, width, height


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SourceError(f"Cannot read {Path(path).name}: {exc}") from exc


def _validate_snapshot(ctx, snapshot, asset_dir=None):
    year, slug, date = _identity(ctx)
    if not isinstance(snapshot, dict) or type(snapshot.get("year")) is not int:
        raise SourceError("Invalid cached inventory object/year")
    if (snapshot["year"], snapshot.get("gp"), snapshot.get("race_date")) != (year, slug, date.isoformat()):
        raise SourceError("Cached inventory belongs to a different event/year/date")
    source, chart = snapshot.get("source"), snapshot.get("chart")
    if not isinstance(source, dict) or not isinstance(chart, dict):
        raise SourceError("Invalid cached source/chart")
    for key in ("url", "title", "published_at", "publisher"):
        if not isinstance(source.get(key), str) or not source[key]:
            raise SourceError(f"Invalid cached source {key}")
    safe_url(source["url"])
    safe_url(chart.get("url"), image=True)
    article = Article("")
    article.title, article.published = source["title"], source["published_at"]
    _check_article(ctx, article)
    _published(snapshot.get("retrieved_at"))
    publisher, provenance = _attribution(source["url"])
    if (source["publisher"] != publisher or chart.get("provenance") != provenance
            or chart.get("credit") != "Pirelli Motorsport"):
        raise SourceError("Invalid cached publisher/creator attribution")
    asset, sha = chart.get("asset"), chart.get("sha256")
    if not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{64}", sha):
        raise SourceError("Invalid cached image hash")
    if not isinstance(asset, str) or not re.fullmatch(
            rf"race-tyres-{year}-{re.escape(slug)}-{sha[:16]}\.(?:png|jpg|webp)", asset):
        raise SourceError("Invalid cached asset basename")
    if any(type(chart.get(key)) is not int for key in ("width", "height")):
        raise SourceError("Invalid cached image dimensions")
    path = Path(ASSET_DIR if asset_dir is None else asset_dir) / asset
    try:
        if path.stat().st_size > MAX_IMAGE:
            raise SourceError("Cached image exceeds size limit")
        data = path.read_bytes()
    except OSError as exc:
        raise SourceError(f"Missing/unreadable cached chart asset: {exc}") from exc
    if hashlib.sha256(data).hexdigest() != sha:
        raise SourceError("Cached chart hash mismatch")
    ext, width, height = raster_info(data, decode=False)
    if (width, height) != (chart["width"], chart["height"]) or not asset.endswith("." + ext):
        raise SourceError("Cached chart dimensions/format mismatch")
    return snapshot


def context(ctx, root=None):
    """Read-only context; optional repository root isolates data and assets."""
    default = {"checked_at": "", "state": "not_found", "error": "", "attempts": []}
    try:
        _, slug, _ = _identity(ctx)
    except SourceError as exc:
        return {"snapshot": {}, "status": {**default, "state": "error", "error": str(exc)}}
    directory = (Path(DATA_DIR) if root is None else Path(root) / "data") / slug
    asset_dir = Path(ASSET_DIR) if root is None else Path(root) / "assets_src"
    status = default.copy()
    warnings = []
    if (directory / "race_tyres_status.json").exists():
        try:
            status = _read_json(directory / "race_tyres_status.json")
            if (not isinstance(status, dict) or not isinstance(status.get("state"), str)
                    or status["state"] not in STATES
                    or not isinstance(status.get("attempts"), list)
                    or not isinstance(status.get("checked_at"), str)
                    or not isinstance(status.get("error"), str)
                    or any(not isinstance(a, dict) or not isinstance(a.get("state"), str)
                           or a["state"] not in STATES
                           or any(not isinstance(a.get(k), str) for k in ("url", "message"))
                           for a in status["attempts"])):
                raise SourceError("Invalid cached inventory status")
        except SourceError as exc:
            status = default.copy()
            warnings.append(str(exc))
    snapshot = {}
    if (directory / "race_tyres.json").exists():
        try:
            snapshot = _validate_snapshot(
                ctx, _read_json(directory / "race_tyres.json"), asset_dir=asset_dir)
        except SourceError as exc:
            warnings.append(str(exc))
    if not snapshot and status["state"] == "available":
        warnings.append("Available status has no valid cached inventory chart")
    if warnings:
        status = {**status, "state": "error",
                  "error": "; ".join(filter(None, [status["error"]] + warnings))}
    return {"snapshot": snapshot, "status": status}


def _atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(f".{path.name}.{uuid.uuid4().hex}.part")
    try:
        with staging.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(staging, path)
    finally:
        staging.unlink(missing_ok=True)


def _save_json(path, value):
    _atomic(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def _attribution(url):
    if urllib.parse.urlsplit(url).hostname == "coffeecornermotorsport.com":
        return "Coffee Corner Motorsport", "secondary-reproduction"
    return "Formula1.com", "first-party"


def _candidate(ctx, title, url):
    pattern = (r"strategy[\s_-]+guide|race[\s_-]*sets|tyres?[\s_-]*available")
    try:
        host = urllib.parse.urlsplit(url).hostname
    except ValueError as exc:
        raise SourceError("Invalid discovered article URL") from exc
    if host == "coffeecornermotorsport.com":
        pattern += r"|tyre[\s_-]+strategy"
    return _event_name(ctx, title + " " + url) and bool(
        re.search(pattern, title + " " + url, re.I))


def discover(ctx, attempts):
    year, slug, _ = _identity(ctx)
    urls = list(SEEDS.get((year, slug), []))
    directory = Path(DATA_DIR) / slug
    for filename in ("news_auto.json", "race_tyres.json"):
        path = directory / filename
        if not path.exists():
            continue
        try:
            obj = _read_json(path)
            if filename == "news_auto.json":
                if not isinstance(obj, list):
                    raise SourceError("Saved news must be a list")
                for item in obj:
                    if not isinstance(item, dict):
                        raise SourceError("Saved news item must be an object")
                    url, title = item.get("url", ""), item.get("title", "")
                    if isinstance(url, str) and isinstance(title, str) and _candidate(ctx, title, url):
                        if urllib.parse.urlsplit(url).hostname not in PAGE_HOSTS:
                            continue
                        urls.append(safe_url(url))
            elif (isinstance(obj, dict) and
                  (obj.get("year"), obj.get("gp"), obj.get("race_date")) ==
                  (year, slug, ctx.get("race_date"))):
                source = obj.get("source")
                if not isinstance(source, dict):
                    raise SourceError("Invalid saved inventory source")
                urls.append(safe_url(source.get("url")))
        except SourceError as exc:
            attempts.append({"url": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else filename,
                             "state": "error", "message": str(exc)})
    for url in (F1_LATEST, SECONDARY_FEED):
        try:
            text = _text(fetch(url))
            if url == F1_LATEST:
                # The public listing embeds access flags for article cards.
                # They do not gate the listing's exposed article links.
                links = list(dict.fromkeys(re.findall(
                    r"/en/latest/article/[a-z0-9-]+\.[A-Za-z0-9_-]+", text)))
                if not links:
                    raise SourceError("Unsupported Formula1 latest format: no article links")
                pairs = [("", urllib.parse.urljoin(url, link)) for link in links[:80]]
            else:
                try:
                    root = ET.fromstring(text)
                except ET.ParseError as exc:
                    raise SourceError("Unsupported publisher feed format: invalid XML") from exc
                items = root.findall("./channel/item")
                if root.tag != "rss" or not items:
                    raise SourceError("Unsupported publisher feed format: no RSS items")
                pairs = [(item.findtext("title", ""), item.findtext("link", "")) for item in items[:40]]
            found = 0
            for title, link in pairs:
                if _candidate(ctx, title, link):
                    urls.append(safe_url(link))
                    found += 1
            attempts.append({"url": url, "state": "available" if found else "not_found",
                             "message": f"Public discovery parsed; {found} candidate article(s)"})
        except (SourceError, AccessRestricted) as exc:
            attempts.append({"url": url, "state": "access_restricted" if isinstance(
                exc, AccessRestricted) else "error", "message": str(exc)})
    return list(dict.fromkeys(urls))[:12]


def collect(ctx):
    year, slug, date = _identity(ctx)
    checked = now()
    attempts = []
    urls = discover(ctx, attempts)
    previous = context(ctx)["snapshot"]
    snapshots = []
    for url in urls:
        try:
            safe_url(url)
            article, charts = chart_links(ctx, url, _text(fetch(url)), previous=previous)
            if not charts:
                attempts.append({"url": url, "state": "not_found",
                                 "message": "Public article exposes no supported race-sets graphic; "
                                            "not proof of non-publication"})
                continue
            for chart in charts:
                try:
                    data = fetch(chart["url"], image=True)
                    ext, width, height = raster_info(data)
                    sha = hashlib.sha256(data).hexdigest()
                    if chart.get("expected_sha256") and sha != chart["expected_sha256"]:
                        raise SourceError("Race chart changed; previous visual venue evidence "
                                          "cannot verify this revision")
                    asset = f"race-tyres-{year}-{slug}-{sha[:16]}.{ext}"
                    _atomic(Path(ASSET_DIR) / asset, data)
                    publisher, provenance = _attribution(url)
                    snapshots.append({
                        "year": year, "gp": slug, "race_date": date.isoformat(),
                        "source": {"url": url, "title": article.title,
                                   "published_at": article.published, "publisher": publisher},
                        "chart": {"url": chart["url"], "asset": asset, "sha256": sha,
                                  "width": width, "height": height, "credit": "Pirelli Motorsport",
                                  "provenance": provenance, "evidence": chart["evidence"]},
                        "retrieved_at": checked,
                    })
                    attempts.append({"url": chart["url"], "state": "available",
                                     "message": f"Full {width}×{height} {ext.upper()} decoded and hashed; "
                                                f"{provenance}; numeric counts not verified"})
                    break
                except (SourceError, OSError) as exc:
                    attempts.append({"url": chart["url"], "state": "access_restricted" if isinstance(
                        exc, AccessRestricted) else "error", "message": str(exc)})
        except (SourceError, OSError) as exc:
            attempts.append({"url": url, "state": "access_restricted" if isinstance(
                exc, AccessRestricted) else "error", "message": str(exc)})
    failures = [a for a in attempts if a["state"] in ("error", "access_restricted")]
    if snapshots:
        # Prefer a first-party public source, otherwise the most recently published.
        snapshots.sort(key=lambda s: (s["chart"]["provenance"] == "first-party",
                                     _published(s["source"]["published_at"])), reverse=True)
        _save_json(Path(DATA_DIR) / slug / "race_tyres.json", snapshots[0])
        state = "available"
    elif any(a["state"] == "error" for a in failures):
        state = "error"
    elif failures:
        state = "access_restricted"
    else:
        state = "not_found"
    status = {"checked_at": checked, "state": state,
              "error": "; ".join(f'{a["url"]}: {a["message"]}' for a in failures),
              "attempts": attempts}
    _save_json(Path(DATA_DIR) / slug / "race_tyres_status.json", status)
    return context(ctx)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gp", help="Explicit calendar slug for backfill; default is the active enrichment window")
    args = parser.parse_args(argv)
    import enrich
    gps = enrich.load_gps()
    if args.gp:
        gps = [ctx for ctx in gps if ctx["dir"] == args.gp]
        if not gps:
            parser.error(f"Unknown GP: {args.gp}")
    else:
        gps = enrich.active_gps(gps)
    failed = False
    for ctx in gps:
        result = collect(ctx)
        status = result["status"]
        print(f'{ctx["dir"]}: {status["state"]}')
        if status["error"]:
            print(f'  Warning: {status["error"]}')
        if not result["snapshot"]:
            print("  Pending public verified-source chart; missing is not zero or proof of non-publication.")
        failed |= status["state"] == "error"
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
