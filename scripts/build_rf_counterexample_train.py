"""Build a train JSONL augmented with RF+ counterexample rows.

This helper supports B-14 iteration by generating additional train rows for
labels that are currently overpredicted as RF+ in holdout error buckets.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
    path.write_text((content + "\n") if content else "", encoding="utf-8")


def _target_labels_from_buckets(
    error_payload: dict[str, Any],
    predicted_label: str,
) -> list[str]:
    buckets = error_payload.get("bucket_counts", [])
    if not isinstance(buckets, list):
        return []

    labels: list[str] = []
    for bucket in buckets:
        if not isinstance(bucket, dict):
            continue
        predicted = str(bucket.get("predicted_label") or "").strip()
        true_label = str(bucket.get("true_label") or "").strip()
        if predicted == predicted_label and true_label:
            labels.append(true_label)
    return sorted(set(labels))


def _build_counterexample_row(
    row: dict[str, Any],
    suffix_index: int,
) -> dict[str, Any]:
    sample_id = str(row.get("sample_id") or f"row_{suffix_index}").strip()
    target_text = str(
        row.get("target_span_text") or row.get("target_text") or ""
    )
    source_text = str(
        row.get("source_span_text") or row.get("source_text") or ""
    )

    new_row = dict(row)
    new_row["sample_id"] = f"{sample_id}_RFCE{suffix_index:02d}"
    new_row["target_text"] = target_text
    new_row["source_text"] = source_text
    if not str(new_row.get("target_span_text") or "").strip():
        new_row["target_span_text"] = target_text
    if "split" in new_row:
        new_row["split"] = "train"

    diagnostics = new_row.get("diagnostics")
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    diagnostics = dict(diagnostics)
    diagnostics["rf_counterexample"] = True
    diagnostics["rf_counterexample_from"] = sample_id
    diagnostics["rf_counterexample_mode"] = "span_focused_train_variant"
    new_row["diagnostics"] = diagnostics

    return new_row


def build_rf_counterexample_train(
    train_jsonl: Path,
    error_buckets_json: Path,
    output_jsonl: Path,
    predicted_label: str = "RF+",
    max_per_label: int = 2,
) -> dict[str, Any]:
    train_rows = _read_jsonl(train_jsonl)
    error_payload = _read_json(error_buckets_json)

    target_labels = _target_labels_from_buckets(error_payload, predicted_label)
    candidates = [
        row
        for row in train_rows
        if str(row.get("tag_code") or "").strip() in target_labels
    ]

    augment_rows: list[dict[str, Any]] = []
    by_label_count: dict[str, int] = {label: 0 for label in target_labels}
    sample_index = 0
    for row in candidates:
        label = str(row.get("tag_code") or "").strip()
        if label not in by_label_count:
            continue
        if by_label_count[label] >= max_per_label:
            continue
        sample_index += 1
        augment_rows.append(_build_counterexample_row(row, sample_index))
        by_label_count[label] += 1

    output_rows = [*train_rows, *augment_rows]
    _write_jsonl(output_jsonl, output_rows)

    return {
        "input_rows": len(train_rows),
        "output_rows": len(output_rows),
        "augmented_rows": len(augment_rows),
        "predicted_label": predicted_label,
        "target_labels": target_labels,
        "augmented_by_label": by_label_count,
        "output_jsonl": str(output_jsonl),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build RF+ counterexample-augmented train JSONL.",
    )
    parser.add_argument(
        "--train-jsonl",
        type=Path,
        required=True,
        help="Input train JSONL path.",
    )
    parser.add_argument(
        "--error-buckets-json",
        type=Path,
        required=True,
        help="Input baseline error buckets JSON path.",
    )
    parser.add_argument(
        "--output-jsonl",
        type=Path,
        required=True,
        help="Output augmented train JSONL path.",
    )
    parser.add_argument(
        "--predicted-label",
        type=str,
        default="RF+",
        help="Predicted label to target for counterexample curation.",
    )
    parser.add_argument(
        "--max-per-label",
        type=int,
        default=2,
        help="Maximum synthetic counterexample rows per true label.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if not args.train_jsonl.exists():
        print(f"Train JSONL not found: {args.train_jsonl}")
        return 2
    if not args.error_buckets_json.exists():
        print(f"Error buckets JSON not found: {args.error_buckets_json}")
        return 2

    summary = build_rf_counterexample_train(
        train_jsonl=args.train_jsonl,
        error_buckets_json=args.error_buckets_json,
        output_jsonl=args.output_jsonl,
        predicted_label=args.predicted_label,
        max_per_label=max(1, args.max_per_label),
    )

    print("RF+ counterexample curation summary")
    print("-" * 34)
    print(f"input_rows: {summary['input_rows']}")
    print(f"augmented_rows: {summary['augmented_rows']}")
    print(f"output_rows: {summary['output_rows']}")
    print(f"predicted_label: {summary['predicted_label']}")
    print(f"target_labels: {summary['target_labels']}")
    print(f"augmented_by_label: {summary['augmented_by_label']}")
    print(f"output_jsonl: {summary['output_jsonl']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
