"""Entry point for `python -m validator_app`."""

from __future__ import annotations

import argparse
from pathlib import Path

from .data_loader import load_dataset
from .view import run


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Interface para revisar dataset_raw.json"
    )
    parser.add_argument(
        "--dataset",
        dest="dataset_path",
        type=Path,
        default=None,
        help="Caminho para o arquivo JSON (padrao: dataset_raw.json)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Carrega o dataset e imprime um resumo (sem abrir UI)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.headless:
        metadata, samples = load_dataset(args.dataset_path)
        print(
            "Projeto: {proj} | Amostras carregadas: {count}".format(
                proj=metadata.projeto,
                count=len(samples),
            )
        )
        return

    run(dataset_path=args.dataset_path)


if __name__ == "__main__":  # pragma: no cover
    main()
