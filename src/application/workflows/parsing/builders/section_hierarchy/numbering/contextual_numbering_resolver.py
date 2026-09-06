from src.application.workflows.parsing.builders.section_hierarchy.numbering.active_numbered_scope_resolver import (
    ActiveNumberedScopeResolver,
)
from src.application.workflows.parsing.builders.section_hierarchy.numbering.forward_numbered_parent_resolver import (
    ForwardNumberedParentResolver,
)
from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    extract_heading_number,
    numbering_depth,
)
from src.application.workflows.parsing.builders.section_hierarchy.numbering.section_parent_link_validator import (
    SectionParentLinkValidator,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)


class ContextualNumberingResolver:
    def __init__(
        self,
        *,
        toc_page_range_strategy,
        numbering_hierarchy_strategy,
        scope_resolver: ActiveNumberedScopeResolver | None = None,
        forward_parent_resolver: ForwardNumberedParentResolver | None = None,
        parent_link_validator: SectionParentLinkValidator | None = None,
    ) -> None:
        self.toc_page_range_strategy = toc_page_range_strategy
        self.numbering_hierarchy_strategy = numbering_hierarchy_strategy
        self.scope_resolver = scope_resolver or ActiveNumberedScopeResolver()
        self.forward_parent_resolver = forward_parent_resolver or ForwardNumberedParentResolver()
        self.parent_link_validator = parent_link_validator or SectionParentLinkValidator()

    def apply(self, headers, resolution) -> None:
        ordered_headers = sorted(headers, key=lambda header: header.order_index)
        self.scope_resolver.apply(ordered_headers, resolution)
        self.forward_parent_resolver.apply(ordered_headers, resolution)
        self._attach_chapter_markers(ordered_headers, resolution)
        self.parent_link_validator.validate(
            ordered_headers,
            resolution.explicit_parent_headers,
        )

    def _attach_chapter_markers(
        self,
        ordered_headers: list[ParsedCanonicalElement],
        resolution,
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
                candidate_page = candidate.page_start or candidate.page_end
                if candidate_page != page_no:
                    break
                if extract_heading_number(candidate.text) != number:
                    continue
                if not (candidate.text or "").casefold().startswith("chapter "):
                    continue

                resolution.explicit_parent_headers[header_id] = candidate.element_id
                parent_level = resolution.effective_levels.get(candidate.element_id, 1)
                resolution.effective_levels[header_id] = min(parent_level + 1, 6)
                resolution.sources[header_id] = "toc_context"
                break
