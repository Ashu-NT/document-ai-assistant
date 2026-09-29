from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
)


class DegradedTablePlainTextRenderer:
    """Renders a table's already-extracted cell text as plain paragraphs,
    with NO Markdown table syntax at all - no header/separator row, no "|"
    used as column punctuation.

    Used only for tables where `GenericRecordStructureSummarizer` (and
    every other table-structure summarizer) already agrees there are too
    few rows to express as a real row/column structure (see
    `TableFragmentBuilder._has_too_few_rows_for_structure`). A degenerate
    Docling table's giant single "row" cells still contain the real,
    meaningful source text - this renders exactly that text, unchanged,
    without ever fabricating rows/columns/headers, and without ever
    emitting a Markdown alignment row (`"| --- | --- |"`) that has no
    header/body distinction to justify it in the first place.
    """

    def render(self, table_rows: list[list[str]] | None) -> str | None:
        if not table_rows:
            return None

        cells = [
            cleaned
            for row in table_rows
            for cell in row
            if (cleaned := clean_chunk_text(cell))
        ]
        if not cells:
            return None

        return "\n\n".join(cells)


__all__ = ["DegradedTablePlainTextRenderer"]
