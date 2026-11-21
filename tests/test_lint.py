"""Unit tests for the slop linter and the shared deck text extractor."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import helpers  # noqa: F401  (puts the script folders on sys.path)
import deck_text
import lint_slop

HAS_PYPDF = importlib.util.find_spec("pypdf") is not None
HAS_PPTX = importlib.util.find_spec("pptx") is not None


def lint(html: str) -> list[dict]:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "deck.html"
        p.write_text(html, encoding="utf-8")
        return lint_slop.lint_html(p, "auto", None)


def ids(findings, severity=None):
    return [f["id"] for f in findings if severity is None or f["severity"] == severity]


class DeckTextTest(unittest.TestCase):
    def test_blocks_are_separate_and_notes_excluded(self):
        s = deck_text.html_slides('<section class="slide"><h1>HR 0.58</h1><p>95% CI <b>0.45</b>–0.75</p>'
                                  '<aside class="notes">say it</aside></section>')[0]
        self.assertEqual(s["blocks"], ["HR 0.58", "95% CI 0.45–0.75"])
        self.assertEqual(s["text"], "HR 0.58 95% CI 0.45–0.75")
        self.assertEqual(s["notes"], "say it")

    def test_scripts_and_styles_are_ignored(self):
        s = deck_text.html_slides('<section class="slide"><style>.a{}</style><script>var x="TODO"</script>'
                                  '<p>Body</p></section>')[0]
        self.assertEqual(s["text"], "Body")


class LintHtmlTest(unittest.TestCase):
    def test_each_blocking_rule(self):
        cases = {
            "S01": '<p class="eyebrow">KEY INSIGHT</p>',
            "S02": "<p>▸ Click for next: 24-month landmark</p>",
            "S03": "<figcaption>Original NEJM Figure 1, recoloured</figcaption>",
            "S04": "<p>Response rate XX%</p>",
        }
        for rule, body in cases.items():
            with self.subTest(rule=rule):
                found = lint(f'<section class="slide"><h2>Title</h2>{body}</section>')
                self.assertIn(rule, ids(found, "blocking"))

    def test_one_phrase_is_reported_once(self):
        found = lint('<section class="slide"><p class="eyebrow">03 · RESULTS · ITT</p>'
                     '<p>▸ Click for next: landmark</p></section>')
        self.assertEqual(ids(found).count("S01"), 1)
        self.assertEqual(ids(found).count("S02"), 1)

    def test_finding_quotes_its_own_block(self):
        found = lint('<section class="slide"><h1>DAPA-HF</h1><p>Lorem ipsum</p><p>Next paragraph</p></section>')
        s04 = [f for f in found if f["id"] == "S04"][0]
        self.assertEqual(s04["text"], "Lorem ipsum")

    def test_ai_disclosure_in_source_credit_is_allowed(self):
        found = lint('<section class="slide"><h2>Mechanism</h2>'
                     '<p class="source">Illustration generated with ChatGPT, anatomy checked</p></section>')
        self.assertNotIn("S03", ids(found))

    def test_speaker_notes_are_never_linted(self):
        found = lint('<section class="slide"><h2>Title</h2><aside class="notes">[click] TODO</aside></section>')
        self.assertEqual(ids(found, "blocking"), [])

    def test_no_slide_markup_is_blocking(self):
        self.assertEqual(ids(lint('<div class="slide"><p>Text</p></div>'), "blocking"), ["S00"])

    def test_advisory_rules(self):
        found = lint('<section class="slide"><h2>A game-changer 🚀</h2></section>')
        self.assertIn("S15", ids(found, "advisory"))
        self.assertIn("S16", ids(found, "advisory"))


@unittest.skipUnless(HAS_PYPDF and importlib.util.find_spec("reportlab"), "needs pypdf and reportlab")
class LintPdfTest(unittest.TestCase):
    def test_pdf_pages_are_slides(self):
        from reportlab.pdfgen import canvas  # type: ignore
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "deck.pdf"
            c = canvas.Canvas(str(p))
            c.drawString(72, 720, "Clean title slide")
            c.showPage()
            c.drawString(72, 720, "Lorem ipsum dolor")
            c.showPage()
            c.save()
            found = lint_slop.lint_pdf(p, None)
        self.assertEqual([(f["id"], f["slide"]) for f in found if f["severity"] == "blocking"], [("S04", 2)])


@unittest.skipUnless(HAS_PPTX, "needs python-pptx")
class LintPptxTest(unittest.TestCase):
    def test_pptx_text_rules(self):
        from pptx import Presentation  # type: ignore
        from pptx.util import Inches
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "deck.pptx"
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            slide.shapes.title.text = "Results"
            slide.shapes.add_textbox(Inches(1), Inches(2), Inches(6), Inches(1)).text_frame.text = "TODO add HR"
            prs.save(str(p))
            found = lint_slop.lint_pptx(p, None)
        self.assertIn("S04", ids(found, "blocking"))

    def test_pptx_footer_and_credit_do_not_count_as_body_text(self):
        from pptx import Presentation  # type: ignore
        from pptx.util import Inches
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "deck.pptx"
            prs = Presentation()
            for _ in range(2):
                slide = prs.slides.add_slide(prs.slide_layouts[5])
                slide.shapes.title.text = "Admissions fell by a quarter"
                for name in ("Source", "Credit"):
                    box = slide.shapes.add_textbox(Inches(1), Inches(6), Inches(8), Inches(1))
                    box.name = name
                    box.text_frame.text = " ".join(["word"] * 30)
            prs.save(str(p))
            found = lint_slop.lint_pptx(p, None)
        self.assertNotIn("S18", ids(found))


if __name__ == "__main__":
    unittest.main()
