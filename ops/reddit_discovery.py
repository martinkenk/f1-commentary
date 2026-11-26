"""Discover independently verifiable F1 headlines using an approved Reddit app."""
import base64
import datetime as dt
import html.parser
import json
import os
from pathlib import Path
import re
import stat
import urllib.error
import urllib.parse
import urllib.request

import news_briefing

UTC = dt.timezone.utc
HOSTS = {
    "formula1.com", "www.formula1.com", "fia.com", "www.fia.com",
    "the-race.com", "www.the-race.com", "motorsport.com", "www.motorsport.com",
    "autosport.com", "www.autosport.com", "bbc.com", "www.bbc.com",
    "haasf1team.com", "www.haasf1team.com",
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _read_json(response):
    data = response.read(2 * 1024 * 1024 + 1)
    if len(data) > 2 * 1024 * 1024:
        raise ValueError("Reddit response exceeds size limit")
    return json.loads(data)


class TitleParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def _source(url):
    if not isinstance(url, str) or len(url) > 2048:
        return None
    try:
        parsed = urllib.parse.urlsplit(url)
        host = parsed.hostname
        if (parsed.scheme != "https" or host not in HOSTS or parsed.username or parsed.password
                or parsed.port not in (None, 443) or not parsed.path.strip("/")):
            return None
    except ValueError:
        return None
    return host


def _config(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError("Reddit credentials cannot be a symbolic link")
    if not path.exists():
        return None
    info = path.lstat()
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) & 0o077):
        raise ValueError("Reddit credentials must be a private, owner-only regular file")
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or config.get("approved") is not True:
        raise ValueError("Reddit API approval must be confirmed in the private configuration")
    for key in ("client_id", "client_secret", "user_agent"):
        if not isinstance(config.get(key), str) or not config[key].strip():
            raise ValueError(f"Reddit configuration is missing {key}")
    if not re.fullmatch(r"[^:\s]+:[^:\s]+:[^\s]+ \(by /u/[A-Za-z0-9_-]+\)", config["user_agent"]):
        raise ValueError("Reddit User-Agent must identify platform, app, version and Reddit user")
    return config


def discover(path, now=None):
    """Return status and publisher titles, without retaining Reddit user content."""
    now = now or dt.datetime.now(UTC)
    status = {"checked_at": now.isoformat()}
    try:
        config = _config(path)
    except (OSError, ValueError, TypeError) as error:
        status.update(status="error", detail=f"Reddit configuration error: {error}")
        return status, []
    if config is None:
        status.update(status="not_configured",
                      detail="Reddit discovery needs approved OAuth credentials.")
        return status, []
    opener = urllib.request.build_opener(NoRedirect())
    basic = base64.b64encode(
        (config["client_id"] + ":" + config["client_secret"]).encode()).decode("ascii")
    token_request = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=urllib.parse.urlencode({"grant_type": "client_credentials"}).encode(),
        headers={"Authorization": "Basic " + basic, "User-Agent": config["user_agent"]})
    try:
        with opener.open(token_request, timeout=15) as response:
            token = _read_json(response)["access_token"]
        if not isinstance(token, str) or not token:
            raise ValueError("Reddit OAuth response lacks an access token")
        posts = []
        for listing in ("new", "hot"):
            request = urllib.request.Request(
                f"https://oauth.reddit.com/r/formula1/{listing}?limit=100",
                headers={"Authorization": "Bearer " + token, "User-Agent": config["user_agent"]})
            with opener.open(request, timeout=15) as response:
                children = _read_json(response)["data"]["children"]
            if not isinstance(children, list):
                raise ValueError("Reddit listing is malformed")
            posts.extend(children[:100])
    except (OSError, ValueError, KeyError, TypeError) as error:
        reason = f"HTTP {error.code}" if isinstance(error, urllib.error.HTTPError) else type(error).__name__
        status.update(status="error", detail=f"Reddit API request failed ({reason}).")
        return status, []

    candidates = []
    for post in posts:
        data = post.get("data") if isinstance(post, dict) else None
        if not isinstance(data, dict) or data.get("is_self") or data.get("over_18") or data.get("stickied"):
            continue
        created = data.get("created_utc")
        score, comments = data.get("score"), data.get("num_comments")
        if (not isinstance(created, (int, float)) or not isinstance(score, int)
                or not isinstance(comments, int) or (score < 30 and comments < 8)
                or not 0 <= now.timestamp() - created <= 48 * 3600):
            continue
        url = data.get("url_overridden_by_dest")
        host = _source(url)
        if host:
            candidates.append((score, comments, host, url))
    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)

    headlines, failures, seen = [], 0, set()
    for _score, _comments, host, url in candidates:
        if len(seen) >= 8:
            break
        if url in seen:
            continue
        seen.add(url)
        request = urllib.request.Request(url, headers={"User-Agent": "f1-commentary-news-discovery/1.0"})
        try:
            with opener.open(request, timeout=8) as response:
                if response.headers.get_content_type() != "text/html":
                    raise ValueError("Publisher did not return HTML")
                body = response.read(512 * 1024).decode("utf-8", "replace")
            parser = TitleParser()
            parser.feed(body)
            title = " ".join(parser.title.split())[:300]
            if not title or news_briefing.PROMOTIONS.search(title):
                continue
            headlines.append({"publisher": host, "title": title})
        except (OSError, ValueError):
            failures += 1
    status.update(status="ok" if not failures else "partial",
                  detail=f"{len(headlines)} independently retrieved publisher headlines; "
                         f"{failures} publisher requests unavailable.")
    return status, headlines
