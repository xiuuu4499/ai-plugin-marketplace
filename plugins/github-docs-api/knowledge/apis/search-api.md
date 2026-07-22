# Search API

**Tags:** github-docs, api, search  
**Source:** https://docs.github.com/api/article/body?pathname=/en/get-started/using-github-docs/github-docs-api (accessed 2026-07-22)  
**Source class:** Official documentation

## Summary

The Search API searches across all GitHub Docs content and returns results sorted by relevance, with highlights and metadata for each matching page.

## Endpoint

### Search — `GET /api/search/v1`

**Required parameters:**
- `query` — The search term.
- `client_name` — Required for external clients (e.g. `curl` or agent code). A name that identifies your client or integration.

**Optional parameters:**
- `version` — Documentation version to search. Defaults to `free-pro-team`. Valid values: `free-pro-team`, `enterprise-cloud`, GitHub Enterprise Server version numbers (e.g. `3.19`).
- `language` — Language to search. Defaults to `en`.
- `page` — Page number for paginated results. Defaults to `1`.
- `size` — Number of results per page, up to a maximum of `50`. Defaults to `10`.

```shell
curl "https://docs.github.com/api/search/v1?query=actions&client_name=my-tool&version=free-pro-team&language=en"
```

## Response structure

```json
{
  "meta": {
    "found": { "value": 1234, "relation": "eq" },
    "took": { "query_msec": 20, "total_msec": 41 },
    "page": 1,
    "size": 10
  },
  "hits": [
    {
      "id": "...",
      "url": "/en/actions/...",
      "title": "...",
      "breadcrumbs": "GitHub Actions / ...",
      "highlights": {
        "title": ["..."],
        "content": ["..."]
      }
    }
  ]
}
```

## Notes

- `hits[].url` values are relative paths; prepend `https://docs.github.com` to form full URLs, or pass directly to the Article API as the `pathname` parameter.
- `highlights.content` contains short excerpts with matched terms wrapped in `<mark>` tags—useful for quick summaries without fetching the full article.
- Increase `size` (up to 50) to get more results per page; use `page` to paginate beyond the first batch.
- For external scripts, always supply `client_name` to identify the caller as required by the API.
