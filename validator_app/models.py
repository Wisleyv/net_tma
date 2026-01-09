"""Dataclasses shared across the validator app."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List, Optional


@dataclass
class Metadata:
    projeto: str
    versao: str
    idioma: str
    descricao: str
    padrao_tags: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AnnotationSample:
    id: str
    tag: str
    nome: str
    tipo_nivel: str
    contexto_anotacao: str
    paragrafo_alvo_id: str
    paragrafo_fonte_ids: List[str]
    fonte_alinhamento_confiavel: bool
    texto_paragrafo_alvo: str
    texto_paragrafo_fonte: Optional[str]
    trecho_alvo: Optional[str]
    trecho_fonte: Optional[str]
    necessita_revisao_humana: bool
    motivo_revisao: Optional[str]
    low_confidence: bool = False
    validado: bool = False
    reviewer: Optional[str] = None
    updated_at: Optional[str] = None
    history: List[dict] = field(default_factory=list)

    def summary(self) -> str:
        status = (
            "VALIDADO-BAIXO" if self.validado and self.low_confidence else
            "VALIDADO" if self.validado else
            "PENDENTE"
        )
        reviewer = f" | {self.reviewer}" if self.reviewer else ""
        return f"{self.id} | {self.tag} | {status}{reviewer}"

    def to_dict(self) -> dict:
        return asdict(self)

    def log_change(
        self,
        action: str,
        reviewer: Optional[str],
        notes: Optional[str],
        timestamp: str,
    ) -> None:
        entry = {
            "timestamp": timestamp,
            "action": action,
        }
        if reviewer:
            entry["reviewer"] = reviewer
        if notes:
            entry["notes"] = notes
        self.history.append(entry)
        self.updated_at = timestamp
        if reviewer:
            self.reviewer = reviewer
