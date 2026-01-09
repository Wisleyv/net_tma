"""Conversor de entrada (DOCX/PDF/TXT) para texto/Markdown compatível com o parser.

Regras principais:
- Mensagens de erro em português (pt-BR) para UX consistente.
- Saída normalizada: UTF-8, parágrafos separados por linha em branco, pronta para segmentação.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


class ConversionError(Exception):
    """Erros previsíveis durante conversão de arquivos."""


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def _join_paragraphs(parts: Iterable[str]) -> str:
    cleaned = [p.strip() for p in parts if p and p.strip()]
    return "\n\n".join(cleaned)


def _paragraphs_from_lines(lines: Iterable[str]) -> list[str]:
    paragraphs: list[str] = []
    buffer: list[str] = []
    for line in lines:
        if not line.strip():
            if buffer:
                paragraphs.append(" ".join(buffer))
                buffer = []
            continue
        buffer.append(line.strip())
    if buffer:
        paragraphs.append(" ".join(buffer))
    return paragraphs


def _read_txt(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="cp1252")
        except UnicodeDecodeError as exc:
            raise ConversionError(
                "Erro ao ler TXT: codificação não suportada (tente UTF-8 ou CP1252)."
            ) from exc


def convert_txt(source_txt: Path) -> str:
    if not source_txt.exists():
        raise ConversionError("Arquivo TXT não encontrado.")
    content = _normalize_newlines(_read_txt(source_txt))
    if not content:
        raise ConversionError("Arquivo TXT está vazio.")
    return content


def convert_docx(source_docx: Path) -> str:
    try:
        from docx import Document  # type: ignore
    except Exception as exc:  # pragma: no cover - import failure is clear to users
        raise ConversionError("Dependência ausente: instale python-docx.") from exc

    if not source_docx.exists():
        raise ConversionError("Arquivo DOCX não encontrado.")

    try:
        document = Document(source_docx)
    except Exception as exc:
        raise ConversionError("Erro ao abrir DOCX (arquivo corrompido ou protegido).") from exc

    paragraphs = [p.text for p in document.paragraphs if p.text and p.text.strip()]
    if not paragraphs:
        raise ConversionError("Arquivo DOCX vazio ou sem texto extraível.")

    return _join_paragraphs(paragraphs)


def convert_pdf(source_pdf: Path) -> str:
    try:
        import pdfplumber  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise ConversionError("Dependência ausente: instale pdfplumber.") from exc

    if not source_pdf.exists():
        raise ConversionError("Arquivo PDF não encontrado.")

    try:
        with pdfplumber.open(source_pdf) as pdf:
            if getattr(pdf, "is_encrypted", False):
                raise ConversionError("Arquivo PDF está criptografado. Desbloqueie antes de importar.")

            paragraphs: list[str] = []
            for page in pdf.pages:
                text = page.extract_text() or ""
                if not text.strip():
                    continue
                lines = _normalize_newlines(text).split("\n")
                paragraphs.extend(_paragraphs_from_lines(lines))

    except ConversionError:
        raise
    except Exception as exc:
        raise ConversionError("Erro ao ler PDF (formato não suportado ou arquivo corrompido).") from exc

    paragraphs = [p for p in paragraphs if p.strip()]
    if not paragraphs:
        raise ConversionError("Arquivo PDF vazio ou sem texto extraível.")

    return _join_paragraphs(paragraphs)


def convert_file(input_path: Path, output_path: Path | None = None) -> str:
    input_path = Path(input_path)
    suffix = input_path.suffix.lower()

    if suffix == ".docx":
        text = convert_docx(input_path)
    elif suffix == ".pdf":
        text = convert_pdf(input_path)
    elif suffix in {".txt", ".md"}:
        text = convert_txt(input_path)
    else:
        raise ConversionError("Formato não suportado. Use PDF, DOCX ou TXT.")

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")

    return text


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Converte DOCX/PDF/TXT para texto normalizado (UTF-8) pronto para o parser."
        )
    )
    parser.add_argument(
        "--docx",
        type=Path,
        help="Caminho para arquivo DOCX (ex.: patriotismo_st.docx)",
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        help="Caminho para arquivo PDF",
    )
    parser.add_argument(
        "--txt",
        type=Path,
        help="Caminho para arquivo TXT/MD",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Saída de texto normalizado (ex.: codebase/patriotismo_st.md)",
    )
    args = parser.parse_args()

    selected = [p for p in [args.docx, args.pdf, args.txt] if p is not None]
    if len(selected) != 1:
        parser.error("Forneça exatamente um arquivo de entrada (DOCX, PDF ou TXT).")

    input_path = selected[0]

    try:
        convert_file(input_path, args.output)
    except ConversionError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
