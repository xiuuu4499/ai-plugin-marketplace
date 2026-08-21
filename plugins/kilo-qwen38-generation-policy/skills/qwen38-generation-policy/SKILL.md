---
name: qwen38-generation-policy
description: Select and explain Qwen3.8 generation profiles for subsequent model invocations, delegated subagents, chat sessions, coding/planning, long-form prose, and image/video prompt construction. Use when choosing thinking vs non-thinking mode, reasoning effort, or sampling settings for Qwen3.8. Do not claim to change parameters of an inference that is already running.
---

# Qwen3.8 Generation Policy

Use this skill to choose a generation profile for a subsequent Qwen3.8 request or delegated subagent. The canonical profiles and parameters are in `profiles.yaml`.

## Core Rule

Never rely on backend or frontend sampler defaults for managed parameters. Resolve the selected profile to explicit request values.

Managed parameters:

- thinking enabled/disabled
- reasoning effort
- preserve thinking
- temperature
- top_p
- top_k
- min_p
- presence_penalty
- frequency_penalty
- repetition_penalty

Do not change sampler values merely because generic LLM folklore suggests it. Start from the Qwen3.8 official thinking or instruct baseline. Only use a documented profile override.

## Execution Constraint

This skill cannot retroactively change the parameters of the inference that is currently reading it.

Use it for delegated subagents, tool-triggered downstream requests, the next request, or explaining which profile should be selected. The Kilo plugin is the enforcement layer that changes request parameters before inference starts.

## Selection Procedure

1. Honor an explicit caller/user profile request first.
2. Classify the intended downstream task.
3. Decide whether hidden reasoning is useful.
4. If thinking is enabled, choose `low`, `medium`, or `xhigh`.
5. Select the closest named profile from `profiles.yaml`.
6. Apply the profile exactly.
7. Do not make ad-hoc sampler changes unless the caller explicitly asks for an experiment.

## Task Guidance

Use `coding-plan-xhigh` for architecture, implementation planning, ambiguous debugging, repo-wide changes, multi-file refactors, and verification strategy.

Use `coding-agent-xhigh` for substantial implementation work. Use `coding-agent-medium` only for clearly bounded, routine implementation where lower latency is worth the tradeoff.

Use `chat-direct` for ordinary conversation and straightforward Q&A. Use `chat-reasoning-medium` for nontrivial analysis, comparison, synthesis, or decisions. Use `chat-reasoning-xhigh` for unusually complex analytical work.

Use `prose-plan-medium` for story planning, continuity, and constraint reconciliation. Use `prose-write-direct` for the actual long-form prose pass.

Use `media-prompt-direct` for straightforward prompt construction. Use `media-prompt-reasoning-medium` when references, camera motion, subject identity, timing, or conflicting visual constraints must be reconciled before the final prompt.

## Reasoning Effort

When thinking is enabled:

- `low`: mechanical reasoning, quick verification, very bounded decisions.
- `medium`: normal nontrivial analysis; preferred adaptive default.
- `xhigh`: difficult planning, complex coding, ambiguous debugging, high-branching decisions.

Prefer changing `reasoning_effort` before changing sampling parameters.

## Session Overrides In Kilo

The installed Kilo plugin supports these slash commands for future requests in the same session:

- `/qwen-profile <profile>`
- `/qwen38-profile <profile>`
- `/qwen-policy-profile <profile>`
- `/qwen-profile reset`

Use `reset`, `auto`, or `default` to return to automatic agent defaults.
