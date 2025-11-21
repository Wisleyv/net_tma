from __future__ import annotations

from parser import annotations, segmentation


def test_segment_source_assigns_prefixed_ids(source_fixture_path):
    segments = segmentation.segment_source(str(source_fixture_path))
    assert list(segments.keys())[0] == "F_001"
    assert len(segments) >= 5  # headings + paragraphs
    assert "texto original complexo" in segments["F_002"]


def test_extract_annotations_handles_multiline_tags(target_fixture_path):
    target_paragraphs = segmentation.segment_target(str(target_fixture_path))
    extracted = annotations.extract_annotations(target_paragraphs)
    tags = {item["tag"] for item in extracted}

    assert tags == {"SL+", "RD+", "OM+"}
    sl_annotation = next(item for item in extracted if item["tag"] == "SL+")
    assert sl_annotation["trecho_alvo"].startswith("Este paragrafo adaptado")

    rd_annotation = next(item for item in extracted if item["tag"] == "RD+")
    assert "reorganizamos" in rd_annotation["conteudo_bruto"]

    cleaned = annotations.clean_all(target_paragraphs)
    assert "[SL+" not in cleaned["A_002"]
    assert cleaned["A_002"].startswith(
        "Este paragrafo adaptado reescreve o termo"
    )
