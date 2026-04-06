from __future__ import annotations

from pathlib import Path

from validator_app.export_utils import (
    build_review_markdown,
    build_review_txt,
    export_review_markdown,
    export_review_txt,
)
from validator_app.models import AnnotationSample, Metadata


def _sample() -> AnnotationSample:
    return AnnotationSample(
        id="PAT_0001_RF",
        tag="RF+",
        nome="Reformulacao",
        tipo_nivel="discurso",
        contexto_anotacao="Contexto de exemplo",
        paragrafo_alvo_id="A_001",
        paragrafo_fonte_ids=["F_001"],
        fonte_alinhamento_confiavel=True,
        texto_paragrafo_alvo="Texto alvo completo",
        texto_paragrafo_fonte="Texto fonte completo",
        trecho_alvo="trecho alvo",
        trecho_fonte="trecho fonte",
        necessita_revisao_humana=False,
        motivo_revisao=None,
        low_confidence=False,
        validado=True,
        reviewer="AN",
        updated_at="2026-04-06T15:00:00",
    )


def _metadata() -> Metadata:
    return Metadata(
        projeto="NET_TMA",
        versao="2.0",
        idioma="pt-BR",
        descricao="dataset de revisao",
    )


def test_build_review_markdown_includes_core_fields() -> None:
    content = build_review_markdown(_metadata(), [_sample()])
    assert "# Relatorio de Revisao" in content
    assert "PAT_0001_RF" in content
    assert "status: VALIDADO" in content
    assert "### Trecho Alvo" in content


def test_build_review_txt_includes_core_fields() -> None:
    content = build_review_txt(_metadata(), [_sample()])
    assert "RELATORIO DE REVISAO" in content
    assert "id: PAT_0001_RF" in content
    assert "status: VALIDADO" in content
    assert "trecho_fonte:" in content


def test_export_review_files_are_written(tmp_path: Path) -> None:
    md_path = tmp_path / "review.md"
    txt_path = tmp_path / "review.txt"

    export_review_markdown(md_path, _metadata(), [_sample()])
    export_review_txt(txt_path, _metadata(), [_sample()])

    assert md_path.exists()
    assert txt_path.exists()
    assert "PAT_0001_RF" in md_path.read_text(encoding="utf-8")
    assert "PAT_0001_RF" in txt_path.read_text(encoding="utf-8")
