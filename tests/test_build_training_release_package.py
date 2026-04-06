from __future__ import annotations

import json
from pathlib import Path

from scripts import build_training_release_package as release_builder


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_release_package_locks_and_copies(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset_curated.json"
    supervised_path = tmp_path / "dataset_supervised.json"
    train_path = tmp_path / "train.jsonl"
    validation_path = tmp_path / "validation.jsonl"
    test_path = tmp_path / "test.jsonl"
    dataset_card = tmp_path / "docs" / "dataset_card.md"
    gate_report = tmp_path / "reports" / "training_data_gate_report.json"
    phase3_report = tmp_path / "reports" / "phase3_export_summary.json"

    dataset_payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "dataset_version": "old-version",
        },
        "amostras": [
            {
                "sample_id": "S1",
                "schema_version": "1.0.0",
                "tag_code": "SL+",
            }
        ],
    }
    supervised_payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "dataset_version": "old-version",
        },
        "amostras": [
            {
                "sample_id": "S1",
                "schema_version": "1.0.0",
                "tag_code": "SL+",
            }
        ],
    }
    _write_json(dataset_path, dataset_payload)
    _write_json(supervised_path, supervised_payload)

    train_path.write_text('{"sample_id":"S1"}\n', encoding="utf-8")
    validation_path.write_text("", encoding="utf-8")
    test_path.write_text("", encoding="utf-8")

    dataset_card.parent.mkdir(parents=True, exist_ok=True)
    dataset_card.write_text(
        """# Dataset Card

## Version

- schema_version: 1.0.0
- dataset_version: old-version
- generated_at: 2026-03-31
""",
        encoding="utf-8",
    )

    _write_json(
        gate_report,
        {
            "passed": True,
            "gate_results": [
                {"name": "a", "passed": True},
                {"name": "b", "passed": True},
            ],
        },
    )
    _write_json(
        phase3_report,
        {
            "input_rows": 1,
            "deduped_supervised_rows": 1,
        },
    )

    summary = release_builder.build_training_release_package(
        dataset_path=dataset_path,
        supervised_dataset_path=supervised_path,
        train_jsonl_path=train_path,
        validation_jsonl_path=validation_path,
        test_jsonl_path=test_path,
        dataset_card_path=dataset_card,
        gate_report_path=gate_report,
        phase3_report_path=phase3_report,
        output_root=tmp_path / "releases",
        dataset_version="2026.04.01-a",
        schema_version="2.0.0",
        release_id="2026.04.01-a",
    )

    assert summary["package_path"].exists()
    assert summary["manifest_path"].exists()

    locked_dataset = _read_json(dataset_path)
    assert locked_dataset["metadata"]["dataset_version"] == "2026.04.01-a"
    assert locked_dataset["metadata"]["schema_version"] == "2.0.0"
    assert "release_locked_at" in locked_dataset["metadata"]
    assert locked_dataset["amostras"][0]["schema_version"] == "2.0.0"

    locked_supervised = _read_json(supervised_path)
    assert locked_supervised["metadata"]["dataset_version"] == "2026.04.01-a"

    card_text = dataset_card.read_text(encoding="utf-8")
    assert "- schema_version: 2.0.0" in card_text
    assert "- dataset_version: 2026.04.01-a" in card_text
    assert "- generated_at: 2026-" in card_text

    manifest = _read_json(summary["manifest_path"])
    assert manifest["release_id"] == "2026.04.01-a"
    assert manifest["counts"]["curated_rows"] == 1
    assert manifest["counts"]["supervised_rows"] == 1
    assert manifest["counts"]["train_rows"] == 1
    artifact_paths = {item["path"] for item in manifest["artifacts"]}
    assert "dataset_curated.json" in artifact_paths
    assert "dataset_supervised.json" in artifact_paths


def test_build_training_release_package_fails_when_gate_not_passed(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "dataset_curated.json"
    supervised_path = tmp_path / "dataset_supervised.json"
    train_path = tmp_path / "train.jsonl"
    validation_path = tmp_path / "validation.jsonl"
    test_path = tmp_path / "test.jsonl"
    dataset_card = tmp_path / "docs" / "dataset_card.md"
    gate_report = tmp_path / "reports" / "training_data_gate_report.json"

    _write_json(dataset_path, {"metadata": {}, "amostras": []})
    _write_json(supervised_path, {"metadata": {}, "amostras": []})
    train_path.write_text("", encoding="utf-8")
    validation_path.write_text("", encoding="utf-8")
    test_path.write_text("", encoding="utf-8")
    dataset_card.parent.mkdir(parents=True, exist_ok=True)
    dataset_card.write_text("# Dataset Card\n", encoding="utf-8")

    _write_json(
        gate_report,
        {
            "passed": False,
            "gate_results": [
                {
                    "name": "source_grounding_coverage",
                    "passed": False,
                }
            ],
        },
    )

    try:
        release_builder.build_training_release_package(
            dataset_path=dataset_path,
            supervised_dataset_path=supervised_path,
            train_jsonl_path=train_path,
            validation_jsonl_path=validation_path,
            test_jsonl_path=test_path,
            dataset_card_path=dataset_card,
            gate_report_path=gate_report,
            phase3_report_path=None,
            output_root=tmp_path / "releases",
            dataset_version="2026.04.01-a",
            schema_version="2.0.0",
            release_id="2026.04.01-a",
        )
    except ValueError as exc:
        assert "not fully passing" in str(exc)
    else:
        raise AssertionError("Expected ValueError when gate report is failing")
