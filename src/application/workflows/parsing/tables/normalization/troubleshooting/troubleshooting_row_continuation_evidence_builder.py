from __future__ import annotations

from src.domain.assets.table_cell_span import TableCellSpan


class TroubleshootingRowContinuationEvidenceBuilder:
    _SUPPORTED_FIELDS = frozenset({"symptom", "cause", "remedy", "notes"})

    def build(
        self,
        *,
        source_row_indexes: list[int],
        header_indexes: dict[int, str],
        cell_spans: list[TableCellSpan] | None,
    ) -> dict[tuple[int, int], frozenset[str]]:
        if not cell_spans or len(source_row_indexes) < 2:
            return {}

        supported_columns = {
            column_index: field_name
            for column_index, field_name in header_indexes.items()
            if field_name in self._SUPPORTED_FIELDS
        }
        if not supported_columns:
            return {}

        evidence: dict[tuple[int, int], set[str]] = {}
        adjacent_pairs = list(zip(source_row_indexes, source_row_indexes[1:]))
        for previous_row_index, current_row_index in adjacent_pairs:
            fields = self._fields_for_pair(
                previous_row_index=previous_row_index,
                current_row_index=current_row_index,
                cell_spans=cell_spans,
                supported_columns=supported_columns,
            )
            if fields:
                evidence[(previous_row_index, current_row_index)] = fields

        return {
            row_pair: frozenset(field_names)
            for row_pair, field_names in evidence.items()
        }

    @staticmethod
    def _fields_for_pair(
        *,
        previous_row_index: int,
        current_row_index: int,
        cell_spans: list[TableCellSpan],
        supported_columns: dict[int, str],
    ) -> set[str]:
        fields: set[str] = set()
        for span in cell_spans:
            if span.col_span != 1:
                continue
            field_name = supported_columns.get(span.col_start)
            if field_name is None:
                continue
            if not (
                span.row_start <= previous_row_index < current_row_index <= span.row_end
            ):
                continue
            fields.add(field_name)
        return fields
