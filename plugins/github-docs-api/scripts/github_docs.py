#!/usr/bin/env python3
"""GitHub Docs API client — search, fetch, and validate GitHub documentation.

Sub-commands
------------
search      Search GitHub Docs and print result URLs and titles.
fetch       Fetch one article body (Markdown) by pathname.
pagelist    Download and optionally filter the page list.
versions    List all available documentation versions.
languages   List all available documentation language codes.
validate-knowledge
            Check that all concept files listed in knowledge/index.md exist
            and that the index itself is well-formed.

All HTTP requests are made with urllib (stdlib only, no third-party deps).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE_URL = "https://docs.github.com"
DEFAULT_CLIENT_NAME = "github-docs-expert"
DEFAULT_VERSION = "free-pro-team@latest"
DEFAULT_LANG = "en"


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _get(url: str, accept: str = "*/*") -> bytes:
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": DEFAULT_CLIENT_NAME})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        sys.exit(f"HTTP {exc.code} fetching {url}: {exc.reason}")
    except urllib.error.URLError as exc:
        sys.exit(f"Network error fetching {url}: {exc.reason}")


def _get_json(url: str) -> dict | list:
    raw = _get(url, accept="application/json")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.exit(f"Invalid JSON from {url}: {exc}")


def _get_text(url: str) -> str:
    return _get(url, accept="text/plain").decode("utf-8")


# ---------------------------------------------------------------------------
# API wrappers
# ---------------------------------------------------------------------------

def search(query: str, client_name: str = DEFAULT_CLIENT_NAME,
           version: str = "free-pro-team", language: str = DEFAULT_LANG,
           page: int = 1, size: int = 10) -> dict:
    params = urllib.parse.urlencode({
        "query": query,
        "client_name": client_name,
        "version": version,
        "language": language,
        "page": page,
        "size": size,
    })
    url = f"{BASE_URL}/api/search/v1?{params}"
    return _get_json(url)  # type: ignore[return-value]


def fetch_body(pathname: str) -> str:
    """Return article body as Markdown."""
    params = urllib.parse.urlencode({"pathname": pathname})
    url = f"{BASE_URL}/api/article/body?{params}"
    return _get_text(url)


def fetch_meta(pathname: str) -> dict:
    """Return article metadata as JSON."""
    params = urllib.parse.urlencode({"pathname": pathname})
    url = f"{BASE_URL}/api/article/meta?{params}"
    return _get_json(url)  # type: ignore[return-value]


def get_pagelist(lang: str = DEFAULT_LANG, version: str = DEFAULT_VERSION) -> list[str]:
    """Return all page paths for the given lang + version."""
    url = f"{BASE_URL}/api/pagelist/{lang}/{version}"
    raw = _get_text(url)
    return [line.strip() for line in raw.splitlines() if line.strip()]


def get_versions() -> list:
    url = f"{BASE_URL}/api/pagelist/versions"
    return _get_json(url)  # type: ignore[return-value]


def get_languages() -> list:
    url = f"{BASE_URL}/api/pagelist/languages"
    return _get_json(url)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Knowledge validation
# ---------------------------------------------------------------------------

_LINK_RE = re.compile(r"\[.*?\]\(([^)]+\.md)\)")


def validate_knowledge(knowledge_root: Path) -> bool:
    """Check that index.md references exist and each referenced file is present."""
    index_file = knowledge_root / "index.md"
    if not index_file.is_file():
        print(f"ERROR: knowledge/index.md not found at {index_file}", file=sys.stderr)
        return False

    index_text = index_file.read_text(encoding="utf-8")
    referenced = _LINK_RE.findall(index_text)
    errors: list[str] = []

    for rel_path in referenced:
        # Paths in index.md are relative to knowledge/
        target = knowledge_root / rel_path
        if not target.is_file():
            errors.append(f"Missing: {target} (referenced as '{rel_path}' in index.md)")

    if errors:
        for msg in errors:
            print(f"ERROR: {msg}", file=sys.stderr)
        return False

    print(f"OK: {len(referenced)} concept file(s) verified.")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cmd_search(args: argparse.Namespace) -> None:
    result = search(
        query=args.query,
        client_name=args.client_name,
        version=args.version,
        language=args.language,
        page=args.page,
        size=args.size,
    )
    if args.json:
        print(json.dumps(result, indent=2))
        return
    meta = result.get("meta", {})
    hits = result.get("hits", [])
    found = meta.get("found", {}).get("value", "?")
    print(f"Found {found} result(s); showing {len(hits)}:\n")
    for hit in hits:
        url = f"{BASE_URL}{hit['url']}"
        print(f"  {hit['title']}")
        print(f"  {url}")
        content_highlights = hit.get("highlights", {}).get("content", [])
        if content_highlights:
            excerpt = re.sub(r"<[^>]+>", "", content_highlights[0])[:200]
            print(f"  …{excerpt}…")
        print()


def _cmd_fetch(args: argparse.Namespace) -> None:
    body = fetch_body(args.pathname)
    print(body)


def _cmd_pagelist(args: argparse.Namespace) -> None:
    paths = get_pagelist(lang=args.lang, version=args.version)
    if args.filter:
        # Whole-word path-segment filter (same logic as the shell script)
        pattern = re.compile(rf"(?i)(^|/){re.escape(args.filter)}(/|$)")
        paths = [p for p in paths if pattern.search(p)]
    for path in paths:
        print(path)


def _cmd_versions(args: argparse.Namespace) -> None:
    data = get_versions()
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        for item in data if isinstance(data, list) else [data]:
            print(item)


def _cmd_languages(args: argparse.Namespace) -> None:
    data = get_languages()
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        for item in data if isinstance(data, list) else [data]:
            print(item)


def _cmd_validate_knowledge(args: argparse.Namespace) -> None:
    root = Path(args.knowledge_root).resolve()
    ok = validate_knowledge(root)
    sys.exit(0 if ok else 1)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="GitHub Docs API client.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    p_search = sub.add_parser("search", help="Search GitHub Docs content.")
    p_search.add_argument("query", help="Search terms.")
    p_search.add_argument("--client-name", default=DEFAULT_CLIENT_NAME)
    p_search.add_argument("--version", default="free-pro-team")
    p_search.add_argument("--language", default=DEFAULT_LANG)
    p_search.add_argument("--page", type=int, default=1)
    p_search.add_argument("--size", type=int, default=10)
    p_search.add_argument("--json", action="store_true", help="Output raw JSON.")
    p_search.set_defaults(func=_cmd_search)

    # fetch
    p_fetch = sub.add_parser("fetch", help="Fetch an article body as Markdown.")
    p_fetch.add_argument("pathname", help="Article pathname (e.g. /en/actions/...).")
    p_fetch.set_defaults(func=_cmd_fetch)

    # pagelist
    p_pagelist = sub.add_parser("pagelist", help="Download and optionally filter the page list.")
    p_pagelist.add_argument("--lang", default=DEFAULT_LANG)
    p_pagelist.add_argument("--version", default=DEFAULT_VERSION)
    p_pagelist.add_argument("--filter", metavar="WORD",
                            help="Whole-word path-segment filter (case-insensitive).")
    p_pagelist.set_defaults(func=_cmd_pagelist)

    # versions
    p_versions = sub.add_parser("versions", help="List available documentation versions.")
    p_versions.add_argument("--json", action="store_true")
    p_versions.set_defaults(func=_cmd_versions)

    # languages
    p_languages = sub.add_parser("languages", help="List available documentation languages.")
    p_languages.add_argument("--json", action="store_true")
    p_languages.set_defaults(func=_cmd_languages)

    # validate-knowledge
    p_val = sub.add_parser("validate-knowledge",
                            help="Validate the knowledge/ index against concept files.")
    p_val.add_argument("knowledge_root", help="Path to the knowledge/ directory.")
    p_val.set_defaults(func=_cmd_validate_knowledge)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
