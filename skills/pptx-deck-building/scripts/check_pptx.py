#!/usr/bin/env python3
"""Check a .pptx for problems an audience would see, and render it for a visual look.

Checks per slide: shapes outside the slide; text likely to overflow its box (estimated
from characters, font size and box area); text below the size floor; pictures without
alt text; missing speaker notes.
--render DIR exports PNGs via PowerPoint (Windows) or LibreOffice + PyMuPDF.

Usage: python check_pptx.py talk.pptx [--min-body 18] [--min-any 10] [--render build/render]
Requires python-pptx.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from pptx import Presentation
    from pptx.util import Emu
except ImportError:
    sys.exit("python-pptx is required: pip install python-pptx")

EMU_PER_PT = 12700


def est_overflow(shape) -> float:
    """Ratio of estimated text height to box height (>1.05 means it probably overflows)."""
    tf = shape.text_frame
    w_pt = max(1, (shape.width - (tf.margin_left or 0) - (tf.margin_right or 0)) / EMU_PER_PT)
    h_pt = max(1, (shape.height - (tf.margin_top or 0) - (tf.margin_bottom or 0)) / EMU_PER_PT)
    total = 0.0
    nowrap = tf.word_wrap is False
    for p in tf.paragraphs:
        size = next((r.font.size.pt for r in p.runs if r.font.size), 18.0)
        chars = sum(len(r.text) for r in p.runs) or 1
        per_line = max(1, w_pt / (size * 0.5))  # average glyph ≈ 0.5 em
        lines = 1 if nowrap else -(-chars // per_line)
        total += lines * size * 1.2 + (p.space_after.pt if p.space_after else 0)
    return total / h_pt


def render(path: Path, rdir: Path) -> str:
    rdir.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        ps = (f"$a=New-Object -ComObject PowerPoint.Application;$p=$a.Presentations.Open('{path.resolve()}',$true,$false,$false);"
              f"foreach($s in $p.Slides){{$s.Export('{rdir.resolve()}\\slide-'+$s.SlideIndex.ToString('00')+'.png','PNG',1920,1080)}};$p.Close();$a.Quit()")
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
        if r.returncode == 0 and any(rdir.glob("*.png")):
            return f"rendered with PowerPoint to {rdir}"
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(rdir), str(path)], capture_output=True)
        pdf = rdir / (path.stem + ".pdf")
        try:
            try:
                import pymupdf as fitz  # type: ignore
            except ImportError:
                import fitz  # type: ignore
            for i, page in enumerate(fitz.open(pdf), 1):
                page.get_pixmap(dpi=144).save(rdir / f"slide-{i:02d}.png")
            return f"rendered with LibreOffice to {rdir} (fonts may differ from PowerPoint)"
        except Exception as e:
            return f"LibreOffice made {pdf}, but PNG export failed: {e}"
    return "no renderer: install LibreOffice or open in PowerPoint"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx")
    ap.add_argument("--min-body", type=float, default=18)
    ap.add_argument("--min-any", type=float, default=10)
    ap.add_argument("--render")
    a = ap.parse_args(argv)
    prs = Presentation(a.pptx)
    W, H = prs.slide_width, prs.slide_height
    issues = []
    for i, slide in enumerate(prs.slides, 1):
        for shp in slide.shapes:
            name = shp.name
            if shp.left is not None and (shp.left < -Emu(9525) or shp.top < -Emu(9525) or
                                         shp.left + shp.width > W + Emu(9525) or shp.top + shp.height > H + Emu(9525)):
                issues.append((i, "off-slide", name))
            if shp.has_text_frame and shp.text_frame.text.strip():
                ratio = est_overflow(shp)
                if ratio > 1.05 and not shp.is_placeholder:
                    issues.append((i, "may-overflow", f"{name} (text ≈ {ratio:.0%} of box height)"))
                for p in shp.text_frame.paragraphs:
                    for r in p.runs:
                        if r.font.size and r.text.strip():
                            if r.font.size.pt < a.min_any:
                                issues.append((i, "tiny-text", f"{name}: {r.font.size.pt:g} pt '{r.text[:30]}'"))
                            elif r.font.size.pt < a.min_body and name.startswith("Body"):
                                issues.append((i, "small-body", f"{name}: {r.font.size.pt:g} pt"))
            if shp.shape_type == 13:  # picture
                descr = shp._element.nvPicPr.cNvPr.get("descr")
                if not descr:
                    issues.append((i, "no-alt-text", name))
        if not (slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip()):
            issues.append((i, "no-notes", ""))
    print(f"# check_pptx: {Path(a.pptx).name}, {len(prs.slides)} slides, {len(issues)} issue(s)")
    for s, kind, what in issues:
        print(f"- slide {s}: {kind} {what}")
    if a.render:
        print(render(Path(a.pptx), Path(a.render)))
    serious = [x for x in issues if x[1] in ("off-slide", "may-overflow", "tiny-text")]
    return 1 if serious else 0


if __name__ == "__main__":
    sys.exit(main())
