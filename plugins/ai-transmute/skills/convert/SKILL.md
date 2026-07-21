---
name: convert
description: Convert AI skills, commands, hooks, agents, plugins, MCP/LSP configurations, Jupyter notebooks, or hosted AI notebook exports into Codex, Claude, Copilot, Grok, or Gemini formats. Use when a target package and an auditable OKF conversion record are required.
---

# Convert an AI artifact

1. Run `python3 "$PLUGIN_ROOT/scripts/ai_transmute.py" inspect <source> --json` and verify the detected source and inventory.
2. Search `$PLUGIN_ROOT/knowledge` with `okf search` for the source, target, and component types. Read only the winning concepts.
3. Run `python3 "$PLUGIN_ROOT/scripts/ai_transmute.py" plan <source> --target <target>` and explain material approximations before rendering.
4. Run `python3 "$PLUGIN_ROOT/scripts/ai_transmute.py" convert <source> --target <target> [--output <parent>]`.
5. Inspect the generated `report.md`, resolve any actionable manual follow-ups, then run the engine's `validate` command against the job directory.

Never edit the source. Never hide an unsupported feature: record it in both the job OKF bundle and report. Preserve notebook cells and metadata byte-for-byte unless the user explicitly requests a semantic transformation.
