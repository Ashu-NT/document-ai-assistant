from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)


class SectionParentLinkValidator:
    def __init__(self, *, max_depth: int = 6) -> None:
        self.max_depth = max(1, max_depth)

    def validate(
        self,
        headers: list[ParsedCanonicalElement],
        parent_links: dict[str, str],
    ) -> None:
        order_by_id = {
            header.element_id: header.order_index
            for header in headers
        }
        for child_id in list(parent_links):
            parent_id = parent_links.get(child_id)
            if not self._is_backward_link(child_id, parent_id, order_by_id):
                parent_links.pop(child_id, None)
                continue
            if self._has_cycle(child_id, parent_links):
                parent_links.pop(child_id, None)
                continue
            if self._depth(child_id, parent_links) > self.max_depth:
                parent_links.pop(child_id, None)

    @staticmethod
    def _is_backward_link(
        child_id: str,
        parent_id: str | None,
        order_by_id: dict[str, int],
    ) -> bool:
        if parent_id is None:
            return False
        child_order = order_by_id.get(child_id)
        parent_order = order_by_id.get(parent_id)
        return bool(
            child_order is not None
            and parent_order is not None
            and parent_order < child_order
        )

    @staticmethod
    def _has_cycle(start_id: str, parent_links: dict[str, str]) -> bool:
        visited = {start_id}
        current_id = start_id
        while current_id in parent_links:
            current_id = parent_links[current_id]
            if current_id in visited:
                return True
            visited.add(current_id)
        return False

    @staticmethod
    def _depth(start_id: str, parent_links: dict[str, str]) -> int:
        depth = 1
        current_id = start_id
        visited = {start_id}
        while current_id in parent_links:
            current_id = parent_links[current_id]
            if current_id in visited:
                return depth + 1
            visited.add(current_id)
            depth += 1
        return depth
