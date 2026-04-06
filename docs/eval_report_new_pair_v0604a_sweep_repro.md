# Model Sweep Reproducibility Report (v06-04a)

- generated_at: 2026-04-06T19:31:37+00:00
- reference_report: reports/new_pair_v0604a_eval/model_sweep_report.json
- repro_report: reports/new_pair_v0604a_eval/model_sweep_repro_check.json
- split_counts: train=24, validation=8, test=10

## Reproducibility Check Outcome

- recorded_top_model: tfidf_linsvc_balanced_char35
- reproduced_top_model: tfidf_linsvc_balanced_char35
- same_top_model: true
- exact_metric_match: true
- delta_macro_f1: 0.0
- delta_weighted_f1: 0.0
- delta_accuracy: 0.0
- promotion_confirmed: true

## Promotion Decision

The Iteration 6 sweep winner remains reproducible and is confirmed for promotion in B-14 tracking:

- candidate_model: tfidf_linsvc_balanced_char35
- confirmed_test_metrics: macro_f1=0.1667, weighted_f1=0.2000, accuracy=0.2000
