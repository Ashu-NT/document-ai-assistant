import re

from src.application.workflows.parsing.builders.chunking.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.chunk_payload import ChunkPayload
from src.application.workflows.parsing.builders.chunking.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.chunking_utils import (
    clean_chunk_text,
    is_contents_title,
    is_low_value_fragment,
    is_reference_title,
    looks_like_boilerplate,
    unique_preserve_order,
)
from src.domain.common import ChunkType, ElementType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class SectionChunkBuilder:
    def __init__(
        self,
        *,
        text_splitter: ChunkTextSplitter | None = None,
        max_chunk_tokens: int = 200,
        chunk_overlap: int = 20,
        min_section_text_length: int = 20,
    ) -> None:
        self.text_splitter = text_splitter or ChunkTextSplitter(
            max_chunk_tokens=max_chunk_tokens,
            chunk_overlap=chunk_overlap,
        )
        self.min_section_text_length = min_section_text_length

    def build_chunk_payloads(
        self,
        *,
        document_title: str | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
    ) -> list[ChunkPayload]:
        if not elements:
            return []

        if self._should_skip_chunk_section(
            document_title=document_title,
            section=section,
            elements=elements,
        ):
            return []

        fragments = self._build_section_fragments(elements)
        if not fragments:
            return []

        return self._chunk_payloads_from_fragments(
            document_title=document_title,
            section_id=section.section_id,
            section_path=section.section_path,
            fragments=fragments,
        )

    def _chunk_payloads_from_fragments(
        self,
        *,
        document_title: str | None,
        section_id: str,
        section_path: list[str],
        fragments: list[ChunkFragment],
    ) -> list[ChunkPayload]:
        chunk_payloads: list[ChunkPayload] = []
        current_fragments: list[ChunkFragment] = []

        for fragment in fragments:
            if fragment.standalone:
                if current_fragments:
                    chunk_payloads.append(
                        self._make_chunk_payload(
                            document_title=document_title,
                            section_id=section_id,
                            section_path=section_path,
                            fragments=current_fragments,
                        )
                    )
                    current_fragments = []

                chunk_payloads.extend(
                    self._split_fragment_to_chunk_payloads(
                        document_title=document_title,
                        section_id=section_id,
                        section_path=section_path,
                        fragment=fragment,
                    )
                )
                continue

            if fragment.token_count > self.text_splitter.max_chunk_tokens:
                if current_fragments:
                    chunk_payloads.append(
                        self._make_chunk_payload(
                            document_title=document_title,
                            section_id=section_id,
                            section_path=section_path,
                            fragments=current_fragments,
                        )
                    )
                    current_fragments = []

                chunk_payloads.extend(
                    self._split_fragment_to_chunk_payloads(
                        document_title=document_title,
                        section_id=section_id,
                        section_path=section_path,
                        fragment=fragment,
                    )
                )
                continue

            candidate_fragments = [*current_fragments, fragment]
            if self._fragments_token_count(candidate_fragments) <= self.text_splitter.max_chunk_tokens:
                current_fragments = candidate_fragments
                continue

            if current_fragments:
                chunk_payloads.append(
                    self._make_chunk_payload(
                        document_title=document_title,
                        section_id=section_id,
                        section_path=section_path,
                        fragments=current_fragments,
                    )
                )

            current_fragments = self._overlap_fragments(current_fragments)
            while (
                current_fragments
                and self._fragments_token_count([*current_fragments, fragment])
                > self.text_splitter.max_chunk_tokens
            ):
                current_fragments = current_fragments[1:]

            current_fragments.append(fragment)

        if current_fragments:
            chunk_payloads.append(
                self._make_chunk_payload(
                    document_title=document_title,
                    section_id=section_id,
                    section_path=section_path,
                    fragments=current_fragments,
                )
            )

        return chunk_payloads

    def _split_fragment_to_chunk_payloads(
        self,
        *,
        document_title: str | None,
        section_id: str,
        section_path: list[str],
        fragment: ChunkFragment,
    ) -> list[ChunkPayload]:
        windows = self.text_splitter.split(fragment.text)
        return [
            self._make_chunk_payload(
                document_title=document_title,
                section_id=section_id,
                section_path=section_path,
                fragments=[fragment],
                content_override=window,
            )
            for window in windows
            if window.strip()
        ]

    def _make_chunk_payload(
        self,
        *,
        document_title: str | None,
        section_id: str,
        section_path: list[str],
        fragments: list[ChunkFragment],
        content_override: str | None = None,
    ) -> ChunkPayload:
        content = content_override or "\n\n".join(
            fragment.text for fragment in fragments if fragment.text
        )
        cleaned_content = clean_chunk_text(content) or ""
        table_only = all(
            fragment.chunk_type == ChunkType.SPARE_PARTS_TABLE
            for fragment in fragments
        )

        return ChunkPayload(
            section_id=section_id,
            section_path=list(section_path),
            content=cleaned_content,
            chunk_type=(
                ChunkType.SPARE_PARTS_TABLE if table_only else ChunkType.GENERAL
            ),
            element_ids=unique_preserve_order(
                element_id
                for fragment in fragments
                for element_id in fragment.element_ids
            ),
            table_ids=unique_preserve_order(
                table_id
                for fragment in fragments
                for table_id in fragment.table_ids
            ),
            picture_ids=unique_preserve_order(
                picture_id
                for fragment in fragments
                for picture_id in fragment.picture_ids
            ),
            page_start=self._min_fragment_page(fragments),
            page_end=self._max_fragment_page(fragments),
            embedding_text=self._build_embedding_text(
                document_title=document_title,
                section_path=section_path,
                content=cleaned_content,
            ),
        )

    def _build_section_fragments(
        self,
        elements: list[CanonicalElement],
    ) -> list[ChunkFragment]:
        fragments: list[ChunkFragment] = []

        for element in elements:
            fragment = self._build_fragment_from_element(element)
            if fragment is not None:
                fragments.append(fragment)

        return fragments

    def _build_fragment_from_element(
        self,
        element: CanonicalElement,
    ) -> ChunkFragment | None:
        if self._is_document_index_element(element):
            return None

        if element.table_id is not None or element.element_type == ElementType.TABLE:
            if not self._should_chunk_table_element(element):
                return None
            text = self._table_fragment_text(element)
            chunk_type = self._table_chunk_type(element, text)
            standalone = True
        else:
            if not self._element_contributes_to_chunk(element):
                return None
            text = clean_chunk_text(element.text)
            chunk_type = ChunkType.GENERAL
            standalone = False

        if not text or is_low_value_fragment(text):
            return None

        return ChunkFragment(
            text=text,
            chunk_type=chunk_type,
            standalone=standalone,
            element_ids=[element.element_id],
            table_ids=[element.table_id] if element.table_id is not None else [],
            picture_ids=[element.picture_id] if element.picture_id is not None else [],
            page_start=element.source.page_start,
            page_end=element.source.page_end,
            token_count=self.text_splitter.count_tokens(text),
        )

    def _should_skip_chunk_section(
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

        if self._is_front_matter_section(
            document_title=document_title,
            section=section,
            elements=elements,
        ):
            return True

        return False

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
        longest_text_tokens = max(self.text_splitter.count_tokens(text) for text in texts)
        total_tokens = sum(self.text_splitter.count_tokens(text) for text in texts)

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

    @staticmethod
    def _element_contributes_to_chunk(element: CanonicalElement) -> bool:
        if element.element_type in {
            ElementType.SECTION_HEADER,
            ElementType.PICTURE,
            ElementType.TITLE,
            ElementType.CAPTION,
        }:
            return False

        parser_extra = (
            element.parser_metadata.extra
            if element.parser_metadata is not None
            and element.parser_metadata.extra is not None
            else {}
        )
        parent_ref = parser_extra.get("parent_ref")
        if (
            isinstance(parent_ref, str)
            and parent_ref.startswith("#/pictures/")
        ):
            return False

        content_layer = parser_extra.get("content_layer")
        if content_layer == "furniture":
            return False

        return True

    def _is_document_index_element(self, element: CanonicalElement) -> bool:
        parser_extra = self._parser_extra(element)
        item_label = str(parser_extra.get("item_label") or "").strip().lower()
        raw_source_type = str(parser_extra.get("raw_source_type") or "").strip().lower()
        return item_label == "document_index" or raw_source_type == "documentindex"

    def _table_fragment_text(self, element: CanonicalElement) -> str | None:
        parser_extra = self._parser_extra(element)
        markdown = clean_chunk_text(parser_extra.get("markdown") or element.text)
        caption = clean_chunk_text(parser_extra.get("caption"))

        if caption and markdown and caption not in markdown:
            return f"{caption}\n{markdown}".strip()

        return markdown or caption

    def _should_chunk_table_element(self, element: CanonicalElement) -> bool:
        parser_extra = self._parser_extra(element)
        column_count = self._coerce_positive_int(parser_extra.get("column_count"))
        row_count = self._coerce_positive_int(parser_extra.get("row_count"))
        markdown = clean_chunk_text(parser_extra.get("markdown") or element.text) or ""

        if column_count is not None and column_count <= 1:
            return False

        if (
            row_count is not None
            and row_count <= 1
            and self.text_splitter.count_tokens(markdown) > 30
        ):
            return False

        return True

    def _table_chunk_type(
        self,
        element: CanonicalElement,
        text: str | None,
    ) -> ChunkType:
        parser_extra = self._parser_extra(element)
        haystack = " ".join(
            part
            for part in [
                clean_chunk_text(parser_extra.get("caption")),
                clean_chunk_text(parser_extra.get("markdown")),
                text,
            ]
            if part
        ).lower()

        spare_part_markers = (
            "spare part",
            "spare parts",
            "part number",
            "part no",
            "| part |",
            "| part number |",
        )
        if any(marker in haystack for marker in spare_part_markers):
            return ChunkType.SPARE_PARTS_TABLE

        return ChunkType.GENERAL

    @staticmethod
    def _parser_extra(element: CanonicalElement) -> dict:
        if element.parser_metadata is None or element.parser_metadata.extra is None:
            return {}

        return element.parser_metadata.extra

    def _build_embedding_text(
        self,
        *,
        document_title: str | None,
        section_path: list[str],
        content: str,
    ) -> str:
        parts: list[str] = []
        if document_title:
            parts.append(f"Document title: {document_title}")

        if section_path:
            parts.append(f"Section path: {' > '.join(section_path)}")

        parts.append(content)
        return "\n\n".join(part for part in parts if part).strip()

    def _overlap_fragments(
        self,
        fragments: list[ChunkFragment],
    ) -> list[ChunkFragment]:
        if self.text_splitter.chunk_overlap <= 0:
            return []

        overlap: list[ChunkFragment] = []
        token_total = 0

        for fragment in reversed(fragments):
            if fragment.chunk_type != ChunkType.GENERAL:
                break

            fragment_tokens = fragment.token_count
            if overlap and token_total + fragment_tokens > self.text_splitter.chunk_overlap:
                break

            if not overlap and fragment_tokens > self.text_splitter.chunk_overlap:
                break

            overlap.insert(0, fragment)
            token_total += fragment_tokens

            if token_total >= self.text_splitter.chunk_overlap:
                break

        return overlap

    @staticmethod
    def _fragments_token_count(fragments: list[ChunkFragment]) -> int:
        return sum(fragment.token_count for fragment in fragments)

    @staticmethod
    def _min_fragment_page(fragments: list[ChunkFragment]) -> int | None:
        pages = [
            fragment.page_start
            for fragment in fragments
            if fragment.page_start is not None
        ]
        return min(pages) if pages else None

    @staticmethod
    def _max_fragment_page(fragments: list[ChunkFragment]) -> int | None:
        pages = [
            fragment.page_end
            for fragment in fragments
            if fragment.page_end is not None
        ]
        return max(pages) if pages else None

    @staticmethod
    def _coerce_positive_int(value: object) -> int | None:
        if value is None:
            return None

        try:
            number = int(value)
        except (TypeError, ValueError):
            return None

        return number if number > 0 else None
