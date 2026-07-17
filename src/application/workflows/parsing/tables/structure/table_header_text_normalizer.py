from __future__ import annotations

import re

from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    normalize_cell,
)

_CONTINUATION_ARTIFACT_PATTERN = re.compile(
    r"""
    (?:
        \(\s*(?:continued|cont['.]?d?)\s*\)
        |
        \[\s*(?:continued|cont['.]?d?)\s*\]
        |
        \b(?:continued|cont['.]?d?)\b
        (?:\s+(?:from|on|to)\s+(?:previous|next)\s+page)?
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)
_TRAILING_SEQUENCE_ARTIFACT_PATTERN = re.compile(
    r"""
    (?:
        [\(\[]\s*\d+\s*(?:of|/)\s*\d+\s*[\)\]]
        |
        \b(?:page|pg|sheet)\s+\d+(?:\s*(?:of|/)\s*\d+)?\b
    )
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)
_DISALLOWED_HEADER_CHAR_PATTERN = re.compile(r"[^\w\s/%.-]")


def normalize_table_header_text(value: str | None) -> str:
    text = normalize_cell(value)
    if not text:
        return ""
    text = text.casefold()
    text = _CONTINUATION_ARTIFACT_PATTERN.sub(" ", text)
    text = _TRAILING_SEQUENCE_ARTIFACT_PATTERN.sub(" ", text)
    text = _DISALLOWED_HEADER_CHAR_PATTERN.sub(" ", text)
    return " ".join(text.split()).strip()
