---
name: plan-mode
description: Create or update a Codex Plan-mode plan that is tied to an AI Scholar research job and routes each phase to the correct AI Scholar skill. Use when planning deep subject research, an AI Scholar plugin design, a human review gate, implementation, validation, or maintenance work.
---

# Plan an AI Scholar workflow

When Codex is in Plan mode, create and maintain the working plan through Codex's plan-management tool. Make every plan item correspond to the current AI Scholar job state and its next named skill; do not create a parallel planning document unless the research job itself requires an artifact.

Use Plan mode to organize work; do not mutate job state, create a package, or edit a marketplace merely because the plan contains those steps. First identify the AI Scholar job, if one exists, and read its state:

`python3 "$PLUGIN_ROOT/scripts/ai_scholar.py" status <job> --json`

If no job exists, make initialization through `$study` the first plan step. State the topic, user outcome, intended audience, source constraints, and the planned job location before proposing research.

## Route the plan by job state

| Job state | Next skill | Plan outcome |
| --- | --- | --- |
| No job or `initialized` | `$study` | Research contract and job in `sourcing`. |
| `sourcing` | `$sources` | Ranked retained sources, discarded-source record, conflict/uncertainty/special-case ledgers, then `triaged`. |
| `triaged` | `$knowledge` | Cited, curated OKF concepts imported in priority order, then `curated`. |
| `curated` or incomplete `design-draft` | `$architect` | Evidence-traceable interface, package tree, acceptance tests, and review packet. |
| `review` | `$review` | Explicit human approval, requested changes, or rejection. |
| `approved` | `$implement` | Approved package implementation and marketplace/docs/test updates. |
| `implemented` | `$validate` | Job, OKF, plugin, and test validation, then `validated`. |
| `validated` | `$validate` | Local-test handoff plan, then `handoff-ready`. |
| `handoff-ready` | `$maintain` only when needed | Incremental source-drift or design-impact work. |
| `rejected` | `$architect` | Revised design before another `$review`. |

## Required plan shape

For every plan step, name the AI Scholar skill, expected state transition, job artifacts to read or create, evidence or user input required, and validation command. Include a separate **Human decision** step whenever the flow reaches `$review`; mark implementation as blocked until that step is explicitly approved.

Keep research, knowledge curation, design, approval, implementation, and handoff as separate steps. Do not collapse them into a generic “build plugin” task. List source gaps, conflicts, and special cases as explicit follow-up steps, not footnotes.

Before an implementation step, include `python3 "$PLUGIN_ROOT/scripts/ai_scholar.py" gate <job> implement --json`; if it cannot pass, the plan must return to `$review` rather than scheduling implementation. End with the relevant `$validate` checks and brief local install/reload instructions.
