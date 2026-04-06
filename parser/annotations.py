"""Extraction of `[TAG+ ...]` annotations from the target text."""

from __future__ import annotations

import re
from typing import Dict, List

_BLOCK_PATTERN = re.compile(r"\[(?P<inner>.+?)\]", re.DOTALL)
_HEADER_PATTERN = re.compile(
    r"^(?P<tags>[A-Z]{2,4}\+(?:/[A-Z]{2,4}\+)*)(?P<body>\s+.*)?$",
    re.DOTALL,
)


class Annotation(dict):
    """Simple dict subclass for type hinting convenience."""


def _collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _parse_annotation_block(
    inner_text: str,
) -> tuple[list[str], str] | None:
    """Parse a bracket block as annotation header + optional body.

    Supported patterns:
    - [TAG+ body]
    - [TAG+]
    - [TAG1+/TAG2+ body]
    """

    header_match = _HEADER_PATTERN.match(inner_text.strip())
    if not header_match:
        return None

    tags = header_match.group("tags").split("/")
    body_raw = header_match.group("body") or ""
    body = _collapse_ws(body_raw)
    return tags, body


def _strip_known_annotation_blocks(text: str) -> str:
    """Remove valid annotation blocks from text and keep other brackets."""

    chunks: list[str] = []
    last_end = 0
    for block in _BLOCK_PATTERN.finditer(text):
        chunks.append(text[last_end:block.start()])
        parsed = _parse_annotation_block(block.group("inner"))
        if parsed is None:
            chunks.append(block.group(0))
        else:
            chunks.append(" ")
        last_end = block.end()

    chunks.append(text[last_end:])
    return "".join(chunks)


def _extract_target_span(paragraph_text: str, tag_start: int) -> str:
    """Grab a short snippet of the target text preceding the tag marker."""

    before = _strip_known_annotation_blocks(paragraph_text[:tag_start]).rstrip()
    if not before:
        return ""

    # Prefer the trailing sentence fragment when punctuation is available.
    sentence_parts = re.split(r"(?<=[\.!?])\s+", before)
    candidate = sentence_parts[-1].strip() if sentence_parts else before
    if len(candidate.split()) < 3:
        words = before.split()
        candidate = " ".join(words[-12:]) if words else before
    return candidate.strip()


def extract_annotations(target_paragraphs: Dict[str, str]) -> List[Annotation]:
    """Return a list of annotations extracted from the target paragraphs."""

    annotations: List[Annotation] = []
    for par_id, text in target_paragraphs.items():
        for block in _BLOCK_PATTERN.finditer(text):
            parsed = _parse_annotation_block(block.group("inner"))
            if parsed is None:
                continue
            tags, body = parsed
            for tag in tags:
                annotations.append(
                    Annotation(
                        {
                            "tag": tag,
                            "conteudo_bruto": body,
                            "paragrafo_alvo_id": par_id,
                            "posicao_inicio": block.start(),
                            "posicao_fim": block.end(),
                            "trecho_alvo": _extract_target_span(
                                text, block.start()
                            ),
                        }
                    )
                )
    return annotations


def clean_paragraph(paragraph_text: str) -> str:
    """Remove `[TAG+ ...]` blocks from a paragraph while retaining spacing."""

    cleaned = _strip_known_annotation_blocks(paragraph_text)
    return _collapse_ws(cleaned)


def clean_all(target_paragraphs: Dict[str, str]) -> Dict[str, str]:
    """Return a dict of cleaned paragraphs with the same IDs."""

    return {
        par_id: clean_paragraph(text)
        for par_id, text in target_paragraphs.items()
    }
