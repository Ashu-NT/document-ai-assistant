from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)
from src.application.workflows.parsing.builders.chunking.builders.chunk_payload_factory import (
    ChunkPayloadFactory,
)
from src.application.workflows.parsing.builders.chunking.builders.overview.overview_subsection_summary_builder import (
    OverviewSubsectionSummaryBuilder,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
    is_contents_title,
    is_reference_title,
)
from src.domain.common import ChunkType
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
        self.subsection_summary_builder = OverviewSubsectionSummaryBuilder(
            count_tokens=self.text_splitter.count_tokens,
        )
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

            overview_result = self._build_overview_text(
                section=section,
                child_sections=child_sections,
            )
            if overview_result is None:
                continue
            overview_text, overview_token_count = overview_result

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
                            token_count=overview_token_count,
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
    ) -> tuple[str, int] | None:
        # Deliberately a pure subsection listing -- no direct section text.
        # Pulling the section's own TEXT/LIST_ITEM/KEY_VALUE/CODE elements
        # in here (as this used to) duplicates the exact same elements that
        # independently flow into the section's own real content chunk(s),
        # and that duplication is only ever truncated to a small fraction
        # of the section's real text (max_overview_tokens is half the chunk
        # budget) -- substantial but partial overlap that a dedup
        # containment check (tuned for near-total duplicates) doesn't
        # reliably catch. Fixed at the source instead of relying on dedup:
        # see project_chunking_pipeline_quality memory, audit finding #5.
        child_titles = [
            clean_chunk_text(child_section.title)
            for child_section in child_sections
            if clean_chunk_text(child_section.title)
            and not self._should_skip_child_title(child_section.title)
        ]
        if not child_titles:
            return None

        parts = [f"Section overview: {section.title}"]
        summary_budget = max(
            0,
            self.max_overview_tokens
            - self.text_splitter.count_tokens(parts[0])
            - 2,
        )
        subsection_summary = self.subsection_summary_builder.build(
            child_titles,
            max_tokens=summary_budget,
        )
        if subsection_summary:
            parts.append(subsection_summary)

        overview_text = clean_chunk_text("\n\n".join(parts))
        if not overview_text:
            return None

        return self._truncate_to_token_limit(overview_text)

    def _truncate_to_token_limit(self, text: str) -> tuple[str, int]:
        return self.text_splitter.token_counter.truncate_to_tokens_with_count(
            text,
            self.max_overview_tokens,
        )

    @staticmethod
    def _should_skip_child_title(title: str | None) -> bool:
        return is_contents_title(title) or is_reference_title(title)
