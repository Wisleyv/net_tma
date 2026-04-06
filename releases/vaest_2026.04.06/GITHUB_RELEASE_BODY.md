## VAEST Windows executable (vaest_2026.04.06)

This release provides a packaged Windows build for VAEST with a quick user guide.

### Assets

- `vaest_2026.04.06.zip`
- `release_manifest.json` (inside the zip and folder)
- `RELEASE_NOTES.md`
- `VAEST_EXE_STEP_BY_STEP.md`

### Validation

- Build: PASS (`scripts/build_validator_exe.py`)
- Headless smoke test (`dataset_raw.json`): PASS
- Headless smoke test (canonical dataset): PASS
- Release-folder runtime smoke test: PASS

### Quick Start

1. Download and unzip `vaest_2026.04.06.zip`.
2. Open the extracted folder.
3. Double-click `vaest.exe`.
4. Use `Arquivo -> Abrir dataset...` if you want to load another JSON.

### Integrity Check

Use SHA256 values in `release_manifest.json` to verify downloaded files.
