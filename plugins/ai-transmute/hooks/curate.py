#!/usr/bin/env python3
"""Fail-open advisory hook for OKF bundles and AI Transmute jobs."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


MAX_LINES = 12


def truthy(name: str) -> bool:
    value = os.environ.get(name, "").strip().lower()
    return bool(value and value not in {"0", "false", "no", "off"})


def edited_path(event: dict) -> Path | None:
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    value = tool_input.get("file_path") or tool_input.get("path")
    return Path(value).expanduser().resolve() if isinstance(value, str) else None


def suppressed(path: Path) -> bool:
    try:
        return path.is_file() and "okf-disable" in path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False


def walk_up(path: Path):
    current = path.parent if path.suffix else path
    while True:
        yield current
        if current.parent == current:
            return
        current = current.parent


def is_okf_root(path: Path) -> bool:
    index = path / "index.md"
    if not index.is_file():
        return False
    try:
        return "okf_version" in index.read_text(encoding="utf-8", errors="ignore")[:512]
    except OSError:
        return False


def run(command: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
        return proc.returncode, (proc.stdout or proc.stderr).strip()
    except (OSError, subprocess.SubprocessError):
        return 0, ""


def context_for(path: Path) -> str | None:
    for parent in walk_up(path):
        if (parent / "job.json").is_file():
            root = os.environ.get("PLUGIN_ROOT") or os.environ.get("CLAUDE_PLUGIN_ROOT")
            if not root:
                return None
            code, output = run([sys.executable, str(Path(root) / "scripts" / "ai_transmute.py"), "validate", str(parent), "--json"])
            if code or '"valid": false' in output.lower():
                return "AI Transmute validation:\n" + "\n".join(output.splitlines()[:MAX_LINES])
            return None
        if is_okf_root(parent):
            messages = []
            for verb in ("validate", "lint"):
                code, output = run(["okf", verb, str(parent), "--json"])
                if code or (output and '"findings":[]' not in output.replace(" ", "")):
                    messages.extend(output.splitlines())
            if messages:
                return "OKF curation advisory:\n" + "\n".join(messages[:MAX_LINES])
            return None
    return None


def main() -> int:
    try:
        if truthy("AI_TRANSMUTE_HOOK_DISABLED"):
            return 0
        event = json.load(sys.stdin)
        path = edited_path(event)
        if path is None or suppressed(path):
            return 0
        context = context_for(path)
        if context:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
