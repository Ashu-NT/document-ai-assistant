import re

from src.application.workflows.parsing.builders.chunking.builders.structured import (
    StructuredFamilySpecFactory,
    StructuredSectionWindowSpec,
)
from src.application.workflows.parsing.builders.chunking.builders.structured.structured_element_text_resolver import (
    StructuredElementTextResolver,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
)
from src.domain.common import ChunkType, DocumentType, ElementType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class StructuredSectionFragmentBuilder:
    def __init__(
        self,
        *,
        text_splitter: ChunkTextSplitter,
        spec_factory: StructuredFamilySpecFactory | None = None,
    ) -> None:
        self.text_splitter = text_splitter
        self.spec_factory = spec_factory or StructuredFamilySpecFactory()

    def build(
        self,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
        document_sections_combined_text: str = "",
    ) -> tuple[list[ChunkFragment], set[str]]:
        ordered_elements = [
            element
            for element in elements
            if self._is_structurable_element(element)
        ]
        if not ordered_elements:
            return [], set()

        selection = self.spec_factory.build(
            document_title=document_title,
            document_type=document_type,
            section=section,
            elements=ordered_elements,
            normalizer=self._normalize_text,
            document_sections_combined_text=document_sections_combined_text,
        )
        if not selection.specs:
            return [], set()

        fragments: list[ChunkFragment] = []
        consumed_element_ids: set[str] = set()
        for spec in selection.specs:
            for window in self._collect_windows(ordered_elements, spec):
                fragment = self._build_fragment(
                    section=section,
                    elements=window,
                    spec=spec,
                )
                if fragment is None:
                    continue
                fragments.append(fragment)
                consumed_element_ids.update(fragment.element_ids)

        if selection.consume_all_elements and fragments:
            consumed_element_ids.update(
                element.element_id
                for element in ordered_elements
            )

        return (
            sorted(fragments, key=lambda fragment: fragment.order_index),
            consumed_element_ids,
        )

    def _collect_windows(
        self,
        elements: list[CanonicalElement],
        spec: StructuredSectionWindowSpec,
    ) -> list[list[CanonicalElement]]:
        anchor_indexes = [
            index
            for index, element in enumerate(elements)
            if self._matches_markers(
                self._normalize_text(StructuredElementTextResolver.resolve(element)),
                spec.anchor_markers,
            )
        ]
        if not anchor_indexes:
            if spec.include_full_section_if_no_anchor and elements:
                anchor_indexes = [0]
            else:
                return []

        windows: list[tuple[int, int]] = []
        for anchor_index in anchor_indexes:
            start_index = max(0, anchor_index - spec.radius_before)
            end_index = min(len(elements) - 1, anchor_index + spec.radius_after)
            windows.append((start_index, end_index))

        merged_windows = self._merge_windows(windows)
        window_elements = [
            elements[start_index : end_index + 1]
            for start_index, end_index in merged_windows
        ]
        if spec.combine_all_windows and window_elements:
            combined_elements: list[CanonicalElement] = []
            seen_element_ids: set[str] = set()
            for window in window_elements:
                for element in window:
                    if element.element_id in seen_element_ids:
                        continue
                    seen_element_ids.add(element.element_id)
                    combined_elements.append(element)
            return [combined_elements]
        return window_elements

    def _build_fragment(
        self,
        *,
        section: DocumentSection,
        elements: list[CanonicalElement],
        spec: StructuredSectionWindowSpec,
    ) -> ChunkFragment | None:
        texts: list[str] = []
        for element in elements:
            text = StructuredElementTextResolver.resolve(element)
            if text:
                texts.append(text)
        if not texts:
            return None

        content = "\n".join(texts).strip()
        token_count = self.text_splitter.count_tokens(content)
        if token_count < spec.min_tokens:
            return None

        section_path = self._enrich_section_path(spec, elements)
        first_element = elements[0]
        return ChunkFragment(
            text=content,
            chunk_type=spec.chunk_type,
            standalone=True,
            section_id=section.section_id,
            section_title=section_path[-1] if section_path else "",
            section_path=section_path,
            section_level=section.level,
            parent_section_id=section.parent_section_id,
            element_ids=[element.element_id for element in elements],
            table_ids=[
                element.table_id
                for element in elements
                if element.table_id is not None
            ],
            picture_ids=[
                element.picture_id
                for element in elements
                if element.picture_id is not None
            ],
            page_start=min(
                (
                    element.source.page_start
                    for element in elements
                    if element.source.page_start is not None
                ),
                default=first_element.source.page_start,
            ),
            page_end=max(
                (
                    element.source.page_end
                    for element in elements
                    if element.source.page_end is not None
                ),
                default=first_element.source.page_end,
            ),
            token_count=token_count,
            order_index=first_element.reading_order or 0,
        )

    @staticmethod
    def _merge_windows(windows: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if not windows:
            return []

        ordered_windows = sorted(windows)
        merged_windows = [ordered_windows[0]]
        for start_index, end_index in ordered_windows[1:]:
            previous_start, previous_end = merged_windows[-1]
            if start_index <= previous_end + 1:
                merged_windows[-1] = (
                    previous_start,
                    max(previous_end, end_index),
                )
                continue
            merged_windows.append((start_index, end_index))
        return merged_windows

    @staticmethod
    def _is_structurable_element(element: CanonicalElement) -> bool:
        if element.element_type not in {
            ElementType.TEXT,
            ElementType.LIST_ITEM,
            ElementType.KEY_VALUE,
            ElementType.CODE,
            ElementType.TABLE,
            ElementType.PICTURE,
        }:
            return False
        parser_extra = (
            element.parser_metadata.extra
            if element.parser_metadata is not None
            and element.parser_metadata.extra is not None
            else {}
        )
        parent_ref = parser_extra.get("parent_ref")
        if isinstance(parent_ref, str) and parent_ref.startswith("#/pictures/"):
            return False
        if parser_extra.get("content_layer") == "furniture":
            return False
        return bool(StructuredElementTextResolver.resolve(element))

    @staticmethod
    def _matches_markers(text: str, markers: tuple[str, ...]) -> bool:
        return any(marker in text for marker in markers)

    @staticmethod
    def _enrich_section_path(
        spec: StructuredSectionWindowSpec,
        elements: list[CanonicalElement],
    ) -> list[str]:
        """Append a subsection label when the anchor element is a heading-like text.

        For individual (non-combined) procedural windows, the element that triggered
        the anchor is often a sub-procedure heading such as "Removal of the Screen
        Basket".  Appending it to the spec path gives the chunk a more specific,
        searchable section path without hardcoding any document-specific strings.

        Guards:
        - combine_all_windows=True specs produce merged content — no single title fits.
        - Non-procedural specs (drawing blocks, spec tables, etc.) must not be enriched
          because their anchors are field labels, not section headings.
        """
        _PROCEDURAL_TYPES = {
            ChunkType.MAINTENANCE_PROCEDURE,
            ChunkType.OPERATION_INSTRUCTION,
            ChunkType.INSTALLATION_INSTRUCTION,
            ChunkType.TROUBLESHOOTING,
        }
        if spec.combine_all_windows:
            return list(spec.section_path)
        if spec.chunk_type not in _PROCEDURAL_TYPES:
            return list(spec.section_path)

        base_last = StructuredSectionFragmentBuilder._normalize_text(
            spec.section_path[-1] if spec.section_path else None
        )
        for element in elements:
            raw = (StructuredElementTextResolver.resolve(element) or "").strip()
            if not raw:
                continue
            normalized = StructuredSectionFragmentBuilder._normalize_text(raw)
            if not any(marker in normalized for marker in spec.anchor_markers):
                continue
            words = raw.split()
            if not (2 <= len(words) <= 12):
                continue
            if not raw[0].isupper():
                continue
            if raw.endswith("."):
                continue
            if normalized == base_last:
                break
            return [*spec.section_path, raw]

        return list(spec.section_path)

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        normalized = re.sub(r"[\W_]+", " ", str(value or ""), flags=re.UNICODE)
        return " ".join(normalized.strip().lower().split())
