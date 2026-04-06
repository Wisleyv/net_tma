"""Build a version-locked training release package.

Phase 4/B-12 helper:
- verifies that the hard quality gate passed
- locks dataset and schema versions on training artifacts
- updates the dataset card version block
- copies frozen artifacts to a release directory
- writes a manifest with checksums for reproducibility
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ARTIFACTS = {
    "dataset": Path("dataset_curated.json"),
    "supervised_dataset": Path("dataset_supervised.json"),
    "train_jsonl": Path("train.jsonl"),
    "validation_jsonl": Path("validation.jsonl"),
    "test_jsonl": Path("test.jsonl"),
    "dataset_card": Path("docs/dataset_card.md"),
    "gate_report": Path("reports/training_data_gate_report.json"),
    "phase3_report": Path("reports/phase3_export_summary.json"),
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _ensure_exists(path: Path, label: str) -> None:
    if not path.exists():
        raise ValueError(f"Missing required {label} file: {path}")


def _normalize_relpath(path: Path, workspace_root: Path) -> Path:
    resolved = path.resolve()
    try:
        return resolved.relative_to(workspace_root)
    except ValueError:
        return Path(path.name)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _jsonl_line_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(
        1
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _assert_gate_passed(gate_report_path: Path) -> dict[str, Any]:
    report = _read_json(gate_report_path)
    gate_passed = bool(report.get("passed"))
    gate_results = report.get("gate_results", [])
    all_results_passed = all(
        isinstance(result, dict) and bool(result.get("passed"))
        for result in gate_results
    )
    if not gate_passed or not all_results_passed:
        raise ValueError(
            "Gate report is not fully passing; "
            "refusing to build version-locked package."
        )
    return report


def _lock_dataset_file(
    dataset_path: Path,
    dataset_version: str,
    schema_version: str,
    locked_at: str,
    release_id: str,
) -> dict[str, Any]:
    payload = _read_json(dataset_path)
    metadata = payload.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    metadata["dataset_version"] = dataset_version
    metadata["schema_version"] = schema_version
    metadata["release_locked_at"] = locked_at
    metadata["release_lock_id"] = release_id
    payload["metadata"] = metadata

    rows = payload.get("amostras", [])
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict):
                row["schema_version"] = schema_version

    _write_json(dataset_path, payload)
    return payload


def _update_dataset_card_versions(
    dataset_card_path: Path,
    schema_version: str,
    dataset_version: str,
    generated_date: str,
) -> None:
    content = dataset_card_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    def _replace_or_insert(prefix: str, value: str) -> None:
        replacement = f"- {prefix}: {value}"
        for index, line in enumerate(lines):
            if line.strip().startswith(f"- {prefix}:"):
                lines[index] = replacement
                return
        version_index = next(
            (
                i
                for i, line in enumerate(lines)
                if line.strip() == "## Version"
            ),
            None,
        )
        insert_at = (version_index + 1) if version_index is not None else 0
        lines.insert(insert_at, replacement)

    _replace_or_insert("schema_version", schema_version)
    _replace_or_insert("dataset_version", dataset_version)
    _replace_or_insert("generated_at", generated_date)

    dataset_card_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _copy_with_manifest_entry(
    source_path: Path,
    workspace_root: Path,
    package_root: Path,
) -> dict[str, Any]:
    relative_path = _normalize_relpath(source_path, workspace_root)
    destination = package_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination)
    return {
        "path": relative_path.as_posix(),
        "bytes": destination.stat().st_size,
        "sha256": _sha256(destination),
    }


def build_training_release_package(
    dataset_path: Path,
    supervised_dataset_path: Path,
    train_jsonl_path: Path,
    validation_jsonl_path: Path,
    test_jsonl_path: Path,
    dataset_card_path: Path,
    gate_report_path: Path,
    phase3_report_path: Path | None,
    output_root: Path,
    dataset_version: str,
    schema_version: str,
    release_id: str,
    force: bool = False,
) -> dict[str, Any]:
    workspace_root = Path.cwd().resolve()

    required_paths = {
        "dataset": dataset_path,
        "supervised dataset": supervised_dataset_path,
        "train split": train_jsonl_path,
        "validation split": validation_jsonl_path,
        "test split": test_jsonl_path,
        "dataset card": dataset_card_path,
        "gate report": gate_report_path,
    }
    for label, path in required_paths.items():
        _ensure_exists(path, label)

    gate_report = _assert_gate_passed(gate_report_path)
    locked_at = _utc_now_iso()
    locked_date = locked_at.split("T", maxsplit=1)[0]

    curated_payload = _lock_dataset_file(
        dataset_path=dataset_path,
        dataset_version=dataset_version,
        schema_version=schema_version,
        locked_at=locked_at,
        release_id=release_id,
    )
    supervised_payload = _lock_dataset_file(
        dataset_path=supervised_dataset_path,
        dataset_version=dataset_version,
        schema_version=schema_version,
        locked_at=locked_at,
        release_id=release_id,
    )
    _update_dataset_card_versions(
        dataset_card_path=dataset_card_path,
        schema_version=schema_version,
        dataset_version=dataset_version,
        generated_date=locked_date,
    )

    package_root = output_root / f"training_ready_{release_id}"
    if package_root.exists():
        if not force:
            raise ValueError(
                "Release package already exists: "
                f"{package_root}. Use --force to overwrite."
            )
        shutil.rmtree(package_root)
    package_root.mkdir(parents=True, exist_ok=True)

    artifact_paths: list[Path] = [
        dataset_path,
        supervised_dataset_path,
        train_jsonl_path,
        validation_jsonl_path,
        test_jsonl_path,
        dataset_card_path,
        gate_report_path,
    ]
    if phase3_report_path is not None and phase3_report_path.exists():
        artifact_paths.append(phase3_report_path)

    manifest_artifacts = [
        _copy_with_manifest_entry(
            source_path=path,
            workspace_root=workspace_root,
            package_root=package_root,
        )
        for path in artifact_paths
    ]

    curated_rows = curated_payload.get("amostras", [])
    supervised_rows = supervised_payload.get("amostras", [])
    if not isinstance(curated_rows, list):
        curated_rows = []
    if not isinstance(supervised_rows, list):
        supervised_rows = []

    manifest = {
        "release_id": release_id,
        "generated_at": locked_at,
        "dataset_version": dataset_version,
        "schema_version": schema_version,
        "workspace_root": workspace_root.as_posix(),
        "gate": {
            "report_path": _normalize_relpath(
                gate_report_path,
                workspace_root,
            ).as_posix(),
            "passed": bool(gate_report.get("passed")),
            "gate_count": len(gate_report.get("gate_results", [])),
        },
        "counts": {
            "curated_rows": len(curated_rows),
            "supervised_rows": len(supervised_rows),
            "train_rows": _jsonl_line_count(train_jsonl_path),
            "validation_rows": _jsonl_line_count(validation_jsonl_path),
            "test_rows": _jsonl_line_count(test_jsonl_path),
        },
        "artifacts": manifest_artifacts,
    }

    manifest_path = package_root / "release_manifest.json"
    _write_json(manifest_path, manifest)

    return {
        "release_id": release_id,
        "package_path": package_root,
        "manifest_path": manifest_path,
        "dataset_version": dataset_version,
        "schema_version": schema_version,
        "counts": manifest["counts"],
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Lock training data versions and build "
            "a frozen release package."
        ),
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_ARTIFACTS["dataset"],
        help="Curated dataset path.",
    )
    parser.add_argument(
        "--supervised-dataset",
        type=Path,
        default=DEFAULT_ARTIFACTS["supervised_dataset"],
        help="Supervised dataset path.",
    )
    parser.add_argument(
        "--train-jsonl",
        type=Path,
        default=DEFAULT_ARTIFACTS["train_jsonl"],
        help="Train split JSONL path.",
    )
    parser.add_argument(
        "--validation-jsonl",
        type=Path,
        default=DEFAULT_ARTIFACTS["validation_jsonl"],
        help="Validation split JSONL path.",
    )
    parser.add_argument(
        "--test-jsonl",
        type=Path,
        default=DEFAULT_ARTIFACTS["test_jsonl"],
        help="Test split JSONL path.",
    )
    parser.add_argument(
        "--dataset-card",
        type=Path,
        default=DEFAULT_ARTIFACTS["dataset_card"],
        help="Dataset card markdown path.",
    )
    parser.add_argument(
        "--gate-report",
        type=Path,
        default=DEFAULT_ARTIFACTS["gate_report"],
        help="Gate report JSON path.",
    )
    parser.add_argument(
        "--phase3-report",
        type=Path,
        default=DEFAULT_ARTIFACTS["phase3_report"],
        help="Optional Phase 3 summary JSON path.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("releases"),
        help="Output directory root for frozen package.",
    )
    parser.add_argument(
        "--dataset-version",
        type=str,
        required=True,
        help=(
            "Dataset version to lock for the release "
            "(for example 2026.04.01-a)."
        ),
    )
    parser.add_argument(
        "--schema-version",
        type=str,
        default="2.0.0",
        help="Schema version to lock for the release.",
    )
    parser.add_argument(
        "--release-id",
        type=str,
        default="",
        help="Optional release package id. Defaults to dataset version.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite package directory when it already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    release_id = args.release_id.strip() or args.dataset_version.strip()

    try:
        summary = build_training_release_package(
            dataset_path=args.dataset,
            supervised_dataset_path=args.supervised_dataset,
            train_jsonl_path=args.train_jsonl,
            validation_jsonl_path=args.validation_jsonl,
            test_jsonl_path=args.test_jsonl,
            dataset_card_path=args.dataset_card,
            gate_report_path=args.gate_report,
            phase3_report_path=args.phase3_report,
            output_root=args.output_root,
            dataset_version=args.dataset_version.strip(),
            schema_version=args.schema_version.strip(),
            release_id=release_id,
            force=bool(args.force),
        )
    except ValueError as exc:
        print(f"Release lock failed: {exc}")
        return 1

    print("Release package summary")
    print("-" * 24)
    print(f"release_id: {summary['release_id']}")
    print(f"dataset_version: {summary['dataset_version']}")
    print(f"schema_version: {summary['schema_version']}")
    print(f"package_path: {summary['package_path']}")
    print(f"manifest_path: {summary['manifest_path']}")
    print(f"counts: {summary['counts']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
