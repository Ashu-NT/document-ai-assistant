from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
)
from src.domain.common import ElementType
from src.domain.elements import CanonicalElement


class StructuredElementTextResolver:
    @classmethod
    def resolve(
        cls,
        element: CanonicalElement,
    ) -> str | None:
        element_text = clean_chunk_text(element.text)
        if element.element_type != ElementType.PICTURE:
            return element_text

        parser_extra = cls._parser_extra(element)
        ocr_text = clean_chunk_text(parser_extra.get("ocr_text"))
        caption = clean_chunk_text(parser_extra.get("caption"))

        if ocr_text and element_text:
            if ocr_text in element_text:
                return element_text
            if element_text in ocr_text:
                return ocr_text
            return clean_chunk_text(f"{element_text}\n{ocr_text}")

        return ocr_text or element_text or caption

    @staticmethod
    def _parser_extra(element: CanonicalElement) -> dict:
        if element.parser_metadata is None or element.parser_metadata.extra is None:
            return {}

        return element.parser_metadata.extra
