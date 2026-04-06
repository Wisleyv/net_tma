# Baseline Evaluation Report

## Run Context

- generated_at: 2026-04-05T15:45:51+00:00
- model: tfidf_logreg_balanced
- train_rows: 20
- validation_rows: 0
- test_rows: 0
- release_id: 2026.04.01-a
- dataset_version: 2026.04.01-a
- schema_version: 2.0.0

## Headline Metrics

- primary_source: cross_validation
- macro_f1: 0.1175
- weighted_f1: 0.2056
- accuracy: 0.2000

## Split Metrics

| split | available | macro_f1 | weighted_f1 | accuracy |
|---|---|---:|---:|---:|
| train | yes | 0.6143 | 0.6100 | 0.6000 |
| validation | no | n/a | n/a | n/a |
| test | no | n/a | n/a | n/a |

## Cross Validation

- strategy: kfold_fallback
- n_splits: 5
- macro_f1: 0.1175
- weighted_f1: 0.2056
- accuracy: 0.2000

## Per-Tag Metrics

| tag | precision | recall | f1 | support |
|---|---:|---:|---:|---:|
| DL+ | 0.0000 | 0.0000 | 0.0000 | 1 |
| IN+ | 0.0000 | 0.0000 | 0.0000 | 2 |
| MOD+ | 0.0000 | 0.0000 | 0.0000 | 2 |
| RD+ | 0.0000 | 0.0000 | 0.0000 | 3 |
| RF+ | 0.2500 | 0.2000 | 0.2222 | 5 |
| RP+ | 0.0000 | 0.0000 | 0.0000 | 2 |
| SL+ | 0.6000 | 0.6000 | 0.6000 | 5 |

## Notes

- Validation split is empty; model selection confidence is limited.
- Test split is empty; generalization estimate is unavailable.
