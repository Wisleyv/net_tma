# B-14 Comparative Evaluation Report

Date: 2026-04-06
Comparison scope: iter2_h6 baseline vs iter3_h6_rfce on identical validation/test splits

## 1) Run Inputs

Common holdout inputs:
- validation_jsonl: reports/b14_eval_h6/validation.jsonl
- test_jsonl: reports/b14_eval_h6/test.jsonl
- release_manifest: releases/training_ready_2026.04.01-a/release_manifest.json

Train inputs:
- iter2_h6: reports/b14_eval_h6/train.jsonl
- iter3_h6_rfce: reports/b14_eval_h6_rfce/train_rf_counterexamples.jsonl

## 2) Headline Comparison

| metric | iter2_h6 | iter3_h6_rfce | delta (iter3 - iter2) |
|---|---:|---:|---:|
| train rows | 8 | 11 | +3 |
| test macro_f1 | 0.0714 | 0.0000 | -0.0714 |
| test weighted_f1 | 0.0833 | 0.0000 | -0.0833 |
| test accuracy | 0.1667 | 0.0000 | -0.1667 |
| validation macro_f1 | 0.0000 | 0.0000 | 0.0000 |
| cross-validation macro_f1 | 0.0000 | 0.2143 | +0.2143 |

Interpretation:
- The RF+ counterexample augmentation improved cross-validation but degraded holdout metrics to zero.
- Holdout metrics remain the primary B-14 acceptance signal for this iteration.

## 3) Confusion Bucket Delta

Persisted errors (iter2 and iter3):
- SL+ -> RF+
- RD+ -> RF+
- IN+ -> RF+
- RF+ -> MOD+
- RP+ -> MOD+

New error introduced in iter3:
- MOD+ -> RF+

Net effect:
- No removal of existing top confusion buckets.
- One additional high-impact confusion bucket appears after augmentation.

## 4) Decision

- Accepted reference run: iter2_h6 (reports/b14_eval_h6)
- Rejected candidate: iter3_h6_rfce for promotion

Reason:
- iter3 does not satisfy the minimum requirement of matching or improving iter2 holdout metrics.

## 5) Next Iteration Constraints

1. Any RF+ counterexample retry must limit synthetic additions to <= 1 row per target label.
2. Prioritize real, reviewer-curated counterexamples from new split groups over span-focused variants.
3. Promote a new run only if test macro_f1 >= 0.0714 and test accuracy >= 0.1667 under the same 6/6 holdout policy.
