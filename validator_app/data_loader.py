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


def _coerce_metadata(raw: dict) -> Metadata:
    return Metadata(
        projeto=raw.get("projeto", ""),
        versao=raw.get("versao", ""),
        idioma=raw.get("idioma", ""),
        descricao=raw.get("descricao", ""),
        padrao_tags=raw.get("padrao_tags"),
    )


def _coerce_sample(raw: dict) -> AnnotationSample:
    low_conf = bool(
        raw.get("low_confidence", raw.get("necessita_revisao_humana", False))
    )
    validado = bool(raw.get("validado", False))
    return AnnotationSample(
        id=raw.get("id", ""),
        tag=raw.get("tag", ""),
        nome=raw.get("nome", raw.get("tag", "")),
        tipo_nivel=raw.get("tipo_nivel", ""),
        contexto_anotacao=raw.get("contexto_anotacao", ""),
        paragrafo_alvo_id=raw.get("paragrafo_alvo_id", ""),
        paragrafo_fonte_ids=list(raw.get("paragrafo_fonte_ids", [])),
        fonte_alinhamento_confiavel=bool(
            raw.get("fonte_alinhamento_confiavel", False)
        ),
        texto_paragrafo_alvo=raw.get("texto_paragrafo_alvo", ""),
        texto_paragrafo_fonte=raw.get("texto_paragrafo_fonte"),
        trecho_alvo=raw.get("trecho_alvo"),
        trecho_fonte=raw.get("trecho_fonte"),
        necessita_revisao_humana=low_conf,
        motivo_revisao=raw.get("motivo_revisao"),
        low_confidence=low_conf,
        validado=validado,
        reviewer=raw.get("reviewer"),
        updated_at=raw.get("updated_at"),
        history=list(raw.get("history", [])),
    )


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
        "metadata": metadata.to_dict(),
        "amostras": [sample.to_dict() for sample in samples],
    }
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
