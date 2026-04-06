# External Handoff Release Note Template

Use this template for every dataset handoff to the external university training team.

## 1) Release Header

- Release ID: `<training_ready_YYYY.MM.DD-x>`
- Delivery Date (UTC): `<YYYY-MM-DD>`
- Prepared By: `<name>`
- Recipient Team: `<institution/team>`
- Scope: `Dataset engineering package + documentation (no in-repo model training)`

## 2) Version Contract

- Dataset Version: `<dataset_version>`
- Schema Version: `<schema_version>`
- Source Snapshot/Commit: `<git commit or tag>`

## 3) Included Artifacts

List each artifact with checksum from `release_manifest.json`:

| Path | SHA256 | Notes |
| --- | --- | --- |
| dataset_curated.json | `<sha256>` | Curated source corpus |
| dataset_supervised.json | `<sha256>` | Supervised labels for training |
| train.jsonl | `<sha256>` | Train split |
| validation.jsonl | `<sha256>` | Validation split |
| test.jsonl | `<sha256>` | Test split |
| docs/dataset_card.md | `<sha256 or N/A>` | Dataset documentation |
| reports/training_data_gate_report.json | `<sha256 or N/A>` | Quality gate evidence |

## 4) Data Snapshot Summary

- Curated Samples: `<count>`
- Supervised Samples: `<count>`
- Train Rows: `<count>`
- Validation Rows: `<count>`
- Test Rows: `<count>`
- Label Distribution Note: `<short summary>`

## 5) Validation Evidence

- Handoff Validator Command:

```bash
python -m scripts.validate_handoff_package \
  --release-dir releases/<release_id> \
  --report-json releases/<release_id>/reports/handoff_validation_report.json
```

- Validator Result: `<PASS/FAIL>`
- Gate Report Result: `<PASS/FAIL>`
- Validation Report Path: `releases/<release_id>/reports/handoff_validation_report.json`

## 6) Known Constraints and Risks

- `<constraint or risk 1>`
- `<constraint or risk 2>`
- `<mitigation or owner>`

## 7) Expected External Actions

1. Verify checksums against `release_manifest.json`.
2. Confirm parser compatibility with `schema_version`.
3. Run university-side training/evaluation protocol.
4. Return training metrics and issue log with `release_id`.

## 8) Communication Footer

- Primary Contact: `<name/email>`
- Escalation Contact: `<name/email>`
- Tracking Reference: `<board ticket or log entry>`
