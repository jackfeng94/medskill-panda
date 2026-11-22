---
description: Turn a manuscript written with Medskill Panda into a talk (or poster) that reuses the paper's evidence ledger, so every number on the slides matches the paper.
---

# From paper to deck

When the user runs `/medskill-panda:paper-to-deck [manuscript] [talk-name]`:

1. **Find the paper.** The manuscript is the file given, otherwise the newest Markdown draft in
   `drafts/` of the writing project. Its evidence files are `references/claims.csv` and
   `references/source_manifest.json`. If the newest draft is Word or LaTeX only, convert a copy
   to Markdown with the `markitdown` skill first, and say that the claim markers must have
   survived the conversion. If there is no claims.csv, stop and say the paper has no evidence
   ledger yet; offer the normal `medical-deck` route instead.
2. **Interview, briefly.** Load `medical-deck` and run its stage 1 (`deck-grilling`), but
   prefill every answer the paper already settles (topic, language, sources, data) and ask
   only what a talk adds: event, audience, duration, output format (HTML, PPTX, Beamer, or a
   poster), template, presenter. Wait for the answers. Create the talk folder as
   `medical-deck` describes, inside the writing project unless the user says otherwise.
3. **Import the evidence.** From the `medical-deck` skill's base directory:

   ```bash
   python3 scripts/manuscript_to_evidence.py <manuscript.md> <claims.csv> <source_manifest.json> --out <talk>/evidence
   ```

   Each claim keeps the paper's sentence as its quote, its numbers as values, its source and
   its verification status. Report how many claims are unverified. Copy figures the paper
   already has into `<talk>/figures/` and record them in `figures/manifest.json` as
   `"kind": "reused-from-manuscript"` with the manuscript's figure number.
4. **Plan and build with `medical-deck` from stage 3.** The plan gate still applies: nothing is
   built before the user approves `plan.md`. When the plan assigns claims to slides, write the
   slide numbers into `claims.json`. A slide may only show numbers that are values of these
   claims; anything new goes through `evidence-research` first. The save hook flags any number
   without a claim as the slide is written.
5. **Poster instead of slides.** If the user chose a poster, plan the panels the same way and
   build with `latex-posters` or `pptx-posters`, using only the imported claims and figures.
6. **Audit and deliver** as `medical-deck` stages 7–8. In the report, say which numbers came
   from the paper, which claims were still unverified in the paper, and anything that had to
   be added.
