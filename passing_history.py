"""Sourced on-track passing counts, kept separate from F1DB result statistics."""
import argparse
import datetime as dt
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

import circuit_history


ROOT = Path(__file__).resolve().parent
SCHEMA_VERSION = 1
FEED = "https://racingpass.net/feed/"
SOURCE = {
    "name": "RacingPass",
    "url": "https://racingpass.net/azerbaijan-gp-had-47-overtakes-most-at-baku-since-2019/",
    "methodology": (
        "Community-counted on-track passes for position. Excludes lap one, pit-stop gains, "
        "passes of cars off track/spun or with major reliability problems, and lapping/unlapping. "
        "No separate DRS breakdown is provided here."
    ),
    "attribution": "Race-total statistics reported by RacingPass; not official FIA statistics. "
                   "Article prose and individual pass logs are not reproduced.",
}


def _read(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an overtaking JSON object: {path.name}")
    return value


def _https(url):
    if not isinstance(url, str):
        raise ValueError("Invalid overtaking source URL")
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or any(ord(char) < 33 for char in url)):
        raise ValueError("Overtaking source URL must be public HTTPS")
    return url


def _validate(snapshot):
    if snapshot.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported overtaking snapshot schema")
    stamp = dt.datetime.fromisoformat(snapshot["checked_at"])
    if stamp.tzinfo is None:
        raise ValueError("Overtaking source timestamp needs a timezone")
    sources, races = snapshot["sources"], snapshot["races"]
    if not isinstance(sources, dict) or not sources or not isinstance(races, list):
        raise ValueError("Invalid overtaking source/record collection")
    for identity, source in sources.items():
        if not re.fullmatch(r"[a-z0-9-]+", identity) or not isinstance(source, dict):
            raise ValueError("Invalid overtaking source identity")
        for key in ("name", "methodology", "attribution", "url"):
            if not isinstance(source.get(key), str) or not source[key].strip():
                raise ValueError(f"Missing overtaking source {key}")
        _https(source["url"])
    seen = set()
    for row in races:
        if (not isinstance(row, dict) or row.get("series_id") not in sources
                or type(row.get("race_id")) is not int or row["race_id"] < 1
                or not isinstance(row.get("circuit_id"), str) or not row["circuit_id"]
                or type(row.get("overtakes")) is not int or row["overtakes"] < 0):
            raise ValueError("Invalid sourced overtaking count or race identity")
        dt.date.fromisoformat(row["date"])
        _https(row["source_url"])
        key = row["series_id"], row["race_id"]
        if key in seen:
            raise ValueError("Duplicate overtaking count for a source/race")
        seen.add(key)
    return snapshot


def context(ctx, profile, root=None):
    """Read-only, same-venue counts for the record book's ten most recent races."""
    result = {"series": [], "error": "", "checked_at": ""}
    if not profile or not profile.get("completed_races"):
        return result
    root = Path(root or ROOT)
    path = root / "data" / "passing_history.json"
    status_path = root / "data" / "passing_history_status.json"
    try:
        status = _read(status_path) if status_path.exists() else {}
        if any(not isinstance(status.get(key, ""), str) for key in ("checked_at", "error")):
            raise ValueError("Invalid overtaking refresh status")
        result["checked_at"] = status.get("checked_at", "")
        result["error"] = status.get("error", "")
        if not path.exists():
            return result
        snapshot = _validate(_read(path))
        result["checked_at"] = result["checked_at"] or snapshot["checked_at"]
        cutoff = ctx["race_date"]
        if profile.get("cutoff_date", cutoff) != cutoff:
            raise ValueError("Overtaking cutoff disagrees with the circuit record book")
        dt.date.fromisoformat(cutoff)
        cutoff = min(cutoff, dt.datetime.now(dt.timezone.utc).date().isoformat())
        circuit = profile["circuit"]["id"]
        editions = {}
        for race in profile.get("recent_winners", []):
            if race["circuit_id"] != circuit:
                raise ValueError("Previous edition belongs to a different venue")
            if race["date"] < cutoff:
                editions[race["race_id"]] = race
        editions = sorted(editions.values(), key=lambda row: (row["date"], row["race_id"]),
                          reverse=True)[:10]
        lookup = {(row["series_id"], row["race_id"]): row for row in snapshot["races"]}
        for identity, source in snapshot["sources"].items():
            rows = []
            for race in editions:
                count = lookup.get((identity, race["race_id"]))
                if count and (count["circuit_id"] != circuit or count["date"] != race["date"]):
                    raise ValueError("Overtaking count disagrees with the F1DB venue/date")
                rows.append({
                    "race_id": race["race_id"], "year": race["year"], "name": race["name"],
                    "date": race["date"], "race_url": race["url"],
                    "overtakes": count["overtakes"] if count else None,
                    "source_url": count["source_url"] if count else "",
                })
            if any(row["overtakes"] is not None for row in rows):
                result["series"].append({**source, "id": identity, "races": rows})
        return result
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {**result, "series": [], "error": "; ".join(
            filter(None, (result["error"], str(error))))}


def _publisher_url(url):
    _https(url)
    parsed = urllib.parse.urlsplit(url)
    if parsed.hostname != "racingpass.net" or parsed.port not in (None, 443):
        raise ValueError("Overtaking collection only accepts the configured primary publisher")
    return url


class _Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _publisher_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _fetch(url):
    _publisher_url(url)
    request = urllib.request.Request(url, headers={"User-Agent": "f1-commentary evidence refresh"})
    with urllib.request.build_opener(_Redirect()).open(request, timeout=30) as response:
        _publisher_url(response.geturl())
        data = response.read(2_000_001)
    if not data or len(data) > 2_000_000:
        raise ValueError("Empty or oversized overtaking publication")
    return data.decode("utf-8-sig")


class _Article(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.active = []
        self.skip = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if not self.skip and tag in ("p", "li", "h1", "h2", "h3", "h4", "h5", "h6"):
            self.active.append([tag, []])

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if self.active and self.active[-1][0] == tag:
            kind, parts = self.active.pop()
            self.blocks.append((kind, re.sub(r"\s+", " ", "".join(parts)).strip()))

    def handle_data(self, text):
        if not self.skip:
            for _, parts in self.active:
                parts.append(text)


def parse_article(text):
    """Extract factual race totals only, never copy the individual pass log."""
    article = _Article(text)
    plain = " ".join(value for _, value in article.blocks).lower()
    if not all(marker in plain for marker in (
            "only on track passes for position", "pitting", "major reliability",
            "lapping and unlapping do not count", "overtakes on lap 1 do not count")):
        raise ValueError("Publisher counting rules are absent or changed; review required")
    primary = set()
    for tag, value in article.blocks:
        if tag == "p":
            primary.update(re.findall(
                r"\bThe (20\d{2}) (.+?) (?:GP|Grand Prix) had (\d+) overtakes\b", value, re.I))
    if len(primary) != 1:
        raise ValueError("Expected one explicit main Grand Prix/year/overtaking total")
    year, gp, total = primary.pop()
    if "sprint" in gp.lower():
        raise ValueError("Sprint counts are not Grand Prix totals")
    rows = [{"year": int(year), "gp": gp, "overtakes": int(total)}]
    season = False
    for tag, value in article.blocks:
        if tag.startswith("h"):
            season = bool(re.fullmatch(r"Numbers for the Season so far", value, re.I))
        elif season and tag == "li":
            match = re.fullmatch(r"(.+?)\s*[-–—]\s*(\d+)(?:\s*\(Sprint\s*[-–—]\s*\d+\))?",
                                 value, re.I)
            if not match:
                raise ValueError("Season totals format changed; review required")
            rows.append({"year": int(year), "gp": match[1].strip(), "overtakes": int(match[2])})
    return rows


def _normal(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    value = re.sub(r"\bgrand prix\b|\bgp\b", "", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def join_facts(articles, data, today):
    aliases = {}
    for gp in data["grands-prix"]:
        for key in ("id", "name", "fullName", "shortName"):
            if gp.get(key):
                aliases.setdefault(_normal(gp[key]), set()).add(gp["id"])
    aliases.setdefault("brazil", set()).add("sao-paulo")
    aliases.setdefault("mexico city", set()).add("mexico")
    aliases.setdefault("usa", set()).add("united-states")
    completed = {row["raceId"] for row in data["races-race-results"]}
    result = {}
    for article in articles:
        url = _publisher_url(article["url"])
        for fact in article["facts"]:
            if (type(fact.get("year")) is not int or type(fact.get("overtakes")) is not int
                    or fact["overtakes"] < 0):
                raise ValueError("Invalid reviewed/parsed overtaking fact")
            candidates = [race for race in data["races"] if race["year"] == fact["year"]
                          and race["id"] in completed and race["date"] < today.isoformat()]
            if fact.get("circuit_id"):
                candidates = [race for race in candidates if race["circuitId"] == fact["circuit_id"]]
            else:
                ids = aliases.get(_normal(fact["gp"]), set())
                candidates = [race for race in candidates if race["grandPrixId"] in ids]
            if len(candidates) != 1:
                raise ValueError(f"Overtaking fact has no unique completed F1DB race: {fact}")
            race = candidates[0]
            row = {"series_id": "racingpass", "race_id": race["id"], "date": race["date"],
                   "circuit_id": race["circuitId"], "overtakes": fact["overtakes"], "source_url": url}
            previous = result.get(race["id"])
            if previous and previous["overtakes"] != row["overtakes"]:
                raise ValueError(f"Conflicting primary-source counts for F1DB race {race['id']}")
            result[race["id"]] = row
    return sorted(result.values(), key=lambda row: (row["date"], row["race_id"]))


def refresh(root=None, now=None, force=False, reviewed_only=False):
    root = Path(root or ROOT)
    now = now or dt.datetime.now(dt.timezone.utc)
    path = root / "data/passing_history.json"
    status_path = root / "data/passing_history_status.json"
    previous = _validate(_read(path)) if path.exists() else {}
    status = _read(status_path) if status_path.exists() else {}
    if not force and not reviewed_only and previous and status.get("mode") == "automatic":
        age = now - dt.datetime.fromisoformat(status["checked_at"])
        if dt.timedelta() <= age < dt.timedelta(hours=6):
            return previous, status
    attempts = []
    try:
        reviewed = _read(root / "data/passing_history_reviewed.json")
        articles = reviewed["articles"]
        if not isinstance(articles, list) or not articles:
            raise ValueError("Reviewed primary-source seed articles are missing")
        urls = list(dict.fromkeys(
            [article["url"] for article in articles] + previous.get("article_urls", [])))
        if not reviewed_only:
            try:
                feed = ET.fromstring(_fetch(FEED))
                if feed.tag != "rss" or feed.find("channel") is None:
                    raise ValueError("Unsupported publisher feed")
                for item in feed.findall("./channel/item"):
                    if re.search(r"overtakes?", item.findtext("title", ""), re.I):
                        url = _publisher_url(item.findtext("link", ""))
                        if url not in urls:
                            urls.append(url)
                attempts.append({"url": FEED, "ok": True, "error": ""})
            except (OSError, ValueError, ET.ParseError) as error:
                attempts.append({"url": FEED, "ok": False, "error": str(error)})
            if len(urls) > 40:
                raise ValueError("Publisher article scope exceeds the bounded refresh; review required")
            for url in urls:
                try:
                    facts = parse_article(_fetch(url))
                    articles.append({"url": url, "facts": facts})
                    attempts.append({"url": url, "ok": True, "error": ""})
                except (OSError, ValueError) as error:
                    attempts.append({"url": url, "ok": False, "error": str(error)})
        cache = root / "__pycache__/circuit-history"
        release = circuit_history._release(cache, now, force=False)
        data, db_source = circuit_history._database(release, cache)
        rows = join_facts(articles, data, now.date())
        merged = {row["race_id"]: row for row in previous.get("races", [])}
        merged.update({row["race_id"]: row for row in rows})
        snapshot = _validate({
            "schema_version": SCHEMA_VERSION, "checked_at": now.isoformat(timespec="seconds"),
            "sources": {"racingpass": SOURCE}, "f1db_release": db_source["release"],
            "article_urls": urls,
            "races": sorted(merged.values(), key=lambda row: (row["date"], row["race_id"])),
        })
        failed = sum(not attempt["ok"] for attempt in attempts)
        status = {
            "checked_at": now.isoformat(timespec="seconds"), "ok": not failed,
            "mode": "reviewed-backfill" if reviewed_only else "automatic", "attempts": attempts,
            "error": (f"{failed} RacingPass source checks were blocked or changed format; "
                      "previously sourced counts are retained, with gaps shown explicitly." if failed else ""),
        }
        circuit_history._write(path, snapshot)
        circuit_history._write(status_path, status)
        return snapshot, status
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        circuit_history._write(status_path, {
            "checked_at": now.isoformat(timespec="seconds"), "ok": False,
            "mode": "automatic", "attempts": attempts, "error": str(error),
        })
        raise ValueError(f"Overtaking refresh failed; last-good snapshot retained: {error}") from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Ignore the six-hour source-check cache")
    parser.add_argument("--reviewed-only", action="store_true",
                        help="Build the initial backfill from reviewed primary-source facts")
    args = parser.parse_args()
    try:
        snapshot, status = refresh(force=args.force, reviewed_only=args.reviewed_only)
    except ValueError as error:
        print(error)
        return 1
    print(f"Overtaking history: {len(snapshot['races'])} sourced Grand Prix totals")
    for attempt in status.get("attempts", []):
        if not attempt["ok"]:
            print(f"  {attempt['url']}: {attempt['error']}")
    if status["error"]:
        print(status["error"])
    return 0 if status["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
