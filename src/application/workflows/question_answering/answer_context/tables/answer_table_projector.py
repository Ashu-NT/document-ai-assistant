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
from src.application.workflows.question_answering.answer_context.tables.spare_parts_table_normalizer import (
    SparePartsTableNormalizer,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table_schema_inferer import (
    AnswerTableSchemaInferer,
)
from src.domain.assets.table_rows.performance_curve_matrix_normalizer import (
    PerformanceCurveMatrixNormalizer,
)
from src.domain.assets.table_rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)


class AnswerTableProjector:
    def __init__(
        self,
        schema_inferer: AnswerTableSchemaInferer | None = None,
        row_canonicalizer: TableRowCanonicalizer | None = None,
        spare_parts_table_normalizer: SparePartsTableNormalizer | None = None,
        performance_curve_normalizer: PerformanceCurveMatrixNormalizer | None = None,
    ) -> None:
        self.schema_inferer = schema_inferer or AnswerTableSchemaInferer()
        self.row_canonicalizer = row_canonicalizer or TableRowCanonicalizer()
        self.spare_parts_table_normalizer = (
            spare_parts_table_normalizer or SparePartsTableNormalizer()
        )
        self.performance_curve_normalizer = (
            performance_curve_normalizer or PerformanceCurveMatrixNormalizer()
        )

    def build(self, sources: Sequence[AnswerSource]) -> list[AnswerTable]:
        tables: list[AnswerTable] = []
        seen_keys: set[str] = set()
        for source in sources:
            if not source.table_rows:
                continue
            table_key = (
                source.metadata.get("logical_table_family_id")
                or source.chunk_id
            )
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

        table_category = source.metadata.get("table_category")
        table_shape = source.table_shape or source.metadata.get("table_shape")
        normalized_spare_parts = self.spare_parts_table_normalizer.normalize(
            cleaned_rows,
            table_category=table_category,
            chunk_type=source.chunk_type,
        )
        if normalized_spare_parts is not None:
            headers = normalized_spare_parts.headers
            body_rows = normalized_spare_parts.rows
            has_headers = True
            table_kind = "record_table"
            column_roles = self.schema_inferer.infer(
                chunk_type=source.chunk_type,
                headers=headers,
                table_category=table_category,
                table_shape=table_shape,
                rows=body_rows,
            )[1]
        else:
            performance_curve = (
                self.performance_curve_normalizer.normalize(cleaned_rows)
                if table_shape in {None, "", "performance_curve_matrix"}
                else None
            )
            if performance_curve is not None:
                headers = performance_curve.headers
                body_rows = performance_curve.rows
                has_headers = True
                table_kind = "performance_curve_matrix"
                column_roles = performance_curve.column_roles
            else:
                has_headers = self.row_canonicalizer.has_explicit_header_row(cleaned_rows)
                headers = cleaned_rows[0] if has_headers else []
                body_rows = cleaned_rows[1:] if has_headers else cleaned_rows
                table_kind, column_roles = self.schema_inferer.infer(
                    chunk_type=source.chunk_type,
                    headers=headers,
                    table_category=table_category,
                    table_shape=table_shape,
                    rows=body_rows,
                )
        rows = [
            AnswerTableRow(
                source_row_index=source_row_index,
                cells=list(row),
                cells_by_header=self._cells_by_header(headers, row),
            )
            for source_row_index, row in enumerate(
                body_rows,
                start=1 if has_headers else 0,
            )
        ]
        if not rows and not headers:
            return None

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
            table_kind=table_kind,
            column_roles=column_roles,
            logical_table_family_id=source.metadata.get("logical_table_family_id"),
            physical_table_ids=self._decode_table_ids(source.metadata),
            table_category=table_category,
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
