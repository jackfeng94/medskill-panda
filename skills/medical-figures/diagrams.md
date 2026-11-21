# Rebuilt diagrams and charts

Rebuild a diagram when the source describes it in text or tables (the trial design, the
CONSORT numbers, the timeline of a case) or when the original is unreadable on a slide.
Every number and label comes from `claims.json`.

## Shared style

- Boxes: theme colours; 2 px border; 12–16 px radius; text ≥ 20 px at 1920 × 1080.
- Connectors: one colour, 3 px, with separate small arrowheads (not SVG markers) so they
  can appear after the line draws.
- Arm colours: intervention and control colours from the theme, the same on every slide.
- Lay out on a grid that you write down in a comment (x positions of columns, y of rows),
  so later edits don't drift.

## Trial schema

```
[Population: key eligibility, 4–6 bullets] → [Stratification factors] → (R ratio)
   → [Arm A: drug, dose, route, schedule, n]
   → [Arm B: comparator, schedule, n]           → [Endpoints: primary; key secondary; safety]
```

Add a dosing timeline underneath when schedules differ between arms (weeks on the
x-axis, a marker per dose, a shaded window for any delay such as manufacturing time).

## CONSORT (RCT) and PRISMA 2020 (systematic review)

Follow the official box order: enrolment (assessed, excluded with reasons), allocation,
follow-up, analysis. Numbers only from the paper or its supplement; a missing number reads
"not reported", never an estimate. Put the analysed populations (ITT, safety) in the last
row. CONSORT 2025 and PRISMA 2020 templates are on the statements' websites.

## Timelines (clinical cases)

Relative days (D0 = admission) instead of dates. One row per stream (symptoms,
investigations, treatment) only if there are more than ~8 events; otherwise a single
line. Key lab values as small labels at their day.

## Algorithms

Copy the guideline's own decision points and wording. Diamonds for decisions, rounded
boxes for actions. Cite the figure or section number of the guideline.

## Charts

| Data | Chart |
|------|-------|
| a rate in two arms, several outcomes | dumbbell plot (one row per outcome, two dots) |
| effect sizes with CI across subgroups | forest plot, log scale for ratios, line at 1 |
| a few proportions | horizontal bars with direct labels |
| change over time | line chart, one axis |

One axis per chart; label series directly; no 3-D, no dual axes. In HTML, hover tooltips
can show the counts behind a percentage. In PPTX, prefer native charts so the user can
edit them.
