#!/usr/bin/env python3
"""Prose and number checks for a manuscript in Vietnamese or English.

Usage:
  python lint_prose.py manuscript.docx [--lang auto|vi|en] [--json]
  python lint_prose.py manuscript.md --compare manuscript_en.md     (bilingual versions)

Reads .md, .txt, .tex and .docx (standard library only). It complements
lint_manuscript.py, which checks Markdown declarations and confidentiality gates:

  P01 error    placeholder or explicit gap left in the text (TODO, [MISSING: …], XX%, ??)
  P02 warning  stock "machine-made" phrase (delve, pivotal; đóng vai trò then chốt, …)
  P03 warning  overstatement (proves, highly significant; chứng minh, hoàn toàn, …)
  P04 warning  statistic outside Methods/Results with no citation in the same sentence
  P05 warning  p-value written as p = 0.000 (report p < 0.001)
  P06 warning  mixed decimal separators (0,58 and 0.58 in one document)
  P07 warning  body text that is mostly bullet points
  P08 warning  heavy em-dash use
  P09 warning  numbers that differ between two language versions (--compare)

Findings quote only the matched phrase, never whole sentences. The References section is
checked for placeholders only. Exit code 1 when an error-level finding remains.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MAX_BYTES = 30 * 1024 * 1024
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

PLACEHOLDER = re.compile(
    r"\bTODO\b|\bTBD\b|\[\s*MISSING\b[^\]]*\]|\[\s*(?:insert|add|citation needed|cần bổ sung|bổ sung)[^\]]*\]|"
    r"lorem\s+ipsum|\bXX(?:[.,]X+)?\s?%|\b20XX\b|\(\s*Author,?\s+Year\s*\)|\[\?\]|(?<![\w?])\?\?(?![\w?])",
    re.I)

STOCK = {
    "en": re.compile(
        r"\bdelv(?:e|es|ed|ing)\b|\bpivotal\b|\bintricate\b|\btapestry\b|\bmultifaceted\b|\ba myriad of\b|"
        r"\bplay(?:s|ed|ing)? an? (?:crucial|pivotal|vital|key|critical) role\b|\bin the realm of\b|"
        r"\bit is (?:important|worth|crucial) (?:to note|noting)\b|\ba testament to\b|\bnavigat\w* the complexit\w*|"
        r"\bshed(?:s|ding)? (?:new )?light on\b|\bpav(?:e|es|ed|ing) the way\b|\bgame[- ]changer\b|"
        r"\bever[- ](?:evolving|changing)\b|\bin today'?s (?:world|fast)|\bunderscor(?:e|es|ed|ing) the (?:importance|need)\b|"
        r"\bthe (?:evolving|complex|dynamic) landscape of\b|\bholds? (?:great|immense|tremendous) promise\b",
        re.I),
    "vi": re.compile(
        r"đóng (?:một )?vai trò (?:then chốt|quan trọng|vô cùng quan trọng|chủ chốt)|ngày càng (?:được|nhận được sự) quan tâm|"
        r"mở ra (?:hướng đi|triển vọng|kỷ nguyên) mới|bước ngoặt|cuộc cách mạng|không thể phủ nhận|có thể nói rằng|"
        r"trong bối cảnh hiện nay|trong thời đại ngày nay|hết sức cần thiết|vô cùng quan trọng|góp phần không nhỏ|"
        r"đáng chú ý là|toàn diện và sâu sắc|tóm lại,? có thể thấy",
        re.I),
}
OVERSTATE = {
    "en": re.compile(
        r"\bprov(?:e|es|ed|en)\b|\bdefinitive(?:ly)?\b|\bhighly significant\b|\btrend(?:ed|ing)? toward(?:s)? significance\b|"
        r"\bguarantee(?:s|d)?\b|\bclearly demonstrat\w+|\bundeniabl\w+|\bconclusively\b|\bno limitations\b",
        re.I),
    "vi": re.compile(
        r"chứng minh (?:rằng|được|là)|khẳng định chắc chắn|\bhoàn toàn (?:không|có|hiệu quả|an toàn|khỏi)|tuyệt đối|"
        r"rất có ý nghĩa thống kê|có xu hướng có ý nghĩa|100% hiệu quả|chắc chắn rằng",
        re.I),
}
STAT = re.compile(
    r"\d+(?:[.,]\d+)?\s?%|\b(?:a?HR|a?OR|RR|IRR|NNT|AUC|SMD|MD)\s*[=:]?\s*\d|\b(?:95|99)\s?%\s?(?:CI|KTC)\b|"
    r"\bKTC\s?(?:95|99)\s?%|\bp\s?[<=>≤≥]\s?0?[.,]\d+",
    re.I)
CITATION = re.compile(
    r"\[\s*\d+(?:\s*[-–,]\s*\d+)*\s*\]|\[\^[^\]]+\]|\[cite\]|\[@[^\]]+\]|\[evidence:E\d+|"
    r"\(\s*[A-ZÀ-ỸĐ][^()]{0,80}?(?:19|20)\d{2}[a-z]?\s*\)|\^\d+")
P_ZERO = re.compile(r"\bp\s?=\s?0[.,]0{2,}\b(?!\d*[1-9])", re.I)
DEC_DOT = re.compile(r"(?<![\w.,/])\d{1,4}\.\d{1,4}(?![\w.,/])")
DEC_COMMA = re.compile(r"(?<![\w.,/])\d{1,4},\d{1,3}(?![\d,.])")
NUMBER = re.compile(r"(?<![\w])\d+(?:[.,]\d+)?")
VI_CHARS = re.compile(r"[ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.I)
SENTENCE = re.compile(r"(?<=[.!?…])\s+(?=[\"“(\[A-ZÀ-ỸĐ0-9])")

NO_CITE_SECTIONS = re.compile(
    r"result|kết quả|method|phương pháp|đối tượng|material|abstract|tóm tắt|summary|table|bảng|appendix|phụ lục|"
    r"characteristic|đặc điểm|supplement",
    re.I)
REFERENCES = re.compile(r"^\s*(?:\d+[.)]?\s*)?(?:references?|bibliography|tài liệu tham khảo|literature cited)\s*$", re.I)


# ---------------------------------------------------------------------------- reading


def _block(kind: str, text: str, where: str) -> dict:
    return {"kind": kind, "text": " ".join(text.split()), "where": where}


def read_markdown(src: str) -> list[dict]:
    blocks, para, start, fence = [], [], 0, False

    def flush():
        if para:
            blocks.append(_block("para", " ".join(para), f"line {start}"))
            para.clear()

    for n, line in enumerate(src.splitlines(), 1):
        s = line.strip()
        if s.startswith(("```", "~~~")):
            flush()
            fence = not fence
            continue
        if fence:
            continue
        if not s:
            flush()
        elif s.startswith("#"):
            flush()
            blocks.append(_block("heading", s.lstrip("#"), f"line {n}"))
        elif s.startswith("|"):
            flush()
            blocks.append(_block("table", s, f"line {n}"))
        elif re.match(r"^(?:[-*+•]|\d+[.)])\s+", s):
            flush()
            blocks.append(_block("bullet", re.sub(r"^(?:[-*+•]|\d+[.)])\s+", "", s), f"line {n}"))
        else:
            if not para:
                start = n
            para.append(s)
    flush()
    return blocks


def _tex_text(s: str) -> str:
    s = re.sub(r"\\(?:begin|end)\{[^}]*\}(?:\[[^\]]*\])?", " ", s)
    s = re.sub(r"\\(?:cite|citep|citet|parencite|autocite|footcite|ref|eqref|autoref|cref)\*?(?:\[[^\]]*\])*\{[^}]*\}",
               "[cite]", s)
    s = re.sub(r"\\([%&$#_])", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", s)
    return s.replace("{", "").replace("}", "").replace("~", " ")


def read_tex(src: str) -> list[dict]:
    # blank out comments and the preamble but keep every newline, so line numbers stay true
    src = re.sub(r"(?<!\\)%[^\n]*", "", src)
    begin = src.find("\\begin{document}")
    if begin != -1:
        cut = begin + len("\\begin{document}")
        src = re.sub(r"[^\n]", " ", src[:cut]) + src[cut:]
    end = src.find("\\end{document}")
    if end != -1:
        src = src[:end]
    src = re.sub(r"\\begin\{(table|tabular|figure)(\*?)\}.*?\\end\{\1\2\}",
                 lambda m: "\\TABLEBLOCK" + "\n" * m.group(0).count("\n"), src, flags=re.S)
    # cut points: headings, blank lines, \item and table blocks, in document order
    marks = re.compile(r"(?P<h>\\(?:part|chapter|section|subsection|subsubsection|paragraph)\*?\s*(?:\[[^\]]*\])?\s*"
                       r"\{(?P<title>[^{}]*)\})|(?P<blank>\n[ \t]*\n)|(?P<item>\\item\b)|(?P<tab>\\TABLEBLOCK)")
    blocks, pos, kind = [], 0, "para"

    def emit(seg: str, start: int, k: str) -> None:
        text = _tex_text(seg)
        if text.strip():
            lead = len(seg) - len(seg.lstrip())
            blocks.append(_block(k, text, f"line {src.count(chr(10), 0, start + lead) + 1}"))

    for m in marks.finditer(src):
        emit(src[pos:m.start()], pos, kind)
        line = f"line {src.count(chr(10), 0, m.start()) + 1}"
        if m.group("h"):
            blocks.append(_block("heading", m.group("title"), line))
            kind = "para"
        elif m.group("tab"):
            blocks.append(_block("table", "", line))
            kind = "para"
        elif m.group("item"):
            kind = "bullet"
        else:
            kind = "para"
        pos = m.end()
    emit(src[pos:], pos, kind)
    return blocks


def read_docx(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as z:
        info = z.getinfo("word/document.xml")
        if info.file_size > MAX_BYTES:
            raise SystemExit("lint_prose: document.xml is too large")
        root = ET.fromstring(z.read(info))
    body = root.find(f"{W}body")
    blocks: list[dict] = []
    count = 0

    def para_text(p) -> str:
        out = []
        for r in p.iter(f"{W}r"):
            sup = r.find(f"{W}rPr/{W}vertAlign")
            t = "".join(x.text or "" for x in r.iter(f"{W}t"))
            if r.find(f"{W}footnoteReference") is not None or r.find(f"{W}endnoteReference") is not None:
                t = "[^n]"
            elif sup is not None and sup.get(f"{W}val") == "superscript" and t.strip():
                t = f"[^{t}]"
            out.append(t)
        return "".join(out)

    def walk(el, in_table: bool) -> None:
        nonlocal count
        for child in el:
            if child.tag == f"{W}p":
                count += 1
                text = para_text(child)
                if not text.strip():
                    continue
                style = child.find(f"{W}pPr/{W}pStyle")
                sval = (style.get(f"{W}val") if style is not None else "") or ""
                if in_table:
                    kind = "table"
                elif re.match(r"(?i)heading|title|tieude|tiêuđề|u\d", sval.replace(" ", "")):
                    kind = "heading"
                elif child.find(f"{W}pPr/{W}numPr") is not None or re.match(r"(?i)list", sval):
                    kind = "bullet"
                else:
                    kind = "para"
                blocks.append(_block(kind, text, f"para {count}"))
            elif child.tag == f"{W}tbl":
                for p in child.iter(f"{W}p"):
                    count += 1
                    text = para_text(p)
                    if text.strip():
                        blocks.append(_block("table", text, f"para {count}"))
            elif child.tag in (f"{W}sdt", f"{W}sdtContent", f"{W}customXml"):
                walk(child, in_table)

    walk(body, False)
    return blocks


def read_blocks(path: Path) -> list[dict]:
    if path.stat().st_size > MAX_BYTES:
        raise SystemExit(f"lint_prose: {path.name} is larger than {MAX_BYTES // 1024 // 1024} MB")
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return read_docx(path)
    src = path.read_text(encoding="utf-8", errors="replace")
    return read_tex(src) if suffix == ".tex" else read_markdown(src)


def with_sections(blocks: list[dict]) -> list[dict]:
    """Attach the current heading to each block; mark the References section."""
    out, section, in_refs = [], "", False
    for b in blocks:
        if b["kind"] == "heading":
            section = b["text"]
            in_refs = bool(REFERENCES.match(section))
        out.append(dict(b, section=section, refs=in_refs))
    return out


def detect_lang(blocks: list[dict]) -> str:
    text = " ".join(b["text"] for b in blocks[:400] if not b.get("refs"))
    return "vi" if len(VI_CHARS.findall(text)) > max(4, len(text) // 200) else "en"


# ---------------------------------------------------------------------------- checks


def lint(blocks: list[dict], lang: str) -> list[dict]:
    out: list[dict] = []
    refs = [b for b in blocks if b.get("refs")]
    blocks = [b for b in blocks if not b.get("refs")]

    def add(rule, sev, b, text, note=""):
        out.append({"id": rule, "severity": sev, "where": b["where"] if b else "document",
                    "section": (b or {}).get("section", ""), "text": text[:80], "note": note})

    body = [b for b in blocks if b["kind"] in ("para", "bullet")]
    for b in refs:  # the reference list is only checked for leftovers
        for m in PLACEHOLDER.finditer(b["text"]):
            add("P01", "error", b, m.group(0))
    for b in blocks:
        t = b["text"]
        for m in PLACEHOLDER.finditer(t):
            add("P01", "error", b, m.group(0))
        if b["kind"] in ("table", "heading"):
            continue
        for m in STOCK[lang].finditer(t):
            add("P02", "warning", b, m.group(0))
        for m in OVERSTATE[lang].finditer(t):
            add("P03", "warning", b, m.group(0))
        for m in P_ZERO.finditer(t):
            add("P05", "warning", b, m.group(0), "report p < 0.001")
        if not NO_CITE_SECTIONS.search(b.get("section", "")):
            for sentence in SENTENCE.split(t):
                stat = STAT.search(sentence)
                if stat and not CITATION.search(sentence):
                    add("P04", "warning", b, stat.group(0), "statistic without a citation in its sentence")

    all_text = " ".join(b["text"] for b in blocks if b["kind"] != "heading")
    dots, commas = len(DEC_DOT.findall(all_text)), len(DEC_COMMA.findall(all_text))
    if lang == "vi" and dots and commas:
        add("P06", "warning", None, f"{commas} × 0,58 style and {dots} × 0.58 style",
            "use one decimal separator, as the venue requires")
    elif lang == "en" and commas and re.search(r"(?<![\w.,])0,\d", all_text):
        add("P06", "warning", None, f"{commas} comma decimal(s) such as 0,58", "English uses 0.58")

    if len(body) >= 10:
        bullets = sum(b["kind"] == "bullet" for b in body)
        if bullets / len(body) > 0.3:
            add("P07", "warning", None, f"{bullets} of {len(body)} body blocks are bullets",
                "academic text is expected as prose")
    words = len(" ".join(b["text"] for b in body).split())
    dashes = sum(b["text"].count("—") for b in body)
    if words and dashes * 1000 / words > 3 and dashes >= 4:
        add("P08", "warning", None, f"{dashes} em dashes in {words} words")
    return out


def compare_numbers(a: list[dict], b: list[dict]) -> list[dict]:
    def numbers(blocks):
        c = Counter()
        for blk in (x for x in blocks if not x.get("refs")):
            for m in NUMBER.finditer(CITATION.sub(" ", blk["text"])):  # citation numbers are not data
                v = m.group(0).replace(",", ".")
                c[v.rstrip("0").rstrip(".") if "." in v else v] += 1
        return c

    na, nb = numbers(a), numbers(b)
    out = []
    for v in sorted(set(na) | set(nb), key=lambda x: (len(x), x)):
        if na[v] != nb[v]:
            out.append({"id": "P09", "severity": "warning", "where": "document", "section": "",
                        "text": v, "note": f"{na[v]}× in this version, {nb[v]}× in the other"})
    return out[:40]


# ---------------------------------------------------------------------------- main


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manuscript", help=".md, .txt, .tex or .docx")
    ap.add_argument("--lang", default="auto", choices=["auto", "vi", "en"])
    ap.add_argument("--compare", help="the other language version, to check that numbers match")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    path = Path(a.manuscript)
    if not path.is_file():
        ap.error(f"{path} not found")
    blocks = with_sections(read_blocks(path))
    lang = a.lang if a.lang != "auto" else detect_lang(blocks)
    findings = lint(blocks, lang)
    if a.compare:
        findings += compare_numbers(blocks, with_sections(read_blocks(Path(a.compare))))
    findings.sort(key=lambda f: (f["severity"] != "error", f["id"]))
    errors = sum(f["severity"] == "error" for f in findings)
    if a.json:
        print(json.dumps({"file": path.name, "lang": lang, "errors": errors, "findings": findings},
                         ensure_ascii=False, indent=2))
    else:
        print(f"# lint_prose: {path.name} ({lang}): {errors} error(s), {len(findings) - errors} warning(s)")
        for f in findings:
            sec = f" [{f['section'][:40]}]" if f["section"] else ""
            note = f"  ({f['note']})" if f["note"] else ""
            print(f"- {f['id']} [{f['severity']}] {f['where']}{sec}: {f['text']}{note}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
