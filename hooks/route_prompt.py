#!/usr/bin/env python3
"""UserPromptSubmit hook: send slide requests to the orchestrator.

With many plugins installed, Claude Code drops the descriptions of rarely used skills from
the skill list, so a request such as "make 5 slides on drug X" may go straight to a
builder skill. When the prompt asks for slides, a deck or a presentation, this hook adds a
short reminder: start from medskill-panda:medical-deck, and make the first reply the
interview. Silent for every other prompt, and on any error of its own.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from talk import emit, read_event  # noqa: E402

DECK_WORDS = re.compile(
    r"\b(?:slides?|slide\s*deck|decks?|presentations?|power\s?point|pptx|keynote|journal\s+club|"
    r"grand\s+rounds|poster\s+talk)\b"
    r"|trình\s+chiếu|thuyết\s+trình|bài\s+trình\s+bày|bài\s+giảng|báo\s+cáo\s+(?:ca|chuyên\s+đề)|"
    r"sinh\s+hoạt\s+khoa\s+học",
    re.I)

REMINDER = (
    "Medskill Panda: this prompt asks for slides or a presentation. If the topic is medical or "
    "health-science, call the Skill tool with medskill-panda:medical-deck before anything else; "
    "do not start from html-deck-building or pptx-deck-building. Unless a talk folder with a "
    "brief the user has confirmed already exists, this turn's reply is the deck-grilling "
    "interview: one round of numbered questions, each with a recommended answer. Then end the "
    "turn and wait for the answers: no talk folder, files, literature searches or slides yet."
)


def wants_deck(prompt: str) -> bool:
    p = prompt.strip()
    return bool(p) and not p.startswith("/") and bool(DECK_WORDS.search(p))


def main() -> int:
    try:
        event = read_event()
        if wants_deck(event.get("prompt") or ""):
            emit({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                         "additionalContext": REMINDER}})
    except Exception:  # fail open
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
