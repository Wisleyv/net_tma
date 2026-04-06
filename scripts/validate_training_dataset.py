"""Dataset quality gate for NET_TMA training data specification v2.

This script enforces the hard gates defined in docs/training_data_spec_v2.md.
It validates a dataset JSON file and returns a non-zero exit code on failure.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

IN_SCOPE_TAGS = {
    "RF+",
    "SL+",
    "IN+",
    "RP+",
    "RD+",
    "MOD+",
    "DL+",
    "EXP+",
    "MT+",
}
OUT_OF_SCOPE_TAGS = {"OM+", "PRO+"}

TAG_MARKER_RE = re.compile(r"\[(?P<tag>[A-Z]{2,4}\+)")


@dataclass
class CanonicalSample:
    sample_id: str
    document_id: str
    split_group_id: str
    tag_code: str
    label_scope: str | None
    target_paragraph_id: str
    target_text: str
    target_span_text: str
    target_span_start: int | None
    target_span_end: int | None
    source_paragraph_ids: list[str]
    source_text: str
    alignment_confidence: float
    human_validated: bool
    split: str | None

    @property
    def in_scope(self) -> bool:
        if self.label_scope == "diagnostic":
            return False
        return self.tag_code in IN_SCOPE_TAGS


@dataclass
class GateResult:
    name: str
    passed: bool
    observed: str
    threshold: str
    details: str


@dataclass
class ValidationReport:
    dataset_path: str
    generated_at: str
    sample_count: int
    in_scope_count: int
    gate_results: list[GateResult]
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["gate_results"] = [asdict(item) for item in self.gate_results]
        return payload


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _is_non_empty(text: str | None) -> bool:
    return bool(text and text.strip())


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "sim"}
    return False


def _as_float_confidence(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return 0.0
        try:
            return max(0.0, min(1.0, float(stripped)))
        except ValueError:
            return 0.0
    return 0.0


def _ensure_list_of_str(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return []


def _int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.strip():
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonicalize_samples(
    dataset_path: Path,
) -> tuple[dict[str, Any], list[CanonicalSample]]:
    payload = _read_json(dataset_path)
    metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
    raw_samples = (
        payload.get("amostras", []) if isinstance(payload, dict) else []
    )

    default_document = (
        metadata.get("document_id")
        or metadata.get("projeto")
        or dataset_path.stem
    )

    samples: list[CanonicalSample] = []
    for index, item in enumerate(raw_samples):
        if not isinstance(item, dict):
            continue

        tag_code = str(item.get("tag_code") or item.get("tag") or "").strip()
        label_scope = item.get("label_scope")

        document_id = str(item.get("document_id") or default_document).strip()
        split_group_id = str(
            item.get("split_group_id") or document_id or default_document
        ).strip()

        sample = CanonicalSample(
            sample_id=str(
                item.get("sample_id") or item.get("id") or f"row_{index}"
            ).strip(),
            document_id=document_id,
            split_group_id=split_group_id,
            tag_code=tag_code,
            label_scope=(
                str(label_scope).strip()
                if label_scope is not None
                else None
            ),
            target_paragraph_id=str(
                item.get("target_paragraph_id")
                or item.get("paragrafo_alvo_id")
                or ""
            ).strip(),
            target_text=str(
                item.get("target_text")
                or item.get("texto_paragrafo_alvo")
                or ""
            ),
            target_span_text=str(
                item.get("target_span_text") or item.get("trecho_alvo") or ""
            ),
            target_span_start=_int_or_none(item.get("target_span_start")),
            target_span_end=_int_or_none(item.get("target_span_end")),
            source_paragraph_ids=_ensure_list_of_str(
                item.get("source_paragraph_ids")
                or item.get("paragrafo_fonte_ids")
            ),
            source_text=str(
                item.get("source_text")
                or item.get("texto_paragrafo_fonte")
                or ""
            ),
            alignment_confidence=_as_float_confidence(
                item.get("alignment_confidence")
                if item.get("alignment_confidence") is not None
                else item.get("fonte_alinhamento_confiavel")
            ),
            human_validated=_as_bool(
                item.get("human_validated")
                if item.get("human_validated") is not None
                else item.get("validado")
            ),
            split=(
                str(item.get("split")).strip()
                if item.get("split") is not None
                else None
            ),
        )
        samples.append(sample)

    return metadata, samples


def _gate_source_grounding(
    samples: list[CanonicalSample],
    min_coverage: float,
) -> GateResult:
    eligible = [sample for sample in samples if sample.in_scope]
    if not eligible:
        return GateResult(
            name="source_grounding_coverage",
            passed=False,
            observed="0/0",
            threshold=f">={min_coverage:.2f}",
            details="No in-scope samples were found.",
        )

    grounded = [
        sample
        for sample in eligible
        if sample.source_paragraph_ids and _is_non_empty(sample.source_text)
    ]
    coverage = len(grounded) / len(eligible)
    return GateResult(
        name="source_grounding_coverage",
        passed=coverage >= min_coverage,
        observed=f"{coverage:.3f} ({len(grounded)}/{len(eligible)})",
        threshold=f">={min_coverage:.2f}",
        details="Share of in-scope rows with source ids and source text.",
    )


def _gate_confident_or_validated(
    samples: list[CanonicalSample],
    min_coverage: float,
) -> GateResult:
    eligible = [sample for sample in samples if sample.in_scope]
    if not eligible:
        return GateResult(
            name="confident_or_validated_coverage",
            passed=False,
            observed="0/0",
            threshold=f">={min_coverage:.2f}",
            details="No in-scope samples were found.",
        )

    accepted = [
        sample
        for sample in eligible
        if sample.alignment_confidence >= 0.80 or sample.human_validated
    ]
    coverage = len(accepted) / len(eligible)
    return GateResult(
        name="confident_or_validated_coverage",
        passed=coverage >= min_coverage,
        observed=f"{coverage:.3f} ({len(accepted)}/{len(eligible)})",
        threshold=f">={min_coverage:.2f}",
        details="Rows with confidence >= 0.80 or explicit human validation.",
    )


def _gate_out_of_scope_labels(
    samples: list[CanonicalSample],
    expect_supervised_export: bool,
) -> GateResult:
    out_of_scope = [
        sample
        for sample in samples
        if sample.tag_code in OUT_OF_SCOPE_TAGS
        and sample.label_scope != "diagnostic"
    ]
    if not expect_supervised_export:
        return GateResult(
            name="out_of_scope_labels",
            passed=True,
            observed=f"{len(out_of_scope)}",
            threshold="informational",
            details=(
                "Check skipped because supervised export was not required."
            ),
        )

    return GateResult(
        name="out_of_scope_labels",
        passed=len(out_of_scope) == 0,
        observed=str(len(out_of_scope)),
        threshold="==0",
        details="OM+ and PRO+ must not appear in supervised export files.",
    )


def _gate_parse_coverage(
    samples: list[CanonicalSample],
    min_coverage: float,
    target_markdown: Path | None,
) -> GateResult:
    if target_markdown is None:
        return GateResult(
            name="parse_coverage",
            passed=False,
            observed="n/a",
            threshold=f">={min_coverage:.2f}",
            details="Missing --target-markdown input.",
        )
    if not target_markdown.exists():
        return GateResult(
            name="parse_coverage",
            passed=False,
            observed="n/a",
            threshold=f">={min_coverage:.2f}",
            details=f"Target markdown file was not found: {target_markdown}",
        )

    content = target_markdown.read_text(encoding="utf-8")
    observed_markers = len(TAG_MARKER_RE.findall(content))
    parsed_samples = len([sample for sample in samples if sample.tag_code])

    if observed_markers <= 0:
        return GateResult(
            name="parse_coverage",
            passed=False,
            observed="0 observed markers",
            threshold=f">={min_coverage:.2f}",
            details="No tag markers were found in target markdown.",
        )

    coverage = parsed_samples / observed_markers
    return GateResult(
        name="parse_coverage",
        passed=coverage >= min_coverage,
        observed=(
            f"{coverage:.3f} ({parsed_samples}/{observed_markers})"
        ),
        threshold=f">={min_coverage:.2f}",
        details="Parsed rows divided by observed tag markers in target text.",
    )


def _dedupe_key(
    sample: CanonicalSample,
) -> tuple[str, str, int, int, str, str]:
    start = (
        sample.target_span_start
        if sample.target_span_start is not None
        else -1
    )
    end = sample.target_span_end if sample.target_span_end is not None else -1
    normalized_span = ""
    if start == -1 and end == -1:
        normalized_span = _normalize_ws(sample.target_span_text)
    return (
        sample.document_id,
        sample.target_paragraph_id,
        start,
        end,
        normalized_span,
        sample.tag_code,
    )


def _gate_duplicate_keys(samples: list[CanonicalSample]) -> GateResult:
    eligible = [sample for sample in samples if sample.in_scope]
    keys = [_dedupe_key(sample) for sample in eligible]
    counter = Counter(keys)
    duplicate_count = sum(count - 1 for count in counter.values() if count > 1)
    return GateResult(
        name="duplicate_supervised_keys",
        passed=duplicate_count == 0,
        observed=str(duplicate_count),
        threshold="==0",
        details=(
            "Key: document_id + target_paragraph_id + target_span + tag_code."
        ),
    )


def _gate_critical_fields(samples: list[CanonicalSample]) -> GateResult:
    eligible = [sample for sample in samples if sample.in_scope]
    if not eligible:
        return GateResult(
            name="critical_fields_non_empty",
            passed=False,
            observed="0/0",
            threshold="==0 missing rows",
            details="No in-scope samples were found.",
        )

    rows_with_missing = 0
    for sample in eligible:
        missing = []
        if not _is_non_empty(sample.sample_id):
            missing.append("sample_id")
        if not _is_non_empty(sample.document_id):
            missing.append("document_id")
        if not _is_non_empty(sample.split_group_id):
            missing.append("split_group_id")
        if not _is_non_empty(sample.tag_code):
            missing.append("tag_code")
        if not _is_non_empty(sample.target_paragraph_id):
            missing.append("target_paragraph_id")
        if not _is_non_empty(sample.target_text):
            missing.append("target_text")
        if not _is_non_empty(sample.target_span_text):
            missing.append("target_span_text")
        if not sample.source_paragraph_ids:
            missing.append("source_paragraph_ids")
        if not _is_non_empty(sample.source_text):
            missing.append("source_text")
        if missing:
            rows_with_missing += 1

    return GateResult(
        name="critical_fields_non_empty",
        passed=rows_with_missing == 0,
        observed=(
            f"{rows_with_missing}/{len(eligible)} "
            "rows with missing fields"
        ),
        threshold="==0 missing rows",
        details="Checks required fields for supervised in-scope rows.",
    )


def _load_split_groups_from_jsonl(path: Path) -> set[str]:
    groups: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            group = str(payload.get("split_group_id") or "").strip()
            if group:
                groups.add(group)
    return groups


def _gate_split_leakage(
    samples: list[CanonicalSample],
    train_jsonl: Path | None,
    validation_jsonl: Path | None,
    test_jsonl: Path | None,
) -> GateResult:
    provided = all(
        path is not None
        for path in (train_jsonl, validation_jsonl, test_jsonl)
    )

    if provided:
        assert train_jsonl is not None
        assert validation_jsonl is not None
        assert test_jsonl is not None

        for path in (train_jsonl, validation_jsonl, test_jsonl):
            if not path.exists():
                return GateResult(
                    name="split_leakage",
                    passed=False,
                    observed="n/a",
                    threshold="==0 overlapping groups",
                    details=f"Split artifact not found: {path}",
                )

        train_groups = _load_split_groups_from_jsonl(train_jsonl)
        valid_groups = _load_split_groups_from_jsonl(validation_jsonl)
        test_groups = _load_split_groups_from_jsonl(test_jsonl)

        overlaps = (
            len(train_groups & valid_groups)
            + len(train_groups & test_groups)
            + len(valid_groups & test_groups)
        )

        return GateResult(
            name="split_leakage",
            passed=overlaps == 0,
            observed=str(overlaps),
            threshold="==0 overlapping groups",
            details=(
                "Intersections across train/validation/test "
                "split_group_id sets."
            ),
        )

    split_values = {
        sample.split
        for sample in samples
        if sample.split in {"train", "validation", "test"}
    }
    if split_values == {"train", "validation", "test"}:
        by_group: dict[str, set[str]] = {}
        for sample in samples:
            if sample.split not in {"train", "validation", "test"}:
                continue
            by_group.setdefault(sample.split_group_id, set()).add(sample.split)
        overlapping = sum(1 for values in by_group.values() if len(values) > 1)
        return GateResult(
            name="split_leakage",
            passed=overlapping == 0,
            observed=str(overlapping),
            threshold="==0 overlapping groups",
            details="Uses sample-level split values from the dataset.",
        )

    return GateResult(
        name="split_leakage",
        passed=False,
        observed="n/a",
        threshold="==0 overlapping groups",
        details=(
            "Missing split inputs. Provide --train-jsonl, --validation-jsonl, "
            "--test-jsonl or include split field in dataset rows."
        ),
    )


def _has_keyword(content: str, options: set[str]) -> bool:
    return any(option in content for option in options)


def _gate_dataset_card(dataset_card_path: Path) -> GateResult:
    if not dataset_card_path.exists():
        return GateResult(
            name="dataset_card_completeness",
            passed=False,
            observed="missing",
            threshold="version+provenance+limitations",
            details=f"Dataset card not found: {dataset_card_path}",
        )

    content = dataset_card_path.read_text(encoding="utf-8").lower()
    version_ok = _has_keyword(content, {"version", "versao"})
    provenance_ok = _has_keyword(
        content,
        {"provenance", "proveniencia", "proveniência", "origem", "source"},
    )
    limits_ok = _has_keyword(
        content,
        {"limitations", "limitacoes", "limitações", "known limitations"},
    )

    passed = version_ok and provenance_ok and limits_ok
    observed = (
        f"version={version_ok}, provenance={provenance_ok}, "
        f"limitations={limits_ok}"
    )
    return GateResult(
        name="dataset_card_completeness",
        passed=passed,
        observed=observed,
        threshold="all true",
        details="Checks required sections in dataset card text.",
    )


def evaluate_dataset(
    dataset_path: Path,
    min_source_grounding: float = 0.95,
    min_confident_or_validated: float = 0.90,
    min_parse_coverage: float = 0.98,
    target_markdown: Path | None = None,
    dataset_card: Path | None = None,
    train_jsonl: Path | None = None,
    validation_jsonl: Path | None = None,
    test_jsonl: Path | None = None,
    expect_supervised_export: bool = True,
) -> ValidationReport:
    _, samples = _canonicalize_samples(dataset_path)
    in_scope_count = len([sample for sample in samples if sample.in_scope])

    gate_results = [
        _gate_source_grounding(samples, min_source_grounding),
        _gate_confident_or_validated(samples, min_confident_or_validated),
        _gate_out_of_scope_labels(samples, expect_supervised_export),
        _gate_parse_coverage(samples, min_parse_coverage, target_markdown),
        _gate_duplicate_keys(samples),
        _gate_critical_fields(samples),
        _gate_split_leakage(
            samples,
            train_jsonl,
            validation_jsonl,
            test_jsonl,
        ),
        _gate_dataset_card(dataset_card or Path("docs/dataset_card.md")),
    ]

    passed = all(result.passed for result in gate_results)
    return ValidationReport(
        dataset_path=str(dataset_path),
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        sample_count=len(samples),
        in_scope_count=in_scope_count,
        gate_results=gate_results,
        passed=passed,
    )


def _print_report(report: ValidationReport) -> None:
    print("Training Data Enforcement Report")
    print("-" * 40)
    print(f"dataset: {report.dataset_path}")
    print(f"generated_at: {report.generated_at}")
    print(f"samples: {report.sample_count}")
    print(f"in_scope_samples: {report.in_scope_count}")
    print()

    for result in report.gate_results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}")
        print(f"  observed : {result.observed}")
        print(f"  threshold: {result.threshold}")
        print(f"  details  : {result.details}")

    print()
    print("overall:", "PASS" if report.passed else "FAIL")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enforce NET_TMA training dataset quality gates."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("dataset_raw.json"),
        help="Path to dataset JSON file (default: dataset_raw.json)",
    )
    parser.add_argument(
        "--target-markdown",
        type=Path,
        default=None,
        help="Path to target markdown file for parse coverage gate.",
    )
    parser.add_argument(
        "--dataset-card",
        type=Path,
        default=Path("docs/dataset_card.md"),
        help="Path to dataset card markdown file.",
    )
    parser.add_argument(
        "--train-jsonl",
        type=Path,
        default=None,
        help="Path to train split JSONL for split leakage checks.",
    )
    parser.add_argument(
        "--validation-jsonl",
        type=Path,
        default=None,
        help="Path to validation split JSONL for split leakage checks.",
    )
    parser.add_argument(
        "--test-jsonl",
        type=Path,
        default=None,
        help="Path to test split JSONL for split leakage checks.",
    )
    parser.add_argument(
        "--min-source-grounding",
        type=float,
        default=0.95,
        help="Minimum required source grounding coverage.",
    )
    parser.add_argument(
        "--min-confident-or-validated",
        type=float,
        default=0.90,
        help="Minimum required confident-or-validated coverage.",
    )
    parser.add_argument(
        "--min-parse-coverage",
        type=float,
        default=0.98,
        help="Minimum required parse coverage ratio.",
    )
    parser.add_argument(
        "--expect-supervised-export",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "If enabled, fail when OM+/PRO+ appear in dataset rows. "
            "Disable for mixed diagnostic+automatic curated files."
        ),
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=None,
        help="Optional path to write machine-readable report JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if not args.dataset.exists():
        print(f"Dataset not found: {args.dataset}", file=sys.stderr)
        return 2

    report = evaluate_dataset(
        dataset_path=args.dataset,
        min_source_grounding=args.min_source_grounding,
        min_confident_or_validated=args.min_confident_or_validated,
        min_parse_coverage=args.min_parse_coverage,
        target_markdown=args.target_markdown,
        dataset_card=args.dataset_card,
        train_jsonl=args.train_jsonl,
        validation_jsonl=args.validation_jsonl,
        test_jsonl=args.test_jsonl,
        expect_supervised_export=args.expect_supervised_export,
    )

    _print_report(report)

    if args.report_json is not None:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
