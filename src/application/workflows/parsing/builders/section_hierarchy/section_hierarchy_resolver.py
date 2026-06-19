from dataclasses import dataclass, field

from src.application.workflows.parsing.builders.section_hierarchy.heading_numbering import (
    extract_contextual_number,
    extract_heading_number,
    numbering_depth,
    parent_numberings,
)
from src.application.workflows.parsing.builders.section_hierarchy.heading_level_strategy import (
    HeadingLevelStrategy,
)
from src.application.workflows.parsing.builders.section_hierarchy.layout_heuristic_strategy import (
    LayoutHeuristicStrategy,
)
from src.application.workflows.parsing.builders.section_hierarchy.numbering_hierarchy_strategy import (
    NumberingHierarchyStrategy,
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
    header_numberings: dict[str, str] = field(default_factory=dict)
    explicit_parent_headers: dict[str, str] = field(default_factory=dict)


class SectionHierarchyResolver:
    def __init__(
        self,
        *,
        heading_level_strategy: HeadingLevelStrategy | None = None,
        toc_page_range_strategy: TocPageRangeStrategy | None = None,
        numbering_hierarchy_strategy: NumberingHierarchyStrategy | None = None,
        layout_heuristic_strategy: LayoutHeuristicStrategy | None = None,
    ) -> None:
        self.heading_level_strategy = heading_level_strategy or HeadingLevelStrategy()
        self.toc_page_range_strategy = toc_page_range_strategy or TocPageRangeStrategy()
        self.numbering_hierarchy_strategy = (
            numbering_hierarchy_strategy or NumberingHierarchyStrategy()
        )
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
            },
            header_numberings={
                header.element_id: number
                for header in headers
                if (number := extract_heading_number(header.text)) is not None
            },
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
            toc_outline = self.toc_page_range_strategy.build_outline(
                headers,
                canonical_elements,
            )
            toc_levels = self.toc_page_range_strategy.assign_levels(
                headers,
                canonical_elements,
                current_levels=resolution.effective_levels,
            )
            for header_id, level in toc_levels.items():
                if current_is_weak or header_id not in resolution.effective_levels:
                    resolution.effective_levels[header_id] = level
                    resolution.sources[header_id] = self.toc_page_range_strategy.name
            resolution.header_numberings.update(toc_outline.header_numberings)

        if self.numbering_hierarchy_strategy.can_apply(
            headers,
            canonical_elements,
            current_levels=resolution.effective_levels,
        ):
            numbering_levels = self.numbering_hierarchy_strategy.assign_levels(
                headers,
                canonical_elements,
                current_levels=resolution.effective_levels,
            )
            for header_id, level in numbering_levels.items():
                previous_level = resolution.effective_levels.get(header_id)
                if previous_level is None or previous_level == 1:
                    resolution.effective_levels[header_id] = level
                    resolution.sources[header_id] = self.numbering_hierarchy_strategy.name

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
        self._apply_contextual_numbering(headers, resolution)
        return resolution

    def _apply_contextual_numbering(
        self,
        headers: list[CanonicalElement],
        resolution: SectionHierarchyResolution,
    ) -> None:
        ordered_headers = sorted(headers, key=lambda header: header.order_index)
        number_to_header_id: dict[str, str] = {}
        for header in ordered_headers:
            number = resolution.header_numberings.get(header.element_id)
            if number is not None:
                number_to_header_id.setdefault(number, header.element_id)

        self._attach_chapter_markers(ordered_headers, resolution)

        for header in ordered_headers:
            header_id = header.element_id
            number = resolution.header_numberings.get(header_id)
            if number is not None:
                parent_assigned = False
                for parent_number in parent_numberings(number):
                    parent_header_id = number_to_header_id.get(parent_number)
                    if parent_header_id is None:
                        continue
                    resolution.explicit_parent_headers[header_id] = parent_header_id
                    parent_assigned = True
                    break
                if parent_assigned or not self._is_simple_numbered_step(header, resolution):
                    continue

            contextual_number = extract_contextual_number(header.text)
            contextual_depth = numbering_depth(contextual_number)
            if contextual_depth is not None and resolution.effective_levels.get(header_id, 1) == 1:
                resolution.effective_levels[header_id] = min(contextual_depth + 1, 6)
                resolution.sources[header_id] = self.numbering_hierarchy_strategy.name

            if not self._can_assign_contextual_parent(header, resolution):
                continue

            parent_header_id = self._find_contextual_parent_header(
                header,
                ordered_headers,
                resolution,
                number_to_header_id,
            )
            if parent_header_id is None:
                continue

            parent_level = resolution.effective_levels.get(parent_header_id, 1)
            current_level = resolution.effective_levels.get(header_id, 1)
            resolution.explicit_parent_headers[header_id] = parent_header_id
            if current_level <= parent_level:
                resolution.effective_levels[header_id] = min(parent_level + 1, 6)
                resolution.sources[header_id] = "toc_context"

    def _attach_chapter_markers(
        self,
        ordered_headers: list[CanonicalElement],
        resolution: SectionHierarchyResolution,
    ) -> None:
        for index, header in enumerate(ordered_headers):
            header_id = header.element_id
            number = resolution.header_numberings.get(header_id)
            if number is None or numbering_depth(number) != 1:
                continue

            if resolution.sources.get(header_id) != self.toc_page_range_strategy.name:
                continue

            page_no = header.page_start or header.page_end
            for candidate in reversed(ordered_headers[:index]):
                candidate_number = extract_heading_number(candidate.text)
                candidate_page = candidate.page_start or candidate.page_end
                if candidate_page != page_no:
                    break
                if candidate_number != number:
                    continue
                if not (candidate.text or "").casefold().startswith("chapter "):
                    continue

                resolution.explicit_parent_headers[header_id] = candidate.element_id
                parent_level = resolution.effective_levels.get(candidate.element_id, 1)
                resolution.effective_levels[header_id] = min(parent_level + 1, 6)
                resolution.sources[header_id] = "toc_context"
                break

    @staticmethod
    def _can_assign_contextual_parent(
        header: CanonicalElement,
        resolution: SectionHierarchyResolution,
    ) -> bool:
        if header.element_id in resolution.explicit_parent_headers:
            return False

        if (
            header.element_id in resolution.header_numberings
            and not SectionHierarchyResolver._is_simple_numbered_step(header, resolution)
        ):
            return False

        normalized = (header.text or "").casefold()
        if normalized.startswith(("chapter ", "section ", "part ")):
            return False

        return resolution.sources.get(header.element_id) in {
            "default",
            "numbering_hierarchy",
            "toc_page_range",
        }

    @staticmethod
    def _is_simple_numbered_step(
        header: CanonicalElement,
        resolution: SectionHierarchyResolution,
    ) -> bool:
        number = resolution.header_numberings.get(header.element_id)
        if number is None or numbering_depth(number) != 1:
            return False

        text = (header.text or "").strip()
        return text.startswith(f"{number}.")

    def _find_contextual_parent_header(
        self,
        header: CanonicalElement,
        ordered_headers: list[CanonicalElement],
        resolution: SectionHierarchyResolution,
        number_to_header_id: dict[str, str],
    ) -> str | None:
        header_index = ordered_headers.index(header)
        header_page = header.page_start or header.page_end

        for next_header in ordered_headers[header_index + 1 :]:
            next_number = resolution.header_numberings.get(next_header.element_id)
            if next_number is None:
                continue

            next_page = next_header.page_start or next_header.page_end
            if (
                header_page is not None
                and next_page is not None
                and next_page - header_page > 2
            ):
                break

            for parent_number in parent_numberings(next_number):
                parent_header_id = number_to_header_id.get(parent_number)
                if parent_header_id is not None:
                    return parent_header_id

        header_page = header.page_start or header.page_end
        for previous_header in reversed(ordered_headers[:header_index]):
            previous_page = previous_header.page_start or previous_header.page_end
            if (
                header_page is not None
                and previous_page is not None
                and header_page - previous_page > 2
            ):
                break

            if self._is_simple_numbered_step(previous_header, resolution):
                continue

            previous_level = resolution.effective_levels.get(previous_header.element_id, 1)
            if previous_level < 2:
                continue

            return previous_header.element_id

        return None

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
