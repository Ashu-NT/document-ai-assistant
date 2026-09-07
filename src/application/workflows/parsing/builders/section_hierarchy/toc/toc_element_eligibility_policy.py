from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)
from src.domain.common import ElementType
from src.application.workflows.parsing.layout.page_furniture import is_page_furniture


class TocElementEligibilityPolicy:
    """Rejects page furniture and vertical marginal text from TOC evidence."""

    _FURNITURE_LABELS = {"page_header", "page_footer"}

    @classmethod
    def is_eligible(cls, element: ParsedCanonicalElement) -> bool:
        if element.element_type == ElementType.TABLE:
            return True

        parser_extra = element.metadata.get("parser_extra")
        if not isinstance(parser_extra, dict):
            parser_extra = {}
        item_label = str(
            element.metadata.get("item_label")
            or parser_extra.get("item_label")
            or parser_extra.get("label")
            or ""
        ).lower()
        content_layer = str(
            element.metadata.get("content_layer")
            or parser_extra.get("content_layer")
            or ""
        ).lower()
        if (
            item_label in cls._FURNITURE_LABELS
            or content_layer == "furniture"
            or is_page_furniture(element.metadata)
            or is_page_furniture(parser_extra)
        ):
            return False

        bbox = element.bbox
        if bbox is None:
            return True
        width = abs(bbox.x2 - bbox.x1)
        height = abs(bbox.y2 - bbox.y1)
        return width >= height
