# Dataset Training Assessment (LLM Perspective)

Date: 2026-03-31
Scope: Evaluate dataset_raw.json for training a model to detect intralingual text simplification patterns from source-target comparison.

## 1) Executive verdict

Current verdict: not ready for direct model training for the intended task.

Reason: the current dataset snapshot lacks usable source alignment for all samples, while the target task depends on comparing source and target text.

The dataset is still valuable as a seed corpus for curation and can become training-ready after targeted fixes.

## 2) Evidence from current dataset snapshot

Data file inspected: dataset_raw.json

Observed metrics:
- Total samples: 26
- Unique target paragraphs (paragrafo_alvo_id): 10
- Unique tags: 9
- Samples with empty paragrafo_fonte_ids: 26/26
- Samples with empty texto_paragrafo_fonte: 26/26
- fonte_alinhamento_confiavel=true: 0/26
- necessita_revisao_humana=true: 26/26
- trecho_fonte equals contexto_anotacao: 26/26
- trecho_alvo still contains bracket marker '[': 6/26

Label distribution:
- OM+: 7
- SL+: 5
- PRO+: 3
- RD+: 3
- RF+: 3
- MOD+: 2
- DL+: 1
- IN+: 1
- RP+: 1

Concentration effect:
- Top duplicated target paragraph IDs: A_004 (6), A_017 (5), A_006 (4), A_008 (4)

Annotation syntax coverage in patriotismo_tt.md:
- Tag starts found: 30
- Strict tags parsed by current parser pattern: 26
- Composite markers found (example pattern TAG1+/TAG2+): 2

Interpretation:
- 4 tag markers are currently not represented in dataset_raw.json due to syntax mismatch with strict parser extraction.

## 3) Structural strengths

Despite current limitations, the schema has useful training-oriented fields:
- Explicit strategy label (tag)
- Target context and snippets (contexto_anotacao, trecho_alvo)
- Alignment confidence and review flags (fonte_alinhamento_confiavel, necessita_revisao_humana, motivo_revisao)
- Stable sample IDs and metadata envelope

These are good foundations for data-centric training workflows.

## 4) Critical blockers for the intended objective

Intended objective: learn simplification patterns by comparing source and target text.

Blockers:
1. No source grounding in the current snapshot.
   - paragrafo_fonte_ids and texto_paragrafo_fonte are empty for all samples.
   - This prevents supervised learning of source-target transformations.

2. All samples are low-confidence/review-needed.
   - 26/26 flagged for human review and 0/26 with confident alignment.
   - High label uncertainty is harmful for direct SFT unless filtered or weighted.

3. Out-of-scope labels are mixed into training labels.
   - tab_est.md states OM+ and PRO+ are not automatic-detection targets.
   - In current snapshot, OM+ and PRO+ are 10/26 (38.5%).

4. Small and narrow corpus.
   - 26 samples from one text pair is far below typical diversity needs.
   - Heavy paragraph reuse increases leakage risk and overfitting.

5. Extraction-schema friction.
   - Current parser regex expects [TAG+ space body], so bodyless tags and some composite forms are dropped or flattened.
   - Some trecho_alvo values still include bracket annotations, adding noise.

## 5) Comparison against current best practices (LLM training)

The assessment below reflects broadly accepted modern practice for supervised LLM training and classification-style adaptation:

1. Data quality over model complexity
- Best practice: prioritize clean, trusted labels and grounded examples before model scaling.
- Current status: fails due to missing source grounding and all-sample review flags.

2. Task-label alignment
- Best practice: train only on labels inside the model objective.
- Current status: fails because out-of-scope tags (OM+, PRO+) are present in the same label pool.

3. Train/validation/test split design
- Best practice: split by document/source unit, not by near-duplicate sample rows, to reduce leakage.
- Current status: high repetition over 10 target paragraphs makes random row splits unreliable.

4. Uncertainty handling
- Best practice: exclude uncertain labels from gold training, or down-weight them with confidence-aware losses.
- Current status: all rows are uncertain/review-needed.

5. Schema for structured outputs
- Best practice: maintain explicit evidence fields and normalized spans/offsets for reproducibility.
- Current status: partially aligned, but snippet contamination and missing source links reduce reliability.

6. Evaluation and governance
- Best practice: macro-F1/per-label metrics, confusion analysis, calibration checks, and dataset versioning with data cards.
- Current status: not yet supported by current snapshot quality.

## 6) Recommended path to training readiness

Phase 0: define training target clearly
- Primary detect labels: RF+, SL+, IN+, RP+, RD+, MOD+, DL+, EXP+, MT+.
- Exclude OM+ and PRO+ from automatic-detection training set (keep as review diagnostics).

Phase 1: repair dataset generation
- Recover source alignment so paragrafo_fonte_ids and texto_paragrafo_fonte are populated.
- Extend parser extraction to support composite/bodyless annotations explicitly.
- Normalize trecho_alvo to remove bracket artifacts.

Phase 2: build gold subset
- Use validator to produce a reviewed set with trusted alignments and reviewer audit.
- Keep only high-confidence or human-confirmed rows for initial supervised training.

Phase 3: expand and diversify corpus
- Add many more source-target document pairs across topics/registers.
- Avoid over-concentration of rows from the same target paragraph.

Phase 4: training/evaluation protocol
- Split by document pair (not random row).
- Report per-tag precision/recall/F1 and macro-F1.
- Track confusion between related tags (RF vs RD, RP vs RF, etc.).

## 7) Go/no-go decision for model training now

Decision for current dataset_raw.json snapshot: no-go for direct production training.

Decision for near-term: go for a curation-first pipeline.
- Use the current schema and tooling as scaffolding.
- Promote only aligned, reviewed, in-scope labels into a gold training set.

## 8) Key repository references

- parser/schema.py (AnnotationSample fields)
- parser/annotations.py (strict extraction regex)
- parser/builder.py (_REVIEW_TAGS includes OM+, PRO+, RP+)
- tab_est.md (OM+ and PRO+ declared out-of-scope for automatic detection)
- docs/project_status.md (best-effort alignment constraint)
- TUTORIAL.md (heuristic alignment may require manual review)

## 9) Execution artifacts

- docs/training_readiness_plan.md (detailed execution plan)
- docs/execution_board.md (dependency-aware execution board)
- docs/training_data_spec_v2.md (canonical requirements and gate policy)
- scripts/validate_training_dataset.py (hard gate enforcement)
