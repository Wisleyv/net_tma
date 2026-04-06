from __future__ import annotations

import json
from pathlib import Path

from scripts import validate_training_dataset as gate


def _base_metadata() -> dict:
    return {
        "projeto": "NET_TMA",
        "versao": "2.0",
        "idioma": "pt-BR",
        "descricao": "dataset de treino",
        "schema_version": "2.0.0",
        "dataset_version": "2026.03.31-a",
        "created_at": "2026-03-31T00:00:00Z",
    }


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    content = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
    path.write_text(content + "\n", encoding="utf-8")


def test_quality_gate_passes_for_valid_v2_dataset(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset_curated.json"
    target_path = tmp_path / "target.md"
    card_path = tmp_path / "dataset_card.md"
    train_path = tmp_path / "train.jsonl"
    valid_path = tmp_path / "validation.jsonl"
    test_path = tmp_path / "test.jsonl"

    payload = {
        "metadata": _base_metadata(),
        "amostras": [
            {
                "sample_id": "S001",
                "document_id": "DOC1",
                "split_group_id": "DOC1",
                "tag_code": "SL+",
                "label_scope": "automatic",
                "target_paragraph_id": "A_001",
                "target_text": "Texto alvo um",
                "target_span_text": "alvo um",
                "target_span_start": 6,
                "target_span_end": 14,
                "source_paragraph_ids": ["F_001"],
                "source_text": "Texto fonte um",
                "alignment_confidence": 0.95,
                "human_validated": True,
                "schema_version": "2.0.0",
                "parser_version": "parser-2.0",
                "created_at": "2026-03-31T00:00:00Z",
            },
            {
                "sample_id": "S002",
                "document_id": "DOC2",
                "split_group_id": "DOC2",
                "tag_code": "RF+",
                "label_scope": "automatic",
                "target_paragraph_id": "A_002",
                "target_text": "Texto alvo dois",
                "target_span_text": "alvo dois",
                "target_span_start": 6,
                "target_span_end": 15,
                "source_paragraph_ids": ["F_002"],
                "source_text": "Texto fonte dois",
                "alignment_confidence": 0.82,
                "human_validated": False,
                "schema_version": "2.0.0",
                "parser_version": "parser-2.0",
                "created_at": "2026-03-31T00:00:00Z",
            },
        ],
    }

    _write_json(dataset_path, payload)
    target_path.write_text("[SL+ termo]\n[RF+ frase]\n", encoding="utf-8")
    card_path.write_text(
        "# Dataset Card\n\n"
        "## Version\n2.0.0\n\n"
        "## Provenance\nManual + parser\n\n"
        "## Known limitations\nSmall corpus\n",
        encoding="utf-8",
    )

    _write_jsonl(train_path, [{"split_group_id": "DOC1"}])
    _write_jsonl(valid_path, [{"split_group_id": "DOC2"}])
    _write_jsonl(test_path, [{"split_group_id": "DOC3"}])

    report = gate.evaluate_dataset(
        dataset_path=dataset_path,
        target_markdown=target_path,
        dataset_card=card_path,
        train_jsonl=train_path,
        validation_jsonl=valid_path,
        test_jsonl=test_path,
        expect_supervised_export=True,
    )

    assert report.passed is True
    assert all(result.passed for result in report.gate_results)


def test_quality_gate_allows_diagnostic_out_of_scope_rows(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "dataset_curated.json"
    target_path = tmp_path / "target.md"
    card_path = tmp_path / "dataset_card.md"
    train_path = tmp_path / "train.jsonl"
    valid_path = tmp_path / "validation.jsonl"
    test_path = tmp_path / "test.jsonl"

    payload = {
        "metadata": _base_metadata(),
        "amostras": [
            {
                "sample_id": "S001",
                "document_id": "DOC1",
                "split_group_id": "DOC1",
                "tag_code": "SL+",
                "label_scope": "automatic",
                "target_paragraph_id": "A_001",
                "target_text": "Texto alvo um",
                "target_span_text": "alvo um",
                "source_paragraph_ids": ["F_001"],
                "source_text": "Texto fonte um",
                "alignment_confidence": 0.95,
                "human_validated": False,
                "schema_version": "2.0.0",
                "parser_version": "parser-2.0",
                "created_at": "2026-03-31T00:00:00Z",
            },
            {
                "sample_id": "D001",
                "document_id": "DOC1",
                "split_group_id": "DOC1",
                "tag_code": "OM+",
                "label_scope": "diagnostic",
                "target_paragraph_id": "A_001",
                "target_text": "Texto alvo um",
                "target_span_text": "corte",
                "source_paragraph_ids": [],
                "source_text": "",
                "alignment_confidence": 0.0,
                "human_validated": False,
                "schema_version": "2.0.0",
                "parser_version": "parser-2.0",
                "created_at": "2026-03-31T00:00:00Z",
            },
        ],
    }

    _write_json(dataset_path, payload)
    target_path.write_text("[SL+ termo]\n[OM+ corte]\n", encoding="utf-8")
    card_path.write_text(
        "# Dataset Card\n\n"
        "## Version\n2.0.0\n\n"
        "## Provenance\nManual + parser\n\n"
        "## Known limitations\nSmall corpus\n",
        encoding="utf-8",
    )

    _write_jsonl(train_path, [{"split_group_id": "DOC1"}])
    _write_jsonl(valid_path, [{"split_group_id": "DOC2"}])
    _write_jsonl(test_path, [{"split_group_id": "DOC3"}])

    report = gate.evaluate_dataset(
        dataset_path=dataset_path,
        target_markdown=target_path,
        dataset_card=card_path,
        train_jsonl=train_path,
        validation_jsonl=valid_path,
        test_jsonl=test_path,
        expect_supervised_export=True,
    )

    status = {result.name: result.passed for result in report.gate_results}
    assert report.passed is True
    assert status["out_of_scope_labels"] is True


def test_quality_gate_fails_on_blocking_issues(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset_bad.json"
    target_path = tmp_path / "target.md"
    card_path = tmp_path / "dataset_card.md"
    train_path = tmp_path / "train.jsonl"
    valid_path = tmp_path / "validation.jsonl"
    test_path = tmp_path / "test.jsonl"

    payload = {
        "metadata": _base_metadata(),
        "amostras": [
            {
                "sample_id": "B001",
                "document_id": "DOC1",
                "split_group_id": "DOC1",
                "tag_code": "OM+",
                "label_scope": "automatic",
                "target_paragraph_id": "A_001",
                "target_text": "Texto alvo",
                "target_span_text": "",
                "source_paragraph_ids": [],
                "source_text": "",
                "alignment_confidence": 0.0,
                "human_validated": False,
                "schema_version": "2.0.0",
                "parser_version": "parser-2.0",
                "created_at": "2026-03-31T00:00:00Z",
            }
        ],
    }

    _write_json(dataset_path, payload)
    target_path.write_text("[OM+ corte]\n[SL+ termo]\n", encoding="utf-8")
    card_path.write_text("# Card\n\n## Version\n2.0\n", encoding="utf-8")

    _write_jsonl(train_path, [{"split_group_id": "DOC1"}])
    _write_jsonl(valid_path, [{"split_group_id": "DOC1"}])
    _write_jsonl(test_path, [{"split_group_id": "DOC2"}])

    report = gate.evaluate_dataset(
        dataset_path=dataset_path,
        target_markdown=target_path,
        dataset_card=card_path,
        train_jsonl=train_path,
        validation_jsonl=valid_path,
        test_jsonl=test_path,
        expect_supervised_export=True,
    )

    assert report.passed is False
    status = {result.name: result.passed for result in report.gate_results}

    assert status["out_of_scope_labels"] is False
    assert status["parse_coverage"] is False
    assert status["split_leakage"] is False
    assert status["dataset_card_completeness"] is False
