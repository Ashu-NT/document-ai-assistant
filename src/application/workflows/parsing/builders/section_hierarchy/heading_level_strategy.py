from src.application.workflows.parsing.builders.section_hierarchy.section_hierarchy_strategy import (
    SectionHierarchyStrategy,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement


class HeadingLevelStrategy(SectionHierarchyStrategy):
    name = "docling_level"

    def can_apply(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> bool:
        del elements
        del current_levels

        levels = self.assign_levels(headers, headers)
        if not levels:
            return False

        return len(set(levels.values())) > 1

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
            heading_level = header.metadata.get("heading_level")
            if not isinstance(heading_level, int) or heading_level <= 0:
                continue

            levels[header.element_id] = heading_level

        return levels
