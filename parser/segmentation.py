"""Paragraph-level segmentation for fonte e alvo."""

from __future__ import annotations

import re
from typing import Dict

from .io_utils import read_text

_PARAGRAPH_SPLIT_RE = re.compile(r"\n{2,}")


def _split_paragraphs(text: str) -> list[str]:
    """Split text on blank lines, stripping whitespace."""
    raw_parts = _PARAGRAPH_SPLIT_RE.split(text.strip())
    return [part.strip() for part in raw_parts if part.strip()]


def _enumerate_paragraphs(paragraphs: list[str], prefix: str) -> Dict[str, str]:
    """Assign sequential IDs (prefix + 3-digit index) to each paragraph."""
    return {f"{prefix}_{idx:03d}": paragraph for idx, paragraph in enumerate(paragraphs, start=1)}


def segment_source(source_path: str) -> Dict[str, str]:
    """Segmenta `patriotismo_st.md` em parágrafos indexados."""
    text = read_text(source_path)
    return _enumerate_paragraphs(_split_paragraphs(text), prefix="F")


def segment_target(target_path: str) -> Dict[str, str]:
    """Segmenta `patriotismo_tt.md` em parágrafos indexados."""
    text = read_text(target_path)
    return _enumerate_paragraphs(_split_paragraphs(text), prefix="A")
