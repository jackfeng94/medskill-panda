#!/usr/bin/env python3
"""Check a deck.json before building: fields each slide type needs, notes, sources, and whether
the deck has every component its talk type requires.

  python check_spec.py build/deck.json [--recipe journal-club] [--json]

Recipes (deck-planning/recipes.md):
  journal-club         title, PICO question, design diagram, a result slide, appraisal,
                       bottom line, references (agenda when the deck has more than 8 slides)
  journal-club-report  the same without the agenda
  conference           title, design diagram, a result slide, bottom line
  lecture              title, agenda, bottom line, references

Exit code 1 when a required component or field is missing, or a slide has no speaker notes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REQUIRED = {
    "title": ["title"], "closing": ["title"], "bullets": ["title", "bullets"],
    "figure": ["title", "image", "alt"], "figure-text": ["title", "image", "alt", "bullets"],
    "big-number": ["title", "numbers"], "table": ["title", "columns", "rows"],
    "diagram": ["title", "nodes"], "chart": ["title", "chart", "categories", "series"],
    "references": ["title", "items"], "agenda": ["title", "items"], "section": ["title"],
    "key-message": ["message"], "two-column": ["title", "left", "right"],
    "comparison": ["title", "left", "right"], "pico": ["title", "rows"],
}
DATA = {"figure", "figure-text", "big-number", "table", "chart"}
RESULT = {"figure", "figure-text", "chart", "big-number", "table"}
# component -> (slide types that satisfy it, what to add when missing)
COMPONENTS = {
    "title": ({"title"}, "a `title` slide: paper, journal, presenter, date"),
    "question": ({"pico"}, "a `pico` slide: the clinical question as population, intervention, comparator, outcome"),
    "design": ({"diagram"}, "a `diagram` slide: the trial schema or CONSORT flow"),
    "result": (RESULT, "a result slide (`figure-text`, `chart`, `big-number`): the primary outcome"),
    "appraisal": ({"two-column", "comparison", "table"}, "a `two-column` slide: strengths and limitations"),
    "bottom-line": ({"key-message"}, "a `key-message` slide: the one sentence to remember"),
    "references": ({"references"}, "a `references` slide"),
    "agenda": ({"agenda"}, "an `agenda` slide after the title"),
}
RECIPES = {
    "journal-club": ["title", "question", "design", "result", "appraisal", "bottom-line", "references", "agenda?"],
    "journal-club-report": ["title", "question", "design", "result", "appraisal", "bottom-line", "references"],
    "conference": ["title", "design", "result", "bottom-line"],
    "lecture": ["title", "agenda", "bottom-line", "references"],
}


def check(spec: dict, recipe: str | None) -> list[dict]:
    found = []

    def add(kind, slide, msg, serious=True):
        found.append({"kind": kind, "slide": slide, "message": msg, "serious": serious})

    slides = spec.get("slides", [])
    deck_cite = spec.get("cite")
    for i, s in enumerate(slides, 1):
        t = s.get("type", "")
        if t not in REQUIRED:
            add("unknown-type", i, f"type {t!r} is not one of {sorted(REQUIRED)}")
            continue
        for f in REQUIRED[t]:
            if not s.get(f):
                add("missing-field", i, f"{t} needs `{f}`")
        if not s.get("notes"):
            add("no-notes", i, "no speaker notes")
        if t in DATA and not (s.get("cite") or deck_cite or s.get("credit")):
            add("no-source", i, f"{t} slide shows data but has no `cite` or `credit`")
    if recipe:
        types = [s.get("type") for s in slides]
        for comp in RECIPES[recipe]:
            optional = comp.endswith("?")
            comp = comp.rstrip("?")
            if optional and len(slides) <= 8:
                continue
            kinds, hint = COMPONENTS[comp]
            if not any(t in kinds for t in types):
                add("missing-component", 0, f"{recipe}: no {comp} slide; add {hint}")
    return found


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--recipe", choices=sorted(RECIPES))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    found = check(spec, a.recipe)
    if a.json:
        print(json.dumps({"slides": len(spec.get("slides", [])), "findings": found}, ensure_ascii=False, indent=2))
    else:
        print(f"# check_spec: {Path(a.spec).name}, {len(spec.get('slides', []))} slides, {len(found)} finding(s)"
              + (f", recipe {a.recipe}" if a.recipe else ""))
        for f in found:
            print(f"- {'slide ' + str(f['slide']) if f['slide'] else 'deck'}: {f['kind']}: {f['message']}")
    return 1 if any(f["serious"] for f in found) else 0


if __name__ == "__main__":
    sys.exit(main())
