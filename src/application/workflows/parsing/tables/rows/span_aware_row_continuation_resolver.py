from __future__ import annotations

from src.application.workflows.parsing.tables.rows.row_continuation_patterns import (
    non_empty_cell_indexes,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    merge_continuation_text,
    normalize_cell,
)
from src.domain.assets.table_cell_span import TableCellSpan

_MIN_TOKEN_OVERLAP = 2
_MIN_TOKEN_OVERLAP_RATIO = 0.75


class SpanAwareRowContinuationResolver:
    """Uses Docling cell-span geometry as continuation proof across row
    boundaries when text-only continuation heuristics are too weak.

    This stays deliberately conservative:
    - only vertical single-column spans are considered
    - the current row must not introduce contradictory populated cells
    - at least one non-anchor cell must be supported by span text
    """

    def resolve(
        self,
        previous_row: list[str],
        current_row: list[str],
        *,
        previous_row_index: int,
        current_row_index: int,
        cell_spans: list[TableCellSpan] | None,
    ) -> list[int]:
        if not cell_spans or current_row_index <= previous_row_index:
            return []

        current_indexes = non_empty_cell_indexes(current_row)
        if not current_indexes:
            return []

        evidence_by_column = self._evidence_by_column(
            previous_row_index=previous_row_index,
            current_row_index=current_row_index,
            cell_spans=cell_spans,
        )
        if not evidence_by_column:
            return []

        saw_supported_non_anchor = False
        for index in current_indexes:
            previous_value = self._value_at(previous_row, index)
            current_value = self._value_at(current_row, index)
            if not previous_value or not current_value:
                return []
            if index == 0:
                if previous_value.casefold() != current_value.casefold():
                    return []
                continue

            evidence = evidence_by_column.get(index)
            if evidence is None:
                if previous_value.casefold() == current_value.casefold():
                    continue
                return []
            if previous_value.casefold() == current_value.casefold():
                continue
            if not self._supports_merge(evidence, previous_value, current_value):
                return []
            saw_supported_non_anchor = True

        if not saw_supported_non_anchor:
            return []
        return current_indexes

    def _evidence_by_column(
        self,
        *,
        previous_row_index: int,
        current_row_index: int,
        cell_spans: list[TableCellSpan],
    ) -> dict[int, TableCellSpan]:
        evidence: dict[int, TableCellSpan] = {}
        for span in cell_spans:
            if span.col_span != 1:
                continue
            if not (span.row_start <= previous_row_index < current_row_index <= span.row_end):
                continue
            current = evidence.get(span.col_start)
            if current is None or self._span_rank(span) > self._span_rank(current):
                evidence[span.col_start] = span
        return evidence

    def _supports_merge(
        self,
        span: TableCellSpan,
        previous_value: str,
        current_value: str,
    ) -> bool:
        merged = normalize_cell(merge_continuation_text(previous_value, current_value))
        target = self._span_text(span)
        if not merged or not target:
            return False
        left = merged.casefold()
        right = target.casefold()
        if left == right:
            return True
        if left in right or right in left:
            return True

        left_tokens = {token for token in left.split() if token}
        right_tokens = {token for token in right.split() if token}
        if not left_tokens or not right_tokens:
            return False
        overlap = left_tokens & right_tokens
        if len(overlap) < _MIN_TOKEN_OVERLAP:
            return False
        return len(overlap) / min(len(left_tokens), len(right_tokens)) >= _MIN_TOKEN_OVERLAP_RATIO

    @staticmethod
    def _span_rank(span: TableCellSpan) -> tuple[int, int, int]:
        return (
            span.row_span,
            len(span.raw_lines),
            len(normalize_cell(span.normalized_text or span.text)),
        )

    @staticmethod
    def _span_text(span: TableCellSpan) -> str:
        if span.raw_lines:
            return normalize_cell(" ".join(span.raw_lines))
        if span.normalized_text:
            return normalize_cell(span.normalized_text)
        return normalize_cell(span.text)

    @staticmethod
    def _value_at(row: list[str], index: int) -> str:
        if index >= len(row):
            return ""
        return normalize_cell(row[index])
