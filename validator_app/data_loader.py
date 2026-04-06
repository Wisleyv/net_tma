"""Utility functions to load dataset_raw.json for the validator app."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Tuple

from .models import AnnotationSample, Metadata

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = BASE_DIR / "dataset_raw.json"


class DatasetLoadError(RuntimeError):
    """Raised when dataset_raw.json cannot be parsed or located."""


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "sim"}
    return False


def _as_float(value) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return 0.0
        try:
            return float(stripped)
        except ValueError:
            return 0.0
    return 0.0


def _as_str_list(value) -> list[str]:
    if isinstance(value, list):
        result = []
        for item in value:
            text = str(item).strip()
            if text:
                result.append(text)
        return result
    return []


def _is_canonical_v2(raw: dict) -> bool:
    return any(
        key in raw
        for key in (
            "sample_id",
            "tag_code",
            "target_paragraph_id",
            "source_paragraph_ids",
            "target_text",
            "source_text",
        )
    )


def _coerce_metadata(raw: dict) -> Metadata:
    metadata = Metadata(
        projeto=raw.get("projeto", ""),
        versao=raw.get("versao", ""),
        idioma=raw.get("idioma", ""),
        descricao=raw.get("descricao", ""),
        padrao_tags=raw.get("padrao_tags"),
    )
    setattr(
        metadata,
        "_raw_metadata",
        dict(raw) if isinstance(raw, dict) else {},
    )
    return metadata


def _coerce_sample(raw: dict) -> AnnotationSample:
    is_canonical = _is_canonical_v2(raw)

    if is_canonical:
        diagnostics = raw.get("diagnostics")
        if not isinstance(diagnostics, dict):
            diagnostics = {}

        validado = _as_bool(
            raw.get("human_validated", raw.get("validado", False))
        )
        alignment_confidence = _as_float(
            raw.get(
                "alignment_confidence",
                raw.get("fonte_alinhamento_confiavel", 0.0),
            )
        )
        raw_low_conf = raw.get("low_confidence")
        if raw_low_conf is None:
            low_conf = (alignment_confidence < 0.80) and (not validado)
        else:
            low_conf = _as_bool(raw_low_conf)

        sample = AnnotationSample(
            id=str(raw.get("sample_id", raw.get("id", ""))),
            tag=str(raw.get("tag_code", raw.get("tag", ""))),
            nome=str(raw.get("nome", raw.get("tag_code", raw.get("tag", "")))),
            tipo_nivel=str(raw.get("tipo_nivel", "")),
            contexto_anotacao=str(
                raw.get(
                    "contexto_anotacao",
                    diagnostics.get("contexto_anotacao", ""),
                )
            ),
            paragrafo_alvo_id=str(
                raw.get(
                    "target_paragraph_id",
                    raw.get("paragrafo_alvo_id", ""),
                )
            ),
            paragrafo_fonte_ids=_as_str_list(
                raw.get(
                    "source_paragraph_ids",
                    raw.get("paragrafo_fonte_ids", []),
                )
            ),
            fonte_alinhamento_confiavel=_as_bool(
                raw.get(
                    "fonte_alinhamento_confiavel",
                    alignment_confidence >= 0.80,
                )
            ),
            texto_paragrafo_alvo=str(
                raw.get(
                    "target_text",
                    raw.get("texto_paragrafo_alvo", ""),
                )
            ),
            texto_paragrafo_fonte=raw.get(
                "source_text",
                raw.get("texto_paragrafo_fonte"),
            ),
            trecho_alvo=raw.get("target_span_text", raw.get("trecho_alvo")),
            trecho_fonte=raw.get("source_span_text", raw.get("trecho_fonte")),
            necessita_revisao_humana=_as_bool(
                raw.get("necessita_revisao_humana", low_conf)
            ),
            motivo_revisao=raw.get("motivo_revisao", raw.get("review_notes")),
            low_confidence=low_conf,
            validado=validado,
            reviewer=raw.get("reviewer", raw.get("reviewer_id")),
            updated_at=raw.get("updated_at"),
            history=list(raw.get("history", []))
            if isinstance(raw.get("history"), list)
            else [],
        )
    else:
        low_conf = _as_bool(
            raw.get(
                "low_confidence",
                raw.get("necessita_revisao_humana", False),
            )
        )
        validado = _as_bool(raw.get("validado", False))
        sample = AnnotationSample(
            id=str(raw.get("id", "")),
            tag=str(raw.get("tag", "")),
            nome=str(raw.get("nome", raw.get("tag", ""))),
            tipo_nivel=str(raw.get("tipo_nivel", "")),
            contexto_anotacao=str(raw.get("contexto_anotacao", "")),
            paragrafo_alvo_id=str(raw.get("paragrafo_alvo_id", "")),
            paragrafo_fonte_ids=_as_str_list(
                raw.get("paragrafo_fonte_ids", [])
            ),
            fonte_alinhamento_confiavel=_as_bool(
                raw.get("fonte_alinhamento_confiavel", False)
            ),
            texto_paragrafo_alvo=str(raw.get("texto_paragrafo_alvo", "")),
            texto_paragrafo_fonte=raw.get("texto_paragrafo_fonte"),
            trecho_alvo=raw.get("trecho_alvo"),
            trecho_fonte=raw.get("trecho_fonte"),
            necessita_revisao_humana=low_conf,
            motivo_revisao=raw.get("motivo_revisao"),
            low_confidence=low_conf,
            validado=validado,
            reviewer=raw.get("reviewer"),
            updated_at=raw.get("updated_at"),
            history=list(raw.get("history", []))
            if isinstance(raw.get("history"), list)
            else [],
        )

    setattr(sample, "_schema", "canonical_v2" if is_canonical else "legacy")
    setattr(sample, "_raw_row", dict(raw))
    return sample


def _serialize_metadata(metadata: Metadata) -> dict:
    raw_metadata = getattr(metadata, "_raw_metadata", None)
    payload = dict(raw_metadata) if isinstance(raw_metadata, dict) else {}

    payload["projeto"] = metadata.projeto
    payload["versao"] = metadata.versao
    payload["idioma"] = metadata.idioma
    payload["descricao"] = metadata.descricao
    if metadata.padrao_tags is not None or "padrao_tags" in payload:
        payload["padrao_tags"] = metadata.padrao_tags

    return payload


def _serialize_sample(sample: AnnotationSample) -> dict:
    raw_row = getattr(sample, "_raw_row", None)
    payload = dict(raw_row) if isinstance(raw_row, dict) else {}
    schema = getattr(sample, "_schema", "legacy")

    if schema == "canonical_v2":
        payload["sample_id"] = sample.id
        payload["tag_code"] = sample.tag
        payload["target_paragraph_id"] = sample.paragrafo_alvo_id
        payload["source_paragraph_ids"] = list(sample.paragrafo_fonte_ids)
        payload["target_text"] = sample.texto_paragrafo_alvo
        payload["source_text"] = sample.texto_paragrafo_fonte or ""
        payload["target_span_text"] = sample.trecho_alvo or ""
        if "source_span_text" in payload or sample.trecho_fonte is not None:
            payload["source_span_text"] = sample.trecho_fonte or ""

        payload["human_validated"] = bool(sample.validado)
        if "reviewer_id" in payload or sample.reviewer is not None:
            payload["reviewer_id"] = sample.reviewer
        if "review_notes" in payload or sample.motivo_revisao is not None:
            payload["review_notes"] = sample.motivo_revisao
        if sample.updated_at is not None or "updated_at" in payload:
            payload["updated_at"] = sample.updated_at

        if sample.history or "history" in payload:
            payload["history"] = list(sample.history)

        if "low_confidence" in payload or sample.low_confidence:
            payload["low_confidence"] = bool(sample.low_confidence)
        if "necessita_revisao_humana" in payload:
            payload["necessita_revisao_humana"] = bool(
                sample.necessita_revisao_humana
            )

        # Keep mirrored legacy fields synchronized when present.
        if "id" in payload:
            payload["id"] = sample.id
        if "tag" in payload:
            payload["tag"] = sample.tag
        if "texto_paragrafo_alvo" in payload:
            payload["texto_paragrafo_alvo"] = sample.texto_paragrafo_alvo
        if "texto_paragrafo_fonte" in payload:
            payload["texto_paragrafo_fonte"] = (
                sample.texto_paragrafo_fonte or ""
            )
        if "trecho_alvo" in payload:
            payload["trecho_alvo"] = sample.trecho_alvo
        if "trecho_fonte" in payload:
            payload["trecho_fonte"] = sample.trecho_fonte
        if "contexto_anotacao" in payload:
            payload["contexto_anotacao"] = sample.contexto_anotacao
        if "paragrafo_alvo_id" in payload:
            payload["paragrafo_alvo_id"] = sample.paragrafo_alvo_id
        if "paragrafo_fonte_ids" in payload:
            payload["paragrafo_fonte_ids"] = list(sample.paragrafo_fonte_ids)
        if "validado" in payload:
            payload["validado"] = bool(sample.validado)
        if "reviewer" in payload:
            payload["reviewer"] = sample.reviewer
        if "motivo_revisao" in payload:
            payload["motivo_revisao"] = sample.motivo_revisao
        return payload

    payload.update(
        {
            "id": sample.id,
            "tag": sample.tag,
            "nome": sample.nome,
            "tipo_nivel": sample.tipo_nivel,
            "contexto_anotacao": sample.contexto_anotacao,
            "paragrafo_alvo_id": sample.paragrafo_alvo_id,
            "paragrafo_fonte_ids": list(sample.paragrafo_fonte_ids),
            "fonte_alinhamento_confiavel": bool(
                sample.fonte_alinhamento_confiavel
            ),
            "texto_paragrafo_alvo": sample.texto_paragrafo_alvo,
            "texto_paragrafo_fonte": sample.texto_paragrafo_fonte,
            "trecho_alvo": sample.trecho_alvo,
            "trecho_fonte": sample.trecho_fonte,
            "necessita_revisao_humana": bool(sample.necessita_revisao_humana),
            "motivo_revisao": sample.motivo_revisao,
            "low_confidence": bool(sample.low_confidence),
            "validado": bool(sample.validado),
            "reviewer": sample.reviewer,
            "updated_at": sample.updated_at,
            "history": list(sample.history),
        }
    )

    # Keep mirrored canonical fields synchronized when present.
    if "sample_id" in payload:
        payload["sample_id"] = sample.id
    if "tag_code" in payload:
        payload["tag_code"] = sample.tag
    if "target_paragraph_id" in payload:
        payload["target_paragraph_id"] = sample.paragrafo_alvo_id
    if "source_paragraph_ids" in payload:
        payload["source_paragraph_ids"] = list(sample.paragrafo_fonte_ids)
    if "target_text" in payload:
        payload["target_text"] = sample.texto_paragrafo_alvo
    if "source_text" in payload:
        payload["source_text"] = sample.texto_paragrafo_fonte or ""
    if "target_span_text" in payload:
        payload["target_span_text"] = sample.trecho_alvo or ""
    if "source_span_text" in payload:
        payload["source_span_text"] = sample.trecho_fonte or ""
    if "human_validated" in payload:
        payload["human_validated"] = bool(sample.validado)
    if "reviewer_id" in payload:
        payload["reviewer_id"] = sample.reviewer
    if "review_notes" in payload:
        payload["review_notes"] = sample.motivo_revisao

    return payload


def load_dataset(
    path: Path | str | None = None,
) -> Tuple[Metadata, List[AnnotationSample]]:
    """Load dataset JSON and convert it to domain objects."""

    target_path = Path(path) if path else DEFAULT_DATASET
    if not target_path.exists():
        raise DatasetLoadError(f"Nao encontrei o arquivo: {target_path}")

    try:
        payload = json.loads(target_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - unreproducible
        raise DatasetLoadError(f"JSON invalido em {target_path}") from exc

    metadata = _coerce_metadata(payload.get("metadata", {}))
    samples = [_coerce_sample(item) for item in payload.get("amostras", [])]
    return metadata, samples


def save_dataset(
    path: Path | str,
    metadata: Metadata,
    samples: Iterable[AnnotationSample],
) -> None:
    """Persist the dataset to disk, preserving the parser schema."""

    payload = {
        "metadata": _serialize_metadata(metadata),
        "amostras": [_serialize_sample(sample) for sample in samples],
    }
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
