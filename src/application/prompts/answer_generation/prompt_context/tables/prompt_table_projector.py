from __future__ import annotations

from src.application.prompts.answer_generation.prompt_context.models.prompt_source_view import (
    PromptSourceView,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_table_row_view import (
    PromptTableRowView,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_table_view import (
    PromptTableView,
)
from src.application.prompts.answer_generation.prompt_context.tables.prompt_table_label_mapper import (
    prompt_table_label_for_strategy,
)
from src.application.prompts.answer_generation.prompt_context.tables.prompt_table_row_normalizer import (
    PromptTableRowNormalizer,
)
from src.application.prompts.answer_generation.prompt_context.tables.prompt_table_type_detector import (
    PromptTableTypeDetector,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
    AnswerTableRow,
)
from src.application.workflows.question_answering.answer_context.tables.table_type_resolution_core import (
    resolve_table_type,
)


class PromptTableProjector:
    def __init__(
        self,
        prompt_table_row_normalizer: PromptTableRowNormalizer | None = None,
        prompt_table_type_detector: PromptTableTypeDetector | None = None,
    ) -> None:
        self.prompt_table_row_normalizer = (
            prompt_table_row_normalizer or PromptTableRowNormalizer()
        )
        self.prompt_table_type_detector = (
            prompt_table_type_detector or PromptTableTypeDetector()
        )

    def build(self, sources: list[PromptSourceView]) -> list[PromptTableView]:
        tables: list[PromptTableView] = []
        for source in sources:
            if not source.table_rows:
                continue
            headers, rows = self.prompt_table_row_normalizer.normalize(source.table_rows)
            if not rows and not headers:
                continue
            tables.append(
                PromptTableView(
                    table_id=f"{source.chunk_id}:table",
                    table_type=self.prompt_table_type_detector.detect(
                        source,
                        headers=headers,
                    ),
                    table_strategy=self._shared_table_strategy(
                        chunk_type=source.chunk_type,
                        headers=headers,
                        table_category=source.metadata.get("table_category"),
                        table_shape=source.table_shape,
                        rows=[list(row.cells) for row in rows],
                    ),
                    source_number=source.source_number,
                    chunk_id=source.chunk_id,
                    chunk_name=source.chunk_name,
                    chunk_type=source.chunk_type,
                    document_title=source.document_title,
                    section_path=source.section_path,
                    page_start=source.page_start,
                    page_end=source.page_end,
                    retrieval_source=source.retrieval_source,
                    table_shape=source.table_shape,
                    table_category=source.metadata.get("table_category"),
                    table_structure_quality=source.table_structure_quality,
                    header_paths=[list(path) for path in source.table_header_paths],
                    axis_summary=dict(source.table_axis_summary),
                    headers=headers,
                    rows=rows,
                )
            )
        return tables

    def build_from_answer_tables(
        self,
        tables: list[AnswerTable],
    ) -> list[PromptTableView]:
        projected: list[PromptTableView] = []
        for table in tables:
            if not table.headers and not table.rows:
                continue
            projected.append(
                PromptTableView(
                    table_id=table.logical_table_family_id or f"{table.chunk_id}:table",
                    table_type=self._table_type_for_answer_table(table),
                    table_strategy=table.table_kind.value,
                    source_number=table.source_number,
                    chunk_id=table.chunk_id,
                    chunk_type=table.chunk_type,
                    document_title=table.document_title or "Current document",
                    section_path=table.section_path or "N/A",
                    page_start=table.page_start,
                    page_end=table.page_end,
                    table_shape=table.table_shape,
                    table_category=table.table_category,
                    table_structure_quality=table.table_structure_quality,
                    header_paths=[list(path) for path in table.header_paths],
                    axis_summary=dict(table.axis_summary),
                    headers=list(table.headers),
                    rows=[
                        self._project_answer_table_row(row)
                        for row in table.rows
                    ],
                )
            )
        return projected

    def _table_type_for_answer_table(self, table: AnswerTable) -> str:
        mapped = prompt_table_label_for_strategy(table.table_kind)
        if mapped != "general_table":
            return mapped
        prompt_source = PromptSourceView(
            source_number=table.source_number,
            chunk_id=table.chunk_id,
            chunk_type=table.chunk_type,
            document_title=table.document_title or "Current document",
            section_path=table.section_path or "N/A",
            page_start=table.page_start,
            page_end=table.page_end,
            table_rows=self._table_rows_for_detection(table),
            table_shape=table.table_shape,
            table_structure_quality=table.table_structure_quality,
            table_header_paths=[list(path) for path in table.header_paths],
            table_axis_summary=dict(table.axis_summary),
            metadata={"table_category": table.table_category or ""},
        )
        return self.prompt_table_type_detector.detect(
            prompt_source,
            headers=list(table.headers),
        )

    @staticmethod
    def _project_answer_table_row(row: AnswerTableRow) -> PromptTableRowView:
        return PromptTableRowView(
            source_row_index=row.source_row_index,
            cells=list(row.cells),
            cells_by_header=dict(row.cells_by_header),
        )

    @staticmethod
    def _table_rows_for_detection(table: AnswerTable) -> list[list[str]]:
        rows = [list(row.cells) for row in table.rows]
        if table.headers:
            return [list(table.headers), *rows]
        return rows

    @staticmethod
    def _shared_table_strategy(
        *,
        chunk_type: str | None,
        headers: list[str],
        table_category: str | None,
        table_shape: str | None,
        rows: list[list[str]] | None,
    ) -> str:
        resolved, _ = resolve_table_type(
            table_category=table_category,
            table_shape=table_shape,
            chunk_type=chunk_type,
            headers=headers,
            rows=rows,
        )
        return resolved.value
