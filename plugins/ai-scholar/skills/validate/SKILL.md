---
name: validate
description: Validate AI Scholar research jobs and their resulting Codex plugins. Use before design approval, implementation handoff, local testing, or when a job has missing evidence, broken OKF curation, inconsistent state, or package-validation failures.
---

# Validate a job

Run the deterministic contract check first:

`python3 "$PLUGIN_ROOT/scripts/ai_scholar.py" verify <job> --json`

For knowledge, run `okf validate`, `okf lint`, and `okf loose` against `<job>/knowledge`; judge citations, contradictions, uncertainty, and source coverage semantically after the mechanical checks. For an approved implementation, validate the package with plugin-creator and skill-creator validators, run its tests, and check that every public capability appears in both the interface design and traceability matrix.

Report failures by phase and do not advance the job until the applicable gate is clean. Only transition `implemented` to `validated` after all required checks pass.
