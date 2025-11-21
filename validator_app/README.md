# Validator App (Model 1)

Minimal PySide6 desktop shell to review `dataset_raw.json` samples. It loads the
JSON exported by `parser.cli`, lists annotations on the left, and displays
context/trechos/review flags on the right.

## Features
- Loads metadata + samples via `validator_app.data_loader.load_dataset`.
- Anchor list with status chips ("REVISAR" vs "OK"), reviewer initials, and
	instant filtering by tag/status/full-text search.
- Detail panel showing context text, target/fonte snippets, editable review
	controls, reviewer initials, and append-only audit history.
- **Salvar** button + `Arquivo -> Salvar como...` persist the current dataset to
	a new JSON (e.g., `dataset_reviewed.json`).
- File menu action to open any `dataset_raw.json`-compatible file or refresh the
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
(No flag needed if the JSON sits in the repo root.)

Press **Recarregar** to refresh after regenerating the dataset, or use
`Arquivo -> Abrir dataset...` to inspect another file. Toggle **Necessita
revisao** or edit the notas field to update `necessita_revisao_humana` and
`motivo_revisao`. Use **Salvar...** to export the updated JSON.

Headless smoke test (useful in CI) prints a summary without opening the UI:

```pwsh
C:/Python312/python.exe -m validator_app --headless --dataset dataset_raw.json
```

## Packaging

See `docs/packaging.md` for the PyInstaller-based workflow that produces a
single-file Windows executable (`vaest.exe`) for analysts.
