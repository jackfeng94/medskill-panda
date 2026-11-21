#!/usr/bin/env python3
"""Render every slide of an HTML deck, find overflow, and capture what the audience sees.

Outputs (in --out, default ./render):
  slide-01.png …     each slide at 1920×1080 with all fragments shown, animations finished
  contact.html       all screenshots on one page, for a quick look
  dom.html           the rendered DOM (includes text injected by JavaScript): lint this file
  report.json        overflow findings, console errors, optional animation timing

Requires Playwright for Python:  pip install playwright
Then either `python -m playwright install chromium`, or let this script use an installed
Microsoft Edge or Google Chrome (it tries them automatically).

Usage:
  python check_render.py out/talk.html [--out build/render] [--smooth 5]
  --smooth N   also time the animation of slide N for 3 s (median / p95 frame interval)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OVERFLOW_JS = r"""
(() => {
  const st = document.getElementById('stage').getBoundingClientRect(), k = st.width / 1920;
  const s = document.querySelector('.slide.active'); const out = [];
  const path = e => { const p = []; for (let x = e; x && x !== s && p.length < 4; x = x.parentElement)
    p.unshift(x.tagName.toLowerCase() + (x.classList.length ? '.' + [...x.classList].slice(0, 2).join('.') : '')); return p.join(' > '); };
  for (const e of s.querySelectorAll('*')) {
    if (e.closest('aside.notes,svg,canvas') && e.tagName.toLowerCase() !== 'svg') continue;
    const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) continue;
    const r = e.getBoundingClientRect(); if (!r.width || !r.height) continue;
    const x0 = (r.left - st.left) / k, y0 = (r.top - st.top) / k, x1 = (r.right - st.left) / k, y1 = (r.bottom - st.top) / k;
    if (x0 < -2 || y0 < -2 || x1 > 1922 || y1 > 1082)
      out.push({kind: 'off-stage', el: path(e), box: [x0, y0, x1, y1].map(Math.round), text: (e.textContent || '').trim().slice(0, 60)});
    const tag = e.tagName.toLowerCase();
    if (tag !== 'svg' && e.children.length + (e.textContent || '').trim().length > 0 && e.clientHeight > 0 &&
        (cs.height.endsWith('px') && e.style.height || cs.overflowY !== 'visible' || e.matches('[class*="box"],[class*="card"],.bx,.stat,.tile')) &&
        e.scrollHeight > e.clientHeight + 4)
      out.push({kind: 'clipped-or-overflowing', el: path(e), by_px: Math.round((e.scrollHeight - e.clientHeight) / k),
                text: (e.textContent || '').trim().slice(0, 60)});
  }
  return out;
})()
"""

SMOOTH_JS = r"""
async (i) => { deck.go(i, false); const t = []; let last = performance.now(); const end = last + 3000;
  while (performance.now() < end) { await new Promise(r => requestAnimationFrame(r)); const n = performance.now(); t.push(n - last); last = n; }
  t.sort((a, b) => a - b); return {frames: t.length, median_ms: +t[t.length >> 1].toFixed(1),
  p95_ms: +t[Math.floor(t.length * .95)].toFixed(1), max_ms: +t[t.length - 1].toFixed(1)}; }
"""


def launch(p):
    errors = []
    for kw in ({}, {"channel": "msedge"}, {"channel": "chrome"}):
        try:
            return p.chromium.launch(**kw)
        except Exception as e:  # browser not installed in this form
            errors.append(f"{kw or 'bundled chromium'}: {str(e).splitlines()[0]}")
    sys.exit("No browser for Playwright. Run `python -m playwright install chromium`.\n  " + "\n  ".join(errors))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--out", default="render")
    ap.add_argument("--smooth", type=int, help="1-based slide number to time")
    a = ap.parse_args(argv)
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        sys.exit("Playwright is required: pip install playwright")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    report = {"deck": a.deck, "slides": [], "console_errors": []}
    with sync_playwright() as p:
        browser = launch(p)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.on("console", lambda m: m.type == "error" and report["console_errors"].append(m.text))
        page.on("pageerror", lambda e: report["console_errors"].append(str(e)))
        url = Path(a.deck).resolve().as_uri()
        page.goto(url)
        page.add_style_tag(content="#tools,#notes{display:none!important}")
        try:
            page.wait_for_function("window.deck && deck.count > 0", timeout=5000)
            api = True
        except Exception:
            api = False
            report["warning"] = ("deck has no window.deck API (not built with deck-engine.html): slides opened "
                                 "by URL hash, fragments not shown")
            print("WARNING: " + report["warning"])
        n = page.evaluate("deck.count") if api else page.evaluate("document.querySelectorAll('section.slide').length")
        page.add_init_script("window.__noop = 1")
        for i in range(n):
            if api:
                page.evaluate(f"deck.go({i}, true)")
            else:
                page.goto(f"{url}#{i + 1}")
                page.reload()
                page.wait_for_timeout(300)
                page.add_style_tag(content="#tools,#notes{display:none!important}")
                page.evaluate("window.deck = window.deck || {finish: () => document.getAnimations().forEach(a => a.finish())}")
            page.wait_for_timeout(120)
            for _ in range(3):
                page.evaluate("deck.finish()")
                page.wait_for_timeout(80)
            page.evaluate("document.body.classList.add('idle')")
            shot = out / f"slide-{i + 1:02d}.png"
            page.screenshot(path=str(shot))
            issues = page.evaluate(OVERFLOW_JS)
            report["slides"].append({"slide": i + 1, "png": shot.name, "issues": issues})
        (out / "dom.html").write_text(page.content(), encoding="utf-8")
        if a.smooth:
            report["smoothness"] = {"slide": a.smooth, **page.evaluate(SMOOTH_JS, a.smooth - 1)}
        browser.close()

    cells = "".join(f'<figure><img src="{s["png"]}"><figcaption>{s["slide"]}'
                    f'{" · " + str(len(s["issues"])) + " issue(s)" if s["issues"] else ""}</figcaption></figure>'
                    for s in report["slides"])
    (out / "contact.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Contact sheet</title><style>body{font:14px Arial;margin:16px;"
        "display:grid;grid-template-columns:repeat(3,1fr);gap:12px}img{width:100%;border:1px solid #ccc}"
        "figure{margin:0}</style>" + cells, encoding="utf-8")
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    bad = [s for s in report["slides"] if s["issues"]]
    print(f"{n} slides rendered to {out}; {len(bad)} with issues; {len(report['console_errors'])} console error(s)")
    for s in bad:
        for it in s["issues"][:6]:
            print(f"  slide {s['slide']}: {it['kind']} {it['el']} {it.get('by_px', it.get('box', ''))} {it['text']!r}")
    for e in report["console_errors"]:
        print(f"  console: {e}")
    if "smoothness" in report:
        print("  smoothness:", report["smoothness"])
    return 1 if bad or report["console_errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
