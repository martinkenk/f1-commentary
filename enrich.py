"""
F1 Commentary Hub — incremental enrichment pipeline.

Where build.py parses live timing and weather, enrich.py incrementally:

  * reads new articles from The Race and Formula1.com and extracts factual news
    cards (general stories or session reports);
  * discovers all FIA event PDFs, retaining a cited document manifest, and
    extracts structured stewards' records only from decision/infringement PDFs.

Output is written to data/<gp>/news_auto.json and data/<gp>/penalties_auto.json,
which the engine (f1lib.py) merges into the News and Penalties pages at build
time — curated prose in the content_<gp>.py modules always takes precedence, so
automation only ever *fills gaps*. Every auto item keeps a link/back-reference
to its source so a commentator can verify it live.

Design goals
------------
* Incremental & idempotent — a manifest (data/<gp>/_seen.json) records every
  article URL and FIA filename already processed, so each run only sends *new*
  material to the extractor. Safe to run at any point across a weekend,
  repeatedly.
* Fail-safe — failed items remain retryable and hard failures make the run
  exit nonzero after saving successful work. If no external model is
  configured, deterministic extraction is used so the site build never depends
  on remote inference.

LLM backend (configurable via environment)
------------------------------------------
GitHub Models was retired on 30 July 2026. CI now uses the deterministic
fallback and delegates critical cross-page editing to a GitHub Copilot Agentic
Workflow. To use an OpenAI-compatible provider directly, set
LLM_ENDPOINT / LLM_MODEL / LLM_TOKEN (see README).

    LLM_ENDPOINT   OpenAI-compatible chat-completions URL
    LLM_MODEL      provider model id
    LLM_TOKEN      bearer token
    LLM_FAKE=1     skip the network model and use deterministic extraction

Usage
-----
    python3 enrich.py                 # enrich every registered GP
    python3 enrich.py --gp hungary    # just one
    python3 enrich.py --max 4         # cap new items processed per source
"""
import os
import re
import sys
import json
import html
import time
import datetime
import hashlib
import argparse
import urllib.request
import urllib.parse

import f1lib

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36")

DEFAULT_ENDPOINT = ""
DEFAULT_MODEL = ""

THE_RACE_RSS = "https://www.the-race.com/category/formula-1/rss/"
F1_LATEST = "https://www.formula1.com/en/latest/all.html"

SESSION_LABELS = ["Practice 1", "Practice 2", "Practice 3",
                  "Qualifying", "Sprint Qualifying", "Sprint", "Race"]

FAILURES = []


def _failure(message):
    FAILURES.append(message)
    print(f"  ! {message}")


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------
def _get(url, timeout=25, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "ignore")


def _sha(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def _strip(txt):
    txt = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", txt, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    return re.sub(r"\s+", " ", html.unescape(txt)).strip()


# --------------------------------------------------------------------------
# GP registry (reuse the same contexts build.py registers)
# --------------------------------------------------------------------------
def load_gps():
    """Import the GP contexts from build.py and attach enrichment hints."""
    import build
    gps = []
    for ctx in build.season_gps():
        c = dict(ctx)
        c["keywords"] = _keywords_for(c)
        gps.append(c)
    return gps


def active_gps(gps, lead_days=10):
    """The GPs worth spending LLM calls on right now.

    With a full season registered, enriching every round would burn tokens on
    races months away that have no coverage yet — and worse, general 2026 stories
    would get filed against a Grand Prix they have nothing to do with. Only three
    windows matter: any weekend currently running, the one just finished (whose
    reports and stewards' decisions are still landing), and the next one once it
    is close enough for genuine build-up coverage to exist.
    """
    today = datetime.datetime.now(datetime.timezone.utc).date()
    for c in gps:
        c.setdefault("dir", c.get("slug") or c.get("name", "").lower().replace(" ", "-"))
        c.setdefault("status", f1lib.event_status(c, today))
    live = [c for c in gps if c["status"] == "live"]
    future = [c for c in gps if c["status"] == "future"]
    past = [c for c in gps if c["status"] == "past"]
    nxt = [c for c in future[:1] if f1lib.days_to_start(c, today) <= lead_days]
    picked = live + nxt + past[-1:]
    seen, out = set(), []
    for c in picked:
        if c["dir"] not in seen:
            seen.add(c["dir"])
            out.append(c)
    return out


# Tokens that appear in circuit names but say nothing about *which* circuit.
# Without this, "circuit" alone would make almost every F1 article look relevant.
_GENERIC = {
    "circuit", "grand", "prix", "international", "autodromo", "autodromme",
    "street", "national", "nazionale", "speedway", "raceway", "motorsport",
    "racing", "track", "park", "arena",
}

_EVENT_MARKERS = {
    "australia": {"australia", "australian", "melbourne"},
    "china": {"china", "chinese", "shanghai"},
    "japan": {"japan", "japanese", "suzuka"},
    "bahrain": {"bahrain", "sepang", "malaysia", "malaysian"},
    "saudi-arabia": {"saudi", "jeddah"},
    "miami": {"miami"},
    "canada": {"canada", "canadian", "montreal"},
    "monaco": {"monaco", "monte carlo"},
    "spain": {"spain", "spanish", "madrid", "madring"},
    "austria": {"austria", "austrian", "spielberg"},
    "great-britain": {"britain", "british", "silverstone"},
    "belgium": {"belgium", "belgian", "spa", "spa-francorchamps"},
    "hungary": {"hungary", "hungarian", "hungaroring", "budapest"},
    "netherlands": {"dutch", "zandvoort", "netherlands"},
    "italy": {"italian", "monza", "italy", "tifosi"},
    "azerbaijan": {"azerbaijan", "baku"},
    "singapore": {"singapore", "marina bay"},
    "united-states": {"austin", "cota", "americas"},
    "mexico": {"mexico", "mexican", "rodriguez"},
    "brazil": {"brazil", "brazilian", "interlagos", "paulo"},
    "las-vegas": {"vegas"},
    "qatar": {"qatar", "lusail"},
    "united-arab-emirates": {"abu dhabi", "yas marina", "emirates"},
}


def _keywords_for(ctx):
    """Lower-case tokens that mark an article as belonging to this GP."""
    kws = set()
    name = ctx.get("name", "").lower()          # "hungarian grand prix"
    kws.add(name.replace(" grand prix", "").strip())   # "hungarian"
    cal = ctx.get("cal") or {}
    for source in (ctx.get("circuit", ""), cal.get("country", ""), cal.get("location", "")):
        for tok in re.split(r"[,\s]+", source.lower()):
            if len(tok) > 4 and tok not in _GENERIC:
                kws.add(tok)
    kws |= _EVENT_MARKERS.get(ctx.get("dir", ""), set())
    return {k for k in kws if k and k not in _GENERIC}


# --------------------------------------------------------------------------
# Manifest (per-GP _seen.json)
# --------------------------------------------------------------------------
def _seen_path(ctx):
    return os.path.join(DATA_DIR, ctx["dir"], "_seen.json")


def load_seen(ctx):
    try:
        with open(_seen_path(ctx), encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        d = {}
    d.setdefault("articles", [])
    d.setdefault("fia", [])
    return d


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_list(path):
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, list) else []
    except Exception:
        return []


# --------------------------------------------------------------------------
# Source discovery
# --------------------------------------------------------------------------
def the_race_articles():
    """Return [{title, url, when, body, source, src_kind}] from The Race RSS."""
    try:
        xml = _get(THE_RACE_RSS)
    except Exception as e:
        _failure(f"The Race RSS unavailable: {e}")
        return []
    if not re.search(r"<(?:rss|feed)\b", xml, re.I):
        _failure("The Race RSS returned an unrecognised response")
        return []
    out = []
    for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
        t = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", item, re.S)
        l = re.search(r"<link>(.*?)</link>", item, re.S)
        d = re.search(r"<pubDate>(.*?)</pubDate>", item, re.S)
        c = re.search(r"<content:encoded>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</content:encoded>", item, re.S)
        if not (t and l):
            continue
        out.append({
            "title": html.unescape(t.group(1)).strip(),
            "url": (l.group(1) or "").strip(),
            "when": _fmt_date(d.group(1) if d else ""),
            "date": _iso_date(d.group(1) if d else ""),
            "body": _strip(c.group(1))[:6000] if c else "",
            "source": "The Race", "src_kind": "race",
        })
    return out


def f1_articles(limit=30):
    """Return recent Formula1.com article stubs [{title,url,source,src_kind}]."""
    try:
        page = _get(F1_LATEST)
    except Exception as e:
        _failure(f"Formula1.com latest unavailable: {e}")
        return []
    # Capture the slug AND the trailing ID (article URLs are "<slug>.<id>"); the
    # ID is required — the slug-only URL 404s, which used to make f1_body empty.
    pairs = []
    seen_slugs = set()
    for slug, aid in re.findall(
            r"/en/latest/article/([a-z0-9-]+)\.([A-Za-z0-9_-]+)", page):
        if slug not in seen_slugs:
            seen_slugs.add(slug)
            pairs.append((slug, aid))
    out = []
    for slug, aid in pairs[:limit]:
        title = slug.replace("-", " ").strip().capitalize()
        out.append({
            "title": title,
            "url": f"https://www.formula1.com/en/latest/article/{slug}.{aid}",
            "when": "", "body": "", "source": "Formula1.com", "src_kind": "f1",
            "slug": slug,
        })
    if not pairs:
        _failure("Formula1.com latest returned no recognisable article links")
    return out


_F1_PAGE_CACHE = {}
_F1_BODY_CACHE = {}
_F1_META_CACHE = {}


def _f1_page(url):
    """Fetch a Formula1.com article page once per run.

    Both the body extractor and the headline/date extractor need the same HTML,
    and relevance testing runs across every GP in the active window, so without
    this a single article would be downloaded several times per run.
    """
    if url not in _F1_PAGE_CACHE:
        try:
            _F1_PAGE_CACHE[url] = _get(url)
        except Exception as e:
            _failure(f"Formula1.com article unavailable ({url}): {e}")
            _F1_PAGE_CACHE[url] = ""
    return _F1_PAGE_CACHE[url]


def _f1_body_cached(url):
    if url not in _F1_BODY_CACHE:
        _F1_BODY_CACHE[url] = f1_body(url)
    return _F1_BODY_CACHE[url]


def f1_meta(url):
    """Real headline + publication date for a Formula1.com article.

    The listing page only gives a URL slug, and a slug de-hyphenated into a
    sentence reads badly on screen ("Half term report racing bulls best and
    worst..."). The article page carries the proper headline and an ISO
    datePublished, so use those when available.
    """
    if url in _F1_META_CACHE:
        return _F1_META_CACHE[url]
    meta = {"title": "", "when": "", "date": ""}
    page = _f1_page(url)
    if not page:
        _F1_META_CACHE[url] = meta
        return meta
    m = (re.search(r'"headline"\s*:\s*"([^"]{3,200})"', page)
         or re.search(r"<title>([^<]{3,200})</title>", page))
    if m:
        meta["title"] = _strip(m.group(1)).split(" | ")[0].strip()
    d = re.search(r'"datePublished"\s*:\s*"(\d{4})-(\d{2})-(\d{2})', page)
    if d:
        months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
        meta["when"] = f"{int(d.group(3))} {months[int(d.group(2)) - 1]}"
        meta["date"] = f"{d.group(1)}-{d.group(2)}-{d.group(3)}"
    _F1_META_CACHE[url] = meta
    return meta


def f1_body(url):
    page = _f1_page(url)
    if not page:
        return ""
    m = re.search(r'"articleBody"\s*:\s*"(.*?)"\s*[,}]', page, re.S)
    if m:
        return _strip(m.group(1).encode().decode("unicode_escape", "ignore"))[:6000]
    # F1.com gates most of the body behind "F1 Unlocked" login, but the lede
    # paragraphs are in the static HTML. Keep sentence-like text, drop the
    # site chrome / promos that also render as <p>.
    _BOILER = ("opens in a new tab", "sign in", "subscribe", "f1 unlocked",
               "download the official f1 app", "ultimate companion",
               "world championship limited", "cookie", "newsletter",
               "exclusive f1 content", "vip experiences")
    keep = []
    for p in re.findall(r"<p[^>]*>(.*?)</p>", page, re.S):
        s = _strip(p)
        low = s.lower()
        if len(s) > 40 and "." in s and not any(b in low for b in _BOILER):
            keep.append(s)
    return " ".join(keep)[:6000]


def _fmt_date(rfc):
    m = re.search(r"(\d{1,2})\s+(\w{3})\s+\d{4}", rfc or "")
    return f"{m.group(1)} {m.group(2)}" if m else ""


_RSS_MONTHS = ("jan", "feb", "mar", "apr", "may", "jun",
               "jul", "aug", "sep", "oct", "nov", "dec")


def _iso_date(rfc):
    """ISO date from an RFC-822 pubDate, for sorting ('' if unparseable)."""
    m = re.search(r"(\d{1,2})\s+(\w{3})\s+(\d{4})", rfc or "")
    if not m or m.group(2).lower() not in _RSS_MONTHS:
        return ""
    month = _RSS_MONTHS.index(m.group(2).lower()) + 1
    return f"{m.group(3)}-{month:02d}-{int(m.group(1)):02d}"


def fia_documents(ctx):
    """Discover every event PDF; raise on failure rather than report no docs."""
    url = ctx.get("fia_url")
    if not url:
        return []
    try:
        page = _get(url)
        if not re.search(r"/system/files/|event-title|document-row|document-list|"
                         r"no documents|no decisions", page, re.I):
            raise ValueError("unrecognised FIA event response")
    except Exception as e:
        # Event pages can return 403/502 to GitHub-hosted runners even after
        # documents are published. Fall back to the season index, which embeds
        # the same document links.
        season_url = url.split("/event/", 1)[0]
        try:
            season_page = _get(season_url)
            event_name = re.sub(r"[^a-z0-9]+", " ", ctx["name"].lower()).strip()
            page = None

            # The *current* event's documents are rendered inline on the season
            # page itself (no AJAX round-trip needed) as
            # <div class="event-title active">Dutch Grand Prix</div><ul ...>...
            # A past/future event instead links out to an AJAX endpoint. Try the
            # inline block first since it needs no extra request.
            for m in re.finditer(
                    r'<div class="event-title active">\s*(.*?)\s*</div>(.*?)'
                    r'(?=<ul class="event-wrapper">|$)',
                    season_page, re.S | re.I):
                label, block = m.groups()
                if event_name in re.sub(r"[^a-z0-9]+", " ", _strip(label).lower()).strip():
                    page = block
                    break

            if page is None:
                nodes = re.findall(
                    r'<a[^>]*href=["\'][^"\']*/decision-document-list/nojs/(\d+)'
                    r'["\'][^>]*>(.*?)</a>',
                    season_page, re.S | re.I)
                node = next((node for node, label in nodes
                             if event_name in re.sub(
                                 r"[^a-z0-9]+", " ", _strip(label).lower()).strip()),
                            None)
                if not node:
                    raise ValueError(f"{ctx['name']} is not listed in the FIA season index")
                payload = json.loads(_get(
                    f"https://www.fia.com/decision-document-list/ajax/{node}"))
                page = "".join(command.get("data", "") for command in payload
                               if command.get("command") == "insert")
            print("  · FIA event page unavailable; checked season index instead")
        except Exception as fallback_error:
            raise RuntimeError(f"FIA documents page unavailable: {e}; "
                               f"season fallback failed: {fallback_error}") from fallback_error
    out, seen = [], set()
    # Do not constrain the storage subdirectory: technical PDFs also live
    # outside /decision-document/.
    for path in re.findall(
            r"/system/files/[^\"'<>\s?]+?\.pdf",
            html.unescape(page), re.I):
        fn = urllib.parse.unquote(path.rsplit("/", 1)[-1])
        if path in seen:
            continue
        seen.add(path)
        out.append({"filename": fn, "url": "https://www.fia.com" + path,
                    "categories": f1lib.fia_document_categories(fn)})
    if not out and not re.search(
            r'event-title|document-row|document-list|no documents|no decisions',
            page, re.I):
        raise ValueError("FIA response has no PDFs or recognisable document listing")
    return out


def is_fia_decision(pdf):
    """Keep broad discovery separate from stewards' extraction."""
    return "penalties" in f1lib.fia_document_categories(pdf["filename"])


def fia_decision_pdfs(ctx):
    """Compatibility helper: only actual decision/infringement candidates."""
    return [pdf for pdf in fia_documents(ctx) if is_fia_decision(pdf)]


def discover_fia(ctx):
    """Persist last good discovery separately from the latest attempt status."""
    if not ctx.get("fia_url"):
        return []
    directory = os.path.join(DATA_DIR, ctx["dir"])
    checked_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    status = {"checked_at": checked_at, "source_url": ctx["fia_url"]}
    try:
        documents = fia_documents(ctx)
    except Exception as e:
        status.update(ok=False, error=str(e))
        save_json(os.path.join(directory, "fia_discovery_status.json"), status)
        _failure(f"{ctx['dir']} FIA discovery failed: {e}")
        return []
    save_json(os.path.join(directory, "fia_documents.json"), {
        "source_url": ctx["fia_url"], "retrieved_at": checked_at,
        "documents": documents,
    })
    status["ok"] = True
    save_json(os.path.join(directory, "fia_discovery_status.json"), status)
    print(f"  · FIA discovery: {len(documents)} documents")
    return documents


def relevant(article, ctx):
    # Match the GP keywords against the headline, the URL slug **and** the body.
    # Many weekend stories (driver/team angles) omit the GP name from the title
    # but reference "Hungaroring"/"Hungarian" in the text — the body check keeps
    # those without pulling in generic or other-GP news that never mentions it.
    #
    # The Race arrives from RSS with its body already attached, but Formula1.com
    # only yields title+URL stubs, so for those the body has to be fetched here
    # or the body check silently never applies to them. Season-preview and
    # team-review pieces routinely bury the GP reference in the text, and those
    # are exactly the ones a commentator wants.
    headline = " ".join((article.get("title", ""), article.get("url", ""))).lower()
    hay = " ".join((
        article.get("title", ""),
        article.get("url", ""),
        article.get("body", ""),
    )).lower()
    target = _EVENT_MARKERS.get(ctx.get("dir", ""), set())
    other_in_headline = any(
        other != ctx.get("dir") and any(k in headline for k in markers)
        for other, markers in _EVENT_MARKERS.items()
    )
    if target and not any(k in headline for k in target) and other_in_headline:
        return False
    other_in_body = _competing_event_in_body(ctx, article.get("body", ""))
    if target and not any(k in headline for k in target) and other_in_body:
        return False
    if target and not any(k in hay for k in target):
        if any(
            other != ctx.get("dir") and any(k in hay for k in markers)
            for other, markers in _EVENT_MARKERS.items()
        ):
            return False
    if any(k in hay for k in ctx["keywords"]):
        _upgrade_f1_meta(article)
        return True
    if article.get("src_kind") == "f1" and not article.get("body"):
        body = _f1_body_cached(article["url"])
        if body:
            article["body"] = body          # reused by summarise_article
            if target and not any(k in headline for k in target):
                if _competing_event_in_body(ctx, body):
                    return False
            if any(k in body.lower() for k in ctx["keywords"]):
                _upgrade_f1_meta(article)
                return True
    return False


def _competing_event_in_body(ctx, body):
    text = body.lower()
    return any(
        other != ctx.get("dir") and any(k in text for k in markers)
        for other, markers in _EVENT_MARKERS.items()
    )


def _upgrade_f1_meta(article):
    """Replace a Formula1.com stub's slug-derived title and missing date with
    the article page's real headline and publication date.

    Every article about the current round matches on its URL slug alone, so the
    keyword test above short-circuits before any body fetch. That used to mean
    the round's *own* coverage — the stories most worth reading — was the only
    coverage stored with an unreadable slug title ("Red bull confirm hadjar to
    miss dutch grand prix...") and no date, while off-round stories that had to
    fall through to the body check got proper metadata. Undated cards then sort
    to the bottom of the wire feed, hiding that weekend's breaking news.
    """
    if article.get("src_kind") != "f1":
        return
    if article.get("title") and article.get("when") and article.get("date"):
        return
    meta = f1_meta(article["url"])
    if meta["title"]:
        article["title"] = meta["title"]
    if meta["when"]:
        article["when"] = meta["when"]
    if meta["date"]:
        article["date"] = meta["date"]


# --------------------------------------------------------------------------
# LLM
# --------------------------------------------------------------------------
def llm_json(system, user, retries=2):
    """Call the chat model and return parsed JSON, or None on failure."""
    if os.environ.get("LLM_FAKE"):
        return None  # caller falls back to a heuristic
    endpoint = os.environ.get("LLM_ENDPOINT", DEFAULT_ENDPOINT)
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL)
    token = (os.environ.get("LLM_TOKEN") or os.environ.get("GITHUB_TOKEN")
             or os.environ.get("GH_TOKEN"))
    if not endpoint or not model or not token:
        return None
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
    }
    body = json.dumps(payload).encode("utf-8")
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                endpoint, data=body,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": UA,
                })
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8", "ignore"))
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < retries:
                time.sleep(3 * (attempt + 1))
                continue
            print(f"  ! LLM HTTP {e.code}: {e.reason}")
            return None
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
                continue
            print(f"  ! LLM error: {e}")
            return None
    return None


NEWS_SYS = (
    "You are an F1 news editor building factual commentary reference cards. "
    "From the supplied article, produce a concise, neutral summary for a TV "
    "commentator. Do NOT invent facts or numbers; use only what the article "
    "states. Return STRICT JSON with keys: "
    "title (string, <=90 chars, punchy but factual), "
    "kind ('general' or 'session'), "
    "session (one of Practice 1, Practice 2, Practice 3, Qualifying, Sprint "
    "Qualifying, Sprint, Race — only if kind is 'session', else ''), "
    "paragraphs (array of 1-2 strings, ~40-90 words total). "
    "Use kind 'session' only for reports clearly about one completed on-track "
    "session's running/results; otherwise 'general'."
)

PEN_SYS = (
    "You extract a single FIA Formula 1 stewards' decision into STRICT JSON for "
    "a penalties tracker. Use only facts present in the document. Return keys: "
    "doc (e.g. 'Doc 41'), no (car number as string, '' if none), "
    "driver (full name, or 'Multiple drivers' for mass track-limits notes), "
    "team (short team name, '' if none), "
    "session (Practice 1/2/3, Qualifying, Sprint Qualifying, Sprint, Race, or ''), "
    "fact (one sentence: what happened), "
    "outcome (one sentence: the ruling and its effect), "
    "kind (one of: penalty, fine, warning, reprimand, noaction, note). "
    "Guidance: grid drop or time penalty -> 'penalty'; monetary fine -> 'fine'; "
    "'No further action'/'take no action' -> 'noaction'; deleted lap times / "
    "track limits note -> 'note'."
)


def summarise_article(a, ctx):
    """Return a news card dict (LLM, or heuristic fallback)."""
    body = a.get("body") or ""
    if not body and a.get("source") == "Formula1.com":
        body = f1_body(a["url"])
    if not body:
        return None
    user = (f"Grand Prix: {ctx['name']}.\nHeadline: {a['title']}\n\n"
            f"Article:\n{body}")
    js = llm_json(NEWS_SYS, user)
    if not js:
        js = _fake_news(a, body)
    if not js:
        return None
    kind = js.get("kind", "general")
    sess = js.get("session", "") if kind == "session" else ""
    if sess and sess not in SESSION_LABELS:
        sess, kind = "", "general"
    paras = js.get("paragraphs") or []
    paras = [p.strip() for p in paras if isinstance(p, str) and p.strip()]
    if not paras:
        return None
    return {
        "id": _sha(a["url"]),
        "url": a["url"],
        "title": (js.get("title") or a["title"]).strip()[:120],
        "source": a["source"], "src_kind": a["src_kind"],
        "when": a.get("when", ""),
        "date": a.get("date", ""),
        "kind": "session" if sess else "general",
        "session": sess,
        "paragraphs": paras[:2],
    }


def structure_decision(text, filename):
    """Return a stewards' decision dict (LLM, or heuristic fallback)."""
    text = _normalise_pdf_text(text)
    js = llm_json(PEN_SYS, "FIA stewards' document:\n\n" + text[:6000])
    if not js:
        js = _fake_decision(text)
    if not js:
        return None
    kind = js.get("kind", "note")
    if kind not in ("penalty", "fine", "warning", "reprimand", "noaction", "note"):
        kind = "note"
    if not js.get("doc"):
        m = re.search(r"document\s+(\d+)", text, re.I)
        js["doc"] = f"Doc {m.group(1)}" if m else ""
    record = {
        "doc": js.get("doc", ""), "no": str(js.get("no", "") or ""),
        "driver": js.get("driver", ""), "team": js.get("team", ""),
        "session": js.get("session", ""), "fact": js.get("fact", ""),
        "outcome": js.get("outcome", ""), "kind": kind,
        "source_pdf": filename,
    }
    repair_decision(record, text, filename)
    return record


def _normalise_pdf_text(text):
    # Keep line/column boundaries: flattening them confuses drivers and teams.
    return text.replace("\u00a0", " ").replace("\u202f", " ")


def decision_identity(text, filename=""):
    """Read subjects from this decision, never from a current-season roster."""
    text = _normalise_pdf_text(text)
    people = []
    for match in re.finditer(
            r"(?im)^\s*(?:No\.?\s*/\s*Driver|Car\s*/\s*Driver)\s+"
            r"(\d+)\s*[-–]\s*([^\n]+)", text):
        people.append((match[1], re.sub(r"\s+", " ", match[2]).strip()))
    if not people:
        people = re.findall(r"(?m)^Affected driver (\d+) - ([^\n]+)", text)
    if not people and re.search(r"Car\s+Driver\s+Competitor", text):
        # Layout extraction preserves the Driver/Competitor column boundary.
        prefix = r"\d+\s+" if re.search(r"Turn\s+Car\s+Driver", text) else ""
        for line in text.splitlines():
            line = re.sub(r"[ \t]{2,}", "\t", line)
            match = re.match(r"^\s*\d+\s+" + prefix + r"(\d+)\s+(.+?)\t", line)
            if match and len(line.split("\t")) >= 5 and not re.search(r"\d", match[2]):
                people.append((match[1], match[2].strip()))
    if not people and "eligible to start" in text.lower():
        people = re.findall(r"(?m)^\s*\d+\.\s*(\d+)\s*[-–]\s*(.+?)\s*[-–]\s*", text)
    subject = re.search(r"(?:^|[_ -])car[_ -]+(\d+)(?:[_ .-]|$)", filename, re.I)
    if not people and subject:
        number = subject[1]
        match = re.search(r"\bCar\s+" + number + r"\s*\(([^)]+)\)", text, re.I)
        # Three-letter timing abbreviations are not driver names.
        if match and " " in match[1].strip():
            people = [(number, match[1].strip())]
    people = list(dict.fromkeys(people))
    competitor = re.search(r"(?im)^\s*Competitor[ \t]+([^\n]+)", text)
    result = {"driver": "; ".join(name for _, name in people),
              "no": people[0][0] if len(people) == 1 else "",
              "team": competitor[1].strip() if competitor else ""}
    if people:
        result["identity_status"] = "named"
    elif subject or re.search(r"deleted lap times|Car\s+Driver", text, re.I):
        result.update(no=subject[1] if subject else "", identity_status="unavailable")
    elif competitor:
        result["identity_status"] = "team"
    elif re.search(r"\btemporar(?:y|ily)\s+stop|\bsession\b[^\n]*\b(?:stop|cancel|suspend)",
                   text, re.I):
        result["identity_status"] = "general"
    else:
        result["identity_status"] = "unavailable"
    return result


def repair_decision(record, text, filename):
    """Backfill source identities without rewriting existing editorial summaries."""
    text = _normalise_pdf_text(text)
    identity = decision_identity(text, filename)
    if identity["driver"] or not record.get("driver"):
        record.update(identity)
    session = re.search(r"(?im)^\s*Session[ \t]+([^\n]+)", text)
    if session and not record.get("session"):
        record["session"] = session[1].strip()
    outcome = _normalise_pdf_text(record.get("outcome", ""))
    source_outcome = re.search(r"(?im)^\s*Decision[ \t]+([^\n]+)", text)
    if source_outcome and outcome.startswith("-"):
        # Old unanchored extraction mistook a wrapper's Title for the ruling.
        record["outcome"] = source_outcome[1].strip()
        outcome = record["outcome"]
    if _no_action(outcome) or (source_outcome and _no_action(source_outcome[1])):
        record["kind"] = "noaction"
    record["identity_version"] = 1
    return record


def _no_action(text):
    return bool(re.search(
        r"\bno (?:further action|action)\b|\btake no action\b|"
        r"\bno penalty(?: is| will be)? (?:applied|imposed|warranted)\b",
        text, re.I))


# --------------------------------------------------------------------------
# Heuristic fallbacks (used only when LLM_FAKE=1 or no model is reachable) —
# these keep the pipeline testable offline; they are NOT a substitute for the
# model in production.
# --------------------------------------------------------------------------
def _fake_news(a, body):
    sents = re.split(r"(?<=[.!?])\s+", body)
    para = " ".join(sents[:3])[:400]
    title = a["title"]
    sess = next((s for s in SESSION_LABELS if s.lower() in title.lower()), "")
    return {"title": title, "kind": "session" if sess else "general",
            "session": sess, "paragraphs": [para] if para else []}


def _fake_decision(text):
    text = _normalise_pdf_text(text)
    def after(label):
        m = re.search(r"(?m)^\s*" + label + r"[ \t]+(.+)", text)
        return m.group(1).strip()[:200] if m else ""
    doc = re.search(r"document\s+(\d+)", text, re.I)
    fact = after("Fact")
    dec = after("Decision") or after("Infringement")
    session = after("Session")
    if not dec:
        # Some administrative rulings are prose, without a Decision/Fact table.
        flat = re.sub(r"\s+", " ", text).strip()
        permission = re.search(
            r"the Stewards determine the following F1 Cars are eligible to start the Race:"
            r"\s*(.+?)\s*The F1 Cars will be placed", flat, re.I)
        stop = re.search(
            r"The Stewards, exercising their authority.{1,300}?"
            r"decided to temporarily stop (Free Practice [123])\.", flat, re.I)
        if permission:
            fact, session = "Permission to start", "Race"
            dec = "Eligible to start the Race: " + permission.group(1)
        elif stop:
            fact = "Temporary session stoppage"
            session = stop.group(1).replace("Free Practice", "Practice")
            completion = re.search(r"the remainder of the session was completed\.",
                                   flat[stop.start():], re.I)
            dec = (flat[stop.start():stop.start() + completion.end()]
                   if completion else stop.group(0))
    low = (fact + " " + dec).lower()
    kind = ("fine" if "fine" in low else
            "noaction" if _no_action(dec) else
            "penalty" if "grid" in low or "penalt" in low or "time penalty" in low else
            "warning" if "warning" in low else
            "reprimand" if "reprimand" in low else "note")
    return {"doc": f"Doc {doc.group(1)}" if doc else "",
            **decision_identity(text), "session": session, "fact": fact,
            "outcome": dec, "kind": kind}


# --------------------------------------------------------------------------
# Per-GP enrichment
# --------------------------------------------------------------------------
def enrich_gp(ctx, max_items=6):
    print(f"{ctx['flag']} {ctx['name']}")
    seen = load_seen(ctx)
    news_path = os.path.join(DATA_DIR, ctx["dir"], "news_auto.json")
    pen_path = os.path.join(DATA_DIR, ctx["dir"], "penalties_auto.json")
    news = load_list(news_path)
    pens = load_list(pen_path)
    # Older versions marked failed attempts as seen. Output citations are the
    # evidence of successful extraction, so orphaned entries must be retryable.
    seen["articles"] = sorted({n["url"] for n in news if n.get("url")})
    seen["fia"] = sorted({p["source_pdf"] for p in pens if p.get("source_pdf")})
    added_news = added_pen = 0

    documents = discover_fia(ctx)

    # --- news: The Race + Formula1.com --------------------------------------
    # Seen-check first: relevance now fetches article bodies for Formula1.com,
    # so testing already-processed URLs would re-download them on every run.
    candidates = [a for a in (the_race_articles() + f1_articles())
                  if a["url"] not in seen["articles"] and relevant(a, ctx)]
    for a in candidates[:max_items]:
        try:
            card = summarise_article(a, ctx)
        except Exception as e:
            _failure(f"Article extraction failed ({a['url']}): {e}")
            continue
        if not card:
            _failure(f"Article extraction returned no usable content ({a['url']})")
            continue
        seen["articles"].append(a["url"])
        if not any(n.get("id") == card["id"] for n in news):
            news.append(card)
            added_news += 1
            print(f"  + news: {card['title']}")

    # --- penalties: FIA decision PDFs ---------------------------------------
    for pdf in documents:
        if not is_fia_decision(pdf):
            continue
        if pdf["filename"] in seen["fia"]:
            continue
        try:
            text = _pdf_text(pdf["url"])
            rec = structure_decision(text, pdf["filename"]) if text.strip() else None
        except Exception as e:
            _failure(f"Decision extraction failed ({pdf['url']}): {e}")
            continue
        if not rec or not rec.get("doc") or not rec.get("outcome"):
            _failure(f"Decision extraction returned no usable ruling ({pdf['url']})")
            continue
        seen["fia"].append(pdf["filename"])
        rec["source_url"] = pdf["url"]
        if not any(p.get("doc") == rec["doc"] for p in pens):
            pens.append(rec)
            added_pen += 1
            print(f"  + penalty: {rec['doc']} — {rec.get('driver','')} "
                  f"({rec.get('kind')})")

    # sort for stable output. Chronological by real publication date — the old
    # key sorted the display string ("12 Aug" before "6 Aug"), which scrambled
    # the feed the moment a month rolled over.
    news.sort(key=lambda n: (f1lib.news_sort_key(n), n.get("title", "")))
    pens.sort(key=lambda p: int(re.search(r"(\d+)", p.get("doc", "0")).group(1))
              if re.search(r"(\d+)", p.get("doc", "")) else 9999)

    save_json(news_path, news)
    save_json(pen_path, pens)
    save_json(_seen_path(ctx), seen)
    print(f"  = {added_news} new news, {added_pen} new decisions "
          f"({len(news)} / {len(pens)} total)")
    return added_news + added_pen


def _pdf_text(url):
    """Extract text from a FIA PDF. Requires pypdf (installed in the workflow)."""
    try:
        import pypdf
    except Exception:
        print("  ! pypdf not installed — skipping PDF extraction "
              "(pip install pypdf)")
        return ""
    try:
        raw = _get(url, binary=True, timeout=40)
        return pdf_text(raw)
    except Exception as e:
        print(f"  ! PDF extract failed ({url.rsplit('/', 1)[-1]}): {e}")
        return ""


def pdf_text(raw):
    """Preserve table columns only where they are needed for named subjects."""
    import io
    import pypdf
    reader = pypdf.PdfReader(io.BytesIO(raw))
    pages = []
    for page in reader.pages:
        text = _normalise_pdf_text(page.extract_text() or "")
        if re.search(r"Car\s+Driver\s+Competitor", text):
            layout = page.extract_text(extraction_mode="layout")
            if layout.strip():
                text = re.sub(r"[^\S\n]{2,}", "\t", _normalise_pdf_text(layout))
        pages.append(text)
    text = "\n".join(pages)
    for number, name in _pdf_table_drivers(raw):
        text += f"\nAffected driver {number} - {name}"
    return text


def _pdf_table_drivers(raw):
    """Use the PDF's own column coordinates when text extraction merges cells."""
    try:
        import pymupdf
    except ImportError:
        return []
    people, columns = [], None
    with pymupdf.open(stream=raw, filetype="pdf") as document:
        for page in document:
            words = page.get_text("words")
            top = 0
            for driver in (word for word in words if word[4] == "Driver"):
                header = {word[4]: word for word in words if abs(word[1] - driver[1]) < 2}
                if "Car" in header and "Competitor" in header:
                    columns = (header["Car"][0], driver[0], header["Competitor"][0])
                    top = driver[3]
                    break
            if not columns:
                continue
            car_x, driver_x, team_x = columns
            ends = [word[1] for word in words
                    if word[1] > top and word[0] < driver_x
                    and word[4] in ("Infringement", "Decision", "Note", "Reasons")]
            bottom = min(ends) if ends else page.rect.height
            for car in words:
                if (top < car[1] < bottom and car_x - 2 <= car[0] < driver_x - 2
                        and car[4].isdigit()):
                    name = " ".join(word[4] for word in sorted(words, key=lambda word: word[0])
                                    if abs(word[1] - car[1]) < 3
                                    and driver_x - 2 <= word[0] < team_x - 2)
                    if " " in name and not re.search(r"\d", name):
                        people.append((car[4], name))
            if ends:
                columns = None
    return list(dict.fromkeys(people))


# --------------------------------------------------------------------------
def main():
    FAILURES.clear()
    _F1_PAGE_CACHE.clear()
    _F1_BODY_CACHE.clear()
    _F1_META_CACHE.clear()
    ap = argparse.ArgumentParser(description="LLM enrichment for the F1 hub.")
    ap.add_argument("--gp", help="only this GP dir (e.g. hungary)")
    ap.add_argument("--all", action="store_true",
                    help="enrich every registered GP instead of just the active window")
    ap.add_argument("--max", type=int, default=6,
                    help="max new articles processed per GP per run")
    args = ap.parse_args()

    gps = load_gps()
    if args.gp:
        gps = [g for g in gps if g["dir"] == args.gp]
        if not gps:
            print(f"No GP with dir '{args.gp}'")
            return 1
    elif not args.all:
        gps = active_gps(gps)
        print("Active window: " + ", ".join(f'{g["dir"]} ({g["status"]})' for g in gps))

    endpoint = os.environ.get("LLM_ENDPOINT", DEFAULT_ENDPOINT)
    backend = ("HEURISTIC (LLM_FAKE)" if os.environ.get("LLM_FAKE")
               else endpoint or "HEURISTIC (no LLM configured)")
    print(f"Enrichment backend: {backend}\n")

    total = 0
    for ctx in gps:
        try:
            total += enrich_gp(ctx, max_items=args.max)
        except Exception as e:
            _failure(f"{ctx['dir']} enrichment error: {e}")
        print()
    print(f"Done — {total} new item(s) added across {len(gps)} GP(s).")
    if FAILURES:
        print(f"Failed — {len(FAILURES)} error(s); successful work saved, failed items will retry.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
