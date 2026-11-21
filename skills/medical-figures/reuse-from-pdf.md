# Reusing figures from a PDF

Most journal PDFs (NEJM, Lancet, JAMA, JCO) store charts as vector line art. Lift the
vectors and you keep every step of a Kaplan–Meier curve exactly as published.

## 1. Find the figure

```bash
python scripts/pdf_figures.py list paper.pdf
```

`vector` lines are clusters of line art with their bounding box in PDF points; `caption`
lines locate "Figure 1…". Clusters often merge neighbouring panels: render the page to
read exact coordinates.

```bash
python scripts/pdf_figures.py raster paper.pdf --page 6 --rect 0,0,567,756 -o page6.png --dpi 100
```

At 100 dpi, 1 pt = 1.39 px. Pick the panel's rectangle in points. Include the axis labels
and the numbers-at-risk table; leave out the figure legend text.

If `list` shows only an `image` where the figure is, the figure is raster. Use `raster`
at 300 dpi and record `reused-raster` in the manifest. Do not trace it.

## 2. Extract and recolour

```bash
python scripts/pdf_figures.py extract paper.pdf --page 6 --rect 32,58,297.2,267.6 \
  -o figures/s05-km-rfs.svg --prefix kma \
  --recolor '#006f99=#d7262e' --recolor '#939598=#5b6b82' --recolor '#231f20=#262626'
```

- Text becomes outlines (`--keep-text` keeps `<text>`, but fonts may not match).
- `--prefix` makes element ids unique when two figures sit in one HTML page.
- Run `colors` first to see which colours the figure uses and which belong to which arm.
  The legend inside the figure tells you.

## 3. Separate the curves for animation (HTML)

```bash
python scripts/pdf_figures.py colors figures/s05-km-rfs.svg
python scripts/pdf_figures.py split figures/s05-km-rfs.svg --colors '#d7262e,#5b6b82' \
  --min-width 0.7 -o figures/s05-km-rfs.base.svg figures/s05-km-rfs.curves.svg
```

The base layer holds the axes, labels and risk table. The curves layer holds the arms (and
censor ticks, if they share the colour). Stack the two in the same box and reveal the
curves with a transform wipe (`motion.md`, "Wipe reveal").

## 4. Overlays in the figure's own coordinates

Overlays (a dashed line at 24 months, labels with the 24-month rates, a shaded first six
months) go in a third SVG with the **same viewBox** stacked on top. To map data to
coordinates:

- read two x-axis ticks from the extracted SVG (or the rendered PNG): x(m) = x0 + m·k
- read y at 0 % and 100 %: y(p) = y0 − (y0 − y100)·p/100

Check the mapping by placing a dot at a published value (the 24-month rate) and confirming
it sits on the curve. If it doesn't, the mapping is wrong, not the paper.

## Licence

Reusing a published figure in a teaching or journal-club talk with citation is common
practice. Publishers' terms differ, and recording the talk or posting the slides can need
permission. Record what you know in the manifest's `licence` field and flag it to the user
when the talk will be recorded or shared. Open-access papers under CC BY may be reused with
attribution; check the article's licence line.
