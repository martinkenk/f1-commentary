#!/usr/bin/env python3
"""Version-history layer for the F1 Commentary Hub (used by CI, works locally too).

Takes a freshly built `site/` and a persistent `public/` deploy tree and:

  1. Decides whether the new build is *materially* different from the last one
     (timestamp-only / tiny diffs are treated as trivial and are NOT pinned).
  2. On a material change, pins the build as a new immutable snapshot under
     `public/versions/<id>/` and records it in `public/versions.json`.
  3. Always refreshes the live site at the `public/` root.
  4. Injects a "Version" dropdown at the top of every page so you can jump back
     to any pinned snapshot if a change breaks something. The bar only appears
     once there are at least two versions to choose from.

Usage:
    python3 versioning.py <incoming_site_dir> <public_dir> [--threshold N] [--keep M]

`--threshold` (default 3): builds whose only differences total this many changed
lines or fewer are considered trivial and are not pinned.
`--keep` (default 20): maximum number of pinned snapshots to retain.
"""
import argparse
import datetime
import difflib
import html
import json
import os
import re
import shutil

try:
    from zoneinfo import ZoneInfo
    _TALLINN = ZoneInfo("Europe/Tallinn")
except Exception:  # pragma: no cover
    _TALLINN = None

WIDGET_START = "<!--VERSION_WIDGET_START-->"
WIDGET_END = "<!--VERSION_WIDGET_END-->"
MAIN_ANCHOR = '<main class="content">'
RESERVED = {"versions", "versions.json", ".raw", ".git", ".nojekyll"}


# --------------------------------------------------------------------------
# Normalisation (so timestamp / injected-widget churn isn't seen as a change)
# --------------------------------------------------------------------------
def _strip_widget(text):
    return re.sub(re.escape(WIDGET_START) + r".*?" + re.escape(WIDGET_END),
                  "", text, flags=re.S)


def _normalize(text):
    text = _strip_widget(text)
    # Drop the "Updated <stamp>" line — it changes every single build.
    text = re.sub(r"Updated [A-Za-z]{3} \d{2} [A-Za-z]{3} \d{4}, \d{2}:\d{2}", "Updated", text)
    return text


def _html_files(root):
    out = {}
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if fn.endswith(".html"):
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                out[rel] = full
    return out


# --------------------------------------------------------------------------
# Materiality decision
# --------------------------------------------------------------------------
def _changed_lines(a, b):
    a_lines = _normalize(a).splitlines()
    b_lines = _normalize(b).splitlines()
    diff = difflib.unified_diff(a_lines, b_lines, n=0)
    return sum(1 for ln in diff if ln[:1] in "+-" and not ln.startswith(("+++", "---")))


def is_material(incoming_dir, raw_dir, threshold):
    """True if `incoming_dir` differs materially from the stored `.raw` mirror."""
    if not os.path.isdir(raw_dir):
        return True  # first run
    inc = _html_files(incoming_dir)
    raw = _html_files(raw_dir)
    if set(inc) != set(raw):
        return True  # a page was added or removed
    total = 0
    for rel, path in inc.items():
        a = open(raw[rel], encoding="utf-8").read()
        b = open(path, encoding="utf-8").read()
        total += _changed_lines(a, b)
        if total > threshold:
            return True
    return False


# --------------------------------------------------------------------------
# Snapshot / mirror helpers
# --------------------------------------------------------------------------
def _copytree(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _write_raw_mirror(incoming_dir, raw_dir):
    """Store an HTML-only mirror of the build for future diffing."""
    if os.path.exists(raw_dir):
        shutil.rmtree(raw_dir)
    for rel, path in _html_files(incoming_dir).items():
        dest = os.path.join(raw_dir, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(path, dest)


def _refresh_root(incoming_dir, public_dir):
    """Replace the live root with the new build, preserving versions/ and .git."""
    for name in os.listdir(public_dir):
        if name in ("versions", ".git", ".raw"):
            continue
        p = os.path.join(public_dir, name)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for name in os.listdir(incoming_dir):
        src = os.path.join(incoming_dir, name)
        dst = os.path.join(public_dir, name)
        shutil.copytree(src, dst) if os.path.isdir(src) else shutil.copy2(src, dst)


# --------------------------------------------------------------------------
# Version-dropdown injection
# --------------------------------------------------------------------------
def _rel_to_root(rel_path):
    """'../' * (depth to the public root) for a file at public-relative rel_path."""
    depth = rel_path.count("/")
    return "../" * depth


def _build_widget(base, subpath, versions, current_id, root_has_page, version_has_page):
    """current_id is None for the live root, else the snapshot id being viewed."""
    opts = []
    latest_label = f"Latest (live){' — ' + versions[0]['label'] if versions else ''}"
    if root_has_page:
        sel = " selected" if current_id is None else ""
        opts.append(f'<option value="{base}{subpath}"{sel}>{html.escape(latest_label)}</option>')
    for v in versions:
        if not version_has_page(v["id"]):
            continue
        sel = " selected" if current_id == v["id"] else ""
        url = f'{base}versions/{v["id"]}/{subpath}'
        opts.append(f'<option value="{url}"{sel}>{html.escape(v["label"])}</option>')
    archived = ""
    if current_id is not None:
        archived = (f'<span class="version-archived"><i class="bi bi-exclamation-triangle-fill"></i>'
                    f'Archived snapshot</span>'
                    f'<a class="version-latest-link" href="{base}{subpath}">Back to latest &rarr;</a>')
    return (
        f'{WIDGET_START}\n'
        f'<div class="version-bar">\n'
        f'  <label for="ver-select"><i class="bi bi-clock-history"></i> Version</label>\n'
        f'  <select id="ver-select" onchange="if(this.value)location.href=this.value;">\n'
        f'    {"".join(opts)}\n'
        f'  </select>\n'
        f'  {archived}\n'
        f'</div>\n'
        f'{WIDGET_END}'
    )


def inject_widgets(public_dir, versions):
    """(Re)inject the version bar into every page under public_dir.

    Skips the live-root pages entirely when there are fewer than two versions
    (nothing to roll back to yet). Archived pages always get the bar.
    """
    version_ids = {v["id"] for v in versions}

    def version_has_page(vid, subpath):
        return os.path.exists(os.path.join(public_dir, "versions", vid, subpath))

    for rel, path in _html_files(public_dir).items():
        parts = rel.split("/")
        in_version = len(parts) >= 2 and parts[0] == "versions" and parts[1] in version_ids
        if in_version:
            current_id = parts[1]
            subpath = "/".join(parts[2:])
        else:
            if rel.startswith("versions/") or rel.startswith(".raw/"):
                continue  # stray file in versions/ that isn't a known snapshot
            current_id = None
            subpath = rel

        text = _strip_widget(open(path, encoding="utf-8").read())

        # Fewer than 2 versions and we're on the live site → no bar needed.
        if current_id is None and len(versions) < 2:
            open(path, "w", encoding="utf-8").write(text)
            continue

        base = _rel_to_root(rel)
        root_has_page = os.path.exists(os.path.join(public_dir, subpath))
        widget = _build_widget(
            base, subpath, versions, current_id,
            root_has_page,
            lambda vid, sp=subpath: version_has_page(vid, sp),
        )
        if MAIN_ANCHOR in text:
            text = text.replace(MAIN_ANCHOR, MAIN_ANCHOR + "\n    " + widget, 1)
        open(path, "w", encoding="utf-8").write(text)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def _now_ids():
    now = datetime.datetime.now(_TALLINN) if _TALLINN else datetime.datetime.utcnow()
    return now.strftime("%Y%m%d-%H%M%S"), now.strftime("%d %b %Y, %H:%M EEST"), now.isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("incoming")
    ap.add_argument("public")
    ap.add_argument("--threshold", type=int, default=3)
    ap.add_argument("--keep", type=int, default=20)
    args = ap.parse_args()

    incoming, public = args.incoming, args.public
    os.makedirs(public, exist_ok=True)
    raw_dir = os.path.join(public, ".raw")
    versions_dir = os.path.join(public, "versions")
    manifest_path = os.path.join(public, "versions.json")

    manifest = {"versions": []}
    if os.path.exists(manifest_path):
        try:
            manifest = json.load(open(manifest_path, encoding="utf-8"))
        except Exception:
            pass
    versions = manifest.get("versions", [])

    material = is_material(incoming, raw_dir, args.threshold)

    if material:
        vid, label, ts = _now_ids()
        os.makedirs(versions_dir, exist_ok=True)
        _copytree(incoming, os.path.join(versions_dir, vid))
        versions.insert(0, {"id": vid, "label": label, "ts": ts})
        # Prune old snapshots.
        for stale in versions[args.keep:]:
            shutil.rmtree(os.path.join(versions_dir, stale["id"]), ignore_errors=True)
        versions = versions[:args.keep]
        print(f"versioning: material change → pinned version {vid} ({label}); "
              f"{len(versions)} snapshot(s) retained")
    else:
        print("versioning: no material change → live site refreshed, no new snapshot pinned")

    # Always refresh the live root and the diff mirror.
    _refresh_root(incoming, public)
    _write_raw_mirror(incoming, raw_dir)
    json.dump({"versions": versions}, open(manifest_path, "w", encoding="utf-8"), indent=2)

    # Re-inject the dropdown everywhere (keeps every snapshot's list current).
    inject_widgets(public, versions)
    # Make sure Pages serves everything verbatim.
    open(os.path.join(public, ".nojekyll"), "w").close()
    print(f"versioning: live site + {len(versions)} version(s) ready in {public}/")


if __name__ == "__main__":
    main()
