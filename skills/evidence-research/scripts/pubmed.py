#!/usr/bin/env python3
"""Literature lookups for medical presentations, using only the Python standard library.

Sources: NCBI E-utilities (PubMed), Europe PMC (fallback and open-access full text),
ClinicalTrials.gov API v2. No API key is needed. Identifiers printed by this tool come from
a live lookup, which is the point: never type a PMID or DOI from memory.

Examples
  python pubmed.py search "intismeran pembrolizumab melanoma" --max 5
  python pubmed.py fetch 38246194            # metadata + abstract
  python pubmed.py refs 38246194 > refs.json  # reference records (references.json shape)
  python pubmed.py doi 10.1016/S0140-6736(23)02268-7
  python pubmed.py fulltext PMC1234567        # open-access full text (Europe PMC), plain text
  python pubmed.py trial NCT05933577
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
CTGOV = "https://clinicaltrials.gov/api/v2/studies/"
TOOL = "medskill-panda"
UA = "medskill-panda/1.0"
_last_ncbi = 0.0


def http_get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def ncbi(endpoint: str, **params) -> bytes:
    """Call an E-utility, staying under NCBI's 3 requests/second limit."""
    global _last_ncbi
    wait = 0.34 - (time.time() - _last_ncbi)
    if wait > 0:
        time.sleep(wait)
    params.setdefault("tool", TOOL)
    url = EUTILS + endpoint + "?" + urllib.parse.urlencode(params)
    try:
        return http_get(url)
    finally:
        _last_ncbi = time.time()


# ---------------------------------------------------------------- PubMed

def search(query: str, retmax: int = 10) -> list[str]:
    data = json.loads(ncbi("esearch.fcgi", db="pubmed", term=query, retmax=retmax, retmode="json"))
    return data.get("esearchresult", {}).get("idlist", [])


def summaries(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    data = json.loads(ncbi("esummary.fcgi", db="pubmed", id=",".join(pmids), retmode="json"))
    res = data.get("result", {})
    return [summary_to_record(res[p]) for p in res.get("uids", []) if p in res]


def summary_to_record(s: dict) -> dict:
    ids = {a.get("idtype"): a.get("value") for a in s.get("articleids", [])}
    year = re.match(r"\d{4}", s.get("pubdate", "") or s.get("epubdate", ""))
    return {
        "id": make_id(s.get("sortfirstauthor") or "", year.group(0) if year else ""),
        "title": (s.get("title") or "").rstrip("."),
        "authors": [a.get("name") for a in s.get("authors", []) if a.get("authtype") == "Author"],
        "journal": s.get("source", ""),
        "year": int(year.group(0)) if year else None,
        "volume": s.get("volume", ""),
        "issue": s.get("issue", ""),
        "pages": s.get("pages", ""),
        "doi": ids.get("doi", ""),
        "pmid": s.get("uid", ""),
        "pmcid": ids.get("pmc", ""),
        "pubtypes": s.get("pubtype", []),
        "retrieved_with": "pubmed.py esummary",
        "access": "metadata",
    }


def abstracts(pmids: list[str]) -> dict[str, str]:
    if not pmids:
        return {}
    root = ET.fromstring(ncbi("efetch.fcgi", db="pubmed", id=",".join(pmids), retmode="xml"))
    out = {}
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        parts = []
        for t in art.iter("AbstractText"):
            label = t.get("Label")
            text = "".join(t.itertext()).strip()
            parts.append(f"{label}: {text}" if label else text)
        out[pmid] = "\n".join(parts)
    return out


def make_id(first_author: str, year: str) -> str:
    surname = re.sub(r"[^a-z]", "", (first_author.split(" ")[0] if first_author else "ref").lower())
    return f"{surname or 'ref'}{year}"


# ---------------------------------------------------------------- Europe PMC

def epmc_search(query: str, retmax: int = 10) -> list[dict]:
    url = EPMC + "search?" + urllib.parse.urlencode(
        {"query": query, "format": "json", "pageSize": retmax, "resultType": "core"})
    data = json.loads(http_get(url))
    out = []
    for r in data.get("resultList", {}).get("result", []):
        out.append({
            "id": make_id(r.get("authorString", "").split(",")[0], str(r.get("pubYear", ""))),
            "title": (r.get("title") or "").rstrip("."),
            "authors": [a.get("fullName") for a in r.get("authorList", {}).get("author", [])],
            "journal": r.get("journalInfo", {}).get("journal", {}).get("medlineAbbreviation", ""),
            "year": int(r["pubYear"]) if str(r.get("pubYear", "")).isdigit() else None,
            "doi": r.get("doi", ""),
            "pmid": r.get("pmid", ""),
            "pmcid": r.get("pmcid", ""),
            "abstract": r.get("abstractText", ""),
            "retrieved_with": "pubmed.py europepmc",
            "access": "metadata",
        })
    return out


def epmc_fulltext(pmcid: str) -> str:
    xml = http_get(EPMC + f"{pmcid}/fullTextXML")
    root = ET.fromstring(xml)
    chunks = []
    for el in root.iter():
        if el.tag in ("title", "p", "caption", "td", "th", "label"):
            text = " ".join("".join(el.itertext()).split())
            if text:
                chunks.append(("\n## " if el.tag == "title" else "") + text)
    return "\n".join(chunks)


# ---------------------------------------------------------------- DOI, trials

def crossref(doi: str) -> dict:
    data = json.loads(http_get("https://api.crossref.org/works/" + urllib.parse.quote(doi)))["message"]
    year = (data.get("issued", {}).get("date-parts") or [[None]])[0][0]
    authors = [f"{a.get('family', '')} {''.join(x[0] for x in a.get('given', '').split() if x)}".strip()
               for a in data.get("author", [])]
    return {
        "id": make_id(authors[0] if authors else "", str(year or "")),
        "title": (data.get("title") or [""])[0],
        "authors": authors,
        "journal": (data.get("short-container-title") or data.get("container-title") or [""])[0],
        "year": year,
        "volume": data.get("volume", ""),
        "pages": data.get("page", ""),
        "doi": data.get("DOI", doi),
        "retrieved_with": "pubmed.py crossref",
        "access": "metadata",
    }


def trial(nct: str) -> dict:
    d = json.loads(http_get(CTGOV + nct))
    p = d.get("protocolSection", {})
    ident, design = p.get("identificationModule", {}), p.get("designModule", {})
    outcomes = p.get("outcomesModule", {})
    return {
        "nct": ident.get("nctId"),
        "title": ident.get("officialTitle") or ident.get("briefTitle"),
        "status": p.get("statusModule", {}).get("overallStatus"),
        "phase": design.get("phases"),
        "enrollment": design.get("enrollmentInfo", {}),
        "allocation": design.get("designInfo", {}).get("allocation"),
        "masking": design.get("designInfo", {}).get("maskingInfo", {}),
        "arms": [{"label": a.get("label"), "type": a.get("type"), "description": a.get("description")}
                 for a in p.get("armsInterventionsModule", {}).get("armGroups", [])],
        "primary_outcomes": outcomes.get("primaryOutcomes", []),
        "secondary_outcomes": outcomes.get("secondaryOutcomes", []),
        "retrieved_with": "pubmed.py trial (ClinicalTrials.gov API v2)",
    }


# ---------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="search PubMed (falls back to Europe PMC)")
    s.add_argument("query")
    s.add_argument("--max", type=int, default=10)
    f = sub.add_parser("fetch", help="metadata + abstract for PMIDs")
    f.add_argument("pmids", nargs="+")
    r = sub.add_parser("refs", help="reference records for PMIDs, as {'references': [...]}")
    r.add_argument("pmids", nargs="+")
    d = sub.add_parser("doi", help="look up a DOI on Crossref")
    d.add_argument("doi")
    t = sub.add_parser("fulltext", help="open-access full text from Europe PMC (PMCID)")
    t.add_argument("pmcid")
    c = sub.add_parser("trial", help="registered design from ClinicalTrials.gov")
    c.add_argument("nct")
    a = ap.parse_args(argv)

    if a.cmd == "search":
        try:
            recs = summaries(search(a.query, a.max))
        except Exception as e:  # NCBI blocked or down: fall back
            print(f"# PubMed unavailable ({e}); using Europe PMC", file=sys.stderr)
            recs = epmc_search(a.query, a.max)
        for x in recs:
            print(f"{x.get('pmid', '')}\t{x.get('year', '')}\t{x.get('journal', '')}\t{x['title']}")
    elif a.cmd == "fetch":
        recs = summaries(a.pmids)
        abs_ = abstracts(a.pmids)
        for x in recs:
            x["abstract"] = abs_.get(x["pmid"], "")
            x["access"] = "abstract" if x["abstract"] else "metadata"
        print(json.dumps(recs, ensure_ascii=False, indent=2))
    elif a.cmd == "refs":
        print(json.dumps({"references": summaries(a.pmids)}, ensure_ascii=False, indent=2))
    elif a.cmd == "doi":
        print(json.dumps(crossref(a.doi), ensure_ascii=False, indent=2))
    elif a.cmd == "fulltext":
        print(epmc_fulltext(a.pmcid))
    elif a.cmd == "trial":
        print(json.dumps(trial(a.nct), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
