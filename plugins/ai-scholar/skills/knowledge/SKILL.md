---
name: knowledge
description: Build and curate a cited OKF knowledge bundle from retained AI Scholar sources. Use after source triage, when importing a source, or when evidence must be transformed into durable, navigable concepts before plugin architecture.
---

# Build knowledge

Use the `knowledge/` directory as the research job's OKF bundle. Read its index and log before editing.

Process retained sources in priority order. Use the OKF migrate workflow when a local source body must remain verbatim; use OKF produce for concise, cited concepts distilled from documentation. Treat one independently linkable fact, rule, or decision as one concept. Label sourced fact, cross-source inference, and proposed design decision distinctly.

After each source import, update indexes and log, then run:

`okf validate <job>/knowledge --json`

`okf lint <job>/knowledge --json`

`okf loose <job>/knowledge --json`

Resolve structural issues immediately and record semantic uncertainty rather than fabricating certainty. After all retained sources are processed, perform tag and semantic-consistency review, then advance:

`python3 "$PLUGIN_ROOT/scripts/ai_scholar.py" advance <job> --to curated --note "Retained sources imported and curated." --json`

Route interface design to `$architect`.
