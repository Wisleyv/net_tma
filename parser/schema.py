"""Typed helpers shared across parser modules."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class Metadata:
    projeto: str = "Analise_Estrategias_Simplificacao_Textual"
    versao: str = "0.1"
    idioma: str = "pt-BR"
    descricao: str = (
        "Dataset anotado: cada tag de simplificação textual gera uma amostra."
    )
    padrao_tags: str = "tab_est.md"

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
    paragrafo_fonte_ids: List[str] = field(default_factory=list)
    fonte_alinhamento_confiavel: bool = False
    texto_paragrafo_alvo: str = ""
    texto_paragrafo_fonte: Optional[str] = None
    trecho_alvo: Optional[str] = None
    trecho_fonte: Optional[str] = None
    necessita_revisao_humana: bool = True
    motivo_revisao: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)
