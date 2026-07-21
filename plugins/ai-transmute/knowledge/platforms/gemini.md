---
type: AI Platform Format
title: Gemini CLI extensions
description: Gemini extensions use gemini-extension.json with skills, TOML commands, hooks, agents, policies, settings, and optional MCP servers.
tags: [gemini, extension, agent-skills]
timestamp: 2026-07-21T00:00:00Z
---

Gemini uses `gemini-extension.json`, `commands/*.toml`, and Agent [Skills](/components/skills.md). Its [hooks](/components/hooks-triggers.md) use events such as `BeforeTool` and `AfterTool`, so Claude-family hook configuration must be translated. Extensions may also provide [policies](/components/policies.md), settings, themes, preview agents, and embedded [MCP](/components/mcp.md); hosted [AI notebooks](/components/hosted-notebooks.md) require a separate import-pack workflow.

# Citations

[1] [Gemini extension reference](https://geminicli.com/docs/extensions/reference/)
[2] [Gemini hooks reference](https://geminicli.com/docs/hooks/reference/)
