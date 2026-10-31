"""Load `.env` and report which backends the current settings can run.

`available` is a settings-only check (no network). stdout is a fixed table so a
skill can inject it with ```!```. Exit 0 even when every backend is unavailable.

Contract (do not change without updating the skill):

    backend  status       reason
    grep      available    no API key required
    ms        available    no API key required
    tav       available    TAVILY_API_KEY is set
    ctx       unavailable  CONTEXT7_API_KEY is empty

Columns are two-space separated and left-aligned. Backend names are `grep` /
`ms` / `tav` / `ctx`. Status is `available` or `unavailable`. Reason strings
are the constants below.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

TAVILY_API_KEY_ENV = "TAVILY_API_KEY"
CONTEXT7_API_KEY_ENV = "CONTEXT7_API_KEY"
OUTPUT_DIR_ENV = "WEB_LOOKUP_OUTPUT_DIR"
DEFAULT_OUTPUT_DIR = "temp/web-lookup"

BACKEND_GREP = "grep"
BACKEND_MS = "ms"
BACKEND_TAV = "tav"
BACKEND_CTX = "ctx"

STATUS_AVAILABLE = "available"
STATUS_UNAVAILABLE = "unavailable"

REASON_NO_KEY_REQUIRED = "no API key required"
REASON_TAVILY_SET = "TAVILY_API_KEY is set"
REASON_TAVILY_EMPTY = "TAVILY_API_KEY is empty"
REASON_CONTEXT7_SET = "CONTEXT7_API_KEY is set"
REASON_CONTEXT7_EMPTY = "CONTEXT7_API_KEY is empty"

_SKILL_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = _SKILL_DIR / ".env"


def load_environment() -> Path | None:
    """Load the skill-directory `.env` only (no cwd or parent search)."""
    load_dotenv(ENV_PATH, override=False)
    if ENV_PATH.is_file():
        return ENV_PATH
    return None


def _key(name: str) -> str:
    return os.environ.get(name, "").strip()


def get_tavily_api_key() -> str:
    return _key(TAVILY_API_KEY_ENV)


def get_context7_api_key() -> str:
    return _key(CONTEXT7_API_KEY_ENV)


def get_output_dir() -> Path:
    value = os.environ.get(OUTPUT_DIR_ENV, "").strip()
    return Path(value or DEFAULT_OUTPUT_DIR)


def backend_rows() -> list[tuple[str, str, str]]:
    """Return (backend, status, reason) in the fixed `available` order."""
    tav_key = get_tavily_api_key()
    ctx_key = get_context7_api_key()
    return [
        (BACKEND_GREP, STATUS_AVAILABLE, REASON_NO_KEY_REQUIRED),
        (BACKEND_MS, STATUS_AVAILABLE, REASON_NO_KEY_REQUIRED),
        (
            BACKEND_TAV,
            STATUS_AVAILABLE if tav_key else STATUS_UNAVAILABLE,
            REASON_TAVILY_SET if tav_key else REASON_TAVILY_EMPTY,
        ),
        (
            BACKEND_CTX,
            STATUS_AVAILABLE if ctx_key else STATUS_UNAVAILABLE,
            REASON_CONTEXT7_SET if ctx_key else REASON_CONTEXT7_EMPTY,
        ),
    ]


def format_availability_table(rows: list[tuple[str, str, str]] | None = None) -> str:
    data = rows if rows is not None else backend_rows()
    headers = ("backend", "status", "reason")
    widths = [len(cell) for cell in headers]
    for row in data:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def _fmt(cells: tuple[str, ...]) -> str:
        padded = [cell.ljust(widths[i]) for i, cell in enumerate(cells[:-1])]
        padded.append(cells[-1])
        return "  ".join(padded)

    lines = [_fmt(headers), *(_fmt(row) for row in data)]
    return "\n".join(lines) + "\n"


def unavailable_reason(backend: str) -> str | None:
    """If `backend` is unavailable, return the same reason `available` would print."""
    for name, status, reason in backend_rows():
        if name == backend:
            return None if status == STATUS_AVAILABLE else reason
    raise KeyError(f"unknown backend: {backend}")
