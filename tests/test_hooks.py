"""End-to-end tests of the three hooks, run through run-hook.sh like Claude Code runs them."""
from __future__ import annotations

import json
import unittest

from helpers import TalkFolder, run_hook

DECK = """<section class="slide"><p class="eyebrow">03 · RESULTS · ITT</p><h1>DAPA-HF</h1>
<p>Lorem ipsum</p><aside class="notes">[click] next</aside></section>"""


class PlanGateTest(unittest.TestCase):
    def setUp(self):
        self.talk = TalkFolder()

    def tearDown(self):
        self.talk.cleanup()

    def write_event(self, rel="build/slides.html"):
        return {"tool_name": "Write", "tool_input": {"file_path": str(self.talk.path / rel)}}

    def denied(self, event) -> bool:
        out = run_hook("plan_gate.py", event)
        return bool(out) and out["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_approved_rows_open_the_gate(self):
        for row in ("| 3 | Plan | done, approved |", "| 3 | Plan | Done, Approved by user |",
                    "| 3 | Plan | done, đã duyệt |", "| 3 | Plan | đã được duyệt |"):
            with self.subTest(row=row):
                self.talk.set_plan_row(row)
                self.assertFalse(self.denied(self.write_event()))

    def test_unapproved_rows_keep_the_gate_shut(self):
        for row in ("| 3 | Plan | not approved |", "| 3 | Plan | isn't approved yet |",
                    "| 3 | Plan | not yet been approved |", "| 3 | Plan | pending, approved? no |",
                    "| 3 | Plan | awaiting approval |", "| 3 | Plan | doing |",
                    "| 3 | Plan | chưa duyệt |", "| 3 | Plan | chờ duyệt |",
                    "| 3 | Plan | không được duyệt |", "| 3 | Plan | wasn’t approved |"):
            with self.subTest(row=row):
                self.talk.set_plan_row(row)
                self.assertTrue(self.denied(self.write_event()))

    def test_missing_plan_or_row_shuts_the_gate(self):
        self.talk.set_plan_row(None)
        self.assertTrue(self.denied(self.write_event()))
        self.talk.set_plan_row("| 3 | Plan | done, approved |")
        (self.talk.path / "plan.md").unlink()
        self.assertTrue(self.denied(self.write_event()))

    def test_out_folder_is_gated_too(self):
        self.talk.set_plan_row("| 3 | Plan | todo |")
        self.assertTrue(self.denied(self.write_event("out/deck.html")))

    def test_files_outside_build_and_out_pass(self):
        self.talk.set_plan_row("| 3 | Plan | todo |")
        self.assertFalse(self.denied(self.write_event("plan.md")))
        self.assertFalse(self.denied(self.write_event("evidence/claims.json")))

    def test_builder_commands_are_gated(self):
        self.talk.set_plan_row("| 3 | Plan | todo |")
        for cmd in (f"python build_deck.py {self.talk.path}/build/index.src.html {self.talk.path}/out/d.html",
                    f"cd {self.talk.path}/build && latexmk -pdf deck.tex",
                    f'python pptx_from_spec.py "{self.talk.path}/build/spec.json"'):
            with self.subTest(cmd=cmd):
                event = {"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": str(self.talk.path)}
                self.assertTrue(self.denied(event))

    def test_unrelated_bash_passes(self):
        self.talk.set_plan_row("| 3 | Plan | todo |")
        event = {"tool_name": "Bash", "tool_input": {"command": "ls -la"}, "cwd": str(self.talk.path)}
        self.assertFalse(self.denied(event))

    def test_bad_input_fails_open(self):
        self.assertIsNone(run_hook("plan_gate.py", {"tool_name": "Write", "tool_input": None}))


class RoutePromptTest(unittest.TestCase):
    def context(self, prompt):
        out = run_hook("route_prompt.py", {"prompt": prompt})
        return out and out["hookSpecificOutput"]["additionalContext"]

    def test_slide_requests_get_the_reminder(self):
        for p in ("làm 5 slide về suy tim", "Make a journal club deck on DAPA-HF",
                  "chuẩn bị bài thuyết trình grand rounds", "báo cáo ca lâm sàng viêm phổi"):
            with self.subTest(p=p):
                self.assertIn("medical-deck", self.context(p) or "")

    def test_other_prompts_are_silent(self):
        for p in ("fix the slider component css", "viết tổng quan tài liệu về SGLT2", "/grill-deck", ""):
            with self.subTest(p=p):
                self.assertFalse(self.context(p))


class SlopOnSaveTest(unittest.TestCase):
    def setUp(self):
        self.talk = TalkFolder()

    def tearDown(self):
        self.talk.cleanup()

    def save(self, rel, html):
        path = self.talk.path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        out = run_hook("slop_on_save.py", {"tool_name": "Write", "tool_input": {"file_path": str(path)}})
        return out and out["hookSpecificOutput"]["additionalContext"]

    def test_blocking_findings_are_reported(self):
        msg = self.save("build/slides.html", DECK)
        self.assertIn("S01", msg)
        self.assertIn("S04", msg)
        self.assertNotIn("[click]", msg)  # speaker notes are never linted

    def claims(self, *values, slide=1):
        ev = self.talk.path / "evidence"
        ev.mkdir(exist_ok=True)
        (ev / "claims.json").write_text(json.dumps({"claims": [
            {"id": "c01", "slide": slide, "values": list(values), "quote": " ".join(values), "kind": "observed"}]}),
            encoding="utf-8")

    def test_clean_slide_with_sourced_numbers_is_silent(self):
        self.claims("HR 0.58", "0.45–0.75")
        self.assertFalse(self.save("build/slides.html",
                                   '<section class="slide"><h2>HR 0.58 (95% CI 0.45–0.75)</h2></section>'))

    def test_number_without_claim_is_reported(self):
        self.claims("HR 0.58")
        msg = self.save("build/slides.html", '<section class="slide"><h2>HR 0.58, NNT 21</h2></section>')
        self.assertIn("number check", msg)
        self.assertIn("UNSUPPORTED", msg)
        self.assertIn("'21'", msg)

    def test_number_mapped_to_another_slide_is_reported(self):
        self.claims("HR 0.58", slide=2)
        msg = self.save("build/slides.html", '<section class="slide"><h2>HR 0.58</h2></section>')
        self.assertIn("ELSEWHERE", msg)

    def test_numbers_without_any_claims_file_are_reported(self):
        msg = self.save("build/slides.html", '<section class="slide"><h2>HR 0.58</h2></section>')
        self.assertIn("claims.json does not exist", msg)

    def test_slide_without_numbers_and_claims_is_silent(self):
        self.assertFalse(self.save("build/slides.html", '<section class="slide"><h2>Mechanism of action</h2></section>'))

    def test_unrecognised_markup_is_reported(self):
        self.assertIn("S00", self.save("build/slides.html", '<div class="slide"><p>Lorem ipsum</p></div>'))

    def test_files_outside_the_talk_build_are_ignored(self):
        self.assertFalse(self.save("notes/draft.html", DECK))


if __name__ == "__main__":
    unittest.main()
