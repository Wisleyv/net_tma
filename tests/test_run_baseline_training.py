from __future__ import annotations

import json
from pathlib import Path

from scripts import run_baseline_training as baseline


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    content = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text((content + "\n") if content else "", encoding="utf-8")


def _train_rows() -> list[dict]:
    return [
        {
            "sample_id": "S001",
            "tag_code": "RF+",
            "target_text": "texto rf um",
            "source_text": "fonte rf um",
            "target_span_text": "rf",
        },
        {
            "sample_id": "S002",
            "tag_code": "RF+",
            "target_text": "texto rf dois",
            "source_text": "fonte rf dois",
            "target_span_text": "rf",
        },
        {
            "sample_id": "S003",
            "tag_code": "SL+",
            "target_text": "texto sl um",
            "source_text": "fonte sl um",
            "target_span_text": "sl",
        },
        {
            "sample_id": "S004",
            "tag_code": "SL+",
            "target_text": "texto sl dois",
            "source_text": "fonte sl dois",
            "target_span_text": "sl",
        },
        {
            "sample_id": "S005",
            "tag_code": "RD+",
            "target_text": "texto rd um",
            "source_text": "fonte rd um",
            "target_span_text": "rd",
        },
        {
            "sample_id": "S006",
            "tag_code": "RD+",
            "target_text": "texto rd dois",
            "source_text": "fonte rd dois",
            "target_span_text": "rd",
        },
    ]


def test_baseline_training_writes_reports(tmp_path: Path) -> None:
    train_path = tmp_path / "train.jsonl"
    validation_path = tmp_path / "validation.jsonl"
    test_path = tmp_path / "test.jsonl"
    report_path = tmp_path / "reports" / "baseline_model_report.json"
    eval_md_path = tmp_path / "docs" / "eval_report.md"
    errors_path = tmp_path / "reports" / "baseline_error_buckets.json"

    _write_jsonl(train_path, _train_rows())
    _write_jsonl(validation_path, _train_rows()[0:3])
    _write_jsonl(test_path, _train_rows()[3:6])

    report = baseline.run_baseline_training(
        train_jsonl=train_path,
        validation_jsonl=validation_path,
        test_jsonl=test_path,
        report_json=report_path,
        eval_report_md=eval_md_path,
        errors_json=errors_path,
    )

    assert report_path.exists()
    assert eval_md_path.exists()
    assert errors_path.exists()

    assert report["splits"]["validation"]["available"] is True
    assert report["splits"]["test"]["available"] is True
    assert report["primary_evaluation"]["source"] == "test"

    eval_md_text = eval_md_path.read_text(encoding="utf-8")
    assert "# Baseline Evaluation Report" in eval_md_text
    assert "## Per-Tag Metrics" in eval_md_text


def test_baseline_training_falls_back_to_cross_validation(
    tmp_path: Path,
) -> None:
    train_path = tmp_path / "train.jsonl"
    validation_path = tmp_path / "validation.jsonl"
    test_path = tmp_path / "test.jsonl"
    report_path = tmp_path / "reports" / "baseline_model_report.json"
    eval_md_path = tmp_path / "docs" / "eval_report.md"
    errors_path = tmp_path / "reports" / "baseline_error_buckets.json"

    _write_jsonl(train_path, _train_rows())
    _write_jsonl(validation_path, [])
    _write_jsonl(test_path, [])

    report = baseline.run_baseline_training(
        train_jsonl=train_path,
        validation_jsonl=validation_path,
        test_jsonl=test_path,
        report_json=report_path,
        eval_report_md=eval_md_path,
        errors_json=errors_path,
    )

    assert report["splits"]["validation"]["available"] is False
    assert report["splits"]["test"]["available"] is False
    assert report["cross_validation"]["available"] is True
    assert report["primary_evaluation"]["source"] == "cross_validation"

    notes = report.get("notes", [])
    assert any("Validation split is empty" in note for note in notes)
    assert any("Test split is empty" in note for note in notes)


def test_baseline_training_reports_unseen_holdout_labels(
    tmp_path: Path,
) -> None:
    train_path = tmp_path / "train.jsonl"
    validation_path = tmp_path / "validation.jsonl"
    test_path = tmp_path / "test.jsonl"
    report_path = tmp_path / "reports" / "baseline_model_report.json"
    eval_md_path = tmp_path / "docs" / "eval_report.md"
    errors_path = tmp_path / "reports" / "baseline_error_buckets.json"

    train_rows = _train_rows()
    unseen_validation_rows = [
        {
            "sample_id": "S100",
            "tag_code": "RP+",
            "target_text": "texto rp valid",
            "source_text": "fonte rp valid",
            "target_span_text": "rp",
        }
    ]
    unseen_test_rows = [
        {
            "sample_id": "S101",
            "tag_code": "DL+",
            "target_text": "texto dl test",
            "source_text": "fonte dl test",
            "target_span_text": "dl",
        }
    ]

    _write_jsonl(train_path, train_rows)
    _write_jsonl(validation_path, unseen_validation_rows)
    _write_jsonl(test_path, unseen_test_rows)

    report = baseline.run_baseline_training(
        train_jsonl=train_path,
        validation_jsonl=validation_path,
        test_jsonl=test_path,
        report_json=report_path,
        eval_report_md=eval_md_path,
        errors_json=errors_path,
        min_primary_support=1,
    )

    validation_per_tag = report["splits"]["validation"]["metrics"]["per_tag"]
    test_per_tag = report["splits"]["test"]["metrics"]["per_tag"]

    assert validation_per_tag["RP+"]["support"] == 1
    assert test_per_tag["DL+"]["support"] == 1

    notes = report.get("notes", [])
    assert any(
        "Validation split contains labels unseen in train" in n
        for n in notes
    )
    assert any(
        "Test split contains labels unseen in train" in n
        for n in notes
    )
