#!/usr/bin/env python3
"""PostToolUse hook: check a slide file as soon as it is saved.

For .html files written under <talk>/build/ or <talk>/out/:
  1. slop-audit's lint_slop: blocking machine-made patterns (S00-S04), by slide;
  2. evidence-audit's check_claims: every number on a slide must be a value of a claim in
     <talk>/evidence/claims.json for that slide (UNSUPPORTED), or is mapped to another slide
     (ELSEWHERE). Without claims.json, slides that show numbers are reported as unchecked.
The agent is told which slide and why, so the fix happens now instead of at the audit.
Silent everywhere else, and on any error of its own.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from talk import emit, find_talk, gated_part, read_event  # noqa: E402

LINT = HERE.parent / "skills" / "slop-audit" / "scripts"
EVIDENCE = HERE.parent / "skills" / "evidence-audit" / "scripts"
MAX_LISTED = 8


def saved_slide(event: dict) -> tuple[Path, Path] | None:
    """(talk folder, saved file) when the event wrote an HTML slide file inside build/ or out/."""
    if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        return None
    fp = (event.get("tool_input") or {}).get("file_path") or ""
    if not fp.lower().endswith((".html", ".htm")):
        return None
    path = Path(fp) if Path(fp).is_absolute() else Path(event.get("cwd") or os.getcwd()) / fp
    talk = find_talk(path.parent)
    if not talk or not gated_part(talk, path) or not path.is_file():
        return None
    return talk, path


def slop_lines(path: Path) -> list[str]:
    sys.path.insert(0, str(LINT))
    import lint_slop  # noqa: E402  (loads deck_text from evidence-audit)
    found = [f for f in lint_slop.lint_html(path, "auto", None) if f["severity"] == "blocking"]
    return [f"- {f['id']} slide {f['slide'] or '-'}: {f['text']}" + (f" ({f['note']})" if f["note"] else "")
            for f in found]


def number_lines(talk: Path, path: Path) -> list[str]:
    sys.path.insert(0, str(EVIDENCE))
    import check_claims  # noqa: E402
    from deck_text import load_slides  # noqa: E402
    slides = load_slides(path)
    claims_file = talk / "evidence" / "claims.json"
    if not claims_file.is_file():
        with_numbers = [s["index"] for s in slides if check_claims.numbers(s.get("text_nosvg", s["text"]))]
        return [f"- slides {with_numbers} show numbers but evidence/claims.json does not exist yet"] if with_numbers else []
    claims = json.loads(claims_file.read_text(encoding="utf-8")).get("claims", [])
    return [f"- {kind}: {msg}" for kind, msg in check_claims.slide_findings(slides, claims)]


def report(title: str, lines: list[str], advice: str) -> str:
    shown = lines[:MAX_LISTED]
    if len(lines) > MAX_LISTED:
        shown.append(f"- … and {len(lines) - MAX_LISTED} more")
    return f"{title}: {len(lines)} finding(s). {advice}\n" + "\n".join(shown)


def main() -> int:
    try:
        hit = saved_slide(read_event())
        if not hit:
            return 0
        talk, path = hit
        parts = []
        try:
            slop = slop_lines(path)
        except BaseException:  # fail open, including lint_slop's sys.exit
            slop = []
        if slop:
            parts.append(report(f"Medskill Panda slop check on {path.name}", slop,
                                "Delete them rather than reword (see slop-audit catalog.md)."))
        try:
            nums = number_lines(talk, path)
        except BaseException:
            nums = []
        if nums:
            parts.append(report(f"Medskill Panda number check on {path.name}", nums,
                                "Every number on a slide must be a value of a claim for that slide in "
                                "evidence/claims.json: add the claim from its source (evidence-research) or "
                                "remove the number. Never add a claim from memory."))
    except BaseException:  # fail open
        return 0
    if parts:
        emit({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "\n\n".join(parts)}})
    return 0


if __name__ == "__main__":
    sys.exit(main())
