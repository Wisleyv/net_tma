"""Prepare review artifacts for an unannotated source-target text pair.

The parser pipeline expects inline strategy tags in the target text. This
helper normalizes raw text encodings, aligns source and target paragraphs,
and builds reviewer-facing artifacts to support manual tagging.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from parser import alignment, annotations

from .convert_inputs import ConversionError, convert_file


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _split_paragraphs(text: str) -> list[str]:
    """Split on blank lines with fallback to non-empty line segmentation."""

    raw_parts = text.strip().split("\n\n")
    parts = [part.strip() for part in raw_parts if part.strip()]

    line_parts = [line.strip() for line in text.splitlines() if line.strip()]

    # Some real-world files mix sparse blank lines with many logical
    # paragraphs separated by single newlines. When blank-line splitting is
    # too coarse, prefer line-level segmentation for review readiness.
    if len(parts) > 1:
        if len(parts) <= 5 and len(line_parts) >= 20:
            return line_parts
        return parts

    return line_parts if line_parts else parts


def _enumerate_paragraphs(
    paragraphs: list[str],
    prefix: str,
) -> dict[str, str]:
    return {
        f"{prefix}_{index:03d}": paragraph
        for index, paragraph in enumerate(paragraphs, start=1)
    }


def _similarity(left: str, right: str) -> float:
    if not left.strip() or not right.strip():
        return 0.0
    return float(SequenceMatcher(None, left, right).ratio())


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _render_review_markdown(
    summary: dict[str, Any],
    pairs: list[dict[str, Any]],
) -> str:
    lines: list[str] = [
        "# Unannotated Pair Review Pack",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- source_input: {summary['source_input']}",
        f"- target_input: {summary['target_input']}",
        f"- source_normalized: {summary['source_normalized']}",
        f"- target_normalized: {summary['target_normalized']}",
        (
            "- counts: "
            f"source_paragraphs={summary['counts']['source_paragraphs']}, "
            f"target_paragraphs={summary['counts']['target_paragraphs']}, "
            f"aligned_pairs={summary['counts']['aligned_pairs']}, "
            f"unaligned_targets={summary['counts']['unaligned_targets']}"
        ),
        "",
        "## Reviewer Instructions",
        "",
        (
            "1. Use each pair as context to add inline simplification tags "
            "in the target text."
        ),
        "2. Keep uncertain cases for manual review instead of forcing labels.",
        (
            "3. Prefer real edit evidence from source-target comparison over "
            "invented examples."
        ),
        "",
    ]

    for pair in pairs:
        source_id = pair.get("source_paragraph_id") or "(none)"
        lines.extend(
            [
                (
                    "## "
                    f"{pair['target_paragraph_id']} <- {source_id} "
                    f"(similarity={pair['similarity']:.4f}, "
                    f"confident={pair['alignment_confident']})"
                ),
                "",
                "### Source",
                pair.get("source_text") or "",
                "",
                "### Target",
                pair.get("target_text") or "",
                "",
            ]
        )

    lines.append("")
    return "\n".join(lines)


def _render_target_template(pairs: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for pair in pairs:
        source_id = pair.get("source_paragraph_id") or "none"
        lines.extend(
            [
                (
                    "<!-- "
                    f"{pair['target_paragraph_id']} "
                    f"source={source_id} "
                    f"similarity={pair['similarity']:.4f} "
                    f"confident={pair['alignment_confident']}"
                    " -->"
                ),
                pair.get("target_text") or "",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def build_unannotated_review_pack(
    source_input: Path,
    target_input: Path,
    source_normalized: Path,
    target_normalized: Path,
    report_json: Path,
    review_md: Path,
    target_template_md: Path,
) -> dict[str, Any]:
    source_text = convert_file(source_input, source_normalized)
    target_text = convert_file(target_input, target_normalized)

    source_paragraphs = _enumerate_paragraphs(
        _split_paragraphs(source_text),
        "F",
    )
    target_paragraphs = _enumerate_paragraphs(
        _split_paragraphs(target_text),
        "A",
    )

    target_clean = annotations.clean_all(target_paragraphs)
    # For unannotated intake we prefer a monotonic global pass to avoid
    # section-heading drift in noisy plain-text exports.
    source_sections = {"GLOBAL": list(source_paragraphs.keys())}
    target_sections = {"GLOBAL": list(target_paragraphs.keys())}
    aligned = alignment.align_paragraphs(
        source_sections=source_sections,
        target_sections=target_sections,
        source_paragraphs=source_paragraphs,
        target_clean=target_clean,
        annotations_map=defaultdict(list),
    )

    pairs: list[dict[str, Any]] = []
    for target_id, target_paragraph in target_paragraphs.items():
        match_payload = aligned.get(target_id, {})
        source_ids = match_payload.get("paragrafo_fonte_ids", [])
        source_id = source_ids[0] if source_ids else None
        source_paragraph = (
            source_paragraphs.get(source_id, "") if source_id else ""
        )
        similarity = _similarity(
            target_clean.get(target_id, ""),
            source_paragraph,
        )
        pairs.append(
            {
                "target_paragraph_id": target_id,
                "source_paragraph_id": source_id,
                "alignment_confident": bool(
                    match_payload.get("fonte_alinhamento_confiavel", False)
                ),
                "similarity": similarity,
                "source_text": source_paragraph,
                "target_text": target_paragraph,
                "needs_manual_annotation": True,
            }
        )

    summary = {
        "generated_at": _utc_now_iso(),
        "source_input": str(source_input),
        "target_input": str(target_input),
        "source_normalized": str(source_normalized),
        "target_normalized": str(target_normalized),
        "counts": {
            "source_paragraphs": len(source_paragraphs),
            "target_paragraphs": len(target_paragraphs),
            "aligned_pairs": len(
                [
                    pair
                    for pair in pairs
                    if pair.get("source_paragraph_id") is not None
                ]
            ),
            "unaligned_targets": len(
                [
                    pair
                    for pair in pairs
                    if pair.get("source_paragraph_id") is None
                ]
            ),
        },
    }

    payload = {
        "summary": summary,
        "pairs": pairs,
    }
    _write_json(report_json, payload)

    review_md.parent.mkdir(parents=True, exist_ok=True)
    review_md.write_text(
        _render_review_markdown(summary, pairs),
        encoding="utf-8",
    )

    target_template_md.parent.mkdir(parents=True, exist_ok=True)
    target_template_md.write_text(
        _render_target_template(pairs),
        encoding="utf-8",
    )

    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize and align an unannotated source-target pair to build "
            "manual annotation review artifacts."
        )
    )
    parser.add_argument(
        "--source-input",
        type=Path,
        required=True,
        help="Input source TXT/MD path.",
    )
    parser.add_argument(
        "--target-input",
        type=Path,
        required=True,
        help="Input target TXT/MD path.",
    )
    parser.add_argument(
        "--source-normalized",
        type=Path,
        default=Path("reports/unannotated_pair/source_normalized.md"),
        help="UTF-8 normalized source output path.",
    )
    parser.add_argument(
        "--target-normalized",
        type=Path,
        default=Path("reports/unannotated_pair/target_normalized.md"),
        help="UTF-8 normalized target output path.",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=Path("reports/unannotated_pair/review_pack.json"),
        help="Output review pack JSON path.",
    )
    parser.add_argument(
        "--review-md",
        type=Path,
        default=Path("reports/unannotated_pair/review_pack.md"),
        help="Output reviewer markdown path.",
    )
    parser.add_argument(
        "--target-template-md",
        type=Path,
        default=Path("reports/unannotated_pair/target_annotation_template.md"),
        help="Output target annotation template markdown path.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if not args.source_input.exists():
        print(f"Source input not found: {args.source_input}")
        return 2
    if not args.target_input.exists():
        print(f"Target input not found: {args.target_input}")
        return 2

    try:
        payload = build_unannotated_review_pack(
            source_input=args.source_input,
            target_input=args.target_input,
            source_normalized=args.source_normalized,
            target_normalized=args.target_normalized,
            report_json=args.report_json,
            review_md=args.review_md,
            target_template_md=args.target_template_md,
        )
    except ConversionError as exc:
        print(f"Review pack generation failed: {exc}")
        return 2

    counts = payload["summary"]["counts"]
    print("Unannotated review pack summary")
    print("-" * 31)
    print(f"source_paragraphs: {counts['source_paragraphs']}")
    print(f"target_paragraphs: {counts['target_paragraphs']}")
    print(f"aligned_pairs: {counts['aligned_pairs']}")
    print(f"unaligned_targets: {counts['unaligned_targets']}")
    print(f"report_json: {args.report_json}")
    print(f"review_md: {args.review_md}")
    print(f"target_template_md: {args.target_template_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
