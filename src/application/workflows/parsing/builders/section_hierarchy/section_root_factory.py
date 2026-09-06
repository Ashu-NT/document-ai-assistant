from src.application.workflows.parsing.builders.chunking.text.section_path_matching import (
    normalize_section_path_for_matching,
)
from src.application.workflows.parsing.builders.section_build_result import (
    SectionBuildResult,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)
from src.domain.common import BoundingBox, SourceLocation
from src.domain.document import DocumentSection
from src.shared.ids import IdGenerator, IdPrefix


class SectionRootFactory:
    def __init__(self, id_generator: IdGenerator) -> None:
        self.id_generator = id_generator

    def build_root_only_result(
        self,
        *,
        document_id: str,
        elements: list[ParsedCanonicalElement],
        title: str,
    ) -> SectionBuildResult:
        root_path = [title]
        root = DocumentSection(
            section_id=self.id_generator.new_id(IdPrefix.SECTION),
            document_id=document_id,
            title=title,
            level=1,
            section_path=list(root_path),
            raw_section_path=list(root_path),
            normalized_section_path=(
                normalize_section_path_for_matching(
                    root_path,
                    document_title=title,
                )
                or list(root_path)
            ),
            source=self._source_from_element(elements[0] if elements else None),
            sequence_number=1,
            reading_order_start=elements[0].order_index if elements else None,
            reading_order_end=elements[-1].order_index if elements else None,
        )
        return SectionBuildResult(
            sections=[root],
            element_section_ids={element.element_id: root.section_id for element in elements},
            element_section_paths={
                element.element_id: list(root.section_path) for element in elements
            },
        )

    def build_leading_root(
        self,
        *,
        document_id: str,
        elements: list[ParsedCanonicalElement],
        headers: list[ParsedCanonicalElement],
        title: str,
    ) -> DocumentSection | None:
        first_header_order = headers[0].order_index
        leading = [
            element for element in elements if element.order_index < first_header_order
        ]
        if not leading:
            return None
        return DocumentSection(
            section_id=self.id_generator.new_id(IdPrefix.SECTION),
            document_id=document_id,
            title=title,
            level=1,
            section_path=[title],
            raw_section_path=[title],
            source=self._source_from_element(leading[0]),
            sequence_number=1,
            reading_order_start=leading[0].order_index,
            reading_order_end=leading[-1].order_index,
        )

    @staticmethod
    def _source_from_element(
        element: ParsedCanonicalElement | None,
    ) -> SourceLocation:
        if element is None:
            return SourceLocation()
        bbox = None
        if element.bbox is not None:
            bbox = BoundingBox(
                x1=element.bbox.x1,
                y1=element.bbox.y1,
                x2=element.bbox.x2,
                y2=element.bbox.y2,
            )
        return SourceLocation(
            page_start=element.page_start,
            page_end=element.page_end,
            bbox=bbox,
        )
