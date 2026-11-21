#!/bin/sh
# Rebuild the DEMO-HF example end to end (needs numpy, matplotlib, python-docx, LibreOffice,
# pymupdf and Node Playwright). Run from anywhere.
set -e
X=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$X/../.." && pwd)
H=$R/skills/html-deck-building/scripts
cd "$X"
python3 make_data.py out > /dev/null
python3 make_charts.py > /dev/null
python3 make_deck.py "$X"
for L in en vi; do
  (cd "deck_$L" && mkdir -p out &&
   python3 "$H/compose_deck.py" --slides build/slides.html --css build/deck.css --title "DEMO-HF · Medskill Panda" \
     --lang "$L" --cite "$(cat cite.txt)" -o build/index.src.html &&
   python3 "$H/build_deck.py" build/index.src.html out/demo-hf.html &&
   python3 "$R/skills/slop-audit/scripts/lint_slop.py" out/demo-hf.html --lang "$L")
done
mkdir -p manuscript screens
python3 make_template.py > /dev/null
python3 make_pptx.py "$X" > /dev/null
P=$R/skills/pptx-deck-building/scripts
for L in en vi; do
  (cd "pptx_$L" && mkdir -p out &&
   python3 "$P/pptx_from_spec.py" build/deck.json out/demo-hf.pptx &&
   python3 "$P/check_pptx.py" out/demo-hf.pptx &&
   python3 "$R/skills/slop-audit/scripts/lint_slop.py" out/demo-hf.pptx --lang "$L" || true
   cd out && soffice --headless --convert-to pdf demo-hf.pptx > /dev/null)
done
python3 make_manuscript.py "$X"
(cd manuscript && soffice --headless --convert-to pdf demo-hf.docx > /dev/null)
python3 "$R/skills/scientific-writing/scripts/lint_prose.py" manuscript/demo-hf.docx || true
rm -f screens/en-*.png screens/vi-*.png screens/pptx-*.png
for L in en vi; do node shoot_deck.js "$X/deck_$L/out/demo-hf.html" "$X/screens/$L" 6; done
python3 - <<'PY'
import pymupdf
for L in ("en", "vi"):
    for i, page in enumerate(pymupdf.open(f"pptx_{L}/out/demo-hf.pdf"), 1):
        page.get_pixmap(dpi=144).save(f"screens/pptx-{L}-{i}.png")
d = pymupdf.open("manuscript/demo-hf.pdf")
d[0].get_pixmap(dpi=150).save("screens/page1.png")
p = d[1]
r = p.rect
p.get_pixmap(dpi=150, clip=pymupdf.Rect(r.x0 + 40, r.y0 + 40, r.x1 - 40, r.y0 + 330)).save("screens/page2-figure.png")
PY
