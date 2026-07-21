---
name: plan
description: Produce a read-only mapping and loss forecast for converting an AI artifact to Codex, Claude, Copilot, Grok, or Gemini. Use when the user wants to review feasibility, equivalences, unsupported features, or expected output before files are generated.
---

# Plan an AI conversion

Run `python3 "$PLUGIN_ROOT/scripts/ai_transmute.py" plan <source> --target <target> --json`.

Enrich the deterministic result with only the relevant OKF platform, component, and mapping concepts. Separate exact mappings, safe approximations, unsupported features, and manual target setup. Planning is read-only and must not create output directories.
