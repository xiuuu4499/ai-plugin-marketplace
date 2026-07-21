from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ai_scholar", PLUGIN / "scripts" / "ai_scholar.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(mod)


class AIScholarTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.result = mod.init_job("Observability systems", str(self.root), "Design a plugin", "Platform engineers")
        self.job_root, self.job = mod.read_job(self.result["job"])

    def tearDown(self):
        self.tmp.cleanup()

    def refresh(self):
        self.job_root, self.job = mod.read_job(str(self.job_root))

    def test_new_job_is_complete_and_unapproved(self):
        result = mod.verify(self.job_root, self.job)
        self.assertTrue(result["valid"])
        blocked = mod.gate(self.job_root, self.job, "implement")
        self.assertFalse(blocked["valid"])
        self.assertIn("explicitly approved", " ".join(blocked["errors"]))

    def test_explicit_review_opens_implementation_gate(self):
        for state in ("sourcing", "triaged", "curated", "design-draft", "review"):
            mod.transition(self.job_root, self.job, state, "test")
            self.refresh()
        reviewed = mod.record_review(self.job_root, self.job, "approved", "Test reviewer", "Approved for implementation.")
        self.assertEqual(reviewed["state"], "approved")
        self.refresh()
        self.assertTrue(mod.gate(self.job_root, self.job, "implement")["valid"])
        self.assertIn("Status: approved", (self.job_root / "design" / "approval.md").read_text(encoding="utf-8"))

    def test_review_changes_return_to_design_draft(self):
        for state in ("sourcing", "triaged", "curated", "design-draft", "review"):
            mod.transition(self.job_root, self.job, state, "test")
            self.refresh()
        result = mod.record_review(self.job_root, self.job, "changes-requested", "Test reviewer", "Add an interface example.")
        self.assertEqual(result["state"], "design-draft")
        self.refresh()
        self.assertFalse(mod.gate(self.job_root, self.job, "implement")["valid"])


if __name__ == "__main__":
    unittest.main()
