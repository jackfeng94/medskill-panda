# Medical visual grammar

Pick the visual from the kind of evidence the slide carries.

| Evidence on the slide | First choice | Notes |
|---|---|---|
| Trial design | Trial schema: population → R (ratio, stratification) → arms (drug, dose, schedule) → endpoints | Rebuild as SVG; never a bullet list |
| Patient flow in an RCT | CONSORT flow diagram | Numbers only from the paper or supplement; leave blank boxes visibly blank |
| Systematic review flow | PRISMA 2020 diagram | Same rule |
| Time-to-event result | Kaplan–Meier curve | Reuse the original vector figure when the source PDF has one; numbers at risk stay |
| Effect across subgroups or studies | Forest plot | Reuse or rebuild from the table; one axis, log scale for ratios |
| Diagnostic accuracy | 2×2 table, ROC curve | |
| Two or three headline numbers | Large numbers with labels, in the slide's own layout | Not a grid of identical "KPI cards" |
| Comparison of rates between arms | Dot or dumbbell plot, paired bars | One axis, label both arms directly |
| Dosing schedule | Timeline with dose markers by week | |
| Clinical course of a case | Horizontal timeline with dated events and key labs | Relative days (D0, D3) for privacy |
| Mechanism, pathophysiology, pharmacology | Labelled pathway diagram; animation when HTML is the format | Every arrow means something stated in a source |
| Diagnostic or treatment pathway | Algorithm / decision tree | From a guideline: cite the figure or section |
| Recommendations | Table: recommendation · class · level · source | Keep the guideline's own wording |
| Imaging, histology | The image itself with arrows and a scale bar | Consent and de-identification first |
| Definitions, criteria | Compact table or two-column list | |
| Discussion questions, take-home | Short numbered statements | Max 3 |

Rules that apply to every visual:

- One idea per visual; one axis per chart; units on axes.
- Label lines and series directly where possible; a legend only when there are more than
  three series.
- Colours follow the entity (intervention vs control) and stay the same on every slide.
- Fonts on visuals no smaller than body text minus 4 pt (PPTX) or 18 px at 1920 × 1080 (HTML).
