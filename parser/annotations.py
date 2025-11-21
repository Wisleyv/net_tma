"""Extraction of `[TAG+ ...]` annotations from the target text."""

from __future__ import annotations

import re
from typing import Dict, List

_TAG_PATTERN = re.compile(
    r"\[(?P<tag>[A-Z]{2,4}\+)\s(?P<body>.+?)\]", re.DOTALL
)


class Annotation(dict):
    """Simple dict subclass for type hinting convenience."""


def _collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_target_span(paragraph_text: str, tag_start: int) -> str:
    """Grab a short snippet of the target text preceding the tag marker."""

    before = paragraph_text[:tag_start].rstrip()
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
        for match in _TAG_PATTERN.finditer(text):
            tag = match.group("tag")
            body = _collapse_ws(match.group("body"))
            annotations.append(
                Annotation(
                    {
                        "tag": tag,
                        "conteudo_bruto": body,
                        "paragrafo_alvo_id": par_id,
                        "posicao_inicio": match.start(),
                        "posicao_fim": match.end(),
                        "trecho_alvo": _extract_target_span(
                            text, match.start()
                        ),
                    }
                )
            )
    return annotations


def clean_paragraph(paragraph_text: str) -> str:
    """Remove `[TAG+ ...]` blocks from a paragraph while retaining spacing."""

    cleaned = _TAG_PATTERN.sub(" ", paragraph_text)
    return _collapse_ws(cleaned)


def clean_all(target_paragraphs: Dict[str, str]) -> Dict[str, str]:
    """Return a dict of cleaned paragraphs with the same IDs."""

    return {
        par_id: clean_paragraph(text)
        for par_id, text in target_paragraphs.items()
    }
