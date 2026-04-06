"""Validate external handoff package completeness and consistency.

This script enforces a repeatable handoff contract for releases shared with
external training teams.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FILES = [
    Path("dataset_curated.json"),
    Path("dataset_supervised.json"),
    Path("train.jsonl"),
    Path("validation.jsonl"),
    Path("test.jsonl"),
    Path("release_manifest.json"),
    Path("docs/dataset_card.md"),
    Path("reports/training_data_gate_report.json"),
]

OUT_OF_SCOPE_TAGS = {"OM+", "PRO+"}


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: str


@dataclass
class HandoffValidationReport:
    generated_at: str
    release_dir: str
    release_id: str | None
    dataset_version: str | None
    schema_version: str | None
    checks: list[CheckResult]
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["checks"] = [asdict(check) for check in self.checks]
        return payload


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _contains_keywords(content: str, keywords: set[str]) -> bool:
    return any(keyword in content for keyword in keywords)


def _required_files_check(release_dir: Path) -> CheckResult:
    missing = [
        str(relative_path)
        for relative_path in REQUIRED_FILES
        if not (release_dir / relative_path).exists()
    ]
    if missing:
        return CheckResult(
            name="required_files",
            passed=False,
            details="Missing required artifacts: " + ", ".join(missing),
        )
    return CheckResult(
        name="required_files",
        passed=True,
        details=(
            "All required artifacts present "
            f"({len(REQUIRED_FILES)} files)."
        ),
    )


def _gate_report_check(release_dir: Path) -> CheckResult:
    gate_path = release_dir / "reports/training_data_gate_report.json"
    if not gate_path.exists():
        return CheckResult(
            name="gate_report_pass",
            passed=False,
            details="Gate report file is missing.",
        )

    try:
        gate_payload = _read_json(gate_path)
    except json.JSONDecodeError as exc:
        return CheckResult(
            name="gate_report_pass",
            passed=False,
            details=f"Gate report is invalid JSON: {exc}",
        )

    if bool(gate_payload.get("passed")):
        return CheckResult(
            name="gate_report_pass",
            passed=True,
            details="Training gate report passed.",
        )

    return CheckResult(
        name="gate_report_pass",
        passed=False,
        details="Training gate report indicates failure.",
    )


def _dataset_card_check(release_dir: Path) -> CheckResult:
    card_path = release_dir / "docs/dataset_card.md"
    if not card_path.exists():
        return CheckResult(
            name="dataset_card_completeness",
            passed=False,
            details="Dataset card is missing.",
        )

    content = card_path.read_text(encoding="utf-8").lower()
    version_ok = _contains_keywords(content, {"version", "versao"})
    provenance_ok = _contains_keywords(
        content,
        {"provenance", "proveniencia", "proveniência", "origem", "source"},
    )
    limitations_ok = _contains_keywords(
        content,
        {"limitations", "limitacoes", "limitações", "known limitations"},
    )

    passed = version_ok and provenance_ok and limitations_ok
    details = (
        f"version={version_ok}, provenance={provenance_ok}, "
        f"limitations={limitations_ok}"
    )
    return CheckResult(
        name="dataset_card_completeness",
        passed=passed,
        details=details,
    )


def _manifest_checksum_check(release_dir: Path) -> CheckResult:
    manifest_path = release_dir / "release_manifest.json"
    if not manifest_path.exists():
        return CheckResult(
            name="manifest_checksums",
            passed=False,
            details="release_manifest.json is missing.",
        )

    try:
        manifest = _read_json(manifest_path)
    except json.JSONDecodeError as exc:
        return CheckResult(
            name="manifest_checksums",
            passed=False,
            details=f"release_manifest.json is invalid JSON: {exc}",
        )

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        return CheckResult(
            name="manifest_checksums",
            passed=False,
            details="release_manifest.json has no artifact list.",
        )

    missing_paths: list[str] = []
    mismatched: list[str] = []

    for item in artifacts:
        if not isinstance(item, dict):
            continue
        rel = str(item.get("path") or "").strip()
        expected = str(item.get("sha256") or "").strip().lower()
        if not rel or not expected:
            continue
        target = release_dir / Path(rel)
        if not target.exists():
            missing_paths.append(rel)
            continue
        observed = _sha256(target).lower()
        if observed != expected:
            mismatched.append(rel)

    if missing_paths or mismatched:
        details = []
        if missing_paths:
            details.append("missing=" + ",".join(missing_paths))
        if mismatched:
            details.append("sha_mismatch=" + ",".join(mismatched))
        return CheckResult(
            name="manifest_checksums",
            passed=False,
            details="; ".join(details),
        )

    return CheckResult(
        name="manifest_checksums",
        passed=True,
        details="Manifest artifact checksums verified.",
    )


def _count_consistency_check(release_dir: Path) -> CheckResult:
    manifest_path = release_dir / "release_manifest.json"
    if not manifest_path.exists():
        return CheckResult(
            name="manifest_count_consistency",
            passed=False,
            details="release_manifest.json is missing.",
        )

    manifest = _read_json(manifest_path)
    counts = manifest.get("counts")
    if not isinstance(counts, dict):
        return CheckResult(
            name="manifest_count_consistency",
            passed=False,
            details="Manifest has no counts section.",
        )

    observed = {
        "train_rows": _jsonl_line_count(release_dir / "train.jsonl"),
        "validation_rows": _jsonl_line_count(release_dir / "validation.jsonl"),
        "test_rows": _jsonl_line_count(release_dir / "test.jsonl"),
    }

    mismatches = []
    for key, value in observed.items():
        expected = counts.get(key)
        if expected is None:
            continue
        if int(expected) != value:
            mismatches.append(f"{key}: expected={expected}, observed={value}")

    if mismatches:
        return CheckResult(
            name="manifest_count_consistency",
            passed=False,
            details="; ".join(mismatches),
        )

    return CheckResult(
        name="manifest_count_consistency",
        passed=True,
        details=(
            "Manifest JSONL counts match observed files: "
            f"train={observed['train_rows']}, "
            f"validation={observed['validation_rows']}, "
            f"test={observed['test_rows']}"
        ),
    )


def _version_consistency_check(release_dir: Path) -> CheckResult:
    manifest_path = release_dir / "release_manifest.json"
    curated_path = release_dir / "dataset_curated.json"
    supervised_path = release_dir / "dataset_supervised.json"

    if (
        not manifest_path.exists()
        or not curated_path.exists()
        or not supervised_path.exists()
    ):
        return CheckResult(
            name="version_consistency",
            passed=False,
            details=(
                "Missing manifest or dataset files "
                "required for version check."
            ),
        )

    manifest = _read_json(manifest_path)
    curated = _read_json(curated_path)
    supervised = _read_json(supervised_path)

    manifest_dataset = str(manifest.get("dataset_version") or "").strip()
    manifest_schema = str(manifest.get("schema_version") or "").strip()

    curated_meta = curated.get("metadata", {})
    supervised_meta = supervised.get("metadata", {})

    curated_dataset = str(curated_meta.get("dataset_version") or "").strip()
    supervised_dataset = str(
        supervised_meta.get("dataset_version") or ""
    ).strip()

    curated_schema = str(curated_meta.get("schema_version") or "").strip()
    supervised_schema = str(
        supervised_meta.get("schema_version") or ""
    ).strip()

    dataset_ok = (
        manifest_dataset
        and curated_dataset
        and supervised_dataset
        and manifest_dataset == curated_dataset == supervised_dataset
    )
    schema_ok = (
        manifest_schema
        and curated_schema
        and supervised_schema
        and manifest_schema == curated_schema == supervised_schema
    )

    if dataset_ok and schema_ok:
        return CheckResult(
            name="version_consistency",
            passed=True,
            details=(
                f"dataset_version={manifest_dataset}, "
                f"schema_version={manifest_schema}"
            ),
        )

    return CheckResult(
        name="version_consistency",
        passed=False,
        details=(
            "Version mismatch: "
            f"manifest(dataset={manifest_dataset}, schema={manifest_schema}), "
            f"curated(dataset={curated_dataset}, schema={curated_schema}), "
            "supervised("
            f"dataset={supervised_dataset}, schema={supervised_schema})"
        ),
    )


def _label_scope_check(release_dir: Path) -> CheckResult:
    supervised_path = release_dir / "dataset_supervised.json"
    if not supervised_path.exists():
        return CheckResult(
            name="supervised_label_scope",
            passed=False,
            details="dataset_supervised.json is missing.",
        )

    supervised = _read_json(supervised_path)
    rows = supervised.get("amostras")
    if not isinstance(rows, list):
        rows = []

    out_of_scope_hits: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        tag = str(row.get("tag_code") or row.get("tag") or "").strip()
        if tag in OUT_OF_SCOPE_TAGS:
            sample_id = str(row.get("sample_id") or row.get("id") or "unknown")
            out_of_scope_hits.append(f"{sample_id}:{tag}")

    if out_of_scope_hits:
        return CheckResult(
            name="supervised_label_scope",
            passed=False,
            details="Out-of-scope tags found in supervised dataset: "
            + ", ".join(out_of_scope_hits[:10]),
        )

    return CheckResult(
        name="supervised_label_scope",
        passed=True,
        details="Supervised dataset contains only in-scope automatic labels.",
    )


def _holdout_support_check(
    release_dir: Path,
    require_non_empty_holdouts: bool,
) -> CheckResult:
    validation_rows = _jsonl_line_count(release_dir / "validation.jsonl")
    test_rows = _jsonl_line_count(release_dir / "test.jsonl")

    if require_non_empty_holdouts and (validation_rows == 0 or test_rows == 0):
        return CheckResult(
            name="holdout_support",
            passed=False,
            details=(
                "Holdout splits must be non-empty "
                "when strict mode is enabled: "
                f"validation={validation_rows}, test={test_rows}"
            ),
        )

    return CheckResult(
        name="holdout_support",
        passed=True,
        details=(
            "Holdout support check completed: "
            f"validation={validation_rows}, test={test_rows}, "
            f"strict={require_non_empty_holdouts}"
        ),
    )


def validate_handoff_package(
    release_dir: Path,
    require_non_empty_holdouts: bool = False,
) -> HandoffValidationReport:
    checks = [
        _required_files_check(release_dir),
        _gate_report_check(release_dir),
        _dataset_card_check(release_dir),
        _manifest_checksum_check(release_dir),
        _count_consistency_check(release_dir),
        _version_consistency_check(release_dir),
        _label_scope_check(release_dir),
        _holdout_support_check(release_dir, require_non_empty_holdouts),
    ]

    manifest_path = release_dir / "release_manifest.json"
    release_id = None
    dataset_version = None
    schema_version = None
    if manifest_path.exists():
        manifest = _read_json(manifest_path)
        release_id = str(manifest.get("release_id") or "").strip() or None
        dataset_version = (
            str(manifest.get("dataset_version") or "").strip() or None
        )
        schema_version = (
            str(manifest.get("schema_version") or "").strip() or None
        )

    passed = all(check.passed for check in checks)
    return HandoffValidationReport(
        generated_at=_utc_now_iso(),
        release_dir=str(release_dir),
        release_id=release_id,
        dataset_version=dataset_version,
        schema_version=schema_version,
        checks=checks,
        passed=passed,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate external handoff release package artifacts.",
    )
    parser.add_argument(
        "--release-dir",
        type=Path,
        required=True,
        help="Path to frozen release directory (training_ready_<id>).",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=None,
        help="Optional JSON report output path.",
    )
    parser.add_argument(
        "--require-non-empty-holdouts",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Fail if validation or test split is empty.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if not args.release_dir.exists():
        print(f"Release directory not found: {args.release_dir}")
        return 2

    report = validate_handoff_package(
        release_dir=args.release_dir,
        require_non_empty_holdouts=args.require_non_empty_holdouts,
    )

    print("External handoff validation report")
    print("-" * 34)
    print(f"release_dir: {report.release_dir}")
    print(f"release_id: {report.release_id}")
    print(f"dataset_version: {report.dataset_version}")
    print(f"schema_version: {report.schema_version}")
    for check in report.checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"[{status}] {check.name}: {check.details}")
    print("overall:", "PASS" if report.passed else "FAIL")

    if args.report_json is not None:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
