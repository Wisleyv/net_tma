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
