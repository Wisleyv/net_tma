# Hybrid Validation Consolidation Note (2026-04-06)

## Scope

This note consolidates the hybrid phased validation run executed after B-17 completion:

1. UI smoke validation on legacy and canonical datasets.
2. Fresh packaged build verification for VAEST.
3. B-14 model-sweep reproducibility and promotion closure.

## Phase Results

### Phase 1: UI Smoke Validation

Status: PASS

Validation targets:
- dataset_raw.json (legacy schema)
- releases/training_ready_2026.04.01-a/dataset_curated.json (canonical v2)

Outcome:
- MainWindow loaded both schemas.
- List selection rendered details and context panels without runtime errors.

### Phase 2: Packaged VAEST Verification

Status: PASS

Build:
- Rebuilt executable through scripts/build_validator_exe.py.
- Bundle produced in dist/ (vaest.exe, dataset_raw.json, README_VAEST.txt).

Packaged runtime check:
- Offscreen launch succeeded with legacy and canonical inputs.
- dist/data/metadata.json was created and persisted last_dataset_path.

### Phase 3: B-14 Reproducibility and Promotion

Status: PASS

Reproducibility report:
- reports/new_pair_v0604a_eval/model_sweep_repro_check.json

Key checks:
- recorded_top_model == reproduced_top_model: tfidf_linsvc_balanced_char35
- exact_metric_match: true
- delta_macro_f1: 0.0
- delta_weighted_f1: 0.0
- delta_accuracy: 0.0
- promotion_confirmed: true

## Updated Tracking Artifacts

- docs/execution_board.md (Iteration 6 reproducibility closure and promotion update)
- docs/eval_report_new_pair_v0604a_sweep_repro.md (human-readable repro summary)
- reports/new_pair_v0604a_eval/model_sweep_repro_check.json (machine-readable repro artifact)

## Consolidation Decision

Hybrid phased validation is complete.

- Packaging and runtime checks are stable for current workflow.
- Iteration 6 sweep winner promotion is confirmed and no longer pending reproducibility.
