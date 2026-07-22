---
name: extract-github-sme-plugin
description: Work in Plan Mode with the ai-scholar plan-mode skill to create a new GitHub domain Subject Matter Expert (SME) agent plugin. Starts by extracting information from GitHub Docs APIs and building an OKF knowledge base. Use when a user wants a focused expert plugin for a specific GitHub feature area.
---

# Extract a GitHub SME plugin

This skill operates in **Plan Mode** and delegates phases to the ai-scholar skill set. The goal is a new Codex plugin focused on a specific GitHub domain (e.g. "GitHub Actions", "GitHub Packages", "GitHub REST API for repositories").

## Pre-flight

Read the knowledge base strategy guide:

`cat "$PLUGIN_ROOT/knowledge/apis/search-strategies.md"`

Read the ai-scholar plan-mode skill:

`cat "$(codex plugin-root ai-scholar)/skills/plan-mode/SKILL.md"`

Read the OKF plugin manifest for reference:

`cat "$(codex plugin-root okf)/.codex-plugin/plugin.json"`

## Workflow (Plan Mode)

Work through the ai-scholar state machine. Create a plan with the following steps—do not collapse them:

### Step 1 — Initialize a research job (ai-scholar `$study`)

```shell
python3 "$(codex plugin-root ai-scholar)/scripts/ai_scholar.py" init "<github-domain>" \
  --output <output-parent-dir> \
  --goal "Create a SME plugin for <github-domain> with complete, cited knowledge extracted from GitHub Docs." \
  --audience "Developers using Codex agents to work with <github-domain>" \
  --json
```

### Step 2 — Crawl GitHub Docs for domain content

Use the pagelist filter and article body strategy from the knowledge base:

```shell
# Get all relevant page paths
curl -s "https://docs.github.com/api/pagelist/en/free-pro-team@latest" \
  | bash "$PLUGIN_ROOT/scripts/github-docs-index-filter.sh" "<keyword>"

# Fetch each matching article
curl -s "https://docs.github.com/api/article/body?pathname=<path>"
```

For breadth, also run a Search API query:

```shell
curl -s "https://docs.github.com/api/search/v1?query=<domain+terms>&client_name=github-docs-expert&size=20"
```

### Step 3 — Curate sources (ai-scholar `$sources`)

Record each fetched page in `sources/registry.md`. Rank by authority, uniqueness, and relevance. Discard low-value or duplicate pages.

### Step 4 — Build OKF knowledge bundle (ai-scholar `$knowledge`)

Use the OKF plugin to create cited concept files from the retained sources:

- Plugin reference: `https://raw.githubusercontent.com/xiuuu4499/ai-plugin-marketplace/refs/heads/main/plugins/okf/.codex-plugin/plugin.json`
- One independently-linkable fact or decision per concept file.
- Validate after each import: `okf validate <job>/knowledge --json`

### Step 5 — Design the SME plugin (ai-scholar `$architect`)

Write `design/interface.md` with: skills, scripts, agents, acceptance tests, and a requirements-to-evidence traceability matrix. Every public capability must trace to a cited source.

### Step 6 — Human review gate (ai-scholar `$review`)

Present the design packet. **Do not implement until the human explicitly approves.**

```shell
python3 "$(codex plugin-root ai-scholar)/scripts/ai_scholar.py" gate <job> implement --json
```

### Step 7 — Implement (ai-scholar `$implement`)

Build the approved plugin package.

### Step 8 — Validate (ai-scholar `$validate`)

Run all acceptance tests and validate the OKF bundle.

## Output

A complete Codex plugin directory in the marketplace `plugins/` folder, ready for PR.
