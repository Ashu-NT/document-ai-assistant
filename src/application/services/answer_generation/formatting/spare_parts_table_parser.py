from __future__ import annotations

import re

from src.application.services.answer_generation.formatting.free_form_position_row_parser import (
    row_from_free_form_position_line,
)
from src.application.services.answer_generation.formatting.pid_tag_row_parser import (
    row_from_pid_tag_line,
)
from src.application.services.answer_generation.formatting.position_pair_row_parser import (
    rows_from_position_pairs,
)
from src.application.services.answer_generation.formatting.spare_parts.spare_parts_group import (
    SparePartsGroup,
)
from src.application.services.answer_generation.formatting.spare_parts_table_evidence_detector import (
    TABLE_EVIDENCE_PHRASE,
)
from src.application.services.answer_generation.formatting.structured_grid_row_parser import (
    HEADER_SEPARATOR_PATTERN,
    rows_from_structured_grid,
    split_cells,
    as_structured_header,
    row_from_structured_cells,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
)
from src.application.workflows.shared.table_category import TableCategory

# Bumped whenever a table-layout strategy (structured header, PID/tag row,
# position-pair, free-form) is added, removed, or changed materially --
# mirrors ANSWER_INTENT_RULES_VERSION's convention.
SPARE_PARTS_TABLE_PARSER_RULES_VERSION = "v1"

_MAX_RAW_ROWS_PER_GROUP = 25

_BOILERPLATE_MARKERS = (
    "take note",
    "use of original manufacturer",
    "exempt",
    "nullify liability",
    "authorised by",
)


class SparePartsTableParser:
    """Turns a retrieved chunk's raw text into structured spare-parts rows.

    Dispatches across several unrelated table-layout conventions seen across
    vendor manuals (structured header tables, P&ID/tag-style rows, two-column
    exploded-view position pairs, free-form position/qty/unit/description
    lines) plus an unparseable-content fallback that still surfaces the raw
    line rather than dropping it silently. The individual layout strategies
    live in their own modules; this class decides which strategy applies to
    a given chunk and combines their results into one `SparePartsGroup`.
    """

    @staticmethod
    def section_title(source: AnswerSource) -> str:
        return source.chunk_name or "Spare Parts List"

    def build_group(self, source: AnswerSource) -> SparePartsGroup:
        structured_result = rows_from_structured_grid(source.table_rows)
        if structured_result is not None:
            rows, raw_rows, partial, dropped_row_count = structured_result
        else:
            rows, raw_rows, partial, dropped_row_count = self._extract_rows(source.content)
        return SparePartsGroup(
            section_title=self.section_title(source),
            section_path=source.section_path,
            page_start=source.page_start,
            page_end=source.page_end,
            rows=rows,
            raw_rows=raw_rows[:_MAX_RAW_ROWS_PER_GROUP],
            partial=partial or len(raw_rows) > _MAX_RAW_ROWS_PER_GROUP,
            dropped_row_count=dropped_row_count,
        )

    def build_group_from_answer_table(self, table: AnswerTable) -> SparePartsGroup | None:
        if not self._should_use_answer_table(table):
            return None

        structured_grid = [table.headers, *[row.cells for row in table.rows]]
        structured_result = rows_from_structured_grid(structured_grid)
        if structured_result is not None:
            rows, raw_rows, partial, dropped_row_count = structured_result
        else:
            rows, raw_rows, partial, dropped_row_count = self._extract_rows_from_answer_table(
                table
            )

        if not rows and not raw_rows:
            return None

        return SparePartsGroup(
            section_title=self._table_section_title(table),
            section_path=table.section_path,
            page_start=table.page_start,
            page_end=table.page_end,
            rows=rows,
            raw_rows=raw_rows[:_MAX_RAW_ROWS_PER_GROUP],
            partial=partial or len(raw_rows) > _MAX_RAW_ROWS_PER_GROUP,
            dropped_row_count=dropped_row_count,
        )

    # -- top-level row extraction ------------------------------------------------

    def _extract_rows(
        self,
        content: str,
    ) -> tuple[list[dict[str, str]], list[str], bool, int]:
        header: list[str | None] | None = None
        rows: list[dict[str, str]] = []
        raw_rows: list[str] = []
        dropped_row_count = 0

        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if HEADER_SEPARATOR_PATTERN.match(line):
                continue
            # Not every spare-parts export renders as a pipe-delimited table --
            # some are plain lines of text. Treat a line with no "|" as a
            # single cell so it still flows through the same layout checks.
            cells = split_cells(line) if "|" in line else [line]

            if header is None:
                header_candidate = as_structured_header(cells)
                if header_candidate is not None:
                    header = header_candidate
                    continue

            if header is not None and len(cells) >= 2:
                row = row_from_structured_cells(cells, header)
                if row is not None:
                    rows.append(row)
                else:
                    dropped_row_count += 1
                continue

            # No confidently detected column layout for this chunk (yet) --
            # evaluate each cell independently against the known free-form
            # layout strategies instead of guessing a column mapping.
            for cell in cells:
                self._parse_free_text_blob(cell, rows, raw_rows)

        partial = header is None or dropped_row_count > 0 or bool(raw_rows) or not rows
        return rows, raw_rows, partial, dropped_row_count

    # -- free-form layout dispatch (B, C, A-variant, D) ---------------------------

    def _parse_free_text_blob(
        self,
        cell: str,
        rows: list[dict[str, str]],
        raw_rows: list[str],
    ) -> None:
        text = cell.strip()
        if not text:
            return

        pid_row = row_from_pid_tag_line(text)
        if pid_row is not None:
            rows.append(pid_row)
            return

        pair_rows = rows_from_position_pairs(text)
        if pair_rows:
            rows.extend(pair_rows)
            return

        free_form_row = row_from_free_form_position_line(text)
        if free_form_row is not None:
            rows.append(free_form_row)
            return

        if self._looks_like_content_fragment(text):
            raw_rows.append(text)

    def _extract_rows_from_answer_table(
        self,
        table: AnswerTable,
    ) -> tuple[list[dict[str, str]], list[str], bool, int]:
        rows: list[dict[str, str]] = []
        raw_rows: list[str] = []
        dropped_row_count = 0

        for row in table.rows:
            blob = self._row_blob_from_cells(row.cells)
            if not blob:
                continue
            row_count_before = len(rows)
            raw_row_count_before = len(raw_rows)
            self._parse_free_text_blob(blob, rows, raw_rows)
            if len(rows) == row_count_before and len(raw_rows) == raw_row_count_before:
                dropped_row_count += 1

        partial = dropped_row_count > 0 or bool(raw_rows) or not rows
        return rows, raw_rows, partial, dropped_row_count

    @staticmethod
    def _should_use_answer_table(table: AnswerTable) -> bool:
        table_category = (table.table_category or "").strip().lower()
        if table_category and table_category != TableCategory.SPARE_PARTS_TABLE:
            return False
        if table_category == TableCategory.SPARE_PARTS_TABLE:
            return True
        return (table.chunk_type or "").strip().lower() == "spare_parts_table"

    @staticmethod
    def _table_section_title(table: AnswerTable) -> str:
        if table.section_path:
            section_parts = [part.strip() for part in table.section_path.split(">") if part.strip()]
            if section_parts:
                return section_parts[-1]
        return "Spare Parts List"

    @staticmethod
    def _row_blob_from_cells(cells: list[str]) -> str:
        non_empty_cells = [str(cell).strip() for cell in cells if str(cell).strip()]
        return " ".join(non_empty_cells).strip()

    @staticmethod
    def _looks_like_content_fragment(text: str) -> bool:
        if len(text) > 240:
            return False
        lowered = text.lower()
        if lowered.strip() == TABLE_EVIDENCE_PHRASE:
            return False
        if any(marker in lowered for marker in _BOILERPLATE_MARKERS):
            return False
        return bool(re.search(r"\d", text))
