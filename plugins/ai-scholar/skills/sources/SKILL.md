---
name: sources
description: Collect, deduplicate, prioritize, and audit sources for an AI Scholar research job. Use when a subject needs authoritative evidence, competing sources must be assessed, or a research job is in sourcing or triaged state.
---

# Curate sources

Read the job's source registry and ledgers before collecting material. Prefer primary/official documentation; add independent sources only where they cover distinct claims, implementation realities, or unresolved questions.

For every candidate, record canonical URL, publisher, source class, publication/update date when available, access date, claims covered, duplicate group, disposition, and rationale. Never discard a source silently: place deferred or excluded material in `sources/discarded.md` with its review reason.

Rank retained sources by authority, direct relevance, unique coverage, specificity, and recency. Do not meet an arbitrary source count when coverage is already sufficient. Put exceptions in `special-cases.md`, conflicts in `conflicts.md`, and unresolved claims in `uncertainties.md`.

Before advancing from sourcing to triaged, present the retained-source list, discarded-source summary, gaps, conflicts, and priority order. Advance only after that review:

`python3 "$PLUGIN_ROOT/scripts/ai_scholar.py" advance <job> --to triaged --note "Source set reviewed and prioritized." --json`

Route retained material to `$knowledge`.
