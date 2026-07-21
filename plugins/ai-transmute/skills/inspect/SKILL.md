---
name: inspect
description: Read-only detection and inventory of AI skills, commands, hooks, agents, plugins, notebooks, instruction files, MCP/LSP configurations, and related packages. Use to identify a source platform, component boundaries, dependencies, or portability hazards before conversion.
---

# Inspect an AI artifact

Run `python3 "$PLUGIN_ROOT/scripts/ai_transmute.py" inspect <source> --json`.

Report the detected platform, artifact kinds, manifests, component counts, notebook characteristics, external commands, and ambiguous signals. If the platform cannot be determined, say `generic` and present the evidence; do not guess a vendor.

This workflow must not write to the source or create a conversion job.
