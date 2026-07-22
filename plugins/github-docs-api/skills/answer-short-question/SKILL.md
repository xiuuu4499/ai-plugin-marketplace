---
name: answer-short-question
description: Quickly look up and answer a focused question using the GitHub Docs Search API and Article Body API. Use when a user asks a specific factual question about GitHub features, APIs, or workflows.
---

# Answer a short question from GitHub Docs

Read the knowledge base strategy guide before proceeding:

`cat "$PLUGIN_ROOT/knowledge/apis/search-strategies.md"`

## Workflow

1. Extract 2–5 concise search terms from the user's question.
2. Search GitHub Docs:

```shell
curl -s "https://docs.github.com/api/search/v1?query=<terms>&client_name=github-docs-expert&version=free-pro-team&language=en&size=10"
```

3. Review `hits[].highlights.content` for a quick answer. If the excerpt is sufficient, present it with a citation (`hits[].url`).
4. If a full article is needed, fetch the top result:

```shell
curl -s "https://docs.github.com/api/article/body?pathname=<hits[0].url>"
```

5. Answer the user's question concisely, citing the source article URL.

## Output

- A direct answer to the question (1–5 sentences).
- Source citation: the full `https://docs.github.com<pathname>` URL for each article used.
- If the answer is uncertain or the search returned no relevant results, say so and suggest a follow-up search term.

## Constraints

- Do not fetch more than 3 full articles; if the answer requires more, switch to the `$extract-github-sme-plugin` skill.
- Always include `client_name=github-docs-expert` in Search API calls.
- Do not fabricate information not found in the retrieved articles.
