---
name: doctor
description: Diagnose AI Transmute's local environment, including Python, OKF, Codex, Claude, Copilot, Grok, Gemini, Ruby, and native validator availability. Use when setup, conversion, hook execution, or target validation fails.
---

# Diagnose AI Transmute

Run `python3 "$PLUGIN_ROOT/scripts/ai_transmute.py" doctor --json`.

Distinguish required dependencies (`python3`; `okf` for audited conversions) from optional native target CLIs. Report missing tools without installing them automatically. If OKF is missing, route setup through the bundled OKF doctor workflow.
