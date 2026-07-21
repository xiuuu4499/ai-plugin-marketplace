---
name: implement
description: Scaffold and implement a Codex plugin from an explicitly approved AI Scholar design. Use only after the user has approved the design and the research job records approved state; reject attempts to implement an unapproved design.
---

# Implement the approved design

Verify the hard gate before creating or editing a package:

`python3 "$PLUGIN_ROOT/scripts/ai_scholar.py" gate <job> implement --json`

If it fails, stop and return to `$review`; do not make an exception. Implement only the approved interfaces and update the job's traceability/report when a design decision changes. Use the plugin-creator workflow to scaffold any new plugin package, preserve marketplace ordering, and update the target marketplace, README, tests, and installation instructions.

Run package and job validation before advancing the job from `approved` to `implemented`. Route final checks to `$validate`.
