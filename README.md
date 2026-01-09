# NET_TMA – Simplification Annotation Dataset Pipeline

**NET_TMA** is a Python-based toolkit for extracting, aligning, and reviewing text simplification annotations from parallel corpora. It produces high-quality, human-validated datasets suitable for training intralingual simplification models.

The project consists of three integrated components:
1. **Document Converter**: Converts DOCX/PDF/TXT documents to Markdown for annotation preparation.
2. **Parser (CLI)**: Automatically extracts annotations from paired source-target Markdown files and produces structured JSON datasets.
3. **VAEST (Desktop Validator)**: A context-aware PySide6 GUI application for human reviewers to inspect, validate, and audit parser output with tri-state validation workflow.

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

### Document Converter
- **Multi-format Support**: Converts DOCX, PDF, and TXT files to Markdown for annotation.
- **GUI Integration**: Accessible via `Ferramentas → Importar Documento` menu in VAEST.
- **Portuguese Error Messages**: Localized feedback for end users without technical backgrounds.
- **Standalone Usage**: Can be invoked programmatically via `scripts/convert_inputs.py`.

### Parser CLI
- **Automated Annotation Extraction**: Parses inline simplification tags (e.g., `[RF+ antiga palavra]`, `[IN+ novo conceito]`) from target texts.
- **Intelligent Alignment**: Matches target paragraphs to source paragraphs using anchor-based heuristics (quoted text in tags) and semantic similarity.
- **Section-Aware Processing**: Detects document structure (headings) to improve alignment accuracy within logical sections.
- **Tag Metadata Integration**: Loads tag definitions from `tab_est.md` (tag types, descriptions, levels) and embeds them in the output.
- **Review Flags**: Automatically marks samples requiring human review when alignment confidence is low or when annotations span multiple source paragraphs.
- **JSON Output**: Exports structured `dataset_raw.json` with metadata, annotation details, alignment info, and review flags.
- **GUI Integration**: Accessible via `Ferramentas → Executar Parser` menu in VAEST.

### VAEST Validator (Desktop GUI)
- **Tri-State Validation Workflow**: Neutral (white) → Low Confidence (orange) → Validated (green) color-coded states.
- **Interactive Review Interface**: List/detail view for inspecting each annotation sample with full context.
- **Filtering & Search**: Instantly filter by tag type, review status, or full-text search across context/target/source snippets.
- **Validation Controls**: Checkbox for low-confidence flagging, notes field with context-aware placeholder, and validation button.
- **Navigation Workflow**: Voltar/Validar/Próximo buttons for efficient sequential review.
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
│   ├── build_validator_exe.py # PyInstaller build automation (Windows)
│   ├── build_validator_macos.py # PyInstaller build automation (macOS)
│   └── convert_inputs.py      # DOCX/PDF/TXT to Markdown converter
├── tests/                     # Pytest test suite
│   ├── fixtures/              # Sample Markdown files for testing
│   ├── test_segmentation_annotations.py
│   ├── test_alignment.py
│   ├── test_cli.py
│   └── test_validator_data.py
├── docs/
│   ├── executive_summary.md   # Unified roadmap and architectural vision
│   ├── project_status.md      # Development milestones and roadmap
│   ├── packaging.md           # PyInstaller build instructions
│   └── ...
├── algorithm.md               # Core alignment algorithm specification
├── design_notes.md            # Architecture and design decisions
├── parser_api.md              # Parser module contracts
├── ROADMAP.md                 # Phased action plan (Phase A-E)
├── tab_est.md                 # Tag metadata definitions (source)
├── patriotismo_st.md          # Example: source text (original)
├── patriotismo_tt.md          # Example: target text (simplified, annotated)
├── dataset_raw.json           # Parser output (generated)
├── requirements.txt           # Runtime dependencies (PySide6)
├── requirements-dev.txt       # Development dependencies (PyInstaller)
└── README.md                  # This file
```

---

## Installation

### Prerequisites
- **Python 3.10+** (tested with 3.10 and 3.11)
- **Operating System**: 
  - **Windows 10+** for `vaest.exe` executable
  - **macOS 10.15+** for `vaest.app` bundle
  - **Linux** (parser and validator work via Python; no pre-built executables yet)

### Clone the Repository
```bash
git clone https://github.com/Wisleyv/net_tma.git
cd net_tma/codebase
```

### Install Runtime Dependencies
```bash
python -m pip install -r requirements.txt
```

This installs:
- **PySide6 6.7.2** (Qt GUI framework)
- **python-docx 1.1.2** (DOCX document parsing)
- **pdfplumber 0.11.2** (PDF text extraction)

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
- `<source_text>.md` (original/complex text)
- `<target_text>.md` (simplified text with inline annotations)
- `tab_est.md` (tag definitions)

All in the current working directory. Output is written to `dataset_raw.json`.

**Note:** Replace `<source_text>` and `<target_text>` with your actual filenames. The provided sample files are `patriotismo_st.md` (source) and `patriotismo_tt.md` (target).

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
- **Sample list**: Color-coded validation states (white=neutral, orange=low confidence, green=validated).
- **Detail panel**: Displays context, target/source snippets, low-confidence checkbox, notes field, reviewer initials, and change history.
- **Action buttons**: Voltar (previous), Validar (mark validated), Próximo (next) for efficient sequential review.
- **Menu actions**: 
  - **Arquivo**: Open dataset, save reviewed JSON
  - **Ferramentas**: Import documents (DOCX/PDF/TXT → Markdown), execute parser

**Saving reviewed datasets:**
Click `Salvar...` or use `Arquivo → Salvar como...` to export the updated JSON (e.g., `dataset_reviewed.json`). All edits (review flags, notes, reviewer info, timestamps) are preserved.

---

### Using the VAEST Executable

For end users (linguists, analysts) who don't have Python installed, distribute the pre-built executable from the `dist/` folder.

**Windows (`vaest.exe`):**
1. Double-click `vaest.exe` in the `dist/` folder.
2. The application opens with the bundled `dataset_raw.json` loaded by default.
3. Use `Arquivo → Abrir dataset...` to load a different JSON file.

**macOS (`vaest.app`):**
1. Right-click `vaest.app` in the `dist/` folder and select **Open** (first launch only).
   - macOS may display a security warning; go to **System Preferences → Security & Privacy** and click **Open Anyway**.
2. On subsequent launches, double-click `vaest.app`.
3. The application opens with the bundled `dataset_raw.json` loaded by default.
4. Use `Arquivo → Abrir dataset...` to load a different JSON file.

**Distributing VAEST:**
- **Windows**: Share the entire `dist/` folder (contains `vaest.exe`, `dataset_raw.json`, and `README_VAEST.txt`).
- **macOS**: Share the entire `dist/` folder (contains `vaest.app`, `dataset_raw.json`, and `README_VAEST.txt`).
- Users can copy their own `dataset_raw.json` into the folder or open it via the file menu.

---

## Workflow

### Standard Pipeline

1. **Prepare Input Files**:
   - **Option A**: Start with existing Markdown files with paragraph IDs.
   - **Option B**: Use VAEST's document converter (`Ferramentas → Importar Documento`) to convert DOCX/PDF/TXT to Markdown.
   
2. **Annotate Target Text**:
   - Edit the Markdown file in your preferred text editor.
   - Add inline annotations using the tag syntax (e.g., `[RF+ antiga palavra]`, `[IN+ novo conceito]`).
   - Ensure paragraph IDs are present (e.g., `(01)`, `(02)`).

3. **Run the Parser**:
   - **Via CLI**:
     ```bash
     python -m parser.cli --source my_st.md --target my_tt.md --tags tab_est.md --output dataset_raw.json
     ```
   - **Via VAEST GUI**: `Ferramentas → Executar Parser` and select source/target/tags files.

4. **Review with VAEST**:
   - Open `dataset_raw.json` in VAEST (GUI or executable).
   - Review samples:
     - White background = neutral/unvalidated
     - Check "Baixo nivel de confianca" for uncertain annotations
     - Add notes justifying low-confidence flags
     - Click "Validar" to mark as validated (turns green/orange)
   - Use "Voltar"/"Próximo" buttons to navigate efficiently.
   - Filter samples by status or search by content.
   - Assign reviewer initials and add contextual notes.
   - Save the reviewed dataset as `dataset_reviewed.json`.

5. **Finalize the Dataset**:
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

To package the validator as a Windows `.exe` or macOS `.app`:

1. **Install development dependencies:**
   ```bash
   python -m pip install -r requirements-dev.txt
   ```

2. **Run the build script:**
   
   **Windows:**
   ```bash
   python scripts/build_validator_exe.py
   ```
   
   **macOS:**
   ```bash
   python scripts/build_validator_macos.py
   ```

3. **Artifacts are created in `dist/`:**
   - `vaest.exe` or `vaest.app` (single-file executable)
   - `dataset_raw.json` (bundled sample dataset)
   - `README_VAEST.txt` (quick-start instructions for analysts)

4. **Test the executable:**
   ```bash
   ./dist/vaest.exe --headless --dataset dataset_raw.json  # Windows
   # or
   ./dist/vaest.app/Contents/MacOS/vaest --headless --dataset dataset_raw.json  # macOS
   ```

**Note**: Ensure VAEST is closed before rebuilding to avoid permission errors during cleanup.

For detailed packaging instructions, see [`docs/packaging.md`](docs/packaging.md).

---

## Documentation

- **[ROADMAP.md](ROADMAP.md)**: Phased action plan (Phase A-E) tracking completed MVP and planned UX enhancements.
- **[docs/executive_summary.md](docs/executive_summary.md)**: Unified architectural vision positioning VAEST as a context-aware validation environment.
- **[algorithm.md](algorithm.md)**: Core alignment algorithm (anchor-based + similarity heuristics).
- **[design_notes.md](design_notes.md)**: Architecture overview and design rationale.
- **[parser_api.md](parser_api.md)**: Module-level contracts for the parser package.
- **[docs/project_status.md](docs/project_status.md)**: Development milestones and technical history.
- **[docs/packaging.md](docs/packaging.md)**: PyInstaller build workflow and troubleshooting.
- **[validator_app/README.md](validator_app/README.md)**: Validator-specific features and usage.

---

## Current Development Status

**Completed (Phase A):**
- ✅ Document converter (DOCX/PDF/TXT → Markdown) with GUI integration
- ✅ Parser orchestration accessible from GUI menu
- ✅ CI quality gate (GitHub Actions with ruff + pytest)
- ✅ Tri-state validation workflow (Neutral → Low Confidence → Validated)
- ✅ Color-coded validation states (white/orange/green)
- ✅ Navigation controls (Voltar/Validar/Próximo buttons)
- ✅ RTL typing bug fixed with LTR layout enforcement

**Planned (Phase B-E):**
- Portable `data/` folder for project-level artifact management
- Source/target text as first-class inputs with persistent associations
- Side-by-side contextual review panels with auto-scroll
- Controlled tag editing with audit logging
- Human-readable export (Markdown/TXT) from reviewed datasets

See [ROADMAP.md](ROADMAP.md) and [docs/executive_summary.md](docs/executive_summary.md) for detailed development priorities.

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
- **python-docx** and **pdfplumber** for document format support.
- **GitHub Actions** for continuous integration.

---

## Contact

- **Repository**: [https://github.com/Wisleyv/net_tma](https://github.com/Wisleyv/net_tma)
- **Issues**: [https://github.com/Wisleyv/net_tma/issues](https://github.com/Wisleyv/net_tma/issues)

For questions or support, please open a GitHub issue.
