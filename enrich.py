"""
F1 Commentary Hub — LLM enrichment pipeline.

This is the *intelligent* half of the skill. Where build.py deterministically
parses live timing/weather, enrich.py does the LLM-type work that would
otherwise need a human in the loop each time:

  * reads new articles from The Race and Formula1.com and summarises each into a
    factual news card (general story or session report);
  * downloads new FIA event *decision* PDFs and turns each into a structured
    stewards' record (driver, session, fact, ruling, kind).

Output is written to data/<gp>/news_auto.json and data/<gp>/penalties_auto.json,
which the engine (f1lib.py) merges into the News and Penalties pages at build
time — curated prose in the content_<gp>.py modules always takes precedence, so
the LLM only ever *fills gaps*. Every auto item keeps a link/back-reference to
its source so a commentator can verify it live.

Design goals
------------
* Incremental & idempotent — a manifest (data/<gp>/_seen.json) records every
  article URL and FIA filename already processed, so each run only sends *new*
  material to the model. Safe to run at any point across a weekend, repeatedly.
* Fail-safe — any single item that errors is skipped; if no model is reachable
  the script exits 0 without changing anything, so the site build never breaks.

LLM backend (configurable via environment)
------------------------------------------
Default: **GitHub Models** — free, native to GitHub Actions, no secret needed.
The workflow grants `permissions: models: read` and the built-in GITHUB_TOKEN is
used automatically. To use Azure OpenAI instead (higher limits, your Azure
credit), set LLM_ENDPOINT / LLM_MODEL / LLM_TOKEN (see README).

    LLM_ENDPOINT   chat-completions URL   (default: GitHub Models)
    LLM_MODEL      model id               (default: openai/gpt-4o-mini)
    LLM_TOKEN      bearer token           (default: GITHUB_TOKEN, then GH_TOKEN)
    LLM_FAKE=1     skip the network model and use a deterministic heuristic
                   extractor (for offline plumbing tests only)

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
import hashlib
import argparse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36")

DEFAULT_ENDPOINT = "https://models.github.ai/inference/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"

THE_RACE_RSS = "https://www.the-race.com/category/formula-1/rss/"
F1_LATEST = "https://www.formula1.com/en/latest/all.html"

# FIA filename keywords that mark an actual *decision/infringement* document
# worth structuring (skips classifications, entry lists, scrutineering, etc.).
FIA_DECISION_KEYS = ("infringement", "decision", "penalty", "reprimand",
                     "fine", "disqualif", "protest")
FIA_SKIP_KEYS = ("summons", "classification", "scrutineering", "entry_list",
                 "provisional_starting_grid", "car_presentation", "self_scrut")

SESSION_LABELS = ["Practice 1", "Practice 2", "Practice 3",
                  "Qualifying", "Sprint Qualifying", "Sprint", "Race"]


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
    for ctx in (build.HUNGARY, build.BELGIUM):
        c = dict(ctx)
        c["keywords"] = _keywords_for(c)
        gps.append(c)
    return gps


def _keywords_for(ctx):
    """Lower-case tokens that mark an article as belonging to this GP."""
    kws = set()
    name = ctx.get("name", "").lower()          # "hungarian grand prix"
    kws.add(name.replace(" grand prix", "").strip())   # "hungarian"
    circuit = ctx.get("circuit", "").lower()
    for tok in re.split(r"[,\s]+", circuit):
        if len(tok) > 4:
            kws.add(tok)
    extra = {
        "hungary": {"hungary", "hungarian", "hungaroring", "budapest"},
        "belgium": {"belgium", "belgian", "spa", "spa-francorchamps"},
    }
    kws |= extra.get(ctx.get("dir", ""), set())
    return {k for k in kws if k}


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
        print(f"  ! The Race RSS unavailable: {e}")
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
            "body": _strip(c.group(1))[:6000] if c else "",
            "source": "The Race", "src_kind": "race",
        })
    return out


def f1_articles(limit=30):
    """Return recent Formula1.com article stubs [{title,url,source,src_kind}]."""
    try:
        page = _get(F1_LATEST)
    except Exception as e:
        print(f"  ! Formula1.com latest unavailable: {e}")
        return []
    slugs = []
    for m in re.findall(r"/en/latest/article/([a-z0-9-]+)", page):
        if m not in slugs:
            slugs.append(m)
    out = []
    for slug in slugs[:limit]:
        title = slug.replace("-", " ").strip().capitalize()
        out.append({
            "title": title,
            "url": f"https://www.formula1.com/en/latest/article/{slug}",
            "when": "", "body": "", "source": "Formula1.com", "src_kind": "f1",
            "slug": slug,
        })
    return out


def f1_body(url):
    try:
        page = _get(url)
    except Exception:
        return ""
    m = re.search(r'"articleBody"\s*:\s*"(.*?)"\s*[,}]', page, re.S)
    if m:
        return _strip(m.group(1).encode().decode("unicode_escape", "ignore"))[:6000]
    paras = re.findall(r"<p[^>]*>(.*?)</p>", page, re.S)
    text = " ".join(_strip(p) for p in paras if len(_strip(p)) > 40)
    return text[:6000]


def _fmt_date(rfc):
    m = re.search(r"(\d{1,2})\s+(\w{3})\s+\d{4}", rfc or "")
    return f"{m.group(1)} {m.group(2)}" if m else ""


def fia_decision_pdfs(ctx):
    """Return [{filename, url}] for FIA decision documents for this GP."""
    url = ctx.get("fia_url")
    if not url:
        return []
    try:
        page = _get(url)
    except Exception as e:
        print(f"  ! FIA documents page unavailable: {e}")
        return []
    out, seen = [], set()
    for path in re.findall(r"/system/files/decision-document/[^\"'?]+\.pdf", page):
        fn = path.rsplit("/", 1)[-1].lower()
        if fn in seen:
            continue
        seen.add(fn)
        if any(s in fn for s in FIA_SKIP_KEYS):
            continue
        if not any(k in fn for k in FIA_DECISION_KEYS):
            continue
        out.append({"filename": fn, "url": "https://www.fia.com" + path})
    return out


def relevant(article, ctx):
    hay = (article.get("title", "") + " " + article.get("url", "")).lower()
    return any(k in hay for k in ctx["keywords"])


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
    if not token:
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
        "kind": "session" if sess else "general",
        "session": sess,
        "paragraphs": paras[:2],
    }


def structure_decision(text, filename):
    """Return a stewards' decision dict (LLM, or heuristic fallback)."""
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
    return {
        "doc": js.get("doc", ""), "no": str(js.get("no", "") or ""),
        "driver": js.get("driver", ""), "team": js.get("team", ""),
        "session": js.get("session", ""), "fact": js.get("fact", ""),
        "outcome": js.get("outcome", ""), "kind": kind,
        "source_pdf": filename,
    }


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
    def after(label):
        m = re.search(label + r"\s+(.+)", text)
        return m.group(1).strip()[:200] if m else ""
    doc = re.search(r"document\s+(\d+)", text, re.I)
    car = re.search(r"\bCar\s+(\d+)", text)
    fact = after("Fact")
    dec = after("Decision") or after("Infringement")
    low = (fact + " " + dec).lower()
    kind = ("fine" if "fine" in low else
            "noaction" if "no further action" in low or "take no action" in low else
            "penalty" if "grid" in low or "penalt" in low or "time penalty" in low else
            "warning" if "warning" in low else
            "reprimand" if "reprimand" in low else "note")
    return {"doc": f"Doc {doc.group(1)}" if doc else "", "no": car.group(1) if car else "",
            "driver": "", "team": "", "session": "", "fact": fact,
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
    added_news = added_pen = 0

    # --- news: The Race + Formula1.com --------------------------------------
    candidates = [a for a in (the_race_articles() + f1_articles())
                  if relevant(a, ctx) and a["url"] not in seen["articles"]]
    for a in candidates[:max_items]:
        card = summarise_article(a, ctx)
        seen["articles"].append(a["url"])          # mark seen even if it failed
        if card and not any(n.get("id") == card["id"] for n in news):
            news.append(card)
            added_news += 1
            print(f"  + news: {card['title']}")

    # --- penalties: FIA decision PDFs ---------------------------------------
    for pdf in fia_decision_pdfs(ctx):
        if pdf["filename"] in seen["fia"]:
            continue
        text = _pdf_text(pdf["url"])
        seen["fia"].append(pdf["filename"])
        if not text:
            continue
        rec = structure_decision(text, pdf["filename"])
        if rec and rec.get("doc") and not any(
                p.get("doc") == rec["doc"] for p in pens):
            pens.append(rec)
            added_pen += 1
            print(f"  + penalty: {rec['doc']} — {rec.get('driver','')} "
                  f"({rec.get('kind')})")

    # sort for stable output
    news.sort(key=lambda n: (n.get("when", ""), n.get("title", "")))
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
        import io
        raw = _get(url, binary=True, timeout=40)
        reader = pypdf.PdfReader(io.BytesIO(raw))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    except Exception as e:
        print(f"  ! PDF extract failed ({url.rsplit('/', 1)[-1]}): {e}")
        return ""


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="LLM enrichment for the F1 hub.")
    ap.add_argument("--gp", help="only this GP dir (e.g. hungary)")
    ap.add_argument("--max", type=int, default=6,
                    help="max new articles processed per GP per run")
    args = ap.parse_args()

    gps = load_gps()
    if args.gp:
        gps = [g for g in gps if g["dir"] == args.gp]
        if not gps:
            print(f"No GP with dir '{args.gp}'")
            return 1

    backend = ("HEURISTIC (LLM_FAKE)" if os.environ.get("LLM_FAKE")
               else os.environ.get("LLM_ENDPOINT", DEFAULT_ENDPOINT))
    print(f"Enrichment backend: {backend}\n")

    total = 0
    for ctx in gps:
        try:
            total += enrich_gp(ctx, max_items=args.max)
        except Exception as e:
            print(f"  ! {ctx['dir']} enrichment error: {e}")
        print()
    print(f"Done — {total} new item(s) added across {len(gps)} GP(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
