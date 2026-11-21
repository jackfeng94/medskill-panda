#!/usr/bin/env python3
"""PostToolUse hook: lint a slide file for AI slop as soon as it is saved.

Runs slop-audit's lint_slop on .html files written under <talk>/build/ or <talk>/out/
and, when a blocking rule (S01-S04) fires, tells the agent which slide and why, so the
fix happens now instead of in the audit stage. Advisory findings stay for the audit.
Silent everywhere else, and on any error of its own.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from talk import emit, find_talk, gated_part, read_event  # noqa: E402

LINT = HERE.parent / "skills" / "slop-audit" / "scripts"
MAX_LISTED = 8


def findings_for(event: dict) -> tuple[Path, list[dict]] | None:
    if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        return None
    fp = (event.get("tool_input") or {}).get("file_path") or ""
    if not fp.lower().endswith((".html", ".htm")):
        return None
    path = Path(fp) if Path(fp).is_absolute() else Path(event.get("cwd") or os.getcwd()) / fp
    talk = find_talk(path.parent)
    if not talk or not gated_part(talk, path) or not path.is_file():
        return None
    sys.path.insert(0, str(LINT))
    import lint_slop  # noqa: E402  (loads deck_text from evidence-audit)
    found = lint_slop.lint_html(path, "auto", None)
    return path, [f for f in found if f["severity"] == "blocking"]


def main() -> int:
    try:
        res = findings_for(read_event())
    except BaseException:  # fail open, including lint_slop's sys.exit
        return 0
    if not res or not res[1]:
        return 0
    path, blocking = res
    lines = [f"- {f['id']} slide {f['slide'] or '-'}: {f['text']}" + (f" ({f['note']})" if f["note"] else "")
             for f in blocking[:MAX_LISTED]]
    more = len(blocking) - MAX_LISTED
    if more > 0:
        lines.append(f"- … and {more} more")
    emit({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": (
            f"Medskill Panda slop check on {path.name}: {len(blocking)} blocking finding(s). "
            "Delete them rather than reword (see slop-audit catalog.md):\n" + "\n".join(lines)),
    }})
    return 0


if __name__ == "__main__":
    sys.exit(main())
