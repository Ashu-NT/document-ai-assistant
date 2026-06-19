from src.application.workflows.parsing.builders.section_hierarchy.heading_numbering import (
    extract_contextual_number,
    extract_heading_number,
    numbering_depth,
)
from src.application.workflows.parsing.builders.section_hierarchy.section_hierarchy_strategy import (
    SectionHierarchyStrategy,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement


class NumberingHierarchyStrategy(SectionHierarchyStrategy):
    name = "numbering_hierarchy"

    def can_apply(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> bool:
        del elements
        del current_levels

        numbered_headers = sum(
            1
            for header in headers
            if extract_heading_number(header.text) is not None
        )
        return numbered_headers >= 2

    def assign_levels(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> dict[str, int]:
        del elements
        del current_levels

        levels: dict[str, int] = {}
        for header in headers:
            number = extract_heading_number(header.text)
            if number is not None:
                depth = numbering_depth(number)
                if depth is not None:
                    levels[header.element_id] = depth
                continue

            contextual_number = extract_contextual_number(header.text)
            contextual_depth = numbering_depth(contextual_number)
            if contextual_depth is None:
                continue

            levels[header.element_id] = min(contextual_depth + 1, 6)

        return levels
