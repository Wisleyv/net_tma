"""Phase 2 review workflow for curated training dataset artifacts.

This script bridges legacy parser output to the v2 training contract,
generates a queue for uncertain in-scope rows, and applies reviewer
decisions to produce dataset_curated.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .validate_training_dataset import IN_SCOPE_TAGS, OUT_OF_SCOPE_TAGS

AUTOMATIC_SCOPE = "automatic"
DIAGNOSTIC_SCOPE = "diagnostic"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_non_empty(value: Any) -> bool:
    return bool(isinstance(value, str) and value.strip())


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "sim"}
    return False


def _as_float(value: Any) -> float:
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


def _nullable_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        result = []
        for item in value:
            text = str(item).strip()
            if text:
                result.append(text)
        return result
    return []


def _coerce_label_scope(tag_code: str, explicit_scope: Any) -> str:
    if explicit_scope is not None:
        explicit = str(explicit_scope).strip().lower()
        if explicit in {AUTOMATIC_SCOPE, DIAGNOSTIC_SCOPE}:
            return explicit
    if tag_code in OUT_OF_SCOPE_TAGS:
        return DIAGNOSTIC_SCOPE
    return AUTOMATIC_SCOPE


def canonicalize_dataset_samples(
    payload: dict[str, Any],
    dataset_path: Path,
    schema_version: str = "2.0.0",
    parser_version: str = "parser-v1-legacy",
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not isinstance(payload, dict):
        raise ValueError("Dataset payload must be a JSON object.")

    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    raw_rows = payload.get("amostras")
    if not isinstance(raw_rows, list):
        raw_rows = []

    default_document = (
        str(
            metadata.get("document_id")
            or metadata.get("projeto")
            or dataset_path.stem
        ).strip()
        or dataset_path.stem
    )
    default_created_at = (
        _nullable_str(metadata.get("created_at")) or _utc_now_iso()
    )
    default_parser_version = (
        _nullable_str(metadata.get("parser_version")) or parser_version
    )

    canonical: list[dict[str, Any]] = []
    for index, row in enumerate(raw_rows, start=1):
        if not isinstance(row, dict):
            continue

        sample_id = (
            _nullable_str(row.get("sample_id"))
            or _nullable_str(row.get("id"))
            or f"row_{index:04d}"
        )
        tag_code = _nullable_str(row.get("tag_code") or row.get("tag")) or ""
        document_id = _nullable_str(row.get("document_id")) or default_document
        split_group_id = _nullable_str(row.get("split_group_id"))
        if not split_group_id:
            split_group_id = document_id or default_document

        label_scope = _coerce_label_scope(tag_code, row.get("label_scope"))
        if tag_code in OUT_OF_SCOPE_TAGS:
            label_scope = DIAGNOSTIC_SCOPE

        alignment_confidence = _as_float(
            row.get("alignment_confidence")
            if row.get("alignment_confidence") is not None
            else row.get("fonte_alinhamento_confiavel")
        )
        human_validated = _as_bool(
            row.get("human_validated")
            if row.get("human_validated") is not None
            else row.get("validado")
        )

        source_ids = _as_str_list(
            row.get("source_paragraph_ids") or row.get("paragrafo_fonte_ids")
        )

        diagnostics: dict[str, Any] = {
            "legacy_sample_id": _nullable_str(row.get("id")) or sample_id,
            "legacy_review_flag": _as_bool(
                row.get("necessita_revisao_humana")
            ),
        }

        legacy_reason = _nullable_str(row.get("motivo_revisao"))
        if legacy_reason:
            diagnostics["legacy_review_reason"] = legacy_reason
        context = _nullable_str(row.get("contexto_anotacao"))
        if context:
            diagnostics["contexto_anotacao"] = context

        sample: dict[str, Any] = {
            "sample_id": sample_id,
            "document_id": document_id,
            "split_group_id": split_group_id,
            "tag_code": tag_code,
            "label_scope": label_scope,
            "target_paragraph_id": (
                _nullable_str(
                    row.get("target_paragraph_id")
                    or row.get("paragrafo_alvo_id")
                )
                or f"UNKNOWN_{index:04d}"
            ),
            "target_text": _nullable_str(
                row.get("target_text") or row.get("texto_paragrafo_alvo")
            )
            or "",
            "target_span_text": _nullable_str(
                row.get("target_span_text") or row.get("trecho_alvo")
            )
            or "",
            "source_paragraph_ids": source_ids,
            "source_text": _nullable_str(
                row.get("source_text") or row.get("texto_paragrafo_fonte")
            )
            or "",
            "alignment_confidence": alignment_confidence,
            "human_validated": human_validated,
            "schema_version": _nullable_str(row.get("schema_version"))
            or schema_version,
            "parser_version": _nullable_str(row.get("parser_version"))
            or default_parser_version,
            "created_at": _nullable_str(row.get("created_at"))
            or default_created_at,
            "reviewer_id": _nullable_str(
                row.get("reviewer_id") or row.get("reviewer")
            ),
            "review_notes": _nullable_str(
                row.get("review_notes") or row.get("motivo_revisao")
            ),
            "training_weight": float(row.get("training_weight", 1.0)),
            "diagnostics": diagnostics,
        }

        target_span_start = _as_int_or_none(row.get("target_span_start"))
        target_span_end = _as_int_or_none(row.get("target_span_end"))
        source_span_start = _as_int_or_none(row.get("source_span_start"))
        source_span_end = _as_int_or_none(row.get("source_span_end"))
        source_span_text = _nullable_str(
            row.get("source_span_text") or row.get("trecho_fonte")
        )
        updated_at = _nullable_str(row.get("updated_at"))
        split = _nullable_str(row.get("split"))

        if target_span_start is not None:
            sample["target_span_start"] = target_span_start
        if target_span_end is not None:
            sample["target_span_end"] = target_span_end
        if source_span_start is not None:
            sample["source_span_start"] = source_span_start
        if source_span_end is not None:
            sample["source_span_end"] = source_span_end
        if source_span_text is not None:
            sample["source_span_text"] = source_span_text
        if updated_at is not None:
            sample["updated_at"] = updated_at
        if split is not None:
            sample["split"] = split

        canonical.append(sample)

    return metadata, canonical


def _review_reasons(
    sample: dict[str, Any], confidence_threshold: float
) -> list[str]:
    if sample.get("label_scope") != AUTOMATIC_SCOPE:
        return []
    if sample.get("tag_code") not in IN_SCOPE_TAGS:
        return []
    if _as_bool(sample.get("human_validated")):
        return []

    reasons: list[str] = []

    if _as_float(sample.get("alignment_confidence")) < confidence_threshold:
        reasons.append("alignment_below_threshold")

    source_ids = sample.get("source_paragraph_ids")
    if not isinstance(source_ids, list) or not source_ids:
        reasons.append("missing_source_ids")

    if not _is_non_empty(sample.get("source_text")):
        reasons.append("missing_source_text")

    if not _is_non_empty(sample.get("target_span_text")):
        reasons.append("missing_target_span")

    diagnostics = sample.get("diagnostics")
    if isinstance(diagnostics, dict) and _as_bool(
        diagnostics.get("legacy_review_flag")
    ):
        reasons.append("parser_marked_for_review")

    return reasons


def build_review_queue(
    samples: list[dict[str, Any]], confidence_threshold: float = 0.80
) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    for sample in samples:
        reasons = _review_reasons(sample, confidence_threshold)
        if not reasons:
            continue
        queue.append(
            {
                "sample_id": sample.get("sample_id"),
                "tag_code": sample.get("tag_code"),
                "target_paragraph_id": sample.get("target_paragraph_id"),
                "alignment_confidence": _as_float(
                    sample.get("alignment_confidence")
                ),
                "human_validated": _as_bool(sample.get("human_validated")),
                "review_reasons": reasons,
                "reviewer_id": sample.get("reviewer_id"),
                "review_notes": sample.get("review_notes"),
                "source_paragraph_ids": sample.get("source_paragraph_ids", []),
                "target_span_text": sample.get("target_span_text", ""),
            }
        )
    return queue


def load_review_decisions(path: Path) -> dict[str, dict[str, Any]]:
    payload = _read_json(path)

    rows: list[dict[str, Any]]
    if isinstance(payload, list):
        rows = [item for item in payload if isinstance(item, dict)]
    elif isinstance(payload, dict):
        if isinstance(payload.get("decisions"), list):
            rows = [
                item for item in payload["decisions"] if isinstance(item, dict)
            ]
        else:
            rows = []
            for sample_id, decision in payload.items():
                if not isinstance(decision, dict):
                    continue
                row = {"sample_id": sample_id}
                row.update(decision)
                rows.append(row)
    else:
        raise ValueError("Decisions file must be a JSON object or array.")

    decisions: dict[str, dict[str, Any]] = {}
    for row in rows:
        sample_id = _nullable_str(row.get("sample_id"))
        if not sample_id:
            raise ValueError(
                "Each decision row requires a non-empty sample_id."
            )

        normalized: dict[str, Any] = {}

        decision_code = _nullable_str(row.get("decision"))
        if decision_code:
            token = decision_code.lower()
            if token == "validate":
                normalized["human_validated"] = True
            elif token == "reject":
                normalized["human_validated"] = False
            elif token == "diagnostic":
                normalized["label_scope"] = DIAGNOSTIC_SCOPE
            elif token != "keep":
                raise ValueError(
                    f"Unsupported decision token: {decision_code}"
                )

        if "human_validated" in row:
            normalized["human_validated"] = _as_bool(
                row.get("human_validated")
            )

        if "alignment_confidence" in row:
            normalized["alignment_confidence"] = _as_float(
                row.get("alignment_confidence")
            )

        if "reviewer_id" in row:
            normalized["reviewer_id"] = _nullable_str(row.get("reviewer_id"))

        if "review_notes" in row:
            normalized["review_notes"] = _nullable_str(row.get("review_notes"))

        if "label_scope" in row:
            scope = _nullable_str(row.get("label_scope"))
            if scope not in {AUTOMATIC_SCOPE, DIAGNOSTIC_SCOPE, None}:
                raise ValueError(
                    f"Invalid label_scope for {sample_id}: {scope}"
                )
            normalized["label_scope"] = scope

        decisions[sample_id] = normalized

    return decisions


def apply_review_decisions(
    samples: list[dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
    timestamp: str,
) -> int:
    by_id = {str(sample.get("sample_id")): sample for sample in samples}

    unknown = sorted(
        sample_id for sample_id in decisions if sample_id not in by_id
    )
    if unknown:
        raise ValueError(
            "Decisions reference unknown sample_id values: "
            + ", ".join(unknown)
        )

    updated_count = 0
    for sample_id, patch in decisions.items():
        sample = by_id[sample_id]
        changed = False

        if "human_validated" in patch:
            value = _as_bool(patch.get("human_validated"))
            if sample.get("human_validated") != value:
                sample["human_validated"] = value
                changed = True

        if "alignment_confidence" in patch:
            value = _as_float(patch.get("alignment_confidence"))
            if _as_float(sample.get("alignment_confidence")) != value:
                sample["alignment_confidence"] = value
                changed = True

        if "reviewer_id" in patch:
            value = _nullable_str(patch.get("reviewer_id"))
            if sample.get("reviewer_id") != value:
                sample["reviewer_id"] = value
                changed = True

        if "review_notes" in patch:
            value = _nullable_str(patch.get("review_notes"))
            if sample.get("review_notes") != value:
                sample["review_notes"] = value
                changed = True

        if "label_scope" in patch:
            value = _nullable_str(patch.get("label_scope"))
            if value not in {AUTOMATIC_SCOPE, DIAGNOSTIC_SCOPE, None}:
                raise ValueError(
                    f"Invalid label_scope in decision for {sample_id}: {value}"
                )
            if value is not None and sample.get("label_scope") != value:
                sample["label_scope"] = value
                changed = True

        if changed:
            sample["updated_at"] = timestamp
            updated_count += 1

    return updated_count


def _build_curated_metadata(
    metadata: dict[str, Any],
    dataset_path: Path,
    schema_version: str,
    dataset_version: str | None,
    generated_at: str,
    pending_review_count: int,
) -> dict[str, Any]:
    out = dict(metadata)
    out["schema_version"] = schema_version
    out["dataset_version"] = (
        dataset_version
        or _nullable_str(out.get("dataset_version"))
        or f"{generated_at[0:10]}-phase2"
    )
    out["created_at"] = _nullable_str(out.get("created_at")) or generated_at
    out["source_dataset"] = dataset_path.name
    out["phase2_generated_at"] = generated_at
    out["phase2_review_pending_count"] = pending_review_count
    return out


def _escape_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def write_queue_markdown(
    path: Path,
    queue: list[dict[str, Any]],
    generated_at: str,
    threshold: float,
) -> None:
    lines = [
        "# Phase 2 Review Queue",
        "",
        f"- generated_at: {generated_at}",
        f"- confidence_threshold: {threshold:.2f}",
        f"- pending_samples: {len(queue)}",
        "",
    ]

    if not queue:
        lines.append("No pending in-scope samples.")
    else:
        lines.extend(
            [
                "| sample_id | tag | paragraph | confidence | reasons | "
                "reviewer |",
                "|---|---|---|---:|---|---|",
            ]
        )
        for item in queue:
            reasons = ", ".join(item.get("review_reasons", []))
            lines.append(
                "| "
                + _escape_cell(item.get("sample_id"))
                + " | "
                + _escape_cell(item.get("tag_code"))
                + " | "
                + _escape_cell(item.get("target_paragraph_id"))
                + " | "
                + f"{_as_float(item.get('alignment_confidence')):.3f}"
                + " | "
                + _escape_cell(reasons)
                + " | "
                + _escape_cell(item.get("reviewer_id") or "")
                + " |"
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_decision_template(
    path: Path,
    queue: list[dict[str, Any]],
) -> None:
    template_rows = []
    for item in queue:
        template_rows.append(
            {
                "sample_id": item.get("sample_id"),
                "decision": "keep",
                "human_validated": False,
                "reviewer_id": None,
                "review_notes": None,
            }
        )
    payload = {"decisions": template_rows}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def run_phase2_workflow(
    dataset_path: Path,
    confidence_threshold: float = 0.80,
    decisions_json: Path | None = None,
    schema_version: str = "2.0.0",
    parser_version: str = "parser-v1-legacy",
    dataset_version: str | None = None,
) -> dict[str, Any]:
    payload = _read_json(dataset_path)
    if not isinstance(payload, dict):
        raise ValueError(
            "Dataset must be a JSON object with metadata and amostras."
        )

    generated_at = _utc_now_iso()
    metadata, samples = canonicalize_dataset_samples(
        payload=payload,
        dataset_path=dataset_path,
        schema_version=schema_version,
        parser_version=parser_version,
    )

    applied_decisions = 0
    if decisions_json is not None:
        decisions = load_review_decisions(decisions_json)
        applied_decisions = apply_review_decisions(
            samples=samples,
            decisions=decisions,
            timestamp=generated_at,
        )

    queue = build_review_queue(
        samples,
        confidence_threshold=confidence_threshold,
    )
    curated_metadata = _build_curated_metadata(
        metadata=metadata,
        dataset_path=dataset_path,
        schema_version=schema_version,
        dataset_version=dataset_version,
        generated_at=generated_at,
        pending_review_count=len(queue),
    )

    return {
        "generated_at": generated_at,
        "metadata": curated_metadata,
        "samples": samples,
        "queue": queue,
        "applied_decisions": applied_decisions,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run Phase 2 review workflow and produce curated artifacts."
        )
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("dataset_raw.json"),
        help="Input dataset JSON path (default: dataset_raw.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dataset_curated.json"),
        help="Curated dataset output path (default: dataset_curated.json)",
    )
    parser.add_argument(
        "--queue-json",
        type=Path,
        default=Path("reports/phase2_review_queue.json"),
        help="Review queue JSON output path.",
    )
    parser.add_argument(
        "--queue-md",
        type=Path,
        default=Path("reports/phase2_review_queue.md"),
        help="Review queue markdown report output path.",
    )
    parser.add_argument(
        "--decision-template-json",
        type=Path,
        default=Path("reports/phase2_review_decisions.template.json"),
        help="Decision template JSON output path.",
    )
    parser.add_argument(
        "--decisions-json",
        type=Path,
        default=None,
        help="Optional reviewer decisions JSON to apply before queue export.",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.80,
        help="Confidence threshold for unresolved in-scope rows.",
    )
    parser.add_argument(
        "--schema-version",
        type=str,
        default="2.0.0",
        help="Schema version to stamp curated samples.",
    )
    parser.add_argument(
        "--parser-version",
        type=str,
        default="parser-v1-legacy",
        help="Parser version fallback for legacy rows.",
    )
    parser.add_argument(
        "--dataset-version",
        type=str,
        default=None,
        help="Optional dataset_version override for curated metadata.",
    )
    parser.add_argument(
        "--skip-curated-output",
        action="store_true",
        help="Generate queue/template without writing dataset_curated.json.",
    )
    parser.add_argument(
        "--fail-on-pending",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Return exit code 1 when unresolved queue is not empty.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if not args.dataset.exists():
        print(f"Dataset not found: {args.dataset}", file=sys.stderr)
        return 2
    if args.decisions_json is not None and not args.decisions_json.exists():
        print(
            f"Decisions file not found: {args.decisions_json}",
            file=sys.stderr,
        )
        return 2

    try:
        result = run_phase2_workflow(
            dataset_path=args.dataset,
            confidence_threshold=args.confidence_threshold,
            decisions_json=args.decisions_json,
            schema_version=args.schema_version,
            parser_version=args.parser_version,
            dataset_version=args.dataset_version,
        )
    except ValueError as exc:
        print(f"Workflow error: {exc}", file=sys.stderr)
        return 2

    curated_payload = {
        "metadata": result["metadata"],
        "amostras": result["samples"],
    }
    queue_payload = {
        "generated_at": result["generated_at"],
        "confidence_threshold": args.confidence_threshold,
        "pending_count": len(result["queue"]),
        "pending_samples": result["queue"],
    }

    if not args.skip_curated_output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(curated_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if args.queue_json is not None:
        args.queue_json.parent.mkdir(parents=True, exist_ok=True)
        args.queue_json.write_text(
            json.dumps(queue_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if args.queue_md is not None:
        write_queue_markdown(
            path=args.queue_md,
            queue=result["queue"],
            generated_at=result["generated_at"],
            threshold=args.confidence_threshold,
        )

    if args.decision_template_json is not None:
        write_decision_template(args.decision_template_json, result["queue"])

    print("Phase 2 review workflow summary")
    print("-" * 34)
    print(f"dataset: {args.dataset}")
    if not args.skip_curated_output:
        print(f"dataset_curated: {args.output}")
    print(f"queue_pending: {len(result['queue'])}")
    print(f"decisions_applied: {result['applied_decisions']}")

    if args.fail_on_pending and result["queue"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
