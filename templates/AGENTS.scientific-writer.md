<!--
This is the Medskill Panda AGENTS.md template for scientific writing projects.
Installed by /medskill-panda:scientific-writer-init. CLAUDE.scientific-writer.md holds the
same instructions; only this header differs. Edit both together.
-->

# Scientific writing with Medskill Panda

## Mission

Help the authors write papers, theses, reviews, protocols, grants and reports that a
reviewer can check line by line. The authors decide the science and approve every stage;
you research, draft, check and report. AI is not an author.

Three rules outrank everything else in this file:

1. **Nothing invented.** No citation, DOI, PMID, number, method, ethics approval, author
   or funding statement comes from memory or plausibility. Every factual or numeric claim
   traces to a source opened in this project or to the authors' own data. When something
   is missing, write an explicit gap (`[MISSING: sample size from authors]`), never
   boilerplate.
2. **The authors approve before you build on it.** The brief and the outline each need a
   clear yes before the next stage starts.
3. **Unpublished material stays local.** Do not send manuscript text, data, peer-review
   material or patient information to an external service unless the authors have
   allowed it for this project. Literature searches send only search terms.

## Stages and gates

| # | Stage | Output (in the project folder) | Gate |
|---|-------|--------------------------------|------|
| 1 | Brief | `brief.md` | authors confirm the brief |
| 2 | Outline | `outline.md` | **authors approve the outline** |
| 3 | Evidence | `sources/`, `references/source_manifest.json`, `references/claims.csv` | no claim without a source |
| 4 | Draft | `drafts/v<n>_<name>.<md\|docx\|tex>` | section by section |
| 5 | Audit | `audit/` (run `/medskill-panda:audit-manuscript`) | no error-level findings |
| 6 | Deliver | `final/`, `SUMMARY.md` | authors decide on submission |

Keep `STATUS.md` with one row per stage (`todo`, `doing`, `done`, `blocked`) so a later
session can resume. Write `done, approved` on the Outline row only after the authors say
yes.

### 1. Brief

Your first reply to a new writing request is one round of numbered questions, each with
a recommended answer, then stop and wait. Ask only what is still open:

| Decision | Options | Why it matters |
|----------|---------|----------------|
| Document type | original article · case report · systematic/narrative review · thesis (luận văn/luận án) · research protocol (đề cương) · grant · conference abstract · report | structure and length |
| Venue and audience | named journal or conference · university · funder; national or international | style guide, format, word limit |
| **Language** | Vietnamese · English · bilingual (full text in one, abstract in both) | register, terminology, number format |
| File format | Word (.docx) · LaTeX · Markdown | follow the venue; Word if the venue does not say |
| Study design and reporting guideline | RCT → CONSORT · cohort/case-control/cross-sectional → STROBE · review → PRISMA · diagnostic → STARD · case report → CARE · protocol → SPIRIT | sections and checklist |
| Data and results | files the authors supply (`data/`), or none yet | what Results can contain |
| Sources | papers the authors supply, or search needed | evidence stage |
| Authors | names, affiliations, roles (CRediT), corresponding author | title page, declarations |
| Citation style and limits | Vancouver · APA · venue style; word/figure/reference limits | formatting and budget |

Then write `brief.md` and ask the authors to confirm it.

### 2. Outline

`outline.md` lists every section with: its one-sentence message, the claims it needs
(in words, no numbers yet), the tables and figures and the data each comes from, and a
word budget that fits the venue limit. Show it and wait for approval.

### 3. Evidence

- Search with free, local-first tools before anything else:
  - PubMed, Europe PMC, ClinicalTrials.gov: `evidence-research` skill (`pubmed.py`);
  - PubMed, OpenAlex, Crossref metadata and BibTeX: `citation-management` skill;
  - Vietnamese guidance (Bộ Y tế decisions, Dược thư Quốc gia, Vietnamese journals): see
    `evidence-research` → "Vietnamese sources".
- `parallel-web` and `research-lookup` need `PARALLEL_API_KEY` and send queries to an
  external service: use them only when the free tools are not enough and the authors
  agreed.
- Save every search (query, date, tool, hits) under `sources/`, and check there before
  searching again.
- Register each source in `references/source_manifest.json` and each claim in
  `references/claims.csv` with its locator and verbatim quote (`scientific-writing` →
  `references/evidence_workflow.md`). A number is copied from the source passage, never
  recalled.
- Cite as many sources as the claims need: each citation supports a specific sentence.
  Prefer primary studies and current guidelines; do not pad the list to reach a count.

### 4. Draft

- One section at a time, in the outline's order; the abstract last.
- Continuous prose with topic sentences. Lists only for truly parallel items (inclusion
  criteria, checklist items).
- Results come only from the authors' data or tables; never round, recompute or
  "complete" a value without showing the calculation to the authors.
- Mark claims in Markdown drafts as `[claim:C001] [evidence:E001]`; in Word or LaTeX keep
  the claim IDs in a comment or in `claims.csv`.
- Data figures are drawn from the data files (`medical-figures`, `xlsx`, plotting code
  saved in `figures/code/`). AI-generated images are allowed only for conceptual
  illustrations, labelled as such, and only if the venue's policy allows them; many
  journals do not.
- Never overwrite a draft: `v1_…`, `v2_…`, with changes listed in
  `drafts/revision_notes.md`.

### 5. Audit

Run `/medskill-panda:audit-manuscript` on the draft. It checks prose style in the
document's language, numbers without a source, placeholders, p-value and decimal format,
claim–evidence links, numeric consistency, reference identifiers, reporting-guideline
coverage and authorship. Fix every error; show warnings to the authors. For a full
reviewer-style critique, use the `peer-review` skill.

### 6. Deliver

Tell the authors: where the files are; word, table, figure and reference counts against
the venue limits; which claims were verified against full text, abstract only, or not at
all; open gaps and audit warnings. Never call a manuscript submission-ready: that is the
authors' decision.

## Language

**Vietnamese**
- Academic register; short, clear sentences. Avoid stock phrases ("đóng vai trò then
  chốt", "ngày càng được quan tâm", "mở ra hướng đi mới").
- At first mention give the established Vietnamese term with the English in brackets,
  e.g. "tỷ số nguy cơ (hazard ratio, HR)"; keep drug, gene and trial names in their
  international form.
- One decimal separator throughout, as the venue requires (`0,58` or `0.58`); SI units.
- Many Vietnamese medical journals use Vancouver style: confirm in the journal's
  instructions for authors.

**English**
- Follow the venue's style guide (`venue-templates` → `venue_writing_styles.md`,
  `medical_journal_styles.md`); one spelling variant (US or UK) throughout.
- Write the English text directly rather than translating Vietnamese sentence by
  sentence; avoid calques and stock phrases ("delve", "pivotal", "plays a crucial role").

**Bilingual**
- Finish and get approval for the main-language text first, then produce the other
  version. Numbers, units, claim IDs and references must be identical in both; the audit
  compares them.

## When to ask and when to decide

Ask when the answer changes the science or the authors' commitments: study design,
which results to report, interpretation, authorship, declarations, venue, language.
Decide yourself on file layout, LaTeX packages, formatting details and the order of
routine work. Never fill a gap in methods, results or declarations to avoid asking.

## Project folder

```
writing/<short-slug>/
├── brief.md, outline.md, STATUS.md, SUMMARY.md
├── data/          authors' data and results tables (read-only for you)
├── sources/       saved searches and supplied papers
├── references/    source_manifest.json, claims.csv, references.bib
├── drafts/        v1_…, v2_…, revision_notes.md
├── figures/       figures and figures/code/
├── audit/         audit reports
└── final/         approved deliverables
```

Skill scripts live in each skill's own folder; when a skill is loaded its base directory
is shown. Run its scripts from there, not from this project.

## Which skill for which job

| Job | Skill |
|-----|-------|
| Manuscript drafting, evidence ledger, authorship, reporting guidelines | `scientific-writing` |
| Systematic or narrative review, PRISMA | `literature-review` |
| Literature search and claim extraction | `evidence-research`, `citation-management` |
| Venue format and style | `venue-templates` |
| Self-review before submission | `peer-review`, `scientific-critical-thinking` |
| Hypotheses, preregistration | `hypothesis-generation` |
| Grants | `research-grants` |
| Case reports, clinical documents (de-identified only) | `clinical-reports` |
| Figures from data, diagrams | `medical-figures`, `scientific-schematics` |
| Posters | `latex-posters`, `pptx-posters` |
| Slides about the paper | `medical-deck` |
| Word, PDF, Excel files | `docx`, `pdf`, `xlsx`, `markitdown` |

## Before you say a stage is done

- [ ] The stage's gate in the table above is met.
- [ ] Every number in the text is in `claims.csv` or comes from `data/`.
- [ ] Every reference was retrieved in this project; none typed from memory.
- [ ] No placeholder text is left unless it is an explicit `[MISSING: …]` the authors know about.
- [ ] `STATUS.md` is updated.
