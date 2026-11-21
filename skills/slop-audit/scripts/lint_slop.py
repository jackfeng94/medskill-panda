#!/usr/bin/env python3
"""Mechanical slop checks for HTML and PPTX decks (the ⚙ rows of catalog.md).

Usage:
  python lint_slop.py deck.html [--lang auto|en|vi] [--max-words N] [--json]
  python lint_slop.py deck.pptx            (needs python-pptx)
  python lint_slop.py deck.pdf             (Beamer or exported decks; needs pypdf)

Speaker notes (<aside class="notes">, PPTX notes) are never linted: cues belong there.
Exit code 1 when a blocking rule (S00-S04) fires. S00 means no slide was recognised: an HTML
deck must mark each slide <section class="slide">, otherwise nothing could be checked.
"""
from __future__ import annotations

import argparse
import html.parser
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# deck_text.py has one copy, owned by the evidence-audit skill next to this one.
_HERE = Path(__file__).resolve().parent
for _d in (_HERE, _HERE.parents[1] / "evidence-audit" / "scripts"):
    if (_d / "deck_text.py").is_file():
        sys.path.insert(0, str(_d))
        break
else:
    sys.exit("lint_slop: deck_text.py not found. Install the evidence-audit skill next to slop-audit "
             "(both come with the medskill-panda plugin).")
from deck_text import load_slides  # noqa: E402

BLOCKING = {"S00", "S01", "S02", "S03", "S04"}
NO_SLIDES = ("no slides recognised: mark each slide <section class=\"slide\">; nothing else was checked")

PRESENTER_CUE = re.compile(
    r"(?:^|\s|[(▸►→>])(?:click(?:ing)?\s+(?:to|for|next|here)|press\s+\S+\s+(?:to|for)|hover\s+(?:to|over)|"
    r"tap\s+to|scroll\s+(?:down|to)|next\s+slide|"
    r"bấm\s+(?:tiếp|để|vào|phím)|nhấn\s+(?:tiếp|để|vào|phím)|nhấp\s+(?:để|vào|tiếp)|rê\s+chuột|di\s+chuột|"
    r"\((?:animation|hiệu\s+ứng|click|bấm)\))", re.I)
CUE_ARROW = re.compile(r"(?:^|\s)[▸►]\s*\S")
PROCESS = re.compile(
    r"recolou?red|re-colou?red|redrawn\s+for|đổi\s+màu|nguyên\s+bản|"
    r"(?:generated|created|made|drawn|redrawn|written)\s+(?:by|with|using)\s+(?:AI|ChatGPT|Claude|GPT[-\w]*|Gemini|an?\s+(?:AI|LLM|model))|"
    r"AI-generated|adapted\s+(?:by|with)\s+AI|tạo\s+bằng\s+AI|do\s+AI\s+tạo|AI\s+tạo\s+ra|vẽ\s+lại\s+bằng\s+AI", re.I)
PLACEHOLDER = re.compile(r"lorem\s+ipsum|\bTODO\b|\bTBD\b|\[insert[^\]]*\]|\bXX(?:\.X)?%|\{\{[^}]*\}\}|<placeholder>", re.I)
NUMBERED_LABEL = re.compile(r"(?:^|\s)0[1-9]\s*[·•|/]\s*[A-ZÀ-ỸĐ]")
NOT_X_DASH = re.compile(r"\b(?:not|không\s+chỉ|không\s+phải|chẳng\s+phải)\b[^—]{0,60}—", re.I)
STOCK = re.compile(
    r"key\s+takeaways?|let'?s\s+dive\s+in|deep\s+dive|game[-\s]changer|unlock(?:s|ing)?\b|revolutioni[sz]e|paradigm\s+shift|"
    r"in\s+today'?s\s+fast-paced|cutting[-\s]edge|seamless(?:ly)?|delve|testament\s+to|"
    r"điểm\s+nhấn|bước\s+ngoặt|cuộc\s+cách\s+mạng|đột\s+phá\s+vượt\s+bậc|khám\s+phá\s+ngay", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U00002600-\U000026FF⭐✅❌]")
VI_CHARS = re.compile(r"[ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.I)

EYEBROW_CLS = re.compile(r"\b(?:eyebrow|kicker|overline|pre-?title|super-?title|pretitle|sh)\b", re.I)
CARD_CLS = re.compile(r"\b(?:kpi|stat-card|metric-card|metric|stat|card)\b", re.I)
CHIP_CLS = re.compile(r"\b(?:chip|pill|badge)\b", re.I)
COUNTER_CLS = re.compile(r"\b(?:num|counter|step-num|section-num|no)\b", re.I)
CREDIT_CLS = re.compile(r"\b(?:cite|citation|credit|source)\b", re.I)
EXCLUDE_BODY_CLS = re.compile(r"\b(?:notes|footer|ftr|cite|citation|source|refs?|references?|credit|caption|legend|pg)\b", re.I)


class _ElementTexts(html.parser.HTMLParser):
    """Collect (slide, class, text) for every classed element, and body text per slide."""

    VOID = {"br", "img", "hr", "meta", "link", "input", "source", "wbr", "area", "col", "embed", "param", "track"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slide = 0
        self.stack: list[dict] = []
        self.elements: list[dict] = []
        self.body: dict[int, list[str]] = defaultdict(list)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "") or ""
        is_slide = tag == "section" and re.search(r"\bslide\b", cls)
        if is_slide:
            self.slide += 1
        node = {"tag": tag, "cls": cls, "text": [], "slide": self.slide if (is_slide or self._in_slide()) else 0,
                "is_slide": bool(is_slide)}
        if tag not in self.VOID:
            self.stack.append(node)
            if cls and node["slide"]:
                self.elements.append(node)

    def _in_slide(self):
        return any(n["is_slide"] for n in self.stack)

    def handle_endtag(self, tag):
        while self.stack:
            n = self.stack.pop()
            if n["tag"] == tag:
                break

    def handle_data(self, data):
        if not self._in_slide():
            return
        tags = [n["tag"] for n in self.stack]
        if any(t in ("script", "style", "template") for t in tags):
            return
        for n in self.stack:
            n["text"].append(data)
        excluded = any(t in ("svg", "footer", "figcaption", "aside") for t in tags) or \
            any(EXCLUDE_BODY_CLS.search(n["cls"]) for n in self.stack if n["cls"])
        if not excluded:
            self.body[self.slide].append(data)


def _txt(node) -> str:
    return " ".join("".join(node["text"]).split())


def lint_html(path: Path, lang: str, max_words: int | None) -> list[dict]:
    src = path.read_text(encoding="utf-8", errors="replace")
    slides = load_slides(path)
    p = _ElementTexts()
    p.feed(src)
    out: list[dict] = []

    def add(rule, slide, text, note=""):
        out.append({"id": rule, "slide": slide, "text": text[:160], "note": note,
                    "severity": "blocking" if rule in BLOCKING else "advisory"})

    # class-based rules
    cards, chips = defaultdict(int), defaultdict(int)
    for e in p.elements:
        t = _txt(e)
        if EYEBROW_CLS.search(e["cls"]) and t and len(t) < 90:
            add("S01", e["slide"], t, f'class="{e["cls"]}"')
        if CARD_CLS.search(e["cls"]):
            cards[e["slide"]] += 1
        if CHIP_CLS.search(e["cls"]):
            chips[e["slide"]] += 1
        if COUNTER_CLS.search(e["cls"]) and re.fullmatch(r"0\d", t or ""):
            add("S13", e["slide"], t, f'class="{e["cls"]}"')
    for s, n in cards.items():
        if n >= 4:
            add("S07", s, f"{n} card-like elements", "identical cards for each number")
    for s, n in chips.items():
        if n >= 3:
            add("S08", s, f"{n} chips/pills/badges")

    # CSS-level decoration
    css = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", src, re.S | re.I))
    css = re.sub(r"url\(\s*['\"]?data:[^)]*\)", "url()", css)  # drop embedded fonts/images
    if re.search(r"background-clip\s*:\s*text|text-fill-color\s*:\s*transparent", css, re.I):
        add("S10", 0, "gradient text (background-clip:text)")
    if re.search(r"backdrop-filter\s*:\s*blur", css, re.I):
        add("S10", 0, "glassmorphism (backdrop-filter: blur)")
    for sel, px in re.findall(r"([^{}]{1,300})\{[^{}]*?font-size\s*:\s*(\d+(?:\.\d+)?)px", css):
        if float(px) < 12:
            add("S19", 0, f"{sel.strip()[:60]} {{font-size:{px}px}}", "below 12 px at 1920×1080")

    if not slides:
        add("S00", 0, NO_SLIDES)
        return out
    eyebrows = {(e["slide"], _txt(e)) for e in p.elements if EYEBROW_CLS.search(e["cls"])}
    credits: dict[int, list[str]] = defaultdict(list)
    for e in p.elements:
        if CREDIT_CLS.search(e["cls"]):
            credits[e["slide"]].append(_txt(e))

    # text rules per slide (visible text only), matched block by block so that each finding
    # quotes its own element and one phrase is reported once
    for s in slides:
        idx, text = s["index"], s["text"]
        for block in s.get("blocks") or [text]:
            cues = [m for m in PRESENTER_CUE.finditer(block)]
            for m in cues:
                add("S02", idx, _ctx(block, m))
            if not cues:
                for m in CUE_ARROW.finditer(block):
                    add("S02", idx, _ctx(block, m), "▸ cue marker")
            # S03 ignores source credits: "Illustration: generated with ChatGPT, anatomy checked..."
            # is a disclosure the audience is owed, not process narration
            if not any(block in c for c in credits.get(idx, ())):
                for m in PROCESS.finditer(block):
                    add("S03", idx, _ctx(block, m))
            for m in PLACEHOLDER.finditer(block):
                add("S04", idx, _ctx(block, m))
            if (idx, block) not in eyebrows:
                for m in NUMBERED_LABEL.finditer(block):
                    add("S01", idx, _ctx(block, m), "numbered section label")
            for m in NOT_X_DASH.finditer(block):
                add("S14", idx, _ctx(block, m), '"not X — Y"')
            for m in STOCK.finditer(block):
                add("S15", idx, _ctx(block, m))
            for m in EMOJI.finditer(block):
                add("S16", idx, m.group(0))
        if text.count("—") >= 3:
            add("S14", idx, f"{text.count('—')} em dashes")

        body = " ".join(" ".join(p.body.get(idx, [])).split())
        lang_s = lang if lang != "auto" else ("vi" if len(VI_CHARS.findall(body)) > 8 else "en")
        limit = max_words or (60 if lang_s == "vi" else 40)
        words = len(body.split())
        if idx > 1 and words > limit:
            add("S18", idx, f"{words} words of body text (limit {limit}, {lang_s})")
    return _dedupe(out)


def lint_text_slides(slides: list[dict], max_words: int | None) -> list[dict]:
    """Text-only rules for decks without HTML classes (PPTX shapes, PDF pages)."""
    out = []
    if not slides:
        return [{"id": "S00", "slide": 0, "text": "no slides found in the file", "note": "",
                 "severity": "blocking"}]
    for s in slides:
        idx, text = s["index"], s["text"]
        for block in s.get("blocks") or [text]:
            for rule, rx in (("S02", PRESENTER_CUE), ("S03", PROCESS), ("S04", PLACEHOLDER),
                             ("S01", NUMBERED_LABEL), ("S15", STOCK)):
                for m in rx.finditer(block):
                    out.append({"id": rule, "slide": idx, "text": _ctx(block, m), "note": "",
                                "severity": "blocking" if rule in BLOCKING else "advisory"})
        body = s.get("body", text)  # PPTX: without footer, page number and source credit
        limit = max_words or (60 if len(VI_CHARS.findall(text)) > 8 else 40)
        if idx > 1 and len(body.split()) > limit:
            out.append({"id": "S18", "slide": idx, "text": f"{len(body.split())} words (limit {limit})",
                        "note": "", "severity": "advisory"})
    return out


def lint_pdf(path: Path, max_words: int | None) -> list[dict]:
    return _dedupe(lint_text_slides(load_slides(path), max_words))


def lint_pptx(path: Path, max_words: int | None) -> list[dict]:
    from pptx import Presentation  # type: ignore
    prs = Presentation(str(path))
    out = lint_text_slides(load_slides(path), max_words)
    for i, slide in enumerate(prs.slides, 1):
        for shp in slide.shapes:
            if not shp.has_text_frame:
                continue
            for para in shp.text_frame.paragraphs:
                for run in para.runs:
                    if run.font.size is not None and run.font.size.pt < 10 and run.text.strip():
                        out.append({"id": "S19", "slide": i, "text": f"{run.font.size.pt:g} pt: {run.text[:40]}",
                                    "note": "below 10 pt", "severity": "advisory"})
    return _dedupe(out)


def _ctx(text: str, m: re.Match, pad: int = 40) -> str:
    if len(text) <= 120:  # a whole block is short enough to quote as it is
        return text
    a, b = max(0, m.start() - pad // 2), min(len(text), m.end() + pad)
    return text[a:b].strip()


def _dedupe(items):
    seen, out = set(), []
    for x in items:
        k = (x["id"], x["slide"], x["text"])
        if k not in seen:
            seen.add(k)
            out.append(x)
    return sorted(out, key=lambda x: (x["severity"] != "blocking", x["slide"], x["id"]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--lang", default="auto", choices=["auto", "en", "vi"])
    ap.add_argument("--max-words", type=int)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    path = Path(a.deck)
    suffix = path.suffix.lower()
    if suffix in (".pptx", ".potx"):
        findings = lint_pptx(path, a.max_words)
    elif suffix == ".pdf":
        findings = lint_pdf(path, a.max_words)
    else:
        findings = lint_html(path, a.lang, a.max_words)
    if a.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        nb = sum(f["severity"] == "blocking" for f in findings)
        print(f"# lint_slop: {path.name}: {nb} blocking, {len(findings) - nb} advisory")
        for f in findings:
            where = f"slide {f['slide']}" if f["slide"] else "deck"
            note = f"  ({f['note']})" if f["note"] else ""
            print(f"- {f['id']} [{f['severity']}] {where}: {f['text']}{note}")
    return 1 if any(f["severity"] == "blocking" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
