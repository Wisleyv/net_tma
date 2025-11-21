### Algoritmo Base para Desenvolvimento

Lógica central para o software em desenvolvimento. Ele resolve o problema principal: **como alinhar o texto fonte ao alvo quando os IDs não batem sequencialmente.**

A lógica utiliza as "pistas" deixadas dentro das tags de anotação (ex: o texto original citado dentro de um `[RF+ ...]`) para ancorar o alinhamento.

#### ⚙️ Pseudocódigo / Lógica do Algoritmo

**Fase 1: Ingestão e Indexação**
1.  **Ler Arquivo Fonte**:
    * Utilizar Regex para capturar `\(.*)`.
    * Criar um Dicionário Fonte: `Map<ID_Fonte, String_Texto>`.
2.  **Ler Arquivo Alvo**:
    * Utilizar Regex para capturar `\(.*)`.
    * Criar uma Lista de Objetos Alvo, onde cada objeto contém: `ID_Alvo`, `Texto_Bruto` (com tags).

**Fase 2: Parsing e Alinhamento (O Core da Inteligência)**
Para cada `Segmento_Alvo` na lista:

1.  **Extração de Tags**:
    * Rodar Regex `\[([A-Z]{2,3}\+) (.*?)\]` no `Texto_Bruto`.
    * Para cada match, extrair: `Tipo_Tag` (ex: SL+) e `Conteúdo_Tag` (ex: "palavra antiga").
    * Gerar `Texto_Limpo`: Remover os matches do `Texto_Bruto`.

2.  **Tentativa de Alinhamento (Heurística em Cascata)**:
    * *Passo A (Match Exato de Citação)*: Se houver uma tag que contém texto (ex: `[RF+ texto antigo]`), buscar esse "texto antigo" no Dicionário Fonte.
        * Se encontrar -> **Vínculo Confirmado**. Recuperar o `ID_Fonte`.
    * *Passo B (Similaridade Semântica)*: Se não houver tags com citações (ex: apenas tags de inserção `IN+` ou texto limpo), comparar o `Texto_Limpo` do alvo com os valores do Dicionário Fonte usando uma métrica de similaridade (ex: Jaccard ou Levenshtein).
        * Definir um "Janelamento": Buscar apenas nos IDs próximos ao último ID alinhado (ex: se o anterior alinhou com o 10, buscar entre 10 e 15).
    * *Passo C (Tratamento de Omissão)*: Se a tag for `OM+` (Omissão), verificar se há um "salto" nos IDs do Passo A anterior para o atual. Os IDs pulados no Dicionário Fonte tornam-se o conteúdo da Omissão.

**Fase 3: Montagem do Objeto JSON**
1.  Consolidar os dados alinhados.
2.  Preencher o campo `estrategias` com os dados extraídos na Fase 2.1.
3.  Exportar para JSON.

#### Exemplo prático de lógica de alinhamento (Python-like):

```python
# Exemplo de como a lógica trataria o caso da tag RF+
def find_source_alignment(target_segment, source_dict, last_aligned_id):
    tags = extract_tags(target_segment)
    
    # 1. Tentar ancorar pelo texto citado na tag
    for tag in tags:
        cited_text = tag['content']
        # Busca o texto citado dentro dos valores do source_dict
        match_id = search_text_in_dict(cited_text, source_dict, start_search_at=last_aligned_id)
        if match_id:
            return [match_id] # Alinhamento encontrado via citação explícita
            
    # 2. Se não houver citação, tentar similaridade do texto limpo
    clean_text = remove_tags(target_segment)
    best_match_id = fuzzy_search(clean_text, source_dict, window=5)
    
    return [best_match_id]