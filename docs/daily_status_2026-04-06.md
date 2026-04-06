# Daily Status

Date: 2026-04-06
Phase: B-14 iteration in progress + B-16 handoff standard completed
Owner: Engineer

Historical note:
- This is a date-scoped daily log entry.
- For current project state, consult docs/execution_board.md and ROADMAP.md.

## 1) Summary

- Overall status: Cautionary but improved progress.
- Biggest win today: controlled model sweep recovered holdout performance on v06-04a and reached the current iter2_h6 acceptance bar.
- Biggest blocker today: label confusion remains concentrated in RF+/SL+/RD+ regions.

## 2) Board Delta

- Stayed In progress:
  - B-14 Error analysis and next-cycle backlog
- Newly completed outside B-14:
  - B-16 External handoff checklist and template standard
- Newly completed within B-14:
  - High-holdout split/gate/baseline cycle (iter2_h6)
  - RF+ counterexample curation tool + tests
  - Counterexample rerun on identical holdouts (iter3_h6_rfce)
  - Real-pair integration run (v06-04) with dedicated export/gate/baseline pack
  - Real-pair integration run (v06-04a) using alignment-table grounding verification
  - Controlled model sweep on frozen v06-04a split pack
- Newly blocked:
  - none

## 3) Comparative Metrics Snapshot

| run | train/validation/test | primary_source | test macro_f1 | test weighted_f1 | test accuracy |
|---|---|---|---:|---:|---:|
| iter2_h6 baseline | 8/6/6 | test | 0.0714 | 0.0833 | 0.1667 |
| iter3_h6_rfce | 11/6/6 | test | 0.0000 | 0.0000 | 0.0000 |
| v06-04 integrated | 12/9/8 | test | 0.0000 | 0.0000 | 0.0000 |
| v06-04a aligned | 24/8/10 | test | 0.0000 | 0.0000 | 0.0000 |
| v06-04a sweep best (char35 SVM) | 24/8/10 | test | 0.1667 | 0.2000 | 0.2000 |

Additional signal:
- v06-04a train label coverage reached 9/9 (no missing labels in train) and gate checks remained 8/8 PASS.
- v06-04a in-scope source grounding reached 42/42 with alignment-table-assisted mapping.
- Character-level TF-IDF + linear SVM improved test macro_f1 by +0.1667 versus baseline on the same split pack.

## 4) Artifacts Updated

- New code:
  - .github/workflows/main.yml
  - scripts/build_rf_counterexample_train.py
  - scripts/validate_handoff_package.py
  - tests/test_build_rf_counterexample_train.py
- New handoff docs:
  - docs/external_handoff_checklist.md
  - docs/external_handoff_release_note_template.md
- New reports:
  - reports/b14_eval_h6/phase3_export_summary_target_groups.json
  - reports/b14_eval_h6/training_data_gate_report.json
  - reports/b14_eval_h6/baseline_model_report.json
  - reports/b14_eval_h6/baseline_error_buckets.json
  - docs/eval_report_b14_iter2_h6.md
  - reports/b14_eval_h6_rfce/train_rf_counterexamples.jsonl
  - reports/b14_eval_h6_rfce/baseline_model_report.json
  - reports/b14_eval_h6_rfce/baseline_error_buckets.json
  - docs/eval_report_b14_iter3_h6_rfce.md
  - reports/new_pair_v0604/dataset_raw_pair.json
  - reports/new_pair_v0604/dataset_curated_pair.json
  - reports/new_pair_v0604_eval/phase3_export_summary_target_groups.json
  - reports/new_pair_v0604_eval/training_data_gate_report.json
  - reports/new_pair_v0604_eval/baseline_model_report.json
  - docs/eval_report_new_pair_v0604.md
  - reports/new_pair_v0604a/dataset_raw_pair.json
  - reports/new_pair_v0604a/dataset_curated_pair.json
  - reports/new_pair_v0604a_eval/phase3_export_summary_target_groups.json
  - reports/new_pair_v0604a_eval/training_data_gate_report.json
  - reports/new_pair_v0604a_eval/baseline_model_report.json
  - docs/eval_report_new_pair_v0604a.md
  - reports/new_pair_v0604a_eval/model_sweep_report.json
  - docs/eval_report_new_pair_v0604a_sweep.md

## 5) Risks and Mitigations

- Active risk: gains are currently demonstrated on a single split pack and can be unstable in low-support labels.
- Mitigation in place: controlled sweep was run on fixed artifacts with explicit baseline deltas and per-tag inspection.
- Escalation needed: confirm the selected model family across additional split seeds and then run confusion-targeted curation.

## 6) Plan for Next Day

1. Promote char-level TF-IDF + linear SVM as the B-14 candidate model and run a reproducibility check across alternate split seeds.
2. Build an error-focused curation batch from the latest confusion buckets (RF+ vs SL+/RD+/EXP+, MT+ drift).
3. Add one additional real aligned pair with explicit RF+/SL+/RD+ boundary examples and rerun the same sweep protocol.

## 7) Decisions Logged

- Decision: accept v06-04a model sweep as a B-14 milestone candidate.
- Rationale: best sweep model (tfidf_linsvc_balanced_char35) improved holdout to macro_f1=0.1667 and accuracy=0.2000 on the same split pack.
- Impact: next cycle should validate this model choice for robustness and use it as the reference while curating confusion-heavy tags.
