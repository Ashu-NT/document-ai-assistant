from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from src.shared.text.text_preview import truncate_at_word_boundary


@dataclass(slots=True, frozen=True)
class AsciiTableColumn:
    key: str
    title: str
    max_width: int = 32


def render_ascii_table(
    columns: Sequence[AsciiTableColumn],
    rows: Sequence[Mapping[str, object]],
) -> str:
    if not columns:
        return ""

    prepared_rows = [
        [_normalize_cell(row.get(column.key), column.max_width) for column in columns]
        for row in rows
    ]
    widths = _column_widths(columns, prepared_rows)
    separator = _separator(widths)
    rendered = [
        separator,
        _render_row([column.title for column in columns], widths),
        separator,
    ]
    if prepared_rows:
        rendered.extend(_render_row(row, widths) for row in prepared_rows)
    else:
        rendered.append(_render_row(["-" for _ in columns], widths))
    rendered.append(separator)
    return "\n".join(rendered)


def _normalize_cell(value: object, max_width: int) -> str:
    text = " ".join(str(value or "").split())
    if not text:
        return "-"
    if max_width <= 0 or len(text) <= max_width:
        return text
    return f"{truncate_at_word_boundary(text, max_width - 3)}..."


def _column_widths(
    columns: Sequence[AsciiTableColumn],
    prepared_rows: Sequence[Sequence[str]],
) -> list[int]:
    widths: list[int] = []
    for index, column in enumerate(columns):
        cell_width = max((len(row[index]) for row in prepared_rows), default=0)
        widths.append(max(len(column.title), cell_width))
    return widths


def _separator(widths: Sequence[int]) -> str:
    return "+" + "+".join("-" * (width + 2) for width in widths) + "+"


def _render_row(values: Sequence[str], widths: Sequence[int]) -> str:
    cells = [f" {value.ljust(width)} " for value, width in zip(values, widths, strict=True)]
    return "|" + "|".join(cells) + "|"
