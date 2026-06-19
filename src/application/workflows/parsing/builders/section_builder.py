from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import BoundingBox, ElementType, SourceLocation
from src.domain.document import DocumentSection
from src.shared.ids import IdGenerator, IdPrefix


class SectionBuilder:
    def __init__(self, id_generator: IdGenerator) -> None:
        self.id_generator = id_generator

    def build(
        self,
        document_id: str,
        canonical_elements: list[CanonicalElement],
        *,
        default_title: str = "Document",
    ) -> list[DocumentSection]:
        headers = sorted(
            [
                element
                for element in canonical_elements
                if element.element_type == ElementType.SECTION_HEADER
            ],
            key=lambda element: element.order_index,
        )

        if not headers:
            return [
                DocumentSection(
                    section_id=self.id_generator.new_id(IdPrefix.SECTION),
                    document_id=document_id,
                    title=default_title,
                    level=1,
                    section_path=[default_title],
                    source=self._source_from_element(
                        canonical_elements[0] if canonical_elements else None
                    ),
                    sequence_number=1,
                    reading_order_start=(
                        canonical_elements[0].order_index if canonical_elements else None
                    ),
                    reading_order_end=(
                        canonical_elements[-1].order_index if canonical_elements else None
                    ),
                )
            ]

        sections: list[DocumentSection] = []
        sections_by_path: dict[tuple[str, ...], DocumentSection] = {}

        for index, header in enumerate(headers, start=1):
            title = header.text or header.section_title or f"Section {index}"
            section_path = header.section_path or [title]
            parent_path = tuple(section_path[:-1])
            parent_section = sections_by_path.get(parent_path)

            section = DocumentSection(
                section_id=self.id_generator.new_id(IdPrefix.SECTION),
                document_id=document_id,
                title=title,
                level=max(1, len(section_path)),
                parent_section_id=(
                    parent_section.section_id if parent_section is not None else None
                ),
                section_path=list(section_path),
                source=self._source_from_element(header),
                sequence_number=index,
                reading_order_start=header.order_index,
                reading_order_end=header.order_index,
            )

            sections.append(section)
            sections_by_path[tuple(section.section_path)] = section

        return sections

    def resolve_section_id(
        self,
        element: CanonicalElement,
        sections: list[DocumentSection],
    ) -> str | None:
        if not sections:
            return None

        sections_by_path = {
            tuple(section.section_path): section
            for section in sections
            if section.section_path
        }

        if element.parent_section_id is not None:
            for section in sections:
                if section.section_id == element.parent_section_id:
                    return section.section_id

        if element.section_path:
            for size in range(len(element.section_path), 0, -1):
                section = sections_by_path.get(tuple(element.section_path[:size]))
                if section is not None:
                    return section.section_id

        if element.section_title:
            for section in sections:
                if section.title == element.section_title:
                    return section.section_id

        ordered_sections = sorted(
            sections,
            key=lambda section: section.sequence_number or 0,
        )

        for section in reversed(ordered_sections):
            if section.reading_order_start is None:
                continue

            if element.order_index >= section.reading_order_start:
                return section.section_id

        return ordered_sections[0].section_id

    @staticmethod
    def _source_from_element(element: CanonicalElement | None) -> SourceLocation:
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
