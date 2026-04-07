"""Helper script to package the validator GUI via PyInstaller (Windows)."""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from pathlib import Path

import PyInstaller.__main__
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

BASE_DIR = Path(__file__).resolve().parents[1]
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build" / "pyinstaller"
ENTRY_MODULE = BASE_DIR / "scripts" / "vaest_entry.py"
DATASET_PATH = BASE_DIR / "dataset_raw.json"
APP_NAME = "vaest"
STARTER_FILES = [
    (BASE_DIR / "dataset_curated.json", "dataset_curated.json"),
    (BASE_DIR / "dataset_supervised.json", "dataset_supervised.json"),
    (BASE_DIR / "tab_est.md", "tab_est.md"),
    (
        BASE_DIR / "reports" / "new_pair_v0604a" / "source_v06-04a_parser.md",
        "sample_source_all_tags.md",
    ),
    (
        BASE_DIR / "reports" / "new_pair_v0604a" / "target_v06-04a_parser.md",
        "sample_target_all_tags.md",
    ),
]


def _validate_build_environment() -> None:
    required_modules = {
        "PySide6": "PySide6",
        "docx": "python-docx",
        "pdfplumber": "pdfplumber",
        "pdfminer": "pdfminer.six",
    }

    missing: list[str] = []
    for module_name, package_name in required_modules.items():
        if importlib.util.find_spec(module_name) is None:
            missing.append(package_name)

    if not missing:
        return

    print("\n" + "=" * 70)
    print("ERRO: dependencias obrigatorias ausentes para empacotamento.")
    print("\nInterpretador usado:")
    print(f"  {sys.executable}")
    print("\nPacotes ausentes:")
    for package_name in missing:
        print(f"  - {package_name}")
    print("\nInstale os requisitos no mesmo interpretador e tente novamente:")
    print("  python -m pip install -r requirements.txt")
    print("  python -m pip install -r requirements-dev.txt")
    print("=" * 70 + "\n")
    raise SystemExit(2)


def _clean_previous() -> None:
    try:
        if DIST_DIR.exists():
            shutil.rmtree(DIST_DIR)
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)
    except PermissionError as exc:
        print("\n" + "="*70)
        print("ERRO: Nao foi possivel limpar os arquivos antigos.")
        print("\nO arquivo vaest.exe pode estar em uso (aberto).")
        print("Feche o aplicativo e tente novamente.")
        print("\nDetalhes tecnicos:")
        print(f"  {exc}")
        print("="*70 + "\n")
        raise SystemExit(1) from exc


def _copy_bundle_resources() -> None:
    """Copy runtime dataset plus optional starter assets to dist/."""

    bundle_readme = DIST_DIR / "README_VAEST.txt"
    bundle_readme.write_text(
        (
            "VAEST quick start (Windows)\n\n"
            "1) Execute vaest.exe.\n"
            "2) Open a dataset via Arquivo -> Abrir dataset... "
            "(or keep JSON in the same folder).\n\n"
            "Included JSON files:\n"
            "- dataset_raw.json: legacy parser output (includes all tags).\n"
            "- dataset_curated.json: canonical v2 dataset with automatic + "
            "diagnostic labels.\n"
            "- dataset_supervised.json: supervised-ready subset "
            "(automatic/in-scope labels only).\n\n"
            "Included starter files:\n"
            "- tab_est.md: canonical tag definitions.\n"
            "- sample_source_all_tags.md + sample_target_all_tags.md: "
            "source/target pair with all in-scope automatic tags "
            "(RF+, SL+, IN+, RP+, RD+, MOD+, DL+, EXP+, MT+).\n\n"
            "Operational note:\n"
            "- OM+ and PRO+ are diagnostic labels, not part of the "
            "supervised in-scope set.\n"
        ),
        encoding="utf-8",
    )

    if DATASET_PATH.exists():
        shutil.copy2(DATASET_PATH, DIST_DIR / DATASET_PATH.name)

    for source_path, target_name in STARTER_FILES:
        if source_path.exists():
            shutil.copy2(source_path, DIST_DIR / target_name)


def build() -> None:
    _validate_build_environment()
    _clean_previous()
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    if DATASET_PATH.exists():
        data_arg = f"{DATASET_PATH}{os.pathsep}."
    else:
        data_arg = None

    # Collect hook data for converter dependencies
    hidden_modules = [
        "validator_app",
        "validator_app.__main__",
        "validator_app.view",
        "validator_app.data_loader",
        "validator_app.models",
        "PySide6",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "scripts.convert_inputs",
    ]

    hidden_modules.extend(collect_submodules("pdfplumber"))
    hidden_modules.extend(collect_submodules("pdfminer"))
    hidden_modules.extend(collect_submodules("docx"))

    data_files = []
    data_files.extend(collect_data_files("pdfplumber"))
    data_files.extend(collect_data_files("pdfminer"))
    data_files.extend(collect_data_files("docx"))

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

    for module_name in hidden_modules:
        args.extend(["--hidden-import", module_name])

    for src, dest in data_files:
        args.extend(["--add-data", f"{src}{os.pathsep}{dest}"])

    args.append(str(ENTRY_MODULE))

    PyInstaller.__main__.run(args)

    _copy_bundle_resources()


if __name__ == "__main__":
    build()
