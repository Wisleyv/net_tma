# Handoff Rapido - Equipe de Treinamento (2026-04-06)

## Objetivo

Este resumo foi feito para a equipe externa de treinamento iniciar rapido, com baixo risco de usar artefatos errados.

## 1) O que ler primeiro (ordem recomendada)

1. [docs/external_handoff_checklist.md](docs/external_handoff_checklist.md)
2. [docs/training_data_spec_v2.md](docs/training_data_spec_v2.md)
3. [releases/training_ready_2026.04.01-a/release_manifest.json](releases/training_ready_2026.04.01-a/release_manifest.json)
4. [releases/training_ready_2026.04.01-a/docs/dataset_card.md](releases/training_ready_2026.04.01-a/docs/dataset_card.md)
5. [releases/training_ready_2026.04.01-a/reports/training_data_gate_report.json](releases/training_ready_2026.04.01-a/reports/training_data_gate_report.json)

## 2) Arquivos obrigatorios para treinamento (pacote congelado)

Use apenas o pacote oficial de entrega:

- [releases/training_ready_2026.04.01-a/dataset_curated.json](releases/training_ready_2026.04.01-a/dataset_curated.json)
- [releases/training_ready_2026.04.01-a/dataset_supervised.json](releases/training_ready_2026.04.01-a/dataset_supervised.json)
- [releases/training_ready_2026.04.01-a/train.jsonl](releases/training_ready_2026.04.01-a/train.jsonl)
- [releases/training_ready_2026.04.01-a/validation.jsonl](releases/training_ready_2026.04.01-a/validation.jsonl)
- [releases/training_ready_2026.04.01-a/test.jsonl](releases/training_ready_2026.04.01-a/test.jsonl)
- [releases/training_ready_2026.04.01-a/release_manifest.json](releases/training_ready_2026.04.01-a/release_manifest.json)
- [releases/training_ready_2026.04.01-a/docs/dataset_card.md](releases/training_ready_2026.04.01-a/docs/dataset_card.md)
- [releases/training_ready_2026.04.01-a/reports/training_data_gate_report.json](releases/training_ready_2026.04.01-a/reports/training_data_gate_report.json)

Observacao importante:

- No release 2026.04.01-a, os contadores oficiais sao: train=20, validation=0, test=0.
- Isso ocorre por restricao de split_group na versao congelada atual.

## 3) Arquivos opcionais (diagnostico interno, pacote nao oficial)

Se voces quiserem reproduzir os checks mais recentes com holdout nao vazio, usem o pack exploratorio:

- [reports/new_pair_v0604a_eval/train.jsonl](reports/new_pair_v0604a_eval/train.jsonl)
- [reports/new_pair_v0604a_eval/validation.jsonl](reports/new_pair_v0604a_eval/validation.jsonl)
- [reports/new_pair_v0604a_eval/test.jsonl](reports/new_pair_v0604a_eval/test.jsonl)
- [reports/new_pair_v0604a_eval/model_sweep_report.json](reports/new_pair_v0604a_eval/model_sweep_report.json)
- [reports/new_pair_v0604a_eval/model_sweep_repro_check.json](reports/new_pair_v0604a_eval/model_sweep_repro_check.json)
- [docs/eval_report_new_pair_v0604a_sweep_repro.md](docs/eval_report_new_pair_v0604a_sweep_repro.md)

Resumo rapido desse pack exploratorio:

- split_counts: train=24, validation=8, test=10
- top model reproduzido: tfidf_linsvc_balanced_char35
- reproducao: exact_metric_match=true e promotion_confirmed=true

## 4) Para que serve o dataset e como ele foi construido

Finalidade:

- Treinar deteccao supervisionada de estrategias de simplificacao a partir de evidencia fonte-alvo.

Construcao (pipeline):

1. Parsing e alinhamento em pares fonte/alvo.
2. Curadoria humana com auditoria de decisao.
3. Export supervisionado com politica de escopo de labels.
4. Gates de qualidade obrigatorios antes do release.

Politica de labels para treino supervisionado:

- In-scope: RF+, SL+, IN+, RP+, RD+, MOD+, DL+, EXP+, MT+
- Fora do escopo supervisionado: OM+, PRO+ (somente diagnostico)

## 5) Como isso conecta com o objetivo de longo prazo

Objetivo de longo prazo do projeto:

- Permitir analise autonoma e confiavel de estrategias de simplificacao textual intralingual.

Como o estado atual ajuda nisso:

- Esquema canonico v2 com rastreabilidade por sample_id e evidencia fonte-alvo.
- Manifesto com checksums para reproducibilidade e auditoria de entrega.
- Gates formais para reduzir ruido de anotacao antes de treino.
- Reproducao de sweep confirmada para evitar regressao silenciosa na base de comparacao.

## 6) Passos minimos ao receber o pacote

1. Validar integridade do release:
   python -m scripts.validate_handoff_package --release-dir releases/training_ready_2026.04.01-a --report-json releases/training_ready_2026.04.01-a/reports/handoff_validation_report.json
2. Conferir manifest, card e gate report.
3. Treinar com os JSONL oficiais do release congelado.
4. Se precisarem de holdout nao vazio para estudos internos, usar apenas o pack exploratorio em reports/new_pair_v0604a_eval sem substituir o pacote oficial.
