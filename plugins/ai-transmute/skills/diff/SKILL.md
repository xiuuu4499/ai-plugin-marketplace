---
name: diff
description: Compare the behavior and structure of two AI artifacts or a source artifact and generated conversion job. Use to verify round trips, find dropped components, distinguish semantic changes from formatting changes, or audit a conversion's loss report.
---

# Diff AI artifacts

Run `python3 "$PLUGIN_ROOT/scripts/ai_transmute.py" diff <source> <target> --json`.

Compare component inventories, invocation behavior, hooks, dependencies, tool configuration, notebook cells, and platform-only features. Treat renamed or relocated equivalent components as mappings, not losses. Ensure unexplained missing behavior is added to the job report before completion.
