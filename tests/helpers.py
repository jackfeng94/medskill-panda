"""Shared helpers for the Medskill Panda tests (standard library only)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "hooks"
LINT_DIR = ROOT / "skills" / "slop-audit" / "scripts"
DECK_TEXT_DIR = ROOT / "skills" / "evidence-audit" / "scripts"

for d in (HOOKS, LINT_DIR, DECK_TEXT_DIR):
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))


def run_hook(script: str, event: dict) -> dict | None:
    """Run a hook through run-hook.sh exactly as Claude Code does; return its JSON or None."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("MEDSKILL_PANDA_NO_GATE", None)
    res = subprocess.run(["sh", str(HOOKS / "run-hook.sh"), script], input=json.dumps(event).encode(),
                         capture_output=True, env=env, timeout=60)
    assert res.returncode == 0, res.stderr.decode()
    out = res.stdout.decode().strip()
    return json.loads(out) if out else None


class TalkFolder:
    """A throwaway talk folder: STATUS.md + brief.md (+ plan.md), with build/ and out/."""

    def __init__(self, plan_row: str | None = "| 3 | Plan | done, approved |", plan: bool = True):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "talk"
        (self.path / "build").mkdir(parents=True)
        (self.path / "out").mkdir()
        (self.path / "brief.md").write_text("# Brief\n", encoding="utf-8")
        if plan:
            (self.path / "plan.md").write_text("# Plan\n", encoding="utf-8")
        self.set_plan_row(plan_row)

    def set_plan_row(self, row: str | None) -> None:
        lines = ["| # | Stage | State |", "|---|---|---|", "| 1 | Interview | done |"]
        if row:
            lines.append(row)
        (self.path / "STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def cleanup(self) -> None:
        self._tmp.cleanup()
