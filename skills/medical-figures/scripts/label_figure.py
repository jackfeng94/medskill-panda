#!/usr/bin/env python3
"""Put editable, non-overlapping labels with leader lines around an illustration.

Use it for any picture whose labels should not be baked into the pixels: a Servier Medical
Art drawing, an AI-generated illustration, a photo of a specimen. The output is one SVG:
the image (embedded, resized) in the middle and the labels in columns on the left and
right, spread so they never overlap, each with a leader line and a dot on its structure.

Spec (JSON):
{
  "image": "servier/cycle-2.png",          path relative to the spec file
  "crop": [0.25, 0, 0.75, 1],             optional, fractions of the source image
  "max_width": 1400,                       resize the embedded image (px)
  "format": "jpeg", "quality": 86,         jpeg (flattened on white) | png | webp
  "margin": [0.55, 0.55],                  label column widths, as fractions of image width
  "font_px": 0,                            0 = automatic (3.2 % of image height)
  "stagger": 0.08,                         >0: labels get class "a-in" with --d delays
  "whiten": 232,                           optional: near-white pixels (all channels >= n) become
                                           pure white, so an off-white AI background doesn't show as a box
  "labels": [{"text": "Right atrium", "at": [0.22, 0.50], "side": "left"}, …]
}
"at" is the point on the structure, as fractions of the (cropped) image.

Usage: python label_figure.py spec.json -o figures/heart-labelled.svg
Requires Pillow.
"""
from __future__ import annotations

import argparse
import base64
import html
import io
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def spread(ys: list[float], gap: float, lo: float, hi: float) -> list[float]:
    """Move label baselines apart by at least `gap`, keeping them within [lo, hi]."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    v = [ys[i] for i in order]
    for i in range(len(v)):
        v[i] = max(v[i], lo if i == 0 else v[i - 1] + gap)
    for i in range(len(v) - 1, -1, -1):
        v[i] = min(v[i], hi if i == len(v) - 1 else v[i + 1] - gap)
    out = [0.0] * len(ys)
    for k, i in enumerate(order):
        out[i] = v[k]
    return out


def encode(img, fmt: str, quality: int) -> str:
    from PIL import Image  # noqa: F401
    buf = io.BytesIO()
    if fmt == "jpeg":
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            bg = img.__class__.new("RGB", img.size, "white")
            bg.paste(img, mask=img.split()[-1])
            img = bg
        img.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True)
        mime = "image/jpeg"
    elif fmt == "webp":
        img.save(buf, "WEBP", quality=quality)
        mime = "image/webp"
    else:
        img.save(buf, "PNG", optimize=True)
        mime = "image/png"
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()


def build(spec: dict, base: Path) -> str:
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Pillow is required: pip install pillow")
    img = Image.open(base / spec["image"])
    if spec.get("crop"):
        x0, y0, x1, y1 = spec["crop"]
        W, H = img.size
        img = img.crop((round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H)))
    if spec.get("whiten"):
        t = int(spec["whiten"])
        img = img.convert("RGB").point(lambda v: v)  # copy
        px = img.load()
        for yy in range(img.height):
            for xx in range(img.width):
                r, g, b = px[xx, yy]
                if r >= t and g >= t and b >= t:
                    px[xx, yy] = (255, 255, 255)
    mw = spec.get("max_width", 1400)
    if img.width > mw:
        img = img.resize((mw, round(img.height * mw / img.width)), Image.LANCZOS)
    w, h = img.size
    ml, mr = (m * w for m in spec.get("margin", [0.5, 0.5]))
    f = spec.get("font_px") or round(h * 0.032)
    gap_line = f * 1.55
    dot = f * 0.24
    stagger = spec.get("stagger", 0)
    total_w = ml + w + mr

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" class="labelled" viewBox="0 0 {total_w:.0f} {h}" '
             f'font-family="Arial, Helvetica, sans-serif">',
             f'<image href="{encode(img, spec.get("format", "jpeg"), spec.get("quality", 86))}" '
             f'x="{ml:.0f}" y="0" width="{w}" height="{h}"/>']
    for side in ("left", "right"):
        items = [lab for lab in spec["labels"] if lab.get("side", "left") == side]
        if not items:
            continue
        ys = spread([lab["at"][1] * h + f * 0.35 for lab in items], gap_line, f * 1.1, h - f * 0.4)
        for lab, y in zip(items, ys):
            px, py = ml + lab["at"][0] * w, lab["at"][1] * h
            if side == "left":
                tx, anchor, lx = ml - f * 0.9, "end", ml - f * 0.55
            else:
                tx, anchor, lx = ml + w + f * 0.9, "start", ml + w + f * 0.55
            ly = y - f * 0.35
            k = spec["labels"].index(lab)
            cls = f' class="a-in" style="--d:{0.3 + k * stagger:.2f}s"' if stagger else ""
            parts.append(
                f'<g{cls}><path d="M{lx:.0f} {ly:.0f} L{px:.0f} {py:.0f}" stroke="#5F6B78" stroke-width="{f * 0.07:.1f}" fill="none"/>'
                f'<circle cx="{px:.0f}" cy="{py:.0f}" r="{dot:.1f}" fill="#1B2430" stroke="#fff" stroke-width="{dot * 0.5:.1f}"/>'
                f'<text x="{tx:.0f}" y="{y:.0f}" font-size="{f}" fill="#1B2430" text-anchor="{anchor}">'
                f'{html.escape(lab["text"])}</text></g>')
    parts.append("</svg>")
    return "\n".join(parts)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    sp = Path(a.spec)
    svg = build(json.loads(sp.read_text(encoding="utf-8")), sp.parent)
    Path(a.out).write_text(svg, encoding="utf-8")
    print(f"{a.out}: {len(svg) // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
