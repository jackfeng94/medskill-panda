# Medskill Panda: notes for working on this repository

This file is for developing the plugin itself. It is not loaded by users of the plugin. The
project file the plugin installs into a user's writing project is `templates/CLAUDE.scientific-writer.md`.

## What this is

A Claude Code plugin with two halves:

- **Medical slides:** `medical-deck` runs the pipeline brief → plan (approval gate) → evidence →
  figures → build (HTML / PPTX / Beamer) → audit → deliver. A "talk folder" holds `STATUS.md`,
  `brief.md`, `plan.md`, `evidence/claims.json`, `figures/`, `build/`, `out/`, `audit/`.
- **Scientific writing:** `scientific-writing` and its neighbours (literature review, citations,
  peer review, venue templates…). IMRaD drafts with an evidence ledger
  (`references/claims.csv`, `source_manifest.json`); `/medskill-panda:paper-to-deck` turns a draft into a talk.

The owner writes in Vietnamese. Answer in Vietnamese. Code, comments, commit messages and PR text are in English.

## Layout

| Path | What |
|------|------|
| `.claude-plugin/plugin.json`, `marketplace.json` | Manifest; the version lives in both |
| `skills/<name>/SKILL.md` (+ `scripts/`, `references/`) | 36 skills |
| `commands/*.md` | Slash commands (`audit-manuscript`, `paper-to-deck`, `scientific-writer-init`, `status`) |
| `hooks/hooks.json`, `run-hook.sh`, `*.py` | `route_prompt` (send slide requests to medical-deck), `plan_gate` (block build/ and out/ before the plan is approved), `slop_on_save` (lint and number check when a slide is saved), `talk.py` (shared helpers) |
| `examples/demo-crs/` | Worked ENT example from simulated data: HTML deck, 12-slide PPTX, IMRaD manuscript, 8 charts |
| `assets/` | Logo and README artwork; `assets/src/` holds the scripts that draw it |
| `docs/GUIDE.md`, `docs/HUONG-DAN.md` | Beginner guides (EN, VI) |
| `README.md`, `README.vi.md` | Kept in step: same version, commands, images and sections |
| `tests/` | unittest suite |

## Commands

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests      # the suite (CI: Python 3.10 and 3.13)
sh examples/demo-crs/check.sh                                       # build the example and run every checker on it (CI job "example")
sh examples/demo-crs/build.sh                                       # full rebuild with LibreOffice renders and screenshots
```

Key scripts: `skills/pptx-deck-building/scripts/pptx_from_spec.py` (deck.json → .pptx; spec in
`spec.md`), `check_spec.py` (components per talk type), `check_pptx.py`;
`skills/slop-audit/scripts/lint_slop.py`; `skills/evidence-audit/scripts/check_claims.py`, `deck_text.py`;
`skills/scientific-writing/scripts/lint_prose.py`.

## Rules that tests enforce

- **Counts and versions:** README badges `skills-N` and `unit tests-N` must match the skill folders
  and `unittest` discovery. The version in `plugin.json` must match `marketplace.json`, both READMEs
  and a `## <version>` heading in `CHANGELOG.md`. Adding a test or a skill means updating both badges.
- **Bilingual docs:** `README.md` and `README.vi.md` must list the same commands and images, and each
  must link the other. `GUIDE.md` and `HUONG-DAN.md` must have the same numbered `##` sections.
- **Artwork:** every image under `assets/` is named `<name>[.vi].<hash8>.png` and must be used. Never
  edit a PNG by hand; regenerate it (see below).
- **Removed skills** (listed in `tests/test_repo.py`) must not be named anywhere outside
  `CHANGELOG.md` and `tests/`, this file included.
- **Example:** `check.sh` expects 0 findings from `lint_slop`, `check_spec` and `check_pptx`, and exactly one
  `lint_prose` finding: the deliberate `[MISSING: authors to confirm]`.

## Code conventions

- Hook scripts run on the user's Python 3.8+: no `match`, no `X | Y` types at runtime (use
  `from __future__ import annotations`), standard library only. They must fail open: never block on their own error.
- Every script must parse on Python 3.10: no backslashes or reused quotes inside f-string expressions.
  Check with `python3.11 -c "import ast; ast.parse(open(F).read())"`.
- Run with `PYTHONDONTWRITEBYTECODE=1`; never commit `__pycache__`.
- Numbers shown on example slides come from `out/results.json` or `values.json`, never typed in by hand.
- Generated PPTX: no shadows (`Builder.flat` removes the theme style from lines), flat shapes, body
  text ≥ 18 pt, speaker notes on every slide. Slide types are listed in `spec.md`; add new ones there and in `check_spec.py`.

## Visual style (owner's preferences)

- Not like Grand Rounds or any other project: own wording, own layouts.
- "Less AI, but not plain": no rounded cards, shadows, gradients, glow or emoji. Flat colour, thin
  rules, editorial or journal look.
- Fonts in artwork: Source Serif 4 for headings (bundled in `assets/src/fonts/`), Inter for text,
  JetBrains Mono for code. No synthetic italics.
- Plain, natural wording in both languages. In manuscripts, run-in headings end with a colon (`Methods:`).

## Regenerating the README artwork

```bash
sh examples/demo-crs/build.sh                       # refreshes examples/demo-crs/screens/
python3 assets/src/make_art.py <dir>                # writes art_en.html, art_vi.html
node assets/src/shoot.js <dir>/art_en.html <dir>/hi-en 2
node assets/src/shoot.js <dir>/art_vi.html <dir>/hi-vi 2
python3 assets/src/publish_art.py <dir>             # hashed copies in assets/, references rewritten
```

`publish_art.py` replaces every image found in `<dir>`. To change one figure only, copy just its two
PNGs (`hi-en-<section>.png`, `hi-vi-<section>.png`) into a separate folder and publish that.
Rebuilding the example rewrites SVG, HTML and DOCX outputs even when nothing changed; commit only the
outputs your change is about.

## Git and PRs

- Work on the assigned `claude/...` branch, reset from `origin/main` at the start of each round.
- Never force-push. If the remote branch has old, already-merged commits, run
  `git merge -s ours FETCH_HEAD` after checking that `git diff FETCH_HEAD origin/main` is empty.
- Add an entry to `CHANGELOG.md` under `## Unreleased`, written in Vietnamese.
- Standing permission from the owner: when CI is green and the PR is mergeable, squash-merge it
  without asking (`gh api -X PUT repos/jackfeng94/medskill-panda/pulls/<n>/merge -f merge_method=squash`).

## Privacy

Medical data: never put patient identifiers in examples, tests or commits. The owner's email appears
only in the plugin manifest author field.
