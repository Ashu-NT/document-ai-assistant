from src.application.workflows.parsing.canonical_element import (
    CanonicalElement as ParsedCanonicalElement,
)
from src.domain.common import BoundingBox, SourceLocation


class SourceLocationFactory:
    @staticmethod
    def from_parsed(parsed_element: ParsedCanonicalElement) -> SourceLocation:
        bbox = None
        if parsed_element.bbox is not None:
            bbox = BoundingBox(
                x1=parsed_element.bbox.x1,
                y1=parsed_element.bbox.y1,
                x2=parsed_element.bbox.x2,
                y2=parsed_element.bbox.y2,
            )

        return SourceLocation(
            page_start=parsed_element.page_start,
            page_end=parsed_element.page_end,
            bbox=bbox,
        )
