r"""Skill-local CLI: `uv run --project ${CLAUDE_SKILL_DIR} web-lookup <subcommand>`.

Subcommands: `available` / `grep search` / `ms search` / `ms fetch` /
`tav search` / `tav extract` / `ctx library` / `ctx docs`.

`available` prints a settings table on stdout and always exits 0. Large results
(grep / ms / tav) write `WEB_LOOKUP_OUTPUT_DIR/NNNN-<slug>/` and print only the
`index.md` path. `ctx` and `available` print to stdout.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from backends import (
    ctx_docs,
    ctx_library,
    grep_search,
    ms_fetch,
    ms_search,
    tav_extract,
    tav_search,
)
from env_check import (
    BACKEND_CTX,
    BACKEND_GREP,
    BACKEND_MS,
    BACKEND_TAV,
    format_availability_table,
    get_context7_api_key,
    get_tavily_api_key,
    load_environment,
    unavailable_reason,
)
from output import print_index_path, write_query_results

EXIT_SUCCESS = 0
EXIT_ERROR = 1


def _reject_if_unavailable(backend: str) -> int | None:
    reason = unavailable_reason(backend)
    if reason is None:
        return None
    print(f"{backend} is unavailable: {reason}", file=sys.stderr)
    return EXIT_ERROR


def _write_or_empty(label: str, items: list[tuple[str, str]]) -> int:
    if not items:
        print("No results.", file=sys.stderr)
        return EXIT_ERROR
    print_index_path(write_query_results(label, items))
    return EXIT_SUCCESS


def cmd_available(_args: argparse.Namespace) -> int:
    sys.stdout.write(format_availability_table())
    return EXIT_SUCCESS


def cmd_grep_search(args: argparse.Namespace) -> int:
    if (code := _reject_if_unavailable(BACKEND_GREP)) is not None:
        return code
    items = grep_search(
        args.query,
        language=args.language,
        repo=args.repo,
        path=args.path,
        match_case=args.match_case,
        match_whole_words=args.match_whole_words,
        use_regexp=args.use_regexp,
    )
    return _write_or_empty(args.query, items)


def cmd_ms_search(args: argparse.Namespace) -> int:
    if (code := _reject_if_unavailable(BACKEND_MS)) is not None:
        return code
    return _write_or_empty(args.query, ms_search(args.query))


def cmd_ms_fetch(args: argparse.Namespace) -> int:
    if (code := _reject_if_unavailable(BACKEND_MS)) is not None:
        return code
    return _write_or_empty(args.url, ms_fetch(args.url))


def cmd_tav_search(args: argparse.Namespace) -> int:
    if (code := _reject_if_unavailable(BACKEND_TAV)) is not None:
        return code
    items = tav_search(
        args.query,
        api_key=get_tavily_api_key(),
        include_domains=args.include_domain,
        exclude_domains=args.exclude_domain,
    )
    return _write_or_empty(args.query, items)


def cmd_tav_extract(args: argparse.Namespace) -> int:
    if (code := _reject_if_unavailable(BACKEND_TAV)) is not None:
        return code
    items = tav_extract(args.urls, api_key=get_tavily_api_key(), query=args.query)
    return _write_or_empty(args.urls[0], items)


def cmd_ctx_library(args: argparse.Namespace) -> int:
    if (code := _reject_if_unavailable(BACKEND_CTX)) is not None:
        return code
    results = ctx_library(args.name, args.query, api_key=get_context7_api_key())
    if not results:
        print("No matching libraries.", file=sys.stderr)
        return EXIT_ERROR
    for item in results:
        print(f"{item.get('id')}  {item.get('title')}")
        description = item.get("description")
        if description:
            print(f"  {description}")
        print(
            f"  trustScore={item.get('trustScore')} snippets={item.get('totalSnippets')} "
            f"stars={item.get('stars')} state={item.get('state')}"
        )
        print()
    return EXIT_SUCCESS


def cmd_ctx_docs(args: argparse.Namespace) -> int:
    if (code := _reject_if_unavailable(BACKEND_CTX)) is not None:
        return code
    text = ctx_docs(args.library_id, args.query, api_key=get_context7_api_key())
    if not text.strip():
        print("No results.", file=sys.stderr)
        return EXIT_ERROR
    print(text, end="" if text.endswith("\n") else "\n")
    return EXIT_SUCCESS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="web-lookup",
        description=(
            "Bundled web lookup for grep.app, Microsoft Learn, Tavily, and Context7. "
            "Run as: uv run --project ${CLAUDE_SKILL_DIR} web-lookup <subcommand>"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_available = sub.add_parser(
        "available",
        help="Print which backends the current .env / environment can run (no network).",
    )
    p_available.set_defaults(func=cmd_available)

    p_grep = sub.add_parser("grep", help="Search public GitHub code via grep.app MCP.")
    grep_sub = p_grep.add_subparsers(dest="grep_command", required=True)
    p_grep_search = grep_sub.add_parser(
        "search", help="Search public GitHub repos for a literal code pattern."
    )
    p_grep_search.add_argument("query", help="A literal code pattern, e.g. 'useState('.")
    p_grep_search.add_argument(
        "--language",
        action="append",
        help="Restrict to a language, e.g. TypeScript. Repeat to allow several.",
    )
    p_grep_search.add_argument("--repo", help="Restrict to a repo, e.g. 'facebook/react'.")
    p_grep_search.add_argument("--path", help="Restrict to a file path, e.g. '/route.ts'.")
    p_grep_search.add_argument("--match-case", action="store_true", help="Case-sensitive match.")
    p_grep_search.add_argument(
        "--match-whole-words", action="store_true", help="Match whole words only."
    )
    p_grep_search.add_argument(
        "--use-regexp", action="store_true", help="Treat query as a regular expression."
    )
    p_grep_search.set_defaults(func=cmd_grep_search)

    p_ms = sub.add_parser("ms", help="Search or fetch Microsoft Learn docs.")
    ms_sub = p_ms.add_subparsers(dest="ms_command", required=True)
    p_ms_search = ms_sub.add_parser("search", help="Semantic search over Microsoft/Azure docs.")
    p_ms_search.add_argument("query")
    p_ms_search.set_defaults(func=cmd_ms_search)
    p_ms_fetch = ms_sub.add_parser("fetch", help="Fetch one Learn page as Markdown.")
    p_ms_fetch.add_argument("url")
    p_ms_fetch.set_defaults(func=cmd_ms_fetch)

    p_tav = sub.add_parser("tav", help="Tavily web search and URL extract.")
    tav_sub = p_tav.add_subparsers(dest="tav_command", required=True)
    p_tav_search = tav_sub.add_parser("search", help="Search the web with Tavily.")
    p_tav_search.add_argument("query")
    p_tav_search.add_argument(
        "--include-domain",
        action="append",
        default=[],
        help="Optional domain to include. Repeat to allow multiple domains.",
    )
    p_tav_search.add_argument(
        "--exclude-domain",
        action="append",
        default=[],
        help="Optional domain to exclude. Repeat to exclude multiple domains.",
    )
    p_tav_search.set_defaults(func=cmd_tav_search)
    p_tav_extract = tav_sub.add_parser("extract", help="Extract content from known URL(s).")
    p_tav_extract.add_argument("urls", nargs="+", help="One or more URLs.")
    p_tav_extract.add_argument("--query", help="Optional relevance query for focused extraction.")
    p_tav_extract.set_defaults(func=cmd_tav_extract)

    p_ctx = sub.add_parser("ctx", help="Context7 library search and docs (API key required).")
    ctx_sub = p_ctx.add_subparsers(dest="ctx_command", required=True)
    p_ctx_library = ctx_sub.add_parser("library", help="Search Context7 for candidate library IDs.")
    p_ctx_library.add_argument("name", help="Library/framework name.")
    p_ctx_library.add_argument("query", help="What you want to do with the library.")
    p_ctx_library.set_defaults(func=cmd_ctx_library)
    p_ctx_docs = ctx_sub.add_parser("docs", help="Fetch documentation context for one library ID.")
    p_ctx_docs.add_argument("library_id", help="Context7 library ID, e.g. /react/react.")
    p_ctx_docs.add_argument("query", help="Single focused question/topic.")
    p_ctx_docs.set_defaults(func=cmd_ctx_docs)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    load_environment()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
