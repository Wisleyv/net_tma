"""I/O helpers for the parser package."""

from __future__ import annotations

from pathlib import Path

def read_text(path: str | Path) -> str:
    """Read a text file using UTF-8 encoding."""
    return Path(path).read_text(encoding="utf-8")


def write_json(path: str | Path, data: dict) -> None:
    """Write a JSON file with UTF-8 encoding and pretty formatting."""
    import json

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
