---
name: review
description: Present and record the mandatory human design review for an AI Scholar plugin job. Use when a plugin design is ready for approval, the user gives design feedback, or implementation must be gated on an explicit human decision.
---

# Review the design

Always present the projected user interface: skills, CLI/scripts, hooks, commands, apps/MCP, and deliberately excluded surfaces. Also present source coverage and discarded-source summary, evidence traceability, conflicts, uncertainties, special cases, package tree, acceptance tests, and marketplace/docs changes.

Ask for an explicit decision. Questions and requested changes are not approval. Record the decision only after the user states it:

`python3 "$PLUGIN_ROOT/scripts/ai_scholar.py" record-review <job> --decision approved|changes-requested|rejected --reviewer "<reviewer>" --notes "<notes>" --json`

For changes requested, return to `$architect`. For approval, hand off to `$implement`. Never infer approval from silence, positive sentiment, or permission to continue researching.
