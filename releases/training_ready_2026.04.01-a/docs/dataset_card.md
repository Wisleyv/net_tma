# Dataset Card

## Version

- schema_version: 2.0.0
- dataset_version: 2026.04.01-a
- generated_at: 2026-04-02

## Provenance

This dataset was produced from the NET_TMA pipeline using:

1. Parser generation from patriotismo_st.md and patriotismo_tt.md.
2. Phase 2 curation workflow with explicit review decisions.
3. Phase 3 supervised export filtering and split generation.

Primary artifacts:
- dataset_curated.json
- dataset_supervised.json
- train.jsonl
- validation.jsonl
- test.jsonl

## Scope

In-scope supervised tags:
- RF+
- SL+
- IN+
- RP+
- RD+
- MOD+
- DL+
- EXP+
- MT+

Diagnostic-only tags (excluded from supervised exports):
- OM+
- PRO+

## Known Limitations

- Current corpus is based on a single source-target document pair.
- Split group diversity is limited (group_count=1 in this iteration).
- Validation and test splits are currently empty due the single-group constraint.
- Additional reviewer passes and corpus expansion are recommended before baseline modeling conclusions.

## Quality Notes

- Phase 1 quality gates for grounding, confidence, parse coverage, and critical fields are passing.
- Supervised export removed diagnostic labels and preserved split_group_id for leakage checks.
