# Project Status (2026-04-06)

This snapshot supersedes the old November/2025 status and reflects the current
state of delivery.

## Current State

- The core pipeline (conversion -> parser -> validator -> curated dataset) is
   operational and documented.
- VAEST has delivered the full B-17 UX hardening track, including:
   - persistent local project state in `data/`
   - side-by-side source/target context panels with highlighting
   - controlled TAG change with audit history logging
   - Markdown/TXT export for human-readable review output
- Canonical-v2 support is integrated in validator load/save paths (B-15 schema
   bridge).
- External handoff process is standardized with checklist + validator script
   (B-16).

## Validation and Release Readiness

- Hybrid post-B-17 validation run is complete:
   - UI smoke on legacy and canonical datasets
   - packaged executable runtime verification
   - model-sweep reproducibility closure
- Frozen release package remains available under:
   `releases/training_ready_2026.04.01-a/`
- Handoff governance artifacts are in place:
   - `docs/external_handoff_checklist.md`
   - `scripts/validate_handoff_package.py`

## In-Progress / Ongoing Work

- B-14 remains the active diagnostic-analysis track for model/data discrimination
   quality improvements.
- This is a quality-evidence loop; training execution ownership remains with the
   partner university team in the current scope.

## Primary References

- `docs/execution_board.md` for gate-by-gate tracking and iteration artifacts.
- `ROADMAP.md` for the current prioritized roadmap.
- `docs/release_note_hybrid_2026-04-06.md` for the consolidated validation
   closure note.