# ROADMAP (Current Snapshot)

This file tracks what is done and what is next after the 2026-04-06
consolidation run.

## Scope Guardrail (2026-04-06)
- Current phase deliverable: training-ready dataset package + handoff
  documentation for the external university training team.
- Product model-training ownership remains outside this repository scope.
- Internal baseline/sweep runs are diagnostic evidence for dataset quality.

---

## Status Snapshot
- ✅ Conversion pipeline (DOCX/PDF/TXT -> MD) implemented and exposed in VAEST.
- ✅ Parser orchestration available in GUI and CLI.
- ✅ CI quality gate in place (ruff + pytest + validator headless smoke).
- ✅ Packaging scripts produce analyst-ready VAEST bundles.
- ✅ B-15 schema bridge delivered (legacy + canonical-v2 dataset support).
- ✅ B-16 external handoff standard delivered (checklist + validator script).
- ✅ B-17 UX hardening delivered:
  - persistent local `data/` project state
  - source/target side-by-side context panels with highlighting
  - controlled TAG change with audit logging
  - Markdown/TXT review export
- ✅ Hybrid post-B-17 validation completed:
  - UI smoke on legacy + canonical datasets
  - packaged runtime verification
  - model-sweep reproducibility closure

---

## Delivered UX Track (Phase A-E)

**Phase A — Immediate Fixes**
- [x] RTL typing fix for review notes
- [x] validation-state color mapping in sample list

**Phase B — Foundational UX & State**
- [x] portable `data/` folder with metadata + associated artifacts
- [x] source/target texts as first-class persisted associations
- [x] managed tag file workflow via VAEST tools menu

**Phase C — Core Review Experience**
- [x] read-only side-by-side source/target context panels
- [x] auto-focus highlight for mapped snippets

**Phase D — Controlled Editing (Auditability)**
- [x] controlled tag-change action with per-sample history logging

**Phase E — Output & Sharing**
- [x] human-readable Markdown/TXT export from reviewed dataset
- [ ] PDF export (optional, lower priority)

---

## Current Priorities (Post-B-17)
1. Continue B-14 diagnostic iteration backlog for data/model discrimination
   improvements with reproducible reporting.
2. Keep release-package and handoff validation workflow stable for external
   training operations.
3. Expand corpus diversity (split-group breadth) before treating holdout metrics
   as strong comparative evidence.

---

## Risk & Regression Notes
- Preserve JSON as canonical source of truth; human-readable exports must remain
  derived artifacts.
- Keep converter/parser entry points callable as standalone scripts for CI,
  packaging, and future automation.
- Maintain schema-bridge compatibility in validator save/load paths to avoid
  field loss on canonical-v2 datasets.
