from __future__ import annotations

from pathlib import Path

from validator_app.project_store import (
    ProjectState,
    load_project_state,
    persist_source_text,
    persist_tags_file,
    persist_target_text,
    resolve_data_dir,
    save_project_state,
)


def test_project_state_defaults_when_missing(tmp_path: Path) -> None:
    state = load_project_state(runtime_root=tmp_path)
    assert state == ProjectState()


def test_project_state_save_and_load_roundtrip(tmp_path: Path) -> None:
    expected = ProjectState(
        tags_path="x/tab_est.md",
        source_text_path="x/source.md",
        target_text_path="x/target.md",
        last_dataset_path="x/dataset.json",
    )
    save_project_state(expected, runtime_root=tmp_path)

    observed = load_project_state(runtime_root=tmp_path)
    assert observed == expected


def test_persist_artifacts_into_data_directory(tmp_path: Path) -> None:
    source = tmp_path / "in_source.txt"
    target = tmp_path / "in_target.txt"
    tags = tmp_path / "in_tags.md"

    source.write_text("Fonte com acao", encoding="utf-8")
    target.write_text("Alvo com revisao", encoding="utf-8")
    tags.write_text("### 2.1 Reformulacao (RF+)", encoding="utf-8")

    out_source = persist_source_text(source, runtime_root=tmp_path)
    out_target = persist_target_text(target, runtime_root=tmp_path)
    out_tags = persist_tags_file(tags, runtime_root=tmp_path)

    data_dir = resolve_data_dir(runtime_root=tmp_path)
    assert out_source == data_dir / "source_text.md"
    assert out_target == data_dir / "target_text.md"
    assert out_tags == data_dir / "tab_est.md"

    assert out_source.read_text(encoding="utf-8") == "Fonte com acao"
    assert out_target.read_text(encoding="utf-8") == "Alvo com revisao"
    assert "RF+" in out_tags.read_text(encoding="utf-8")
