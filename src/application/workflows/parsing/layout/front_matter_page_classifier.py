import re
from collections import defaultdict

from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)

_BODY_TEXT_LABELS = {
    "caption",
    "list_item",
    "section_header",
    "text",
    "title",
}


class FrontMatterPageClassifier:
    _NUMBERED_HEADING_PATTERN = re.compile(r"^\s*\d+(?:\.\d+)*\b")
    _MIN_BODY_TEXT_CANDIDATES = 3
    _MIN_BODY_TEXT_CHARS = 250

    def classify(self, candidates: list[PageLayoutCandidate]) -> set[int]:
        pages: dict[int, list[PageLayoutCandidate]] = defaultdict(list)
        for candidate in candidates:
            pages[candidate.page_number].append(candidate)

        first_body_page: int | None = None
        for page_number in sorted(pages):
            if self._looks_like_body_page(pages[page_number]):
                first_body_page = page_number
                break

        if first_body_page is None:
            return set()
        return {
            page_number
            for page_number in pages
            if page_number < first_body_page
        }

    def _looks_like_body_page(self, candidates: list[PageLayoutCandidate]) -> bool:
        numbered_headers = 0
        text_like_candidates = 0
        text_characters = 0

        for candidate in candidates:
            normalized_label = (candidate.label or "").strip().lower()
            text = (candidate.text or "").strip()
            if not text:
                continue
            if (
                normalized_label == "section_header"
                and self._NUMBERED_HEADING_PATTERN.match(text) is not None
            ):
                numbered_headers += 1
            if normalized_label in _BODY_TEXT_LABELS:
                text_like_candidates += 1
                text_characters += len(text)

        if numbered_headers > 0:
            return True
        return (
            text_like_candidates >= self._MIN_BODY_TEXT_CANDIDATES
            and text_characters >= self._MIN_BODY_TEXT_CHARS
        )
