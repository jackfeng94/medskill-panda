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

    def test_rounded_by_default_square_on_request(self):
        from pptx.enum.shapes import MSO_SHAPE  # type: ignore
        self.assertEqual(set(self.shapes(None)), {MSO_SHAPE.ROUNDED_RECTANGLE})
        self.assertEqual(set(self.shapes("square")), {MSO_SHAPE.RECTANGLE})


if __name__ == "__main__":
    unittest.main()
