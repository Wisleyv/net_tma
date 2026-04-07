# Guia Passo a Passo do VAEST (.exe)

Data: 2026-04-06
Público-alvo: analistas e revisores que usam o executável no Windows
Codificação recomendada: UTF-8 (pt-BR)

## 1) Antes de Começar

Você precisa de:
- `vaest.exe`
- `dataset_raw.json` (dataset legado, inclui todas as tags)
- `dataset_curated.json` (dataset canonico v2 com etiquetas automaticas + diagnosticas)
- `dataset_supervised.json` (subset supervisionado com etiquetas elegiveis)
- `tab_est.md` (definicao canonica das tags)
- `sample_source_all_tags.md` + `sample_target_all_tags.md` (par fonte/alvo cobrindo RF+, SL+, IN+, RP+, RD+, MOD+, DL+, EXP+, MT+)

Estrutura de pasta recomendada:

```text
VAEST/
  vaest.exe
  dataset_raw.json
  dataset_curated.json
  dataset_supervised.json
  tab_est.md
  sample_source_all_tags.md
  sample_target_all_tags.md
  README_VAEST.txt
```

## 2) Abrindo o VAEST

1. Dê duplo clique em `vaest.exe`.
2. Se houver um dataset na mesma pasta, o VAEST carrega automaticamente.
3. Caso contrário, use `Arquivo -> Abrir dataset...`.

## 3) Entendendo a Interface

O VAEST tem três áreas principais:

1. Painel esquerdo (lista de amostras)
- Exibe as linhas de anotação.
- Cores:
  - branco: pendente
  - laranja: validado com baixa confiança
  - verde: validado

2. Painel central (contexto fonte/alvo)
- Exibe lado a lado os contextos de fonte e alvo.
- Destaca os trechos mapeados quando disponíveis.

3. Painel direito (detalhes e ações)
- Contexto da anotação, trecho alvo e trecho fonte.
- Controles de revisão e histórico.
- Botões de ação: `Voltar`, `Alterar TAG`, `Validar`, `Proximo`.

## 4) Fluxo Básico de Revisão

1. Filtre primeiro:
- Use `Status -> Necessita revisar` para revisar primeiro as linhas incertas.

2. Inspecione as evidências:
- Leia contexto, trecho fonte e trecho alvo.

3. Aplique a decisão de revisão:
- Marque/desmarque `Baixo nivel de confianca` quando necessário.
- Adicione notas em `Notas / Motivo da revisao`.
- Preencha as iniciais em `Revisor`.
- Use `Validar` quando a decisão estiver concluída.

4. Navegue entre amostras:
- Use `Voltar` e `Proximo` para revisão sequencial.

5. Se precisar trocar a tag:
- Clique em `Alterar TAG`.
- Selecione a tag correta.
- O VAEST registra a mudança no histórico.

## 5) Salvar e Exportar

1. Salvar JSON canônico:
- Clique em `Salvar...` ou `Arquivo -> Salvar como...`.

2. Exportar relatório de leitura humana (opcional):
- `Arquivo -> Exportar revisao (Markdown)...`
- `Arquivo -> Exportar revisao (TXT)...`

Recomendação:
- Mantenha o JSON como fonte da verdade.
- Use Markdown/TXT para compartilhamento e reuniões de revisão.

## 6) Ações Opcionais do Menu Ferramentas

Em `Ferramentas`:
- `Gerenciar Arquivo de Tags...`
- `Associar Texto Fonte...`
- `Associar Texto Alvo...`
- `Importar Documento (DOCX/PDF)...`
- `Executar Parser...`

Essas ações ajudam na continuidade do trabalho e reduzem prompts repetidos de seleção de arquivo.

Dica pratica:
- Use o par `sample_source_all_tags.md` + `sample_target_all_tags.md` para testar rapidamente o fluxo de associacao fonte/alvo com cobertura completa das tags elegiveis.

## 7) Solução de Problemas

1. Script de build reporta acesso negado em `dist/vaest.exe`
- Causa: aplicativo ainda em execução.
- Solução: feche o VAEST e rode o build novamente.

2. VAEST não abre um dataset
- Use `Arquivo -> Abrir dataset...` e selecione o JSON manualmente.

3. Interface parece vazia após abrir
- Selecione uma linha no painel esquerdo para carregar detalhes e contexto.

4. Precisa de um teste rápido em modo headless
- Na raiz do repositório:

```powershell
$env:QT_QPA_PLATFORM='offscreen'; .\dist\vaest.exe --dataset dataset_raw.json
```

Resultado esperado: código de saída `0`.
