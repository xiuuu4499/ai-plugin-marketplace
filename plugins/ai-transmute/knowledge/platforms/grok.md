---
type: AI Platform Format
title: Grok Build plugins
description: Grok Build plugins extend the CLI with skills, agents, hooks, MCP, and LSP while directly reading Claude formats.
tags: [grok, plugin, claude-compatible, agent-skills]
timestamp: 2026-07-21T00:00:00Z
---

Grok discovers native `.grok` configuration and enabled plugins, but explicitly reads Claude marketplaces, plugins, skills, agents, hooks, MCP, and [instruction files](/components/instruction-files.md). AI Transmute therefore renders a [Claude-compatible package](claude.md) for the Grok target instead of inventing a manifest. Hook scripts should accept Grok plugin root/data variables alongside compatibility variables.

# Citations

[1] [Grok Skills, Plugins & Marketplaces](https://docs.x.ai/build/features/skills-plugins-marketplaces)
