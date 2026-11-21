"""Shared helpers for the Medskill Panda hooks: find the talk folder and read its plan state.

A talk folder is a directory that holds both STATUS.md and brief.md (the orchestrator
creates them in stages 1). Paths outside a talk folder are none of the hooks' business.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

GATED = {"build", "out"}          # folders that must wait for an approved plan
APPROVED = re.compile(r"(?<!not )(?<!not yet )\bapproved\b|đã duyệt", re.I)
PLAN_ROW = re.compile(r"^\s*\|\s*3\s*\||^\s*\|[^|]*\|\s*plan\b", re.I)


def read_event() -> dict:
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    return json.loads(raw) if raw.strip() else {}


def find_talk(path: Path, max_up: int = 8) -> Path | None:
    """The nearest ancestor of `path` (or `path` itself) that is a talk folder."""
    p = path
    for _ in range(max_up + 1):
        if p.is_dir() and (p / "STATUS.md").is_file() and (p / "brief.md").is_file():
            return p
        if p.parent == p:
            return None
        p = p.parent
    return None


def gated_part(talk: Path, path: Path) -> str | None:
    """'build' or 'out' when `path` lies in one of the gated folders of `talk`."""
    try:
        rel = path.resolve().relative_to(talk.resolve())
    except ValueError:
        return None
    return rel.parts[0] if rel.parts and rel.parts[0] in GATED else None


def plan_state(talk: Path) -> tuple[bool, str]:
    """(approved?, reason). Approval is recorded on the Plan row of STATUS.md."""
    if not (talk / "plan.md").is_file():
        return False, "there is no plan.md yet"
    for line in (talk / "STATUS.md").read_text(encoding="utf-8", errors="replace").splitlines():
        if PLAN_ROW.search(line):
            if APPROVED.search(line):
                return True, ""
            return False, f"the Plan row of STATUS.md does not say approved ({line.strip()[:120]})"
    return False, "STATUS.md has no Plan row (stage 3)"


def emit(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False))
