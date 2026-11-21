#!/usr/bin/env python3
"""Flag text in a deck that could identify a patient (English and Vietnamese patterns).

Heuristic, not a guarantee: a clean scan does not clear a deck. Images, scans and
screenshots of records must be looked at by a person.

Usage: python phi_scan.py deck.html|deck.pptx [--include-notes] [--fail-on-hit]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deck_text import load_slides  # noqa: E402

UP = "A-ZÀ-ỸĐ"
NAME = rf"[{UP}][a-zà-ỹđ]+"

PATTERNS = [
    ("date", re.compile(r"\b\d{1,2}[/.-]\d{1,2}[/.-](?:19|20)?\d{2}\b")),
    ("date", re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b")),
    ("date", re.compile(r"\bngày\s+\d{1,2}\s+tháng\s+\d{1,2}(?:\s+năm\s+\d{4})?", re.I)),
    ("record-id", re.compile(r"\b(?:MRN|PID|hospital\s+no\.?|record\s+no\.?|mã\s*(?:BN|bệnh\s*nhân|hồ\s*sơ|y\s*tế)|"
                             r"số\s*(?:hồ\s*sơ|vào\s*viện|lưu\s*trữ|bệnh\s*án)|SBA|SVV)\s*[:#]?\s*[A-Z0-9][A-Z0-9/-]{3,}", re.I)),
    ("long-number", re.compile(r"(?<![\d.,])\d{8,}(?![\d.,])")),
    ("phone", re.compile(r"(?<!\d)(?:\+84[\s.-]?|0)\d{2,3}[\s.-]?\d{3}[\s.-]?\d{3,4}(?!\d|[.,]\d)")),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("name", re.compile(rf"\b(?:[Bb]ệnh\s+nhân|BN|[Pp]atient|Mr\.?|Mrs\.?|Ms\.?|[Ôô]ng|[Bb]à|[Cc]hị|[Aa]nh|[Cc]háu|[Bb]é)\s+"
                        rf"({NAME}(?:\s+{NAME}){{1,3}})")),
    ("initials", re.compile(rf"\b[{UP}]\.\s?[{UP}]\.(?:\s?[{UP}]\.)?")),
    ("address", re.compile(r"\b(?:số\s+nhà|đường|phường|quận|huyện|xã|thôn|ấp|street|road|ward|district)\s+[\w\d]+", re.I)),
]


def scan(text: str) -> list[tuple[str, str]]:
    hits = []
    for kind, rx in PATTERNS:
        for m in rx.finditer(text):
            hits.append((kind, m.group(0)))
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--include-notes", action="store_true")
    ap.add_argument("--fail-on-hit", action="store_true")
    a = ap.parse_args(argv)
    path = Path(a.deck)
    slides = load_slides(path)
    total = 0
    print(f"# phi_scan: {path.name}")
    for s in slides:
        text = s["text"] + (" " + s["notes"] if a.include_notes else "")
        for kind, val in scan(text):
            total += 1
            print(f"- slide {s['index']} [{kind}] {val}")
    if path.suffix.lower() in (".html", ".htm"):
        src = path.read_text(encoding="utf-8", errors="replace")
        imgs = len(re.findall(r"<img\b", src, re.I)) + len(re.findall(r"url\(data:image/(?:png|jpe?g)", src, re.I))
        if imgs:
            print(f"- {imgs} raster image(s): check each for faces, names, dates, record numbers burned into the pixels")
    print(f"{total} text hit(s). Review each; dates in a paper's methods are usually fine, dates of care are not.")
    return 1 if (a.fail_on_hit and total) else 0


if __name__ == "__main__":
    sys.exit(main())
