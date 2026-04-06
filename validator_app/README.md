# Validator App (Model 1)

Minimal PySide6 desktop shell to review annotation samples. It supports both
legacy parser output (`dataset_raw.json`) and canonical v2 curated datasets
(`dataset_curated.json`) used in the training-release workflow.

## Features
- Loads metadata + samples via `validator_app.data_loader.load_dataset`.
- Anchor list with status chips ("REVISAR" vs "OK"), reviewer initials, and
	instant filtering by tag/status/full-text search.
- Persistent project state in `data/metadata.json` plus associated
	`data/tab_est.md`, `data/source_text.md`, and `data/target_text.md`.
- Side-by-side context panel for source and target paragraphs with automatic
	highlight on mapped snippets when available.
- Detail panel showing context text, target/fonte snippets, editable review
	controls, reviewer initials, and append-only audit history.
- Controlled tag-change action (`Alterar TAG`) using managed tag definitions,
	with change history logged per sample.
- **Salvar** button + `Arquivo -> Salvar como...` persist the current dataset to
	a new JSON (e.g., `dataset_reviewed.json`).
- Human-readable review exports via `Arquivo -> Exportar revisao (Markdown)...`
	or `Arquivo -> Exportar revisao (TXT)...`.
- File menu action to open legacy or canonical-v2 dataset files and refresh the
	current dataset when regenerating from the parser CLI.

## Setup
```pwsh
python -m pip install -r requirements.txt
```
(PySide6 6.7+ is required; command above pins 6.7.2).

## Run
```pwsh
C:/Python312/python.exe -m validator_app --dataset dataset_raw.json
```

Canonical v2 example:

```pwsh
C:/Python312/python.exe -m validator_app --dataset releases/training_ready_2026.04.01-a/dataset_curated.json
```

(No flag needed if the JSON sits in the repo root.)

Press **Recarregar** to refresh after regenerating the dataset, or use
`Arquivo -> Abrir dataset...` to inspect another file. Toggle **Necessita
revisao** or edit the notas field to update `necessita_revisao_humana` and
`motivo_revisao`. Use **Alterar TAG** for controlled tag updates, and
**Salvar...** to export the updated JSON.

Use `Ferramentas -> Gerenciar Arquivo de Tags...`,
`Ferramentas -> Associar Texto Fonte...`, and
`Ferramentas -> Associar Texto Alvo...` to manage persistent project
artifacts in the local `data/` folder.

Headless smoke test (useful in CI) prints a summary without opening the UI:

```pwsh
C:/Python312/python.exe -m validator_app --headless --dataset dataset_raw.json
```

## Packaging

See `docs/packaging.md` for the PyInstaller-based workflow that produces a
single-file Windows executable (`vaest.exe`) for analysts.
