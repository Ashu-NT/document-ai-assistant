from __future__ import annotations

from dataclasses import replace as dataclass_replace

from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
)


class TableFragmentSplitter:
    def __init__(self, *, text_splitter: ChunkTextSplitter) -> None:
        self.text_splitter = text_splitter

    def split(self, fragment: ChunkFragment) -> list[ChunkFragment]:
        if not fragment.table_rows or len(fragment.table_rows) <= 1:
            return [fragment]

        header = _clean_row(fragment.table_rows[0])
        body_rows = [
            _clean_row(row)
            for row in fragment.table_rows[1:]
            if any(_clean_row(row))
        ]
        if not body_rows:
            return [fragment]

        groups: list[tuple[int, int, list[list[str]]]] = []
        current_rows: list[list[str]] = []
        current_start = 1

        for row_index, row in enumerate(body_rows, start=1):
            candidate_rows = [*current_rows, row]
            candidate_text = self._render_fragment_text(
                fragment=fragment,
                rows=[header, *candidate_rows],
            )
            if (
                current_rows
                and self.text_splitter.count_tokens(candidate_text)
                > self.text_splitter.max_chunk_tokens
            ):
                groups.append((current_start, row_index - 1, current_rows))
                current_rows = [row]
                current_start = row_index
                continue
            current_rows = candidate_rows

        if current_rows:
            groups.append((current_start, len(body_rows), current_rows))

        if len(groups) == 1:
            start, end, rows = groups[0]
            return [
                dataclass_replace(
                    fragment,
                    table_rows=[header, *rows],
                    table_row_start=start,
                    table_row_end=end,
                )
            ]

        split_fragments: list[ChunkFragment] = []
        total = len(groups)
        for index, (start, end, rows) in enumerate(groups, start=1):
            text = self._render_fragment_text(fragment=fragment, rows=[header, *rows])
            split_fragments.append(
                dataclass_replace(
                    fragment,
                    text=text,
                    token_count=self.text_splitter.count_tokens(text),
                    table_rows=[header, *rows],
                    logical_table_family_index=index,
                    logical_table_family_total=total,
                    logical_table_continuation_role=_continuation_role(index, total),
                    table_row_start=start,
                    table_row_end=end,
                )
            )

        return split_fragments

    @staticmethod
    def _render_fragment_text(
        *,
        fragment: ChunkFragment,
        rows: list[list[str]],
    ) -> str:
        markdown = _rows_to_markdown(rows)
        parts = [part for part in [fragment.table_context, markdown] if part]
        return clean_chunk_text("\n\n".join(parts)) or fragment.text


def _clean_row(row: list[str]) -> list[str]:
    return [" ".join(str(cell or "").split()).strip() for cell in row]


def _rows_to_markdown(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header = rows[0]
    body = rows[1:]
    header_line = "| " + " | ".join(header) + " |"
    separator = "| " + " | ".join("---" for _ in header) + " |"
    body_lines = ["| " + " | ".join(row) + " |" for row in body]
    return "\n".join([header_line, separator, *body_lines] if body_lines else [header_line])


def _continuation_role(index: int, total: int) -> str:
    if total <= 1:
        return "single"
    if index == 1:
        return "start"
    if index == total:
        return "end"
    return "middle"
