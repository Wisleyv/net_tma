# Packaging Guide

This document describes how to build a distributable Windows executable for the
PySide6 validator application.

## Prerequisites
- Python 3.12 (same interpreter used for development).
- All runtime requirements: `python -m pip install -r requirements.txt`.
- Packaging toolchain: `python -m pip install -r requirements-dev.txt` (installs
  PyInstaller 6.11).

## Build Steps
From the repository root:

```pwsh
C:/Python312/python.exe scripts/build_validator_exe.py
```

The script wraps PyInstaller with project defaults:
- Generates a one-file executable named `vaest.exe`.
- Outputs artifacts under `dist/` and intermediary files under `build/pyinstaller/`.
- Bundles the latest `dataset_raw.json` and a short README next to the exe for
easy smoke-testing.

## Resulting Bundle
After the command finishes you should see:

```
dist/
  vaest.exe
  dataset_raw.json        # sample dataset used by default when launching
  README_VAEST.txt
```

Share the entire `dist/` folder with analysts. They can double-click
`vaest.exe` to launch the GUI, load their own dataset via the
menu, and save reviewed JSON files locally.

## Updating the Bundle
Whenever parser outputs or validator UI change, re-run the same command to build
an updated executable. Clean-up is automatic, but you can remove `build/` and
`dist/` manually if needed.
