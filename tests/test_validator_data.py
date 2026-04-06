from __future__ import annotations

import json
from pathlib import Path

from validator_app import data_loader


def _write_sample_dataset(tmp_path: Path) -> Path:
    payload = {
        "metadata": {
            "projeto": "Teste",
            "versao": "0.0",
            "idioma": "pt-BR",
            "descricao": "amostras artificiais",
        },
        "amostras": [
            {
                "id": "T_0001",
                "tag": "SL+",
                "nome": "Simplificacao",
                "tipo_nivel": "lexical",
                "contexto_anotacao": "texto",
                "paragrafo_alvo_id": "A_001",
                "paragrafo_fonte_ids": ["F_001"],
                "fonte_alinhamento_confiavel": True,
                "texto_paragrafo_alvo": "alvo",
                "texto_paragrafo_fonte": "fonte",
                "trecho_alvo": "alvo",
                "trecho_fonte": "fonte",
                "necessita_revisao_humana": False,
                "motivo_revisao": None,
            }
        ],
    }
    path = tmp_path / "sample_dataset.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path


def _write_sample_dataset_v2(tmp_path: Path) -> Path:
    payload = {
        "metadata": {
            "projeto": "TesteV2",
            "versao": "2.0",
            "idioma": "pt-BR",
            "descricao": "amostras canonicas",
            "schema_version": "2.0.0",
            "dataset_version": "2026.04.01-a",
            "custom_meta": "keep-me",
        },
        "amostras": [
            {
                "sample_id": "S_0001",
                "document_id": "DOC_1",
                "split_group_id": "DOC_1",
                "tag_code": "SL+",
                "label_scope": "automatic",
                "target_paragraph_id": "A_001",
                "target_text": "alvo",
                "target_span_text": "trecho alvo",
                "source_paragraph_ids": ["F_001"],
                "source_text": "fonte",
                "source_span_text": "trecho fonte",
                "alignment_confidence": 0.93,
                "human_validated": False,
                "reviewer_id": None,
                "review_notes": None,
                "custom_row": "keep-row",
            }
        ],
    }
    path = tmp_path / "sample_dataset_v2.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path


def _write_sample_dataset_v2_hybrid(tmp_path: Path) -> Path:
    payload = {
        "metadata": {
            "projeto": "TesteV2Hybrid",
            "versao": "2.0",
            "idioma": "pt-BR",
            "descricao": "amostras canonicas com espelho legado",
            "schema_version": "2.0.0",
            "dataset_version": "2026.04.01-a",
        },
        "amostras": [
            {
                "sample_id": "S_0001",
                "tag_code": "SL+",
                "target_paragraph_id": "A_001",
                "source_paragraph_ids": ["F_001"],
                "target_text": "alvo",
                "source_text": "fonte",
                "target_span_text": "trecho alvo",
                "source_span_text": "trecho fonte",
                "human_validated": False,
                "reviewer_id": "OLD_ID",
                "review_notes": "old-note",
                "id": "LEG_0001",
                "tag": "SL+",
                "paragrafo_alvo_id": "A_001",
                "paragrafo_fonte_ids": ["F_001"],
                "texto_paragrafo_alvo": "alvo",
                "texto_paragrafo_fonte": "fonte",
                "trecho_alvo": "trecho alvo",
                "trecho_fonte": "trecho fonte",
                "contexto_anotacao": "contexto inicial",
                "validado": False,
                "reviewer": "OLD_LEGACY",
                "motivo_revisao": "old-reason",
                "legacy_only_custom": "keep-this",
            }
        ],
    }
    path = tmp_path / "sample_dataset_v2_hybrid.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path


def test_load_dataset_from_custom_file(tmp_path):
    dataset_path = _write_sample_dataset(tmp_path)
    metadata, samples = data_loader.load_dataset(dataset_path)

    assert metadata.projeto == "Teste"
    assert len(samples) == 1
    assert samples[0].tag == "SL+"


def test_save_dataset_roundtrip(tmp_path):
    dataset_path = _write_sample_dataset(tmp_path)
    metadata, samples = data_loader.load_dataset(dataset_path)

    output_path = tmp_path / "out.json"
    data_loader.save_dataset(output_path, metadata, samples)

    metadata_b, samples_b = data_loader.load_dataset(output_path)

    assert metadata_b == metadata
    assert [sample.tag for sample in samples_b] == [
        sample.tag for sample in samples
    ]


def test_load_dataset_from_canonical_v2_file(tmp_path):
    dataset_path = _write_sample_dataset_v2(tmp_path)

    metadata, samples = data_loader.load_dataset(dataset_path)

    assert metadata.projeto == "TesteV2"
    assert len(samples) == 1
    sample = samples[0]
    assert sample.id == "S_0001"
    assert sample.tag == "SL+"
    assert sample.paragrafo_fonte_ids == ["F_001"]
    assert sample.texto_paragrafo_fonte == "fonte"
    assert sample.trecho_alvo == "trecho alvo"
    assert sample.trecho_fonte == "trecho fonte"


def test_save_dataset_roundtrip_preserves_canonical_v2_fields(tmp_path):
    dataset_path = _write_sample_dataset_v2(tmp_path)
    metadata, samples = data_loader.load_dataset(dataset_path)

    sample = samples[0]
    sample.validado = True
    sample.reviewer = "RV"
    sample.motivo_revisao = "manual-check"

    output_path = tmp_path / "out_v2.json"
    data_loader.save_dataset(output_path, metadata, samples)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["metadata"]["schema_version"] == "2.0.0"
    assert payload["metadata"]["dataset_version"] == "2026.04.01-a"
    assert payload["metadata"]["custom_meta"] == "keep-me"

    row = payload["amostras"][0]
    assert row["sample_id"] == "S_0001"
    assert row["tag_code"] == "SL+"
    assert row["source_paragraph_ids"] == ["F_001"]
    assert row["source_text"] == "fonte"
    assert row["target_text"] == "alvo"
    assert row["target_span_text"] == "trecho alvo"
    assert row["source_span_text"] == "trecho fonte"
    assert row["human_validated"] is True
    assert row["reviewer_id"] == "RV"
    assert row["review_notes"] == "manual-check"
    assert row["custom_row"] == "keep-row"


def test_save_dataset_roundtrip_syncs_hybrid_mirror_fields(tmp_path):
    dataset_path = _write_sample_dataset_v2_hybrid(tmp_path)
    metadata, samples = data_loader.load_dataset(dataset_path)

    sample = samples[0]
    sample.id = "S_0001_EDIT"
    sample.tag = "RD+"
    sample.paragrafo_alvo_id = "A_002"
    sample.paragrafo_fonte_ids = ["F_010", "F_011"]
    sample.texto_paragrafo_alvo = "novo alvo"
    sample.texto_paragrafo_fonte = "nova fonte"
    sample.trecho_alvo = "novo trecho alvo"
    sample.trecho_fonte = "novo trecho fonte"
    sample.contexto_anotacao = "novo contexto"
    sample.validado = True
    sample.reviewer = "RV_NEW"
    sample.motivo_revisao = "updated-note"

    output_path = tmp_path / "out_v2_hybrid.json"
    data_loader.save_dataset(output_path, metadata, samples)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    row = payload["amostras"][0]

    # Canonical fields are the source of truth.
    assert row["sample_id"] == "S_0001_EDIT"
    assert row["tag_code"] == "RD+"
    assert row["target_paragraph_id"] == "A_002"
    assert row["source_paragraph_ids"] == ["F_010", "F_011"]
    assert row["target_text"] == "novo alvo"
    assert row["source_text"] == "nova fonte"
    assert row["target_span_text"] == "novo trecho alvo"
    assert row["source_span_text"] == "novo trecho fonte"
    assert row["human_validated"] is True
    assert row["reviewer_id"] == "RV_NEW"
    assert row["review_notes"] == "updated-note"

    # Legacy mirrors stay synchronized when present.
    assert row["id"] == "S_0001_EDIT"
    assert row["tag"] == "RD+"
    assert row["paragrafo_alvo_id"] == "A_002"
    assert row["paragrafo_fonte_ids"] == ["F_010", "F_011"]
    assert row["texto_paragrafo_alvo"] == "novo alvo"
    assert row["texto_paragrafo_fonte"] == "nova fonte"
    assert row["trecho_alvo"] == "novo trecho alvo"
    assert row["trecho_fonte"] == "novo trecho fonte"
    assert row["contexto_anotacao"] == "novo contexto"
    assert row["validado"] is True
    assert row["reviewer"] == "RV_NEW"
    assert row["motivo_revisao"] == "updated-note"

    # Unknown fields are preserved.
    assert row["legacy_only_custom"] == "keep-this"
