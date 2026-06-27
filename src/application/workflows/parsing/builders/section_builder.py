from src.application.workflows.parsing.builders.section_build_result import (
    SectionBuildResult,
)
from src.application.workflows.parsing.builders.section_hierarchy import (
    SectionHeaderFilter,
    SectionHierarchyResolver,
    SectionPathRelinker,
    SectionStackBuilder,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import BoundingBox, ElementType, SourceLocation
from src.domain.document import DocumentSection
from src.shared.ids import IdGenerator, IdPrefix


class SectionBuilder:
    def __init__(
        self,
        id_generator: IdGenerator,
        *,
        header_filter: SectionHeaderFilter | None = None,
        hierarchy_resolver: SectionHierarchyResolver | None = None,
        section_path_relinker: SectionPathRelinker | None = None,
        section_stack_builder: SectionStackBuilder | None = None,
    ) -> None:
        self.id_generator = id_generator
        self.header_filter = header_filter or SectionHeaderFilter()
        self.hierarchy_resolver = hierarchy_resolver or SectionHierarchyResolver()
        self.section_path_relinker = section_path_relinker or SectionPathRelinker()
        self.section_stack_builder = section_stack_builder or SectionStackBuilder(
            id_generator
        )

    def build(
        self,
        document_id: str,
        canonical_elements: list[CanonicalElement],
        *,
        default_title: str = "Document",
    ) -> SectionBuildResult:
        ordered_elements = sorted(
            canonical_elements,
            key=lambda element: element.order_index,
        )
        headers = self.header_filter.filter(
            sorted(
                [
                    element
                    for element in canonical_elements
                    if element.element_type == ElementType.SECTION_HEADER
                ],
                key=lambda element: element.order_index,
            )
        )
        filtered_header_ids = {
            header.element_id
            for header in headers
        }

        if not headers:
            root_section = DocumentSection(
                section_id=self.id_generator.new_id(IdPrefix.SECTION),
                document_id=document_id,
                title=default_title,
                level=1,
                section_path=[default_title],
                source=self._source_from_element(
                    ordered_elements[0] if ordered_elements else None
                ),
                sequence_number=1,
                reading_order_start=(
                    ordered_elements[0].order_index if ordered_elements else None
                ),
                reading_order_end=(
                    ordered_elements[-1].order_index if ordered_elements else None
                ),
            )
            return SectionBuildResult(
                sections=[root_section],
                element_section_ids={
                    element.element_id: root_section.section_id
                    for element in ordered_elements
                },
                element_section_paths={
                    element.element_id: list(root_section.section_path)
                    for element in ordered_elements
                },
            )

        hierarchy_resolution = self.hierarchy_resolver.resolve(
            [
                element
                for element in ordered_elements
                if element.element_type != ElementType.SECTION_HEADER
                or element.element_id in filtered_header_ids
            ]
        )
        sections, header_section_ids = self.section_stack_builder.build(
            document_id,
            headers,
            hierarchy_resolution.effective_levels,
            hierarchy_resolution.explicit_parent_headers,
        )
        section_lookup = {section.section_id: section for section in sections}

        root_section = self._build_leading_root_section(
            document_id,
            ordered_elements,
            headers,
            default_title,
        )
        if root_section is not None:
            sections.insert(0, root_section)
            section_lookup[root_section.section_id] = root_section

        self.section_path_relinker.relink(sections)
        element_section_ids: dict[str, str] = {}
        element_section_paths: dict[str, list[str]] = {}
        active_section = root_section

        for element in ordered_elements:
            if element.element_type == ElementType.SECTION_HEADER:
                section_id = header_section_ids.get(element.element_id)
                if section_id is not None:
                    active_section = section_lookup[section_id]

            if active_section is None:
                continue

            element_section_ids[element.element_id] = active_section.section_id
            element_section_paths[element.element_id] = list(active_section.section_path)

        return SectionBuildResult(
            sections=sections,
            element_section_ids=element_section_ids,
            element_section_paths=element_section_paths,
            header_levels=hierarchy_resolution.effective_levels,
            header_sources=hierarchy_resolution.sources,
            header_raw_levels=hierarchy_resolution.raw_levels,
            header_parent_headers=hierarchy_resolution.explicit_parent_headers,
            header_section_ids=header_section_ids,
        )

    def resolve_section_id(
        self,
        element: CanonicalElement,
        build_result: SectionBuildResult,
    ) -> str | None:
        return build_result.element_section_ids.get(element.element_id)

    def resolve_section_path(
        self,
        element: CanonicalElement,
        build_result: SectionBuildResult,
    ) -> list[str]:
        return list(build_result.element_section_paths.get(element.element_id, []))

    def _build_leading_root_section(
        self,
        document_id: str,
        ordered_elements: list[CanonicalElement],
        headers: list[CanonicalElement],
        default_title: str,
    ) -> DocumentSection | None:
        first_header_order = headers[0].order_index
        leading_elements = [
            element
            for element in ordered_elements
            if element.order_index < first_header_order
        ]
        if not leading_elements:
            return None

        return DocumentSection(
                    section_id=self.id_generator.new_id(IdPrefix.SECTION),
                    document_id=document_id,
                    title=default_title,
                    level=1,
                    section_path=[default_title],
                    source=self._source_from_element(
                        leading_elements[0]
                    ),
                    sequence_number=1,
                    reading_order_start=(
                        leading_elements[0].order_index
                    ),
                    reading_order_end=(
                        leading_elements[-1].order_index
                    ),
                )

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
