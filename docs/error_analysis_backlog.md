# Error Analysis Backlog (B-14)

Date: 2026-04-06
Phase: B-14 in progress
Owner: Engineer + Analyst

## 1) Inputs

- reports/b14_eval_h6/baseline_model_report.json
- reports/b14_eval_h6/baseline_error_buckets.json
- docs/eval_report_b14_iter2_h6.md
- reports/b14_eval_h6_rfce/train_rf_counterexamples.jsonl
- reports/b14_eval_h6_rfce/baseline_model_report.json
- reports/b14_eval_h6_rfce/baseline_error_buckets.json
- docs/eval_report_b14_iter3_h6_rfce.md

## 2) Comparative Snapshot (Same Holdout Splits)

| run | train/validation/test | primary_source | test macro_f1 | test weighted_f1 | test accuracy | note |
|---|---|---|---:|---:|---:|---|
| iter2_h6 baseline | 8/6/6 | test | 0.0714 | 0.0833 | 0.1667 | one correct test prediction (MOD+) |
| iter3_h6_rfce | 11/6/6 | test | 0.0000 | 0.0000 | 0.0000 | RF+ counterexample augmentation regressed holdout |

Key observation:
- Holdout confusion remained dominated by RF+ overprediction, and iter3 added a new error bucket MOD+ -> RF+ that was not present in iter2.

## 3) Highest-Impact Confusion Buckets

1. Persistent: SL+ -> RF+ (count=1)
2. Persistent: RD+ -> RF+ (count=1)
3. Persistent: IN+ -> RF+ (count=1)
4. Persistent: RF+ -> MOD+ (count=1)
5. Persistent: RP+ -> MOD+ (count=1)
6. Regression in iter3: MOD+ -> RF+ (count=1)

## 4) Prioritized Backlog

1. P0 Freeze iter2_h6 as B-14 reference baseline
- Objective: preserve the best currently observed holdout result under the 6/6 support protocol.
- Action: keep reports/b14_eval_h6 as the comparison anchor for future experiments.
- Success check: no future experiment is accepted unless it beats iter2_h6 test accuracy 0.1667 and macro_f1 0.0714.

2. P0 Replace naive RF+ counterexample augmentation policy
- Objective: prevent overfitting from span-focused synthetic rows.
- Action: only accept counterexamples that come from new source-target groups or reviewer-authored contrasts; cap synthetic additions to <= 1 row per target label for initial retries.
- Success check: no new MOD+ -> RF+ confusion while maintaining or improving iter2_h6 headline metrics.

3. P1 Expand holdout diversity with new document pairs
- Objective: increase robustness beyond split-policy gains on a single document pair.
- Action: ingest additional source-target pairs and rebuild high-holdout exports with min_validation_rows=6 and min_test_rows=6.
- Success check: validation and test each contain >= 6 rows and >= 3 distinct labels from different split groups.

4. P1 RF+ vs SL+ annotation guidance pass
- Objective: reduce ambiguity between lexical simplification and reformulation.
- Action: attach reviewer guidance notes for SL+/RF+ boundary cases in curation workflow.
- Success check: SL+ and RF+ both achieve non-zero recall on holdout or cross-validation.

5. P2 Feature ablation baseline iteration
- Objective: check whether source span fields amplify confusions.
- Action: rerun baseline with and without source_span_text/target_span_text under identical split protocol.
- Success check: select the variant with higher test macro_f1 and stable confusion buckets.

6. P2 Rare-label support expansion (DL+, IN+, MOD+, RP+)
- Objective: improve minority-class signal stability.
- Action: collect at least 5 additional validated samples per rare label.
- Success check: non-zero recall for each rare class in holdout or cross-validation.

## 5) Decisions Logged

1. Iteration decision: keep iter2_h6 as the active B-14 baseline reference.
2. Iteration decision: do not promote iter3_h6_rfce metrics; treat it as a negative-control experiment.
3. Process decision: future RF+ counterexample attempts must enforce stricter curation constraints before rerun.

## 6) Exit Criteria for B-14

1. Error buckets are reviewed and accepted by analyst.
2. Next-cycle data collection tasks are assigned by label bucket.
3. Holdout support and label-diversity targets are met on expanded corpus.
4. At least one rerun improves or matches iter2_h6 without adding new confusion regressions.
