# Slop catalog

⚙ = the linter flags it. The others need eyes on the rendered slide.

## Text that serves the tool, not the audience (blocking)

| ID | Pattern | Examples | Fix |
|----|---------|----------|-----|
| S01 ⚙ | **Eyebrow / kicker**: a small, often uppercase, letter-spaced label above the title, frequently numbered | `03 · RESULTS · ITT`, `KEY INSIGHT`, `01 Bối cảnh & cơ chế` | Delete. A section label is justified only when the template prints one on every slide. |
| S02 ⚙ | **Presenter instructions on the slide** | `▸ Click for next: 24-month landmark`, `Bấm tiếp: …`, `Hover to see grades`, `(animation)`, `Press N for notes` | Delete; put the cue in speaker notes. |
| S03 ⚙ | **Process or provenance narration** | `Original NEJM Figure 1, recoloured`, `Hình 1 nguyên bản, đổi màu`, `Generated with…`, `Adapted by AI`, `Redrawn for clarity` | Delete. Keep a plain source credit (`Source: Long GV et al. N Engl J Med 2026; Fig. 1A`). |
| S04 ⚙ | **Leftover placeholders** | `Lorem ipsum`, `TODO`, `[insert figure]`, `XX%`, `{{title}}` | Replace or delete. |
| S05 | **Invented visuals**: a chart, diagram or image whose data or structure has no source | A KM curve drawn from memory; a CONSORT box with a made-up number | Remove or rebuild from claims. Also an evidence finding (E-FIG). |
| S06 | **Overflow or clipping** | Text running past a box, a figure cut off by the footer | Re-layout; split the slide; never shrink below the size floor. |

## Template-y design moves (advisory)

| ID | Pattern | Fix |
|----|---------|-----|
| S07 ⚙ | **KPI-card grids**: every number in an identical rounded card | Show the one number that matters large, or use a chart that compares the numbers. |
| S08 ⚙ | **Chips and pills** used as decoration (`Phase 3`, `n = 1,137`, `6 continents`) | Fold into a sentence or the title slide's subtitle. |
| S09 | **Decorative icons**: an icon per bullet that adds no meaning | Delete, or use a real diagram. |
| S10 ⚙ | **Gradient text, glow, glassmorphism, heavy shadows** outside the template | Flat colour from the theme. |
| S11 | **Accent bar** under every title, or a coloured stripe down one side of each card | Delete; use space. |
| S12 | **Same layout on every slide** (title + three cards, repeated) | Choose the layout from the evidence type (visual-grammar). |
| S13 ⚙ | **Section counters** in big numerals (`01`, `02`, `03`) next to every heading | Delete; titles carry the order. |

## Language tics (advisory; blocking if in a title)

| ID | Pattern | Examples | Fix |
|----|---------|----------|-----|
| S14 ⚙ | **Em-dash cascades** and the "not X — it's Y" construction | `Not just a vaccine — a personalised therapy` | One clause per line, or a full sentence. |
| S15 ⚙ | **Stock phrases** | `Key takeaways`, `Let's dive in`, `game-changer`, `unlock`, `revolutionize`, `paradigm shift`, `in today's fast-paced world`, `Điểm nhấn`, `bước ngoặt`, `cuộc cách mạng` | Say the specific thing. |
| S16 ⚙ | **Emoji and decorative symbols** in clinical slides | `🚀`, `✨`, `✅` used as bullets | Delete. |
| S17 | **Topic titles** where an assertion belongs | `Results`, `Kết quả hiệu quả` | Write the conclusion as the title. |
| S18 ⚙ | **Wall of text**: more than ~40 words of body text on a content slide (title, footer and figure labels excluded) | | Split the slide or move detail to notes. |
| S19 ⚙ | **Tiny type**: body text under 18 px at 1920 × 1080 (HTML) or under 14 pt (PPTX); footers under 12 px or 10 pt | | Cut words; do not shrink. |
| S20 | **Explaining the obvious** | `This chart shows…`, `As we can see…`, `Như hình trên cho thấy` | Delete; the title says what the chart shows. |
| S21 | **Hedge-free hype** in medical claims | `dramatically improves survival` for HR 0.77, P = 0.33 | Use the evidence's own strength. Also an evidence finding (E-CLAIM). |

## Not slop

- Elements of the user's template: header bars, logos, footers, page numbers.
- A short source credit under a reused figure, including the disclosure that an illustration
  was AI-generated and who checked it ("Illustration: generated with ChatGPT, anatomy checked
  against Servier Medical Art"). Put it in a credit or footer element (`.credit`, `data-cite`).
- Speaker notes, however long.
- Repeated layouts in a deliberate series (one slide per guideline change).
