# Pagelist API

**Tags:** github-docs, api, pagelist  
**Source:** https://docs.github.com/api/article/body?pathname=/en/get-started/using-github-docs/github-docs-api (accessed 2026-07-22)  
**Source class:** Official documentation

## Summary

The Pagelist API returns a complete list of every available page path for a given language and documentation version. Use it to enumerate all articles and to build indexes for further article retrieval.

## Endpoints

### Page List — `GET /api/pagelist/:lang/:version`

Returns a **newline-separated plain-text list** of all page paths for the specified language and version.

**Path parameters:**
- `:lang` — Language code (e.g. `en`, `ja`). Retrieve valid values from the Languages API.
- `:version` — Documentation version (e.g. `free-pro-team@latest`, `enterprise-cloud@latest`, `3.19`). Retrieve valid values from the Versions API.

```shell
curl "https://docs.github.com/api/pagelist/en/free-pro-team@latest"
```

### Languages — `GET /api/pagelist/languages`

Returns **all available language codes as JSON**.

```shell
curl "https://docs.github.com/api/pagelist/languages"
```

### Versions — `GET /api/pagelist/versions`

Returns **all available documentation versions as JSON**, including GitHub Enterprise Server version numbers.

```shell
curl "https://docs.github.com/api/pagelist/versions"
```

## Notes

- The page list output is a plain newline-separated list of URL paths; it is not JSON.
- Each path in the list can be passed directly to the Article API as the `pathname` parameter.
- The free-pro-team version is the default public GitHub.com documentation.
- Filtering the page list for specific keywords (whole-word match) is the basis for targeted navigation of the docs tree without a search query.
- See `scripts/github-docs-index-filter.sh` for a shell-based whole-word filter against the page list.
