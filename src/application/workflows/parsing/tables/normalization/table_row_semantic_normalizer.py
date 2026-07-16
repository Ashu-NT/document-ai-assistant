from __future__ import annotations

from src.domain.assets import TableAsset
from src.domain.assets.table_cell_span import TableCellSpan
from src.domain.assets.table_rows import (
    CertificationParticularsTableNormalizer,
    GenericWrappedRowTableNormalizer,
    MaintenanceScheduleTableNormalizer,
    NormalizedTableRows,
    PerformanceCurveTableNormalizer,
    SparePartsTableNormalizer,
    SpecificationKeyValueTableNormalizer,
    TroubleshootingTableNormalizer,
)


class TableRowSemanticNormalizer:
    def __init__(
        self,
        *,
        spare_parts_normalizer: SparePartsTableNormalizer | None = None,
        troubleshooting_normalizer: TroubleshootingTableNormalizer | None = None,
        maintenance_schedule_normalizer: (
            MaintenanceScheduleTableNormalizer | None
        ) = None,
        performance_curve_normalizer: PerformanceCurveTableNormalizer | None = None,
        specification_key_value_normalizer: (
            SpecificationKeyValueTableNormalizer | None
        ) = None,
        certification_particulars_normalizer: (
            CertificationParticularsTableNormalizer | None
        ) = None,
        generic_wrapped_row_normalizer: (
            GenericWrappedRowTableNormalizer | None
        ) = None,
    ) -> None:
        self.spare_parts_normalizer = (
            spare_parts_normalizer or SparePartsTableNormalizer()
        )
        self.troubleshooting_normalizer = (
            troubleshooting_normalizer or TroubleshootingTableNormalizer()
        )
        self.maintenance_schedule_normalizer = (
            maintenance_schedule_normalizer or MaintenanceScheduleTableNormalizer()
        )
        self.performance_curve_normalizer = (
            performance_curve_normalizer or PerformanceCurveTableNormalizer()
        )
        self.specification_key_value_normalizer = (
            specification_key_value_normalizer
            or SpecificationKeyValueTableNormalizer()
        )
        self.certification_particulars_normalizer = (
            certification_particulars_normalizer
            or CertificationParticularsTableNormalizer()
        )
        self.generic_wrapped_row_normalizer = (
            generic_wrapped_row_normalizer or GenericWrappedRowTableNormalizer()
        )

    def normalize(self, table: TableAsset) -> bool:
        normalized_main_rows = self._normalize_rows(
            table.rows,
            table_category=table.table_category,
            cell_spans=table.cell_spans,
        )
        updated = self._apply_main_rows(table, normalized_main_rows)
        if self._normalize_parallel_streams(table):
            updated = True

        if updated:
            table.row_count = len(table.rows) or None
            table.column_count = max((len(row) for row in table.rows), default=0) or None
        return updated

    def _normalize_parallel_streams(self, table: TableAsset) -> bool:
        if not table.parallel_stream_rows:
            return False

        normalized_streams: list[list[list[str]]] = []
        updated = False
        for rows in table.parallel_stream_rows:
            normalized_rows = self._normalize_rows(
                rows,
                table_category=table.table_category,
                cell_spans=table.cell_spans,
            )
            if normalized_rows is not None and normalized_rows != rows:
                normalized_streams.append(normalized_rows)
                updated = True
                continue
            normalized_streams.append(rows)

        if not updated:
            return False

        table.parallel_stream_rows = normalized_streams
        combined_rows = self._combine_parallel_stream_rows(normalized_streams)
        if combined_rows is not None:
            table.rows = combined_rows
        return True

    def _normalize_rows(
        self,
        rows: list[list[str]],
        *,
        table_category: str | None,
        cell_spans: list[TableCellSpan] | None = None,
    ) -> list[list[str]] | None:
        normalized = self._specialized_normalization(
            rows,
            table_category=table_category,
            cell_spans=cell_spans,
        )
        if normalized is None:
            return None
        return [list(normalized.headers), *[list(row) for row in normalized.rows]]

    def _specialized_normalization(
        self,
        rows: list[list[str]],
        *,
        table_category: str | None,
        cell_spans: list[TableCellSpan] | None = None,
    ) -> NormalizedTableRows | None:
        for normalizer in (
            self.spare_parts_normalizer,
            self.troubleshooting_normalizer,
            self.maintenance_schedule_normalizer,
            self.performance_curve_normalizer,
            self.specification_key_value_normalizer,
            self.certification_particulars_normalizer,
            self.generic_wrapped_row_normalizer,
        ):
            normalized = normalizer.normalize(
                rows,
                table_category=table_category,
                chunk_type=None,
                cell_spans=cell_spans,
            )
            if normalized is not None:
                return normalized
        return None

    @staticmethod
    def _apply_main_rows(
        table: TableAsset,
        normalized_rows: list[list[str]] | None,
    ) -> bool:
        if normalized_rows is None or normalized_rows == table.rows:
            return False
        table.rows = normalized_rows
        return True

    @staticmethod
    def _combine_parallel_stream_rows(
        streams: list[list[list[str]]],
    ) -> list[list[str]] | None:
        if not streams:
            return None

        headers = [stream[0] for stream in streams if stream]
        if len(headers) != len(streams) or not headers:
            return None

        first_signature = TableRowSemanticNormalizer._header_signature(headers[0])
        if not first_signature:
            return None
        if any(
            TableRowSemanticNormalizer._header_signature(header) != first_signature
            for header in headers[1:]
        ):
            return None

        combined = [list(headers[0])]
        for stream in streams:
            combined.extend([list(row) for row in stream[1:]])
        return combined

    @staticmethod
    def _header_signature(header: list[str]) -> tuple[str, ...]:
        return tuple(str(cell).strip().casefold() for cell in header if str(cell).strip())
