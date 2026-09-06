from dataclasses import dataclass

from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    extract_heading_number,
    strip_heading_number,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry import (
    TocEntry,
    normalize_toc_title,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)


@dataclass(slots=True, frozen=True)
class _ScoredHeader:
    header: ParsedCanonicalElement
    title_quality: int
    page_distance: int


class TocHeaderMatcher:
    """Matches TOC entries with title, numbering, and page-position evidence."""

    _MAX_PAGE_DISTANCE = 24

    @classmethod
    def match_entry_to_header(
        cls,
        entry: TocEntry,
        headers: list[ParsedCanonicalElement],
        matched_header_ids: set[str],
    ) -> ParsedCanonicalElement | None:
        scored = [
            match
            for header in headers
            if header.element_id not in matched_header_ids
            if (match := cls._score(entry, header)) is not None
        ]
        if not scored:
            return None

        scored.sort(
            key=lambda item: (
                -item.title_quality,
                item.page_distance,
                item.header.order_index,
            )
        )
        winner = scored[0]
        if len(scored) > 1 and cls._materially_tied(winner, scored[1]):
            return None
        return winner.header

    @staticmethod
    def _score(
        entry: TocEntry,
        header: ParsedCanonicalElement,
    ) -> _ScoredHeader | None:
        candidate_number = extract_heading_number(header.text)
        candidate_title = normalize_toc_title(strip_heading_number(header.text))
        if not candidate_title:
            return None
        if (
            entry.numbering is not None
            and candidate_number is not None
            and candidate_number != entry.numbering
        ):
            return None

        exact_title = candidate_title == entry.normalized_title
        same_number = bool(entry.numbering and candidate_number == entry.numbering)
        contains_title = (
            candidate_title in entry.normalized_title
            or entry.normalized_title in candidate_title
        )
        if same_number and exact_title:
            quality = 4
        elif exact_title:
            quality = 3
        elif same_number and contains_title:
            quality = 2
        elif contains_title:
            quality = 1
        else:
            return None

        page_no = header.page_start or header.page_end
        page_distance = (
            abs(page_no - entry.start_page)
            if page_no is not None
            else 10_000
        )
        if page_distance > TocHeaderMatcher._MAX_PAGE_DISTANCE:
            return None
        return _ScoredHeader(
            header=header,
            title_quality=quality,
            page_distance=page_distance,
        )

    @staticmethod
    def _materially_tied(left: _ScoredHeader, right: _ScoredHeader) -> bool:
        return (
            left.title_quality == right.title_quality
            and left.page_distance == right.page_distance
        )
