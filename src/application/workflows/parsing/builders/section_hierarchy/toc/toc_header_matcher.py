from src.application.workflows.parsing.builders.section_hierarchy.heading_numbering import (
    extract_heading_number,
    strip_heading_number,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry import (
    TocEntry,
    normalize_toc_title,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement


class TocHeaderMatcher:
    """Matches parsed TOC entries to actual document section headers."""

    @staticmethod
    def match_entry_to_header(
        entry: TocEntry,
        headers: list[CanonicalElement],
        matched_header_ids: set[str],
    ) -> CanonicalElement | None:
        candidates = [
            header
            for header in headers
            if header.element_id not in matched_header_ids
        ]

        for candidate in candidates:
            candidate_number = extract_heading_number(candidate.text)
            candidate_title = normalize_toc_title(strip_heading_number(candidate.text))
            if (
                entry.numbering
                and candidate_number == entry.numbering
                and candidate_title == entry.normalized_title
            ):
                return candidate

        for candidate in candidates:
            candidate_title = normalize_toc_title(strip_heading_number(candidate.text))
            if candidate_title == entry.normalized_title:
                return candidate

        for candidate in candidates:
            candidate_title = normalize_toc_title(strip_heading_number(candidate.text))
            if (
                candidate_title
                and (
                    candidate_title in entry.normalized_title
                    or entry.normalized_title in candidate_title
                )
            ):
                return candidate

        return None
