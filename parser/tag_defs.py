"""Extraction of tag metadata from tab_est.md."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

# Regex to capture lines like "### 2.1 Reformulação (RF+)"
_HEADING_RE = re.compile(r"^###\s+.*?\(([A-Z]{2,4}\+)\)")
_LEVEL_HINTS = {
    "RF+": "discurso",
    "SL+": "lexical",
    "OM+": "discurso",
    "RP+": "frase",
    "RD+": "discurso",
    "MOD+": "frase",
    "DL+": "lexical",
    "EXP+": "frase",
    "IN+": "frase",
    "MT+": "titulo",
    "PRO+": "discurso",
}


def load_tag_definitions(path: Path) -> Dict[str, Dict[str, str]]:
    """Parse `tab_est.md` and return tag metadata.

    The parser looks for Markdown headings that mention the tag code in
    parentheses. This is enough to retrieve a human-friendly name and a
    coarse level (lexical, frase, discurso, titulo). If the document cannot
    be parsed, a minimal fallback entry is returned so the CLI keeps working.
    """

    if not path.exists():
        return {}

    content = path.read_text(encoding="utf-8")
    tag_definitions: Dict[str, Dict[str, str]] = {}

    for line in content.splitlines():
        match = _HEADING_RE.match(line.strip())
        if not match:
            continue
        tag = match.group(1)
        # Extract the human readable name before the parenthesis
        name = line.split("(")[0].replace("###", "").strip()
        tag_definitions[tag] = {
            "nome": name,
            "tipo_nivel": _LEVEL_HINTS.get(tag, "desconhecido"),
        }

    return tag_definitions
