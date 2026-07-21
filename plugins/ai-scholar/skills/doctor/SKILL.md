---
name: doctor
description: Diagnose AI Scholar local dependencies and research-job validation failures. Use when job initialization, state gates, OKF curation, advisory hooks, plugin validation, or local test instructions fail.
---

# Diagnose AI Scholar

Run `python3 --version`, `okf --help`, and `codex --version` as needed; report each required or optional tool separately. Verify the job path with:

`python3 "$PLUGIN_ROOT/scripts/ai_scholar.py" verify <job> --json`

Diagnose missing artifacts and invalid state before changing content. Do not install tools automatically; explain the missing dependency and route OKF setup through its doctor workflow when appropriate.
