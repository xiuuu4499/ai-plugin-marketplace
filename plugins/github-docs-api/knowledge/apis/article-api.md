# Article API

**Tags:** github-docs, api, article  
**Source:** https://docs.github.com/api/article/body?pathname=/en/get-started/using-github-docs/github-docs-api (accessed 2026-07-22)  
**Source class:** Official documentation

## Summary

The Article API returns the content and metadata of any GitHub Docs page. It supports standard articles, REST API reference pages, GraphQL reference pages, and landing pages.

## Endpoints

### Article Body — `GET /api/article/body`

Returns the **full article content as Markdown**. Preferred for LLM consumption.

**Required parameter:**
- `pathname` — The article path including language prefix (e.g. `/en/get-started/start-your-journey/what-is-github`).

**Optional parameter:**
- `apiVersion` — For REST API reference pages, specifies which API version to use. Defaults to the latest.

```shell
curl "https://docs.github.com/api/article/body?pathname=/en/get-started/start-your-journey/what-is-github"
```

Versioned (GitHub Enterprise Cloud):
```shell
curl "https://docs.github.com/api/article/body?pathname=/en/enterprise-cloud@latest/admin/overview/about-github-enterprise-cloud"
```

### Article Metadata — `GET /api/article/meta`

Returns article **metadata as JSON**: title, intro, product area, document type, and breadcrumbs.

```shell
curl "https://docs.github.com/api/article/meta?pathname=/en/get-started/start-your-journey/what-is-github"
```

### Article (combined) — `GET /api/article`

Returns both **metadata and body in a single JSON response**.

```shell
curl "https://docs.github.com/api/article?pathname=/en/get-started/start-your-journey/what-is-github"
```

## Notes

- The `pathname` must include the language prefix (`/en/`, `/ja/`, etc.).
- For versioned content, include the version in the pathname: `/en/enterprise-cloud@latest/...`.
- Use `/api/article/body` when the goal is LLM-readable Markdown.
- Use `/api/article` or `/api/article/meta` when structured metadata is also needed.
