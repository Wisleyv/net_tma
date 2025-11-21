from __future__ import annotations

from collections import defaultdict

from parser import alignment, annotations, segmentation


def _prepare_alignment_inputs(source_path: str, target_path: str):
    source_paragraphs = segmentation.segment_source(source_path)
    target_paragraphs = segmentation.segment_target(target_path)
    source_sections = alignment.detect_sections(source_paragraphs)
    target_sections = alignment.detect_sections(target_paragraphs)

    target_clean = annotations.clean_all(target_paragraphs)
    extracted = annotations.extract_annotations(target_paragraphs)

    annotations_map = defaultdict(list)
    for item in extracted:
        annotations_map[item["paragrafo_alvo_id"]].append(item)

    return (
        source_sections,
        target_sections,
        source_paragraphs,
        target_clean,
        annotations_map,
    )


def test_alignment_prefers_anchor_matches(
    source_fixture_path, target_fixture_path
):
    (
        source_sections,
        target_sections,
        source_paragraphs,
        target_clean,
        annotations_map,
    ) = _prepare_alignment_inputs(
        str(source_fixture_path), str(target_fixture_path)
    )

    result = alignment.align_paragraphs(
        source_sections=source_sections,
        target_sections=target_sections,
        source_paragraphs=source_paragraphs,
        target_clean=target_clean,
        annotations_map=annotations_map,
    )

    assert result["A_002"]["paragrafo_fonte_ids"] == ["F_002"]
    assert result["A_002"]["fonte_alinhamento_confiavel"] is True


def test_alignment_falls_back_to_similarity() -> None:
    source_sections = {"GLOBAL": ["F_001", "F_002"]}
    target_sections = {"GLOBAL": ["A_001"]}
    source_paragraphs = {
        "F_001": "Introducao padrao",
        "F_002": "Conteudo raro com expressao distinta e unica",
    }
    target_clean = {
        "A_001": "Conteudo raro com expressao distinta e unica",
    }
    annotations_map = defaultdict(list)

    result = alignment.align_paragraphs(
        source_sections=source_sections,
        target_sections=target_sections,
        source_paragraphs=source_paragraphs,
        target_clean=target_clean,
        annotations_map=annotations_map,
    )

    assert result["A_001"]["paragrafo_fonte_ids"] == ["F_002"]
    assert result["A_001"]["fonte_alinhamento_confiavel"] is True
