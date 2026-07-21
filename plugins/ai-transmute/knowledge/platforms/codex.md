---
type: AI Platform Format
title: Codex plugins
description: Codex packages skills, hooks, apps, MCP servers, and presentation assets under a .codex-plugin manifest.
tags: [codex, plugin, agent-skills]
timestamp: 2026-07-21T00:00:00Z
---

Codex requires a [plugin manifest](/components/plugin-manifests.md) at `.codex-plugin/plugin.json`; default components remain at the plugin root. It discovers [skills](/components/skills.md), advisory [hooks](/components/hooks-triggers.md), and [MCP](/components/mcp.md). AI Transmute omits undocumented fields and relies on default `hooks/hooks.json` discovery.

# Citations

[1] [Build Codex plugins](https://developers.openai.com/codex/plugins/build)
