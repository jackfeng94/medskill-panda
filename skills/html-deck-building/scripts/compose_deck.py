#!/usr/bin/env python3
"""Assemble a deck source from the engine plus your parts, so engine updates flow into decks.

  python compose_deck.py --slides slides.html [--css deck.css] [--js deck.js] \
      [--title "Talk · Presenter"] [--lang vi] [--cite "Footer citation"] \
      [--engine ../assets/deck-engine.html] -o build/index.src.html

The output keeps <!--include: slides.html-->, <link href="deck.css"> and <script src="deck.js">
as references (relative to the output file), and build_deck.py inlines them. Theme variables
go at the top of deck.css (`:root{--primary:…}`), which overrides the engine defaults.
"""
from __future__ import annotations

import argparse
import html
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENGINE = Path(__file__).resolve().parent.parent / "assets" / "deck-engine.html"


def compose(engine: str, slides_ref: str, css_ref: str | None, js_ref: str | None,
            title: str | None, lang: str | None, cite: str | None) -> str:
    e = engine
    e, n = re.subn(r"<!-- ===== SLIDES: replace everything between the markers ===== -->.*?<!-- ===== END SLIDES ===== -->",
                   f"<!-- ===== SLIDES ===== -->\n<!--include: {slides_ref}-->\n<!-- ===== END SLIDES ===== -->", e, flags=re.S)
    if n != 1:
        raise SystemExit("engine has no slide markers")
    if title:
        e = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", e, count=1)
    if lang:
        e = re.sub(r'<html lang="[^"]*">', f'<html lang="{lang}">', e, count=1)
    if cite is not None:
        e = e.replace('<body class="t-none" data-cite="">', f'<body class="t-none" data-cite="{html.escape(cite, quote=True)}">', 1)
    if css_ref:
        e = e.replace("</style>\n</head>", f'</style>\n<link rel="stylesheet" href="{css_ref}">\n</head>', 1)
    per_deck = "<script>\n/* ---- per-deck code (figures, charts) goes here, before the engine ---- */\n</script>"
    e = e.replace(per_deck, f'<script src="{js_ref}"></script>' if js_ref else "", 1)
    return e


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slides", required=True)
    ap.add_argument("--css")
    ap.add_argument("--js")
    ap.add_argument("--title")
    ap.add_argument("--lang")
    ap.add_argument("--cite")
    ap.add_argument("--engine", default=str(ENGINE))
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    rel = lambda p: os.path.relpath(Path(p).resolve(), out.resolve().parent).replace("\\", "/") if p else None
    text = compose(Path(a.engine).read_text(encoding="utf-8"), rel(a.slides), rel(a.css), rel(a.js), a.title, a.lang, a.cite)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"{out}: engine + {a.slides}" + (f" + {a.css}" if a.css else "") + (f" + {a.js}" if a.js else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
