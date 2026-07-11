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
        chunk_type = (source.chunk_type or "").strip().lower()
        section_path = (source.section_path or "").strip().lower()
        header_text = " ".join(header.lower() for header in headers)

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
