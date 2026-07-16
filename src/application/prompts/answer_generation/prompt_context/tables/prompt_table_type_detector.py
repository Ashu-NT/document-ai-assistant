from __future__ import annotations

from src.application.prompts.answer_generation.prompt_context.models.prompt_source_view import (
    PromptSourceView,
)
from src.application.workflows.shared.table_kind import TableKind
from src.application.workflows.question_answering.answer_context.tables.table_type_resolution_core import (
    resolve_table_type,
)

_RESOLVED_TYPE_TO_PROMPT_LABEL: dict[TableKind, str] = {
    TableKind.MAINTENANCE_SCHEDULE_MATRIX: "maintenance_table",
    TableKind.MAINTENANCE_SCHEDULE_TABLE: "maintenance_table",
    TableKind.PERFORMANCE_CURVE_MATRIX: "specification_table",
    TableKind.SPECIFICATION_MATRIX: "specification_table",
    TableKind.TOC_TABLE: "general_table",
    TableKind.TROUBLESHOOTING_TABLE: "general_table",
    TableKind.SPARE_PARTS_TABLE: "spare_parts_table",
    TableKind.CERTIFICATION_TABLE: "certification_table",
    TableKind.RECORD_TABLE: "general_table",
    TableKind.KEY_VALUE_TABLE: "general_table",
    TableKind.GENERAL_TABLE: "general_table",
}


class PromptTableTypeDetector:
    def detect(
        self,
        source: PromptSourceView,
        *,
        headers: list[str],
    ) -> str:
        table_shape = (source.table_shape or "").strip().lower()
        table_category = (
            (source.metadata.get("table_category") or "").strip().lower()
        )
        chunk_type = (source.chunk_type or "").strip().lower()
        section_path = (source.section_path or "").strip().lower()
        header_text = " ".join(header.lower() for header in headers)

        resolved, _ = resolve_table_type(
            table_category=table_category or None,
            table_shape=table_shape or None,
            chunk_type=chunk_type or None,
            headers=headers,
            rows=source.table_rows,
        )
        mapped = _RESOLVED_TYPE_TO_PROMPT_LABEL[resolved]
        if mapped != "general_table":
            return mapped

        # Residual, prompt-only heuristics with no equivalent on the answer
        # path -- `AnswerTableSchemaInferer` never had these, so they are
        # deliberately kept out of the shared core rather than forced onto
        # the answer path too. Only reached when the shared core's decision
        # for this input has no more specific opinion than "general_table".
        if table_category == "technical_data_table":
            return "specification_table"
        if chunk_type == "spare_parts_table":
            return "spare_parts_table"
        if "certificate" in section_path or "particulars" in section_path:
            return "certification_table"
        if chunk_type == "technical_specification" or any(
            token in section_path
            for token in ("technical", "specification", "specifications", "specs")
        ):
            return "specification_table"
        if any(token in header_text for token in ("task", "interval", "frequency")):
            return "maintenance_table"
        return "general_table"
