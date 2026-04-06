from __future__ import annotations

import json
from pathlib import Path

from scripts import build_supervised_exports as exports


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_build_supervised_exports_filters_and_dedupes(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset_curated.json"
    output_dataset = tmp_path / "dataset_supervised.json"
    train_path = tmp_path / "train.jsonl"
    valid_path = tmp_path / "validation.jsonl"
    test_path = tmp_path / "test.jsonl"
    report_path = tmp_path / "summary.json"

    payload = {
        "metadata": {
            "projeto": "NET_TMA",
            "versao": "0.1",
            "idioma": "pt-BR",
            "descricao": "test payload",
        },
        "amostras": [
            {
                "sample_id": "S001",
                "document_id": "DOC1",
                "split_group_id": "DOC1",
                "tag_code": "SL+",
                "label_scope": "automatic",
                "target_paragraph_id": "A_001",
                "target_span_text": "span-a",
                "source_paragraph_ids": ["F_001"],
                "source_text": "fonte",
            },
            {
                "sample_id": "S001_DUP",
                "document_id": "DOC1",
                "split_group_id": "DOC1",
                "tag_code": "SL+",
                "label_scope": "automatic",
                "target_paragraph_id": "A_001",
                "target_span_text": "span-a",
                "source_paragraph_ids": ["F_001"],
                "source_text": "fonte",
            },
            {
                "sample_id": "D001",
                "document_id": "DOC1",
                "split_group_id": "DOC1",
                "tag_code": "OM+",
                "label_scope": "diagnostic",
                "target_paragraph_id": "A_001",
                "target_span_text": "cut",
                "source_paragraph_ids": [],
                "source_text": "",
            },
        ],
    }

    _write_json(dataset_path, payload)

    summary = exports.build_supervised_exports(
        dataset_path=dataset_path,
        output_dataset=output_dataset,
        train_jsonl=train_path,
        validation_jsonl=valid_path,
        test_jsonl=test_path,
        report_json=report_path,
    )

    assert summary["input_rows"] == 3
    assert summary["filtered_supervised_rows"] == 2
    assert summary["deduped_supervised_rows"] == 1
    assert summary["removed_duplicates"] == 1

    supervised = json.loads(output_dataset.read_text(encoding="utf-8"))
    rows = supervised["amostras"]
    assert len(rows) == 1
    assert rows[0]["tag_code"] == "SL+"
    assert rows[0]["label_scope"] == "automatic"
    assert rows[0]["split"] in {"train", "validation", "test"}

    assert report_path.exists()
    assert train_path.exists()
    assert valid_path.exists()
    assert test_path.exists()


def test_build_supervised_exports_supports_custom_group_field(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "dataset_curated.json"
    output_dataset = tmp_path / "dataset_supervised.json"
    train_path = tmp_path / "train.jsonl"
    valid_path = tmp_path / "validation.jsonl"
    test_path = tmp_path / "test.jsonl"
    report_path = tmp_path / "summary.json"

    rows: list[dict] = []
    for index in range(1, 8):
        rows.append(
            {
                "sample_id": f"S{index:03d}",
                "document_id": "DOC1",
                "split_group_id": "DOC1",
                "tag_code": "SL+" if index % 2 else "RF+",
                "label_scope": "automatic",
                "target_paragraph_id": f"A_{index:03d}",
                "target_span_text": f"span-{index}",
                "source_paragraph_ids": [f"F_{index:03d}"],
                "source_text": f"fonte-{index}",
            }
        )

    payload = {
        "metadata": {
            "projeto": "NET_TMA",
            "versao": "0.1",
            "idioma": "pt-BR",
            "descricao": "test payload",
        },
        "amostras": rows,
    }
    _write_json(dataset_path, payload)

    summary = exports.build_supervised_exports(
        dataset_path=dataset_path,
        output_dataset=output_dataset,
        train_jsonl=train_path,
        validation_jsonl=valid_path,
        test_jsonl=test_path,
        report_json=report_path,
        group_field="target_paragraph_id",
    )

    assert summary["group_field"] == "target_paragraph_id"
    assert summary["group_count"] == 7
    assert summary["split_counts"]["validation"] > 0
    assert summary["split_counts"]["test"] > 0

    supervised = json.loads(output_dataset.read_text(encoding="utf-8"))
    assert supervised["metadata"]["split_group_field"] == "target_paragraph_id"
    supervised_groups = {
        row["split_group_id"] for row in supervised["amostras"]
    }
    assert "DOC1" not in supervised_groups


def test_build_supervised_exports_respects_min_holdout_rows(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "dataset_curated.json"
    output_dataset = tmp_path / "dataset_supervised.json"
    train_path = tmp_path / "train.jsonl"
    valid_path = tmp_path / "validation.jsonl"
    test_path = tmp_path / "test.jsonl"
    report_path = tmp_path / "summary.json"

    group_ids = [
        "A_001",
        "A_001",
        "A_001",
        "A_002",
        "A_002",
        "A_003",
        "A_004",
        "A_005",
    ]
    rows: list[dict] = []
    for index, group_id in enumerate(group_ids, start=1):
        rows.append(
            {
                "sample_id": f"S{index:03d}",
                "document_id": "DOC1",
                "split_group_id": "DOC1",
                "tag_code": "SL+" if index % 2 else "RF+",
                "label_scope": "automatic",
                "target_paragraph_id": group_id,
                "target_span_text": f"span-{index}",
                "source_paragraph_ids": [f"F_{index:03d}"],
                "source_text": f"fonte-{index}",
            }
        )

    payload = {
        "metadata": {
            "projeto": "NET_TMA",
            "versao": "0.1",
            "idioma": "pt-BR",
            "descricao": "test payload",
        },
        "amostras": rows,
    }
    _write_json(dataset_path, payload)

    summary = exports.build_supervised_exports(
        dataset_path=dataset_path,
        output_dataset=output_dataset,
        train_jsonl=train_path,
        validation_jsonl=valid_path,
        test_jsonl=test_path,
        report_json=report_path,
        group_field="target_paragraph_id",
        min_validation_rows=2,
        min_test_rows=2,
    )

    assert summary["min_validation_rows"] == 2
    assert summary["min_test_rows"] == 2
    assert summary["split_counts"]["validation"] >= 2
    assert summary["split_counts"]["test"] >= 2
    assert summary["split_counts"]["train"] > 0
    assert "train_label_coverage" in summary


def test_build_supervised_exports_prioritizes_train_label_coverage(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "dataset_curated.json"
    output_dataset = tmp_path / "dataset_supervised.json"
    train_path = tmp_path / "train.jsonl"
    valid_path = tmp_path / "validation.jsonl"
    test_path = tmp_path / "test.jsonl"
    report_path = tmp_path / "summary.json"

    rows = [
        {
            "sample_id": "S001",
            "document_id": "DOC1",
            "split_group_id": "DOC1",
            "tag_code": "SL+",
            "label_scope": "automatic",
            "target_paragraph_id": "A_001",
            "target_span_text": "span-1",
            "source_paragraph_ids": ["F_001"],
            "source_text": "fonte-1",
        },
        {
            "sample_id": "S002",
            "document_id": "DOC1",
            "split_group_id": "DOC1",
            "tag_code": "MOD+",
            "label_scope": "automatic",
            "target_paragraph_id": "A_001",
            "target_span_text": "span-2",
            "source_paragraph_ids": ["F_001"],
            "source_text": "fonte-2",
        },
        {
            "sample_id": "S003",
            "document_id": "DOC1",
            "split_group_id": "DOC1",
            "tag_code": "RF+",
            "label_scope": "automatic",
            "target_paragraph_id": "A_002",
            "target_span_text": "span-3",
            "source_paragraph_ids": ["F_002"],
            "source_text": "fonte-3",
        },
        {
            "sample_id": "S004",
            "document_id": "DOC1",
            "split_group_id": "DOC1",
            "tag_code": "RF+",
            "label_scope": "automatic",
            "target_paragraph_id": "A_002",
            "target_span_text": "span-4",
            "source_paragraph_ids": ["F_002"],
            "source_text": "fonte-4",
        },
        {
            "sample_id": "S005",
            "document_id": "DOC1",
            "split_group_id": "DOC1",
            "tag_code": "RD+",
            "label_scope": "automatic",
            "target_paragraph_id": "A_003",
            "target_span_text": "span-5",
            "source_paragraph_ids": ["F_003"],
            "source_text": "fonte-5",
        },
        {
            "sample_id": "S006",
            "document_id": "DOC1",
            "split_group_id": "DOC1",
            "tag_code": "RD+",
            "label_scope": "automatic",
            "target_paragraph_id": "A_003",
            "target_span_text": "span-6",
            "source_paragraph_ids": ["F_003"],
            "source_text": "fonte-6",
        },
        {
            "sample_id": "S007",
            "document_id": "DOC1",
            "split_group_id": "DOC1",
            "tag_code": "SL+",
            "label_scope": "automatic",
            "target_paragraph_id": "A_004",
            "target_span_text": "span-7",
            "source_paragraph_ids": ["F_004"],
            "source_text": "fonte-7",
        },
        {
            "sample_id": "S008",
            "document_id": "DOC1",
            "split_group_id": "DOC1",
            "tag_code": "SL+",
            "label_scope": "automatic",
            "target_paragraph_id": "A_004",
            "target_span_text": "span-8",
            "source_paragraph_ids": ["F_004"],
            "source_text": "fonte-8",
        },
        {
            "sample_id": "S009",
            "document_id": "DOC1",
            "split_group_id": "DOC1",
            "tag_code": "RF+",
            "label_scope": "automatic",
            "target_paragraph_id": "A_005",
            "target_span_text": "span-9",
            "source_paragraph_ids": ["F_005"],
            "source_text": "fonte-9",
        },
        {
            "sample_id": "S010",
            "document_id": "DOC1",
            "split_group_id": "DOC1",
            "tag_code": "RF+",
            "label_scope": "automatic",
            "target_paragraph_id": "A_005",
            "target_span_text": "span-10",
            "source_paragraph_ids": ["F_005"],
            "source_text": "fonte-10",
        },
    ]

    payload = {
        "metadata": {
            "projeto": "NET_TMA",
            "versao": "0.1",
            "idioma": "pt-BR",
            "descricao": "coverage payload",
        },
        "amostras": rows,
    }
    _write_json(dataset_path, payload)

    summary = exports.build_supervised_exports(
        dataset_path=dataset_path,
        output_dataset=output_dataset,
        train_jsonl=train_path,
        validation_jsonl=valid_path,
        test_jsonl=test_path,
        report_json=report_path,
        group_field="target_paragraph_id",
        min_validation_rows=2,
        min_test_rows=2,
    )

    coverage = summary["train_label_coverage"]
    assert coverage["covered"] == coverage["total"]
    assert coverage["missing_labels"] == []
