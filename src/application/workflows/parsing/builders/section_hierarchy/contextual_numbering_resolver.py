from __future__ import annotations

from typing import TYPE_CHECKING

from src.application.workflows.parsing.builders.section_hierarchy.heading_numbering import (
    extract_contextual_number,
    extract_heading_number,
    numbering_depth,
    parent_numberings,
)
from src.application.workflows.parsing.builders.section_hierarchy.numbering_hierarchy_strategy import (
    NumberingHierarchyStrategy,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc_page_range_strategy import (
    TocPageRangeStrategy,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement

if TYPE_CHECKING:
    from src.application.workflows.parsing.builders.section_hierarchy.section_hierarchy_resolver import (
        SectionHierarchyResolution,
    )


class ContextualNumberingResolver:
    # Note: contextual-parent lookup is worst-case O(headers^2) for documents
    # with many unnumbered headers. Flagged as a separate, optional efficiency
    # follow-up (see doc/repo_refactoring_plan.md section 6) -- not addressed here.

    def __init__(
        self,
        *,
        toc_page_range_strategy: TocPageRangeStrategy,
        numbering_hierarchy_strategy: NumberingHierarchyStrategy,
    ) -> None:
        self.toc_page_range_strategy = toc_page_range_strategy
        self.numbering_hierarchy_strategy = numbering_hierarchy_strategy

    def apply(
        self,
        headers: list[CanonicalElement],
        resolution: SectionHierarchyResolution,
    ) -> None:
        ordered_headers = sorted(headers, key=lambda header: header.order_index)
        header_index_by_id: dict[str, int] = {
            header.element_id: index for index, header in enumerate(ordered_headers)
        }
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
                header_index_by_id,
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
            and not ContextualNumberingResolver._is_simple_numbered_step(header, resolution)
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
        header_index_by_id: dict[str, int],
    ) -> str | None:
        header_index = header_index_by_id[header.element_id]
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
