# GitHub Docs API — Overview

**Tags:** github-docs, api, llms-txt  
**Source:** https://docs.github.com/llms.txt (accessed 2026-07-22)  
**Source class:** Official documentation

## Summary

GitHub Docs exposes a set of programmatic HTTP APIs that allow LLMs, agents, and automation tools to discover, list, search, and retrieve documentation content without scraping HTML.

The canonical entry point for AI agents is `https://docs.github.com/llms.txt`, which follows the [llms.txt standard](https://llmstxt.org/) and lists all available API endpoints with examples.

## Available APIs

| API | Base URL | Purpose |
|---|---|---|
| llms.txt | `https://docs.github.com/llms.txt` | Structured index for LLM/agent consumption |
| Versions API | `https://docs.github.com/api/pagelist/versions` | List all available documentation versions |
| Languages API | `https://docs.github.com/api/pagelist/languages` | List all available language codes |
| Pagelist API | `https://docs.github.com/api/pagelist/:lang/:version` | List all page paths for a language + version |
| Article Body API | `https://docs.github.com/api/article/body` | Fetch full article as Markdown |
| Article Meta API | `https://docs.github.com/api/article/meta` | Fetch article metadata as JSON |
| Article API | `https://docs.github.com/api/article` | Fetch article body + metadata as JSON |
| Search API | `https://docs.github.com/api/search/v1` | Search across all docs content |

## Recommended discovery sequence for agents

1. Start at `llms.txt` to get an authoritative overview of the API surface.
2. Use the **Pagelist API** to enumerate all available paths for a language/version pair.
3. Use the **Search API** to locate pages relevant to a query.
4. Use the **Article Body API** to fetch individual pages as Markdown for LLM consumption.
5. Use the **Article Meta API** or combined **Article API** when structured metadata (breadcrumbs, product area, document type) is also needed.

## Key design notes

- The `/api/article/body` endpoint returns **Markdown**, which is ideal for LLM consumption.
- The Pagelist endpoint returns a **newline-separated plain-text list** of paths.
- The Search API requires a `client_name` parameter for external (non-browser) clients.
- All endpoints are public and require no authentication.
- The `:version` path parameter controls which edition of the docs is served. The default for non-Enterprise use is `free-pro-team@latest`. Enterprise editions use `enterprise-cloud@latest` (GHEC) or a numeric version string such as `3.12` (GHES). See `apis/enterprise-deployments.md` for full details and guidance on when to use each.
