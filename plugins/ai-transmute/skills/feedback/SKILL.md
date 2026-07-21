---
name: feedback
description: Apply corrections to AI Transmute's format knowledge, conversion mappings, renderer behavior, or a generated conversion job. Use when a conversion is inaccurate, lossy in an avoidable way, outdated, or missing a target feature.
---

# Apply conversion feedback

Classify feedback as format fact, mapping policy, renderer defect, or job-specific preference.

- Update the persistent OKF catalog only for durable facts or policies, with citations and a log entry.
- Update only the job bundle for source-specific preferences.
- Patch deterministic rendering code when repeated output is wrong; add a regression fixture.
- Regenerate into a new job directory unless the user explicitly authorizes editing the existing output.

Run OKF curation, engine tests, `$validate`, and `$diff` for every affected target.
