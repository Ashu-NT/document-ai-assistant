import re

from src.application.workflows.parsing.builders.section_hierarchy.section_hierarchy_strategy import (
    SectionHierarchyStrategy,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import ElementType


class LayoutHeuristicStrategy(SectionHierarchyStrategy):
    name = "layout_heuristic"
    _UMBRELLA_WORDS = {
        "controls",
        "functions",
        "loading",
        "measurements",
        "properties",
        "types",
        "waveforms",
    }

    def can_apply(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> bool:
        del elements
        return bool(headers and (current_levels or self._has_numbered_heading(headers)))

    def assign_levels(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> dict[str, int]:
        levels = dict(current_levels or {})
        sorted_headers = sorted(headers, key=lambda header: header.order_index)

        for header in sorted_headers:
            numbered_level = self._infer_numbered_level(header.text)
            if numbered_level is not None:
                levels[header.element_id] = numbered_level

        text_between_cache = self._build_text_between_cache(elements)
        top_level_anchor_ids = self._build_top_level_anchor_ids(sorted_headers, levels)

        for index, header in enumerate(sorted_headers):
            current_level = levels.get(header.element_id, 1)
            if current_level == 1:
                continue

            current_root_id = top_level_anchor_ids[index]
            if current_root_id is None:
                continue

            for candidate_index in range(index - 1, -1, -1):
                candidate = sorted_headers[candidate_index]
                candidate_root_id = top_level_anchor_ids[candidate_index]
                if candidate_root_id != current_root_id:
                    continue

                candidate_level = levels.get(candidate.element_id, 1)
                if candidate_level >= current_level and candidate.element_id != current_root_id:
                    pass

                if not self._should_nest_under(candidate, header, text_between_cache):
                    continue

                levels[header.element_id] = min(candidate_level + 1, 6)
                break

        return levels

    @staticmethod
    def _has_numbered_heading(headers: list[CanonicalElement]) -> bool:
        return any(
            LayoutHeuristicStrategy._infer_numbered_level(header.text) is not None
            for header in headers
        )

    @staticmethod
    def _infer_numbered_level(text: str | None) -> int | None:
        if not text:
            return None

        match = re.match(r"^\s*(\d+(?:\.\d+)*)\b", text)
        if match is not None:
            return len(match.group(1).split("."))

        normalized = text.casefold().strip()
        if normalized.startswith("chapter ") or normalized.startswith("section "):
            return 1

        return None

    def _should_nest_under(
        self,
        candidate: CanonicalElement,
        current: CanonicalElement,
        text_between_cache: dict[tuple[str, str], int],
    ) -> bool:
        if candidate.element_id == current.element_id:
            return False

        candidate_title = self._normalize_title(candidate.text)
        current_title = self._normalize_title(current.text)
        if not candidate_title or not current_title:
            return False

        candidate_page = candidate.page_start or candidate.page_end
        current_page = current.page_start or current.page_end
        if candidate_page is not None and current_page is not None:
            if current_page < candidate_page or current_page - candidate_page > 1:
                return False

        if current_title.endswith(f" {candidate_title}") or current_title.startswith(f"{candidate_title} "):
            return True

        candidate_words = candidate_title.split()
        current_words = current_title.split()
        text_between = text_between_cache.get((candidate.element_id, current.element_id), 0)

        if (
            candidate_words
            and candidate_words[-1] in self._UMBRELLA_WORDS
            and len(candidate_words) == 1
            and len(current_words) <= 4
            and text_between <= 220
        ):
            return True

        return False

    @staticmethod
    def _build_text_between_cache(
        elements: list[CanonicalElement],
    ) -> dict[tuple[str, str], int]:
        ordered = sorted(elements, key=lambda element: element.order_index)
        cache: dict[tuple[str, str], int] = {}
        headers: list[tuple[CanonicalElement, int]] = [
            (element, index)
            for index, element in enumerate(ordered)
            if element.element_type == ElementType.SECTION_HEADER
        ]
        if len(headers) < 2:
            return cache

        prefix_text_lengths = [0]
        running_total = 0
        text_like_types = {
            ElementType.TEXT,
            ElementType.CAPTION,
            ElementType.LIST_ITEM,
        }
        for element in ordered:
            if element.element_type in text_like_types:
                running_total += len(element.text or "")
            prefix_text_lengths.append(running_total)

        for index, (header, header_position) in enumerate(headers):
            start_prefix_index = header_position + 1
            for next_header, next_header_position in headers[index + 1 :]:
                text_length = (
                    prefix_text_lengths[next_header_position]
                    - prefix_text_lengths[start_prefix_index]
                )
                cache[(header.element_id, next_header.element_id)] = text_length

        return cache

    @staticmethod
    def _build_top_level_anchor_ids(
        headers: list[CanonicalElement],
        levels: dict[str, int],
    ) -> list[str | None]:
        anchors: list[str | None] = []
        current_anchor_id: str | None = None

        for header in headers:
            if levels.get(header.element_id, 1) == 1:
                current_anchor_id = header.element_id
            anchors.append(current_anchor_id)

        return anchors

    @staticmethod
    def _top_level_anchor_id(
        index: int,
        headers: list[CanonicalElement],
        levels: dict[str, int],
    ) -> str | None:
        for candidate in reversed(headers[: index + 1]):
            if levels.get(candidate.element_id, 1) == 1:
                return candidate.element_id

        return None

    @staticmethod
    def _normalize_title(value: str | None) -> str:
        if not value:
            return ""

        text = value.casefold()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
