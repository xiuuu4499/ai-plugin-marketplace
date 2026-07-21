---
name: architect
description: Design a Codex plugin interface from a curated AI Scholar knowledge bundle. Use when the research job is curated and a user needs a traceable plan for skills, scripts, hooks, commands, apps, MCP, package structure, and acceptance tests.
---

# Architect the plugin

Read the curated knowledge, source gaps, special cases, conflicts, and uncertainty ledger. Advance to `design-draft` before writing the design.

Write `design/interface.md` with the projected user interface first: each skill's trigger, input, output, state requirement, and failure behavior; every script/command's inputs and deterministic guarantees; every hook's matcher, scope, and fail-open/fail-closed choice; and an explicit decision for apps/MCP or their omission.

Add a requirements-to-evidence traceability matrix, package tree, acceptance tests, marketplace/README changes, security/privacy implications, and open questions. Every public capability must trace to a cited requirement or say `Design decision` with its rationale. Do not add a surface merely because the source plugin had one.

Advance to review when the packet is complete:

`python3 "$PLUGIN_ROOT/scripts/ai_scholar.py" advance <job> --to review --note "Design packet ready for human review." --json`

Route approval to `$review`; do not implement here.
