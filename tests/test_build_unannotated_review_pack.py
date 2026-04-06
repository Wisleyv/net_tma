from __future__ import annotations

import json
from pathlib import Path

from scripts import build_unannotated_review_pack as intake


def _write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)


def test_build_unannotated_review_pack_creates_outputs(
    tmp_path: Path,
) -> None:
    source_input = tmp_path / "source.txt"
    target_input = tmp_path / "target.txt"

    source_normalized = tmp_path / "out" / "source_norm.md"
    target_normalized = tmp_path / "out" / "target_norm.md"
    report_json = tmp_path / "out" / "review_pack.json"
    review_md = tmp_path / "out" / "review_pack.md"
    target_template = tmp_path / "out" / "target_template.md"

    _write_text(
        source_input,
        "Titulo\n\nParagrafo fonte um.\n\nParagrafo fonte dois.",
    )
    _write_text(
        target_input,
        "Titulo\n\nParagrafo alvo um.\n\nParagrafo alvo dois.",
    )

    payload = intake.build_unannotated_review_pack(
        source_input=source_input,
        target_input=target_input,
        source_normalized=source_normalized,
        target_normalized=target_normalized,
        report_json=report_json,
        review_md=review_md,
        target_template_md=target_template,
    )

    assert source_normalized.exists()
    assert target_normalized.exists()
    assert report_json.exists()
    assert review_md.exists()
    assert target_template.exists()

    summary = payload["summary"]
    assert summary["counts"]["source_paragraphs"] == 3
    assert summary["counts"]["target_paragraphs"] == 3

    report_payload = json.loads(report_json.read_text(encoding="utf-8"))
    assert len(report_payload["pairs"]) == 3

    review_text = review_md.read_text(encoding="utf-8")
    assert "Unannotated Pair Review Pack" in review_text

    template_text = target_template.read_text(encoding="utf-8")
    assert "<!-- A_001" in template_text


def test_build_unannotated_review_pack_normalizes_cp1252_input(
    tmp_path: Path,
) -> None:
    source_input = tmp_path / "source_cp1252.txt"
    target_input = tmp_path / "target_cp1252.txt"

    source_normalized = tmp_path / "out" / "source_norm.md"
    target_normalized = tmp_path / "out" / "target_norm.md"
    report_json = tmp_path / "out" / "review_pack.json"
    review_md = tmp_path / "out" / "review_pack.md"
    target_template = tmp_path / "out" / "target_template.md"

    source_input.write_bytes("Ação e coração.".encode("cp1252"))
    target_input.write_bytes("Ação simples.".encode("cp1252"))

    intake.build_unannotated_review_pack(
        source_input=source_input,
        target_input=target_input,
        source_normalized=source_normalized,
        target_normalized=target_normalized,
        report_json=report_json,
        review_md=review_md,
        target_template_md=target_template,
    )

    assert "Ação" in source_normalized.read_text(encoding="utf-8")
    assert "Ação" in target_normalized.read_text(encoding="utf-8")


def test_split_paragraphs_falls_back_when_blank_split_is_too_coarse() -> None:
    lines = [f"linha {idx}" for idx in range(1, 31)]
    text = "\n".join(lines[0:10]) + "\n\n" + "\n".join(lines[10:20])
    text += "\n\n" + "\n".join(lines[20:30])

    parts = intake._split_paragraphs(text)

    assert len(parts) == 30
    assert parts[0] == "linha 1"
    assert parts[-1] == "linha 30"
