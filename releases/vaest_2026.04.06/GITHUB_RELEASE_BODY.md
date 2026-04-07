## VAEST Windows executable (vaest_2026.04.06)

This release provides a packaged Windows build for VAEST with a quick user guide.

### Assets

- `vaest_2026.04.06.zip`
- `release_manifest.json` (inside the zip and folder)
- `RELEASE_NOTES.md`
- `VAEST_EXE_STEP_BY_STEP.md`
- `tab_est.md`
- `sample_source_all_tags.md`
- `sample_target_all_tags.md`
- `dataset_curated.json`
- `dataset_supervised.json`

### Validation

- Build: PASS (`scripts/build_validator_exe.py`)
- Headless smoke test (`dataset_raw.json`): PASS
- Headless smoke test (canonical dataset): PASS
- Release-folder runtime smoke test: PASS

### Runtime Fix Included

- Fixed packaging issue that could cause `ModuleNotFoundError: No module named 'PySide6'` in some builds.
- This release was rebuilt using the project virtual environment and validated again.

### Quick Start

1. Download and unzip `vaest_2026.04.06.zip`.
2. Open the extracted folder.
3. Double-click `vaest.exe`.
4. Open `dataset_raw.json`, `dataset_curated.json`, or `dataset_supervised.json` via `Arquivo -> Abrir dataset...`.
5. Optional: use `Ferramentas -> Associar Texto Fonte...` and `Ferramentas -> Associar Texto Alvo...` with `sample_source_all_tags.md` and `sample_target_all_tags.md`.

### Starter Coverage

- Included sample pair covers all in-scope automatic tags:
	- RF+, SL+, IN+, RP+, RD+, MOD+, DL+, EXP+, MT+

### Integrity Check

Use SHA256 values in `release_manifest.json` to verify downloaded files.
