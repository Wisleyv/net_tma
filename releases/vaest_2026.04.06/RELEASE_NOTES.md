# VAEST Windows Release Notes

Release ID: vaest_2026.04.06
Date (UTC): 2026-04-06

## Included Artifacts

- `vaest.exe`
- `dataset_raw.json`
- `dataset_curated.json`
- `dataset_supervised.json`
- `tab_est.md`
- `sample_source_all_tags.md`
- `sample_target_all_tags.md`
- `README_VAEST.txt`
- `VAEST_EXE_STEP_BY_STEP.md`
- `release_manifest.json` (SHA256 checksums)

## Starter Content Included

- Added a ready-to-use sample source/target pair that covers all in-scope automatic tags:
	- RF+, SL+, IN+, RP+, RD+, MOD+, DL+, EXP+, MT+
- Added canonical tag reference (`tab_est.md`) in the same folder to avoid first-run file hunting.
- Added both dataset views used by operations:
	- `dataset_curated.json` (automatic + diagnostic)
	- `dataset_supervised.json` (automatic/in-scope only)

## Validation Performed

- Build completed via `scripts/build_validator_exe.py`.
- Headless smoke test on legacy dataset: PASS (`exit=0`).
- Headless smoke test on canonical dataset: PASS (`exit=0`).
- Headless smoke test from release folder: PASS (`exit=0`).

## Runtime Fix Included

- Fixed packaging issue that could raise `ModuleNotFoundError: No module named 'PySide6'` in some builds.
- Root cause: executable built with an interpreter that did not have PySide6 installed.
- Mitigation applied:
	- packaging scripts now validate required dependencies before building
	- release executable rebuilt using project virtual environment (`.venv`)

## Deployment Recommendation

1. Upload `releases/vaest_2026.04.06.zip` to GitHub Releases.
2. Also publish `release_manifest.json` and `RELEASE_NOTES.md` in the release body/assets.
3. Ask recipients to verify file hashes from `release_manifest.json` after download.

## Known Operational Note

- Rebuild will fail with access denied if `vaest.exe` is still running.
- Close all running VAEST processes before running the build script again.
