---
description: Audit a manuscript (Word, LaTeX or Markdown; Vietnamese or English) for machine-made style, unsourced numbers, placeholders, claim–evidence links, numeric consistency, references, reporting-guideline coverage and authorship.
---

# Audit a manuscript

When the user runs `/medskill-panda:audit-manuscript [file] [--compare other-language-file]`:

1. **Find the inputs.** The manuscript is the file given, otherwise the newest file in
   `drafts/` of the writing project (`writing/<slug>/`). Ask only if there is none. Look,
   without asking, for these optional files in the project's `references/` folder (or
   next to the manuscript): `claims.csv`, `source_manifest.json`,
   `manuscript_manifest.json`, `consistency_manifest.json`, `reporting_coverage.json`,
   `authorship.json`. If the brief says the work is bilingual and the other language
   version exists, use it for `--compare`.
2. **Load the `scientific-writing` skill** and run its scripts from that skill's base
   directory. Run every check whose inputs exist; record the others as skipped with the
   reason. Keep everything local: none of these checks uses the network.

   | Check | Command | Needs |
   |-------|---------|-------|
   | Style, unsourced numbers, placeholders, p-values, decimals | `python3 scripts/lint_prose.py <manuscript> [--compare <other>]` | any .md/.tex/.docx/.txt |
   | Declarations, confidentiality gate | `python3 scripts/lint_manuscript.py <manuscript.md> [--manifest manuscript_manifest.json]` | Markdown manuscript |
   | Claim ↔ evidence | `python3 scripts/audit_claims.py <manuscript.md> claims.csv source_manifest.json` | Markdown + both files |
   | Numbers across sections | `python3 scripts/check_consistency.py consistency_manifest.json` | the manifest |
   | Reference identifiers, duplicates | `python3 scripts/check_references.py source_manifest.json` | the manifest |
   | Reporting guideline coverage | `python3 scripts/select_reporting_guidelines.py check reporting_coverage.json` | the coverage file |
   | Authorship, CRediT, AI disclosure | `python3 scripts/validate_authorship.py authorship.json` | the file |

   `lint_prose.py` runs on Python 3.8+; the other scripts need Python 3.11+. If only a
   Word or LaTeX file exists, the Markdown-only checks are skipped; say so and suggest
   keeping a Markdown working copy, or converting with the `markitdown` skill.
3. **Write the report** to `audit/manuscript-audit-<YYYYMMDD>.md` in the project (create
   `audit/` if needed):
   - a table with one row per check: ran or skipped (why), errors, warnings;
   - every error, then every warning, grouped by section, each with its location
     (line or paragraph) and the rule code;
   - for P02/P03 (style, overstatement), a suggested rewrite in the manuscript's own
     language, kept to the sentence's meaning;
   - for P04 (statistic without a citation), which claim in `claims.csv` it might map to,
     or "no source found".
4. **Reply to the user** with the summary table and the five most important findings.
   Do not change the manuscript: offer to apply the fixes, and apply only what the user
   accepts, as a new draft version (`v<n+1>_…`), never overwriting the audited file.
   Never call the manuscript submission-ready.
