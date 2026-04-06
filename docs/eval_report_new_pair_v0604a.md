# Baseline Evaluation Report

## Run Context

- generated_at: 2026-04-06T15:24:17+00:00
- model: tfidf_logreg_balanced
- train_rows: 24
- validation_rows: 8
- test_rows: 10
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
| train | yes | 0.5387 | 0.4846 | 0.5417 |
| validation | yes | 0.0494 | 0.1111 | 0.2500 |
| test | yes | 0.0000 | 0.0000 | 0.0000 |

## Cross Validation

- strategy: kfold_fallback
- n_splits: 5
- macro_f1: 0.0808
- weighted_f1: 0.1667
- accuracy: 0.1667

## Per-Tag Metrics

| tag | precision | recall | f1 | support |
|---|---:|---:|---:|---:|
| DL+ | 0.0000 | 0.0000 | 0.0000 | 0 |
| EXP+ | 0.0000 | 0.0000 | 0.0000 | 2 |
| IN+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| MOD+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| MT+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| RD+ | 0.0000 | 0.0000 | 0.0000 | 2 |
| RF+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| RP+ | 0.0000 | 0.0000 | 0.0000 | 0 |
| SL+ | 0.0000 | 0.0000 | 0.0000 | 2 |
