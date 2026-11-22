#!/bin/sh
# CI check for the DEMO-CRS example: build the HTML decks, the PowerPoint decks and the manuscript
# with the plugin's own tools and run every check on them. No screenshots, no LibreOffice.
# Needs numpy, matplotlib, python-docx and python-pptx. Fails on any finding.
set -e
X=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$X/../.." && pwd)
H=$R/skills/html-deck-building/scripts
P=$R/skills/pptx-deck-building/scripts
LINT=$R/skills/slop-audit/scripts/lint_slop.py
cd "$X"
python3 make_data.py out > /dev/null
python3 make_charts.py > /dev/null
python3 make_deck.py "$X" > /dev/null
for L in en vi; do
  (cd "deck_$L" && mkdir -p out &&
   python3 "$H/compose_deck.py" --slides build/slides.html --css build/deck.css --title "DEMO-CRS · Medskill Panda" \
     --lang "$L" --cite "$(cat cite.txt)" -o build/index.src.html > /dev/null &&
   python3 "$H/build_deck.py" build/index.src.html out/demo-crs.html > /dev/null &&
   python3 "$LINT" out/demo-crs.html --lang "$L")
done
python3 make_template.py > /dev/null
python3 make_pptx.py "$X" > /dev/null
for L in en vi; do
  (cd "pptx_$L" && mkdir -p out &&
   python3 "$P/check_spec.py" build/deck.json --recipe journal-club &&
   python3 "$P/pptx_from_spec.py" build/deck.json out/demo-crs.pptx > /dev/null &&
   python3 "$P/check_pptx.py" out/demo-crs.pptx &&
   python3 "$LINT" out/demo-crs.pptx --lang "$L")
done
mkdir -p manuscript
python3 make_manuscript.py "$X" > /dev/null
# The manuscript keeps exactly one deliberate gap: [MISSING: authors to confirm].
python3 "$R/skills/scientific-writing/scripts/lint_prose.py" manuscript/demo-crs.docx --json > manuscript/lint.json || true
python3 - <<'PY'
import json, sys
r = json.load(open("manuscript/lint.json", encoding="utf-8"))
ids = [(f["id"], f["text"]) for f in r["findings"]]
if ids != [("P01", "[MISSING: authors to confirm]")]:
    sys.exit(f"lint_prose: expected only the deliberate [MISSING] gap, got {ids}")
print("# lint_prose: demo-crs.docx: only the deliberate gap")
PY
rm -f manuscript/lint.json
echo "DEMO-CRS example: all checks passed"
