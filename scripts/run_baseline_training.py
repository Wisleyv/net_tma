"""Run baseline model training and evaluation for Phase 5 (B-13).

This script trains a text classifier on supervised JSONL artifacts and
produces machine-readable and human-readable evaluation reports.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline


@dataclass
class SampleRecord:
    sample_id: str
    label: str
    text: str
    split: str


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _normalize_ws(text: str) -> str:
    return " ".join((text or "").split())


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _as_float_list(values: Any) -> list[float]:
    if isinstance(values, (list, tuple)):
        return [float(value) for value in values]

    tolist = getattr(values, "tolist", None)
    if callable(tolist):
        raw_values = tolist()
        if isinstance(raw_values, (list, tuple)):
            return [float(value) for value in raw_values]
        return [float(str(raw_values))]

    return [float(values)]


def _as_int_list(values: Any) -> list[int]:
    if values is None:
        return [0]
    if isinstance(values, (list, tuple)):
        return [int(value) for value in values]

    tolist = getattr(values, "tolist", None)
    if callable(tolist):
        raw_values = tolist()
        if isinstance(raw_values, (list, tuple)):
            return [int(value) for value in raw_values]
        return [int(str(raw_values))]

    return [int(values)]


def _metric_labels(
    labels_true: list[str],
    labels_pred: list[str],
    preferred_labels: list[str],
) -> list[str]:
    label_space = {label for label in preferred_labels if label}
    label_space.update(label for label in labels_true if label)
    label_space.update(label for label in labels_pred if label)
    return sorted(label_space)


def _labels_from_records(records: list[SampleRecord]) -> set[str]:
    return {record.label for record in records if record.label}


def _compose_feature_text(row: dict[str, Any]) -> str:
    parts: list[str] = []
    for field in (
        "target_text",
        "source_text",
        "target_span_text",
        "source_span_text",
    ):
        value = _normalize_ws(str(row.get(field) or ""))
        if value:
            parts.append(f"{field}:{value}")
    if not parts:
        return "<empty>"
    return " ".join(parts)


def _read_jsonl_samples(path: Path, split: str) -> list[SampleRecord]:
    if not path.exists():
        return []

    records: list[SampleRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            item = json.loads(stripped)
            if not isinstance(item, dict):
                continue

            label = str(item.get("tag_code") or item.get("tag") or "").strip()
            if not label:
                continue

            sample_id = str(
                item.get("sample_id")
                or item.get("id")
                or f"{split}_{line_number}"
            ).strip()
            if not sample_id:
                sample_id = f"{split}_{line_number}"

            records.append(
                SampleRecord(
                    sample_id=sample_id,
                    label=label,
                    text=_compose_feature_text(item),
                    split=split,
                )
            )

    return records


def _build_model() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=1,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


def _evaluate_labels(
    labels_true: list[str],
    labels_pred: list[str],
    labels: list[str],
) -> dict[str, Any]:
    precision, recall, f1_by_tag, support = precision_recall_fscore_support(
        labels_true,
        labels_pred,
        labels=labels,
        zero_division=0,
    )

    precision_values = _as_float_list(precision)
    recall_values = _as_float_list(recall)
    f1_values = _as_float_list(f1_by_tag)
    support_values = _as_int_list(support)

    per_tag: dict[str, dict[str, Any]] = {}
    for index, label in enumerate(labels):
        per_tag[label] = {
            "precision": float(precision_values[index]),
            "recall": float(recall_values[index]),
            "f1": float(f1_values[index]),
            "support": int(support_values[index]),
        }

    matrix = confusion_matrix(labels_true, labels_pred, labels=labels)
    matrix_rows = [[int(value) for value in row] for row in matrix.tolist()]

    return {
        "macro_f1": float(
            f1_score(
                labels_true,
                labels_pred,
                labels=labels,
                average="macro",
                zero_division=0,
            )
        ),
        "weighted_f1": float(
            f1_score(
                labels_true,
                labels_pred,
                labels=labels,
                average="weighted",
                zero_division=0,
            )
        ),
        "accuracy": float(accuracy_score(labels_true, labels_pred)),
        "support": int(len(labels_true)),
        "per_tag": per_tag,
        "confusion_matrix": {
            "labels": labels,
            "matrix": matrix_rows,
        },
    }


def _evaluate_records(
    records: list[SampleRecord],
    predictions: list[str],
    labels: list[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    truth = [record.label for record in records]
    metric_labels = _metric_labels(truth, predictions, labels)
    metrics = _evaluate_labels(truth, predictions, metric_labels)

    mistakes: list[dict[str, Any]] = []
    for record, predicted in zip(records, predictions):
        if record.label == predicted:
            continue
        mistakes.append(
            {
                "sample_id": record.sample_id,
                "split": record.split,
                "true_label": record.label,
                "predicted_label": predicted,
                "text_preview": record.text[:220],
            }
        )

    return metrics, mistakes


def _cross_validate(
    records: list[SampleRecord],
    labels: list[str],
) -> dict[str, Any] | None:
    if len(records) < 2:
        return None

    texts = [record.text for record in records]
    truth = [record.label for record in records]
    unique_labels = set(truth)
    if len(unique_labels) < 2:
        return None

    label_counts = Counter(truth)
    min_count = min(label_counts.values())

    if min_count >= 2:
        n_splits = min(5, min_count)
        splitter = StratifiedKFold(
            n_splits=n_splits,
            shuffle=True,
            random_state=42,
        )
        split_iterator = splitter.split(texts, truth)
        strategy = "stratified_kfold"
    else:
        n_splits = min(5, len(records))
        if n_splits < 2:
            return None
        splitter = KFold(
            n_splits=n_splits,
            shuffle=True,
            random_state=42,
        )
        split_iterator = splitter.split(texts)
        strategy = "kfold_fallback"

    oof_predictions = ["" for _ in records]

    for train_index, valid_index in split_iterator:
        train_texts = [texts[int(i)] for i in train_index]
        train_labels = [truth[int(i)] for i in train_index]

        if len(set(train_labels)) < 2:
            majority = Counter(train_labels).most_common(1)[0][0]
            for item_index in valid_index:
                oof_predictions[int(item_index)] = majority
            continue

        model = _build_model()
        model.fit(train_texts, train_labels)

        valid_texts = [texts[int(i)] for i in valid_index]
        valid_predictions = [str(pred) for pred in model.predict(valid_texts)]
        for offset, item_index in enumerate(valid_index):
            oof_predictions[int(item_index)] = valid_predictions[offset]

    if any(not prediction for prediction in oof_predictions):
        fallback_label = Counter(truth).most_common(1)[0][0]
        oof_predictions = [
            prediction or fallback_label for prediction in oof_predictions
        ]

    metrics, mistakes = _evaluate_records(records, oof_predictions, labels)
    metrics["strategy"] = strategy
    metrics["n_splits"] = int(n_splits)

    return {
        "available": True,
        "metrics": metrics,
        "mistakes": mistakes,
    }


def _misclassification_buckets(
    mistakes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    buckets: Counter[tuple[str, str]] = Counter()
    for item in mistakes:
        key = (str(item["true_label"]), str(item["predicted_label"]))
        buckets[key] += 1

    rows: list[dict[str, Any]] = []
    for (true_label, predicted_label), count in buckets.most_common():
        rows.append(
            {
                "true_label": true_label,
                "predicted_label": predicted_label,
                "count": int(count),
            }
        )
    return rows


def _split_result(
    records: list[SampleRecord],
    predictions: list[str],
    labels: list[str],
    evaluation_type: str,
) -> dict[str, Any]:
    metrics, mistakes = _evaluate_records(records, predictions, labels)
    return {
        "available": True,
        "evaluation_type": evaluation_type,
        "metrics": metrics,
        "mistakes": mistakes,
    }


def _empty_split_result(reason: str) -> dict[str, Any]:
    return {
        "available": False,
        "reason": reason,
    }


def _resolve_input_path(
    explicit_path: Path | None,
    release_dir: Path | None,
    release_filename: str,
    default_path: Path,
) -> Path:
    if explicit_path is not None:
        return explicit_path
    if release_dir is not None:
        return release_dir / release_filename
    return default_path


def _load_release_metadata(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    payload = _read_json(path)
    if not isinstance(payload, dict):
        return None
    return {
        "release_id": str(payload.get("release_id") or "").strip() or None,
        "dataset_version": str(
            payload.get("dataset_version") or ""
        ).strip()
        or None,
        "schema_version": str(payload.get("schema_version") or "").strip()
        or None,
    }


def _render_eval_report(report: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Baseline Evaluation Report",
        "",
        "## Run Context",
        "",
        f"- generated_at: {report['generated_at']}",
        f"- model: {report['model_name']}",
        f"- train_rows: {report['counts']['train']}",
        f"- validation_rows: {report['counts']['validation']}",
        f"- test_rows: {report['counts']['test']}",
    ]

    release_info = report.get("release")
    if isinstance(release_info, dict) and release_info.get("release_id"):
        lines.extend(
            [
                f"- release_id: {release_info.get('release_id')}",
                f"- dataset_version: {release_info.get('dataset_version')}",
                f"- schema_version: {release_info.get('schema_version')}",
            ]
        )

    lines.extend(
        [
            "",
            "## Headline Metrics",
            "",
            (
                f"- primary_source: "
                f"{report['primary_evaluation']['source']}"
            ),
            (
                f"- macro_f1: "
                f"{report['primary_evaluation']['metrics']['macro_f1']:.4f}"
            ),
            (
                f"- weighted_f1: "
                f"{report['primary_evaluation']['metrics']['weighted_f1']:.4f}"
            ),
            (
                f"- accuracy: "
                f"{report['primary_evaluation']['metrics']['accuracy']:.4f}"
            ),
            "",
            "## Split Metrics",
            "",
            "| split | available | macro_f1 | weighted_f1 | accuracy |",
            "|---|---|---:|---:|---:|",
        ]
    )

    for split_name in ("train", "validation", "test"):
        split = report["splits"][split_name]
        if not split.get("available"):
            lines.append(f"| {split_name} | no | n/a | n/a | n/a |")
            continue
        metrics = split["metrics"]
        lines.append(
            "| "
            + split_name
            + " | yes | "
            + f"{metrics['macro_f1']:.4f} | "
            + f"{metrics['weighted_f1']:.4f} | "
            + f"{metrics['accuracy']:.4f} |"
        )

    cross_validation = report.get("cross_validation")
    if (
        isinstance(cross_validation, dict)
        and cross_validation.get("available")
    ):
        cv_metrics = cross_validation["metrics"]
        lines.extend(
            [
                "",
                "## Cross Validation",
                "",
                f"- strategy: {cv_metrics.get('strategy')}",
                f"- n_splits: {cv_metrics.get('n_splits')}",
                f"- macro_f1: {cv_metrics['macro_f1']:.4f}",
                f"- weighted_f1: {cv_metrics['weighted_f1']:.4f}",
                f"- accuracy: {cv_metrics['accuracy']:.4f}",
            ]
        )

    primary_metrics = report["primary_evaluation"]["metrics"]
    per_tag = primary_metrics.get("per_tag", {})
    lines.extend(
        [
            "",
            "## Per-Tag Metrics",
            "",
            "| tag | precision | recall | f1 | support |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for tag, metrics in per_tag.items():
        lines.append(
            "| "
            + tag
            + " | "
            + f"{metrics['precision']:.4f} | "
            + f"{metrics['recall']:.4f} | "
            + f"{metrics['f1']:.4f} | "
            + f"{metrics['support']} |"
        )

    notes = report.get("notes", [])
    if notes:
        lines.extend(["", "## Notes", ""])
        for note in notes:
            lines.append(f"- {note}")

    lines.append("")
    return "\n".join(lines)


def run_baseline_training(
    train_jsonl: Path,
    validation_jsonl: Path,
    test_jsonl: Path,
    report_json: Path,
    eval_report_md: Path,
    errors_json: Path,
    release_manifest: Path | None = None,
    model_name: str = "tfidf_logreg_balanced",
    min_primary_support: int = 3,
) -> dict[str, Any]:
    train_records = _read_jsonl_samples(train_jsonl, split="train")
    if not train_records:
        raise ValueError(
            f"Train split is empty or missing labeled rows: {train_jsonl}"
        )

    validation_records = _read_jsonl_samples(
        validation_jsonl,
        split="validation",
    )
    test_records = _read_jsonl_samples(test_jsonl, split="test")

    labels = sorted({record.label for record in train_records})
    train_labels = [record.label for record in train_records]
    train_label_set = set(train_labels)
    if len(set(train_labels)) < 2:
        raise ValueError("Baseline training requires at least two classes.")

    model = _build_model()
    train_texts = [record.text for record in train_records]
    model.fit(train_texts, train_labels)

    train_predictions = [str(pred) for pred in model.predict(train_texts)]
    split_reports = {
        "train": _split_result(
            records=train_records,
            predictions=train_predictions,
            labels=labels,
            evaluation_type="resubstitution",
        )
    }

    notes: list[str] = []

    if validation_records:
        validation_texts = [record.text for record in validation_records]
        validation_predictions = [
            str(pred) for pred in model.predict(validation_texts)
        ]
        split_reports["validation"] = _split_result(
            records=validation_records,
            predictions=validation_predictions,
            labels=labels,
            evaluation_type="holdout",
        )
    else:
        split_reports["validation"] = _empty_split_result(
            "validation split has zero rows",
        )
        notes.append(
            "Validation split is empty; model selection confidence is limited."
        )

    validation_unseen_labels = sorted(
        _labels_from_records(validation_records) - train_label_set
    )
    if validation_unseen_labels:
        notes.append(
            "Validation split contains labels unseen in train: "
            + ", ".join(validation_unseen_labels)
            + "."
        )

    if test_records:
        test_predictions = [
            str(pred)
            for pred in model.predict([record.text for record in test_records])
        ]
        split_reports["test"] = _split_result(
            records=test_records,
            predictions=test_predictions,
            labels=labels,
            evaluation_type="holdout",
        )
    else:
        split_reports["test"] = _empty_split_result(
            "test split has zero rows",
        )
        notes.append(
            "Test split is empty; generalization estimate is unavailable."
        )

    test_unseen_labels = sorted(
        _labels_from_records(test_records) - train_label_set
    )
    if test_unseen_labels:
        notes.append(
            "Test split contains labels unseen in train: "
            + ", ".join(test_unseen_labels)
            + "."
        )

    cross_validation = _cross_validate(train_records, labels)
    if cross_validation is None:
        cross_validation_payload: dict[str, Any] = {
            "available": False,
            "reason": "cross validation could not be computed",
        }
    else:
        cross_validation_payload = cross_validation

    test_support = int(
        split_reports["test"].get("metrics", {}).get("support", 0)
    )
    validation_support = int(
        split_reports["validation"].get("metrics", {}).get("support", 0)
    )

    if (
        split_reports["test"].get("available")
        and test_support >= min_primary_support
    ):
        primary_source = "test"
        primary_metrics = split_reports["test"]["metrics"]
        primary_mistakes = split_reports["test"]["mistakes"]
    elif (
        split_reports["validation"].get("available")
        and validation_support >= min_primary_support
    ):
        primary_source = "validation"
        primary_metrics = split_reports["validation"]["metrics"]
        primary_mistakes = split_reports["validation"]["mistakes"]
    elif cross_validation_payload.get("available"):
        primary_source = "cross_validation"
        primary_metrics = cross_validation_payload["metrics"]
        primary_mistakes = cross_validation_payload["mistakes"]
    else:
        primary_source = "train"
        primary_metrics = split_reports["train"]["metrics"]
        primary_mistakes = split_reports["train"]["mistakes"]
        notes.append(
            "Only train metrics are available; these are optimistic."
        )

    if (
        split_reports["test"].get("available")
        and test_support < min_primary_support
    ):
        notes.append(
            "Test split support below minimum for primary reporting; "
            f"support={test_support}, min_required={min_primary_support}."
        )
    if (
        split_reports["validation"].get("available")
        and validation_support < min_primary_support
    ):
        notes.append(
            (
                "Validation split support below minimum for "
                "primary reporting; "
                "support="
                f"{validation_support}, "
                "min_required="
                f"{min_primary_support}."
            )
        )

    error_payload = {
        "source": primary_source,
        "bucket_counts": _misclassification_buckets(primary_mistakes),
        "examples": primary_mistakes[:25],
    }

    release_info = _load_release_metadata(release_manifest)

    report = {
        "generated_at": _utc_now_iso(),
        "model_name": model_name,
        "inputs": {
            "train_jsonl": str(train_jsonl),
            "validation_jsonl": str(validation_jsonl),
            "test_jsonl": str(test_jsonl),
            "release_manifest": (
                str(release_manifest)
                if release_manifest is not None
                else None
            ),
        },
        "release": release_info,
        "counts": {
            "train": len(train_records),
            "validation": len(validation_records),
            "test": len(test_records),
        },
        "label_distribution_train": dict(Counter(train_labels)),
        "splits": {
            "train": {
                "available": bool(split_reports["train"]["available"]),
                "evaluation_type": split_reports["train"]["evaluation_type"],
                "metrics": split_reports["train"]["metrics"],
                "mistakes": split_reports["train"]["mistakes"][:25],
            },
            "validation": (
                {
                    "available": False,
                    "reason": split_reports["validation"]["reason"],
                }
                if not split_reports["validation"]["available"]
                else {
                    "available": True,
                    "evaluation_type": split_reports["validation"][
                        "evaluation_type"
                    ],
                    "metrics": split_reports["validation"]["metrics"],
                    "mistakes": split_reports["validation"][
                        "mistakes"
                    ][:25],
                }
            ),
            "test": (
                {
                    "available": False,
                    "reason": split_reports["test"]["reason"],
                }
                if not split_reports["test"]["available"]
                else {
                    "available": True,
                    "evaluation_type": split_reports["test"][
                        "evaluation_type"
                    ],
                    "metrics": split_reports["test"]["metrics"],
                    "mistakes": split_reports["test"]["mistakes"][:25],
                }
            ),
        },
        "cross_validation": (
            {
                "available": False,
                "reason": cross_validation_payload.get("reason"),
            }
            if not cross_validation_payload.get("available")
            else {
                "available": True,
                "metrics": cross_validation_payload["metrics"],
                "mistakes": cross_validation_payload["mistakes"][:25],
            }
        ),
        "primary_evaluation": {
            "source": primary_source,
            "metrics": primary_metrics,
        },
        "notes": notes,
    }

    _write_json(report_json, report)
    _write_json(errors_json, error_payload)

    eval_report_md.parent.mkdir(parents=True, exist_ok=True)
    eval_report_md.write_text(_render_eval_report(report), encoding="utf-8")

    return report


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train and evaluate a B-13 baseline classifier.",
    )
    parser.add_argument(
        "--release-dir",
        type=Path,
        default=None,
        help=(
            "Optional release package directory. "
            "When set, default split paths resolve inside it."
        ),
    )
    parser.add_argument(
        "--train-jsonl",
        type=Path,
        default=None,
        help="Train split JSONL path.",
    )
    parser.add_argument(
        "--validation-jsonl",
        type=Path,
        default=None,
        help="Validation split JSONL path.",
    )
    parser.add_argument(
        "--test-jsonl",
        type=Path,
        default=None,
        help="Test split JSONL path.",
    )
    parser.add_argument(
        "--release-manifest",
        type=Path,
        default=None,
        help="Optional release manifest JSON path.",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=Path("reports/baseline_model_report.json"),
        help="Output JSON report path.",
    )
    parser.add_argument(
        "--eval-report-md",
        type=Path,
        default=Path("docs/eval_report.md"),
        help="Output markdown evaluation report path.",
    )
    parser.add_argument(
        "--errors-json",
        type=Path,
        default=Path("reports/baseline_error_buckets.json"),
        help="Output error bucket JSON path for B-14 handoff.",
    )
    parser.add_argument(
        "--min-primary-support",
        type=int,
        default=3,
        help="Minimum support required to select holdout split as primary.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    train_jsonl = _resolve_input_path(
        explicit_path=args.train_jsonl,
        release_dir=args.release_dir,
        release_filename="train.jsonl",
        default_path=Path("train.jsonl"),
    )
    validation_jsonl = _resolve_input_path(
        explicit_path=args.validation_jsonl,
        release_dir=args.release_dir,
        release_filename="validation.jsonl",
        default_path=Path("validation.jsonl"),
    )
    test_jsonl = _resolve_input_path(
        explicit_path=args.test_jsonl,
        release_dir=args.release_dir,
        release_filename="test.jsonl",
        default_path=Path("test.jsonl"),
    )

    if args.release_manifest is not None:
        release_manifest = args.release_manifest
    elif args.release_dir is not None:
        release_manifest = args.release_dir / "release_manifest.json"
    else:
        release_manifest = None

    try:
        report = run_baseline_training(
            train_jsonl=train_jsonl,
            validation_jsonl=validation_jsonl,
            test_jsonl=test_jsonl,
            report_json=args.report_json,
            eval_report_md=args.eval_report_md,
            errors_json=args.errors_json,
            release_manifest=release_manifest,
            min_primary_support=args.min_primary_support,
        )
    except ValueError as exc:
        print(f"Baseline training failed: {exc}")
        return 2

    primary = report["primary_evaluation"]
    print("Baseline training summary")
    print("-" * 24)
    print(f"train_rows: {report['counts']['train']}")
    print(f"validation_rows: {report['counts']['validation']}")
    print(f"test_rows: {report['counts']['test']}")
    print(f"primary_source: {primary['source']}")
    print(f"macro_f1: {primary['metrics']['macro_f1']:.4f}")
    print(f"weighted_f1: {primary['metrics']['weighted_f1']:.4f}")
    print(f"report_json: {args.report_json}")
    print(f"eval_report_md: {args.eval_report_md}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
