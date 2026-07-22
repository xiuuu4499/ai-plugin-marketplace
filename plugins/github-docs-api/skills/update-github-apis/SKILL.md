---
name: update-github-apis
description: Re-crawl the GitHub Docs API surface to detect changes and update this plugin's knowledge base. Use when the GitHub Docs API may have changed since the plugin was last generated, or when new GitHub features need to be captured.
---

# Update GitHub Docs API knowledge

This skill re-runs the knowledge-generation process for this plugin, looking for changes since the last update recorded in `knowledge/log.md`.

## Workflow

### Step 1 — Check the current state

```shell
cat "$PLUGIN_ROOT/knowledge/log.md"
```

Note the date of the last update.

### Step 2 — Re-crawl the discovery sources

**Version selection:** Re-crawl `free-pro-team@latest` by default. If a prior crawl included Enterprise versions (check `knowledge/log.md`), re-crawl those too. To list all GHES release versions:

```shell
curl -s "https://docs.github.com/api/pagelist/versions"
```

```shell
# Fetch the current llms.txt
curl -s "https://docs.github.com/llms.txt"

# Fetch the current GitHub Docs API reference
curl -s "https://docs.github.com/api/article/body?pathname=/en/get-started/using-github-docs/github-docs-api"

# Fetch the pagelist and look for new or changed API/search/schema pages
curl -s "https://docs.github.com/api/pagelist/en/free-pro-team@latest" \
  | bash "$PLUGIN_ROOT/scripts/github-docs-index-filter.sh" "api"
```

### Step 3 — Compare to existing knowledge

For each concept file in `knowledge/apis/`, check whether the source content has changed materially:
- New endpoints added?
- Endpoint signatures or parameters changed?
- New query parameters, response fields, or error codes?
- Deprecated or removed endpoints?

### Step 4 — Update knowledge files

For each changed concept:
1. Update the concept file with the new information.
2. Preserve or update the source URL and access date.
3. Add a row to `knowledge/log.md` describing what changed.

### Step 5 — Validate

```shell
python3 "$PLUGIN_ROOT/scripts/github_docs.py" validate-knowledge "$PLUGIN_ROOT/knowledge"
```

Confirm that all concept files are internally consistent and that the index still references all concept files.

### Step 6 — Report

Summarize the changes found:
- New APIs or endpoints discovered.
- Existing API parameters changed.
- Deprecated or removed APIs.
- No changes (if applicable).

## Constraints

- Do not remove knowledge that was accurate when written without first confirming it is outdated.
- Record all changes in `knowledge/log.md` with the current date.
- Do not update the plugin version string; that is done by a separate release workflow.
