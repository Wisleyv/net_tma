# Baseline Evaluation Report

## Run Context

- generated_at: 2026-04-06T14:36:53+00:00
- model: tfidf_logreg_balanced
- train_rows: 12
- validation_rows: 9
- test_rows: 8
- release_id: 2026.04.01-a
- dataset_version: 2026.04.01-a
- schema_version: 2.0.0

## Headline Metrics

- primary_source: test
- macro_f1: 0.0000
- weighted_f1: 0.0000
- accuracy: 0.0000

## Split Metrics

| split | available | macro_f1 | weighted_f1 | accuracy |
|---|---|---:|---:|---:|
| train | yes | 1.0000 | 1.0000 | 1.0000 |
| validation | yes | 0.0000 | 0.0000 | 0.0000 |
| test | yes | 0.0000 | 0.0000 | 0.0000 |

## Cross Validation

- strategy: kfold_fallback
- n_splits: 5
- macro_f1: 0.2296
- weighted_f1: 0.4018
- accuracy: 0.5000

## Per-Tag Metrics

| tag | precision | recall | f1 | support |
|---|---:|---:|---:|---:|
| DL+ | 0.0000 | 0.0000 | 0.0000 | 0 |
| EXP+ | 0.0000 | 0.0000 | 0.0000 | 0 |
| IN+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| MOD+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| RD+ | 0.0000 | 0.0000 | 0.0000 | 3 |
| RF+ | 0.0000 | 0.0000 | 0.0000 | 2 |
| RP+ | 0.0000 | 0.0000 | 0.0000 | 0 |
| SL+ | 0.0000 | 0.0000 | 0.0000 | 1 |

## Notes

- Validation split contains labels unseen in train: RD+.
- Test split contains labels unseen in train: RD+.
