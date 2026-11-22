"""manuscript_to_evidence.py: a manuscript's evidence ledger becomes a talk's claims.json."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT

sys.path.insert(0, str(ROOT / "skills" / "medical-deck" / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "evidence-audit" / "scripts"))
import manuscript_to_evidence as m2e  # noqa: E402
import check_claims  # noqa: E402
from deck_text import html_slides  # noqa: E402

MANUSCRIPT = """# Results

Admissions occurred in 243 of 1,000 patients with the intervention [claim:C001] [evidence:E001].
The rate ratio was 0.75 (95% CI 0.63–0.89) [claim:C002] [evidence:E001]. Follow-up was complete.

# Discussion

Structured follow-up was feasible in routine care [claim:C003] [evidence:E002].
"""
CSV = """claim_id,section,claim_kind,claim_text_sha256,evidence_ids,verification_status,uncertainty,analysis_intent
C001,results,factual,x,E001,verified,not_estimated,confirmatory
C002,results,factual,x,E001,verified,ci_95,confirmatory
C003,discussion,factual,x,E002,unverified,not_estimated,not_applicable
"""
MANIFEST = {"sources": [
    {"evidence_id": "E001", "title": "DEMO-CRS dataset", "authors": [], "year": 2026, "source_type": "dataset",
     "identifiers": {"doi": "", "pmid": "", "pmcid": "", "url": "", "isbn": ""}, "locator": "results.json",
     "verification": {"status": "verified", "source_opened": True}},
    {"evidence_id": "E002", "title": "A feasibility study", "authors": ["Doe J"], "year": 2024, "source_type": "article",
     "identifiers": {"doi": "10.1000/xyz", "pmid": "", "pmcid": "", "url": "", "isbn": ""}, "locator": "[[TODO:x]]",
     "verification": {"status": "unverified", "source_opened": False}}]}


class ManuscriptToEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        (d / "paper.md").write_text(MANUSCRIPT, encoding="utf-8")
        (d / "claims.csv").write_text(CSV, encoding="utf-8")
        (d / "manifest.json").write_text(json.dumps(MANIFEST), encoding="utf-8")
        self.d = d
        with contextlib.redirect_stdout(io.StringIO()):
            self.rc = m2e.main([str(d / "paper.md"), str(d / "claims.csv"), str(d / "manifest.json"),
                                "--out", str(d / "evidence")])
        self.claims = json.loads((d / "evidence" / "claims.json").read_text(encoding="utf-8"))["claims"]
        self.refs = json.loads((d / "evidence" / "references.json").read_text(encoding="utf-8"))["references"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_claims_carry_the_papers_numbers_quote_and_status(self):
        self.assertEqual(self.rc, 0)
        by_id = {c["id"]: c for c in self.claims}
        self.assertEqual(by_id["c001"]["values"], ["243", "1,000"])
        self.assertEqual(by_id["c002"]["values"], ["0.75", "95%", "0.63", "0.89"])
        self.assertNotIn("[claim", by_id["c002"]["quote"])
        self.assertEqual(by_id["c001"]["status"], "verified-fulltext")
        self.assertEqual(by_id["c003"]["status"], "unverified")
        self.assertTrue(by_id["c001"]["locator"].startswith("manuscript, Results"))
        self.assertEqual({r["id"] for r in self.refs}, {"E001", "E002"})

    def test_a_slide_with_the_papers_numbers_passes_and_a_new_number_fails(self):
        for c in self.claims:
            c["slide"] = 1
        good = html_slides('<section class="slide"><h2>Rate ratio 0.75 (95% CI 0.63–0.89)</h2></section>')
        bad = html_slides('<section class="slide"><h2>Rate ratio 0.71</h2></section>')
        self.assertEqual(check_claims.slide_findings(good, self.claims), [])
        self.assertEqual([k for k, _ in check_claims.slide_findings(bad, self.claims)], ["UNSUPPORTED"])

    def test_unknown_claim_id_is_reported(self):
        (self.d / "paper.md").write_text("# Results\n\nRate 5% [claim:C009] [evidence:E001].\n", encoding="utf-8")
        refs, claims, problems = m2e.convert(self.d / "paper.md", self.d / "claims.csv", self.d / "manifest.json")
        self.assertEqual(claims["claims"], [])
        self.assertTrue(any("C009" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
