# Execution Board (Training Data Readiness)

Date: 2026-04-01
Cadence: Daily check-in, gate-driven progression
Board type: Dependency-aware Kanban with phase gates

## 1. Board Overview

Status legend:
- Not started
- In progress
- Blocked
- Done

Current snapshot:
- Current phase: Phase 7 UX hardening delivered (B-17 done), B-14 in progress
- Last updated: 2026-04-06
- Completed: B-00, B-01, B-02, B-03, B-04, B-05, B-06, B-07, B-08, B-09, B-10, B-11, B-12, B-13, B-15, B-16, B-17
- Active: B-14
- Waiting: none

Scope alignment update (2026-04-06):
- Primary deliverable for this project phase is a training-ready dataset package plus handoff documentation for an external university training team.
- Internal model runs remain diagnostic evidence for dataset quality, not product-training deliverables.
- Full roadmap review and VAEST suitability assessment: docs/roadmap_review_2026-04-06.md.
- VAEST status after backend updates: suitable for legacy parser-output and canonical-v2 curated dataset QA (schema bridge delivered in B-15).

Latest Phase 2 artifact snapshot:
- dataset_curated.json generated from dataset_raw.json using Phase 2 workflow bridge.
- Pending in-scope review queue: 0 samples.
- Applied decisions: 3 (2 validated RP+, 1 moved to diagnostic scope).
- Phase 2 baseline gate report: reports/training_data_gate_report_phase2_start.json (6/8 PASS at phase start).
- Review artifacts:
  - reports/phase2_review_queue.json
  - reports/phase2_review_queue.md
  - reports/phase2_review_decisions.json
  - reports/phase2_review_decisions.template.json

Latest Phase 3/4 artifact snapshot:
- Supervised export summary: reports/phase3_export_summary.json
- Supervised dataset: dataset_supervised.json
- Splits: train.jsonl, validation.jsonl, test.jsonl
- Dataset card: docs/dataset_card.md
- Final gate report: reports/training_data_gate_report.json (8/8 PASS)

Latest B-12 release lock snapshot:
- Release lock script: scripts/build_training_release_package.py
- Frozen package: releases/training_ready_2026.04.01-a
- Release manifest: releases/training_ready_2026.04.01-a/release_manifest.json
- Locked versions: schema_version=2.0.0, dataset_version=2026.04.01-a
- Post-lock gate report: reports/training_data_gate_report.json (8/8 PASS)

Latest B-13 baseline snapshot:
- Baseline script: scripts/run_baseline_training.py
- Baseline report: reports/baseline_model_report.json
- Eval markdown report: docs/eval_report.md
- Error buckets for B-14: reports/baseline_error_buckets.json
- Primary evaluation source: cross_validation (validation/test splits are empty)
- Headline metrics: macro_f1=0.1175, weighted_f1=0.2056, accuracy=0.2000

Latest B-14 iteration snapshots:
- Iteration 1 diversified export summary: reports/b14_eval/phase3_export_summary_target_groups.json
- Iteration 1 diversified split config: group_field=target_paragraph_id, group_count=7
- Iteration 1 split counts: train=13, validation=3, test=4
- Iteration 1 train label coverage: 7/7 labels covered in train
- Iteration 1 gate report: reports/b14_eval/training_data_gate_report.json (8/8 PASS)
- Iteration 1 baseline report: reports/b14_eval/baseline_model_report.json
- Iteration 1 eval markdown report: docs/eval_report_b14_iter1.md
- Iteration 1 error buckets: reports/b14_eval/baseline_error_buckets.json
- Iteration 1 primary evaluation source: test (support=4, min_primary_support=3)
- Iteration 1 headline metrics: macro_f1=0.0000, weighted_f1=0.0000, accuracy=0.0000
- Iteration 2 high-holdout split summary: reports/b14_eval_h6/phase3_export_summary_target_groups.json
- Iteration 2 split counts: train=8, validation=6, test=6
- Iteration 2 gate report: reports/b14_eval_h6/training_data_gate_report.json (8/8 PASS)
- Iteration 2 baseline report: reports/b14_eval_h6/baseline_model_report.json
- Iteration 2 eval markdown report: docs/eval_report_b14_iter2_h6.md
- Iteration 2 error buckets: reports/b14_eval_h6/baseline_error_buckets.json
- Iteration 2 primary evaluation source: test
- Iteration 2 headline metrics: macro_f1=0.0714, weighted_f1=0.0833, accuracy=0.1667
- Iteration 3 RF+ counterexample train set: reports/b14_eval_h6_rfce/train_rf_counterexamples.jsonl
- Iteration 3 baseline report: reports/b14_eval_h6_rfce/baseline_model_report.json
- Iteration 3 eval markdown report: docs/eval_report_b14_iter3_h6_rfce.md
- Iteration 3 error buckets: reports/b14_eval_h6_rfce/baseline_error_buckets.json
- Iteration 3 primary evaluation source: test
- Iteration 3 headline metrics: macro_f1=0.0000, weighted_f1=0.0000, accuracy=0.0000
- Iteration 4 real-pair (v06-04) merged summary: reports/new_pair_v0604_eval/phase3_export_summary_target_groups.json
- Iteration 4 gate report: reports/new_pair_v0604_eval/training_data_gate_report.json (8/8 PASS)
- Iteration 4 baseline report: reports/new_pair_v0604_eval/baseline_model_report.json
- Iteration 4 eval markdown report: docs/eval_report_new_pair_v0604.md
- Iteration 4 split counts: train=12, validation=9, test=8
- Iteration 4 headline metrics: macro_f1=0.0000, weighted_f1=0.0000, accuracy=0.0000
- Iteration 5 real-pair (v06-04a) with alignment-table grounding: reports/new_pair_v0604a_eval/phase3_export_summary_target_groups.json
- Iteration 5 gate report: reports/new_pair_v0604a_eval/training_data_gate_report.json (8/8 PASS)
- Iteration 5 baseline report: reports/new_pair_v0604a_eval/baseline_model_report.json
- Iteration 5 eval markdown report: docs/eval_report_new_pair_v0604a.md
- Iteration 5 split counts: train=24, validation=8, test=10
- Iteration 5 train label coverage: 9/9 labels covered in train
- Iteration 5 headline metrics: macro_f1=0.0000, weighted_f1=0.0000, accuracy=0.0000
- Iteration 6 model sweep report: reports/new_pair_v0604a_eval/model_sweep_report.json
- Iteration 6 sweep eval markdown report: docs/eval_report_new_pair_v0604a_sweep.md
- Iteration 6 reproducibility eval markdown report: docs/eval_report_new_pair_v0604a_sweep_repro.md
- Iteration 6 best model: tfidf_linsvc_balanced_char35
- Iteration 6 best headline metrics on test: macro_f1=0.1667, weighted_f1=0.2000, accuracy=0.2000
- Iteration 6 reproducibility check report: reports/new_pair_v0604a_eval/model_sweep_repro_check.json
- Iteration 6 reproducibility result: same_top_model=true, exact_metric_match=true,
  promotion_confirmed=true (delta metrics all 0.0).
- Working decision: keep Iteration 2 as current B-14 reference and treat Iteration 3 as a negative-control curation result.
- Working decision extension: v06-04a confirms ingestion/alignment/gate integrity; next bottleneck is model discrimination quality.
- Working decision extension 2: promote Iteration 6 sweep best model as the next B-14 candidate (reproducibility checks closed).

Latest B-15 schema-bridge snapshot:
- validator_app.data_loader now supports dual-schema loading for legacy parser rows and canonical v2 rows.
- save flow now preserves canonical v2 keys/metadata and updates edited fields without dropping unknown fields.
- Added canonical-v2 coverage tests in tests/test_validator_data.py (load + round-trip preserve).
- CI now includes a second validator headless smoke run on releases/training_ready_2026.04.01-a/dataset_curated.json.

Latest B-16 handoff snapshot:
- New handoff checklist: docs/external_handoff_checklist.md
- New release note template: docs/external_handoff_release_note_template.md
- New automated handoff validator: scripts/validate_handoff_package.py
- CI now runs handoff package validation in .github/workflows/main.yml.
- Validation contract now enforces required artifacts, manifest checksum/count consistency,
  schema+version consistency, supervised label scope, dataset card completeness, and
  gate-pass status for each external delivery package.

Latest B-17 UX hardening snapshot:
- Added side-by-side source/target context panel in VAEST review flow.
- Added excerpt highlighting and auto-focus anchor for mapped trecho_fonte/trecho_alvo.
- Added rendering helper: validator_app/context_utils.py.
- Added regression tests for context highlight rendering: tests/test_context_utils.py.
- Updated validator app docs with context panel behavior: validator_app/README.md.
- Added persistent local project state in data/metadata.json with associated
  data/tab_est.md, data/source_text.md, and data/target_text.md.
- Added controlled TAG change action in the detail panel with audit-history
  logging of tag transitions.
- Added human-readable export actions for reviewed datasets
  (Markdown/TXT report output).
- Added tests for project-state persistence and export rendering
  (tests/test_project_store.py, tests/test_export_utils.py).

Latest full gate metrics (Phase 4):
- source_grounding_coverage: 1.000 (20/20) PASS
- confident_or_validated_coverage: 1.000 (20/20) PASS
- out_of_scope_labels: 0 PASS
- parse_coverage: 1.067 (32/30) PASS
- duplicate_supervised_keys: 0 PASS
- critical_fields_non_empty: 0/20 missing PASS
- split_leakage: 0 PASS
- dataset_card_completeness: PASS

Latest interim gate metrics (Phase 1 report):
- source_grounding_coverage: 1.000 (21/21) PASS
- confident_or_validated_coverage: 0.952 (20/21) PASS
- parse_coverage: 1.067 (32/30) PASS
- critical_fields_non_empty: 0/21 missing PASS
- Remaining FAILs are Phase 3+ artifacts: split files and dataset card.

Priority legend:
- P0: blocks all downstream work
- P1: high impact, near-term
- P2: important, after P0/P1

## 2. Kanban Table

| ID | Work Item | Phase | Priority | Owner | Estimate | Depends On | Gate/Output | Status |
|---|---|---|---|---|---|---|---|---|
| B-00 | Freeze scope and label policy | 0 | P0 | Owner + Engineer | 0.5d | None | Scope approved | Done |
| B-01 | Regenerate dataset with source alignment | 1 | P0 | Engineer | 0.5-1d | B-00 | Source fields populated | Done |
| B-02 | Fix composite/bodyless parsing coverage | 1 | P0 | Engineer | 0.5-1d | B-00 | Parse coverage >= 98% | Done |
| B-03 | Normalize target spans and clean artifacts | 1 | P1 | Engineer | 0.5d | B-00 | Critical span fields clean | Done |
| B-04 | Run gate baseline after Phase 1 | 1 | P0 | Engineer | 0.25d | B-01,B-02,B-03 | Interim gate report | Done |
| B-05 | Human review of uncertain in-scope rows | 2 | P0 | Analyst | 2-4d | B-04 | Confident-or-validated >= 90% | Done |
| B-06 | Export reviewed dataset_curated.json | 2 | P0 | Analyst + Engineer | 0.25d | B-05 | Curated dataset | Done |
| B-07 | Filter supervised labels to in-scope only | 3 | P0 | Engineer | 0.25d | B-06 | OM+/PRO+ removed from supervised export | Done |
| B-08 | Deduplicate supervised keys | 3 | P1 | Engineer | 0.25d | B-06 | Duplicate key count == 0 | Done |
| B-09 | Create group-safe train/val/test splits | 3 | P0 | Engineer | 0.25d | B-07,B-08 | Zero split leakage | Done |
| B-10 | Produce dataset_card.md | 3 | P1 | Engineer + Analyst | 0.25d | B-06 | Version/provenance/limitations documented | Done |
| B-11 | Run full gate and fix failures | 4 | P0 | Engineer | 0.5d | B-09,B-10 | All gates PASS | Done |
| B-12 | Version lock release package | 4 | P0 | Owner + Engineer | 0.25d | B-11 | Training-ready package frozen | Done |
| B-13 | Baseline model training run | 5 | P1 | Engineer | 0.5-1d | B-12 | Initial model metrics | Done |
| B-14 | Error analysis and next-cycle backlog | 5 | P1 | Engineer + Analyst | 0.5-1d | B-13 | eval_report_b14_iter2_h6.md + eval_report_b14_iter3_h6_rfce.md + eval_report_new_pair_v0604.md + eval_report_new_pair_v0604a.md + eval_report_new_pair_v0604a_sweep.md + prioritized backlog | In progress |
| B-15 | VAEST schema bridge for canonical v2 | 6 | P0 | Engineer | 1-2d | B-14 | Validator loads and saves v2 records without field loss | Done |
| B-16 | External handoff checklist and template | 6 | P0 | Owner + Engineer | 0.5d | B-12 | Repeatable delivery package for university team | Done |
| B-17 | VAEST linguist UX hardening track | 7 | P1 | Engineer + Analyst | 3-5d | B-15 | Context-first review flow and reduced reviewer friction | Done |

## 3. Phase Gates

- Gate G0 (after Phase 0):
  - Label scope fixed and approved.

- Gate G1 (after Phase 1):
  - Source grounding coverage >= 95%.
  - Parse coverage >= 98%.
  - Critical supervised fields non-empty.

- Gate G2 (after Phase 2):
  - Confident-or-validated coverage >= 90% for in-scope rows.

- Gate G3 (after Phase 3):
  - In-scope-only supervised exports.
  - Duplicate supervised keys == 0.
  - Split leakage == 0.
  - dataset_card.md present.

- Gate G4 (after Phase 4):
  - scripts/validate_training_dataset.py returns PASS for all gates.

- Gate G5 (after Phase 5):
  - Baseline metrics and confusion analysis documented.

## 4. Suggested Day-by-Day Sequence

Day 1:
- B-00, B-01, B-02 (parallel), start B-03.

Day 2:
- Finish B-03, run B-04, begin B-05.

Day 3-4:
- Continue and finish B-05, then B-06.

Day 5:
- B-07, B-08, B-09, B-10.

Day 6:
- B-11, B-12.

Day 7:
- B-13, B-14.

## 5. Weekly Reporting Snapshot

Track these KPIs daily:
1. Source grounding coverage (in-scope)
2. Confident-or-validated coverage (in-scope)
3. Parse coverage ratio
4. Out-of-scope label count in supervised exports
5. Duplicate supervised key count
6. Split leakage count
7. Gate pass count / total gates

## 6. Blocking Rules

1. Do not start B-05 before interim gate baseline (B-04).
2. Do not generate training splits before review export (B-06).
3. Do not train baseline model before full gate pass (B-11).

## 7. Command Anchor

Use this command for final gate run:
- python -m scripts.validate_training_dataset --dataset dataset_curated.json --target-markdown patriotismo_tt.md --dataset-card docs/dataset_card.md --train-jsonl train.jsonl --validation-jsonl validation.jsonl --test-jsonl test.jsonl --report-json reports/training_data_gate_report.json

Use this command for B-12 release lock package:
- python -m scripts.build_training_release_package --dataset dataset_curated.json --supervised-dataset dataset_supervised.json --train-jsonl train.jsonl --validation-jsonl validation.jsonl --test-jsonl test.jsonl --dataset-card docs/dataset_card.md --gate-report reports/training_data_gate_report.json --phase3-report reports/phase3_export_summary.json --output-root releases --dataset-version 2026.04.01-a --schema-version 2.0.0 --release-id 2026.04.01-a

Use this command for B-13 baseline run from release package:
- python -m scripts.run_baseline_training --release-dir releases/training_ready_2026.04.01-a --report-json reports/baseline_model_report.json --eval-report-md docs/eval_report.md --errors-json reports/baseline_error_buckets.json

Use this command for B-14 diversified split export:
- python -m scripts.build_supervised_exports --dataset releases/training_ready_2026.04.01-a/dataset_curated.json --output-dataset reports/b14_eval/dataset_supervised_target_groups.json --train-jsonl reports/b14_eval/train.jsonl --validation-jsonl reports/b14_eval/validation.jsonl --test-jsonl reports/b14_eval/test.jsonl --report-json reports/b14_eval/phase3_export_summary_target_groups.json --group-field target_paragraph_id --min-validation-rows 3 --min-test-rows 3

Use this command for B-14 baseline rerun on diversified splits:
- python -m scripts.run_baseline_training --train-jsonl reports/b14_eval/train.jsonl --validation-jsonl reports/b14_eval/validation.jsonl --test-jsonl reports/b14_eval/test.jsonl --release-manifest releases/training_ready_2026.04.01-a/release_manifest.json --report-json reports/b14_eval/baseline_model_report.json --eval-report-md docs/eval_report_b14_iter1.md --errors-json reports/b14_eval/baseline_error_buckets.json --min-primary-support 3

Use this command for B-14 high-holdout split export:
- python -m scripts.build_supervised_exports --dataset releases/training_ready_2026.04.01-a/dataset_curated.json --output-dataset reports/b14_eval_h6/dataset_supervised_target_groups.json --train-jsonl reports/b14_eval_h6/train.jsonl --validation-jsonl reports/b14_eval_h6/validation.jsonl --test-jsonl reports/b14_eval_h6/test.jsonl --report-json reports/b14_eval_h6/phase3_export_summary_target_groups.json --group-field target_paragraph_id --min-validation-rows 6 --min-test-rows 6

Use this command for B-14 high-holdout gate validation:
- python -m scripts.validate_training_dataset --dataset releases/training_ready_2026.04.01-a/dataset_curated.json --target-markdown patriotismo_tt.md --dataset-card docs/dataset_card.md --train-jsonl reports/b14_eval_h6/train.jsonl --validation-jsonl reports/b14_eval_h6/validation.jsonl --test-jsonl reports/b14_eval_h6/test.jsonl --report-json reports/b14_eval_h6/training_data_gate_report.json

Use this command for B-14 baseline rerun on high-holdout splits:
- python -m scripts.run_baseline_training --train-jsonl reports/b14_eval_h6/train.jsonl --validation-jsonl reports/b14_eval_h6/validation.jsonl --test-jsonl reports/b14_eval_h6/test.jsonl --release-manifest releases/training_ready_2026.04.01-a/release_manifest.json --report-json reports/b14_eval_h6/baseline_model_report.json --eval-report-md docs/eval_report_b14_iter2_h6.md --errors-json reports/b14_eval_h6/baseline_error_buckets.json --min-primary-support 3

Use this command for RF+ counterexample curation on high-holdout train:
- python -m scripts.build_rf_counterexample_train --train-jsonl reports/b14_eval_h6/train.jsonl --error-buckets-json reports/b14_eval_h6/baseline_error_buckets.json --output-jsonl reports/b14_eval_h6_rfce/train_rf_counterexamples.jsonl --predicted-label RF+ --max-per-label 2

Use this command for B-14 rerun with RF+ counterexample train:
- python -m scripts.run_baseline_training --train-jsonl reports/b14_eval_h6_rfce/train_rf_counterexamples.jsonl --validation-jsonl reports/b14_eval_h6/validation.jsonl --test-jsonl reports/b14_eval_h6/test.jsonl --release-manifest releases/training_ready_2026.04.01-a/release_manifest.json --report-json reports/b14_eval_h6_rfce/baseline_model_report.json --eval-report-md docs/eval_report_b14_iter3_h6_rfce.md --errors-json reports/b14_eval_h6_rfce/baseline_error_buckets.json --min-primary-support 3

Use this command for B-16 external handoff package validation:
- python -m scripts.validate_handoff_package --release-dir releases/training_ready_2026.04.01-a --report-json releases/training_ready_2026.04.01-a/reports/handoff_validation_report.json

