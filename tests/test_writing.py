"""Tests for the scientific-writing side: project templates, lint_prose and the writing CLIs."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT

WRITING = ROOT / "skills" / "scientific-writing" / "scripts"
sys.path.insert(0, str(WRITING))
import lint_prose  # noqa: E402

HAS_DOCX = importlib.util.find_spec("docx") is not None
CLI_SKILLS = ("scientific-writing", "literature-review", "research-lookup", "citation-management",
              "peer-review", "venue-templates", "hypothesis-generation", "scholar-evaluation")


def run_lint(text: str, suffix: str = ".md", *args: str) -> list[dict]:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / f"m{suffix}"
        p.write_text(text, encoding="utf-8")
        blocks = lint_prose.with_sections(lint_prose.read_blocks(p))
        lang = args[0] if args else lint_prose.detect_lang(blocks)
        return lint_prose.lint(blocks, lang)


def ids(findings, severity=None):
    return [f["id"] for f in findings if severity is None or f["severity"] == severity]


class TemplateTest(unittest.TestCase):
    def body(self, name):
        text = (ROOT / "templates" / name).read_text(encoding="utf-8")
        return text.split("-->", 1)[1]

    def test_claude_and_agents_templates_match(self):
        self.assertEqual(self.body("CLAUDE.scientific-writer.md"), self.body("AGENTS.scientific-writer.md"))

    def test_template_names_only_existing_skills_and_commands(self):
        text = self.body("CLAUDE.scientific-writer.md")
        skills = {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()}
        table = text.split("## Which skill for which job", 1)[1].split("##", 1)[0]
        for name in re.findall(r"`([a-z][a-z0-9-]+)`", table):
            with self.subTest(skill=name):
                self.assertIn(name, skills)
        for cmd in re.findall(r"/medskill-panda:([a-z-]+)", text):
            with self.subTest(command=cmd):
                self.assertTrue((ROOT / "commands" / f"{cmd}.md").is_file())

    def test_template_has_no_stale_rules(self):
        text = self.body("CLAUDE.scientific-writer.md")
        for stale in ("sync_skills.py", "Token usage is unlimited", "MINIMUM Figure", "35-50+"):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, text)


class LintProseTest(unittest.TestCase):
    def test_vietnamese_rules(self):
        found = run_lint(
            "# Đặt vấn đề\n\nSuy tim ngày càng được quan tâm. Tỷ lệ tử vong là 50% sau 5 năm.\n\n"
            "Nghiên cứu chứng minh rằng thuốc hoàn toàn an toàn.\n\n# Kết quả\n\n"
            "Tuổi 65,2 và 8.4 năm, p = 0.000. [MISSING: nhóm chứng]\n")
        for rule in ("P01", "P02", "P03", "P04", "P05", "P06"):
            with self.subTest(rule=rule):
                self.assertIn(rule, ids(found))

    def test_english_rules(self):
        found = run_lint("# Introduction\n\nThis pivotal study delves into AF, which proves benefit. "
                         "Prevalence is 33% in older adults.\n")
        self.assertEqual(sorted(set(ids(found))), ["P02", "P03", "P04"])

    def test_cited_statistics_and_results_numbers_pass(self):
        found = run_lint("# Introduction\n\nSGLT2 inhibitors cut admissions by 26% [3]. "
                         "Mortality was 50% (McMurray et al., 2019).\n\n# Results\n\nResponse was 42%.\n")
        self.assertNotIn("P04", ids(found))

    def test_reference_list_is_checked_for_placeholders_only(self):
        found = run_lint("# Introduction\n\nPlain text.\n\n# References\n\n1. A pivotal paper. 2019. TODO\n")
        self.assertEqual(ids(found), ["P01"])

    def test_bullet_heavy_body(self):
        found = run_lint("# Discussion\n\n" + "".join(f"- point {i}\n" for i in range(8)) + "\nOne. \n\nTwo.\n")
        self.assertIn("P07", ids(found))

    def test_compare_finds_numbers_missing_in_one_version(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / "vi.md", Path(d) / "en.md"
            a.write_text("# A\n\nĐáp ứng 26% ở 120 bệnh nhân, tuổi 65,2.\n", encoding="utf-8")
            b.write_text("# A\n\nResponse 26% in 112 patients, age 65.2.\n", encoding="utf-8")
            diff = lint_prose.compare_numbers(lint_prose.with_sections(lint_prose.read_blocks(a)),
                                              lint_prose.with_sections(lint_prose.read_blocks(b)))
        self.assertEqual(sorted(f["text"] for f in diff), ["112", "120"])

    def test_latex_input(self):
        found = run_lint("\\documentclass{article}\\begin{document}\n\\section{Introduction}\n"
                         "AF affects 2\\% of adults \\cite{k2020}. It is 33\\% in the elderly. % TODO hidden\n"
                         "\\begin{itemize}\\item TBD\\end{itemize}\n\\end{document}\n", ".tex")
        self.assertEqual(sorted((f["id"], f["text"]) for f in found), [("P01", "TBD"), ("P04", "33%")])

    @unittest.skipUnless(HAS_DOCX, "needs python-docx")
    def test_word_input_with_superscript_citations(self):
        from docx import Document  # type: ignore
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "m.docx"
            doc = Document()
            doc.add_heading("Introduction", 1)
            p = doc.add_paragraph("Admissions fell by 26%")
            p.add_run("12").font.superscript = True
            p.add_run(". Mortality was 50% at five years.")
            doc.add_table(rows=1, cols=1).cell(0, 0).text = "TODO 42%"
            doc.save(str(path))
            found = lint_prose.lint(lint_prose.with_sections(lint_prose.read_blocks(path)), "en")
        self.assertEqual(sorted((f["id"], f["text"]) for f in found), [("P01", "TODO"), ("P04", "50%")])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            clean, dirty = Path(d) / "clean.md", Path(d) / "dirty.md"
            clean.write_text("# Intro\n\nPlain text [1].\n", encoding="utf-8")
            dirty.write_text("# Intro\n\nTODO\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(lint_prose.main([str(clean), "--json"]), 0)
                self.assertEqual(lint_prose.main([str(dirty), "--json"]), 1)


class WritingCliTest(unittest.TestCase):
    """Every writing script answers --help (the scientific-writing CLIs need Python 3.11+)."""

    @unittest.skipIf(sys.version_info < (3, 11), "scientific-writing CLIs need Python 3.11+")
    def test_help(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        for skill in CLI_SKILLS:
            for script in sorted((ROOT / "skills" / skill / "scripts").glob("*.py")):
                if script.name.startswith("_"):
                    continue
                with self.subTest(script=f"{skill}/{script.name}"):
                    res = subprocess.run([sys.executable, str(script), "--help"], capture_output=True,
                                         env=env, cwd=tempfile.gettempdir(), timeout=60)
                    self.assertEqual(res.returncode, 0, res.stderr.decode()[-300:])

    @unittest.skipIf(sys.version_info < (3, 11), "scientific-writing CLIs need Python 3.11+")
    def test_scaffold_creates_an_incomplete_workspace(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "draft"
            res = subprocess.run([sys.executable, str(WRITING / "scaffold_manuscript.py"), "--output-dir", str(out),
                                  "--document-id", "test-draft", "--study-design", "randomized_trial",
                                  "--guideline", "consort-2025"], capture_output=True, env=env, timeout=60)
            self.assertEqual(res.returncode, 0, res.stderr.decode()[-300:])
            self.assertTrue(any(out.iterdir()))


if __name__ == "__main__":
    unittest.main()
