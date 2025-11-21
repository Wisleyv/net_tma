"""Assembly of final annotation samples."""

from __future__ import annotations

from typing import Dict, List

from .schema import AnnotationSample

_REVIEW_TAGS = {"OM+", "PRO+", "RP+"}


def _merge_source_text(
    paragraph_ids: List[str], source_paragraphs: Dict[str, str]
) -> str | None:
    if not paragraph_ids:
        return None
    chunks = [source_paragraphs.get(par_id, "") for par_id in paragraph_ids]
    merged = "\n\n".join(chunk for chunk in chunks if chunk)
    return merged or None


def _needs_manual_review(
    tag: str, confident_alignment: bool
) -> tuple[bool, str | None]:
    if tag in _REVIEW_TAGS:
        return True, "tag exige revisao manual"
    if not confident_alignment:
        return True, "alinhamento derivado automaticamente"
    return False, None


def build_samples(
    annotations: List[dict],
    target_clean: Dict[str, str],
    alignment: Dict[str, Dict[str, object]],
    tag_definitions: Dict[str, Dict[str, str]],
    source_paragraphs: Dict[str, str],
) -> List[AnnotationSample]:
    """Create `AnnotationSample` objects from raw annotations and metadata."""

    samples: List[AnnotationSample] = []

    for idx, annotation in enumerate(annotations, start=1):
        par_id = annotation["paragrafo_alvo_id"]
        align_info = alignment.get(
            par_id,
            {"paragrafo_fonte_ids": [], "fonte_alinhamento_confiavel": False},
        )
        tag = annotation["tag"]
        tag_info = tag_definitions.get(
            tag,
            {"nome": "Estrategia", "tipo_nivel": "desconhecido"},
        )

        fonte_ids = align_info["paragrafo_fonte_ids"]
        confident = bool(align_info["fonte_alinhamento_confiavel"])
        precisa_revisao, motivo = _needs_manual_review(tag, confident)

        sample = AnnotationSample(
            id=f"PAT_{idx:04d}_{tag.replace('+', '')}",
            tag=tag,
            nome=tag_info.get("nome", tag),
            tipo_nivel=tag_info.get("tipo_nivel", "desconhecido"),
            contexto_anotacao=annotation["conteudo_bruto"],
            paragrafo_alvo_id=par_id,
            paragrafo_fonte_ids=fonte_ids,
            fonte_alinhamento_confiavel=confident,
            texto_paragrafo_alvo=target_clean.get(par_id, ""),
            texto_paragrafo_fonte=_merge_source_text(
                fonte_ids, source_paragraphs
            ),
            trecho_alvo=annotation.get("trecho_alvo") or None,
            trecho_fonte=annotation.get("conteudo_bruto") or None,
            necessita_revisao_humana=precisa_revisao,
            motivo_revisao=motivo,
        )
        samples.append(sample)

    return samples
