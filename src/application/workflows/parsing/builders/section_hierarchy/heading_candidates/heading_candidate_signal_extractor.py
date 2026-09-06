import re

from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_document_context import (
    HeadingCandidateDocumentContext,
)
from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_signals import (
    HeadingCandidateSignals,
)
from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    has_embedded_item_numbering,
    numbering_depth,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_heading_recognizer import (
    TocHeadingRecognizer,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)
from src.domain.common import ElementType


_CAPTION_PATTERN = re.compile(
    r"^(?:fig(?:ure)?|table|diagram|drawing|image|plate)"
    r"(?:\s+(?:no\.?\s*)?[a-z]?\d[\w.-]*|\s*[.:-]\s*\S)",
    re.IGNORECASE,
)
_LOW_SIGNAL_PATTERN = re.compile(r"^[\W_\d]+$", re.UNICODE)


class HeadingCandidateSignalExtractor:
    def extract(
        self,
        *,
        context: HeadingCandidateDocumentContext,
        header_index: int,
        active_header: ParsedCanonicalElement | None,
        active_numberings: dict[int, str],
    ) -> HeadingCandidateSignals:
        header = context.headers[header_index]
        numbering = context.numbering_for(header)
        depth = numbering_depth(numbering)
        active_depth = max(active_numberings, default=None)
        toc_entry = context.toc_entry_for(header.element_id)
        normalized_title = context.normalized_title(header.element_id)
        header_page = header.page_start or header.page_end
        next_element = context.next_content(header)
        next_page = (
            next_element.page_start or next_element.page_end
            if next_element is not None
            else None
        )
        toc_page_distance = (
            abs(header_page - toc_entry.start_page)
            if toc_entry is not None and header_page is not None
            else None
        )
        numbering_compatible = self._numbering_compatible(
            numbering,
            active_numberings,
        )
        document_index_heading = TocHeadingRecognizer.matches(header.text)
        return HeadingCandidateSignals(
            numbering=numbering,
            numbering_depth=depth,
            active_scope_depth=active_depth,
            numbering_compatible=numbering_compatible,
            implausible_hierarchy_jump=self._is_implausible_jump(
                depth=depth,
                active_depth=active_depth,
                numbering_compatible=numbering_compatible,
                toc_matched=toc_entry is not None,
            ),
            toc_matched=toc_entry is not None,
            toc_title_exact=bool(
                toc_entry is not None
                and normalized_title == toc_entry.normalized_title
            ),
            toc_number_exact=bool(
                toc_entry is not None
                and toc_entry.numbering
                and toc_entry.numbering == numbering
            ),
            toc_page_close=toc_page_distance is not None and toc_page_distance <= 3,
            document_index_heading=document_index_heading,
            native_heading_level=self._positive_int(
                header.metadata.get("heading_level")
            ),
            has_descendant_pattern=context.has_descendant_pattern(header_index),
            has_sibling_pattern=context.has_sibling_pattern(header_index),
            next_element_type=(
                next_element.element_type if next_element is not None else None
            ),
            next_element_same_page=bool(
                header_page is not None and header_page == next_page
            ),
            next_element_order_gap=(
                next_element.order_index - header.order_index
                if next_element is not None
                else None
            ),
            nearby_table_same_page=context.has_nearby_element_type(
                header,
                ElementType.TABLE,
            ),
            nearby_picture_same_page=context.has_nearby_element_type(
                header,
                ElementType.PICTURE,
            ),
            repeated_title_count=context.repeated_title_count(header.element_id),
            nearby_repeated_title=context.has_nearby_repeated_title(header_index),
            embedded_item_numbering=has_embedded_item_numbering(header.text),
            layout_prominent=context.has_prominent_height(header),
            indented_from_active=self._is_indented(header, active_header),
            page_continuous=self._is_page_continuous(header, active_header),
            caption_like=bool(
                not document_index_heading
                and _CAPTION_PATTERN.match((header.text or "").strip())
            ),
            noise_like=self._is_noise(header, normalized_title),
            title_word_count=len(normalized_title.split()),
            ends_with_colon=(header.text or "").rstrip().endswith(":"),
        )

    @staticmethod
    def _numbering_compatible(
        numbering: str | None,
        active_numberings: dict[int, str],
    ) -> bool | None:
        depth = numbering_depth(numbering)
        if depth is None:
            return None
        if not active_numberings:
            return True
        if depth > 1:
            return active_numberings.get(depth - 1) == numbering.rsplit(".", 1)[0]

        active_root = active_numberings.get(1)
        if active_root is None:
            return True
        try:
            return int(numbering) == int(active_root) + 1
        except (TypeError, ValueError):
            return False

    @staticmethod
    def _is_implausible_jump(
        *,
        depth: int | None,
        active_depth: int | None,
        numbering_compatible: bool | None,
        toc_matched: bool,
    ) -> bool:
        if depth is None or active_depth is None:
            return False
        if depth > active_depth + 1:
            return True
        return (
            depth == 1
            and active_depth >= 2
            and numbering_compatible is False
            and not toc_matched
        )

    @staticmethod
    def _is_indented(
        header: ParsedCanonicalElement,
        active_header: ParsedCanonicalElement | None,
    ) -> bool:
        if header.bbox is None or active_header is None or active_header.bbox is None:
            return False
        return header.bbox.x1 >= active_header.bbox.x1 + 12

    @staticmethod
    def _is_page_continuous(
        header: ParsedCanonicalElement,
        active_header: ParsedCanonicalElement | None,
    ) -> bool:
        if active_header is None:
            return True
        page = header.page_start or header.page_end
        active_page = active_header.page_start or active_header.page_end
        return bool(
            page is not None
            and active_page is not None
            and 0 <= page - active_page <= 2
        )

    @staticmethod
    def _is_noise(header: ParsedCanonicalElement, normalized_title: str) -> bool:
        content_layer = str(header.metadata.get("content_layer") or "").casefold()
        return bool(
            not normalized_title
            or _LOW_SIGNAL_PATTERN.fullmatch((header.text or "").strip())
            or content_layer in {"furniture", "background"}
        )

    @staticmethod
    def _positive_int(value) -> int | None:
        return value if isinstance(value, int) and value > 0 else None
