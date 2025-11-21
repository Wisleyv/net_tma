# Parser Interfaces and Sample Output

## 1. Core function signatures

These functions outline the primary contracts the `parser/` package must fulfill. They are intentionally implementation-agnostic but include enough detail for downstream teams to build upon.

### `parser.segmentation`
- `def segment_source(source_path: str) -> dict[str, str]`
  - Reads `patriotismo_st.md`.
  - Returns `{paragrafo_fonte_id: paragrafo_texto}` with IDs like `F_001`, `F_002`, etc.
- `def segment_target(target_path: str) -> dict[str, str]`
  - Reads `patriotismo_tt.md`.
  - Returns `{paragrafo_alvo_id: paragrafo_bruto}`.

### `parser.annotations`
- `def extract_annotations(target_paragraphs: dict[str, str]) -> list[dict]`
  - Scans each paragraph for `[TAG+ ...]` patterns.
  - Yields dicts with keys: `tag`, `conteudo_bruto`, `paragrafo_alvo_id`, `posicao_inicio`, `posicao_fim`.
- `def clean_paragraph(paragraph_text: str) -> str`
  - Returns the paragraph text with all `[TAG+ ...]` blocks removed.

### `parser.alignment`
- `def detect_sections(paragraphs: dict[str, str]) -> dict[str, list[str]]`
  - Groups paragraphs by headings (e.g., `"OS MILITARES"`).
- `def align_paragraphs(source_sections: dict, target_sections: dict) -> dict[str, dict]`
  - For each `paragrafo_alvo_id`, returns `{"paragrafo_fonte_ids": list[str], "fonte_alinhamento_confiavel": bool}`.
  - Uses relative order and paragraph length heuristics; may leave empty lists when uncertain.

### `parser.builder`
- `def build_samples(annotations: list[dict], target_clean: dict[str, str], alignment: dict[str, dict], tag_definitions: dict[str, dict]) -> list[dict]`
  - Combines tags, cleaned text, alignment info, and `tab_est.md` metadata.
  - Outputs sample dicts containing the fields listed in `algorithm.md` (id, tag, nome, contexto_anotacao, paragrafo_alvo_id, paragrafo_fonte_ids, fonte_alinhamento_confiavel, texto_paragrafo_alvo, texto_paragrafo_fonte, trecho_alvo, trecho_fonte, necesita_revisao_humana, motivo_revisao, tipo_nivel).

### `parser.cli`
- `def main(source_path: str, target_path: str, tags_path: str, output_path: str) -> None`
  - High-level orchestration of segmentation, annotation extraction, alignment, and JSON serialization.
  - Writes `dataset_raw.json` (metadata + `amostras`).

### Shared schema helpers (`parser.schema`)
- Provide dataclasses or `TypedDict` definitions for:
  - `AnnotationSample` (fields enumerated above).
  - Metadata structure (project name, version, idioma, descricao, padrao_tags).

## 2. Example JSON samples (Model 1)

The samples below illustrate how actual annotations in `patriotismo_tt.md` translate into dataset objects.

```json
{
  "metadata": {
    "projeto": "Analise_Estrategias_Simplificacao_Textual",
    "versao": "0.1",
    "idioma": "pt-BR",
    "descricao": "Cada anotacao vira um registro; o primeiro lote cobre o verbete \"Patriotismo\".",
    "padrao_tags": "tab_est.md"
  },
  "amostras": [
    {
      "id": "PAT_0001_SL",
      "tag": "SL+",
      "nome": "Simplificacao Lexical",
      "tipo_nivel": "lexical",
      "contexto_anotacao": "díspares",
      "paragrafo_alvo_id": "A_002",
      "paragrafo_fonte_ids": ["F_005"],
      "fonte_alinhamento_confiavel": true,
      "texto_paragrafo_alvo": "Desde então, essas ideias têm sido invocadas por forças políticas e ideologias muito diferentes, e, por isso, também bastante criticadas. O patriotismo-nacionalismo diferenc...",
      "texto_paragrafo_fonte": "Desde então, patriotismo e nacionalismo têm sido invocados por forças políticas e ideologias muito díspares, ...",
      "trecho_alvo": "ideologias muito diferentes",
      "trecho_fonte": "ideologias muito díspares",
      "necessita_revisao_humana": false,
      "motivo_revisao": null
    },
    {
      "id": "PAT_0002_OM",
      "tag": "OM+",
      "nome": "Omissao",
      "tipo_nivel": "discurso",
      "contexto_anotacao": "3 parágrafos cortados: vinheta e introdução",
      "paragrafo_alvo_id": "A_001",
      "paragrafo_fonte_ids": [],
      "fonte_alinhamento_confiavel": false,
      "texto_paragrafo_alvo": "",
      "texto_paragrafo_fonte": null,
      "trecho_alvo": null,
      "trecho_fonte": null,
      "necessita_revisao_humana": true,
      "motivo_revisao": "omissao extensa; sem alinhamento confiavel"
    },
    {
      "id": "PAT_0003_PRO",
      "tag": "PRO+",
      "nome": "Problema de traducao",
      "tipo_nivel": "discurso",
      "contexto_anotacao": "a introducao ficou desconectada devido à falta de menções ao 7 de setembro...",
      "paragrafo_alvo_id": "A_010",
      "paragrafo_fonte_ids": ["F_045"],
      "fonte_alinhamento_confiavel": false,
      "texto_paragrafo_alvo": "Mas há algo de novo nas cenas patrióticas do presente...",
      "texto_paragrafo_fonte": "Mas há algo de novo nas cenas patrióticas do presente...",
      "trecho_alvo": null,
      "trecho_fonte": null,
      "necessita_revisao_humana": true,
      "motivo_revisao": "tag PRO+; tratar como anotacao auxiliar"
    }
  ]
}
```

These examples illustrate the schema (target paragraph, optional source text, metadata, review flags). They will serve as reference fixtures for tests and for the validator UI.