from __future__ import annotations

import json
from pathlib import Path

from scripts import build_rf_counterexample_train as rfce


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    content = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text((content + "\n") if content else "", encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def test_build_rf_counterexample_train_adds_targeted_rows(
    tmp_path: Path,
) -> None:
    train_path = tmp_path / "train.jsonl"
    errors_path = tmp_path / "errors.json"
    output_path = tmp_path / "train_aug.jsonl"

    train_rows = [
        {
            "sample_id": "S001",
            "tag_code": "SL+",
            "target_text": "texto sl",
            "source_text": "fonte sl",
            "target_span_text": "span sl",
            "split": "train",
        },
        {
            "sample_id": "S002",
            "tag_code": "RD+",
            "target_text": "texto rd",
            "source_text": "fonte rd",
            "target_span_text": "span rd",
            "split": "train",
        },
        {
            "sample_id": "S003",
            "tag_code": "RF+",
            "target_text": "texto rf",
            "source_text": "fonte rf",
            "target_span_text": "span rf",
            "split": "train",
        },
    ]
    _write_jsonl(train_path, train_rows)

    _write_json(
        errors_path,
        {
            "source": "test",
            "bucket_counts": [
                {
                    "true_label": "SL+",
                    "predicted_label": "RF+",
                    "count": 2,
                },
                {
                    "true_label": "RD+",
                    "predicted_label": "RF+",
                    "count": 1,
                },
            ],
        },
    )

    summary = rfce.build_rf_counterexample_train(
        train_jsonl=train_path,
        error_buckets_json=errors_path,
        output_jsonl=output_path,
        predicted_label="RF+",
        max_per_label=1,
    )

    assert summary["input_rows"] == 3
    assert summary["augmented_rows"] == 2
    assert summary["output_rows"] == 5
    assert summary["target_labels"] == ["RD+", "SL+"]

    rows = _read_jsonl(output_path)
    assert len(rows) == 5
    augmented = [
        row
        for row in rows
        if (
            str(row.get("sample_id") or "").endswith("RFCE01")
            or str(row.get("sample_id") or "").endswith("RFCE02")
        )
    ]
    assert len(augmented) == 2
    assert all(row.get("split") == "train" for row in augmented)
