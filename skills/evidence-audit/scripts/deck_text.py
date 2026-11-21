"""Shared helper: extract visible text per slide from an HTML deck or a .pptx file.

This is the only copy. slop-audit's lint_slop.py and the plugin hooks load it from here.

HTML decks: each <section class="slide ..."> is a slide; <aside class="notes"> is speaker
notes (returned separately), <script>/<style> are ignored. PPTX needs python-pptx; PDF
(Beamer and exported decks: one page = one slide) needs pypdf.

Each slide has `text` (all visible text on one line) and `blocks` (the text of each block
element, paragraph or shape separately), so a match can be reported with its own context
instead of running into the next element.
"""
from __future__ import annotations

import html.parser
import re
from pathlib import Path

BLOCK = {"p", "div", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "tr", "table",
         "figure", "figcaption", "header", "footer", "blockquote", "dt", "dd", "dl", "section", "article",
         "aside", "caption", "pre", "hr", "br", "text", "tspan", "g", "foreignobject"}
SEP = "\n"
VOID = {"br", "img", "hr", "meta", "link", "input", "source", "wbr", "area", "col", "embed", "param", "track"}


class _SlideParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides: list[dict] = []
        self.stack: list[tuple[str, str]] = []  # (tag, role)
        self.cur: dict | None = None
        self.depth_in_slide = 0

    def _role(self, tag, attrs):
        cls = dict(attrs).get("class", "") or ""
        if tag == "section" and re.search(r"\bslide\b", cls):
            return "slide"
        if tag == "aside" and re.search(r"\bnotes\b", cls):
            return "notes"
        if tag in ("script", "style", "template", "noscript"):
            return "skip"
        return ""

    def handle_starttag(self, tag, attrs):
        role = self._role(tag, attrs)
        if role == "slide":
            self.cur = {"index": len(self.slides) + 1, "text": [], "nosvg": [], "notes": [], "classes": [],
                        "name": dict(attrs).get("data-name", "")}
            self.slides.append(self.cur)
        if self.cur is not None:
            cls = dict(attrs).get("class")
            if cls:
                self.cur["classes"].append((tag, cls))
        if tag not in VOID:
            self.stack.append((tag, role))
        if tag in BLOCK and self.cur is not None:
            self.cur["text"].append(SEP)
            self.cur["nosvg"].append(SEP)

    def handle_endtag(self, tag):
        if tag in BLOCK and self.cur is not None:
            self.cur["text"].append(SEP)
            self.cur["nosvg"].append(SEP)
        while self.stack:
            t, role = self.stack.pop()
            if role == "slide":
                self.cur = None
            if t == tag:
                break

    def handle_data(self, data):
        if self.cur is None:
            return
        roles = [r for _, r in self.stack]
        if "skip" in roles:
            return
        if "notes" in roles:
            self.cur["notes"].append(data)
            return
        self.cur["text"].append(data)
        if not any(t == "svg" for t, _ in self.stack):
            self.cur["nosvg"].append(data)


def _flat(s: str) -> str:
    return " ".join(s.split())


def _blocks(s: str) -> list[str]:
    return [b for b in (_flat(x) for x in s.split(SEP)) if b]


def html_slides(src: str) -> list[dict]:
    p = _SlideParser()
    p.feed(src)
    out = []
    for s in p.slides:
        raw = "".join(s["text"])
        out.append({
            "index": s["index"],
            "name": s["name"],
            "text": _flat(raw),
            "blocks": _blocks(raw),
            "text_nosvg": _flat("".join(s["nosvg"])),
            "notes": " ".join(" ".join(s["notes"]).split()),
            "classes": s["classes"],
        })
    return out


def pptx_slides(path: Path) -> list[dict]:
    try:
        from pptx import Presentation  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise SystemExit("Reading .pptx needs python-pptx: pip install python-pptx") from e
    prs = Presentation(str(path))
    out = []
    for i, slide in enumerate(prs.slides, 1):
        texts = []
        for shp in slide.shapes:
            if shp.has_text_frame:
                texts.append(shp.text_frame.text)
            if getattr(shp, "has_table", False) and shp.has_table:
                for row in shp.table.rows:
                    texts.extend(c.text for c in row.cells)
        notes = slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""
        joined = " ".join(" ".join(texts).split())
        out.append({"index": i, "name": "", "text": joined, "text_nosvg": joined,
                    "blocks": [b for b in (_flat(x) for x in texts) if b],
                    "notes": " ".join(notes.split()), "classes": []})
    return out


def pdf_slides(path: Path) -> list[dict]:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise SystemExit("Reading .pdf needs pypdf: pip install pypdf") from e
    out = []
    for i, page in enumerate(PdfReader(str(path)).pages, 1):
        raw = page.extract_text() or ""
        joined = _flat(raw)
        out.append({"index": i, "name": "", "text": joined, "text_nosvg": joined,
                    "blocks": _blocks(raw), "notes": "", "classes": []})
    return out


def load_slides(path: str | Path) -> list[dict]:
    path = Path(path)
    if path.suffix.lower() in (".pptx", ".potx"):
        return pptx_slides(path)
    if path.suffix.lower() == ".pdf":
        return pdf_slides(path)
    return html_slides(path.read_text(encoding="utf-8", errors="replace"))
