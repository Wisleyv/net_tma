"""Build supervised training exports from dataset_curated.json.

Phase 3 artifact builder:
- filters in-scope automatic rows
- deduplicates supervised keys
- creates deterministic split JSONL files by split_group_id
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .validate_training_dataset import IN_SCOPE_TAGS


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_ws(text: str) -> str:
    return " ".join((text or "").split())


def _as_int_or_none(value: Any) -> int | None:
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


def _dedupe_key(row: dict[str, Any]) -> tuple[str, str, int, int, str, str]:
    document_id = str(row.get("document_id") or "").strip()
    target_paragraph_id = str(row.get("target_paragraph_id") or "").strip()
    tag_code = str(row.get("tag_code") or "").strip()

    start = _as_int_or_none(row.get("target_span_start"))
    end = _as_int_or_none(row.get("target_span_end"))
    start_norm = start if start is not None else -1
    end_norm = end if end is not None else -1
    normalized_span = ""
    if start is None and end is None:
        normalized_span = _normalize_ws(str(row.get("target_span_text") or ""))

    return (
        document_id,
        target_paragraph_id,
        start_norm,
        end_norm,
        normalized_span,
        tag_code,
    )


def _group_bucket(group_id: str) -> float:
    digest = hashlib.sha256(group_id.encode("utf-8")).hexdigest()
    integer = int(digest[:16], 16)
    return integer / float(16**16)


def _resolve_group_id(row: dict[str, Any], group_field: str) -> str:
    for key in (group_field, "split_group_id", "document_id"):
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return "__ungrouped__"


def _split_row_counts(
    assignments: dict[str, str],
    group_sizes: dict[str, int],
) -> dict[str, int]:
    counts = {
        "train": 0,
        "validation": 0,
        "test": 0,
    }
    for group, split in assignments.items():
        counts[split] += int(group_sizes.get(group, 0))
    return counts


def _split_group_counts(assignments: dict[str, str]) -> dict[str, int]:
    counts = {
        "train": 0,
        "validation": 0,
        "test": 0,
    }
    for split in assignments.values():
        counts[split] += 1
    return counts


def _transition_penalty(order: tuple[str, ...]) -> int:
    if not order:
        return 0
    switches = 0
    for index in range(1, len(order)):
        if order[index] != order[index - 1]:
            switches += 1
    return switches


def _search_assignment(
    ordered_groups: list[str],
    group_sizes: dict[str, int],
    group_labels: dict[str, set[str]],
    all_labels: set[str],
    train_ratio: float,
    validation_ratio: float,
    min_validation_rows: int,
    min_test_rows: int,
) -> dict[str, str] | None:
    # Exhaustive search is deterministic and robust for tiny group counts.
    if len(ordered_groups) > 12:
        return None

    total_rows = sum(group_sizes[group] for group in ordered_groups)
    train_target = int(round(train_ratio * total_rows))
    validation_target = int(round(validation_ratio * total_rows))
    test_target = total_rows - train_target - validation_target

    best_assignment: dict[str, str] | None = None
    best_score: tuple[int, int, int, int] | None = None

    split_names = ("train", "validation", "test")
    for combo in itertools.product(split_names, repeat=len(ordered_groups)):
        assignments = dict(zip(ordered_groups, combo, strict=False))
        group_counts = _split_group_counts(assignments)
        if any(group_counts[split] == 0 for split in split_names):
            continue

        row_counts = _split_row_counts(assignments, group_sizes)
        validation_shortfall = max(
            0,
            min_validation_rows - row_counts["validation"],
        )
        test_shortfall = max(0, min_test_rows - row_counts["test"])

        support_penalty = validation_shortfall + test_shortfall
        train_labels: set[str] = set()
        for group, split in assignments.items():
            if split == "train":
                train_labels.update(group_labels.get(group, set()))
        label_missing_penalty = len(all_labels - train_labels)

        ratio_penalty = (
            abs(row_counts["train"] - train_target)
            + abs(row_counts["validation"] - validation_target)
            + abs(row_counts["test"] - test_target)
        )
        shape_penalty = _transition_penalty(combo)
        score = (
            support_penalty,
            label_missing_penalty,
            ratio_penalty,
            shape_penalty,
        )

        if best_score is None or score < best_score:
            best_score = score
            best_assignment = assignments

    return best_assignment


def _assign_splits(
    groups: list[str],
    group_sizes: dict[str, int],
    group_labels: dict[str, set[str]],
    all_labels: set[str],
    train_ratio: float,
    validation_ratio: float,
    min_validation_rows: int,
    min_test_rows: int,
) -> dict[str, str]:
    assignments: dict[str, str] = {}
    ordered = sorted(groups, key=_group_bucket)

    # For tiny-but-multi-group datasets, force one group per split and
    # optimize row-level support on holdouts when possible.
    if len(ordered) >= 3:
        searched = _search_assignment(
            ordered_groups=ordered,
            group_sizes=group_sizes,
            group_labels=group_labels,
            all_labels=all_labels,
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
            min_validation_rows=max(1, min_validation_rows),
            min_test_rows=max(1, min_test_rows),
        )
        if searched is not None:
            return searched

        group_count = len(ordered)

        valid_start = max(1, int(round(train_ratio * group_count)))
        test_start = max(
            valid_start + 1,
            int(round((train_ratio + validation_ratio) * group_count)),
        )

        if test_start >= group_count:
            test_start = group_count - 1
        if valid_start >= test_start:
            valid_start = max(1, test_start - 1)

        for index, group in enumerate(ordered):
            if index < valid_start:
                assignments[group] = "train"
            elif index < test_start:
                assignments[group] = "validation"
            else:
                assignments[group] = "test"

        return assignments

    train_cut = train_ratio
    valid_cut = train_ratio + validation_ratio

    for group in ordered:
        bucket = _group_bucket(group)
        if bucket < train_cut:
            split = "train"
        elif bucket < valid_cut:
            split = "validation"
        else:
            split = "test"
        assignments[group] = split

    # Guarantee at least one training group for tiny datasets.
    if ordered and "train" not in assignments.values():
        assignments[ordered[0]] = "train"

    return assignments


def build_supervised_exports(
    dataset_path: Path,
    output_dataset: Path,
    train_jsonl: Path,
    validation_jsonl: Path,
    test_jsonl: Path,
    report_json: Path | None,
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
    group_field: str = "split_group_id",
    min_validation_rows: int = 1,
    min_test_rows: int = 1,
) -> dict[str, Any]:
    payload = _read_json(dataset_path)
    metadata = payload.get("metadata", {})
    rows = payload.get("amostras", [])
    if not isinstance(rows, list):
        rows = []

    filtered: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        tag_code = str(row.get("tag_code") or row.get("tag") or "").strip()
        label_scope = str(row.get("label_scope") or "automatic").strip()
        if label_scope == "diagnostic":
            continue
        if tag_code not in IN_SCOPE_TAGS:
            continue
        filtered.append(dict(row))

    deduped: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str, int, int, str, str]] = set()
    for row in filtered:
        key = _dedupe_key(row)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(row)

    group_sizes: Counter[str] = Counter(
        _resolve_group_id(row, group_field) for row in deduped
    )
    group_labels: dict[str, set[str]] = {}
    all_labels: set[str] = set()
    for row in deduped:
        group = _resolve_group_id(row, group_field)
        label = str(row.get("tag_code") or "").strip()
        if not label:
            continue
        all_labels.add(label)
        group_labels.setdefault(group, set()).add(label)

    groups = sorted(group for group in group_sizes if group)
    assignments = _assign_splits(
        groups=groups,
        group_sizes=dict(group_sizes),
        group_labels=group_labels,
        all_labels=all_labels,
        train_ratio=train_ratio,
        validation_ratio=validation_ratio,
        min_validation_rows=min_validation_rows,
        min_test_rows=min_test_rows,
    )

    split_rows: dict[str, list[dict[str, Any]]] = {
        "train": [],
        "validation": [],
        "test": [],
    }
    for row in deduped:
        group = _resolve_group_id(row, group_field)
        split = assignments.get(group, "train")
        row["split_group_id"] = group
        row["split"] = split
        split_rows[split].append(row)

    out_metadata = dict(metadata) if isinstance(metadata, dict) else {}
    out_metadata["phase3_generated_at"] = _utc_now_iso()
    out_metadata["supervised_row_count"] = len(deduped)
    out_metadata["supervised_group_count"] = len(groups)
    out_metadata["split_group_field"] = group_field

    output_dataset.parent.mkdir(parents=True, exist_ok=True)
    output_dataset.write_text(
        json.dumps(
            {
                "metadata": out_metadata,
                "amostras": deduped,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    train_jsonl.parent.mkdir(parents=True, exist_ok=True)
    validation_jsonl.parent.mkdir(parents=True, exist_ok=True)
    test_jsonl.parent.mkdir(parents=True, exist_ok=True)

    for split, path in (
        ("train", train_jsonl),
        ("validation", validation_jsonl),
        ("test", test_jsonl),
    ):
        content = "\n".join(
            json.dumps(row, ensure_ascii=False) for row in split_rows[split]
        )
        path.write_text((content + "\n") if content else "", encoding="utf-8")

    summary = {
        "dataset": str(dataset_path),
        "output_dataset": str(output_dataset),
        "input_rows": len(rows),
        "filtered_supervised_rows": len(filtered),
        "deduped_supervised_rows": len(deduped),
        "removed_duplicates": len(filtered) - len(deduped),
        "group_field": group_field,
        "group_count": len(groups),
        "min_validation_rows": min_validation_rows,
        "min_test_rows": min_test_rows,
        "split_counts": {
            split: len(items) for split, items in split_rows.items()
        },
        "train_label_coverage": {
            "covered": len({
                str(row.get("tag_code") or "").strip()
                for row in split_rows["train"]
                if str(row.get("tag_code") or "").strip()
            }),
            "total": len(all_labels),
            "missing_labels": sorted(
                all_labels
                - {
                    str(row.get("tag_code") or "").strip()
                    for row in split_rows["train"]
                    if str(row.get("tag_code") or "").strip()
                }
            ),
        },
        "tag_counts": dict(Counter(row.get("tag_code") for row in deduped)),
    }

    if report_json is not None:
        report_json.parent.mkdir(parents=True, exist_ok=True)
        report_json.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return summary


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build supervised dataset and split artifacts."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("dataset_curated.json"),
        help="Input curated dataset path.",
    )
    parser.add_argument(
        "--output-dataset",
        type=Path,
        default=Path("dataset_supervised.json"),
        help="Supervised-only dataset output path.",
    )
    parser.add_argument(
        "--train-jsonl",
        type=Path,
        default=Path("train.jsonl"),
        help="Train split JSONL path.",
    )
    parser.add_argument(
        "--validation-jsonl",
        type=Path,
        default=Path("validation.jsonl"),
        help="Validation split JSONL path.",
    )
    parser.add_argument(
        "--test-jsonl",
        type=Path,
        default=Path("test.jsonl"),
        help="Test split JSONL path.",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=Path("reports/phase3_export_summary.json"),
        help="Optional summary report JSON path.",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.70,
        help="Group-level train split ratio.",
    )
    parser.add_argument(
        "--validation-ratio",
        type=float,
        default=0.15,
        help="Group-level validation split ratio.",
    )
    parser.add_argument(
        "--group-field",
        type=str,
        default="split_group_id",
        help=(
            "Field used as split grouping key (for example split_group_id "
            "or target_paragraph_id)."
        ),
    )
    parser.add_argument(
        "--min-validation-rows",
        type=int,
        default=1,
        help="Minimum target rows for validation split when feasible.",
    )
    parser.add_argument(
        "--min-test-rows",
        type=int,
        default=1,
        help="Minimum target rows for test split when feasible.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if not args.dataset.exists():
        print(f"Dataset not found: {args.dataset}")
        return 2

    summary = build_supervised_exports(
        dataset_path=args.dataset,
        output_dataset=args.output_dataset,
        train_jsonl=args.train_jsonl,
        validation_jsonl=args.validation_jsonl,
        test_jsonl=args.test_jsonl,
        report_json=args.report_json,
        train_ratio=args.train_ratio,
        validation_ratio=args.validation_ratio,
        group_field=args.group_field,
        min_validation_rows=max(1, args.min_validation_rows),
        min_test_rows=max(1, args.min_test_rows),
    )

    print("Phase 3 export summary")
    print("-" * 24)
    print(f"input_rows: {summary['input_rows']}")
    print(f"filtered_supervised_rows: {summary['filtered_supervised_rows']}")
    print(f"deduped_supervised_rows: {summary['deduped_supervised_rows']}")
    print(f"removed_duplicates: {summary['removed_duplicates']}")
    print(f"group_field: {summary['group_field']}")
    print(f"group_count: {summary['group_count']}")
    print(f"split_counts: {summary['split_counts']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
