from dataclasses import dataclass, field

from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates import (
    HeadingCandidateAssessment,
    HeadingCandidateRole,
    HeadingCandidateRoleResolver,
)
from src.application.workflows.parsing.builders.section_hierarchy.numbering.contextual_numbering_resolver import (
    ContextualNumberingResolver,
)
from src.application.workflows.parsing.builders.section_hierarchy.strategies.heading_level_strategy import (
    HeadingLevelStrategy,
)
from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    extract_heading_number,
)
from src.application.workflows.parsing.builders.section_hierarchy.strategies.layout_heuristic_strategy import (
    LayoutHeuristicStrategy,
)
from src.application.workflows.parsing.builders.section_hierarchy.strategies.numbering_hierarchy_strategy import (
    NumberingHierarchyStrategy,
)
from src.application.workflows.parsing.builders.section_hierarchy.numbering.section_level_normalizer import (
    levels_are_weak,
    normalize_levels,
)
from src.application.workflows.parsing.builders.section_hierarchy.strategies.toc_page_range_strategy import (
    TocPageRangeStrategy,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc import (
    TocOutline,
)
from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement
from src.application.workflows.parsing.parsing_value_coercion import (
    coerce_positive_int,
)
from src.domain.common import ElementType


@dataclass(slots=True)
class SectionHierarchyResolution:
    effective_levels: dict[str, int] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)
    raw_levels: dict[str, int | None] = field(default_factory=dict)
    header_numberings: dict[str, str] = field(default_factory=dict)
    explicit_parent_headers: dict[str, str] = field(default_factory=dict)
    heading_assessments: dict[str, HeadingCandidateAssessment] = field(
        default_factory=dict
    )
    toc_outline: TocOutline | None = None


class SectionHierarchyResolver:
    def __init__(
        self,
        *,
        heading_level_strategy: HeadingLevelStrategy | None = None,
        toc_page_range_strategy: TocPageRangeStrategy | None = None,
        numbering_hierarchy_strategy: NumberingHierarchyStrategy | None = None,
        layout_heuristic_strategy: LayoutHeuristicStrategy | None = None,
        heading_candidate_role_resolver: HeadingCandidateRoleResolver | None = None,
    ) -> None:
        self.heading_level_strategy = heading_level_strategy or HeadingLevelStrategy()
        self.toc_page_range_strategy = toc_page_range_strategy or TocPageRangeStrategy()
        self.numbering_hierarchy_strategy = (
            numbering_hierarchy_strategy or NumberingHierarchyStrategy()
        )
        self.layout_heuristic_strategy = layout_heuristic_strategy or LayoutHeuristicStrategy()
        self.heading_candidate_role_resolver = (
            heading_candidate_role_resolver or HeadingCandidateRoleResolver()
        )
        self._contextual_numbering_resolver = ContextualNumberingResolver(
            toc_page_range_strategy=self.toc_page_range_strategy,
            numbering_hierarchy_strategy=self.numbering_hierarchy_strategy,
        )

    def resolve(
        self,
        canonical_elements: list[ParsedCanonicalElement],
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
                header.element_id: coerce_positive_int(
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

        current_is_weak = levels_are_weak(resolution.effective_levels)
        toc_outline = self.toc_page_range_strategy.build_outline(
            headers,
            canonical_elements,
        )
        if toc_outline.entries:
            resolution.toc_outline = toc_outline
            toc_levels = self.toc_page_range_strategy.assign_levels_from_outline(
                headers,
                toc_outline,
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

        resolution.effective_levels = normalize_levels(headers, resolution.effective_levels)
        resolution.heading_assessments = self.heading_candidate_role_resolver.resolve(
            headers=headers,
            elements=canonical_elements,
            hierarchy_resolution=resolution,
        )
        outline_headers = self._retain_outline_candidates(headers, resolution)
        if outline_headers:
            resolution.effective_levels = normalize_levels(
                outline_headers,
                resolution.effective_levels,
            )
            self._contextual_numbering_resolver.apply(outline_headers, resolution)
        if resolution.toc_outline is not None:
            resolution.toc_outline.header_numberings = dict(
                resolution.header_numberings
            )
        return resolution

    @staticmethod
    def _retain_outline_candidates(
        headers: list[ParsedCanonicalElement],
        resolution: SectionHierarchyResolution,
    ) -> list[ParsedCanonicalElement]:
        outline_ids = {
            header_id
            for header_id, assessment in resolution.heading_assessments.items()
            if assessment.role == HeadingCandidateRole.OUTLINE_SECTION
        }
        for header_id in tuple(resolution.effective_levels):
            if header_id in outline_ids:
                continue
            resolution.effective_levels.pop(header_id, None)
            resolution.sources.pop(header_id, None)
            resolution.explicit_parent_headers.pop(header_id, None)
        return [header for header in headers if header.element_id in outline_ids]
