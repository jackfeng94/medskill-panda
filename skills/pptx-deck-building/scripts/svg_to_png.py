#!/usr/bin/env python3
"""Rasterise an SVG to PNG with a headless browser (exact rendering, transparent background).

Usage: python svg_to_png.py figure.svg figure.png [--width 2400]
Requires Playwright for Python (pip install playwright) and Chromium, Edge or Chrome.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("svg")
    ap.add_argument("png")
    ap.add_argument("--width", type=int, default=2400)
    a = ap.parse_args(argv)
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        sys.exit("Playwright is required: pip install playwright")
    svg = Path(a.svg).read_text(encoding="utf-8")
    vb = re.search(r'viewBox="([\d.\s-]+)"', svg)
    if not vb:
        sys.exit("SVG has no viewBox")
    _, _, vw, vh = (float(v) for v in vb.group(1).split())
    w, h = a.width, round(a.width * vh / vw)
    svg = re.sub(r"<svg\b", f'<svg width="{w}" height="{h}"', svg, count=1)
    html = f"<html><body style='margin:0;background:transparent'>{svg}</body></html>"
    with sync_playwright() as p:
        browser = None
        for kw in ({}, {"channel": "msedge"}, {"channel": "chrome"}):
            try:
                browser = p.chromium.launch(**kw)
                break
            except Exception:
                continue
        if browser is None:
            sys.exit("No browser: run `python -m playwright install chromium`")
        page = browser.new_page(viewport={"width": w, "height": h})
        page.set_content(html)
        page.locator("svg").first.screenshot(path=a.png, omit_background=True)
        browser.close()
    print(f"{a.png}: {w}×{h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
