#!/usr/bin/env python3
"""Fail-open advisory checks for AI Scholar research jobs."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def edited_path(event: dict) -> Path | None:
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    value = tool_input.get("file_path") or tool_input.get("path")
    return Path(value).resolve() if isinstance(value, str) else None


def job_root(path: Path) -> Path | None:
    current = path.parent
    while current != current.parent:
        if (current / "job.json").is_file():
            return current
        current = current.parent
    return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
        path = edited_path(event)
        root = job_root(path) if path else None
        plugin_root = os.environ.get("PLUGIN_ROOT") or os.environ.get("CLAUDE_PLUGIN_ROOT")
        if not root or not plugin_root:
            return 0
        proc = subprocess.run(
            [sys.executable, str(Path(plugin_root) / "scripts" / "ai_scholar.py"), "verify", str(root), "--json"],
            capture_output=True, text=True, timeout=15, check=False,
        )
        result = json.loads(proc.stdout) if proc.stdout else {"valid": True}
        messages = list(result.get("errors", []))[:8]
        if "package" in path.parts:
            review = json.loads((root / "job.json").read_text(encoding="utf-8")).get("review", {})
            if review.get("decision") != "approved":
                messages.append("Package edited before explicit design approval; the implementation gate will reject it.")
        if messages:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "AI Scholar advisory:\n" + "\n".join(messages)}}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
