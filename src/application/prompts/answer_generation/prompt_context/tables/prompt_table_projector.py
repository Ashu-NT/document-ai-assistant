from __future__ import annotations

from src.application.prompts.answer_generation.prompt_context.models.prompt_source_view import (
    PromptSourceView,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_table_view import (
    PromptTableView,
)
from src.application.prompts.answer_generation.prompt_context.tables.prompt_table_row_normalizer import (
    PromptTableRowNormalizer,
)
from src.application.prompts.answer_generation.prompt_context.tables.prompt_table_type_detector import (
    PromptTableTypeDetector,
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
                    source_number=source.source_number,
                    chunk_id=source.chunk_id,
                    chunk_name=source.chunk_name,
                    chunk_type=source.chunk_type,
                    document_title=source.document_title,
                    section_path=source.section_path,
                    page_start=source.page_start,
                    page_end=source.page_end,
                    retrieval_source=source.retrieval_source,
                    headers=headers,
                    rows=rows,
                )
            )
        return tables
