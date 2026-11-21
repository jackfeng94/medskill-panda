#!/usr/bin/env python3
"""Measure a PowerPoint template (.pptx/.potx) using only the standard library.

Writes <out>/scan.json and extracts media to <out>/media/. Optional:
  --render            export one PNG per slide via PowerPoint (Windows) or LibreOffice
  --sample IMG x,y …  print hex colours at pixel positions of an image (needs Pillow)

Usage:
  python scan_template.py template.pptx --out theme [--render]
  python scan_template.py template.pptx --sample theme/media/image2.jpeg 500,40 500,700
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

EMU_PER_IN = 914400
A = "http://schemas.openxmlformats.org/drawingml/2006/main"


def scheme_colors(theme_xml: str) -> dict:
    out = {}
    for name in ("dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6",
                 "hlink", "folHlink"):
        m = re.search(rf"<a:{name}>(.*?)</a:{name}>", theme_xml, re.S)
        if m:
            c = re.search(r'(?:srgbClr val|lastClr)="([0-9A-Fa-f]{6})"', m.group(1))
            if c:
                out[name] = "#" + c.group(1).upper()
    return out


def theme_fonts(theme_xml: str) -> dict:
    maj = re.search(r"<a:majorFont>.*?<a:latin typeface=\"([^\"]*)\"", theme_xml, re.S)
    mnr = re.search(r"<a:minorFont>.*?<a:latin typeface=\"([^\"]*)\"", theme_xml, re.S)
    return {"heading": maj.group(1) if maj else None, "body": mnr.group(1) if mnr else None}


def rels(z: zipfile.ZipFile, part: str) -> dict:
    p = Path(part)
    rp = str(p.parent / "_rels" / (p.name + ".rels")).replace("\\", "/")
    if rp not in z.namelist():
        return {}
    xml = z.read(rp).decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r'<Relationship [^>]*Id="([^"]+)"[^>]*Target="([^"]+)"', xml):
        out[m.group(1)] = os.path.normpath(os.path.join(str(p.parent), m.group(2))).replace("\\", "/")
    return out


def bg_image(z, part: str, xml: str):
    m = re.search(r"<p:bg>.*?r:embed=\"([^\"]+)\"", xml, re.S)
    if not m:
        return None
    return rels(z, part).get(m.group(1))


def scan(path: Path, out: Path) -> dict:
    z = zipfile.ZipFile(path)
    names = z.namelist()
    pres = z.read("ppt/presentation.xml").decode("utf-8", "replace")
    sz = re.search(r'<p:sldSz cx="(\d+)" cy="(\d+)"', pres)
    cx, cy = (int(sz.group(1)), int(sz.group(2))) if sz else (0, 0)
    themes = sorted(n for n in names if re.match(r"ppt/theme/theme\d+\.xml$", n))
    theme_xml = z.read(themes[0]).decode("utf-8", "replace") if themes else ""

    layouts = []
    for n in sorted((n for n in names if re.match(r"ppt/slideLayouts/slideLayout\d+\.xml$", n)),
                    key=lambda s: int(re.search(r"(\d+)\.xml", s).group(1))):
        xml = z.read(n).decode("utf-8", "replace")
        name = re.search(r'<p:cSld name="([^"]*)"', xml)
        phs = re.findall(r'<p:ph(?: type="(\w+)")?[^>]*?(?:idx="(\d+)")?', xml)
        layouts.append({"part": n, "name": name.group(1) if name else "",
                        "placeholders": [t or "body" for t, _ in phs], "background": bg_image(z, n, xml)})
    masters = []
    for n in sorted(n for n in names if re.match(r"ppt/slideMasters/slideMaster\d+\.xml$", n)):
        xml = z.read(n).decode("utf-8", "replace")
        masters.append({"part": n, "background": bg_image(z, n, xml)})

    used_fonts, used_colors, used_sizes = Counter(), Counter(), Counter()
    slides = []
    for n in sorted((n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                    key=lambda s: int(re.search(r"(\d+)\.xml", s).group(1))):
        xml = z.read(n).decode("utf-8", "replace")
        used_fonts.update(re.findall(r'<a:latin typeface="([^"+][^"]*)"', xml))
        used_colors.update("#" + c.upper() for c in re.findall(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', xml))
        used_sizes.update(int(s) / 100 for s in re.findall(r'<a:rPr[^>]*\bsz="(\d+)"', xml))
        layout = next((v for v in rels(z, n).values() if "slideLayout" in v), None)
        title = re.search(r'<p:ph type="(?:title|ctrTitle)".*?</p:sp>', xml, re.S)
        ttext = " ".join(re.findall(r"<a:t>([^<]*)</a:t>", title.group(0))) if title else ""
        box = None
        if title:
            off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>\s*<a:ext cx="(\d+)" cy="(\d+)"', title.group(0))
            if off:
                box = [round(int(v) / EMU_PER_IN, 3) for v in off.groups()]
        slides.append({"part": n, "layout": layout, "title": ttext[:80], "title_box_in": box})

    media_dir = out / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    media = []
    for n in names:
        if n.startswith("ppt/media/"):
            data = z.read(n)
            (media_dir / Path(n).name).write_bytes(data)
            info = {"file": f"media/{Path(n).name}", "bytes": len(data)}
            try:
                from PIL import Image  # type: ignore
                with Image.open(media_dir / Path(n).name) as im:
                    info["px"] = list(im.size)
            except Exception:
                pass
            media.append(info)

    result = {
        "source": str(path),
        "slide_size_in": [round(cx / EMU_PER_IN, 3), round(cy / EMU_PER_IN, 3)],
        "aspect": f"{cx / cy:.3f}" if cy else None,
        "theme_colors": scheme_colors(theme_xml),
        "theme_fonts": theme_fonts(theme_xml),
        "fonts_on_slides": dict(used_fonts.most_common()),
        "colors_on_slides": dict(used_colors.most_common(12)),
        "font_sizes_pt": dict(sorted(used_sizes.items(), key=lambda kv: -kv[1])[:10]),
        "masters": masters,
        "layouts": layouts,
        "slides": slides,
        "title_boxes_in": dict(Counter(str(x["title_box_in"]) for x in slides if x["title_box_in"]).most_common(3)),
        "media": media,
    }
    (out / "scan.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def render(path: Path, out: Path) -> str:
    rdir = out / "render"
    rdir.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        ps = (f"$a=New-Object -ComObject PowerPoint.Application;$p=$a.Presentations.Open('{path.resolve()}',$true,$false,$false);"
              f"foreach($s in $p.Slides){{$s.Export('{rdir.resolve()}\\slide'+$s.SlideIndex+'.png','PNG',1600,900)}};$p.Close();$a.Quit()")
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
        if r.returncode == 0 and any(rdir.glob("*.png")):
            return f"rendered with PowerPoint to {rdir}"
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(rdir), str(path)], capture_output=True)
        pdf = rdir / (path.stem + ".pdf")
        if pdf.exists():
            try:
                try:
                    import pymupdf as fitz  # type: ignore
                except ImportError:
                    import fitz  # type: ignore
                for i, page in enumerate(fitz.open(pdf), 1):
                    page.get_pixmap(dpi=110).save(rdir / f"slide{i}.png")
                return f"rendered with LibreOffice to {rdir}"
            except ImportError:
                return f"PDF at {pdf} (install pymupdf to split it into PNGs)"
    return "no renderer found: install LibreOffice, or open the file in PowerPoint and export images"


def sample(img: str, points: list[str]) -> None:
    from PIL import Image  # type: ignore
    im = Image.open(img).convert("RGB")
    for p in points:
        x, y = (int(v) for v in p.split(","))
        print(f"{p}\t#{'%02X%02X%02X' % im.getpixel((x, y))}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("template")
    ap.add_argument("--out", default="theme")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--sample", nargs="+", metavar=("IMAGE", "X,Y"))
    a = ap.parse_args(argv)
    if a.sample:
        sample(a.sample[0], a.sample[1:])
        return 0
    out = Path(a.out)
    res = scan(Path(a.template), out)
    print(f"{out / 'scan.json'}: {len(res['layouts'])} layouts, {len(res['slides'])} slides, "
          f"{len(res['media'])} media, size {res['slide_size_in']} in")
    print("theme colours:", res["theme_colors"])
    print("fonts on slides:", res["fonts_on_slides"])
    names = {l["part"]: l["name"] for l in res["layouts"]}
    used = {}
    for sl in res["slides"]:
        nm = f'{names.get(sl["layout"], "?")} ({Path(sl["layout"] or "").stem})'
        used[nm] = used.get(nm, 0) + 1
    print("layouts used by the template's own slides (use these):", used)
    print("title boxes on the template's slides [left, top, width, height] in:", res["title_boxes_in"])
    if a.render:
        print(render(Path(a.template), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
