# VAEST .exe Step-by-Step Guide

Date: 2026-04-06
Audience: analysts and reviewers using the Windows executable

## 1) Before You Start

You need:
- `vaest.exe`
- `dataset_raw.json` (or another dataset JSON)
- Optional: `tab_est.md`, source text `.md`, target text `.md`

Recommended folder layout:

```text
VAEST/
  vaest.exe
  dataset_raw.json
  README_VAEST.txt
```

## 2) Launch VAEST

1. Double-click `vaest.exe`.
2. If a dataset is in the same folder, VAEST loads it automatically.
3. If not, use `Arquivo -> Abrir dataset...`.

## 3) Understand the Interface

VAEST has three main regions:

1. Left panel (sample list)
- Shows annotation rows.
- Colors:
  - white: pending
  - orange: validated with low confidence
  - green: validated

2. Center panel (source/target context)
- Shows source and target context side-by-side.
- Highlights mapped snippets when available.

3. Right panel (details and actions)
- Annotation context, target snippet, source snippet.
- Review controls and history.
- Action buttons: `Voltar`, `Alterar TAG`, `Validar`, `Proximo`.

## 4) Basic Review Workflow

1. Filter first:
- Use `Status -> Necessita revisar` to review uncertain rows first.

2. Inspect evidence:
- Read context, source snippet, and target snippet.

3. Apply review decision:
- Toggle `Baixo nivel de confianca` when needed.
- Add notes in `Notas / Motivo da revisao`.
- Fill reviewer initials in `Revisor`.
- Use `Validar` when decision is complete.

4. Navigate:
- Use `Voltar` and `Proximo` for sequential review.

5. If a tag must change:
- Click `Alterar TAG`.
- Select the correct tag.
- VAEST logs the change in history.

## 5) Save and Export

1. Save canonical JSON:
- Click `Salvar...` or `Arquivo -> Salvar como...`.

2. Export human-readable report (optional):
- `Arquivo -> Exportar revisao (Markdown)...`
- `Arquivo -> Exportar revisao (TXT)...`

Recommendation:
- Keep JSON as source of truth.
- Use Markdown/TXT for sharing and review meetings.

## 6) Optional Tools Menu Actions

Under `Ferramentas`:
- `Gerenciar Arquivo de Tags...`
- `Associar Texto Fonte...`
- `Associar Texto Alvo...`
- `Importar Documento (DOCX/PDF)...`
- `Executar Parser...`

These actions support continuity and reduce repeated file prompts.

## 7) Troubleshooting

1. Build script reports access denied on `dist/vaest.exe`
- Cause: app still running.
- Fix: close VAEST and rerun build.

2. VAEST does not open a dataset
- Use `Arquivo -> Abrir dataset...` and choose JSON manually.

3. Interface seems blank after open
- Select a row in the left panel to load details/context.

4. Need a quick headless smoke test
- From repository root:

```powershell
$env:QT_QPA_PLATFORM='offscreen'; .\dist\vaest.exe --dataset dataset_raw.json
```

Expected result: exit code `0`.
