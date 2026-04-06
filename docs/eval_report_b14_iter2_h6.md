# Baseline Evaluation Report

## Run Context

- generated_at: 2026-04-06T11:11:33+00:00
- model: tfidf_logreg_balanced
- train_rows: 8
- validation_rows: 6
- test_rows: 6
- release_id: 2026.04.01-a
- dataset_version: 2026.04.01-a
- schema_version: 2.0.0

## Headline Metrics

- primary_source: test
- macro_f1: 0.0714
- weighted_f1: 0.0833
- accuracy: 0.1667

## Split Metrics

| split | available | macro_f1 | weighted_f1 | accuracy |
|---|---|---:|---:|---:|
| train | yes | 1.0000 | 1.0000 | 1.0000 |
| validation | yes | 0.0000 | 0.0000 | 0.0000 |
| test | yes | 0.0714 | 0.0833 | 0.1667 |

## Cross Validation

- strategy: kfold_fallback
- n_splits: 5
- macro_f1: 0.0000
- weighted_f1: 0.0000
- accuracy: 0.0000

## Per-Tag Metrics

| tag | precision | recall | f1 | support |
|---|---:|---:|---:|---:|
| DL+ | 0.0000 | 0.0000 | 0.0000 | 0 |
| IN+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| MOD+ | 0.3333 | 1.0000 | 0.5000 | 1 |
| RD+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| RF+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| RP+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| SL+ | 0.0000 | 0.0000 | 0.0000 | 1 |
