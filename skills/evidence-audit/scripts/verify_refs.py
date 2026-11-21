#!/usr/bin/env python3
"""Verify that every reference in references.json is real and is the paper it claims to be.

For each record with a PMID, look it up on PubMed (E-utilities esummary); with a DOI, on
Crossref. Compare title (fuzzy), year and first-author surname, and check that the PMID's
DOI equals the record's DOI.

Statuses: VERIFIED · MISMATCH (exists, but metadata differs) · NOT_FOUND ·
NO_IDENTIFIER (cannot be checked) · ERROR (network). Exit 1 unless all are VERIFIED.

Usage: python verify_refs.py references.json [--json]
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = "medskill-panda/1.0"


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fetch_pubmed(pmid: str) -> dict | None:
    time.sleep(0.34)
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": pmid, "retmode": "json", "tool": "medskill-panda"})
    res = json.loads(_get(url)).get("result", {})
    s = res.get(str(pmid))
    if not s or "error" in s:
        return None
    ids = {a.get("idtype"): a.get("value") for a in s.get("articleids", [])}
    year = re.match(r"\d{4}", s.get("pubdate", "") or "")
    return {"title": s.get("title", ""), "year": int(year.group(0)) if year else None,
            "first_author": s.get("sortfirstauthor", ""), "doi": ids.get("doi", ""),
            "journal": s.get("source", "")}


def fetch_crossref(doi: str) -> dict | None:
    try:
        m = json.loads(_get("https://api.crossref.org/works/" + urllib.parse.quote(doi)))["message"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    year = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
    authors = m.get("author", [])
    return {"title": (m.get("title") or [""])[0], "year": year,
            "first_author": authors[0].get("family", "") if authors else "", "doi": m.get("DOI", doi),
            "journal": (m.get("short-container-title") or m.get("container-title") or [""])[0]}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


def surname(author: str) -> str:
    a = norm(author)
    return a.split(" ")[0] if a else ""


def compare(rec: dict, found: dict) -> list[str]:
    problems = []
    if rec.get("title"):
        ratio = difflib.SequenceMatcher(None, norm(rec["title"]), norm(found["title"])).ratio()
        if ratio < 0.85:
            problems.append(f"title differs ({ratio:.2f}): found '{found['title'][:90]}'")
    if rec.get("year") and found.get("year") and int(rec["year"]) != int(found["year"]):
        problems.append(f"year {rec['year']} ≠ {found['year']}")
    first = (rec.get("authors") or [""])[0]
    if first and found.get("first_author") and surname(first) != surname(found["first_author"]):
        problems.append(f"first author '{first}' ≠ '{found['first_author']}'")
    return problems


def verify(rec: dict, pubmed=fetch_pubmed, crossref=fetch_crossref) -> tuple[str, list[str]]:
    pmid, doi = str(rec.get("pmid") or "").strip(), str(rec.get("doi") or "").strip()
    if not pmid and not doi:
        return "NO_IDENTIFIER", ["no PMID or DOI: cannot be checked automatically"]
    try:
        notes: list[str] = []
        if pmid:
            found = pubmed(pmid)
            if not found:
                return "NOT_FOUND", [f"PMID {pmid} not found on PubMed"]
            notes += compare(rec, found)
            if doi and found.get("doi") and found["doi"].lower() != doi.lower():
                notes.append(f"PMID {pmid} has DOI {found['doi']}, record says {doi}")
        elif doi:
            found = crossref(doi)
            if not found:
                return "NOT_FOUND", [f"DOI {doi} not found on Crossref"]
            notes += compare(rec, found)
        return ("MISMATCH" if notes else "VERIFIED"), notes
    except Exception as e:  # network or parse problem: never report as verified
        return "ERROR", [f"{type(e).__name__}: {e}"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("references")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    refs = json.loads(Path(a.references).read_text(encoding="utf-8")).get("references", [])
    results = []
    for r in refs:
        status, notes = verify(r)
        results.append({"id": r.get("id"), "status": status, "notes": notes})
    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"# verify_refs: {len(results)} references")
        for x in results:
            print(f"- {x['id']}: {x['status']}" + "".join(f"\n    · {n}" for n in x["notes"]))
    return 0 if all(x["status"] == "VERIFIED" for x in results) else 1


if __name__ == "__main__":
    sys.exit(main())
