# Guia Passo a Passo: Da Conversão ao Dataset Final

Este guia orienta você desde a preparação dos arquivos de entrada (PDF/DOCX) até a validação e exportação do dataset final usando o sistema NET_TMA. É voltado para analistas, linguistas e pesquisadores sem conhecimento técnico avançado.

---

## Sumário

1. [Visão Geral do Fluxo de Trabalho](#visão-geral-do-fluxo-de-trabalho)
2. [Pré-requisitos](#pré-requisitos)
3. [Etapa 1: Preparação dos Arquivos de Entrada](#etapa-1-preparação-dos-arquivos-de-entrada)
4. [Etapa 2: Conversão de PDF/DOCX para Markdown](#etapa-2-conversão-de-pdfdocx-para-markdown)
5. [Etapa 3: Anotação do Texto Alvo](#etapa-3-anotação-do-texto-alvo)
6. [Etapa 4: Execução do Parser](#etapa-4-execução-do-parser)
7. [Etapa 5: Validação com VAEST](#etapa-5-validação-com-vaest)
8. [Etapa 6: Exportação do Dataset Final](#etapa-6-exportação-do-dataset-final)
9. [Solução de Problemas](#solução-de-problemas)
10. [Recursos Adicionais](#recursos-adicionais)

---

## Visão Geral do Fluxo de Trabalho

O sistema NET_TMA processa pares de textos (fonte e alvo) para gerar datasets anotados de simplificação textual. O fluxo completo é:

```
[PDF/DOCX] → [Markdown] → [Anotação Manual] → [Parser] → [dataset_raw.json] → [VAEST] → [dataset_reviewed.json]
```

1. **Conversão**: Transformar arquivos PDF/DOCX em Markdown estruturado.
2. **Anotação**: Marcar estratégias de simplificação no texto alvo usando tags padronizadas.
3. **Parsing**: Extrair automaticamente as anotações e alinhar com o texto fonte.
4. **Validação**: Revisar e corrigir alinhamentos usando a interface gráfica VAEST.
5. **Exportação**: Gerar o dataset final validado.

---

## Pré-requisitos

### Para Usuários do Executável VAEST (Recomendado)
- **Sistema Operacional**: Windows 10 ou superior
- **Executável VAEST**: Baixe a pasta `dist/` do repositório (contém `vaest.exe`)
- **Editor de Texto**: Qualquer editor Markdown (VS Code, Notepad++, Typora, etc.)

### Para Usuários macOS
- **Sistema Operacional**: macOS 10.15 (Catalina) ou superior
- **Aplicativo VAEST**: Baixe a pasta `dist/` do repositório (contém `vaest.app`)
- **Editor de Texto**: TextEdit, VS Code, ou qualquer editor Markdown
- **Permissões**: Pode ser necessário autorizar o app em Preferências do Sistema → Segurança e Privacidade

### Para Desenvolvedores (Opcional)
- **Python 3.12+**
- **Dependências**: Instale com `pip install -r requirements.txt`
- **Git**: Para clonar o repositório

---

## Etapa 1: Preparação dos Arquivos de Entrada

Você precisa de **três arquivos** para processar um par de textos:

### 1.1 Texto Fonte (Original/Complexo)
- **Formato inicial**: PDF, DOCX ou Markdown
- **Conteúdo**: Texto original sem anotações, segmentado em parágrafos
- **Nomenclatura sugerida**: `<nome_projeto>_st.md` (source text)

**Exemplo de estrutura esperada:**
```markdown
# Título do Documento

## Seção 1

(01) Este é o primeiro parágrafo do texto original. Ele contém termos técnicos e estruturas complexas que serão simplificadas.

(02) Segundo parágrafo com informações detalhadas sobre o tema.

## Seção 2

(03) Continuação do texto em outra seção.
```

**Importante:**
- Cada parágrafo deve ser identificado com um número entre parênteses: `(01)`, `(02)`, etc.
- Headings (títulos) devem usar a sintaxe Markdown: `#`, `##`, `###`
- Mantenha a numeração sequencial para facilitar o alinhamento

### 1.2 Texto Alvo (Simplificado/Anotado)
- **Formato inicial**: PDF, DOCX ou Markdown
- **Conteúdo**: Texto simplificado **com anotações inline** das estratégias aplicadas
- **Nomenclatura sugerida**: `<nome_projeto>_tt.md` (target text)

**Exemplo de estrutura esperada:**
```markdown
# Título do Documento

## Seção 1

(01) Este é o primeiro parágrafo [SL+ simplificado]. Ele contém termos [RF+ foi reescrito com] fáceis e estruturas [SL+ simples].

(02) Segundo parágrafo com informações [OM+ resumidas sobre o tema].
```

**Formato das anotações:**
- Padrão: `[TAG+ conteúdo original ou explicação]`
- `TAG`: Código de 2-3 letras (RF, SL, OM, etc.) — consulte `tab_est.md`
- `+`: Sempre obrigatório
- `conteúdo`: Texto original que foi modificado OU nota explicativa

### 1.3 Arquivo de Definição de Tags
- **Nome fixo**: `tab_est.md`
- **Conteúdo**: Tabela com códigos, nomes e descrições das estratégias de simplificação
- **Localização**: Raiz do projeto (mesmo diretório dos arquivos fonte/alvo)

**Exemplo:**
```markdown
## 2. Estratégias de Simplificação

### 2.1 Reformulação (RF+)
**Descrição:** Expressão da mesma ideia com palavras diferentes...

### 2.2 Simplificação Lexical (SL+)
**Descrição:** Substituição de termos menos frequentes por outros mais comuns...
```

O arquivo `tab_est.md` já está incluído no repositório como modelo. Você pode adaptá-lo conforme seu projeto.

---

## Etapa 2: Conversão de PDF/DOCX para Markdown

Se seus arquivos estão em PDF ou DOCX, você precisa convertê-los para Markdown antes de processar.

### Opção A: Conversão Manual (Recomendado)
Use ferramentas online ou editores especializados:
- **Pandoc** (linha de comando): `pandoc input.docx -o output.md`
- **Word/LibreOffice**: Salvar como texto simples → adicionar formatação Markdown
- **Ferramentas online**: [Pandoc Online](https://pandoc.org/try/), [CloudConvert](https://cloudconvert.com/)

**Depois de converter:**
1. Abra o arquivo `.md` em um editor de texto
2. Adicione os IDs de parágrafo: `(01)`, `(02)`, etc.
3. Corrija a formatação de headings: `#`, `##`, `###`
4. Revise o texto para garantir que a estrutura está correta

### Opção B: Script de Conversão (Placeholder)
O repositório inclui um script auxiliar em `scripts/convert_inputs.py`, mas ele ainda é um **placeholder**. Para usá-lo no futuro:

```bash
python scripts/convert_inputs.py --docx meu_arquivo.docx --output codebase/meu_projeto_st.md
```

**Nota:** Atualmente, o script apenas copia os arquivos. A conversão real de DOCX/PDF para Markdown estruturado precisa ser implementada (contribuições são bem-vindas!).

---

## Etapa 3: Anotação do Texto Alvo

Agora você precisa **anotar manualmente** o texto alvo com as tags de simplificação.

### 3.1 Entendendo as Tags

Consulte o arquivo `tab_est.md` para a lista completa. As principais são:

| Código | Nome | Uso |
|--------|------|-----|
| `RF+` | Reformulação | Reescrita mantendo o sentido |
| `SL+` | Simplificação Lexical | Substituição de termo complexo por simples |
| `OM+` | Omissão | Remoção de informação |
| `RP+` | Reconstrução de Período | Reestruturação de frases |
| `RD+` | Reorganização Discursiva | Mudança na ordem das ideias |
| `IN+` | Inserção | Adição de novo conteúdo |
| `EXP+` | Explicação | Esclarecimento de conceito |
| `MOD+` | Modulação | Mudança de perspectiva |

### 3.2 Como Anotar

**Regra geral**: Coloque a tag **onde a mudança ocorreu** no texto alvo. O conteúdo dentro dos colchetes deve ser o **texto original** (do fonte) que foi modificado.

**Exemplos:**

1. **Simplificação Lexical:**
   - Fonte: "...por forças políticas e ideologias muito **díspares**..."
   - Alvo: "...por forças políticas e ideologias muito **diferentes** `[SL+ díspares]`..."

2. **Reformulação:**
   - Fonte: "...inúmeras vozes e movimentos políticos **recorreram ao ideário do** patriotismo..."
   - Alvo: "...várias pessoas e grupos políticos **se voltaram para o** `[RF+ inúmeras vozes e movimentos políticos recorreram ao ideário do]` patriotismo..."

3. **Omissão:**
   - Fonte: "...texto com detalhes adicionais que foram removidos..."
   - Alvo: "...texto `[OM+ com detalhes adicionais que foram removidos]`..."

4. **Inserção:**
   - Fonte: (não existe no original)
   - Alvo: "...texto novo `[IN+]` que esclarece o conceito..."

### 3.3 Dicas Práticas

- **Seja consistente**: Use sempre o mesmo padrão de anotação
- **Não anote demais**: Foque nas mudanças significativas
- **Teste incrementalmente**: Processe arquivos menores primeiro para validar sua anotação
- **Revise o original**: Compare os parágrafos lado a lado antes de anotar

---

## Etapa 4: Execução do Parser

O parser extrai as anotações e gera o arquivo `dataset_raw.json`.

### 4.1 Preparação

Certifique-se de que você tem os três arquivos na mesma pasta:
```
meu_projeto/
├── meu_projeto_st.md    # Texto fonte
├── meu_projeto_tt.md    # Texto alvo anotado
└── tab_est.md           # Definições das tags
```

### 4.2 Executando via Python (se instalado)

Abra um terminal/prompt de comando e navegue até a pasta do projeto:

```bash
cd caminho/para/net_tma/codebase
python -m parser.cli --source meu_projeto_st.md --target meu_projeto_tt.md --tags tab_est.md --output meu_dataset_raw.json
```

**Parâmetros:**
- `--source`: Caminho para o texto fonte
- `--target`: Caminho para o texto alvo anotado
- `--tags`: Caminho para o arquivo de tags (geralmente `tab_est.md`)
- `--output`: Nome do arquivo de saída (padrão: `dataset_raw.json`)

### 4.3 Resultado

O parser gera um arquivo JSON estruturado:
```json
{
  "metadata": {
    "projeto": "NET_TMA",
    "versao": "1.0",
    "idioma": "pt-BR",
    "descricao": "Dataset anotado para simplificação textual intralingual"
  },
  "amostras": [
    {
      "id": "st-001",
      "tag": "SL",
      "nome": "Simplificacao Lexical",
      "contexto_anotacao": "díspares",
      "paragrafo_alvo_id": "tt-005",
      "paragrafo_fonte_ids": ["st-007"],
      "texto_paragrafo_alvo": "...texto limpo sem tags...",
      "texto_paragrafo_fonte": "...texto original correspondente...",
      "trecho_alvo": "diferentes",
      "trecho_fonte": "díspares",
      "necessita_revisao_humana": false
    }
  ]
}
```

### 4.4 Verificação Rápida

Abra o arquivo JSON em um editor de texto ou visualizador JSON. Verifique:
- ✅ O número de amostras corresponde ao número de tags anotadas?
- ✅ Os campos `texto_paragrafo_fonte` e `texto_paragrafo_alvo` estão preenchidos?
- ✅ O campo `necessita_revisao_humana` está marcado corretamente?

Se encontrar problemas, consulte a seção [Solução de Problemas](#solução-de-problemas).

---

## Etapa 5: Validação com VAEST

VAEST (Validador de Anotações sobre Estratégias de Simplificação Textual) é uma interface gráfica para revisar e corrigir o dataset gerado.

### 5.1 Iniciando o VAEST

#### Opção A: Executável Windows (Recomendado para não-desenvolvedores)

1. Navegue até a pasta `dist/` que você baixou
2. **Copie** o arquivo `dataset_raw.json` (gerado na Etapa 4) para dentro da pasta `dist/`
3. **Dê um duplo clique** em `vaest.exe`

O programa abre automaticamente carregando o `dataset_raw.json` da mesma pasta.

#### Opção A (macOS): Executável macOS (Recomendado para não-desenvolvedores)

1. Navegue até a pasta `dist/` que você baixou
2. **Copie** o arquivo `dataset_raw.json` (gerado na Etapa 4) para dentro da pasta `dist/`
3. **Clique com o botão direito** em `vaest.app` e selecione **Abrir**
   - Na primeira execução, o macOS pode exibir um aviso de segurança
   - Vá em **Preferências do Sistema → Segurança e Privacidade**
   - Clique em **Abrir Mesmo Assim** ou **Open Anyway**
4. Em execuções futuras, basta dar duplo clique em `vaest.app`

O programa abre automaticamente carregando o `dataset_raw.json` da mesma pasta.

**Nota para macOS:** Se você mover o `vaest.app` para outra pasta, copie também o `dataset_raw.json` e `README_VAEST.txt` para a nova localização.

#### Opção B: Via Python (para desenvolvedores)

```bash
cd caminho/para/net_tma/codebase
python -m validator_app --dataset dataset_raw.json
```

### 5.2 Interface do VAEST

A janela principal está dividida em duas áreas:

**Painel Esquerdo (Lista de Amostras):**
- Mostra todas as anotações extraídas
- Cada item exibe: `ID | TAG | STATUS | Revisor`
- Status: `OK` (verde) ou `REVISAR` (vermelho)

**Painel Direito (Detalhes da Amostra):**
- **Contexto da Anotação**: Texto ou explicação original da tag
- **Trecho Alvo**: Fragmento simplificado
- **Trecho Fonte**: Fragmento original correspondente
- **Checkbox "Necessita revisão humana"**: Marque se houver problema
- **Campo "Notas"**: Adicione observações sobre a amostra
- **Campo "Revisor"**: Suas iniciais ou nome
- **Histórico**: Log de todas as alterações feitas na amostra

**Barra de Ferramentas (Topo):**
- **Filtro por Tag**: Mostra apenas anotações de um tipo específico
- **Filtro por Status**: `Todos` | `Somente OK` | `Necessita revisar`
- **Campo de Busca**: Pesquisa por palavras no contexto/alvo/fonte
- **Botões**: `Recarregar` | `Salvar...`

### 5.3 Fluxo de Revisão Recomendado

1. **Filtre por status "Necessita revisar"**
   - O parser marca automaticamente amostras com baixa confiança de alinhamento
   - Revise essas primeiro

2. **Para cada amostra problemática:**
   - Leia o **Contexto da Anotação**, **Trecho Fonte** e **Trecho Alvo**
   - Verifique se o alinhamento fonte ↔ alvo está correto
   - Se estiver correto: desmarque "Necessita revisão humana"
   - Se estiver errado: adicione uma nota explicativa e mantenha marcado

3. **Adicione suas iniciais no campo "Revisor"**
   - Isso registra quem validou a amostra
   - Útil para rastrear o trabalho em equipe

4. **Revise amostras marcadas como "OK"** (opcional)
   - Use os filtros de tag para focar em tipos específicos
   - Busque padrões de erro com a caixa de pesquisa

5. **Salve incrementalmente**
   - Use `Arquivo → Salvar como...` periodicamente
   - Nomeie como `dataset_reviewed_parcial.json` durante o trabalho

### 5.4 Recursos de Auditoria

O VAEST registra automaticamente:
- **Timestamp**: Data/hora de cada edição
- **Revisor**: Iniciais da pessoa que fez a alteração
- **Ação**: Tipo de mudança (e.g., "Status de revisão", "Notas atualizadas")
- **Notas**: Comentários adicionados

Esse histórico aparece no painel **Histórico** e é salvo no campo `history` do JSON final.

---

## Etapa 6: Exportação do Dataset Final

Após revisar todas as amostras (ou pelo menos as críticas), exporte o dataset validado.

### 6.1 Salvando no VAEST

1. Clique em **Salvar...** (ou `Arquivo → Salvar como...`)
2. Escolha um nome: `dataset_reviewed.json` ou `<nome_projeto>_final.json`
3. Selecione o diretório de destino
4. Clique em **Salvar**

### 6.2 Estrutura do Dataset Final

O arquivo exportado mantém a mesma estrutura do `dataset_raw.json`, mas inclui:
- ✅ Status de revisão atualizado (`necessita_revisao_humana`)
- ✅ Notas adicionadas (`motivo_revisao`)
- ✅ Informações do revisor (`reviewer`, `updated_at`)
- ✅ Histórico completo de alterações (`history`)

**Exemplo de amostra validada:**
```json
{
  "id": "st-042",
  "tag": "RF",
  "nome": "Reformulacao",
  "necessita_revisao_humana": false,
  "motivo_revisao": null,
  "reviewer": "AJS",
  "updated_at": "2025-11-21T14:32:00",
  "history": [
    {
      "timestamp": "2025-11-21T14:30:00",
      "action": "Status de revisao",
      "reviewer": "AJS",
      "notes": null
    },
    {
      "timestamp": "2025-11-21T14:32:00",
      "action": "Revisor atribuido",
      "reviewer": "AJS",
      "notes": null
    }
  ]
}
```

### 6.3 Uso do Dataset

O arquivo JSON final pode ser usado para:
- **Treinamento de modelos NLP**: Detectar automaticamente estratégias de simplificação
- **Análise linguística**: Estudar padrões de simplificação em corpora
- **Métricas de qualidade**: Avaliar sistemas automáticos de simplificação
- **Criação de recursos lexicais**: Dicionários de termos simplificados

---

## Solução de Problemas

### Problema: Parser não encontra os arquivos
**Sintoma:** Erro "Nao encontrei o arquivo: ..."

**Solução:**
- Verifique se os caminhos especificados em `--source`, `--target` e `--tags` estão corretos
- Use caminhos absolutos se estiver em dúvida: `C:/caminho/completo/arquivo.md`
- Certifique-se de que os arquivos têm a extensão `.md`

### Problema: JSON gerado está vazio ou incompleto
**Sintoma:** `"amostras": []` ou número muito baixo de amostras

**Solução:**
- Verifique se o texto alvo contém tags no formato correto: `[TAG+ conteúdo]`
- Certifique-se de que há um espaço após o `+`: `[RF+ texto]` (não `[RF+texto]`)
- Revise se os códigos de tag correspondem aos definidos em `tab_est.md`
- Execute o parser com `--help` para ver exemplos

### Problema: Alinhamento fonte/alvo incorreto
**Sintoma:** Parágrafos fonte não correspondem aos parágrafos alvo

**Solução:**
- Verifique se ambos os arquivos (fonte e alvo) têm IDs de parágrafo sequenciais: `(01)`, `(02)`, etc.
- Certifique-se de que as seções (headings) coincidem entre fonte e alvo
- O parser usa heurísticas de alinhamento; alguns casos podem requerer revisão manual no VAEST
- Marque "Necessita revisão humana" para amostras problemáticas e adicione notas explicativas

### Problema: VAEST não abre ou fecha imediatamente
**Sintoma:** Executável não inicia ou janela fecha logo após abrir

**Solução Windows:**
- Verifique se o arquivo `dataset_raw.json` está na mesma pasta que `vaest.exe`
- Abra o Prompt de Comando, navegue até a pasta `dist/` e execute: `vaest.exe --headless --dataset dataset_raw.json`
  - Se aparecer uma mensagem de erro, copie-a e consulte o repositório GitHub para suporte
- Certifique-se de que você tem permissões de execução (antivírus pode bloquear)

**Solução macOS:**
- Verifique se o arquivo `dataset_raw.json` está na mesma pasta que `vaest.app`
- Abra o Terminal, navegue até a pasta `dist/` e execute: `./vaest.app/Contents/MacOS/vaest --headless --dataset dataset_raw.json`
  - Se aparecer uma mensagem de erro, copie-a e consulte o repositório GitHub para suporte
- Certifique-se de que concedeu permissão em **Preferências do Sistema → Segurança e Privacidade**
- Se o macOS bloquear por "desenvolvedor não identificado", clique com botão direito no app → **Abrir** → **Abrir** novamente na confirmação

### Problema: Erro ao salvar no VAEST
**Sintoma:** "Erro ao salvar: [WinError 5] Acesso negado"

**Solução:**
- Escolha um diretório onde você tem permissão de escrita (ex.: Documentos, Desktop)
- Execute o VAEST como Administrador (clique direito → Executar como administrador)
- Verifique se outro programa não está usando o arquivo de destino

---

## Recursos Adicionais

### Documentação Técnica
- **README.md**: Visão geral do projeto e instalação
- **algorithm.md**: Lógica de alinhamento e heurísticas do parser
- **design_notes.md**: Arquitetura do sistema e decisões de design
- **parser_api.md**: Contratos dos módulos do parser
- **docs/packaging.md**: Como recompilar o executável VAEST

### Arquivos de Exemplo
- **patriotismo_st.md**: Texto fonte de amostra (verbete "Patriotismo")
- **patriotismo_tt.md**: Texto alvo anotado de amostra
- **tab_est.md**: Definições completas das tags de simplificação

### Suporte
- **Issues no GitHub**: [https://github.com/Wisleyv/net_tma/issues](https://github.com/Wisleyv/net_tma/issues)
- **Discussões**: Use a aba "Discussions" para tirar dúvidas ou compartilhar experiências

### Contribuindo
Contribuições são bem-vindas! Áreas onde você pode ajudar:
- Implementar conversão robusta de DOCX/PDF para Markdown
- Melhorar heurísticas de alinhamento no parser
- Adicionar mais filtros e visualizações no VAEST
- Criar tutoriais em vídeo ou workshops
- Reportar bugs e sugerir melhorias

---

## Checklist de Validação Final

Antes de considerar seu dataset completo, verifique:

- [ ] Todos os arquivos fonte e alvo foram convertidos para Markdown
- [ ] IDs de parágrafo estão sequenciais e corretos: `(01)`, `(02)`, etc.
- [ ] Todas as estratégias de simplificação foram anotadas no texto alvo
- [ ] Parser executado sem erros e `dataset_raw.json` gerado
- [ ] Todas as amostras marcadas como "Necessita revisão" foram revisadas no VAEST
- [ ] Revisor atribuído para amostras críticas
- [ ] Dataset final exportado como `dataset_reviewed.json`
- [ ] Backup dos arquivos originais e intermediários criado

---

**Última atualização:** 21 de novembro de 2025  
**Versão do guia:** 1.0  
**Repositório:** [https://github.com/Wisleyv/net_tma](https://github.com/Wisleyv/net_tma)
