---
name: beamer-deck-building
description: Use when building or editing a medical or scientific presentation as LaTeX Beamer (PDF), after the plan is approved and claims and figures exist; typical for thesis defences, research seminars and conference talks with equations, or when a Beamer deck overflows, fails to compile or needs a template applied.
---

# Beamer deck building

## Before you start

This skill is stage 6 of medskill-panda:medical-deck. Work only inside a talk folder whose
`STATUS.md` marks the Plan as `done, approved` and which has `evidence/claims.json`. If
either is missing, stop and call the Skill tool with medskill-panda:medical-deck instead: it
runs the interview, the plan and the evidence first. This holds for a new deck from a
one-line request too.

## Overview

Beamer gives a PDF that opens anywhere, typesets equations and cites with BibLaTeX. It has
no motion beyond `\pause`/overlays and is not editable by non-LaTeX users: when the brief
needs either, the format should have been HTML or PPTX (go back to deck-grilling).

Start from one of the templates in `assets/` and keep its preamble:

| Template | Use for |
|----------|---------|
| `beamer_template_conference.tex` | 10–20 min conference talk |
| `beamer_template_seminar.tex` | 45–60 min seminar, grand rounds, lecture |
| `beamer_template_defense.tex` | thesis or dissertation defence |

`references/beamer_guide.md` covers themes, overlays, columns, TikZ and BibLaTeX;
`references/common_pitfalls.md` lists the usual compile and layout traps.

## Procedure

1. Copy the template to `<talk>/build/deck.tex`. Replace every placeholder (`Your Name`,
   `Author Name`, institution, date) with the exact strings from `brief.md`. A placeholder
   left in the PDF is a blocking slop finding (S04).
2. **Theme.** If `theme/theme.json` exists, define its colours with `\definecolor` and set
   them with `\setbeamercolor`; use the template's logo file with `\logo{}`.
3. **Bibliography.** Write `<talk>/build/refs.bib` from `evidence/references.json` only
   (DOI and PMID exactly as stored). Never type a reference from memory.
4. **Slides.** One `frame` per row of `plan.md`, in order:
   - the plan's assertion as the frame title;
   - the visual from `figures/` with `\includegraphics` (PDF or PNG; convert SVG first);
   - only numbers from `claims.json`, written as in the source and formatted for the
     deck's language (`0,58` in Vietnamese with `\usepackage[vietnamese]{babel}`,
     `0.58` in English);
   - speaker notes with `\note{…}`. **Cues such as "[click]" never go on the slide.**
   - the slide's source with `\footcite{}` or a small `\source{}` line.
5. **Compile** (from `<talk>/build/`):

   ```bash
   latexmk -pdf -interaction=nonstopmode deck.tex
   ```

   Use `-xelatex` instead of `-pdf` for Vietnamese text with system fonts. Copy the PDF to
   `<talk>/out/<name>.pdf`.
6. **Check.**

   ```bash
   python scripts/validate_presentation.py <talk>/out/<name>.pdf --duration <minutes>
   ```

   ```bash
   python scripts/pdf_to_images.py <talk>/out/<name>.pdf <talk>/build/render/slide --dpi 110
   ```

   Fix every `Overfull \hbox`/`\vbox` warning in `deck.log` that moves text off a frame,
   then look at every rendered page yourself. Fix overflow by cutting words or splitting
   the frame, never with `\tiny` or `\scriptsize` for body text.
7. Hand `<talk>/out/<name>.pdf` to the audits: `lint_slop.py` and the evidence-audit
   scripts read PDF text page by page (needs `pip install pypdf`).

## Type floor (16:9, `aspectratio=169`)

| Element | Minimum |
|---------|---------|
| Body text | `\small` (11 pt at the default 11 pt class) |
| Figure labels, tables | `\footnotesize` |
| Source credit | `\scriptsize` |

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `\pause` on every bullet | Overlays only where the plan's notes ask for a reveal |
| Itemize of six bullets as the only content | Pick visuals per `deck-planning` → `visual-grammar.md` |
| `\cite{}` keys invented while writing | Keys come from `refs.bib`, built from `references.json` |
| Figures redrawn in TikZ from memory | Use `figures/`; a new diagram goes back to stage 5 |
