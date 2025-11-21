"""Best-effort paragraph alignment using headings, anchors, and similarity."""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Dict, List, Sequence, Tuple, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - hinting only
    from .annotations import Annotation

_SIMILARITY_THRESHOLD = 0.55
_SIMILARITY_WINDOW = 3
_MIN_ANCHOR_LEN = 4


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _canonicalize_heading(text: str) -> str:
    cleaned = _strip_accents(text)
    cleaned = re.sub(r"[^A-Z0-9\s]", " ", cleaned.upper())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "GLOBAL"


def _looks_like_heading(paragraph: str) -> bool:
    stripped = paragraph.strip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        stripped = stripped.lstrip("#").strip()
    letters = [ch for ch in stripped if ch.isalpha()]
    if not letters:
        return False
    upper_ratio = sum(1 for ch in letters if ch.isupper()) / len(letters)
    return upper_ratio >= 0.75 and len(stripped.split()) <= 8


def detect_sections(paragraphs: Dict[str, str]) -> Dict[str, List[str]]:
    """Group paragraph IDs by detected sections (headings)."""

    sections: Dict[str, List[str]] = {"GLOBAL": []}
    current_section = "GLOBAL"
    for par_id, text in paragraphs.items():
        if _looks_like_heading(text):
            current_section = _canonicalize_heading(text)
            sections.setdefault(current_section, [])
            continue
        sections.setdefault(current_section, []).append(par_id)
    return sections


def _normalize_anchor(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) < _MIN_ANCHOR_LEN:
        return ""
    return _strip_accents(collapsed).lower()


def _search_window(length: int, last_idx: int) -> List[int]:
    if length == 0:
        return []
    if last_idx < 0:
        return list(range(min(_SIMILARITY_WINDOW, length)))
    start = max(0, last_idx - 1)
    end = min(length, last_idx + _SIMILARITY_WINDOW)
    return list(range(start, end))


def _match_by_anchor(
    anchors: Sequence[str],
    source_ids: Sequence[str],
    source_paragraphs: Dict[str, str],
    last_idx: int,
) -> Tuple[str, int] | tuple[None, None]:
    if not anchors or not source_ids:
        return None, None
    window = _search_window(len(source_ids), last_idx)
    for anchor in anchors:
        normalized_anchor = _normalize_anchor(anchor)
        if not normalized_anchor:
            continue
        for idx in window:
            source_text = source_paragraphs.get(source_ids[idx], "")
            normalized_source = _strip_accents(source_text).lower()
            if normalized_anchor in normalized_source:
                return source_ids[idx], idx
    return None, None


def _match_by_similarity(
    target_id: str,
    source_ids: Sequence[str],
    source_paragraphs: Dict[str, str],
    target_clean: Dict[str, str],
    last_idx: int,
) -> Tuple[str, int] | tuple[None, None]:
    if not source_ids:
        return None, None
    target_text = target_clean.get(target_id, "").strip()
    if not target_text:
        return None, None
    window = _search_window(len(source_ids), last_idx)
    best_idx = None
    best_ratio = 0.0
    for idx in window:
        candidate_text = source_paragraphs.get(source_ids[idx], "")
        ratio = SequenceMatcher(None, target_text, candidate_text).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_idx = idx
    if best_idx is not None and best_ratio >= _SIMILARITY_THRESHOLD:
        return source_ids[best_idx], best_idx
    return None, None


def _collect_anchor_texts(annotations: Sequence["Annotation"]) -> List[str]:
    anchors: List[str] = []
    for annotation in annotations:
        if annotation.get("tag") in {"OM+", "PRO+"}:
            continue
        raw = annotation.get("conteudo_bruto", "").strip()
        if len(raw) >= _MIN_ANCHOR_LEN:
            anchors.append(raw)
    return anchors


def align_paragraphs(
    source_sections: Dict[str, List[str]],
    target_sections: Dict[str, List[str]],
    source_paragraphs: Dict[str, str],
    target_clean: Dict[str, str],
    annotations_map: Dict[str, List["Annotation"]],
) -> Dict[str, Dict[str, object]]:
    """Align target paragraphs to source paragraphs via cascaded heuristics."""

    alignment: Dict[str, Dict[str, object]] = {}
    last_idx_per_section: Dict[str, int] = {}

    for section, target_ids in target_sections.items():
        source_ids = source_sections.get(section, [])
        last_idx = last_idx_per_section.get(section, -1)
        for target_id in target_ids:
            annotations = annotations_map.get(target_id, [])
            anchors = _collect_anchor_texts(annotations)
            match_id, matched_idx = _match_by_anchor(
                anchors, source_ids, source_paragraphs, last_idx
            )
            confident = match_id is not None

            if match_id is None:
                match_id, matched_idx = _match_by_similarity(
                    target_id,
                    source_ids,
                    source_paragraphs,
                    target_clean,
                    last_idx,
                )
                confident = match_id is not None

            if match_id is not None and matched_idx is not None:
                alignment[target_id] = {
                    "paragrafo_fonte_ids": [match_id],
                    "fonte_alinhamento_confiavel": confident,
                }
                last_idx = matched_idx
            else:
                alignment[target_id] = {
                    "paragrafo_fonte_ids": [],
                    "fonte_alinhamento_confiavel": False,
                }
        last_idx_per_section[section] = last_idx

    # Track paragraphs cujas secoes nao existem na fonte
    for section, target_ids in target_sections.items():
        if section in source_sections:
            continue
        for target_id in target_ids:
            alignment.setdefault(
                target_id,
                {
                    "paragrafo_fonte_ids": [],
                    "fonte_alinhamento_confiavel": False,
                },
            )

    return alignment
