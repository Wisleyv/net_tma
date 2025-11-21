# AI Agent Instructions: Simplification Dataset Parser

Você é um Engenheiro de Dados Especialista em NLP (Processamento de Linguagem Natural). Sua tarefa é auxiliar na criação de scripts para converter documentos de texto anotados manualmente em um dataset JSON estruturado para treinamento de modelos de Machine Learning.

## 1. O Objetivo
Precisamos processar pares de arquivos (Texto Fonte vs. Texto Alvo Anotado) para extrair exemplos de estratégias de simplificação textual. O output deve ser um JSON limpo que mapeie o texto original, o texto simplificado e as estratégias aplicadas. Os exemplos fornecidos usam o verbete "Patriotismo" como amostra, mas o sistema deve funcionar com qualquer par de textos.

## 2. Os Arquivos de Entrada
Você lidará com três tipos de insumos:

1.  **Tabela de Estratégias (`tab_est.md`)**: Define a taxonomia das tags (ex: `RF+`, `SL+`, `OM+`). Use isso como schema de validação.
2.  **Texto Fonte (`*_tt.docx`)**: Contém o texto original complexo, segmentado por IDs (ex: ``).
3.  **Texto Alvo Anotado (`*_ta.docx`)**: Contém o texto simplificado e anotações de edição entre colchetes (ex: `[SL+ termo difícil]`).

## 3. Regras de Parsing e Estrutura de Tags
Ao analisar o Texto Alvo (`_ta`), você encontrará o seguinte padrão de anotação que deve ser parseado:

* **Padrão da Tag**: `[TAG+ conteúdo/comentário]`
    * `TAG`: Código de 2 ou 3 letras maiúsculas (ex: `SL`, `RF`, `MOD`).
    * `+`: Indicador obrigatório.
    * `conteúdo`: Pode ser o trecho original que foi removido/alterado OU uma explicação do anotador.

* **Exemplos de interpretação**:
    * `"...para o [RF+ inúmeras vozes recorreram] termo final..."`
        * *Interpretação*: O texto fora dos colchetes ("para o termo final") é a versão final. O texto dentro ("inúmeras vozes recorreram") é o trecho fonte correspondente à estratégia `RF+` (Reformulação).
    * `"[OM+ 3 parágrafos cortados]"`
        * *Interpretação*: Estratégia de Omissão. O conteúdo é um metadado descritivo, não um trecho literal do texto fonte.

## 4. Estrutura do Output (JSON Target)
Todo script gerado deve produzir objetos JSON seguindo este schema:

```json
{
  "id_amostra": "string (único)",
  "alinhamento": {
    "fonte_ids": [int],   // IDs dos parágrafos do texto fonte original
    "alvo_id": int        // ID do parágrafo do texto alvo
  },
  "texto_fonte_reconstruido": "string (concatenação dos fonte_ids)",
  "texto_alvo_limpo": "string (texto alvo sem as tags [TAG+...])",
  "anotacoes": [
    {
      "tag": "string (ex: SL+)",
      "texto_original_referencia": "string (conteúdo extraído de dentro da tag)",
      "categoria": "string (nome completo da estratégia, ex: Simplificação Lexical)"
    }
  ]
}
## 5. Diretrizes de Implementação

Limpeza: Ao extrair texto_alvo_limpo, remova todas as ocorrências de [TAG+ ...], mantendo a pontuação e espaçamento corretos.

Alinhamento: O pareamento entre Fonte e Alvo nem sempre é 1:1. Use o conteúdo textual dentro das tags (quando houver citação literal) para fazer a busca difusa (fuzzy match) no Texto Fonte e determinar os IDs corretos.