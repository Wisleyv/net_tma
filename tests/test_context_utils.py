from __future__ import annotations

from validator_app.context_utils import build_highlighted_html


def test_build_highlighted_html_marks_excerpt_when_found() -> None:
    html, has_focus = build_highlighted_html(
        text="Linha de contexto com trecho importante.",
        excerpt="trecho importante",
    )

    assert has_focus is True
    assert "background-color:#fff59d" in html
    assert "<a name=\"focus\"></a>" in html


def test_build_highlighted_html_is_case_insensitive() -> None:
    html, has_focus = build_highlighted_html(
        text="Texto com TRECHO em caixa alta.",
        excerpt="trecho",
    )

    assert has_focus is True
    assert "TRECHO" in html


def test_build_highlighted_html_without_match_returns_plain_context() -> None:
    html, has_focus = build_highlighted_html(
        text="Contexto sem correspondencia direta.",
        excerpt="nao existe",
    )

    assert has_focus is False
    assert "background-color:#fff59d" not in html
    assert "Contexto sem correspondencia direta." in html


def test_build_highlighted_html_handles_empty_context() -> None:
    html, has_focus = build_highlighted_html(text="", excerpt="algo")

    assert has_focus is False
    assert "Sem contexto disponivel." in html
