#!/usr/bin/env python3
"""Backfill real headlines and publication dates onto stored Formula1.com news.

Formula1.com's listing page only exposes a URL slug, so until now every F1.com
card was stored with a slug-derived title ("Half term report racing bulls best
and worst moments...") and no date. The article pages carry a proper headline
and an ISO ``datePublished``; this walks the saved cards and fills both in.

Only ``title`` and ``when`` are touched — the LLM-written ``paragraphs`` are
left exactly as they are, so this costs no model calls.

    python3 backfill_meta.py [--gp hungary] [--dry-run]
"""
import argparse
import json
import os
import sys

import enrich

DATA_DIR = "data"


def gp_dirs():
    return sorted(d for d in os.listdir(DATA_DIR)
                  if os.path.isdir(os.path.join(DATA_DIR, d)))


def backfill(gp, dry_run=False):
    path = os.path.join(DATA_DIR, gp, "news_auto.json")
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8") as fh:
        news = json.load(fh)

    changed = 0
    for card in news:
        if card.get("src_kind") != "f1":
            continue
        slug_title = _slug_like(card.get("title", ""))
        if card.get("when") and not slug_title:
            continue
        meta = enrich.f1_meta(card["url"])
        upd = []
        # Most stored titles were written by the summariser and read better than
        # F1.com's own headline, so only overwrite the ones that are plainly the
        # de-hyphenated URL slug (the summariser's fallback).
        if slug_title and meta["title"] and meta["title"] != card.get("title"):
            upd.append(f'title: {card.get("title", "")[:40]!r} -> {meta["title"][:40]!r}')
            card["title"] = meta["title"]
        if meta["when"] and meta["when"] != card.get("when"):
            upd.append(f'when: {card.get("when", "")!r} -> {meta["when"]!r}')
            card["when"] = meta["when"]
        if upd:
            changed += 1
            print(f"  ~ {' | '.join(upd)}")

    if changed and not dry_run:
        news.sort(key=lambda n: (n.get("when", ""), n.get("title", "")))
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(news, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    return changed


def _slug_like(title):
    """A slug-derived title has no punctuation and only its first word capitalised."""
    if not title:
        return True
    words = title.split()
    caps = sum(1 for w in words[1:] if w[:1].isupper())
    return caps == 0 and not any(c in title for c in ",:'\"?!")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gp", help="only this GP dir")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    targets = [args.gp] if args.gp else gp_dirs()
    total = 0
    for gp in targets:
        print(f"{gp}:")
        n = backfill(gp, dry_run=args.dry_run)
        total += n
        print(f"  = {n} card(s) updated")
    print(f"\nDone — {total} card(s){' (dry run)' if args.dry_run else ''}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
