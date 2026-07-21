---
name: extract
description: Extract selected skills, commands, hooks, agents, notebooks, MCP/LSP configurations, or metadata from an AI plugin or artifact collection. Use when reusable components are needed without converting the whole package, or when a larger plugin should be extrapolated from a smaller asset.
---

# Extract AI assets

Inspect first with `python3 "$PLUGIN_ROOT/scripts/ai_transmute.py" inspect <source> --json`.

For a subset, run:

`python3 "$PLUGIN_ROOT/scripts/ai_transmute.py" extract <source> --select <comma-separated-kinds> [--output <directory>]`

For extrapolation, extract the seed component, model the inferred package boundaries in a job OKF bundle, and use `$convert` for the requested target. Label inferred metadata and behavior as approximations; do not present them as source facts.
