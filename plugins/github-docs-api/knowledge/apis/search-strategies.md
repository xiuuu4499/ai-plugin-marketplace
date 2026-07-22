# Search Strategies

**Tags:** github-docs, search, strategy  
**Source:** Derived from https://docs.github.com/llms.txt and https://docs.github.com/api/article/body?pathname=/en/get-started/using-github-docs/github-docs-api (accessed 2026-07-22)  
**Source class:** Design decision based on official documentation

## Summary

Different information needs call for different GitHub Docs API strategies. This concept maps user intents to the most appropriate API combination.

## Strategy taxonomy

### 1. Quick single-question answer

**Use case:** User asks a focused factual question (e.g. "What is the rate limit for the GitHub REST API?").

**Strategy:** Search API → Article Body API

1. Run `GET /api/search/v1?query=<terms>&client_name=<name>&size=5` to find relevant pages.
2. Review `hits[].highlights.content` for a quick answer.
3. If the highlight is insufficient, fetch the top result with `GET /api/article/body?pathname=<hits[0].url>`.

**Rationale:** Search is fast and returns ranked excerpts. Most single questions are answered by the excerpt alone or by one article.

### 2. Deep extraction of a subject area

**Use case:** User wants all information on a topic (e.g. "Explain everything about GitHub Actions concurrency controls").

**Strategy:** Pagelist API filter → Article Body API (batch)

1. Fetch `GET /api/pagelist/en/free-pro-team@latest` to get the full path list.
2. Filter paths with `scripts/github-docs-index-filter.sh <keyword>` (whole-word match) to locate the relevant section of the docs tree.
3. Fetch each matched path with `GET /api/article/body?pathname=<path>`.
4. Synthesize across all fetched articles.

**Rationale:** Search is relevance-ranked and may omit pages that don't score highly. When complete coverage of a docs subtree is required, the pagelist filter approach guarantees no pages are missed.

### 3. Browsing an unknown docs area

**Use case:** User is exploring a new GitHub feature area and wants to understand its structure.

**Strategy:** Pagelist API + partial-path filtering → Article Meta API

1. Fetch the pagelist and filter for a topic-prefix path segment (e.g. `/en/actions/`).
2. Use `GET /api/article/meta?pathname=<path>` to fetch titles and breadcrumbs for each match cheaply (no full body needed).
3. Present the resulting navigation tree to the user.

**Rationale:** Meta-only fetches are much lighter than full body fetches for navigation tasks.

### 4. Finding an exact page by keyword

**Use case:** User asks for a specific page (e.g. "Find the page about billing for GitHub Copilot").

**Strategy:** Search API with precise query

1. Run `GET /api/search/v1?query=<precise+terms>&client_name=<name>&size=10`.
2. Match `hits[].title` and `hits[].breadcrumbs` against the user's intent.
3. Fetch the body of the best match.

**Rationale:** Shorter search queries are usually sufficient for exact-page lookup; pagelist filtering is not needed.

### 5. Keeping knowledge current (update workflow)

**Use case:** Agent wants to detect changes since a previous crawl.

**Strategy:** Pagelist diff + selective Article Body refetch

1. Fetch the current pagelist and compare to the previously stored list.
2. Identify added, removed, and path-stable pages.
3. Re-fetch changed or new pages with the Article Body API.
4. Update the knowledge base concepts accordingly.

**Rationale:** Full re-crawl is expensive. Diffing the pagelist first narrows re-fetching to only changed content.

## Decision matrix

| Intent | Completeness needed | Recommended primary API |
|---|---|---|
| Answer a short question | Low — one excerpt suffices | Search API |
| Answer a short question | Medium — one full article | Search API + Article Body |
| Survey a docs subtree | High — full coverage | Pagelist filter + Article Body (batch) |
| Explore structure / navigate | Navigation only | Pagelist filter + Article Meta |
| Locate an exact page | Single page | Search API |
| Detect changes since last crawl | Incremental | Pagelist diff + Article Body (selective) |
