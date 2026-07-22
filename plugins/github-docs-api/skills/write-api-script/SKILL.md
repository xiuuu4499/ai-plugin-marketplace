---
name: write-api-script
description: Create a standalone script (shell or Python) that invokes GitHub Docs APIs to extract information without AI tooling. Use when a user needs a reproducible, automatable way to fetch or process GitHub documentation content.
---

# Write a GitHub Docs API script

## Workflow

1. Clarify with the user:
   - What information should the script retrieve (search results, a specific article, a set of pages, the full pagelist)?
   - What output format is needed (Markdown, JSON, plain text, filtered list)?
   - What language is preferred (shell/`curl`, Python)?
   - Should the script be idempotent and cacheable?

2. Read the relevant knowledge base concepts:

```shell
cat "$PLUGIN_ROOT/knowledge/apis/search-strategies.md"
cat "$PLUGIN_ROOT/knowledge/apis/search-api.md"
cat "$PLUGIN_ROOT/knowledge/apis/article-api.md"
cat "$PLUGIN_ROOT/knowledge/apis/pagelist-api.md"
```

3. Reference the provided utility scripts for patterns:

```shell
cat "$PLUGIN_ROOT/scripts/github-docs-index-filter.sh"
cat "$PLUGIN_ROOT/scripts/github_docs.py"
```

4. Write the script. Follow these conventions:
   - Always include a `client_name` parameter in Search API calls.
   - Handle HTTP errors explicitly (check exit codes for `curl`, status codes for Python `requests`/`urllib`).
   - Accept parameters via command-line arguments, not hardcoded values.
   - Add a usage comment or `--help` flag.

5. Show the script to the user and explain:
   - What it does, step by step.
   - Any required environment variables or dependencies.
   - Example invocation.

## Output

A ready-to-run script file, with usage instructions and example invocation.

## Constraints

- Do not include GitHub personal access tokens or any credentials in the script.
- Do not use unofficial or undocumented GitHub APIs.
- Keep scripts minimal and focused on the stated information-retrieval goal.
