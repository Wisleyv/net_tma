# Training Readiness Plan (Detailed)

Date: 2026-04-01
Status: Execution-ready
Scope: Move from current dataset state to gate-passing, model-training-ready artifacts with maximum impact per effort.

## 1. Objective

Produce a supervised training dataset for simplification-pattern detection that passes all hard quality gates and supports reliable baseline model training.

Primary success condition:
- All gates in scripts/validate_training_dataset.py pass with exit code 0.

## 2. Non-Negotiable Policy

In-scope automatic labels:
- RF+
- SL+
- IN+
- RP+
- RD+
- MOD+
- DL+
- EXP+
- MT+

Diagnostic only (excluded from supervised exports):
- OM+
- PRO+

Rationale:
- OM+ and PRO+ are out of scope for automatic detection according to project guidance.

## 3. Workstreams

- WS1: Parser and extraction quality
- WS2: Source-target grounding
- WS3: Human validation and auditability
- WS4: Dataset curation, splits, and exports
- WS5: Quality gating and release
- WS6: Baseline model evaluation

## 4. Phase Plan

### Phase 0 - Scope Freeze (same day)

Goal:
- Eliminate objective drift before implementation.

Tasks:
1. Freeze supervised label set (in-scope only).
2. Freeze gate thresholds from training_data_spec_v2.md.
3. Freeze artifact contract (dataset_curated.json, train/validation/test JSONL, dataset_card.md, eval_report.md).

Inputs:
- docs/training_data_spec_v2.md
- docs/dataset_training_assessment.md

Outputs:
- Team-wide agreement on scope and acceptance criteria.

Exit criteria:
- Label policy and gate thresholds are approved and documented.

Estimated duration:
- 0.5 day

---

### Phase 1 - Grounding and Parse Recovery (1-2 days)

Goal:
- Recover source grounding and extraction coverage so training signals are valid.

Tasks:
1. Run parser regeneration with source alignment enabled.
2. Improve extraction for composite/bodyless annotation patterns.
3. Normalize target spans (remove annotation artifacts).
4. Rebuild dataset snapshot and immediately run gate report.

Inputs:
- patriotismo_st.md
- patriotismo_tt.md
- parser/alignment.py
- parser/annotations.py
- parser/builder.py

Outputs:
- Regenerated dataset with populated source fields for in-scope rows.
- Improved parse coverage against observed markers.

Exit criteria:
- Source grounding coverage >= 95% (in-scope rows).
- Parse coverage >= 98%.
- Critical span artifact issues reduced to zero for supervised rows.

Estimated duration:
- 1-2 days

Parallelization notes:
- Parser extraction fixes and span normalization can run in parallel with alignment tuning.

---

### Phase 2 - Human Validation Pass (2-4 days)

Goal:
- Convert uncertain rows into confident or human-validated supervisory data.

Tasks:
1. Load curated dataset into validator workflow.
2. Review uncertain in-scope rows and confirm source-target mapping.
3. Set confidence and validation states with reviewer trace.
4. Export reviewed dataset_curated.json.

Inputs:
- validator_app/view.py
- validator_app/models.py
- dataset from Phase 1

Outputs:
- dataset_curated.json with review traceability.

Exit criteria:
- Confident-or-validated coverage >= 90% (in-scope rows).
- Reviewer attribution and notes available where needed.

Estimated duration:
- 2-4 days

Dependency:
- Requires Phase 1 output.

---

### Phase 3 - Supervised Export and Split Safety (0.5-1 day)

Goal:
- Produce clean supervised training artifacts with no leakage.

Tasks:
1. Filter to in-scope automatic labels only.
2. Deduplicate by supervised key:
   - document_id + target_paragraph_id + target_span + tag_code
3. Generate train.jsonl, validation.jsonl, test.jsonl split by split_group_id.
4. Create dataset_card.md with version, provenance, and known limitations.

Inputs:
- dataset_curated.json
- docs/training_data_spec_v2.md

Outputs:
- train.jsonl
- validation.jsonl
- test.jsonl
- dataset_card.md

Exit criteria:
- No split_group_id overlap across splits.
- Out-of-scope labels absent from supervised exports.
- Duplicate supervised keys == 0.

Estimated duration:
- 0.5-1 day

Dependency:
- Requires Phase 2 output.

---

### Phase 4 - Hard Gate Enforcement and Version Lock (0.5 day)

Goal:
- Formally certify dataset readiness.

Tasks:
1. Run quality gate script against curated dataset and split artifacts.
2. Fix failing gates only, rerun until pass.
3. Lock dataset_version and schema_version for training run.

Reference command:
- python -m scripts.validate_training_dataset --dataset dataset_curated.json --target-markdown patriotismo_tt.md --dataset-card docs/dataset_card.md --train-jsonl train.jsonl --validation-jsonl validation.jsonl --test-jsonl test.jsonl --report-json reports/training_data_gate_report.json

Outputs:
- Gate report JSON
- Final pass/fail status
- Version-locked dataset package

Exit criteria:
- All hard gates pass.

Estimated duration:
- 0.5 day

Dependency:
- Requires Phase 3 artifacts.

---

### Phase 5 - Baseline Model Evaluation (1-2 days)

Goal:
- Validate practical training utility before scaling data volume.

Tasks:
1. Train one baseline classifier on gated artifacts.
2. Report macro-F1, per-tag precision/recall/F1, confusion matrix.
3. Produce error buckets and next data-collection targets.

Outputs:
- eval_report.md
- Prioritized error-driven data-improvement backlog

Exit criteria:
- Baseline metrics and confusion analysis documented.
- Next improvement cycle focused on observed error modes.

Estimated duration:
- 1-2 days

Dependency:
- Requires Phase 4 pass.

## 5. Critical Risks and Mitigations

1. Risk: Alignment remains sparse after parser pass.
- Mitigation: Use validator-assisted manual mapping on only unresolved rows.

2. Risk: Composite annotation coverage remains below threshold.
- Mitigation: Add explicit parser handling for multi-tag patterns and bodyless tags, then re-run parse coverage check.

3. Risk: Class imbalance limits useful learning.
- Mitigation: Track per-tag counts and use weighted losses or targeted collection for minority labels.

4. Risk: Split leakage from repeated paragraph structures.
- Mitigation: Group splits by split_group_id and verify zero overlap gate.

5. Risk: Label drift during review.
- Mitigation: Keep fixed label policy and reject out-of-scope labels in supervised export stage.

## 6. RACI (Lightweight)

- Engineer:
  - Parser updates
  - Export pipeline
  - Gate automation
  - Baseline training scripts

- Analyst/Reviewer:
  - Source-target verification
  - Confidence decisions
  - Review notes and audit trail

- Project owner:
  - Scope decisions
  - Gate threshold sign-off
  - Version lock approval

## 7. Done Definition

Ready for model training when all are true:
1. Gate script returns exit code 0.
2. Supervised exports contain only in-scope automatic labels.
3. Source grounding and confident-or-validated thresholds are met.
4. Split leakage is zero.
5. Dataset card and eval report are present and versioned.
