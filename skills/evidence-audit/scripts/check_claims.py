#!/usr/bin/env python3
"""Cross-check the numbers on a deck against evidence/claims.json.

Reports:
  * UNSUPPORTED   a number shown on a slide that no claim for that slide contains
  * ELSEWHERE     the number exists in a claim, but the claim is mapped to another slide
  * QUOTE         a claim value that does not appear in the claim's own verbatim quote
  * SOURCE        a claim whose source id is not in references.json
  * UNVERIFIED    claims whose status is 'unverified'

Usage:
  python check_claims.py deck.html claims.json [--refs references.json] [--include-notes]

Exit code 1 when there is any UNSUPPORTED, QUOTE or SOURCE finding.
Numbers are matched after normalising decimal commas (0,58 = 0.58) and thousands
separators (1.137 = 1,137 = 1137). Years, page counters ("3 / 8") and integers 0-10
without a % sign are ignored. Text inside inline <svg> figures is skipped unless
--include-figures: figures are traced through figures/manifest.json instead.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deck_text import load_slides  # noqa: E402

NUM = re.compile(r"(?<![\w.,])[-−–]?\d+(?:[.,]\d+)*(?:\s?%)?")
STRIP = [
    re.compile(r"\b10\.\d{4,9}/\S+", re.I),                    # DOI
    re.compile(r"https?://\S+"),
    re.compile(r"\b(?:PMID|PMCID|NCT)\s*:?\s*\w+", re.I),
    re.compile(r"\b(?:19|20)\d{2}\s*;\s*\d+(?:\s*\(\s*\d+\s*\))?(?::\s*[\w-]+)?"),  # 2024;403(10427):632-644
    re.compile(r"\b\d+\s*/\s*\d+\s*$"),                        # page counter at end
    re.compile(r"(?:\b(?:KTC|CI)\s*)?\b(?:90|95|99)\s?%\s*(?:CI|KTC|confidence)?", re.I),  # CI level label
    re.compile(r"\bCC[\s-]?(?:BY|0)(?:[\s-](?:SA|NC|ND))*(?:[\s-]?\d\.\d)?", re.I),  # licence names: CC BY 4.0
]


def canon(token: str) -> float | None:
    """Turn '82,2%', '1.137', '1,137', '0.58', '−0,45' into a float."""
    t = token.replace("−", "-").replace("–", "-").replace("%", "").strip()
    neg = t.startswith("-")
    t = t.lstrip("-")
    if not t:
        return None
    seps = re.findall(r"[.,]", t)
    if len(seps) > 1:  # 1.234.567 or 1,234,567 (or 1.234,5)
        last = t[-4] if len(t) > 4 and t[-4] in ".," else None
        if last and len(set(seps)) == 1:
            t = t.replace(seps[0], "")
        else:
            dec = seps[-1]
            t = t.replace("." if dec == "," else ",", "").replace(dec, ".")
    elif len(seps) == 1:
        head, tail = re.split(r"[.,]", t)
        if len(tail) == 3 and head not in ("0", "") and len(head) <= 3:
            t = head + tail  # thousands separator
        else:
            t = head + "." + tail
    try:
        v = float(t)
    except ValueError:
        return None
    return -v if neg else v


def numbers(text: str, keep_small: bool = False) -> list[tuple[str, float]]:
    for rx in STRIP:
        text = rx.sub(" ", text)
    out = []
    for m in NUM.finditer(text):
        tok = m.group(0).strip()
        v = canon(tok)
        if v is None:
            continue
        is_pct = tok.endswith("%")
        is_int = re.fullmatch(r"[-−–]?\d+", tok) is not None
        if is_int and 1900 <= abs(v) <= 2100:
            continue  # year
        if is_int and abs(v) <= 10 and not is_pct and not keep_small:
            continue  # list numbering, counts like "3 doses" are usually claims too, but noisy
        out.append((tok, v))
    return out


def close(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("claims")
    ap.add_argument("--refs")
    ap.add_argument("--include-notes", action="store_true", help="also check numbers in speaker notes")
    ap.add_argument("--include-figures", action="store_true",
                    help="also check numbers inside inline <svg> figures (axis ticks will need claims too)")
    a = ap.parse_args(argv)

    slides = load_slides(a.deck)
    claims = json.loads(Path(a.claims).read_text(encoding="utf-8")).get("claims", [])
    refs = None
    if a.refs:
        refs = {r["id"] for r in json.loads(Path(a.refs).read_text(encoding="utf-8")).get("references", [])}

    by_slide: dict[int | None, list[float]] = {}
    for c in claims:
        vals = []
        for v in c.get("values", []):
            vals += [n for _, n in numbers(str(v), keep_small=True)]
        by_slide.setdefault(c.get("slide"), []).extend(vals)
    unmapped = by_slide.get(None, [])

    findings: list[tuple[str, str]] = []
    for s in slides:
        text = (s["text"] if a.include_figures else s.get("text_nosvg", s["text"])) +             (" " + s["notes"] if a.include_notes else "")
        own = by_slide.get(s["index"], []) + unmapped
        for tok, v in numbers(text):
            if any(close(v, x) for x in own):
                continue
            other = [k for k, xs in by_slide.items() if k not in (s["index"], None) and any(close(v, x) for x in xs)]
            if other:
                findings.append(("ELSEWHERE", f"slide {s['index']}: '{tok}' is in a claim for slide(s) {other}"))
            else:
                findings.append(("UNSUPPORTED", f"slide {s['index']}: '{tok}' has no claim"))

    for c in claims:
        cid = c.get("id", "?")
        if c.get("kind") != "derived" and c.get("quote"):
            qnums = [n for _, n in numbers(c["quote"], keep_small=True)]
            for v in c.get("values", []):
                for tok, n in numbers(str(v), keep_small=True):
                    if not any(close(n, q) for q in qnums):
                        findings.append(("QUOTE", f"claim {cid}: value '{tok}' is not in its quote"))
        if c.get("kind") == "derived" and not c.get("derivation"):
            findings.append(("QUOTE", f"claim {cid}: derived value without 'derivation'"))
        if refs is not None and c.get("source") not in refs:
            findings.append(("SOURCE", f"claim {cid}: source '{c.get('source')}' not in references"))
        if c.get("status") == "unverified":
            findings.append(("UNVERIFIED", f"claim {cid}: {c.get('text', '')}"))

    order = ["UNSUPPORTED", "QUOTE", "SOURCE", "ELSEWHERE", "UNVERIFIED"]
    findings.sort(key=lambda f: order.index(f[0]))
    print(f"# check_claims: {Path(a.deck).name}, {len(slides)} slides, {len(claims)} claims")
    if not findings:
        print("No findings.")
    for kind, msg in findings:
        print(f"- [{kind}] {msg}")
    blocking = any(k in ("UNSUPPORTED", "QUOTE", "SOURCE") for k, _ in findings)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
