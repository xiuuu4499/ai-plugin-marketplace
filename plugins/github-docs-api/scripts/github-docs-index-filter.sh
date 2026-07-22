#!/usr/bin/env bash
# github-docs-index-filter.sh — Search the GitHub Docs page list for whole-word matches.
#
# Usage:
#   curl -s "https://docs.github.com/api/pagelist/en/free-pro-team@latest" \
#     | bash github-docs-index-filter.sh <WORD>
#
# Or supply the page list from a local file:
#   cat pagelist.txt | bash github-docs-index-filter.sh <WORD>
#
# Returns lines from the page list where WORD appears as a complete path segment
# (bounded by '/' or end-of-line), preventing "api" from matching "graphql-api"
# mid-segment.  The match is case-insensitive.
#
# Exit codes:
#   0  — at least one match found
#   1  — no matches found
#   2  — usage error (missing WORD argument)

set -euo pipefail

if [[ $# -lt 1 || -z "${1:-}" ]]; then
    echo "Usage: ... | $(basename "$0") <WORD>" >&2
    exit 2
fi

WORD="$1"

# Match WORD as a full path segment: preceded by '/' and followed by '/' or end-of-line.
# The -i flag makes the match case-insensitive.
grep -i -E "(^|/)${WORD}(/|$)"
