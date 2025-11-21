## Project Status in November 20 2025
Current state looks solidly aligned with the documented goal of generating a gold-standard dataset for intralingual simplification:

- Core documentation (algorithm.md, copilot_instructions.md, parser_api.md, design_notes.md, dev_log.md) consistently describe the Model‑1 pipeline (parser + desktop validator) and its constraints (paragraph-level, annotation-centric, best-effort alignment).
- Parser scaffolding is in place under parser with modules for segmentation, annotation extraction, alignment, sample building, schema definitions, and CLI orchestration. `parser.cli` now loads real tag metadata from tab_est.md and produces dataset_raw.json using local defaults.
- Parser internals were upgraded (Nov 20) with stronger heading detection, anchor/similarity alignment, richer annotation snippets, and more faithful sample assembly (fonte/alvo snippets + review flags).
- Input conversion prep (convert_inputs.py) ensures future DOCX/PDF sources can be normalized into the Markdown format the parser expects.
- Sample source/target texts (patriotismo_st.md, patriotismo_tt.md) plus tab_est.md provide the raw material for the parser, and dataset_raw.json confirms end-to-end wiring works.

Given that foundation, the logical roadmap is:

1. **Enhance parser logic _(DONE – Nov 20, 2025)_**
   - Implemented heading/section detection, anchor-driven + similarity alignment, multi-line tag handling, snippet extraction, and richer builder outputs (trechos, fonte text, review flags).
   - Tag metadata now flows from `tab_est.md` via `parser/tag_defs.py`.

2. **Add automated tests/fixtures _(DONE – Nov 20, 2025)_**
   - Added `tests/` with pytest, including markdown fixtures for segmentation/annotation scenarios.
   - Covered `segmentation`, `annotations`, `tag_defs`, alignment heuristics (anchor + similarity), and the CLI JSON output to guard against regressions.

3. **Develop the Windows validator app _(DONE – Nov 20, 2025)_**
   - `validator_app/` now loads `dataset_raw.json`, exposes a PySide6 list/detail UI, supports headless mode for CI smoke tests, and lets reviewers editar notas/flags.
   - Added reviewer-friendly workflows: tag/status/search filters, inline reviewer initials, and append-only audit history rendered per sample.
   - Dataset load/save helpers are unit-tested via `tests/test_validator_data.py`.

4. **Package the validator for analysts _(DONE – Nov 20, 2025)_**
   - Added `requirements-dev.txt`, `docs/packaging.md`, and `scripts/build_validator_exe.py` (PyInstaller wrapper) to emit `vaest.exe` under `dist/`.
   - Bundle includes a sample `dataset_raw.json` plus README for distribution.

Next iteration can focus on analyst niceties (batch approvals, diff exports) and parser-to-validator automation, but the current build is ready for packaging and distribution.