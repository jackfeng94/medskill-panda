#!/usr/bin/env python3
"""Inline every local asset of an HTML deck into ONE offline file.

Handles:
  <!--include: figures/s05.svg-->         replaced by the file's content (SVG/HTML fragments)
  <img src="figures/a.png">               → data: URI
  url(fonts/x.woff2) in <style> or style= → data: URI
  <link rel="stylesheet" href="x.css">    → <style> (its url()s resolved relative to the CSS file)
  <script src="x.js"></script>            → inline <script>

Remote URLs (http/https) are left alone and reported, because the deck must run offline.

Usage: python build_deck.py build/index.src.html out/talk.html
"""
from __future__ import annotations

import base64
import mimetypes
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MIME = {".svg": "image/svg+xml", ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf",
        ".otf": "font/otf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".gif": "image/gif", ".webp": "image/webp", ".mp4": "video/mp4", ".webm": "video/webm"}


def data_uri(path: Path) -> str:
    mime = MIME.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def is_local(ref: str) -> bool:
    return not re.match(r"^(?:[a-z]+:|//|#)", ref, re.I)


def inline_css_urls(css: str, base: Path, missing: list) -> str:
    def sub(m):
        ref = m.group(2)
        if not is_local(ref):
            return m.group(0)
        p = (base / ref.split("?")[0].split("#")[0])
        if not p.exists():
            missing.append(str(p))
            return m.group(0)
        return f"url({data_uri(p)})"
    return re.sub(r"url\((['\"]?)([^)'\"]+)\1\)", sub, css)


def build(src: Path, out: Path) -> dict:
    base = src.parent
    html = src.read_text(encoding="utf-8")
    missing: list[str] = []

    def include(m):
        p = base / m.group(1).strip()
        if not p.exists():
            missing.append(str(p))
            return m.group(0)
        text = p.read_text(encoding="utf-8")
        return re.sub(r"<\?xml[^>]*\?>\s*", "", text)
    for _ in range(3):  # nested includes
        html = re.sub(r"<!--\s*include:\s*([^>]+?)\s*-->", include, html)

    def link(m):
        href = re.search(r'href="([^"]+)"', m.group(0)).group(1)
        if not is_local(href):
            return m.group(0)
        p = base / href
        if not p.exists():
            missing.append(str(p))
            return m.group(0)
        return "<style>\n" + inline_css_urls(p.read_text(encoding="utf-8"), p.parent, missing) + "\n</style>"
    html = re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>', link, html)

    def script(m):
        srcref = m.group(1)
        if not is_local(srcref):
            return m.group(0)
        p = base / srcref
        if not p.exists():
            missing.append(str(p))
            return m.group(0)
        return "<script>\n" + p.read_text(encoding="utf-8") + "\n</script>"
    html = re.sub(r'<script\b[^>]*\bsrc="([^"]+)"[^>]*>\s*</script>', script, html)

    def img(m):
        ref = m.group(2)
        if not is_local(ref):
            return m.group(0)
        p = base / ref
        if not p.exists():
            missing.append(str(p))
            return m.group(0)
        return f'{m.group(1)}"{data_uri(p)}"'
    html = re.sub(r'(<(?:img|source|video|image)\b[^>]*?\s(?:src|href|poster)=)"([^"]+)"', img, html)
    html = re.sub(r"(<style[^>]*>)(.*?)(</style>)",
                  lambda m: m.group(1) + inline_css_urls(m.group(2), base, missing) + m.group(3), html, flags=re.S)
    html = re.sub(r'style="([^"]*url\([^"]*)"', lambda m: 'style="' + inline_css_urls(m.group(1), base, missing) + '"', html)

    remote = sorted(set(re.findall(r'(?:src|href)="(https?://[^"]+)"', html)))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return {"out": str(out), "kb": round(len(html.encode()) / 1024), "missing": missing, "remote": remote}


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 2 or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    r = build(Path(argv[0]), Path(argv[1]))
    print(f"{r['out']}: {r['kb']} KB")
    for m in r["missing"]:
        print(f"  MISSING {m}")
    for u in r["remote"]:
        print(f"  REMOTE  {u}  (will not load offline)")
    return 1 if r["missing"] else 0


if __name__ == "__main__":
    sys.exit(main())
