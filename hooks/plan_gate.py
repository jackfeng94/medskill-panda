#!/usr/bin/env python3
"""PreToolUse hook: no deck is built before the user approves plan.md.

Blocks, inside a talk folder whose plan is not approved:
  - Write/Edit/MultiEdit of any file under <talk>/build/ or <talk>/out/;
  - Bash commands that run a deck builder (compose_deck.py, build_deck.py,
    pptx_from_spec.py) on such a talk folder.
Everything else passes untouched. Set MEDSKILL_PANDA_NO_GATE=1 to switch the gate off.
The hook fails open: any error of its own lets the tool call through.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from talk import emit, find_talk, gated_part, plan_state, read_event  # noqa: E402

BUILDERS = ("compose_deck.py", "build_deck.py", "pptx_from_spec.py")
TOKEN = re.compile(r'"([^"]+)"|\'([^\']+)\'|(\S+)')


def blocked_talks(event: dict) -> list[Path]:
    tool = event.get("tool_name", "")
    inp = event.get("tool_input") or {}
    cwd = Path(event.get("cwd") or os.getcwd())
    talks: list[Path] = []
    if tool in ("Write", "Edit", "MultiEdit"):
        fp = inp.get("file_path") or ""
        if fp:
            path = Path(fp) if Path(fp).is_absolute() else cwd / fp
            talk = find_talk(path.parent)
            if talk and gated_part(talk, path):
                talks.append(talk)
    elif tool == "Bash":
        cmd = inp.get("command") or ""
        if any(b in cmd for b in BUILDERS):
            cands = [cwd] + [cwd / next(g for g in m.groups() if g) for m in TOKEN.finditer(cmd)]
            for c in cands:
                talk = find_talk(c if c.is_dir() else c.parent)
                if talk and talk not in talks:
                    talks.append(talk)
    return [t for t in talks if not plan_state(t)[0]]


def main() -> int:
    if os.environ.get("MEDSKILL_PANDA_NO_GATE") == "1":
        return 0
    try:
        talks = blocked_talks(read_event())
    except Exception:  # fail open
        return 0
    if talks:
        t = talks[0]
        why = plan_state(t)[1]
        emit({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"Medskill Panda plan gate: {t.name}/build and {t.name}/out stay closed until the user "
                f"approves plan.md ({why}). Show the user the plan and wait for a clear yes, then mark "
                f"stage 3 in STATUS.md as 'done, approved' and try again. Never mark it approved "
                f"without the user's yes."),
        }})
    return 0


if __name__ == "__main__":
    sys.exit(main())
