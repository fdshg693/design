"""Minimal calls for the four backends. No MCP passthrough, no Tavily extras.

grep / ms use fastmcp against public MCP servers. tav uses `tavily-python`.
ctx uses Context7 REST with `requests`. 202 polling / 429 backoff / 301 follow
are not implemented — failures surface as-is.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any

import requests

GREP_ENDPOINT = "https://mcp.grep.app"
# Cold-start grep.app can 504 around 20s and succeed near 40s (same as tools/grepapp).
GREP_TIMEOUT = 45.0
GREP_TOOL = "searchGitHub"

MS_ENDPOINT = "https://learn.microsoft.com/api/mcp"
MS_TIMEOUT = 30.0
MS_SEARCH_TOOL = "microsoft_docs_search"
MS_FETCH_TOOL = "microsoft_docs_fetch"

TAV_TIMEOUT = 60.0
CTX_TIMEOUT = 30.0
CTX_BASE_URL = "https://context7.com/api/v2/"
CTX_SEARCH_PATH = "libs/search"
CTX_CONTEXT_PATH = "context"

_REPO_LINE = re.compile(r"^Repository: (.+)$", re.MULTILINE)
_PATH_LINE = re.compile(r"^Path: (.+)$", re.MULTILINE)
_MARKDOWN_TITLE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_URL_LINE = re.compile(r"^URL:\s+\S+", re.MULTILINE)


def _content_text(result: Any) -> str:
    return "\n".join(block.text for block in result.content if hasattr(block, "text"))


def _call_mcp(endpoint: str, timeout: float, tool_name: str, arguments: dict[str, Any]) -> Any:
    from fastmcp import Client

    async def _run() -> Any:
        client = Client(endpoint, timeout=timeout)
        async with client:
            return await client.call_tool(tool_name, arguments, raise_on_error=False)

    return asyncio.run(_run())


def _clean_title(text: str) -> str:
    return " ".join(text.split()) or "(untitled)"


def grep_search(
    query: str,
    *,
    language: list[str] | None = None,
    repo: str | None = None,
    path: str | None = None,
    match_case: bool = False,
    match_whole_words: bool = False,
    use_regexp: bool = False,
) -> list[tuple[str, str]]:
    arguments: dict[str, Any] = {"query": query}
    if language:
        arguments["language"] = language
    if repo:
        arguments["repo"] = repo
    if path:
        arguments["path"] = path
    if match_case:
        arguments["matchCase"] = True
    if match_whole_words:
        arguments["matchWholeWords"] = True
    if use_regexp:
        arguments["useRegexp"] = True

    result = _call_mcp(GREP_ENDPOINT, GREP_TIMEOUT, GREP_TOOL, arguments)
    if result.is_error:
        raise RuntimeError(f"{GREP_TOOL} failed: {_content_text(result)}")

    blocks = [block.text for block in result.content if hasattr(block, "text")]
    if len(blocks) == 1 and not blocks[0].startswith("Repository: "):
        return []

    items: list[tuple[str, str]] = []
    for position, text in enumerate(blocks, start=1):
        repo_match = _REPO_LINE.search(text)
        path_match = _PATH_LINE.search(text)
        if repo_match and path_match:
            title = f"{repo_match.group(1)} — {path_match.group(1)}"
        else:
            title = f"result-{position}"
        items.append((title, f"# {title}\n\n{text}"))
    return items


def ms_search(query: str) -> list[tuple[str, str]]:
    result = _call_mcp(MS_ENDPOINT, MS_TIMEOUT, MS_SEARCH_TOOL, {"query": query})
    if result.is_error:
        raise RuntimeError(f"{MS_SEARCH_TOOL} failed: {_content_text(result)}")

    items: list[tuple[str, str]] = []
    for raw in (result.structured_content or {}).get("results", []):
        title = _clean_title(raw.get("title") or "(untitled)")
        url = raw.get("contentUrl", "")
        content = f"# {title}\n\nURL: {url}\n\n{raw.get('content', '')}"
        items.append((title, content))
    return items


def _with_source_url(markdown: str, url: str) -> str:
    head = "\n".join(markdown.splitlines()[:15])
    if _URL_LINE.search(head):
        return markdown
    url_line = f"URL: {url}"
    heading_match = _MARKDOWN_TITLE.search(markdown)
    if heading_match is None:
        return f"{url_line}\n\n{markdown}"
    before = markdown[: heading_match.end()]
    after = markdown[heading_match.end() :].lstrip("\n")
    return f"{before}\n\n{url_line}\n\n{after}"


def ms_fetch(url: str) -> list[tuple[str, str]]:
    result = _call_mcp(MS_ENDPOINT, MS_TIMEOUT, MS_FETCH_TOOL, {"url": url})
    if result.is_error:
        raise RuntimeError(f"{MS_FETCH_TOOL} failed: {_content_text(result)}")

    markdown = _content_text(result)
    if not markdown.strip():
        return []
    title_match = _MARKDOWN_TITLE.search(markdown)
    raw_title = title_match.group(1) if title_match else url.rstrip("/").rsplit("/", 1)[-1]
    title = _clean_title(raw_title)
    return [(title, _with_source_url(markdown, url))]


def _tavily_client(api_key: str) -> Any:
    from tavily import TavilyClient

    return TavilyClient(api_key=api_key)


def tav_search(
    query: str,
    *,
    api_key: str,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
) -> list[tuple[str, str]]:
    response = _tavily_client(api_key).search(
        query=query,
        search_depth="advanced",
        topic="general",
        max_results=5,
        chunks_per_source=3,
        include_answer=False,
        include_raw_content=False,
        include_images=False,
        include_favicon=False,
        include_usage=False,
        timeout=TAV_TIMEOUT,
        include_domains=include_domains or None,
        exclude_domains=exclude_domains or None,
    )
    items: list[tuple[str, str]] = []
    for position, raw in enumerate(response.get("results") or [], start=1):
        title = _clean_title(raw.get("title") or raw.get("url") or f"result-{position}")
        url = raw.get("url", "")
        score = raw.get("score", "")
        body = raw.get("content") or ""
        content = f"# {title}\n\nURL: {url}\nScore: {score}\n\n{body}"
        items.append((title, content))
    return items


def tav_extract(
    urls: list[str], *, api_key: str, query: str | None = None
) -> list[tuple[str, str]]:
    options: dict[str, Any] = {
        "extract_depth": "advanced",
        "format": "markdown",
        "timeout": TAV_TIMEOUT,
        "include_images": False,
        "include_favicon": False,
        "include_usage": False,
    }
    if query:
        options["chunks_per_source"] = 3
    response = _tavily_client(api_key).extract(urls=urls, query=query, **options)
    items: list[tuple[str, str]] = []
    for position, raw in enumerate(response.get("results") or [], start=1):
        url = raw.get("url", "")
        title = _clean_title(raw.get("title") or url or f"result-{position}")
        body = raw.get("raw_content") or ""
        items.append((title, f"# {title}\n\nURL: {url}\n\n{body}"))
    return items


def _ctx_headers(api_key: str) -> dict[str, str]:
    return {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}


def ctx_library(name: str, query: str, *, api_key: str) -> list[dict[str, Any]]:
    response = requests.get(
        CTX_BASE_URL + CTX_SEARCH_PATH,
        params={"libraryName": name, "query": query, "fast": "false"},
        headers=_ctx_headers(api_key),
        timeout=CTX_TIMEOUT,
    )
    response.raise_for_status()
    return (response.json() or {}).get("results") or []


def ctx_docs(library_id: str, query: str, *, api_key: str) -> str:
    response = requests.get(
        CTX_BASE_URL + CTX_CONTEXT_PATH,
        params={"libraryId": library_id, "query": query, "type": "txt", "fast": "false"},
        headers=_ctx_headers(api_key),
        timeout=CTX_TIMEOUT,
    )
    response.raise_for_status()
    return response.text
