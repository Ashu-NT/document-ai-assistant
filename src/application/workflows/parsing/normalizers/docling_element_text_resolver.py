from typing import Any

from src.application.workflows.parsing.normalizers.docling_caption_extractor import (
    DoclingCaptionExtractor,
)
from src.application.workflows.parsing.normalizers.docling_table_extractor import (
    DoclingTableExtractor,
)
from src.application.workflows.parsing.normalizers.docling_value_accessors import (
    clean_text,
    get_value,
)
from src.application.workflows.parsing.normalizers.table_layout.table_reconstruction_result import (
    TableReconstructionResult,
)
from src.domain.common import ElementType


class DoclingElementTextResolver:
    def __init__(self, table_extractor: DoclingTableExtractor) -> None:
        self.table_extractor = table_extractor

    def extract_text(
        self,
        item: Any,
        element_type: ElementType,
        *,
        caption: str | None,
        table_markdown: str | None,
    ) -> str | None:
        if element_type == ElementType.TABLE:
            return table_markdown

        if element_type == ElementType.PICTURE:
            return clean_text(
                caption
                or get_value(item, "ocr_text")
                or get_value(item, "text")
            )

        for attribute_name in ("text", "orig", "caption", "name"):
            cleaned = clean_text(get_value(item, attribute_name))
            if cleaned:
                return cleaned

        for method_name in ("export_to_markdown", "to_markdown"):
            method = getattr(item, method_name, None)
            if callable(method):
                try:
                    cleaned = clean_text(method())
                except Exception:
                    cleaned = None
                if cleaned:
                    return cleaned

        return None

    def extract_table_markdown(
        self,
        item: Any,
        element_type: ElementType,
        *,
        raw_document: Any,
    ) -> str | None:
        if element_type != ElementType.TABLE:
            return None

        return self.table_extractor.extract_markdown(
            item,
            doc=raw_document,
        )

    @staticmethod
    def extract_caption_text(
        item: Any,
        caption_extractor: DoclingCaptionExtractor,
    ) -> str | None:
        return clean_text(
            caption_extractor.extract_caption(item)
            or get_value(item, "caption")
        )

    def extract_table_structure(
        self,
        item: Any,
        element_type: ElementType,
        *,
        page_lane_count: int | None = None,
    ) -> TableReconstructionResult | None:
        if element_type != ElementType.TABLE:
            return None
        return self.table_extractor.extract_structure(
            item, page_lane_count=page_lane_count
        )

    @staticmethod
    def extract_section_title(
        element_type: ElementType,
        text: str | None,
    ) -> str | None:
        if element_type == ElementType.SECTION_HEADER:
            return text

        return None
