# Roadmap Review (2026-04-06)

Historical note:
- This document records a point-in-time scope/suitability review and should be
	read as historical analysis.
- Several items flagged here as gaps were resolved later on 2026-04-06 (B-15,
	B-16, B-17 closure and hybrid validation consolidation).
- For current status, use:
	- docs/execution_board.md
	- ROADMAP.md
	- docs/release_note_hybrid_2026-04-06.md

## 1) Scope Reset (Authoritative)

This review formalizes the project boundary for the current academic partnership phase.

In scope now:
- Build and maintain a training-ready dataset package.
- Provide evidence and documentation so the external university team can evaluate training suitability.
- Stabilize backend workflows and the linguist-facing interface so dataset population is reliable and scalable.

Out of scope now:
- Training or selecting production language models inside this repository.
- Building the full AI-driven analysis platform in this phase.

Interpretation rule:
- Baseline and sweep model runs in this repo are diagnostic evidence for dataset quality, not product-training deliverables.

## 2) Current Baseline (Evidence)

Operationally strong:
- Dataset release bundle exists: releases/training_ready_2026.04.01-a.
- Gate reports are passing for current curated/export flows (8/8 PASS in the latest board snapshots).
- v06-04 and v06-04a real-pair ingestion runs are integrated and documented.

Operationally incomplete:
- A formal handoff package checklist for the external team is not yet codified as a single acceptance gate.
- Interface/backend contract alignment is partial (see VAEST suitability section).

## 3) VAEST Interface Suitability Assessment (vaest.exe)

### 3.1 Build and distribution suitability

Strengths:
- Windows packaging automation is present via scripts/build_validator_exe.py.
- Packaging docs are present in docs/packaging.md.
- Entry-point isolation is clear via scripts/vaest_entry.py.

Risks:
- No tracked dist/vaest.exe artifact in the repository snapshot; release readiness depends on reproducible rebuilds.
- CI smoke validates python -m validator_app on dataset_raw.json, but does not validate compatibility against curated v2 artifacts.

Assessment:
- Suitable for controlled internal builds and analyst distribution when the packaging pipeline is executed for release.

### 3.2 Functional suitability for linguists

Strengths:
- Efficient review operations exist (filtering, sequential navigation, reviewer initials, history log).
- Converter and parser orchestration are integrated into the UI.

Gaps already known in roadmap/executive summary:
- Persistent project data folder and file association lifecycle.
- Side-by-side full source/target context panels.
- Controlled tag management workflow.
- Human-readable export for review outcomes.

Assessment:
- Conditionally suitable for ongoing annotation/review throughput, but still below target ergonomics for sustained scale.

### 3.3 Backend-update compatibility suitability

Observed compatibility result:
- validator_app.data_loader is legacy-key oriented (id/tag/paragrafo_fonte_ids/texto_paragrafo_fonte).
- Curated v2 datasets use canonical keys (sample_id/tag_code/source_paragraph_ids/source_text/target_text).
- Loader can read files but key mapping drops source context and tag identity fidelity for v2 rows unless explicitly mapped.

Practical impact:
- VAEST is suitable for legacy parser output review (dataset_raw-style workflow).
- VAEST is not yet suitable as a direct QA interface for canonical curated v2 datasets used in release/handoff.

Assessment:
- Suitability after backend updates: PARTIAL.

## 4) Revised Roadmap (Scope-Aligned)

### Phase R0 - Governance realignment (Done)
Goal:
- Lock current scope to dataset engineering + external handoff readiness.

Exit criteria:
- Scope statement applied in roadmap/board/status artifacts.

### Phase R1 - Dataset pipeline reliability (Mostly done)
Goal:
- Keep parser -> curation -> export -> gate workflow stable and reproducible.

Exit criteria:
- Gate pass reproducibility on each new pair integration.
- Release manifest + dataset card updated per version.

### Phase R2 - VAEST/backend contract bridge (Next, P0)
Goal:
- Make VAEST schema-aware for both legacy and canonical v2 records.

Tasks:
1. Add dual-schema read mapping in validator_app.data_loader.
2. Preserve canonical fields on save (round-trip safe) or enforce explicit export mode.
3. Add CI smoke that opens a canonical curated sample file.

Exit criteria:
- VAEST can load curated v2 with correct source/target/tag rendering.
- No loss of canonical fields after save workflow.

### Phase R3 - Linguist operations hardening (Next, P1)
Goal:
- Reduce reviewer friction and errors during large annotation cycles.

Tasks:
1. Persistent data folder and stable file associations.
2. Side-by-side source/target contextual panels.
3. Controlled tag change action with audit logging.
4. Human-readable markdown/txt export.

Exit criteria:
- Reviewer workflow can run without external tools for core validation context.

### Phase R4 - External handoff package standardization (Next, P0)
Goal:
- Deliver a complete package for the university training team to assess and run independently.

Tasks:
1. Publish handoff checklist with mandatory artifacts and acceptance criteria.
2. Include schema/version notes, gate report, label policy, and known limitations.
3. Freeze release naming/versioning protocol for repeated deliveries.

Exit criteria:
- External team can validate dataset readiness without ad hoc clarification loops.

### Phase R5 - Future platform track (Deferred)
Goal:
- Start the full AI-driven analysis/reporting product only after R2-R4 maturity.

## 5) Handoff Package Minimum (for external training team)

Per release, provide:
- dataset_curated.json
- dataset_supervised.json
- train.jsonl
- validation.jsonl
- test.jsonl
- release_manifest.json
- docs/dataset_card.md
- reports/training_data_gate_report.json
- Short release note summarizing corpus deltas, risks, and known limitations

## 6) Decision Summary

Current go/no-go:
- GO for continuing dataset engineering and handoff preparation under the revised scope.
- CONDITIONAL GO for VAEST in linguist review workflows tied to legacy parser output.
- NO-GO for using current VAEST as direct canonical-v2 QA front-end until Phase R2 is completed.

Immediate priority order:
1. Phase R2 schema bridge.
2. Phase R4 handoff checklist and release protocol.
3. Phase R3 usability upgrades that directly increase reviewer throughput.
