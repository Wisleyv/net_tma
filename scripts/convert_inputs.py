"""Utility script to convert DOCX/PDF sources into Markdown/TXT for the parser."""

from __future__ import annotations

import argparse
from pathlib import Path
from shutil import copy2

# Placeholder imports for future integration:
# from docx import Document
# import pdfplumber


def _copy_if_needed(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    copy2(source, destination)


def convert_docx(source_docx: Path, output_txt: Path) -> None:
    """Stub conversion: currently just copies placeholder files."""
    # TODO: integrate python-docx to extract paragraphs/headings.
    _copy_if_needed(source_docx, output_txt)


def convert_pdf(source_pdf: Path, output_txt: Path) -> None:
    """Stub conversion for PDF sources."""
    # TODO: integrate pdfplumber or external CLI (pdftotext) for robust extraction.
    _copy_if_needed(source_pdf, output_txt)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert DOCX/PDF inputs into normalized Markdown/TXT files."
    )
    parser.add_argument(
        "--docx",
        type=Path,
        nargs="?",
        help="Path to DOCX file to convert (e.g., patriotismo_st.docx)",
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        nargs="?",
        help="Path to PDF file to convert",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output path for converted text (e.g., codebase/patriotismo_st.md)",
    )
    args = parser.parse_args()

    if args.docx:
        convert_docx(args.docx, args.output)
    elif args.pdf:
        convert_pdf(args.pdf, args.output)
    else:
        parser.error("You must provide either --docx or --pdf.")


if __name__ == "__main__":
    main()
