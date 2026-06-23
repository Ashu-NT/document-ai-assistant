from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)
from src.application.workflows.parsing.builders.chunking.builders.chunk_payload_factory import (
    ChunkPayloadFactory,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
    is_contents_title,
    is_reference_title,
)
from src.domain.common import ChunkType, ElementType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class SectionOverviewChunkBuilder:
    def __init__(
        self,
        *,
        text_splitter: ChunkTextSplitter,
        payload_factory: ChunkPayloadFactory,
    ) -> None:
        self.text_splitter = text_splitter
        self.payload_factory = payload_factory
        self.max_overview_tokens = max(
            60,
            min(
                self.text_splitter.max_chunk_tokens,
                self.text_splitter.max_chunk_tokens // 2,
            ),
        )

    def build(
        self,
        *,
        document_title: str | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
    ) -> list[ChunkPayload]:
        child_sections_by_parent: dict[str, list[DocumentSection]] = {}
        for section in sections:
            if section.parent_section_id is None:
                continue
            child_sections_by_parent.setdefault(section.parent_section_id, []).append(
                section
            )

        payloads: list[ChunkPayload] = []
        for section in sections:
            child_sections = child_sections_by_parent.get(section.section_id, [])
            if not child_sections:
                continue

            overview_text = self._build_overview_text(
                section=section,
                child_sections=child_sections,
                elements=section_elements_by_id.get(section.section_id, []),
            )
            if not overview_text:
                continue

            section.overview_text = overview_text

            payloads.append(
                self.payload_factory.build_payload(
                    document_title=document_title,
                    fragments=[
                        ChunkFragment(
                            text=overview_text,
                            chunk_type=ChunkType.OVERVIEW,
                            standalone=True,
                            section_id=section.section_id,
                            section_title=section.title,
                            section_path=list(section.section_path),
                            section_level=section.level,
                            parent_section_id=section.parent_section_id,
                            element_ids=[
                                element.element_id
                                for element in section_elements_by_id.get(
                                    section.section_id, []
                                )
                            ],
                            page_start=section.source.page_start,
                            page_end=section.source.page_end,
                            token_count=self.text_splitter.count_tokens(overview_text),
                        )
                    ],
                )
            )

        return payloads

    def _build_overview_text(
        self,
        *,
        section: DocumentSection,
        child_sections: list[DocumentSection],
        elements: list[CanonicalElement],
    ) -> str | None:
        child_titles = [
            clean_chunk_text(child_section.title)
            for child_section in child_sections
            if clean_chunk_text(child_section.title)
            and not self._should_skip_child_title(child_section.title)
        ]
        if not child_titles:
            return None

        intro_text = self._direct_section_text(elements)
        parts = [f"Section overview: {section.title}"]
        if intro_text:
            parts.append(intro_text)

        subsection_summary = "; ".join(child_titles[:8])
        if subsection_summary:
            parts.append(f"Subsections: {subsection_summary}")

        overview_text = clean_chunk_text("\n\n".join(parts))
        if not overview_text:
            return None

        return self._truncate_to_token_limit(overview_text)

    def _direct_section_text(self, elements: list[CanonicalElement]) -> str | None:
        texts: list[str] = []

        for element in elements:
            if element.element_type not in {
                ElementType.TEXT,
                ElementType.LIST_ITEM,
                ElementType.KEY_VALUE,
                ElementType.CODE,
            }:
                continue

            text = clean_chunk_text(element.text)
            if text:
                texts.append(text)

        if not texts:
            return None

        return self._truncate_to_token_limit("\n\n".join(texts))

    def _truncate_to_token_limit(self, text: str) -> str:
        tokens = text.split()
        if len(tokens) <= self.max_overview_tokens:
            return text
        return " ".join(tokens[: self.max_overview_tokens]).strip()

    @staticmethod
    def _should_skip_child_title(title: str | None) -> bool:
        return is_contents_title(title) or is_reference_title(title)
