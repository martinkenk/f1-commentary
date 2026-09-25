"""Refresh source-faithful FIA PDF screenshots without editorial transcription.

    python3 fia_media.py                 # active weekends, saved discovery manifests
    python3 fia_media.py --gp spain

Run enrich.py first to discover new URLs. A blocked listing does not prevent
retrieval of already-discovered public PDFs. Failed downloads retain prior images.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

import enrich
import f1lib

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ASSETS_DIR = ROOT / "assets_src"
MAX_PDF_BYTES = 20 * 1024 * 1024
MAX_PAGES = 40
MAX_PAGE_PIXELS = 8_000_000


def _read(path):
    if not path.exists():
        return {}
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return record


def _write(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def _download(url):
    if not f1lib._official_fia_url(url):
        raise ValueError(f"Not an official HTTPS FIA source: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": enrich.UA})
    with urllib.request.urlopen(request, timeout=40) as response:
        if not f1lib._official_fia_url(response.url):
            raise ValueError(f"Unexpected FIA PDF redirect: {response.url}")
        raw = response.read(MAX_PDF_BYTES + 1)
    if len(raw) > MAX_PDF_BYTES:
        raise ValueError("FIA PDF exceeds the 20 MiB download limit")
    if not raw.startswith(b"%PDF-"):
        raise ValueError("FIA source did not return a PDF")
    return raw


def _render(raw, prefix):
    import pymupdf

    pages = []
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(stream=raw, filetype="pdf") as document:
        if document.is_encrypted or not 1 <= len(document) <= MAX_PAGES:
            raise ValueError("Encrypted, empty or excessively long FIA PDF")
        for index, page in enumerate(document):
            text = page.get_text().lower()
            # FIA's publication wrapper is not the attached technical report.
            if (index == 0 and len(document) > 1
                    and all(word in text for word in ("document", "title", "enclosed"))
                    and not any(word in text for word in
                                ("decision\n", "decision ", "fact\n", "fact ",
                                 "the stewards determine", "the stewards decide"))):
                continue
            if page.rect.width * page.rect.height * 4 > MAX_PAGE_PIXELS:
                raise ValueError(f"FIA PDF page {index + 1} exceeds the render-size limit")
            name = f"{prefix}-p{index + 1}.png"
            target = ASSETS_DIR / name
            if not target.exists():
                image = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
                temporary = target.with_suffix(".tmp")
                temporary.write_bytes(image.tobytes("png"))
                temporary.replace(target)
            pages.append({"page": index + 1, "asset": name})
    if not pages:
        raise ValueError("No substantive FIA PDF pages found")
    return pages


def refresh_gp(ctx, decisions_only=False):
    directory = DATA_DIR / ctx["dir"]
    discovered = _read(directory / "fia_documents.json")
    previous = _read(directory / "fia_media.json")
    records = {item["url"]: item for item in previous.get("documents", [])}
    penalties_path = directory / "penalties_auto.json"
    penalties = enrich.load_list(str(penalties_path))
    sources = {item["url"]: item for item in discovered.get("documents", [])}
    for document in previous.get("documents", []):
        if "penalties" in f1lib.fia_document_categories(document["filename"]):
            sources.setdefault(document["url"], document)
    # Older successful extraction citations can survive a blocked/later listing.
    for penalty in penalties:
        url, filename = penalty.get("source_url"), penalty.get("source_pdf")
        if f1lib._official_fia_url(url) and filename:
            sources.setdefault(url, {"url": url, "filename": filename})
    attempted = {url for url, source in sources.items()
                 if (not decisions_only
                     or "penalties" in f1lib.fia_document_categories(source["filename"]))}
    errors = [error for error in previous.get("errors", [])
              if decisions_only and error.get("url") not in attempted]
    checked_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    if not discovered:
        errors.append({"url": ctx.get("fia_url", ""), "error": "No saved FIA discovery manifest"})
    for source in sources.values():
        categories = f1lib.fia_document_categories(source["filename"])
        if not categories or (decisions_only and "penalties" not in categories):
            continue
        url = source["url"]
        try:
            raw = _download(url)
            digest = hashlib.sha256(raw).hexdigest()
            old = records.get(url, {})
            if (old.get("sha256") == digest and old.get("pages")
                    and all((ASSETS_DIR / page["asset"]).is_file() for page in old["pages"])):
                pages = old["pages"]
            else:
                identity = hashlib.sha256(url.encode()).hexdigest()[:12]
                prefix = f"fia-{ctx['dir']}-{identity}-{digest[:16]}"
                pages = _render(raw, prefix)
            records[url] = {
                "url": url, "filename": source["filename"], "categories": categories,
                "sha256": digest, "fetched_at": checked_at, "pages": pages,
                "revision": old.get("revision", 0) + int(bool(old.get("sha256"))
                                                       and old["sha256"] != digest),
            }
            if "penalties" in categories:
                text = enrich.pdf_text(raw)
                for penalty in penalties:
                    if (penalty.get("source_url") == url
                            or (not penalty.get("source_url")
                                and penalty.get("source_pdf") == source["filename"])):
                        enrich.repair_decision(penalty, text, source["filename"])
                        penalty["source_url"] = url
            print(f"  {ctx['dir']}: {source['filename']} ({len(pages)} pages)")
        except Exception as error:
            errors.append({"url": url, "error": str(error)})
            print(f"  ! {ctx['dir']} FIA screenshots: {url}: {error}")
    # Keep the published listing order, retaining older successful documents last.
    order = {doc["url"]: index for index, doc in enumerate(discovered.get("documents", []))}
    _write(directory / "fia_media.json", {
        "checked_at": checked_at,
        "discovery_retrieved_at": discovered.get("retrieved_at", ""),
        "documents": sorted(records.values(), key=lambda d: order.get(d["url"], len(order))),
        "errors": errors,
    })
    if penalties:
        _write(penalties_path, penalties)
    return not errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gp", help="one registered GP slug; otherwise use the active window")
    parser.add_argument("--decisions-only", action="store_true",
                        help="backfill decision screenshots and source identities only")
    args = parser.parse_args()
    gps = enrich.load_gps()
    if args.gp:
        gps = [gp for gp in gps if gp["dir"] == args.gp]
        if not gps:
            parser.error(f"Unknown GP: {args.gp}")
    else:
        gps = enrich.active_gps(gps)
    # Fail clearly before touching manifests if the optional render dependency is absent.
    import pymupdf  # noqa: F401
    import pypdf  # noqa: F401

    failed = False
    for gp in gps:
        if not refresh_gp(gp, decisions_only=args.decisions_only):
            failed = True
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
