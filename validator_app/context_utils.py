"""Helpers to render contextual text with optional excerpt highlighting."""

from __future__ import annotations

import html


EMPTY_CONTEXT_HTML = (
    "<p style=\"color:#666;font-style:italic;\">"
    "Sem contexto disponivel."
    "</p>"
)


def build_highlighted_html(
    text: str | None,
    excerpt: str | None,
) -> tuple[str, bool]:
    """Return HTML for a read-only context box with optional highlight.

    Returns a tuple ``(html, has_focus_anchor)``. When ``has_focus_anchor`` is
    True, the HTML includes a ``focus`` anchor that callers can scroll to.
    """

    body = text or ""
    if not body.strip():
        return EMPTY_CONTEXT_HTML, False

    snippet = (excerpt or "").strip()
    if snippet:
        start = body.casefold().find(snippet.casefold())
        if start >= 0:
            end = start + len(snippet)
            before = html.escape(body[:start])
            hit = html.escape(body[start:end])
            after = html.escape(body[end:])
            rendered = (
                "<div style=\"white-space: pre-wrap;\">"
                f"{before}<a name=\"focus\"></a>"
                f"<span style=\"background-color:#fff59d;\">{hit}</span>"
                f"{after}"
                "</div>"
            )
            return rendered, True

    rendered = (
        "<div style=\"white-space: pre-wrap;\">"
        f"{html.escape(body)}"
        "</div>"
    )
    return rendered, False
