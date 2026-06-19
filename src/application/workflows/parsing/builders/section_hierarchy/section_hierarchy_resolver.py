from dataclasses import dataclass, field

from src.application.workflows.parsing.builders.section_hierarchy.heading_level_strategy import (
    HeadingLevelStrategy,
)
from src.application.workflows.parsing.builders.section_hierarchy.layout_heuristic_strategy import (
    LayoutHeuristicStrategy,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc_page_range_strategy import (
    TocPageRangeStrategy,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import ElementType


@dataclass(slots=True)
class SectionHierarchyResolution:
    effective_levels: dict[str, int] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)
    raw_levels: dict[str, int | None] = field(default_factory=dict)


class SectionHierarchyResolver:
    def __init__(
        self,
        *,
        heading_level_strategy: HeadingLevelStrategy | None = None,
        toc_page_range_strategy: TocPageRangeStrategy | None = None,
        layout_heuristic_strategy: LayoutHeuristicStrategy | None = None,
    ) -> None:
        self.heading_level_strategy = heading_level_strategy or HeadingLevelStrategy()
        self.toc_page_range_strategy = toc_page_range_strategy or TocPageRangeStrategy()
        self.layout_heuristic_strategy = layout_heuristic_strategy or LayoutHeuristicStrategy()

    def resolve(
        self,
        canonical_elements: list[CanonicalElement],
    ) -> SectionHierarchyResolution:
        headers = sorted(
            [
                element
                for element in canonical_elements
                if element.element_type == ElementType.SECTION_HEADER
            ],
            key=lambda element: element.order_index,
        )
        resolution = SectionHierarchyResolution(
            raw_levels={
                header.element_id: self._coerce_positive_int(
                    header.metadata.get("heading_level")
                )
                for header in headers
            }
        )

        if not headers:
            return resolution

        if self.heading_level_strategy.can_apply(headers, canonical_elements):
            heading_levels = self.heading_level_strategy.assign_levels(headers, canonical_elements)
            resolution.effective_levels.update(heading_levels)
            resolution.sources.update(
                {
                    header_id: self.heading_level_strategy.name
                    for header_id in heading_levels
                }
            )

        current_is_weak = self._levels_are_weak(resolution.effective_levels)
        if self.toc_page_range_strategy.can_apply(
            headers,
            canonical_elements,
            current_levels=resolution.effective_levels,
        ):
            toc_levels = self.toc_page_range_strategy.assign_levels(
                headers,
                canonical_elements,
                current_levels=resolution.effective_levels,
            )
            for header_id, level in toc_levels.items():
                if current_is_weak or header_id not in resolution.effective_levels:
                    resolution.effective_levels[header_id] = level
                    resolution.sources[header_id] = self.toc_page_range_strategy.name

        if self.layout_heuristic_strategy.can_apply(
            headers,
            canonical_elements,
            current_levels=resolution.effective_levels,
        ):
            refined_levels = self.layout_heuristic_strategy.assign_levels(
                headers,
                canonical_elements,
                current_levels=resolution.effective_levels,
            )
            for header_id, level in refined_levels.items():
                previous_level = resolution.effective_levels.get(header_id)
                resolution.effective_levels[header_id] = level
                if previous_level is None or previous_level != level:
                    resolution.sources[header_id] = self.layout_heuristic_strategy.name

        for header in headers:
            resolution.effective_levels.setdefault(header.element_id, 1)
            resolution.sources.setdefault(header.element_id, "default")

        resolution.effective_levels = self._normalize_levels(headers, resolution.effective_levels)
        return resolution

    @staticmethod
    def _levels_are_weak(levels: dict[str, int]) -> bool:
        if not levels:
            return True

        return len(set(levels.values())) <= 1

    @staticmethod
    def _normalize_levels(
        headers: list[CanonicalElement],
        levels: dict[str, int],
    ) -> dict[str, int]:
        if not levels:
            return {}

        clamped = {
            header_id: min(max(level, 1), 6)
            for header_id, level in levels.items()
        }
        unique_levels = sorted(set(clamped.values()))
        normalized_levels = {
            original_level: index + 1
            for index, original_level in enumerate(unique_levels)
        }

        normalized = {
            header_id: normalized_levels[level]
            for header_id, level in clamped.items()
        }

        first_header_id = headers[0].element_id
        normalized[first_header_id] = 1
        return normalized

    @staticmethod
    def _coerce_positive_int(value: object) -> int | None:
        if value is None:
            return None

        try:
            number = int(value)
        except (TypeError, ValueError):
            return None

        return number if number > 0 else None
