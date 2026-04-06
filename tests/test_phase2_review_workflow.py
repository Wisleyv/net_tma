from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import phase2_review_workflow as phase2


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _legacy_payload() -> dict:
    return {
        "metadata": {
            "projeto": "NET_TMA",
            "versao": "0.1",
            "idioma": "pt-BR",
            "descricao": "legacy parser output",
        },
        "amostras": [
            {
                "id": "PAT_0001_DL",
                "tag": "DL+",
                "paragrafo_alvo_id": "A_010",
                "paragrafo_fonte_ids": ["F_015"],
                "fonte_alinhamento_confiavel": False,
                "texto_paragrafo_alvo": "Texto alvo um",
                "texto_paragrafo_fonte": "Texto fonte um",
                "trecho_alvo": "A AIB nunca sustentou",
                "necessita_revisao_humana": True,
                "motivo_revisao": "alinhamento derivado automaticamente",
            },
            {
                "id": "PAT_0002_RF",
                "tag": "RF+",
                "paragrafo_alvo_id": "A_011",
                "paragrafo_fonte_ids": ["F_016"],
                "fonte_alinhamento_confiavel": True,
                "texto_paragrafo_alvo": "Texto alvo dois",
                "texto_paragrafo_fonte": "Texto fonte dois",
                "trecho_alvo": "Outro exemplo",
                "necessita_revisao_humana": False,
                "motivo_revisao": None,
            },
            {
                "id": "PAT_0003_OM",
                "tag": "OM+",
                "paragrafo_alvo_id": "A_012",
                "paragrafo_fonte_ids": [],
                "fonte_alinhamento_confiavel": False,
                "texto_paragrafo_alvo": "",
                "texto_paragrafo_fonte": None,
                "trecho_alvo": None,
                "necessita_revisao_humana": True,
                "motivo_revisao": "tag exige revisao manual",
            },
        ],
    }


def test_phase2_builds_review_queue_for_uncertain_in_scope_rows(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "dataset_raw.json"
    _write_json(dataset_path, _legacy_payload())

    result = phase2.run_phase2_workflow(dataset_path=dataset_path)

    samples = result["samples"]
    queue = result["queue"]

    assert len(samples) == 3
    assert samples[0]["sample_id"] == "PAT_0001_DL"
    assert samples[2]["label_scope"] == "diagnostic"

    assert len(queue) == 1
    assert queue[0]["sample_id"] == "PAT_0001_DL"
    assert "alignment_below_threshold" in queue[0]["review_reasons"]
    assert "parser_marked_for_review" in queue[0]["review_reasons"]


def test_phase2_applies_reviewer_decisions_and_clears_queue(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "dataset_raw.json"
    decisions_path = tmp_path / "decisions.json"
    _write_json(dataset_path, _legacy_payload())
    _write_json(
        decisions_path,
        {
            "decisions": [
                {
                    "sample_id": "PAT_0001_DL",
                    "decision": "validate",
                    "reviewer_id": "AN",
                    "review_notes": (
                        "Source-target mapping manually confirmed."
                    ),
                }
            ]
        },
    )

    result = phase2.run_phase2_workflow(
        dataset_path=dataset_path,
        decisions_json=decisions_path,
    )

    sample = result["samples"][0]
    assert sample["human_validated"] is True
    assert sample["reviewer_id"] == "AN"
    assert sample["review_notes"] == (
        "Source-target mapping manually confirmed."
    )
    assert "updated_at" in sample

    assert result["applied_decisions"] == 1
    assert result["queue"] == []


def test_phase2_rejects_decisions_with_unknown_sample_id(
    tmp_path: Path,
) -> None:
    dataset_path = tmp_path / "dataset_raw.json"
    _write_json(dataset_path, _legacy_payload())

    payload = _legacy_payload()
    _, samples = phase2.canonicalize_dataset_samples(payload, dataset_path)

    with pytest.raises(ValueError, match="unknown sample_id"):
        phase2.apply_review_decisions(
            samples=samples,
            decisions={"MISSING_SAMPLE": {"decision": "validate"}},
            timestamp="2026-04-01T00:00:00+00:00",
        )
