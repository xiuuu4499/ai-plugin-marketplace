from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ai_transmute", PLUGIN / "scripts" / "ai_transmute.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(mod)


class AITransmuteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "sample"
        (self.source / ".claude-plugin").mkdir(parents=True)
        (self.source / "skills" / "hello").mkdir(parents=True)
        (self.source / "commands").mkdir()
        (self.source / "hooks" / "scripts").mkdir(parents=True)
        (self.source / "agents").mkdir()
        (self.source / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "sample", "version": "1.0.0", "description": "Sample plugin"}), encoding="utf-8"
        )
        (self.source / "skills" / "hello" / "SKILL.md").write_text(
            "---\nname: hello\ndescription: Say hello.\n---\n\nSay hello.\n", encoding="utf-8"
        )
        (self.source / "commands" / "deploy.md").write_text("Deploy $ARGUMENTS safely.\n", encoding="utf-8")
        (self.source / "agents" / "reviewer.agent.md").write_text("Review changes.\n", encoding="utf-8")
        (self.source / "hooks" / "hooks.json").write_text(
            json.dumps({"hooks": {"PostToolUse": [{"matcher": "Edit", "hooks": [{"type": "command", "command": "true"}]}]}}),
            encoding="utf-8",
        )
        (self.source / "hooks" / "scripts" / "check.py").write_text("print('{}')\n", encoding="utf-8")
        (self.source / ".mcp.json").write_text(json.dumps({"demo": {"command": "demo-mcp"}}), encoding="utf-8")
        (self.source / "lsp.json").write_text(json.dumps({"python": {"command": "pylsp"}}), encoding="utf-8")
        notebook = {
            "cells": [{"cell_type": "markdown", "metadata": {}, "source": ["Prompt"]}],
            "metadata": {"kernelspec": {"name": "python3"}}, "nbformat": 4, "nbformat_minor": 5,
        }
        (self.source / "workflow.ipynb").write_text(json.dumps(notebook, separators=(",", ":")), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def digest(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_inspect_detects_claude_components(self):
        result = mod.inspect_source(str(self.source))
        self.assertEqual(result["platform"], "claude")
        for kind in ("plugin", "skill", "command", "hook", "agent", "mcp", "lsp", "jupyter-notebook"):
            self.assertIn(kind, result["kinds"])
        self.assertEqual(result["notebooks"][0]["cells"], 1)

    def test_plan_reports_target_gaps(self):
        result = mod.plan_conversion(mod.inspect_source(str(self.source)), "codex")
        self.assertTrue(any(item["kind"] == "lsp" for item in result["losses"]))
        self.assertTrue(any(item["kind"] == "command" for item in result["approximations"]))

    def test_convert_all_targets_and_preserve_source(self):
        source_hash = self.digest(self.source / "workflow.ipynb")
        manifests = {
            "codex": Path("package/.codex-plugin/plugin.json"),
            "claude": Path("package/.claude-plugin/plugin.json"),
            "copilot": Path("package/plugin.json"),
            "grok": Path("package/.claude-plugin/plugin.json"),
            "gemini": Path("package/gemini-extension.json"),
        }
        for target, manifest in manifests.items():
            with self.subTest(target=target):
                result = mod.convert(str(self.source), target, str(self.root / "outputs"))
                job = Path(result["job"])
                self.assertTrue((job / manifest).is_file())
                self.assertTrue((job / "okf" / "index.md").is_file())
                self.assertTrue((job / "report.md").is_file())
                self.assertTrue((job / "job.json").is_file())
                self.assertEqual(self.digest(job / "package" / "notebooks" / "workflow.ipynb"), source_hash)
        self.assertEqual(self.digest(self.source / "workflow.ipynb"), source_hash)

    def test_extract_is_collision_safe(self):
        result = mod.extract(str(self.source), "skill,hook", str(self.root / "extracts"))
        self.assertTrue(Path(result["output"]).is_dir())
        with self.assertRaises(FileExistsError):
            mod.extract(str(self.source), "skill", str(self.root / "extracts"))

    def test_diff_reports_component_change(self):
        other = self.root / "other"
        other.mkdir()
        (other / "SKILL.md").write_text("---\nname: x\ndescription: X.\n---\n", encoding="utf-8")
        result = mod.diff_artifacts(str(self.source), str(other))
        self.assertIn("plugin", result["missing_on_right"])

    def test_advisory_hook_is_fail_open(self):
        event = json.dumps({"session_id": "test", "tool_input": {"file_path": str(self.source / "unknown.txt")}})
        env = dict(os.environ, PLUGIN_ROOT=str(PLUGIN))
        proc = subprocess.run(
            [sys.executable, str(PLUGIN / "hooks" / "curate.py")], input=event,
            capture_output=True, text=True, env=env, check=False,
        )
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
