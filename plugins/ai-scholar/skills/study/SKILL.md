---
name: study
description: Start an evidence-led AI Scholar research job for a subject area that should become a high-quality Codex plugin. Use when a user asks to deeply learn a topic, research before designing a plugin, or establish a source-quality and approval workflow.
---

# Start a research job

Clarify the subject, desired user outcome, target audience, scope limits, and whether any source classes are required or prohibited. Separate facts to learn from assumptions about the eventual plugin.

Initialize a job with:

`python3 "$PLUGIN_ROOT/scripts/ai_scholar.py" init "<topic>" --output <parent> --goal "<goal>" --audience "<audience>" --json`

Review the generated research contract and source ledgers with the user, then advance it to sourcing:

`python3 "$PLUGIN_ROOT/scripts/ai_scholar.py" advance <job> --to sourcing --note "Research contract accepted." --json`

Do not design an interface or create a package in this skill. Route source work to `$sources`.
