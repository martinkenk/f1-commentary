"""Offline GP inventory for a periodic coverage editor, not a completeness verdict.

Build first, then run ``python3 coverage_inventory.py --all --check``.
Without --all, inspect the same active window as the refresh automation.
--check fails on missing rendered pages or broken local image references only.
"""
import argparse
import datetime
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import urllib.parse

import build
import enrich
import f1lib


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.sources.extend(value for key, value in attrs if key == "src" and value)


def inventory(gps, root=None):
    root = Path(root or build.ROOT)
    today = datetime.datetime.now(datetime.timezone.utc).date()
    events = []
    for ctx in gps:
        directory = root / "data" / ctx["dir"]
        stored, records = {}, {}
        for path in sorted(directory.glob("*.json")):
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, (dict, list)):
                raise ValueError(f"Expected a JSON object or array: {path}")
            if path.name.startswith("fia_") and not isinstance(value, dict):
                raise ValueError(f"Expected an FIA JSON object: {path}")
            records[path.name] = value
            stored[path.name] = ({"items": len(value)} if isinstance(value, list) else {
                "fields": list(value),
                "list_counts": {key: len(items) for key, items in value.items()
                                if isinstance(items, list)},
            })
        missing, broken = [], []
        for slug, filename, *_ in ctx["nav"]:
            page = root / "site" / ctx["dir"] / filename
            if not page.is_file():
                missing.append(slug)
                continue
            parser = Images()
            parser.feed(page.read_text(encoding="utf-8"))
            for source in parser.sources:
                url = urllib.parse.urlsplit(source)
                if url.scheme or url.netloc:
                    continue
                target = ((root / "site" / url.path.lstrip("/")) if url.path.startswith("/")
                          else page.parent / urllib.parse.unquote(url.path))
                if not target.is_file():
                    broken.append({"page": filename, "image": source})
        documents = records.get("fia_documents.json", {})
        media = records.get("fia_media.json", {})
        media_urls = {doc["url"] for doc in media.get("documents", [])
                      if doc.get("pages") and all((root / "assets_src" / p["asset"]).is_file()
                                                 for p in doc["pages"])}
        uncached = [doc["filename"] for doc in documents.get("documents", [])
                    if f1lib.fia_document_categories(doc["filename"]) and doc["url"] not in media_urls]
        events.append({
            "gp": ctx["dir"], "race_date": ctx["race_date"],
            "status": f1lib.event_status(ctx, today), "content_module": ctx["pages"].__module__,
            "data": stored,
            "event_assets": sorted(p.name for p in (root / "assets_src").glob(f"*{ctx['dir']}*")),
            "missing_rendered_pages": missing, "broken_local_images": broken,
            "fia_discovery": records.get("fia_discovery_status.json", {}),
            "fia_media_errors": media.get("errors", []),
            "fia_documents_without_automatic_screenshots": uncached,
            "editorial_review_required": True,
        })
    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "note": ("Inventory only. A linked PDF, screenshot or existing page is not proof of complete "
                 "editorial coverage. An uncached PDF may already have a curated figure. "
                 "Audit all 17 surfaces and source dates using SKILL.md."),
        "events": events,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    gps = enrich.load_gps()
    if not args.all:
        gps = enrich.active_gps(gps)
    report = inventory(gps)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(args.check and any(event["missing_rendered_pages"] or event["broken_local_images"]
                                  for event in report["events"]))


if __name__ == "__main__":
    sys.exit(main())
