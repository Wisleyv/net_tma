# Development Log

## 2025-11-19
- Established parser scaffolding (`parser/` package) and CLI capable of generating `dataset_raw.json`.
- Created placeholder conversion utility in `scripts/convert_inputs.py` to normalize DOCX/PDF inputs prior to parsing.
- Adjusted workspace layout so `parser/` and `scripts/` reside within `codebase/` for easier access via VS Code.
- Added automated tag metadata extraction via `parser/tag_defs.py` and wired it into the CLI so `tab_est.md` values appear in `dataset_raw.json` metadata.

## 2025-11-20
- Refined parser internals: improved annotation extraction (multi-line tags + snippet capture), cascade heading/anchor alignment heuristics, and richer sample assembly (source text, review flags).
- Introduced `tests/` + pytest fixtures covering segmentation, annotations, `tag_defs`, alignment heuristics, and the CLI JSON output; sample fixtures live under `tests/fixtures/`.
- Added regression command `C:/Python312/python.exe -m pytest` to CI notes after verifying all six tests pass locally.
- Bootstrapped `validator_app/` (PySide6) with dataset loader, list/detail UI, and headless mode for CI smoke tests; requirements pinned in `requirements.txt`.
- Added editable review controls (checkbox + notas) and JSON export via `validator_app.view`; created headless-friendly CLI flag for automation.
- Introduced validator regression tests (`tests/test_validator_data.py`) to cover dataset load/save helpers.
- Layered filtering (tag/status/search) + reviewer/audit metadata into the PySide6 UI and wired history logging.
- Added `scripts/build_validator_exe.py`, `requirements-dev.txt`, and `docs/packaging.md` so analysts can receive a PyInstaller-built `vaest.exe` bundle (sample dataset + README included).
