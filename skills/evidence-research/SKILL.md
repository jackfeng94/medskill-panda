---
name: evidence-research
description: Use when a medical presentation needs facts, numbers, trial results, guideline recommendations or references, whether from papers the user supplied or from a literature search (PubMed, Europe PMC, ClinicalTrials.gov, OpenEvidence) or Vietnamese guidance (Bộ Y tế decisions, Dược thư Quốc gia), and before any number is written on a slide.
---

# Evidence research

## Overview

Every claim a slide makes becomes a record: what is claimed, which source says it, where in
the source, the exact words, and how well you could check it. A paper existing does not make
a number from it correct. Numbers are copied from the source passage, never recalled.

**Identifiers (PMID, DOI, NCT) come only from a lookup you ran in this session.** An
identifier you remember, even one marked "(verify)", does not go into any file.

## Sources, in order

1. Files the user supplied (`<talk>/sources/`). Read the full text: results, tables,
   figure legends, supplement if given.
2. The database tools the user allowed in the brief. If the user named one (for example
   "OpenEvidence only"), use only that one and record what it could not give you as a gap.
3. Otherwise:
   - **PubMed** through a PubMed MCP server if one is connected, else
     `python scripts/pubmed.py` (see `--help`; needs no API key).
   - **Europe PMC** for full text of open-access papers (`pubmed.py fulltext`).
   - **ClinicalTrials.gov** for the registered design and endpoints (`pubmed.py trial NCT…`).
   - Guidelines from the issuing society's own site.
   - **Vietnamese guidance** when the talk is for a Vietnamese audience or the brief asks
     for local practice (see below).

Record every search string and its date in `evidence/notes.md`.

## Vietnamese sources (Bộ Y tế and local literature)

For talks in Vietnam, local guidance often decides what the audience can actually do.
Look it up; do not recall it.

- **Hướng dẫn chẩn đoán và điều trị / quy trình chuyên môn của Bộ Y tế**: each is issued
  by a *Quyết định* (`<số>/QĐ-BYT`, with its date). Find the decision on the Cục Quản lý
  Khám, chữa bệnh site (kcb.vn) or the government legal-document portals
  (vanban.chinhphu.vn, thuvienphapluat.vn), and cite the decision number, date and the
  guideline title exactly as issued. Check that no later decision replaced it.
- **Dược thư Quốc gia Việt Nam** and the drug's approved Vietnamese label for doses,
  indications and reimbursement (BHYT) conditions, which can differ from FDA/EMA labels.
- **Vietnamese journals** (e.g. Tạp chí Y học Việt Nam) for local epidemiology and
  outcomes. Many are not in PubMed: record the journal's own URL and access date.

Store these like any other reference: `kind: "recommendation"` for guideline statements,
`retrieved_with` naming the site, and the quote in Vietnamese as printed. When a Bộ Y tế
guideline and an international guideline disagree, put both on the slide with their
sources rather than choosing silently, and flag it to the presenter.

## Extracting a claim

For each claim the plan lists:

- Copy the number exactly as printed, with its unit, CI and P value. Keep the
  denominator.
- Record the **locator** (page, table, figure panel, section) and a **verbatim quote** of
  20–60 words that contains the number.
- Classify it with `kind`:

| kind | Use for | Watch for |
|------|---------|-----------|
| `observed` | results actually measured | primary vs secondary endpoint; ITT vs per-protocol; interim vs final |
| `planned` | protocol assumptions, sample-size targets | never present as a result |
| `derived` | numbers you computed (1 − HR, absolute difference, NNT) | store the formula in `derivation` |
| `recommendation` | guideline statements | keep class and level, and the exact wording |
| `background` | epidemiology, mechanism | prefer reviews or guidelines from the last 5 years |

- Set `status`: `verified-fulltext`, `verified-abstract` (you saw only the abstract), or
  `unverified` (could not open any version). Unverified claims may stay in the plan but are
  flagged to the user.

## Files

`evidence/references.json`:

```json
{"references": [{"id": "long2026", "title": "…", "authors": ["Long GV", "…"],
  "journal": "N Engl J Med", "year": 2026, "volume": "", "pages": "",
  "doi": "10.1056/…", "pmid": "…", "nct": "",
  "retrieved_with": "pubmed.py esummary", "access": "full-text"}]}
```

`evidence/claims.json`:

```json
{"claims": [{"id": "c07", "slide": 7, "text": "RFS at 24 months, intervention vs control",
  "values": ["82.2%", "70.0%", "HR 0.58", "0.45–0.75"], "source": "long2026",
  "locator": "p. 6, Results; Fig. 1A", "quote": "…exact words…",
  "kind": "observed", "status": "verified-fulltext"}]}
```

`pubmed.py refs PMID…` prints reference records in this shape from a real lookup.

## Common mistakes

- Swapping endpoints: an HR from RFS written under DMFS. Each value's quote must name its
  endpoint.
- Reporting "improved" for a result whose CI crosses 1. Store the CI and P value so the
  audit can catch it.
- Taking a conference abstract's interim number when the paper reports a later one. Note
  the data cut-off date.
- Citing a review for a trial result. Cite the trial.
