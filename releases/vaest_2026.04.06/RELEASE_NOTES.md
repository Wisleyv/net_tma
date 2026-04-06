# VAEST Windows Release Notes

Release ID: vaest_2026.04.06
Date (UTC): 2026-04-06

## Included Artifacts

- `vaest.exe`
- `dataset_raw.json`
- `README_VAEST.txt`
- `VAEST_EXE_STEP_BY_STEP.md`
- `release_manifest.json` (SHA256 checksums)

## Validation Performed

- Build completed via `scripts/build_validator_exe.py`.
- Headless smoke test on legacy dataset: PASS (`exit=0`).
- Headless smoke test on canonical dataset: PASS (`exit=0`).
- Headless smoke test from release folder: PASS (`exit=0`).

## Deployment Recommendation

1. Upload `releases/vaest_2026.04.06.zip` to GitHub Releases.
2. Also publish `release_manifest.json` and `RELEASE_NOTES.md` in the release body/assets.
3. Ask recipients to verify file hashes from `release_manifest.json` after download.

## Known Operational Note

- Rebuild will fail with access denied if `vaest.exe` is still running.
- Close all running VAEST processes before running the build script again.
