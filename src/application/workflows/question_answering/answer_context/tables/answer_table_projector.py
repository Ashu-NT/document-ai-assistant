from __future__ import annotations

import json
from typing import Sequence

from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
    AnswerTableRow,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table_schema_inferer import (
    AnswerTableSchemaInferer,
)
from src.application.workflows.question_answering.answer_context.tables.projections import (
    AnswerTableProjectionRouter,
    GenericTableProjectionBuilder,
    PerformanceCurveTableProjectionBuilder,
    SparePartsTableProjectionBuilder,
    TroubleshootingTableProjectionBuilder,
)
from src.domain.assets.table_rows import (
    PerformanceCurveMatrixNormalizer,
    SparePartsTableNormalizer,
    TableRowCanonicalizer,
    TroubleshootingTableNormalizer,
)


class AnswerTableProjector:
    def __init__(
        self,
        schema_inferer: AnswerTableSchemaInferer | None = None,
        row_canonicalizer: TableRowCanonicalizer | None = None,
        spare_parts_table_normalizer: SparePartsTableNormalizer | None = None,
        troubleshooting_table_normalizer: (
            TroubleshootingTableNormalizer | None
        ) = None,
        performance_curve_normalizer: PerformanceCurveMatrixNormalizer | None = None,
        projection_router: AnswerTableProjectionRouter | None = None,
    ) -> None:
        self.row_canonicalizer = row_canonicalizer or TableRowCanonicalizer()
        schema_inferer = schema_inferer or AnswerTableSchemaInferer()
        self.projection_router = projection_router or AnswerTableProjectionRouter(
            spare_parts_projection_builder=SparePartsTableProjectionBuilder(
                spare_parts_table_normalizer=(
                    spare_parts_table_normalizer or SparePartsTableNormalizer()
                ),
                schema_inferer=schema_inferer,
            ),
            troubleshooting_projection_builder=TroubleshootingTableProjectionBuilder(
                troubleshooting_table_normalizer=(
                    troubleshooting_table_normalizer
                    or TroubleshootingTableNormalizer()
                )
            ),
            performance_curve_projection_builder=PerformanceCurveTableProjectionBuilder(
                performance_curve_normalizer=(
                    performance_curve_normalizer
                    or PerformanceCurveMatrixNormalizer()
                )
            ),
            generic_projection_builder=GenericTableProjectionBuilder(
                schema_inferer=schema_inferer,
                row_canonicalizer=self.row_canonicalizer,
            ),
        )

    def build(self, sources: Sequence[AnswerSource]) -> list[AnswerTable]:
        tables: list[AnswerTable] = []
        seen_keys: set[str] = set()
        for source in sources:
            if not source.table_rows:
                continue
            table_key = source.metadata.get("logical_table_family_id") or source.chunk_id
            if table_key in seen_keys:
                continue
            table = self._build_table(source)
            if table is not None:
                tables.append(table)
                seen_keys.add(table_key)
        return tables

    def _build_table(self, source: AnswerSource) -> AnswerTable | None:
        cleaned_rows = self.row_canonicalizer.canonicalize(source.table_rows or [])
        if not cleaned_rows:
            return None

        projection = self.projection_router.project(
            source=source,
            cleaned_rows=cleaned_rows,
        )
        if projection is None:
            return None

        headers = projection.headers
        body_rows = projection.body_rows
        rows = [
            AnswerTableRow(
                source_row_index=source_row_index,
                cells=list(row),
                cells_by_header=self._cells_by_header(headers, row),
            )
            for source_row_index, row in enumerate(
                body_rows,
                start=1 if projection.has_headers else 0,
            )
        ]
        if not rows and not headers:
            return None

        table_shape = source.table_shape or source.metadata.get("table_shape")
        return AnswerTable(
            source_number=source.source_number,
            chunk_id=source.chunk_id,
            chunk_type=source.chunk_type,
            document_title=source.document_title,
            section_path=source.section_path,
            page_start=source.page_start,
            page_end=source.page_end,
            headers=headers,
            rows=rows,
            table_kind=projection.table_kind,
            column_roles=projection.column_roles,
            logical_table_family_id=source.metadata.get("logical_table_family_id"),
            physical_table_ids=self._decode_table_ids(source.metadata),
            table_category=source.metadata.get("table_category"),
            table_category_confidence=self._coerce_float(
                source.metadata.get("table_category_confidence")
            ),
            table_shape=table_shape,
            table_structure_quality=source.table_structure_quality,
            header_paths=[list(path) for path in source.table_header_paths],
            axis_summary=dict(source.table_axis_summary),
            row_start=self._coerce_int(source.metadata.get("table_row_start")),
            row_end=self._coerce_int(source.metadata.get("table_row_end")),
        )

    @staticmethod
    def _cells_by_header(headers: list[str], row: list[str]) -> dict[str, str]:
        if not headers:
            return {}
        return {
            header: row[index]
            for index, header in enumerate(headers)
            if header and index < len(row) and row[index]
        }

    @staticmethod
    def _decode_table_ids(metadata: dict[str, str]) -> list[str]:
        raw = metadata.get("hydrated_table_ids") or metadata.get("table_ids") or ""
        if not raw:
            return []
        if raw.startswith("[") and raw.endswith("]"):
            try:
                decoded = json.loads(raw)
            except ValueError:
                decoded = []
            if isinstance(decoded, list):
                return [str(value).strip() for value in decoded if str(value).strip()]
            return []
        return [value.strip() for value in raw.split(",") if value.strip()]

    @staticmethod
    def _coerce_int(value: str | None) -> int | None:
        if not value:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_float(value: str | None) -> float | None:
        if not value:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
