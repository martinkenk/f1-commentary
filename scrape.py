#!/usr/bin/env python3
"""Fetch an F1 / The Race article and extract clean heading+paragraph text."""
import re, html, sys, subprocess

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

def fetch(url):
    return subprocess.run(
        ["curl", "-sL", "-A", UA, url],
        capture_output=True, text=True).stdout

def extract(h):
    h = re.sub(r'<script.*?</script>', '', h, flags=re.S)
    h = re.sub(r'<style.*?</style>', '', h, flags=re.S)
    # Capture headings and paragraphs in document order
    out = []
    for m in re.finditer(r'<(h1|h2|h3|h4|p|li)[^>]*>(.*?)</\1>', h, flags=re.S):
        tag, inner = m.group(1), m.group(2)
        t = re.sub(r'<[^>]+>', '', inner)
        t = html.unescape(t).strip()
        t = re.sub(r'\s+', ' ', t)
        if len(t) < 25:
            continue
        out.append((tag, t))
    return out

if __name__ == "__main__":
    url = sys.argv[1]
    data = fetch(url)
    for tag, t in extract(data):
        prefix = {"h1": "\n# ", "h2": "\n## ", "h3": "\n### ", "h4": "\n#### ", "li": "- ", "p": ""}[tag]
        print(prefix + t)
