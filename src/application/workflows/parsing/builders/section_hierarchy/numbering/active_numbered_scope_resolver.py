from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    numbering_depth,
    parent_numberings,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)


class ActiveNumberedScopeResolver:
    """Parents local headings under the active numbered document scope."""

    _TRUSTED_DEEP_SOURCES = {"layout_heuristic", "toc_page_range"}

    def apply(self, headers, resolution) -> None:
        latest_header_by_number: dict[str, str] = {}
        active_header_by_depth: dict[int, ParsedCanonicalElement] = {}

        for header in sorted(headers, key=lambda item: item.order_index):
            header_id = header.element_id
            number = resolution.header_numberings.get(header_id)
            if number and not self._is_local_numbered_step(
                header,
                number,
                active_header_by_depth,
            ):
                has_numbered_scope = self._attach_numbered_parent(
                    header_id,
                    number,
                    latest_header_by_number,
                    resolution,
                )
                depth = numbering_depth(number) or 1
                if depth == 1 or has_numbered_scope:
                    active_header_by_depth[depth] = header
                    self._clear_deeper_scopes(active_header_by_depth, depth)
                latest_header_by_number[number] = header_id
                continue

            active_parent = self._deepest_active_parent(active_header_by_depth)
            if active_parent is not None:
                self._attach_local_parent(active_parent, header, resolution)

    @staticmethod
    def _attach_numbered_parent(
        header_id: str,
        number: str,
        latest_header_by_number: dict[str, str],
        resolution,
    ) -> bool:
        for parent_number in parent_numberings(number):
            parent_id = latest_header_by_number.get(parent_number)
            if parent_id is not None:
                resolution.explicit_parent_headers[header_id] = parent_id
                return True
        return False

    def _attach_local_parent(self, parent, header, resolution) -> None:
        header_id = header.element_id
        if header_id in resolution.explicit_parent_headers:
            return

        parent_level = resolution.effective_levels.get(parent.element_id, 1)
        current_level = resolution.effective_levels.get(header_id, 1)
        source = resolution.sources.get(header_id, "default")
        if source in self._TRUSTED_DEEP_SOURCES and current_level > parent_level + 1:
            return

        resolution.explicit_parent_headers[header_id] = parent.element_id
        resolution.effective_levels[header_id] = min(parent_level + 1, 6)
        resolution.sources[header_id] = "numbered_scope"

    @staticmethod
    def _is_local_numbered_step(
        header: ParsedCanonicalElement,
        number: str,
        active_header_by_depth: dict[int, ParsedCanonicalElement],
    ) -> bool:
        if numbering_depth(number) != 1 or not active_header_by_depth:
            return False
        text = (header.text or "").strip()
        return text.startswith(f"{number}.") and max(active_header_by_depth) >= 2

    @staticmethod
    def _deepest_active_parent(
        active_header_by_depth: dict[int, ParsedCanonicalElement],
    ) -> ParsedCanonicalElement | None:
        if not active_header_by_depth:
            return None
        return active_header_by_depth[max(active_header_by_depth)]

    @staticmethod
    def _clear_deeper_scopes(
        active_header_by_depth: dict[int, ParsedCanonicalElement],
        depth: int,
    ) -> None:
        for candidate_depth in [
            value for value in active_header_by_depth if value > depth
        ]:
            active_header_by_depth.pop(candidate_depth, None)
