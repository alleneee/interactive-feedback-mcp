"""Utility helper functions extracted from legacy *feedback_ui.py*.

They are intentionally **LLM-simplified** replicas of the original logic, keeping
behaviour close enough for day-one migration. Future refactors can gradually
improve coverage & testability.
"""
from __future__ import annotations

import html
import json
import re
from typing import Final

__all__ = [
    "preprocess_text",
    "is_markdown",
    "convert_text_to_html",
    "convert_markdown_to_html",
]


_ESCAPE_REPLACEMENTS: Final[dict[str, str]] = {
    "\\n": "\n",
    "\\t": "\t",
    "\\r": "\r",
    "\\\\": "\\",
}


# ---------------------------------------------------------------------------
# Basic text pre-processing (deal with double-escaped sequences from JSON / CLI)
# ---------------------------------------------------------------------------

def preprocess_text(text: str) -> str:
    """Best-effort clean-up of incoming *text* before further processing."""
    if not isinstance(text, str):
        return text  # type: ignore[return-value]

    # Try JSON decode first – handles strings like '"line\nline"'
    try:
        decoded = json.loads(text)
        if isinstance(decoded, str):
            text = decoded
    except Exception:  # noqa: BLE001 – permissive by design
        pass

    # Replace common escape sequences
    for src, dst in _ESCAPE_REPLACEMENTS.items():
        text = text.replace(src, dst)

    # Normalise newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


# ---------------------------------------------------------------------------
# Markdown detection helpers (heuristic)
# ---------------------------------------------------------------------------

_MD_PATTERNS: Final[list[str]] = [
    r"^#{1,6}\s+.+",  # headings
    r"\*\*.+?\*\*",  # bold
    r"\*.+?\*",  # italic *text*
    r"_.+?_",  # italic _text_
    r"`[^`]+`",  # inline code
    r"^\s*```",  # fenced code block
    r"^\s*>",  # blockquote
    r"^\s*[-*+]\s+",  # unordered list
    r"^\s*\d+\.\s+",  # ordered list
]


def is_markdown(text: str) -> bool:
    """Heuristic check if *text* likely contains Markdown."""
    text = preprocess_text(text)
    if not text.strip():
        return False

    lines = text.split("\n")
    features = 0
    for line in lines:
        for pat in _MD_PATTERNS:
            if re.search(pat, line):
                features += 1
                break
    return features >= 2 or (features and features / len(lines) > 0.1)


# ---------------------------------------------------------------------------
# HTML conversion helpers
# ---------------------------------------------------------------------------

def convert_text_to_html(text: str) -> str:
    """Escape *text* → minimal HTML preserving newlines."""
    text = preprocess_text(text)
    escaped = html.escape(text)
    return escaped.replace("\n", "<br>")


def convert_markdown_to_html(markdown_text: str) -> str:  # noqa: D401 – descriptive
    """Convert *markdown_text* to HTML with *markdown* library if available."""
    markdown_text = preprocess_text(markdown_text)
    try:
        import markdown  # heavyweight import guarded

        html_out = markdown.markdown(
            markdown_text,
            extensions=["extra", "codehilite", "toc"],
        )
        return html_out
    except ModuleNotFoundError:
        # Fallback: plain escape
        return convert_text_to_html(markdown_text)
    except Exception:  # noqa: BLE001 – graceful degradation
        return convert_text_to_html(markdown_text)
