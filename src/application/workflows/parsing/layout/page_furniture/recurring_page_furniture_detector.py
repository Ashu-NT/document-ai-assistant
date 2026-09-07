from __future__ import annotations

import math
import re
import unicodedata
from collections import defaultdict

from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)
from src.application.workflows.parsing.layout.page_furniture.page_furniture_role import (
    PageFurnitureRole,
)

_SPACE_RE = re.compile(r"\s+")
_DATE_RE = re.compile(r"\b\d{1,4}[./-]\d{1,2}[./-]\d{1,4}\b")
_PAGE_FRACTION_RE = re.compile(r"\b\d+\s*/\s*\d+\b")
_NUMBER_RE = re.compile(r"\d+")
_ELIGIBLE_LABELS = frozenset(
    {"caption", "footnote", "list_item", "section_header", "text", "title"}
)


class RecurringPageFurnitureDetector:
    """Detects repeated marginal content without relying on document vocabulary."""

    _PAGE_EDGE_RATIO = 0.10
    _MAX_VERTICAL_SPREAD = 0.025
    _MIN_SPAN_DENSITY = 0.45
    _MIN_DOCUMENT_COVERAGE = 0.50

    def detect(
        self,
        *,
        candidates: list[PageLayoutCandidate],
        page_sizes: dict[int, tuple[float | None, float | None]],
        reference_candidates: list[PageLayoutCandidate] | None = None,
    ) -> dict[str, PageFurnitureRole]:
        page_numbers = set(page_sizes) or {
            candidate.page_number for candidate in candidates
        }
        if len(page_numbers) < 2:
            return {}

        groups: dict[
            tuple[PageFurnitureRole, str, int],
            list[tuple[PageLayoutCandidate, float]],
        ] = defaultdict(list)
        target_refs = {candidate.element_ref for candidate in candidates}
        all_candidates = [*candidates, *(reference_candidates or [])]
        for candidate in all_candidates:
            classified = self._classify(candidate, page_sizes)
            if classified is None:
                continue
            role, vertical_anchor, horizontal_bucket = classified
            signature = self._signature(candidate.text)
            if not signature:
                continue
            groups[(role, signature, horizontal_bucket)].append(
                (candidate, vertical_anchor)
            )

        minimum_occurrences = self._minimum_occurrences(len(page_numbers))
        detected: dict[str, PageFurnitureRole] = {}
        for (role, _signature, _bucket), entries in groups.items():
            entries_by_page = {entry[0].page_number: entry for entry in entries}
            if len(entries_by_page) < minimum_occurrences:
                continue
            pages = sorted(entries_by_page)
            page_span = pages[-1] - pages[0] + 1
            span_density = len(pages) / max(1, page_span)
            document_coverage = len(pages) / len(page_numbers)
            anchors = [entry[1] for entry in entries_by_page.values()]
            if max(anchors) - min(anchors) > self._MAX_VERTICAL_SPREAD:
                continue
            if (
                span_density < self._MIN_SPAN_DENSITY
                and document_coverage < self._MIN_DOCUMENT_COVERAGE
            ):
                continue
            for candidate, _anchor in entries_by_page.values():
                if candidate.element_ref in target_refs:
                    detected[candidate.element_ref] = role
        return detected

    def _classify(
        self,
        candidate: PageLayoutCandidate,
        page_sizes: dict[int, tuple[float | None, float | None]],
    ) -> tuple[PageFurnitureRole, float, int] | None:
        explicit_role = self._explicit_role(candidate)
        if candidate.bbox is None or (
            explicit_role is None
            and candidate.label.casefold() not in _ELIGIBLE_LABELS
        ):
            return None
        page_width, page_height = page_sizes.get(candidate.page_number, (None, None))
        if not page_width or not page_height or page_width <= 0 or page_height <= 0:
            return None

        top_ratio = candidate.top_y() / page_height
        bottom_ratio = candidate.bottom_y() / page_height
        if explicit_role is not None:
            role = explicit_role
            vertical_anchor = (
                top_ratio
                if role == PageFurnitureRole.RUNNING_HEADER
                else bottom_ratio
            )
        elif top_ratio >= 1.0 - self._PAGE_EDGE_RATIO:
            role = PageFurnitureRole.RUNNING_HEADER
            vertical_anchor = top_ratio
        elif bottom_ratio <= self._PAGE_EDGE_RATIO:
            role = PageFurnitureRole.RUNNING_FOOTER
            vertical_anchor = bottom_ratio
        else:
            return None

        center_x = candidate.center_x() or 0.0
        horizontal_bucket = min(2, max(0, int((center_x / page_width) * 3)))
        return role, vertical_anchor, horizontal_bucket

    @staticmethod
    def _explicit_role(
        candidate: PageLayoutCandidate,
    ) -> PageFurnitureRole | None:
        label = candidate.label.casefold()
        if label == "page_header":
            return PageFurnitureRole.RUNNING_HEADER
        if label == "page_footer":
            return PageFurnitureRole.RUNNING_FOOTER
        return None

    @staticmethod
    def _minimum_occurrences(page_count: int) -> int:
        if page_count <= 4:
            return 2
        return min(8, max(3, math.ceil(page_count * 0.05)))

    @staticmethod
    def _signature(value: str | None) -> str:
        text = unicodedata.normalize("NFKC", str(value or "")).casefold()
        text = _DATE_RE.sub(" {date} ", text)
        text = _PAGE_FRACTION_RE.sub(" {page} ", text)
        text = _NUMBER_RE.sub(" {number} ", text)
        return _SPACE_RE.sub(" ", text).strip(" -|:;,.\t\r\n")
