import re

from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
    is_contents_title,
    is_reference_title,
    looks_like_boilerplate,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ElementType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class SectionChunkSkipper:
    def __init__(self, *, text_splitter: ChunkTextSplitter) -> None:
        self.text_splitter = text_splitter

    def should_skip_section(
        self,
        *,
        document_title: str | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
    ) -> bool:
        path_titles = [section.title, *section.section_path]
        if any(
            is_contents_title(title) or is_reference_title(title)
            for title in path_titles
        ):
            return True

        return self._is_front_matter_section(
            document_title=document_title,
            section=section,
            elements=elements,
        )

    def _is_front_matter_section(
        self,
        *,
        document_title: str | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
    ) -> bool:
        if section.parent_section_id is not None:
            return False

        page_end = section.source.page_end
        if page_end is not None and page_end > 2:
            return False

        content_elements = [
            element
            for element in elements
            if element.element_type
            not in {ElementType.SECTION_HEADER, ElementType.PICTURE, ElementType.TABLE}
            and element.text
            and element.text.strip()
        ]
        if not content_elements:
            return False

        if any(
            element.element_type in {ElementType.LIST_ITEM, ElementType.CODE}
            for element in content_elements
        ):
            return False

        texts = [
            clean_chunk_text(element.text)
            for element in content_elements
            if clean_chunk_text(element.text)
        ]
        if not texts:
            return True

        boilerplate_hits = sum(1 for text in texts if looks_like_boilerplate(text))
        longest_text_tokens = max(
            self.text_splitter.count_tokens(text)
            for text in texts
        )
        total_tokens = sum(
            self.text_splitter.count_tokens(text)
            for text in texts
        )

        if boilerplate_hits >= 2:
            return True

        if any(
            self.text_splitter.count_tokens(text) >= 18 and re.search(r"[.!?]", text)
            for text in texts
        ):
            return False

        if boilerplate_hits > 0 and total_tokens <= self.text_splitter.max_chunk_tokens // 2:
            return True

        if not document_title:
            return False

        return (
            page_end == 1
            and len(texts) >= 3
            and longest_text_tokens <= 12
            and total_tokens <= self.text_splitter.max_chunk_tokens // 4
        )
