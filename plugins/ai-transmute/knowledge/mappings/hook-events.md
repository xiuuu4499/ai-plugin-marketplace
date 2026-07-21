---
type: Conversion Mapping
title: Hook event mapping
description: Map lifecycle intent while preserving platform-specific payload and control semantics.
tags: [hooks, mapping, fidelity]
timestamp: 2026-07-21T00:00:00Z
---

Claude-family `PreToolUse`/`PostToolUse`, Copilot `preToolUse`/`postToolUse`, and Gemini `BeforeTool`/`AfterTool` are related but not identical. Translate the event name, then audit [hook](/components/hooks-triggers.md) matchers, output JSON, exit behavior, and trust separately. Never infer permission grants from name similarity.
