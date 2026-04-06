"""Human-readable export helpers for reviewed datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import AnnotationSample, Metadata


def _sample_status(sample: AnnotationSample) -> str:
    if sample.validado and sample.low_confidence:
        return "VALIDADO_BAIXO"
    if sample.validado:
        return "VALIDADO"
    if sample.necessita_revisao_humana:
        return "REVISAR"
    return "PENDENTE"


def _safe_text(value: str | None) -> str:
    return (value or "").strip()


def build_review_markdown(
    metadata: Metadata,
    samples: Iterable[AnnotationSample],
) -> str:
    lines = [
        "# Relatorio de Revisao",
        "",
        f"- projeto: {metadata.projeto}",
        f"- versao: {metadata.versao}",
        f"- idioma: {metadata.idioma}",
        f"- descricao: {metadata.descricao}",
        "",
    ]

    for sample in samples:
        lines.extend(
            [
                f"## {sample.id} ({sample.tag})",
                "",
                f"- nome: {sample.nome}",
                f"- status: {_sample_status(sample)}",
                f"- revisor: {sample.reviewer or '-'}",
                f"- atualizado_em: {sample.updated_at or '-'}",
                f"- paragrafo_alvo_id: {sample.paragrafo_alvo_id}",
                (
                    "- paragrafos_fonte_ids: "
                    + ", ".join(sample.paragrafo_fonte_ids)
                    if sample.paragrafo_fonte_ids
                    else "- paragrafos_fonte_ids: -"
                ),
                f"- motivo_revisao: {sample.motivo_revisao or '-'}",
                "",
                "### Contexto",
                _safe_text(sample.contexto_anotacao) or "-",
                "",
                "### Trecho Alvo",
                _safe_text(sample.trecho_alvo) or "-",
                "",
                "### Trecho Fonte",
                _safe_text(sample.trecho_fonte) or "-",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def build_review_txt(
    metadata: Metadata,
    samples: Iterable[AnnotationSample],
) -> str:
    lines = [
        "RELATORIO DE REVISAO",
        "=" * 72,
        f"projeto: {metadata.projeto}",
        f"versao: {metadata.versao}",
        f"idioma: {metadata.idioma}",
        f"descricao: {metadata.descricao}",
        "",
    ]

    for sample in samples:
        lines.extend(
            [
                "-" * 72,
                f"id: {sample.id}",
                f"tag: {sample.tag}",
                f"nome: {sample.nome}",
                f"status: {_sample_status(sample)}",
                f"revisor: {sample.reviewer or '-'}",
                f"atualizado_em: {sample.updated_at or '-'}",
                f"paragrafo_alvo_id: {sample.paragrafo_alvo_id}",
                (
                    "paragrafos_fonte_ids: "
                    + ", ".join(sample.paragrafo_fonte_ids)
                    if sample.paragrafo_fonte_ids
                    else "paragrafos_fonte_ids: -"
                ),
                f"motivo_revisao: {sample.motivo_revisao or '-'}",
                "contexto:",
                _safe_text(sample.contexto_anotacao) or "-",
                "trecho_alvo:",
                _safe_text(sample.trecho_alvo) or "-",
                "trecho_fonte:",
                _safe_text(sample.trecho_fonte) or "-",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def export_review_markdown(
    path: Path,
    metadata: Metadata,
    samples: Iterable[AnnotationSample],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        build_review_markdown(metadata, samples),
        encoding="utf-8",
    )


def export_review_txt(
    path: Path,
    metadata: Metadata,
    samples: Iterable[AnnotationSample],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        build_review_txt(metadata, samples),
        encoding="utf-8",
    )
