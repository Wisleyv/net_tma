# Baseline Evaluation Report

## Run Context

- generated_at: 2026-04-06T02:26:23+00:00
- model: tfidf_logreg_balanced
- train_rows: 13
- validation_rows: 3
- test_rows: 4
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
| train | yes | 0.7238 | 0.5436 | 0.6154 |
| validation | yes | 0.0000 | 0.0000 | 0.0000 |
| test | yes | 0.0000 | 0.0000 | 0.0000 |

## Cross Validation

- strategy: kfold_fallback
- n_splits: 5
- macro_f1: 0.0952
- weighted_f1: 0.2051
- accuracy: 0.2308

## Per-Tag Metrics

| tag | precision | recall | f1 | support |
|---|---:|---:|---:|---:|
| DL+ | 0.0000 | 0.0000 | 0.0000 | 0 |
| IN+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| MOD+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| RD+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| RF+ | 0.0000 | 0.0000 | 0.0000 | 0 |
| RP+ | 0.0000 | 0.0000 | 0.0000 | 0 |
| SL+ | 0.0000 | 0.0000 | 0.0000 | 1 |
