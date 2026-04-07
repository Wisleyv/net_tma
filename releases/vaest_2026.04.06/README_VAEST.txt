VAEST quick start (Windows)

1) Execute vaest.exe.
2) Open a dataset via Arquivo -> Abrir dataset... (or keep JSON in the same folder).

Included JSON files:
- dataset_raw.json: legacy parser output (includes all tags).
- dataset_curated.json: canonical v2 dataset with automatic + diagnostic labels.
- dataset_supervised.json: supervised-ready subset (automatic/in-scope labels only).

Included starter files:
- tab_est.md: canonical tag definitions.
- sample_source_all_tags.md + sample_target_all_tags.md: source/target pair with all in-scope automatic tags (RF+, SL+, IN+, RP+, RD+, MOD+, DL+, EXP+, MT+).

Operational note:
- OM+ and PRO+ are diagnostic labels, not part of the supervised in-scope set.