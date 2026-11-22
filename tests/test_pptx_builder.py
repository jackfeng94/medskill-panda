"""pptx_from_spec.py (every slide type, diagram style) and check_spec.py."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT

SCRIPTS = ROOT / "skills" / "pptx-deck-building" / "scripts"
BUILDER = SCRIPTS / "pptx_from_spec.py"
sys.path.insert(0, str(SCRIPTS))
import check_spec  # noqa: E402

PARTS = ["Question", "Design", "Results", "Appraisal"]
FULL_DECK = {"cite": "Doe J, et al. Example J 2026", "slides": [
    {"type": "title", "title": "Structured follow-up after discharge", "subtitle": "Doe J, et al. Example J 2026",
     "presenter": "Dr A Presenter", "affiliation": "Cardiology", "event": "Journal club", "date": "22 Nov 2026"},
    {"type": "agenda", "title": "Four parts", "items": [{"text": x, "minutes": 3} for x in PARTS], "current": 3},
    {"type": "pico", "title": "Does follow-up prevent admissions?", "rows": [
        {"label": "Population", "text": "HFrEF after discharge"}, {"label": "Intervention", "text": "Structured follow-up"},
        {"label": "Comparator", "text": "Usual care"}, {"label": "Outcome", "text": "Admission at 24 months"}]},
    {"type": "diagram", "title": "Randomised 1:1", "nodes": [
        {"id": "a", "x": 0, "y": 0.3, "w": 0.3, "h": 0.3, "text": "A"}, {"id": "b", "x": 0.6, "y": 0.3, "w": 0.3, "h": 0.3, "text": "B"}],
     "edges": [{"from": "a", "to": "b"}]},
    {"type": "section", "title": "Results", "subtitle": "Admissions", "parts": PARTS, "current": 3},
    {"type": "figure-text", "title": "Curves separated early", "image": "fig.png", "alt": "KM curve",
     "bullets": ["Difference 6.7 points"], "takeaway": "One admission prevented per 15 patients"},
    {"type": "big-number", "title": "Fifteen to treat", "numbers": [
        {"value": "15", "label": "number needed to treat", "context": "over 24 months"},
        {"value": "0.75", "label": "rate ratio", "context": "95% CI 0.63–0.89"}]},
    {"type": "two-column", "title": "Strong design, simulated data",
     "left": {"heading": "Strengths", "bullets": ["Randomised"]},
     "right": {"heading": "Limitations", "bullets": ["Simulated"], "style": "int"}, "takeaway": "Learn the method"},
    {"type": "key-message", "message": "Follow-up prevented 6.7 admissions per 100 patients", "support": ["Simulated"]},
    {"type": "references", "title": "References", "items": [
        {"authors": "Doe J, Roe R", "title": "A trial", "journal": "Example J", "year": 2026, "doi": "10.1000/xyz"},
        "A plain reference."]},
    {"type": "closing", "title": "Questions"}]}
for _s in FULL_DECK["slides"]:
    _s["notes"] = "Speaker notes."


def build(spec, d):
    from PIL import Image  # python-pptx depends on Pillow
    Image.new("RGB", (600, 400), "white").save(Path(d) / "fig.png")
    (Path(d) / "deck.json").write_text(json.dumps(spec), encoding="utf-8")
    out = Path(d) / "deck.pptx"
    subprocess.run([sys.executable, str(BUILDER), str(Path(d) / "deck.json"), str(out)], check=True, capture_output=True)
    return out


@unittest.skipUnless(importlib.util.find_spec("pptx"), "needs python-pptx")
class DiagramCornersTest(unittest.TestCase):
    def shapes(self, corners):
        from pptx import Presentation  # type: ignore
        spec = {"slides": [{"type": "diagram", "title": "Schema", "nodes": [
            {"id": "a", "x": 0, "y": 0.2, "w": 0.3, "h": 0.5, "text": "A"},
            {"id": "b", "x": 0.6, "y": 0.2, "w": 0.3, "h": 0.5, "text": "B"}], "edges": [{"from": "a", "to": "b"}]}]}
        if corners:
            spec["theme"] = {"corners": corners}
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "deck.json").write_text(json.dumps(spec), encoding="utf-8")
            out = Path(d) / "deck.pptx"
            subprocess.run([sys.executable, str(BUILDER), str(Path(d) / "deck.json"), str(out)], check=True,
                           capture_output=True)
            slide = Presentation(str(out)).slides[0]
            return [s.auto_shape_type for s in slide.shapes if s.name.startswith("Node")]

    def test_connectors_use_the_left_and_right_sites_of_a_circle(self):
        from pptx import Presentation  # type: ignore
        from pptx.oxml.ns import qn  # type: ignore
        spec = {"slides": [{"type": "diagram", "title": "Schema", "nodes": [
            {"id": "a", "x": 0, "y": 0.4, "w": 0.3, "h": 0.2, "text": "A"},
            {"id": "r", "x": 0.45, "y": 0.4, "w": 0.1, "h": 0.2, "text": "R", "style": "primary", "shape": "circle"},
            {"id": "b", "x": 0.7, "y": 0.4, "w": 0.3, "h": 0.2, "text": "B"}],
            "edges": [{"from": "a", "to": "r"}, {"from": "r", "to": "b"}]}]}
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "deck.json").write_text(json.dumps(spec), encoding="utf-8")
            out = Path(d) / "deck.pptx"
            subprocess.run([sys.executable, str(BUILDER), str(Path(d) / "deck.json"), str(out)], check=True,
                           capture_output=True)
            slide = Presentation(str(out)).slides[0]
            sites = [(c._element.find(".//" + qn("a:stCxn")).get("idx"), c._element.find(".//" + qn("a:endCxn")).get("idx"))
                     for c in slide.shapes if c.shape_type == 5 or c._element.tag.endswith("cxnSp")]
        self.assertEqual(sites, [("3", "2"), ("6", "1")])  # rectangle right -> circle left; circle right -> rectangle left

    def test_square_by_default_rounded_on_request(self):
        from pptx.enum.shapes import MSO_SHAPE  # type: ignore
        self.assertEqual(set(self.shapes(None)), {MSO_SHAPE.RECTANGLE})
        self.assertEqual(set(self.shapes("rounded")), {MSO_SHAPE.ROUNDED_RECTANGLE})


@unittest.skipUnless(importlib.util.find_spec("pptx"), "needs python-pptx")
class SlideTypesTest(unittest.TestCase):
    """A journal-club deck using every slide type builds and passes check_pptx."""

    @classmethod
    def setUpClass(cls):
        from pptx import Presentation  # type: ignore
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = build(FULL_DECK, cls.tmp.name)
        cls.prs = Presentation(str(cls.out))
        cls.names = [{s.name: s for s in slide.shapes} for slide in cls.prs.slides]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_check_pptx_finds_nothing(self):
        res = subprocess.run([sys.executable, str(SCRIPTS / "check_pptx.py"), str(self.out)], capture_output=True,
                             text=True)
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("0 issue(s)", res.stdout)

    def test_title_slide_carries_presenter_affiliation_event_and_date(self):
        text = self.names[0]["Presenter"].text_frame.text
        for part in ("Dr A Presenter", "Cardiology", "Journal club · 22 Nov 2026"):
            self.assertIn(part, text)

    def test_agenda_marks_the_current_part(self):
        bold = [self.names[1][f"Agenda item {i}"].text_frame.paragraphs[0].runs[0].font.bold for i in range(1, 5)]
        self.assertEqual(bold, [False, False, True, False])

    def test_takeaways_and_numbers_with_context(self):
        self.assertEqual(self.names[5]["Takeaway"].text_frame.text, "One admission prevented per 15 patients")
        self.assertIn("95% CI 0.63–0.89", self.names[6]["Label 2"].text_frame.text)
        self.assertIn("Takeaway", self.names[7])

    def test_section_and_key_message_have_no_footer(self):
        for i in (4, 8):
            self.assertNotIn("Page", self.names[i])
        self.assertEqual(self.names[8]["Title"].text_frame.text, FULL_DECK["slides"][8]["message"])

    def test_structured_references(self):
        p = self.names[9]["References"].text_frame.paragraphs[0]
        self.assertEqual(p.text, "1.\tDoe J, Roe R, A trial. Example J 2026. doi:10.1000/xyz")
        self.assertTrue(any(r.font.italic and r.text == "Example J 2026" for r in p.runs))

    def test_lines_have_no_shadow(self):
        from pptx.oxml.ns import qn  # type: ignore
        for slide in self.prs.slides:
            for shp in slide.shapes:
                if shp._element.tag.endswith("cxnSp"):
                    self.assertIsNone(shp._element.find(qn("p:style")), shp.name)


class CheckSpecTest(unittest.TestCase):
    def test_full_deck_meets_the_journal_club_recipe(self):
        self.assertEqual(check_spec.check(FULL_DECK, "journal-club"), [])

    def test_missing_components_fields_and_notes_are_reported(self):
        spec = {"slides": [{"type": "title", "title": "T", "notes": "n"},
                           {"type": "chart", "title": "C", "notes": "n", "chart": "bar", "categories": ["a"],
                            "series": [{"name": "s", "values": [1]}]},
                           {"type": "figure", "title": "F", "image": "x.png"}]}
        kinds = sorted({(f["kind"], f["message"].split(";")[0]) for f in check_spec.check(spec, "journal-club-report")})
        self.assertIn(("missing-field", "figure needs `alt`"), kinds)
        self.assertIn(("no-notes", "no speaker notes"), kinds)
        self.assertIn(("no-source", "chart slide shows data but has no `cite` or `credit`"), kinds)
        missing = {m for k, m in kinds if k == "missing-component"}
        self.assertEqual(missing, {f"journal-club-report: no {c} slide" for c in
                                   ("question", "design", "appraisal", "bottom-line", "references")})


if __name__ == "__main__":
    unittest.main()
