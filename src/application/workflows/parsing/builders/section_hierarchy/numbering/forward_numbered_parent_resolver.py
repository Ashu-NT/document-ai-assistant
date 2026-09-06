from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    numbering_depth,
    parent_numberings,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)


class ForwardNumberedParentResolver:
    """Repairs same-page child-before-parent PDF reading-order inversions."""

    def apply(self, headers, resolution) -> None:
        ordered_headers = sorted(headers, key=lambda header: header.order_index)
        for index, header in enumerate(ordered_headers):
            header_id = header.element_id
            number = resolution.header_numberings.get(header_id)
            if header_id in resolution.explicit_parent_headers or numbering_depth(number) in {
                None,
                1,
            }:
                continue

            parent_id = self._same_page_forward_parent(
                header=header,
                parent_numbers=parent_numberings(number),
                candidates=ordered_headers[index + 1 :],
                numberings=resolution.header_numberings,
            )
            if parent_id is None:
                continue

            resolution.explicit_parent_headers[header_id] = parent_id
            parent_level = resolution.effective_levels.get(parent_id, 1)
            resolution.effective_levels[header_id] = min(parent_level + 1, 6)
            resolution.sources[header_id] = "forward_numbered_scope"

    @staticmethod
    def _same_page_forward_parent(
        *,
        header: ParsedCanonicalElement,
        parent_numbers: list[str],
        candidates: list[ParsedCanonicalElement],
        numberings: dict[str, str],
    ) -> str | None:
        page = header.page_start or header.page_end
        if page is None:
            return None

        for parent_number in parent_numbers:
            for candidate in candidates:
                candidate_page = candidate.page_start or candidate.page_end
                if candidate_page != page:
                    continue
                if numberings.get(candidate.element_id) == parent_number:
                    return candidate.element_id
        return None
