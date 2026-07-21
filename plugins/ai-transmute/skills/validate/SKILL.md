---
name: validate
description: Validate AI Transmute conversion jobs, OKF bundles, and Codex, Claude, Copilot, Grok, Gemini, skill, hook, plugin, or notebook artifacts. Use before delivery or when diagnosing malformed manifests, missing components, broken links, or incomplete audit reports.
---

# Validate an artifact

Run `python3 "$PLUGIN_ROOT/scripts/ai_transmute.py" validate <path> [--target <target>] --json`.

For an OKF bundle, also run `okf validate`, `okf lint`, and `okf loose`. For a generated job, require `package/`, `okf/`, `report.md`, and `job.json`; validate the target package and confirm every approximation or omission is present in the report. Native validators are supplemental and must not replace internal checks.
