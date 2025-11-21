# NET_TMA – Simplification Annotation Dataset Pipeline

**NET_TMA** is a Python-based toolkit for extracting, aligning, and reviewing text simplification annotations from parallel corpora. It produces high-quality, human-validated datasets suitable for training intralingual simplification models.

The project consists of two main components:
1. **Parser (CLI)**: Automatically extracts annotations from paired source-target Markdown files and produces structured JSON datasets.
2. **VAEST (Desktop Validator)**: A PySide6 GUI application that allows human reviewers to inspect, correct, and validate the parser output before finalizing the dataset.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [Running the Parser](#running-the-parser)
  - [Running the Validator](#running-the-validator)
  - [Using the VAEST Executable](#using-the-vaest-executable)
- [Workflow](#workflow)
- [Development](#development)
  - [Running Tests](#running-tests)
  - [Building the VAEST Executable](#building-the-vaest-executable)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### Parser CLI
- **Automated Annotation Extraction**: Parses inline simplification tags (e.g., `[RF+ antiga palavra]`, `[IN+ novo conceito]`) from target texts.
- **Intelligent Alignment**: Matches target paragraphs to source paragraphs using anchor-based heuristics (quoted text in tags) and semantic similarity.
- **Section-Aware Processing**: Detects document structure (headings) to improve alignment accuracy within logical sections.
- **Tag Metadata Integration**: Loads tag definitions from `tab_est.md` (tag types, descriptions, levels) and embeds them in the output.
- **Review Flags**: Automatically marks samples requiring human review when alignment confidence is low or when annotations span multiple source paragraphs.
- **JSON Output**: Exports structured `dataset_raw.json` with metadata, annotation details, alignment info, and review flags.

### VAEST Validator (Desktop GUI)
- **Interactive Review Interface**: List/detail view for inspecting each annotation sample with full context.
- **Filtering & Search**: Instantly filter by tag type, review status, or full-text search across context/target/source snippets.
- **Editable Review Controls**: Toggle review flags, add notes, and assign reviewer initials directly in the UI.
- **Audit History**: Append-only change log per sample, recording timestamps, reviewers, and actions.
- **Dataset Management**: Load/reload datasets, save reviewed JSON files, and open multiple datasets via file menu.
- **Windows Executable**: Distributable `.exe` (VAEST) packaged with PyInstaller—no Python installation required for end users.

---

## Project Structure

```
codebase/
├── parser/                    # Annotation parser and alignment engine
│   ├── cli.py                 # Command-line entry point
│   ├── segmentation.py        # Paragraph extraction and ID assignment
│   ├── annotations.py         # Tag parsing and snippet extraction
│   ├── alignment.py           # Source-target paragraph alignment
│   ├── builder.py             # JSON sample construction
│   ├── tag_defs.py            # Tag metadata loader
│   ├── schema.py              # Data structures (AnnotationSample, Metadata)
│   └── io_utils.py            # File I/O utilities
├── validator_app/             # PySide6 desktop validator application
│   ├── __main__.py            # Entry point for `python -m validator_app`
│   ├── view.py                # Main window, list/detail panels, filtering
│   ├── models.py              # Data models (AnnotationSample, Metadata)
│   └── data_loader.py         # JSON load/save helpers
├── scripts/
│   ├── vaest_entry.py         # Standalone entry script for PyInstaller
│   ├── build_validator_exe.py # PyInstaller build automation
│   └── convert_inputs.py      # (Placeholder) DOCX/PDF to Markdown converter
├── tests/                     # Pytest test suite
│   ├── fixtures/              # Sample Markdown files for testing
│   ├── test_segmentation_annotations.py
│   ├── test_alignment.py
│   ├── test_cli.py
│   └── test_validator_data.py
├── docs/
│   ├── project_status.md      # Development milestones and roadmap
│   ├── packaging.md           # PyInstaller build instructions
│   └── ...
├── algorithm.md               # Core alignment algorithm specification
├── design_notes.md            # Architecture and design decisions
├── parser_api.md              # Parser module contracts
├── tab_est.md                 # Tag metadata definitions (source)
├── patriotismo_st.md          # Sample source text (original)
├── patriotismo_tt.md          # Sample target text (simplified, annotated)
├── dataset_raw.json           # Parser output (generated)
├── requirements.txt           # Runtime dependencies (PySide6)
├── requirements-dev.txt       # Development dependencies (PyInstaller)
└── README.md                  # This file
```

---

## Installation

### Prerequisites
- **Python 3.12+** (tested with 3.12.7)
- **Windows OS** (for VAEST executable; parser runs cross-platform)

### Clone the Repository
```bash
git clone https://github.com/Wisleyv/net_tma.git
cd net_tma/codebase
```

### Install Runtime Dependencies
```bash
python -m pip install -r requirements.txt
```

This installs **PySide6 6.7.2** (required for the validator GUI).

### (Optional) Install Development Tools
```bash
python -m pip install -r requirements-dev.txt
```

This adds **PyInstaller 6.11.0** for building the VAEST executable.

---

## Quick Start

### Running the Parser

The parser reads annotated Markdown files and produces `dataset_raw.json`.

**Basic usage:**
```bash
python -m parser.cli
```

By default, it expects:
- `patriotismo_st.md` (source text)
- `patriotismo_tt.md` (target text with annotations)
- `tab_est.md` (tag definitions)

All in the current working directory. Output is written to `dataset_raw.json`.

**Custom paths:**
```bash
python -m parser.cli --source my_source.md --target my_target.md --tags my_tags.md --output my_dataset.json
```

Run `python -m parser.cli --help` for full options.

**Sample output structure:**
```json
{
  "metadata": {
    "projeto": "NET_TMA",
    "versao": "1.0",
    "idioma": "pt-BR",
    "descricao": "Dataset anotado para simplificação textual intralingual",
    "padrao_tags": "Consulte tab_est.md para especificação completa"
  },
  "amostras": [
    {
      "id": "st-001",
      "tag": "RF",
      "nome": "Reformulação",
      "tipo_nivel": "Nível 1",
      "contexto_anotacao": "Parágrafo contendo a reformulação...",
      "paragrafo_alvo_id": "tt-010",
      "paragrafo_fonte_ids": ["st-012"],
      "fonte_alinhamento_confiavel": true,
      "texto_paragrafo_alvo": "Texto limpo do parágrafo alvo...",
      "texto_paragrafo_fonte": "Texto do parágrafo fonte correspondente...",
      "trecho_alvo": "palavra reformulada",
      "trecho_fonte": "palavra original",
      "necessita_revisao_humana": false,
      "motivo_revisao": null,
      "reviewer": null,
      "updated_at": null,
      "history": []
    }
  ]
}
```

---

### Running the Validator

The validator GUI loads `dataset_raw.json` and provides an interactive review interface.

**From source:**
```bash
python -m validator_app --dataset dataset_raw.json
```

**Headless mode (for CI/automation):**
```bash
python -m validator_app --headless --dataset dataset_raw.json
```

This prints a summary without opening the GUI.

**Main UI features:**
- **Filter bar**: Combo boxes for tag type and review status, plus full-text search.
- **Sample list**: Shows all annotations with status indicators ("OK" / "REVISAR").
- **Detail panel**: Displays context, target/source snippets, review checkbox, notes field, reviewer initials, and change history.
- **Menu actions**: Open dataset, reload, save reviewed JSON.

**Saving reviewed datasets:**
Click `Salvar...` or use `Arquivo → Salvar como...` to export the updated JSON (e.g., `dataset_reviewed.json`). All edits (review flags, notes, reviewer info, timestamps) are preserved.

---

### Using the VAEST Executable

For end users (linguists, analysts) who don't have Python installed, distribute the pre-built `vaest.exe` from the `dist/` folder.

**To launch:**
1. Double-click `vaest.exe` in the `dist/` folder.
2. The application opens with the bundled `dataset_raw.json` loaded by default.
3. Use `Arquivo → Abrir dataset...` to load a different JSON file.

**Distributing VAEST:**
- Share the entire `dist/` folder (contains `vaest.exe`, `dataset_raw.json`, and `README_VAEST.txt`).
- Users can copy their own `dataset_raw.json` into the folder or open it via the file menu.

---

## Workflow

1. **Prepare Input Files**:
   - Source text (`*_st.md`): Original text in Markdown format, with paragraph IDs like `(01)`.
   - Target text (`*_tt.md`): Simplified text with inline annotations (e.g., `[RF+ antiga palavra]`).
   - Tag definitions (`tab_est.md`): Table mapping tag codes to names, types, and descriptions.

2. **Run the Parser**:
   ```bash
   python -m parser.cli --source my_st.md --target my_tt.md --tags tab_est.md --output dataset_raw.json
   ```

3. **Review with VAEST**:
   - Open `dataset_raw.json` in VAEST (GUI or executable).
   - Filter samples flagged for review (`necessita_revisao_humana: true`).
   - Inspect alignment, edit notes, toggle flags, assign reviewer initials.
   - Save the reviewed dataset as `dataset_reviewed.json`.

4. **Finalize the Dataset**:
   - The reviewed JSON becomes the gold-standard dataset for training simplification models or further linguistic analysis.

---

## Development

### Running Tests

The project includes a pytest suite covering parser logic, alignment heuristics, and validator data helpers.

```bash
python -m pytest
```

**Expected output:**
```
======================================== test session starts =========================================
collected 8 items

tests\test_alignment.py ..                                                                      [ 25%]
tests\test_cli.py .                                                                             [ 37%]
tests\test_segmentation_annotations.py ..                                                       [ 62%]
tests\test_tag_defs.py .                                                                        [ 75%]
tests\test_validator_data.py ..                                                                 [100%]

========================================= 8 passed in 0.08s ==========================================
```

---

### Building the VAEST Executable

To package the validator as a Windows `.exe`:

1. **Install development dependencies:**
   ```bash
   python -m pip install -r requirements-dev.txt
   ```

2. **Run the build script:**
   ```bash
   python scripts/build_validator_exe.py
   ```

3. **Artifacts are created in `dist/`:**
   - `vaest.exe` (single-file executable, ~30 MB)
   - `dataset_raw.json` (bundled sample dataset)
   - `README_VAEST.txt` (quick-start instructions for analysts)

4. **Test the executable:**
   ```bash
   ./dist/vaest.exe --headless --dataset dataset_raw.json
   ```

For detailed packaging instructions, see [`docs/packaging.md`](docs/packaging.md).

---

## Documentation

- **[algorithm.md](algorithm.md)**: Core alignment algorithm (anchor-based + similarity heuristics).
- **[design_notes.md](design_notes.md)**: Architecture overview and design rationale.
- **[parser_api.md](parser_api.md)**: Module-level contracts for the parser package.
- **[docs/project_status.md](docs/project_status.md)**: Development milestones and roadmap.
- **[docs/packaging.md](docs/packaging.md)**: PyInstaller build workflow and troubleshooting.
- **[validator_app/README.md](validator_app/README.md)**: Validator-specific features and usage.

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** and create a feature branch.
2. **Run tests** before submitting a pull request:
   ```bash
   python -m pytest
   ```
3. **Follow existing code style** (PEP 8, type hints, docstrings).
4. **Document new features** in relevant Markdown files (e.g., update `README.md` or add notes to `docs/`).
5. **Submit a pull request** with a clear description of changes.

For major changes, please open an issue first to discuss the proposed approach.

---

## License

This project is currently unlicensed. For licensing inquiries or collaboration opportunities, please contact the repository owner.

---

## Acknowledgments

- **PySide6** (Qt for Python) for the desktop GUI framework.
- **PyInstaller** for executable packaging.
- **pytest** for testing infrastructure.

---

## Contact

- **Repository**: [https://github.com/Wisleyv/net_tma](https://github.com/Wisleyv/net_tma)
- **Issues**: [https://github.com/Wisleyv/net_tma/issues](https://github.com/Wisleyv/net_tma/issues)

For questions or support, please open a GitHub issue.
