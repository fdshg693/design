"""Write one call's results as `NNNN-<slug>/` + `index.md`; print only that path.

No file lock, no Q&A split, no `--json`. Sequence numbers are scanned from
existing `NNNN-*` entries under `WEB_LOOKUP_OUTPUT_DIR` (default `temp/web-lookup`).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path

from env_check import get_output_dir

_SLUG_SEPARATOR = re.compile(r"[^\w]+", re.UNICODE)
_SEQUENCE_PREFIX = re.compile(r"^(\d{4})")


def slugify(text: str | None, *, max_length: int = 50) -> str:
    lowered = (text or "").strip().lower()
    slug = _SLUG_SEPARATOR.sub("-", lowered).strip("-")
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")
    return slug or "item"


def _next_prefixed_sequence(directory: Path) -> int:
    if not directory.exists():
        return 1
    highest = 0
    for entry in directory.iterdir():
        match = _SEQUENCE_PREFIX.match(entry.name)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def write_query_results(label: str, items: Sequence[tuple[str, str]]) -> Path:
    """Write `(title, content)` items into a fresh folder; return `index.md`."""
    root = get_output_dir()
    root.mkdir(parents=True, exist_ok=True)
    folder = root / f"{_next_prefixed_sequence(root):04d}-{slugify(label)}"
    folder.mkdir(parents=True)

    lines = [f"# {label}", ""]
    for position, (title, content) in enumerate(items, start=1):
        filename = f"{position:04d}.md"
        (folder / filename).write_text(content, encoding="utf-8")
        lines.append(f"- [{title}]({filename}) ({len(content)} chars)")

    index_path = folder / "index.md"
    index_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return index_path


def print_index_path(index_path: Path) -> None:
    print(index_path)
