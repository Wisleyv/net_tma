from __future__ import annotations

import json

from parser import cli


def test_cli_generates_dataset(
    tmp_path,
    source_fixture_path,
    target_fixture_path,
    tab_fixture_path,
) -> None:
    output_path = tmp_path / "dataset_test.json"

    cli.main(
        source_path=source_fixture_path,
        target_path=target_fixture_path,
        tags_path=tab_fixture_path,
        output_path=output_path,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert (
        payload["metadata"]["projeto"]
        == "Analise_Estrategias_Simplificacao_Textual"
    )
    assert len(payload["amostras"]) >= 3

    first_sample = payload["amostras"][0]
    assert first_sample["tag"] in {"SL+", "RD+", "OM+"}
    assert first_sample["texto_paragrafo_alvo"]
    assert "trecho_alvo" in first_sample
