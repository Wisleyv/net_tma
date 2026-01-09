# ROADMAP (Updated with current status)

This file tracks what is done, what is next, and what remains, incorporating the latest findings (see docs/executive_summary.md).

---

## Status Snapshot
- ✅ Conversion pipeline (DOCX/PDF/TXT → MD) implemented in scripts/convert_inputs.py and exposed in VAEST GUI via Ferramentas → Importar Documento.
- ✅ Parser orchestration exposed in GUI (Ferramentas → Executar Parser) and still callable via CLI.
- ✅ CI quality gate (ruff F/E9, pytest, headless validator) runs on push/PR to main.
- ✅ Packaging scripts updated to bundle converter deps (pdfplumber, python-docx) and GUI orchestrator.
- ⚠️ Build cleanup requires closing running vaest.exe before rebuilding (now emits clear message).
- ❗ UX gaps from executive summary remain (context panels, validation-state colors, tag change workflow, RTL notes bug, human-readable export, persistent data folder/tag management).

---

## Phased Action Plan (Summarized)

**Phase A — Immediate Fixes (ergonomics & clarity)**
- [x] Fix RTL typing in “Notas / Motivo da Revisão” box.
- [x] Add validation-state color mapping in segment list (e.g., green = validado, white = pendente, light red = revisar).

**Phase B — Foundational UX & State**
- [ ] Introduce portable data/ folder colocated with the executable to hold tab_est.md, source_text.md, target_text.md, metadata.json.
- [ ] Treat source/target texts as first-class: remembered paths, no repeated prompts; ensure they stay associated with loaded datasets.
- [ ] Simplify tag file handling: load once, manage via “Ferramentas → Gerenciar Arquivo de Tags…”, log changes.

**Phase C — Core Review Experience**
- [ ] Add read-only side-by-side panels for source and target context; auto-scroll/highlight relevant segments.

**Phase D — Controlled Editing (Auditability)**
- [ ] Allow tag changes via controlled action (menu/dialog), log every change in sample history.

**Phase E — Output & Sharing**
- [ ] Add human-readable export (Markdown/TXT) from reviewed dataset; keep JSON as canonical. PDF export optional/later.

---

## Completed Milestones (from original MVP plan)
- ✅ Phase 1: Pipeline Integrity — real conversion implemented and used in GUI/CLI.
- ✅ Phase 2: Safety Net — CI workflow with lint + tests + headless smoke on push/PR.
- ✅ Phase 3: Minimal Distribution — PyInstaller scripts updated for new deps; produces vaest.exe/vaest.app (ensure app is closed before rebuild).

---

## Next 2 Sprints (suggested sequence)
1) Phase A items (RTL fix + validation colors) — low risk, high UX gain.
2) Phase B essentials (data/ folder + remembered source/target + tag manager).
3) Phase C (context panels) once Phase B is stable.

---

## Notes on Risk & Regression
- Keep converter/parser callable as standalone modules (already true) to reuse in CLI/CI and future frontends.
- Guard new GUI features with graceful error dialogs (no crashes) to preserve stability of the validator core.
- When adding exports, ensure JSON remains the canonical storage; generate human-readable formats from JSON to avoid divergence.
