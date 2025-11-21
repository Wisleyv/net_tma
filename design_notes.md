# Design Notes – Parser and Desktop Validator

## Architectural Decision

- **Parser (CLI, developer-facing)**
  - Implemented in Python as a command-line tool.
  - Reads source and target Markdown files (e.g., `<name>_st.md`, `<name>_tt.md`) plus `tab_est.md` (tag definitions).
  - Applies the spec in `algorithm.md` (Model 1: 1 tag → 1 JSON sample).
  - Outputs a file como `dataset_raw.json`.
  - Executado por usuários com familiaridade técnica (desenvolvedores), não pelos linguistas.

- **Desktop validator (Windows, analyst-facing)**
  - Aplicativo desktop em Python (ex.: PySide6/PyQt5) empacotado como `.exe`.
  - Carrega `dataset_raw.json` e exibe, para cada anotação:
    - `texto_paragrafo_alvo` (limpo),
    - `texto_paragrafo_fonte` opcional,
    - `tag`, `contexto_anotacao`,
    - flags como `fonte_alinhamento_confiavel`, `necessita_revisao_humana`.
  - Permite que analistas humanos:
    - Confirmem ou ajustem o alinhamento de parágrafos fonte,
    - Selecione manualmente parágrafos fonte quando necessário,
    - Editem `trecho_fonte` / `trecho_alvo`,
    - Alterem `necessita_revisao_humana`, `motivo_revisao`.
  - Salva o resultado como `dataset_refinado.json`, que se torna o dataset de ouro para treinamento.

## Python Package Structure

Estrutura sugerida na raiz do projeto (onde estão `codebase/` e `copilot_instructions.md`):

- `parser/`
  - `__init__.py`
  - `cli.py` — ponto de entrada da linha de comando.
  - `segmentation.py` — funções para segmentar arquivos Markdown (fonte e alvo) em parágrafos e atribuir IDs.
  - `annotations.py` — funções para:
    - extrair anotações `[TAG+ ...]` dos parágrafos alvo,
    - produzir parágrafos alvo limpos.
  - `alignment.py` — lógica de alinhamento em nível de parágrafo (best effort):
    - detecção de seções (headings),
    - mapeamento de parágrafos fonte ↔ alvo por seção,
    - decisão de `fonte_alinhamento_confiavel`.
  - `builder.py` — monta as amostras JSON finais:
    - consome segmentação, anotações, alinhamento e `tab_est.md`,
    - constrói a lista de amostras com todos os campos exigidos.
  - `schema.py` (opcional) — constantes / dataclasses com nomes de campos, tipos e valores padrão (mantém CLI e GUI sincronizados).
  - `io_utils.py` — leitura/escrita de markdown e JSON (e, se necessário, CSV).

- `validator_app/`
  - `__init__.py`
  - `main.py` — ponto de entrada da GUI (usado ao empacotar como `.exe`).
  - `model.py` — modelo de dados envolvendo as amostras JSON:
    - carrega e salva `dataset_raw.json` / `dataset_refinado.json`,
    - fornece filtros (ex.: "apenas itens que precisam de revisão").
  - `views.py` — widgets / janelas Qt:
    - janela principal com:
      - lista de anotações,
      - painel de detalhes para texto fonte/alvo + campos editáveis.
  - `controllers.py` (ou integrado a `views.py`):
    - liga ações do usuário (cliques, seleções) às atualizações em `model`.
  - `resources/` (opcional) — ícones, estilos, etc.

- `scripts/` (opcional)
  - `run_parser.py` — pequeno script que chama `parser.cli.main()` com caminhos padrão.
  - `run_validator.py` — script para lançar a GUI (`validator_app.main`).

- `README.md`
  - Instruções curtas:
    - como executar o parser (para desenvolvedores),
    - como iniciar o validador (para analistas).
