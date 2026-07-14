from __future__ import annotations

from src.application.prompts.answer_generation.prompt_context.models.prompt_source_view import (
    PromptSourceView,
)


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

        if table_shape == "maintenance_schedule_matrix":
            return "maintenance_table"
        if table_shape == "performance_curve_matrix":
            return "specification_table"
        if table_shape == "specification_matrix":
            return "specification_table"
        if table_category == "maintenance_interval_table":
            return "maintenance_table"
        if table_category == "technical_data_table":
            return "specification_table"
        if table_category == "certification_table":
            return "certification_table"
        if table_category == "spare_parts_table":
            return "spare_parts_table"
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
