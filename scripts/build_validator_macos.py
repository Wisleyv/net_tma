"""Helper script to package the validator GUI via PyInstaller for macOS."""

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
    """Build macOS .app bundle using PyInstaller."""
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
        "--windowed",  # macOS equivalent of --noconsole, creates .app bundle
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
    
    # Hidden imports for validator_app package
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

    # Copy README + sample dataset next to the .app bundle for analysts.
    # On macOS, the executable is inside vaest.app/Contents/MacOS/vaest,
    # but we place resources at the dist/ level for easy access.
    bundle_readme = DIST_DIR / "README_VAEST.txt"
    bundle_readme.write_text(
        (
            "Abrir vaest.app para usar o Validador de Anotações sobre "
            "Estratégias de Simplificação Textual.\n\n"
            "Coloque seu dataset_raw.json na mesma pasta (dist/) ou use o "
            "menu Arquivo -> Abrir.\n\n"
            "NOTA: Na primeira execução, o macOS pode pedir permissão para "
            "executar aplicativos de desenvolvedores não identificados. "
            "Vá em Preferências do Sistema → Segurança e Privacidade e "
            "clique em 'Abrir Mesmo Assim'."
        ),
        encoding="utf-8",
    )
    
    if DATASET_PATH.exists():
        shutil.copy2(DATASET_PATH, DIST_DIR / DATASET_PATH.name)
    
    print("\n" + "="*60)
    print(f"✅ Build concluído: {DIST_DIR / f'{APP_NAME}.app'}")
    print(f"📂 Recursos copiados para: {DIST_DIR}")
    print("="*60 + "\n")


if __name__ == "__main__":
    build()
