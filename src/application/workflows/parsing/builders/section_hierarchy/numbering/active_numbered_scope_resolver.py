from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    has_embedded_item_numbering,
    numbering_depth,
    parent_numberings,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)


_NON_OUTLINE_ROLES = {
    "caption",
    "local_label",
    "noise",
    "table_category",
}


class ActiveNumberedScopeResolver:
    """Parents local headings under the active numbered document scope."""

    _TRUSTED_DEEP_SOURCES = {"layout_heuristic", "toc_page_range"}

    def apply(self, headers, resolution) -> None:
        latest_header_by_number: dict[str, str] = {}
        active_header_by_depth: dict[int, ParsedCanonicalElement] = {}

        for header in sorted(headers, key=lambda item: item.order_index):
            header_id = header.element_id
            number = resolution.header_numberings.get(header_id)
            if number and not self._is_embedded_numbered_heading(
                header,
                number,
                active_header_by_depth,
                source=resolution.sources.get(header_id),
                effective_level=resolution.effective_levels.get(header_id),
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
    def _is_embedded_numbered_heading(
        header: ParsedCanonicalElement,
        number: str,
        active_header_by_depth: dict[int, ParsedCanonicalElement],
        *,
        source: str | None,
        effective_level: int | None,
    ) -> bool:
        candidate_role = header.metadata.get("heading_candidate_role")
        if candidate_role == "outline_section":
            return False
        if candidate_role in _NON_OUTLINE_ROLES:
            return True
        if numbering_depth(number) != 1 or not active_header_by_depth:
            return False
        del source, effective_level
        text = (header.text or "").strip()
        return max(active_header_by_depth) >= 2 and (
            text.startswith(f"{number}.")
            or has_embedded_item_numbering(text)
        )

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
        for candidate_depth in [value for value in active_header_by_depth if value > depth]:
            active_header_by_depth.pop(candidate_depth, None)
