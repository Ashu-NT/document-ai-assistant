from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement
from src.application.workflows.parsing.builders.section_hierarchy.section_heading_labeler import (
    SectionHeadingLabeler,
)
from src.domain.common import BoundingBox, SourceLocation
from src.domain.document import DocumentSection
from src.shared.ids import IdGenerator, IdPrefix


class SectionStackBuilder:
    def __init__(
        self,
        id_generator: IdGenerator,
        *,
        heading_labeler: SectionHeadingLabeler | None = None,
    ) -> None:
        self.id_generator = id_generator
        self.heading_labeler = heading_labeler or SectionHeadingLabeler()

    def build(
        self,
        document_id: str,
        headers: list[ParsedCanonicalElement],
        effective_levels: dict[str, int],
        explicit_parent_headers: dict[str, str] | None = None,
        header_numberings: dict[str, str] | None = None,
    ) -> tuple[list[DocumentSection], dict[str, str]]:
        sections: list[DocumentSection] = []
        header_section_ids: dict[str, str] = {}
        header_sections: dict[str, DocumentSection] = {}
        stack: dict[int, DocumentSection] = {}

        for index, header in enumerate(
            sorted(headers, key=lambda element: element.order_index), start=1
        ):
            level = min(max(1, effective_levels.get(header.element_id, 1)), 6)
            explicit_parent_header_id = (
                explicit_parent_headers.get(header.element_id)
                if explicit_parent_headers is not None
                else None
            )
            parent_section = (
                header_sections.get(explicit_parent_header_id)
                if explicit_parent_header_id is not None
                else None
            )
            if parent_section is None:
                parent_section = self._find_parent_section(level, stack)
            raw_title = header.text or header.section_title or f"Section {index}"
            title = self.heading_labeler.build_label(
                raw_title=raw_title,
                resolved_numbering=(
                    header_numberings.get(header.element_id)
                    if header_numberings is not None
                    else None
                ),
            )
            section_path = (
                [*parent_section.section_path, title] if parent_section is not None else [title]
            )

            section = DocumentSection(
                section_id=self.id_generator.new_id(IdPrefix.SECTION),
                document_id=document_id,
                title=title,
                level=level,
                parent_section_id=(
                    parent_section.section_id if parent_section is not None else None
                ),
                section_path=section_path,
                raw_section_path=list(section_path),
                source=self._source_from_element(header),
                sequence_number=index,
                reading_order_start=header.order_index,
                reading_order_end=header.order_index,
            )

            sections.append(section)
            header_section_ids[header.element_id] = section.section_id
            header_sections[header.element_id] = section
            stack[level] = section
            self._clear_deeper_levels(stack, level)

        self._apply_explicit_parents(
            header_sections=header_sections,
            explicit_parent_headers=explicit_parent_headers or {},
        )

        return sections, header_section_ids

    @staticmethod
    def _apply_explicit_parents(
        *,
        header_sections: dict[str, DocumentSection],
        explicit_parent_headers: dict[str, str],
    ) -> None:
        for child_header_id, parent_header_id in explicit_parent_headers.items():
            child = header_sections.get(child_header_id)
            parent = header_sections.get(parent_header_id)
            if child is None or parent is None:
                continue
            child.parent_section_id = parent.section_id

        section_by_id = {section.section_id: section for section in header_sections.values()}
        resolved_paths: dict[str, list[str]] = {}

        def resolve_path(section: DocumentSection) -> list[str]:
            cached = resolved_paths.get(section.section_id)
            if cached is not None:
                return cached
            parent = section_by_id.get(section.parent_section_id or "")
            path = [section.title]
            if parent is not None:
                path = [*resolve_path(parent), section.title]
            resolved_paths[section.section_id] = path
            return path

        for section in header_sections.values():
            section.section_path = resolve_path(section)
            section.raw_section_path = list(section.section_path)

    @staticmethod
    def _find_parent_section(
        level: int,
        stack: dict[int, DocumentSection],
    ) -> DocumentSection | None:
        for candidate_level in range(level - 1, 0, -1):
            parent = stack.get(candidate_level)
            if parent is not None:
                return parent

        return None

    @staticmethod
    def _clear_deeper_levels(stack: dict[int, DocumentSection], level: int) -> None:
        for candidate_level in [value for value in stack if value > level]:
            stack.pop(candidate_level, None)

    @staticmethod
    def _source_from_element(element: ParsedCanonicalElement) -> SourceLocation:
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
