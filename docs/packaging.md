# Packaging Guide

This document describes how to build distributable executables for the
PySide6 validator application on **Windows** and **macOS**.

## Prerequisites
- Python 3.12+ (same interpreter used for development).
- All runtime requirements: `python -m pip install -r requirements.txt`.
- Packaging toolchain: `python -m pip install -r requirements-dev.txt` (installs
  PyInstaller 6.11).

---

## Windows Build

### Build Steps
From the repository root:

```pwsh
C:/Python312/python.exe scripts/build_validator_exe.py
```

The script wraps PyInstaller with project defaults:
- Generates a one-file executable named `vaest.exe`.
- Outputs artifacts under `dist/` and intermediary files under `build/pyinstaller/`.
- Bundles the latest `dataset_raw.json` and a short README next to the exe for
easy smoke-testing.

### Resulting Bundle
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

---

## macOS Build

### Build Steps
From the repository root (on a Mac with Python 3.12+ installed):

```bash
python3 scripts/build_validator_macos.py
```

The script wraps PyInstaller with macOS-specific flags:
- Generates a `.app` bundle named `vaest.app`.
- Uses `--windowed` flag (macOS equivalent of `--noconsole` on Windows).
- Outputs artifacts under `dist/` and intermediary files under `build/pyinstaller/`.
- Bundles the latest `dataset_raw.json` and a macOS-specific README next to the app.

### Resulting Bundle
After the command finishes you should see:

```
dist/
  vaest.app/              # macOS application bundle
    Contents/
      MacOS/
        vaest             # actual executable
      Resources/
      Info.plist
  dataset_raw.json        # sample dataset used by default when launching
  README_VAEST.txt
```

**Distribution:**
- Share the entire `dist/` folder with analysts.
- On first launch, users must right-click `vaest.app` → **Open** and confirm the security dialog.
- Subsequent launches: double-click `vaest.app`.

**Important Notes for macOS:**
- The app may be blocked by Gatekeeper ("unidentified developer"). Users need to authorize it in **System Preferences → Security & Privacy**.
- If distributing via download, consider notarizing the app with an Apple Developer ID to avoid security warnings.
- The `dataset_raw.json` should be placed in the same `dist/` folder (not inside `vaest.app/Contents/`), as the app loads files from its parent directory.

---

## Cross-Platform Notes

Both scripts (`build_validator_exe.py` and `build_validator_macos.py`) share the same core logic:
- **Entry point**: `scripts/vaest_entry.py` (avoids relative import issues)
- **Hidden imports**: Explicitly bundle `validator_app` submodules
- **Data files**: Automatically include `dataset_raw.json` if present

The only difference is the PyInstaller flag:
- Windows: `--noconsole` (hides command prompt window)
- macOS: `--windowed` (creates `.app` bundle structure)

## Updating the Bundle
Whenever parser outputs or validator UI change, re-run the same command to build
an updated executable. Clean-up is automatic, but you can remove `build/` and
`dist/` manually if needed.
