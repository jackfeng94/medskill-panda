"""pptx_from_spec.py: diagram corner style."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT

BUILDER = ROOT / "skills" / "pptx-deck-building" / "scripts" / "pptx_from_spec.py"


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


if __name__ == "__main__":
    unittest.main()
