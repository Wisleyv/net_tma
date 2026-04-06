"""Persistent project-state helpers for the validator UI."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ProjectState:
    tags_path: str | None = None
    source_text_path: str | None = None
    target_text_path: str | None = None
    last_dataset_path: str | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ProjectState":
        return cls(
            tags_path=_as_optional_str(payload.get("tags_path")),
            source_text_path=_as_optional_str(payload.get("source_text_path")),
            target_text_path=_as_optional_str(payload.get("target_text_path")),
            last_dataset_path=_as_optional_str(
                payload.get("last_dataset_path")
            ),
        )

    def to_payload(self) -> dict[str, str | None]:
        return {
            "tags_path": self.tags_path,
            "source_text_path": self.source_text_path,
            "target_text_path": self.target_text_path,
            "last_dataset_path": self.last_dataset_path,
        }


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def resolve_runtime_root() -> Path:
    """Return runtime root (repo root in dev, exe dir in packaged mode)."""

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def resolve_data_dir(runtime_root: Path | None = None) -> Path:
    root = runtime_root or resolve_runtime_root()
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _state_file_path(runtime_root: Path | None = None) -> Path:
    return resolve_data_dir(runtime_root=runtime_root) / "metadata.json"


def load_project_state(runtime_root: Path | None = None) -> ProjectState:
    state_file = _state_file_path(runtime_root=runtime_root)
    if not state_file.exists():
        return ProjectState()

    try:
        payload = json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ProjectState()

    if not isinstance(payload, dict):
        return ProjectState()
    return ProjectState.from_payload(payload)


def save_project_state(
    state: ProjectState,
    runtime_root: Path | None = None,
) -> None:
    state_file = _state_file_path(runtime_root=runtime_root)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(
        json.dumps(state.to_payload(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _decode_text_bytes(raw: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _persist_text_file(
    source_file: Path,
    destination_name: str,
    runtime_root: Path | None = None,
) -> Path:
    if not source_file.exists():
        raise FileNotFoundError(source_file)

    content = _decode_text_bytes(source_file.read_bytes())
    destination = (
        resolve_data_dir(runtime_root=runtime_root) / destination_name
    )
    destination.write_text(content, encoding="utf-8")
    return destination


def persist_tags_file(
    source_file: Path,
    runtime_root: Path | None = None,
) -> Path:
    return _persist_text_file(
        source_file=source_file,
        destination_name="tab_est.md",
        runtime_root=runtime_root,
    )


def persist_source_text(
    source_file: Path,
    runtime_root: Path | None = None,
) -> Path:
    return _persist_text_file(
        source_file=source_file,
        destination_name="source_text.md",
        runtime_root=runtime_root,
    )


def persist_target_text(
    source_file: Path,
    runtime_root: Path | None = None,
) -> Path:
    return _persist_text_file(
        source_file=source_file,
        destination_name="target_text.md",
        runtime_root=runtime_root,
    )
