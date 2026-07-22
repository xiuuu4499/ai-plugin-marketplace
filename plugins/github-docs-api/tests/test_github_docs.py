"""Tests for the github_docs script (offline, no network calls)."""

from __future__ import annotations

import importlib.util
import io
import json
import re
import textwrap
import unittest
import unittest.mock
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "github_docs", PLUGIN / "scripts" / "github_docs.py"
)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(mod)


class SearchParamTests(unittest.TestCase):
    """Verify that search() builds the correct URL and passes parameters."""

    def _mock_response(self, payload: dict):
        raw = json.dumps(payload).encode()
        return unittest.mock.patch.object(mod, "_get_json", return_value=payload)

    def test_search_calls_correct_url(self):
        captured: list[str] = []

        def fake_get_json(url: str):
            captured.append(url)
            return {"meta": {}, "hits": []}

        with unittest.mock.patch.object(mod, "_get_json", side_effect=fake_get_json):
            mod.search("actions rate limit", size=5)

        self.assertEqual(len(captured), 1)
        url = captured[0]
        self.assertIn("/api/search/v1", url)
        self.assertIn("query=actions+rate+limit", url.replace("%20", "+").replace("%2B", "+"))
        self.assertIn("size=5", url)
        self.assertIn("client_name=", url)

    def test_search_passes_version_and_language(self):
        captured: list[str] = []

        def fake_get_json(url: str):
            captured.append(url)
            return {"meta": {}, "hits": []}

        with unittest.mock.patch.object(mod, "_get_json", side_effect=fake_get_json):
            mod.search("pull request", version="enterprise-cloud", language="ja")

        url = captured[0]
        self.assertIn("version=enterprise-cloud", url)
        self.assertIn("language=ja", url)


class FetchBodyTests(unittest.TestCase):
    """Verify fetch_body() uses the correct endpoint and returns text."""

    def test_fetch_body_url(self):
        captured: list[str] = []

        def fake_get_text(url: str) -> str:
            captured.append(url)
            return "# Hello"

        with unittest.mock.patch.object(mod, "_get_text", side_effect=fake_get_text):
            result = mod.fetch_body("/en/actions/overview")

        self.assertEqual(result, "# Hello")
        self.assertIn("/api/article/body", captured[0])
        self.assertIn("pathname=%2Fen%2Factions%2Foverview", captured[0])


class PagelistTests(unittest.TestCase):
    """Verify pagelist parsing and filtering."""

    SAMPLE = textwrap.dedent("""\
        /en
        /en/actions
        /en/actions/overview
        /en/copilot/overview
        /en/copilot/actions-integration
        /en/rest/actions/artifacts
    """)

    def _get_pagelist(self, lang="en", version="free-pro-team@latest"):
        with unittest.mock.patch.object(mod, "_get_text", return_value=self.SAMPLE):
            return mod.get_pagelist(lang=lang, version=version)

    def test_pagelist_returns_non_empty_lines(self):
        paths = self._get_pagelist()
        self.assertTrue(len(paths) > 0)
        for p in paths:
            self.assertTrue(p.strip(), "Empty path in pagelist")

    def test_pagelist_filter_whole_word(self):
        paths = self._get_pagelist()
        # Filter for "actions" — should NOT match "actions-integration"
        pattern = re.compile(r"(?i)(^|/)actions(/|$)")
        filtered = [p for p in paths if pattern.search(p)]
        matched_paths = "\n".join(filtered)
        self.assertIn("/en/actions", matched_paths)
        self.assertIn("/en/actions/overview", matched_paths)
        self.assertNotIn("actions-integration", matched_paths)

    def test_pagelist_filter_does_not_match_superset(self):
        paths = self._get_pagelist()
        pattern = re.compile(r"(?i)(^|/)rest(/|$)")
        filtered = [p for p in paths if pattern.search(p)]
        # /en/rest/actions/artifacts should match
        self.assertTrue(any("rest" in p for p in filtered))
        # /en/actions should NOT appear
        self.assertNotIn("/en/actions", filtered)


class ValidateKnowledgeTests(unittest.TestCase):
    """Verify validate_knowledge() checks index references."""

    def _make_knowledge(self, tmp_path: Path, index_extra: str = "") -> Path:
        knowledge = tmp_path / "knowledge"
        knowledge.mkdir()
        apis = knowledge / "apis"
        apis.mkdir()
        (apis / "overview.md").write_text("# Overview\n", encoding="utf-8")
        (knowledge / "index.md").write_text(
            "# Index\n\n"
            "[Overview](apis/overview.md)\n"
            + index_extra,
            encoding="utf-8",
        )
        return knowledge

    def test_valid_knowledge_passes(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            knowledge = self._make_knowledge(Path(tmp))
            self.assertTrue(mod.validate_knowledge(knowledge))

    def test_missing_concept_file_fails(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            knowledge = self._make_knowledge(Path(tmp), "[Missing](apis/missing.md)\n")
            self.assertFalse(mod.validate_knowledge(knowledge))

    def test_missing_index_fails(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            knowledge = Path(tmp) / "knowledge"
            knowledge.mkdir()
            self.assertFalse(mod.validate_knowledge(knowledge))


class PluginKnowledgeIntegrityTest(unittest.TestCase):
    """Ensure the bundled knowledge/ directory passes validate_knowledge()."""

    def test_bundled_knowledge_is_valid(self):
        knowledge_root = PLUGIN / "knowledge"
        self.assertTrue(
            mod.validate_knowledge(knowledge_root),
            "Bundled knowledge/ directory failed validation — check index.md references.",
        )


if __name__ == "__main__":
    unittest.main()
