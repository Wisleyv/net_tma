# External Handoff Checklist (B-16)

## Purpose

Define a repeatable, auditable handoff process for delivering frozen training-ready
packages to the external university training team.

## Scope Guardrail

This checklist covers dataset package quality and release documentation only.
Model training execution and model selection are out of scope for this repository.

## Standard Inputs

1. Frozen release directory: `releases/training_ready_<release_id>/`
2. Release manifest: `release_manifest.json`
3. Data quality gate report: `reports/training_data_gate_report.json`
4. Dataset card: `docs/dataset_card.md`

## Required Artifacts

The handoff package must include all files below:

- `dataset_curated.json`
- `dataset_supervised.json`
- `train.jsonl`
- `validation.jsonl`
- `test.jsonl`
- `release_manifest.json`
- `docs/dataset_card.md`
- `reports/training_data_gate_report.json`

## Validation Command (Required)

Run the automated handoff validation before every external delivery:

```bash
python -m scripts.validate_handoff_package \
  --release-dir releases/training_ready_<release_id> \
  --report-json releases/training_ready_<release_id>/reports/handoff_validation_report.json
```

Optional strict mode when non-empty holdouts are mandatory:

```bash
python -m scripts.validate_handoff_package \
  --release-dir releases/training_ready_<release_id> \
  --require-non-empty-holdouts
```

## Acceptance Checklist

All items must be marked PASS before handoff:

1. Required files are present in the frozen release directory.
2. `release_manifest.json` checksums match all listed artifacts.
3. Manifest counts match observed JSONL line counts.
4. `dataset_version` and `schema_version` are consistent across:
   - `release_manifest.json`
   - `dataset_curated.json` metadata
   - `dataset_supervised.json` metadata
5. Gate report status is PASS (`"passed": true`).
6. Supervised labels do not include out-of-scope tags (`OM+`, `PRO+`).
7. Dataset card includes versioning, provenance, and limitations.
8. Release note is produced using the handoff template.
9. Delivery message includes release ID, schema version, and checksum location.

## Delivery Packet Protocol

1. Freeze package in `releases/training_ready_<release_id>/`.
2. Run validator script and persist JSON report under `reports/`.
3. Fill release note using `docs/external_handoff_release_note_template.md`.
4. Share package path (or archive), release note, and validation report together.
5. Record handoff completion in board/status docs.

## Sign-Off Block

- Release ID:
- Delivery Date (UTC):
- Prepared By:
- Validator Result:
- University Recipient:
- Acknowledgement Received (Y/N):
- Notes/Risks:
