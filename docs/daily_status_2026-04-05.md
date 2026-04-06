# Daily Status

Date: 2026-04-05
Phase: Phase 5 baseline complete, B-14 iteration in progress
Owner: Engineer

Historical note:
- This is a date-scoped daily log entry.
- For current project state, consult docs/execution_board.md and ROADMAP.md.

## 1) Summary

- Overall status: On track
- Biggest win today: B-14 diversified split pack and baseline rerun completed with gate pass and support-aware primary metric selection
- Biggest blocker today: holdout slices remain small and highly homogeneous, keeping generalization estimates unstable

## 2) Board Delta

- Moved to Done:
  - B-13 Baseline model training run
- Moved to In progress:
  - B-14 Error analysis and next-cycle backlog
- Newly Blocked:
  - none
- Unblocked today:
  - support floor policy met for holdout selection and full train label coverage achieved (7/7 labels)

## 3) B-14 Iteration Metrics Snapshot

- Evaluation source: test (min_primary_support=3)
- macro_f1: 0.0000
- weighted_f1: 0.0000
- accuracy: 0.0000
- Train resubstitution macro_f1: 0.7238
- Validation split rows: 3
- Test split rows: 4
- Cross-validation (kfold_fallback) macro_f1: 0.0952
- Cross-validation weighted_f1: 0.2051
- Cross-validation accuracy: 0.2308
- Note: test holdout qualifies as primary with support=4 and all labels remain represented in train

## 4) Artifacts Updated

- Files changed:
  - scripts/build_supervised_exports.py
  - tests/test_build_supervised_exports.py
  - scripts/run_baseline_training.py
  - tests/test_run_baseline_training.py
  - requirements.txt
  - docs/execution_board.md
  - docs/daily_status_2026-04-05.md
  - docs/error_analysis_backlog.md
- Reports generated:
  - reports/b14_eval/phase3_export_summary_target_groups.json
  - reports/b14_eval/training_data_gate_report.json
  - reports/b14_eval/baseline_model_report.json
  - reports/b14_eval/baseline_error_buckets.json
  - docs/eval_report_b14_iter1.md

## 5) Risks and Mitigations

- Active risk: holdout support is too small for stable model ranking
- Mitigation in place: min_primary_support guard plus split exporter min holdout rows
- Escalation needed: approve adding new document pairs for stronger split-group diversity

## 6) Plan for Next Day

1. Execute B-14 backlog item P0 by expanding corpus with new split_group_id groups and raising test support.
2. Curate targeted RF+ overprediction counterexamples in SL+/RD+/IN+/MOD+ contexts.
3. Rerun baseline after new data ingest and compare validation plus cross-validation deltas.

## 7) Decisions Logged

- Decision: use release package artifacts as the sole B-13 training source.
- Rationale: preserve reproducibility and prevent drift from unlocked local files.
- Impact: baseline metrics are traceable to release_id 2026.04.01-a.
- Decision: run B-14 interim export with group_field=target_paragraph_id.
- Rationale: unlock non-empty validation/test splits despite single original split_group_id.
- Impact: enabled holdout-capable iteration and then support-targeted split with 13/3/4 train/validation/test rows.
- Decision: require min_primary_support=3 before selecting holdout as primary source.
- Rationale: avoid unstable support-1 primary reporting.
- Impact: B-14 primary source now returns to test only when support floor is met.
- Decision: optimize split assignment for train label coverage under support constraints.
- Rationale: prevent holdout-only labels from dropping out of train in tiny-group settings.
- Impact: latest split run keeps all 7 labels represented in train.
