# Baseline Evaluation Report

## Run Context

- generated_at: 2026-04-06T11:13:55+00:00
- model: tfidf_logreg_balanced
- train_rows: 11
- validation_rows: 6
- test_rows: 6
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
| train | yes | 0.8286 | 0.8121 | 0.8182 |
| validation | yes | 0.0000 | 0.0000 | 0.0000 |
| test | yes | 0.0000 | 0.0000 | 0.0000 |

## Cross Validation

- strategy: kfold_fallback
- n_splits: 5
- macro_f1: 0.2143
- weighted_f1: 0.2727
- accuracy: 0.2727

## Per-Tag Metrics

| tag | precision | recall | f1 | support |
|---|---:|---:|---:|---:|
| DL+ | 0.0000 | 0.0000 | 0.0000 | 0 |
| IN+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| MOD+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| RD+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| RF+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| RP+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| SL+ | 0.0000 | 0.0000 | 0.0000 | 1 |
