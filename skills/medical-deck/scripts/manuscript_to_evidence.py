#!/usr/bin/env python3
"""Turn a manuscript's evidence ledger into a talk's evidence files, so slides reuse the paper's numbers.

Reads a Markdown manuscript written with the scientific-writing skill (claims marked
`[claim:C001] [evidence:E001]`), its claims.csv and its source_manifest.json, and writes
<talk>/evidence/references.json and <talk>/evidence/claims.json in the format medical-deck,
evidence-audit and the save hook use.

For each claim marker in the text:
  values  = the numbers in that sentence (as printed)
  quote   = the sentence itself, markers removed
  source  = the first evidence id, kept as the reference id
  locator = "manuscript, <section>" plus the source's own locator
  status  = verified-fulltext when the manuscript marks the claim and its source verified, else unverified
  slide   = null (deck-planning assigns slides)

Nothing is invented: a claim with no number becomes a text claim with empty values; a claim id
in the text but missing from claims.csv is reported and skipped.

Usage:
  python manuscript_to_evidence.py drafts/v3_paper.md references/claims.csv \
      references/source_manifest.json --out ../talk/evidence [--json]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MARK = re.compile(r"\[claim:(C\d{3,8})\]\s*(?:\[evidence:([E\d,\s]+)\])?")
ANY_MARK = re.compile(r"\[(?:claim|evidence):[^\]]*\]|\[@E\d+[^\]]*\]")
NUMBER = re.compile(r"(?<![\w.,])[-−–]?\d+(?:[.,]\d+)*(?:\s?%)?")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ỸĐ0-9(\[])")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")
YEAR = re.compile(r"^(?:19|20)\d{2}$")


def sentences_with_sections(md: str):
    """Yield (section, sentence) for every sentence of the body text."""
    section = ""
    for block in re.split(r"\n\s*\n", md):
        lines = block.strip().splitlines()
        if not lines:
            continue
        m = HEADING.match(lines[0])
        if m:
            section = m.group(1).strip()
            lines = lines[1:]
        text = " ".join(l.strip() for l in lines)
        for s in SENTENCE_END.split(text):
            if s.strip():
                yield section, s.strip()


def values_in(sentence: str) -> list[str]:
    clean = ANY_MARK.sub(" ", sentence)
    return [v.strip() for v in NUMBER.findall(clean) if not YEAR.match(v.strip())]


def convert(manuscript: Path, claims_csv: Path, manifest: Path) -> tuple[dict, dict, list[str]]:
    rows = {r["claim_id"]: r for r in csv.DictReader(claims_csv.open(encoding="utf-8"))}
    sources = {s["evidence_id"]: s for s in json.loads(manifest.read_text(encoding="utf-8")).get("sources", [])}
    problems: list[str] = []
    claims, used = [], set()
    for section, sent in sentences_with_sections(manuscript.read_text(encoding="utf-8")):
        for m in MARK.finditer(sent):
            cid = m.group(1)
            row = rows.get(cid)
            if row is None:
                problems.append(f"{cid}: in the text but not in claims.csv; skipped")
                continue
            ev = [e.strip() for e in (m.group(2) or row.get("evidence_ids", "")).replace(";", ",").split(",") if e.strip()]
            src = sources.get(ev[0]) if ev else None
            if ev and src is None:
                problems.append(f"{cid}: evidence {ev[0]} not in source_manifest.json")
            verified = (row.get("verification_status") == "verified"
                        and (src or {}).get("verification", {}).get("status") == "verified")
            locator = f"manuscript, {section or 'untitled section'}"
            if src and src.get("locator") and "TODO" not in src["locator"]:
                locator += f"; source: {src['locator']}"
            claims.append({
                "id": cid.lower(), "slide": None, "text": ANY_MARK.sub("", sent).strip()[:160],
                "values": values_in(sent), "source": ev[0] if ev else "",
                "locator": locator, "quote": " ".join(ANY_MARK.sub(" ", sent).split()),
                "kind": "derived" if row.get("claim_kind") == "derived" else "observed",
                "status": "verified-fulltext" if verified else "unverified",
                "from_manuscript": manuscript.name,
            })
            used.update(ev)
    refs = []
    for eid in sorted(used):
        s = sources.get(eid)
        if not s:
            continue
        ids = s.get("identifiers", {})
        refs.append({"id": eid, "title": s.get("title", ""), "authors": s.get("authors", []), "year": s.get("year"),
                     "doi": ids.get("doi", ""), "pmid": ids.get("pmid", ""), "pmcid": ids.get("pmcid", ""),
                     "url": ids.get("url", ""), "source_type": s.get("source_type", ""),
                     "retrieved_with": "manuscript source_manifest.json",
                     "access": "verified" if s.get("verification", {}).get("status") == "verified" else "unverified"})
    if not claims:
        problems.append("no [claim:C…] markers found: is this a scientific-writing Markdown draft?")
    return {"references": refs}, {"claims": claims}, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manuscript")
    ap.add_argument("claims_csv")
    ap.add_argument("source_manifest")
    ap.add_argument("--out", required=True, help="the talk's evidence/ folder")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    refs, claims, problems = convert(Path(a.manuscript), Path(a.claims_csv), Path(a.source_manifest))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "references.json").write_text(json.dumps(refs, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "claims.json").write_text(json.dumps(claims, ensure_ascii=False, indent=2), encoding="utf-8")
    n = len(claims["claims"])
    unverified = sum(c["status"] == "unverified" for c in claims["claims"])
    if a.json:
        print(json.dumps({"claims": n, "references": len(refs["references"]), "unverified": unverified,
                          "problems": problems}, ensure_ascii=False, indent=2))
    else:
        print(f"# manuscript_to_evidence: {n} claim(s), {len(refs['references'])} reference(s), {unverified} unverified")
        for p in problems:
            print(f"- {p}")
    return 1 if not n else 0


if __name__ == "__main__":
    sys.exit(main())
