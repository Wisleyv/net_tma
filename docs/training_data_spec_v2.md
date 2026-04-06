# Training Data Specification v2 (Simplification Pattern Detection)

Status: Draft for implementation
Date: 2026-03-31
Owner: NET_TMA project
Companion analysis: docs/dataset_training_assessment.md

## 1. Purpose

This specification defines the canonical training dataset format for learning simplification pattern detection from intralingual source-target pairs.

The target task is supervised detection of simplification strategy tags by comparing source and target text evidence.

## 2. Scope and task definition

Task type:
- Primary: multi-class classification over simplification strategy tags.
- Secondary: evidence-grounded extraction (source and target span text) for explainability.

Prediction unit:
- One sample per strategy occurrence.
- Each sample must be grounded in target text and linked to source text.

In-scope labels for automatic detection:
- RF+
- SL+
- IN+
- RP+
- RD+
- MOD+
- DL+
- EXP+
- MT+

Out-of-scope labels for automatic detection:
- OM+
- PRO+

Out-of-scope labels are allowed only as diagnostic metadata and must not be present in the supervised label column used for training.

## 3. Best-practice basis (external guidance)

This spec adopts widely accepted recommendations reflected in:
- OpenAI Fine-tuning Best Practices: prioritize data quality, consistency, train/test separation, and iterative eval-driven improvement.
- OpenAI Model Optimization workflow: eval -> prompt/data iteration -> fine-tune -> eval loop.
- Hugging Face Evaluate guidance: compute multiple metrics, include per-class analysis.
- Google ML guidance on imbalanced datasets: do not rely on accuracy alone; handle class imbalance explicitly.

Reference URLs:
- https://developers.openai.com/api/docs/guides/fine-tuning-best-practices
- https://developers.openai.com/api/docs/guides/model-optimization
- https://developers.openai.com/api/docs/guides/evals
- https://huggingface.co/docs/evaluate/main/en/base_evaluator
- https://developers.google.com/machine-learning/data-prep/construct/sampling-splitting/imbalanced-data

## 4. Canonical schema

The canonical dataset file remains a JSON object:
- metadata: dataset-level metadata
- amostras: list of TrainingSampleV2 items

A JSON Schema file is provided in docs/training_sample_v2.schema.json.

Required sample fields:
- sample_id: unique sample id
- document_id: stable source-target pair id
- split_group_id: grouping key used for leakage-safe splits (normally same as document_id)
- tag_code: in-scope tag code for supervised learning
- target_paragraph_id
- target_text
- target_span_text
- source_paragraph_ids
- source_text
- alignment_confidence
- human_validated
- label_scope
- parser_version
- schema_version
- created_at

Optional sample fields:
- source_span_text
- target_span_start
- target_span_end
- source_span_start
- source_span_end
- reviewer_id
- review_notes
- training_weight
- diagnostics

Field constraints:
- source_paragraph_ids must contain at least one id for in-scope labels.
- target_text and source_text must be non-empty for in-scope labels.
- label_scope must be one of: automatic, diagnostic.
- tag_code in supervised exports must be in-scope.
- training_weight default is 1.0.

## 5. Label policy

Supervised label column:
- tag_code

Policy:
- Only in-scope labels are allowed in supervised training files.
- OM+ and PRO+ are retained only in diagnostic files.
- Composite annotations (example RF+/RP+) must produce separate samples, one per tag_code, linked by a shared multi_tag_group_id in diagnostics.

## 6. Curation policy

Gold set eligibility (recommended):
- human_validated == true
- alignment_confidence >= 0.80 OR explicit manual source mapping confirmed
- label_scope == automatic
- target_span_text normalized (no bracket artifacts)

Silver set eligibility (optional):
- label_scope == automatic
- alignment_confidence >= 0.60
- not manually rejected

No-go records for training:
- missing source_paragraph_ids
- empty source_text for in-scope labels
- unresolved composite tag parsing
- contradictory reviewer decisions

## 7. Split policy and leakage control

Split strategy:
- Split by split_group_id, never by random row.
- Recommended ratio: 70/15/15 (train/validation/test) once data volume permits.
- For low-volume stage: GroupKFold by split_group_id.

Leakage prevention:
- No split may contain samples from the same split_group_id in multiple partitions.
- No near-duplicate span pair should cross partitions.

## 8. Class imbalance policy

Requirements:
- Track per-tag counts before each training run.
- Report macro-F1 as primary metric.
- Report per-tag precision, recall, F1.

Mitigation options:
- Class-weighted loss.
- Controlled downsampling of majority labels.
- Targeted data collection for minority labels.

Do not use accuracy as the only decision metric.

## 9. Evaluation protocol

Minimum evaluation outputs per model run:
- macro_f1
- weighted_f1
- per_tag_precision_recall_f1
- confusion_matrix
- calibration summary or confidence histogram (if available)
- error bucket report by tag pair confusion

Evaluation set rules:
- Must be fixed and versioned.
- Must be disjoint from training by split_group_id.
- Must include a representative distribution of tags and document styles.

## 10. Acceptance gates (hard quality checks)

A dataset build is accepted for supervised training only if all checks pass:

1. Source grounding coverage >= 95% for in-scope labels.
2. Confident-or-validated coverage >= 90% for in-scope labels.
3. Out-of-scope labels in supervised export == 0.
4. Parse coverage >= 98%: parsed tags / observed tag markers.
5. Duplicate supervised keys == 0.
Key definition: document_id + target_paragraph_id + target_span_start + target_span_end + tag_code.
6. Null/empty critical fields == 0 for supervised rows.
7. Split leakage count == 0 by split_group_id.
8. Dataset card updated with version, provenance, and known limitations.

## 11. Export contracts

Required outputs per build:
- dataset_curated.json
- train.jsonl
- validation.jsonl
- test.jsonl
- dataset_card.md
- eval_report.md

JSONL line format for supervised training:
- One JSON object per line.
- Contains task prompt fields plus expected label.
- Must preserve sample_id for traceability.

## 12. Mapping to current repository implementation

Parser changes required:
- parser/annotations.py
Add support for composite tags and bodyless tags while preserving strict mode diagnostics.
Add normalized span extraction and optional char offsets.

- parser/alignment.py
Improve fallback alignment coverage and emit calibrated confidence score in [0,1].

- parser/builder.py
Populate source_paragraph_ids and source_text for in-scope labels.
Separate diagnostic labels via label_scope field.

Validator changes required:
- validator_app/view.py and validator_app/models.py
Add explicit validation status for source grounding confirmation.
Add tag-scope awareness (automatic vs diagnostic).

Data contract changes:
- parser/schema.py
Introduce TrainingSampleV2 fields and defaults consistent with JSON Schema.

## 13. Readiness checklist

Use this checklist before any training run:

- [ ] In-scope label policy applied (OM+/PRO+ excluded from supervised labels).
- [ ] Source grounding coverage threshold passed.
- [ ] Confidence/validation threshold passed.
- [ ] Parse coverage threshold passed.
- [ ] No split leakage by split_group_id.
- [ ] Per-tag counts reviewed and imbalance mitigation selected.
- [ ] Train/validation/test artifacts generated and versioned.
- [ ] dataset_card.md updated.
- [ ] eval_report.md generated with macro-F1 and per-tag metrics.

## 14. Versioning

Versioning format:
- schema_version: semantic version for structure (example 2.0.0)
- dataset_version: semantic or date-based version for content (example 2026.03.31-a)

Any structural field change requires schema_version bump.
Any sample-content regeneration requires dataset_version bump.

## 15. Enforcement command

Run the gate locally:

```bash
python -m scripts.validate_training_dataset \
	--dataset dataset_curated.json \
	--target-markdown patriotismo_tt.md \
	--dataset-card docs/dataset_card.md \
	--train-jsonl train.jsonl \
	--validation-jsonl validation.jsonl \
	--test-jsonl test.jsonl \
	--report-json reports/training_data_gate_report.json
```

Exit codes:
- 0: all gates passed.
- 1: one or more gates failed.
- 2: invalid invocation (for example, dataset file not found).

## 16. Phase 2 review workflow command

Generate Phase 2 artifacts (curated bridge + pending review queue):

```bash
python -m scripts.phase2_review_workflow \
	--dataset dataset_raw.json \
	--output dataset_curated.json \
	--queue-json reports/phase2_review_queue.json \
	--queue-md reports/phase2_review_queue.md \
	--decision-template-json reports/phase2_review_decisions.template.json
```

Apply reviewer decisions and refresh artifacts:

```bash
python -m scripts.phase2_review_workflow \
	--dataset dataset_raw.json \
	--decisions-json reports/phase2_review_decisions.json \
	--output dataset_curated.json \
	--queue-json reports/phase2_review_queue.json \
	--queue-md reports/phase2_review_queue.md
```

Decision tokens accepted in decisions JSON:
- validate: sets human_validated=true
- reject: sets human_validated=false
- diagnostic: forces label_scope=diagnostic
- keep: leaves the sample unresolved

## 17. Phase 3 supervised export command

Generate supervised-only exports and split artifacts:

```bash
python -m scripts.build_supervised_exports \
	--dataset dataset_curated.json \
	--output-dataset dataset_supervised.json \
	--train-jsonl train.jsonl \
	--validation-jsonl validation.jsonl \
	--test-jsonl test.jsonl \
	--report-json reports/phase3_export_summary.json \
	--min-validation-rows 1 \
	--min-test-rows 1
```

Notes:
- Use --group-field target_paragraph_id to diversify split groups for small corpora.
- Raise --min-validation-rows and --min-test-rows during B-14 when holdout
  support must meet a reporting threshold (for example, 3 rows each).

Expected outputs:
- dataset_supervised.json
- train.jsonl
- validation.jsonl
- test.jsonl
- reports/phase3_export_summary.json

## 18. Phase 4 version lock release package command

Build an immutable training-ready package only after gate pass:

```bash
python -m scripts.build_training_release_package \
	--dataset dataset_curated.json \
	--supervised-dataset dataset_supervised.json \
	--train-jsonl train.jsonl \
	--validation-jsonl validation.jsonl \
	--test-jsonl test.jsonl \
	--dataset-card docs/dataset_card.md \
	--gate-report reports/training_data_gate_report.json \
	--phase3-report reports/phase3_export_summary.json \
	--output-root releases \
	--dataset-version 2026.04.01-a \
	--schema-version 2.0.0 \
	--release-id 2026.04.01-a
```

Expected outputs:
- releases/training_ready_2026.04.01-a/release_manifest.json
- Frozen copies of dataset and split artifacts under releases/training_ready_2026.04.01-a/

## 19. Phase 5 baseline training command

Run baseline training and evaluation against the version-locked package:

```bash
python -m scripts.run_baseline_training \
	--release-dir releases/training_ready_2026.04.01-a \
	--report-json reports/baseline_model_report.json \
	--eval-report-md docs/eval_report.md \
	--errors-json reports/baseline_error_buckets.json
```

Expected outputs:
- reports/baseline_model_report.json
- docs/eval_report.md
- reports/baseline_error_buckets.json

Notes:
- If validation/test splits are empty, the baseline report must explicitly
  mark those splits unavailable and provide cross-validation fallback metrics.
