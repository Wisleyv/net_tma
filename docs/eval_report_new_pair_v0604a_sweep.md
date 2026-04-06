# Model Sweep Report (v06-04a Split Pack)

- Baseline model: tfidf_logreg_balanced_word12
- Split counts: train=24, validation=8, test=10
- Labels: DL+, EXP+, IN+, MOD+, MT+, RD+, RF+, RP+, SL+

| rank | model | test macro_f1 | test weighted_f1 | test accuracy | delta macro_f1 vs baseline | delta acc vs baseline |
|---|---|---:|---:|---:|---:|---:|
| 1 | tfidf_linsvc_balanced_char35 | 0.1667 | 0.2000 | 0.2000 | +0.1667 | +0.2000 |
| 2 | tfidf_sgd_logloss_balanced_word12 | 0.1111 | 0.1000 | 0.1000 | +0.1111 | +0.1000 |
| 3 | tfidf_nb_word12 | 0.0202 | 0.0182 | 0.1000 | +0.0202 | +0.1000 |
| 4 | tfidf_logreg_balanced_word12 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| 5 | tfidf_linsvc_balanced_word12 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| 6 | tfidf_linsvc_balanced_word13 | 0.0000 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |

## Best Candidate

- Model: tfidf_linsvc_balanced_char35
- Test macro_f1: 0.1667
- Test weighted_f1: 0.2000
- Test accuracy: 0.2000

## Per-Tag Test F1 Delta (Best vs Baseline)

| tag | delta f1 |
|---|---:|
| DL+ | +0.0000 |
| EXP+ | +0.5000 |
| IN+ | +0.0000 |
| MOD+ | +0.0000 |
| MT+ | +1.0000 |
| RD+ | +0.0000 |
| RF+ | +0.0000 |
| RP+ | +0.0000 |
| SL+ | +0.0000 |
