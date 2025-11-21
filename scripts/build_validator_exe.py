"""Helper script to package the validator GUI via PyInstaller."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import PyInstaller.__main__

BASE_DIR = Path(__file__).resolve().parents[1]
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build" / "pyinstaller"
ENTRY_MODULE = BASE_DIR / "scripts" / "vaest_entry.py"
DATASET_PATH = BASE_DIR / "dataset_raw.json"
APP_NAME = "vaest"


def build() -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    if DATASET_PATH.exists():
        data_arg = f"{DATASET_PATH}{os.pathsep}."
    else:
        data_arg = None

    args = [
        "--name",
        APP_NAME,
        "--noconfirm",
        "--noconsole",
        "--onefile",
        "--clean",
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
    ]
    if data_arg:
        args.extend(["--add-data", data_arg])
    args.extend(["--paths", str(BASE_DIR)])
    hidden_modules = [
        "validator_app",
        "validator_app.__main__",
        "validator_app.view",
        "validator_app.data_loader",
        "validator_app.models",
    ]
    for module_name in hidden_modules:
        args.extend(["--hidden-import", module_name])
    args.append(str(ENTRY_MODULE))

    PyInstaller.__main__.run(args)

    # Copy README + sample dataset next to the executable for analysts.
    bundle_readme = DIST_DIR / "README_VAEST.txt"
    bundle_readme.write_text(
        (
            "Executar vaest.exe para abrir o Validador de Anotacoes sobre "
            "Estrategias de Simplificacao Textual. Coloque seu "
            "dataset_raw.json na mesma pasta ou use o menu Arquivo -> "
            "Abrir."
        ),
        encoding="utf-8",
    )
    if DATASET_PATH.exists():
        shutil.copy2(DATASET_PATH, DIST_DIR / DATASET_PATH.name)


if __name__ == "__main__":
    build()
