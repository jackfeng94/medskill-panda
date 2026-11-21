#!/usr/bin/env python3
"""Find and lift figures out of a PDF as vector SVG (or PNG), without redrawing them.

Journal PDFs usually store Kaplan–Meier curves, forest plots and flow diagrams as vector
line art. Extracting the vectors keeps every step, censor tick and number-at-risk exact,
at any zoom. Requires PyMuPDF (pip install pymupdf).

Commands
  list    PDF [--page N]                       pages, images, vector clusters, captions (PDF points)
  extract PDF --page N --rect x0,y0,x1,y1 -o fig.svg [--recolor OLD=NEW ...] [--prefix id]
  raster  PDF --page N --rect x0,y0,x1,y1 -o fig.png [--dpi 300]
  colors  fig.svg                              stroke/fill colours with counts and widths
  split   fig.svg --colors '#d7262e,#5b6b82' [--min-width 1.0] -o base.svg curves.svg

Pages are 1-based. Coordinates are PDF points from the top-left, as printed by `list`.
Typical KM workflow: list → extract (with --recolor to the deck palette) → colors →
split (curves on their own layer, so the deck can animate them).
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CAPTION = re.compile(r"^\s*(?:Figure|Fig\.|Table|Hình|Bảng|Panel)\s*\S*", re.I)


def _fitz():
    try:
        import pymupdf as fitz  # type: ignore  # PyMuPDF >= 1.24
        return fitz
    except ImportError:
        pass
    try:
        import fitz  # type: ignore
        return fitz
    except ImportError:
        sys.exit("PyMuPDF is required: pip install pymupdf")


def parse_rect(s: str):
    fitz = _fitz()
    x0, y0, x1, y1 = (float(v) for v in s.split(","))
    return fitz.Rect(x0, y0, x1, y1)


# ------------------------------------------------------------------ list

def cluster(rects, gap=6.0):
    """Merge drawing rectangles that touch or sit within `gap` points of each other."""
    boxes = [list(r) for r in rects if r.width * r.height > 0 or r.width > 2 or r.height > 2]
    changed = True
    while changed:
        changed = False
        out = []
        while boxes:
            b = boxes.pop()
            i = 0
            while i < len(boxes):
                o = boxes[i]
                if not (o[0] > b[2] + gap or o[2] < b[0] - gap or o[1] > b[3] + gap or o[3] < b[1] - gap):
                    b = [min(b[0], o[0]), min(b[1], o[1]), max(b[2], o[2]), max(b[3], o[3])]
                    boxes.pop(i)
                    changed = True
                else:
                    i += 1
            out.append(b)
        boxes = out
    return sorted(boxes, key=lambda b: (b[1], b[0]))


def cmd_list(a):
    fitz = _fitz()
    doc = fitz.open(a.pdf)
    pages = [a.page] if a.page else range(1, len(doc) + 1)
    for n in pages:
        p = doc[n - 1]
        drawings = p.get_drawings()
        print(f"page {n}  size {p.rect.width:.0f}×{p.rect.height:.0f} pt  drawings {len(drawings)}")
        for img in p.get_image_info():
            x0, y0, x1, y1 = img["bbox"]
            print(f"  image   {x0:.1f},{y0:.1f},{x1:.1f},{y1:.1f}  {img['width']}×{img['height']} px")
        for b in cluster([d["rect"] for d in drawings]):
            w, h = b[2] - b[0], b[3] - b[1]
            if w > 60 and h > 40:
                n_in = sum(1 for d in drawings if fitz.Rect(b).contains(d["rect"]))
                print(f"  vector  {b[0]:.1f},{b[1]:.1f},{b[2]:.1f},{b[3]:.1f}  ({w:.0f}×{h:.0f} pt, {n_in} paths)")
        for blk in p.get_text("blocks"):
            if CAPTION.match(blk[4]):
                print(f"  caption {blk[0]:.1f},{blk[1]:.1f},{blk[2]:.1f},{blk[3]:.1f}  {blk[4].strip()[:80]!r}")


# ------------------------------------------------------------------ extract / raster

def isolate(page, rect):
    """Remove everything outside `rect` (text, line art; images are kept), then crop."""
    fitz = _fitz()
    W, H = page.rect.width, page.rect.height
    for r in (fitz.Rect(0, 0, W, rect.y0), fitz.Rect(0, rect.y1, W, H),
              fitz.Rect(0, rect.y0, rect.x0, rect.y1), fitz.Rect(rect.x1, rect.y0, W, rect.y1)):
        if r.width > 0 and r.height > 0:
            page.add_redact_annot(r)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED)
    page.set_cropbox(rect)


def recolor(svg: str, pairs: list[str]) -> str:
    for pair in pairs:
        old, new = (c.strip().lower() for c in pair.split("="))
        svg = re.sub(re.escape(old), new, svg, flags=re.I)
    return svg


def prefix_ids(svg: str, prefix: str) -> str:
    svg = re.sub(r'id="([^"]+)"', lambda m: f'id="{prefix}-{m.group(1)}"', svg)
    svg = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{prefix}-{m.group(1)})", svg)
    return re.sub(r'href="#([^"]+)"', lambda m: f'href="#{prefix}-{m.group(1)}"', svg)


def responsive(svg: str) -> str:
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    return re.sub(r'(<svg\b[^>]*?)\swidth="[\d.]+(?:pt|px)?"\s+height="[\d.]+(?:pt|px)?"', r"\1", svg, count=1)


def cmd_extract(a):
    fitz = _fitz()
    doc = fitz.open(a.pdf)
    page = doc[a.page - 1]
    isolate(page, parse_rect(a.rect))
    svg = page.get_svg_image(text_as_path=not a.keep_text)
    svg = responsive(svg)
    if a.recolor:
        svg = recolor(svg, a.recolor)
    if a.prefix:
        svg = prefix_ids(svg, a.prefix)
    Path(a.out).write_text(svg, encoding="utf-8")
    print(f"{a.out}: {len(svg) // 1024} KB")


def cmd_raster(a):
    fitz = _fitz()
    doc = fitz.open(a.pdf)
    page = doc[a.page - 1]
    pix = page.get_pixmap(clip=parse_rect(a.rect), dpi=a.dpi)
    pix.save(a.out)
    print(f"{a.out}: {pix.width}×{pix.height} px")


# ------------------------------------------------------------------ colours / split

PATH = re.compile(r"<path\b[^>]*?(?:/>|>\s*</path>)", re.S)


def attr(tag: str, name: str) -> str | None:
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def cmd_colors(a):
    svg = Path(a.svg).read_text(encoding="utf-8")
    c = Counter()
    for tag in PATH.findall(svg):
        for kind in ("stroke", "fill"):
            v = attr(tag, kind)
            if v and v.startswith("#"):
                w = attr(tag, "stroke-width") if kind == "stroke" else ""
                c[(kind, v.lower(), w or "")] += 1
    for (kind, col, w), n in c.most_common():
        print(f"{kind:6} {col}  width {w or '-':6} ×{n}")


def cmd_split(a):
    svg = Path(a.svg).read_text(encoding="utf-8")
    cols = {c.strip().lower() for c in a.colors.split(",")}
    moved = []

    def take(m):
        tag = m.group(0)
        stroke = (attr(tag, "stroke") or "").lower()
        width = float(attr(tag, "stroke-width") or 0)
        if stroke in cols and width >= a.min_width:
            moved.append(tag)
            return ""
        return tag

    base = PATH.sub(take, svg)
    root = re.match(r"\s*(<svg\b[^>]*>)", svg).group(1)
    curves = root + "".join(moved) + "</svg>"
    Path(a.out[0]).write_text(base, encoding="utf-8")
    Path(a.out[1]).write_text(curves, encoding="utf-8")
    print(f"moved {len(moved)} path(s) to {a.out[1]}")
    if not moved:
        print("nothing matched: run `colors` to see the curve colours and widths", file=sys.stderr)
        return 1
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list"); s.add_argument("pdf"); s.add_argument("--page", type=int)
    e = sub.add_parser("extract"); e.add_argument("pdf"); e.add_argument("--page", type=int, required=True)
    e.add_argument("--rect", required=True); e.add_argument("-o", "--out", required=True)
    e.add_argument("--recolor", action="append", default=[], metavar="OLD=NEW")
    e.add_argument("--prefix"); e.add_argument("--keep-text", action="store_true", help="keep <text> instead of paths")
    r = sub.add_parser("raster"); r.add_argument("pdf"); r.add_argument("--page", type=int, required=True)
    r.add_argument("--rect", required=True); r.add_argument("-o", "--out", required=True); r.add_argument("--dpi", type=int, default=300)
    c = sub.add_parser("colors"); c.add_argument("svg")
    p = sub.add_parser("split"); p.add_argument("svg"); p.add_argument("--colors", required=True)
    p.add_argument("--min-width", type=float, default=0.0); p.add_argument("-o", "--out", nargs=2, required=True)
    a = ap.parse_args(argv)
    return {"list": cmd_list, "extract": cmd_extract, "raster": cmd_raster, "colors": cmd_colors, "split": cmd_split}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
