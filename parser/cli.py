"""Command-line entry point to generate dataset_raw.json."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from . import alignment, annotations, builder, segmentation, tag_defs
from .annotations import Annotation
from .io_utils import write_json
from .schema import Metadata

BASE_DIR = Path(__file__).resolve().parents[1]

_DEFAULT_TAG_NAMES: Dict[str, Dict[str, str]] = {
    "RF+": {"nome": "Reformulacao", "tipo_nivel": "discurso"},
    "SL+": {"nome": "Simplificacao Lexical", "tipo_nivel": "lexical"},
    "OM+": {"nome": "Omissao", "tipo_nivel": "discurso"},
    "RP+": {"nome": "Reconstrucao de Periodo", "tipo_nivel": "frase"},
    "RD+": {"nome": "Reorganizacao Discursiva", "tipo_nivel": "discurso"},
    "MOD+": {"nome": "Modulacao", "tipo_nivel": "frase"},
    "DL+": {"nome": "Deslocamento Lexical", "tipo_nivel": "lexical"},
    "EXP+": {"nome": "Explicacao", "tipo_nivel": "frase"},
    "IN+": {"nome": "Insercao", "tipo_nivel": "frase"},
    "MT+": {"nome": "Mudanca de Titulo", "tipo_nivel": "titulo"},
    "PRO+": {"nome": "Problema", "tipo_nivel": "discurso"},
}


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera dataset_raw.json a partir dos textos anotados."
    )
    parser.add_argument(
        "--source",
        dest="source_path",
        type=Path,
        default=BASE_DIR / "patriotismo_st.md",
        help="Caminho para o texto fonte (patriotismo_st.md)",
    )
    parser.add_argument(
        "--target",
        dest="target_path",
        type=Path,
        default=BASE_DIR / "patriotismo_tt.md",
        help="Caminho para o texto alvo anotado (patriotismo_tt.md)",
    )
    parser.add_argument(
        "--tags",
        dest="tags_path",
        type=Path,
        default=BASE_DIR / "tab_est.md",
        help="Caminho para o documento de referencia das tags (tab_est.md)",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        type=Path,
        default=BASE_DIR / "dataset_raw.json",
        help="Arquivo de saída (JSON)",
    )
    return parser


def _load_tag_definitions(tags_path: Path) -> Dict[str, Dict[str, str]]:
    """Load tag definitions from `tab_est.md` with graceful fallback."""

    parsed = tag_defs.load_tag_definitions(tags_path)
    if parsed:
        return parsed
    return _DEFAULT_TAG_NAMES


def main(
    source_path: Path | str | None = None,
    target_path: Path | str | None = None,
    tags_path: Path | str | None = None,
    output_path: Path | str | None = None,
) -> None:
    """Generate `dataset_raw.json` by orchestrating all parser modules."""

    if (
        source_path is None
        or target_path is None
        or tags_path is None
        or output_path is None
    ):
        args = _build_argument_parser().parse_args()
        source_path = args.source_path
        target_path = args.target_path
        tags_path = args.tags_path
        output_path = args.output_path

    assert source_path is not None
    assert target_path is not None
    assert tags_path is not None
    assert output_path is not None

    source_path = Path(source_path)
    target_path = Path(target_path)
    tags_path = Path(tags_path)
    output_path = Path(output_path)

    source_paragraphs = segmentation.segment_source(str(source_path))
    target_paragraphs = segmentation.segment_target(str(target_path))

    target_clean = annotations.clean_all(target_paragraphs)
    extracted_annotations = annotations.extract_annotations(target_paragraphs)

    annotations_by_paragraph: Dict[str, List[Annotation]] = defaultdict(list)
    for item in extracted_annotations:
        annotations_by_paragraph[item["paragrafo_alvo_id"]].append(item)

    source_sections = alignment.detect_sections(source_paragraphs)
    target_sections = alignment.detect_sections(target_paragraphs)
    alignment_info = alignment.align_paragraphs(
        source_sections=source_sections,
        target_sections=target_sections,
        source_paragraphs=source_paragraphs,
        target_clean=target_clean,
        annotations_map=annotations_by_paragraph,
    )

    tag_definitions = _load_tag_definitions(tags_path)

    samples = builder.build_samples(
        annotations=[dict(item) for item in extracted_annotations],
        target_clean=target_clean,
        alignment=alignment_info,
        tag_definitions=tag_definitions,
        source_paragraphs=source_paragraphs,
    )

    metadata = Metadata()
    payload = {
        "metadata": metadata.to_dict(),
        "amostras": [sample.to_dict() for sample in samples],
    }

    write_json(output_path, payload)


if __name__ == "__main__":
    main()
