from __future__ import annotations

from typing import TYPE_CHECKING

from src.application.reporting.document_parsing.parsing.ocr_trace_serializer import (
    OcrTraceSerializer,
)

if TYPE_CHECKING:
    from src.application.workflows.parsing.parsing_workflow_result import (
        ParsingWorkflowResult,
    )


class ParsingReportBuilder:
    """Assembles the parse-summary report payload (pure dict-building, no I/O)."""

    def __init__(self, *, ocr_trace_serializer: OcrTraceSerializer | None = None) -> None:
        self.ocr_trace_serializer = ocr_trace_serializer or OcrTraceSerializer()

    def build(self, result: ParsingWorkflowResult) -> dict[str, object]:
        ocr_trace = getattr(result, "ocr_trace", None)
        return {
            "document_id": result.document_id,
            "file_path": result.file_path,
            "page_count": result.page_count,
            "element_count": result.element_count,
            "section_count": result.section_count,
            "chunk_count": result.chunk_count,
            "table_count": result.table_count,
            "picture_count": result.picture_count,
            "parse_confidence": result.parse_confidence,
            "orphan_element_count": result.orphan_element_count,
            "elements_without_page_count": result.elements_without_page_count,
            "parse_warnings": list(result.parse_warnings),
            "ocr": self.ocr_trace_serializer.serialize(ocr_trace),
        }
