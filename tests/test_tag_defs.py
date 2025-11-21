from __future__ import annotations

from parser import tag_defs


def test_load_tag_definitions_from_sample_file(tab_fixture_path):
    definitions = tag_defs.load_tag_definitions(tab_fixture_path)

    assert "SL+" in definitions
    assert definitions["SL+"]["nome"].startswith("###") is False
    assert definitions["SL+"]["tipo_nivel"] == "lexical"
    assert definitions["OM+"]["tipo_nivel"] == "discurso"
