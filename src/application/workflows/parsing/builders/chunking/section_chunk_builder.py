from src.application.workflows.parsing.builders.chunking.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.chunk_fragment_builder import (
    ChunkFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.chunk_payload import ChunkPayload
from src.application.workflows.parsing.builders.chunking.chunk_payload_factory import (
    ChunkPayloadFactory,
)
from src.application.workflows.parsing.builders.chunking.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.section_chunk_skipper import (
    SectionChunkSkipper,
)
from src.application.workflows.parsing.builders.chunking.section_merge_policy import (
    SectionMergePolicy,
)
from src.domain.common import ChunkType
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
        self.fragment_builder = ChunkFragmentBuilder(
            text_splitter=self.text_splitter,
        )
        self.section_skipper = SectionChunkSkipper(
            text_splitter=self.text_splitter,
        )
        self.payload_factory = ChunkPayloadFactory()
        self.merge_policy = SectionMergePolicy(
            text_splitter=self.text_splitter,
            min_section_text_length=min_section_text_length,
        )

    def build_chunk_payloads(
        self,
        *,
        document_title: str | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
    ) -> list[ChunkPayload]:
        if not elements:
            return []

        if self.section_skipper.should_skip_section(
            document_title=document_title,
            section=section,
            elements=elements,
        ):
            return []

        fragments = self.fragment_builder.build_section_fragments(section, elements)
        if not fragments:
            return []

        return self._chunk_payloads_from_fragments(
            document_title=document_title,
            fragments=fragments,
        )

    def build_document_chunk_payloads(
        self,
        *,
        document_title: str | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
    ) -> list[ChunkPayload]:
        ordered_sections = sorted(
            sections,
            key=lambda value: value.sequence_number or 0,
        )
        section_path_lookup = {
            tuple(section.section_path): section.section_id
            for section in ordered_sections
            if section.section_path
        }
        fragments: list[ChunkFragment] = []

        for section in ordered_sections:
            elements = section_elements_by_id.get(section.section_id, [])
            if not elements:
                continue

            if self.section_skipper.should_skip_section(
                document_title=document_title,
                section=section,
                elements=elements,
            ):
                continue

            fragments.extend(
                self.fragment_builder.build_section_fragments(section, elements)
            )

        if not fragments:
            return []

        return self._chunk_payloads_from_fragments(
            document_title=document_title,
            fragments=fragments,
            section_path_lookup=section_path_lookup,
        )

    def _chunk_payloads_from_fragments(
        self,
        *,
        document_title: str | None,
        fragments: list[ChunkFragment],
        section_path_lookup: dict[tuple[str, ...], str] | None = None,
    ) -> list[ChunkPayload]:
        chunk_payloads: list[ChunkPayload] = []
        current_fragments: list[ChunkFragment] = []

        for fragment in fragments:
            if fragment.standalone:
                self._flush_current_fragments(
                    chunk_payloads=chunk_payloads,
                    document_title=document_title,
                    current_fragments=current_fragments,
                    section_path_lookup=section_path_lookup,
                )
                current_fragments = []
                chunk_payloads.extend(
                    self._split_fragment_to_chunk_payloads(
                        document_title=document_title,
                        fragment=fragment,
                        section_path_lookup=section_path_lookup,
                    )
                )
                continue

            if fragment.token_count > self.text_splitter.max_chunk_tokens:
                self._flush_current_fragments(
                    chunk_payloads=chunk_payloads,
                    document_title=document_title,
                    current_fragments=current_fragments,
                    section_path_lookup=section_path_lookup,
                )
                current_fragments = []
                chunk_payloads.extend(
                    self._split_fragment_to_chunk_payloads(
                        document_title=document_title,
                        fragment=fragment,
                        section_path_lookup=section_path_lookup,
                    )
                )
                continue

            if (
                current_fragments
                and fragment.section_id != current_fragments[-1].section_id
                and self.merge_policy.should_flush_on_section_change(
                    current_fragments=current_fragments,
                    next_fragment=fragment,
                )
            ):
                self._flush_current_fragments(
                    chunk_payloads=chunk_payloads,
                    document_title=document_title,
                    current_fragments=current_fragments,
                    section_path_lookup=section_path_lookup,
                )
                current_fragments = []

            candidate_fragments = [*current_fragments, fragment]
            if self._fragments_token_count(candidate_fragments) <= self.text_splitter.max_chunk_tokens:
                current_fragments = candidate_fragments
                continue

            self._flush_current_fragments(
                chunk_payloads=chunk_payloads,
                document_title=document_title,
                current_fragments=current_fragments,
                section_path_lookup=section_path_lookup,
            )

            current_fragments = self._overlap_fragments(current_fragments)
            while (
                current_fragments
                and self._fragments_token_count([*current_fragments, fragment])
                > self.text_splitter.max_chunk_tokens
            ):
                current_fragments = current_fragments[1:]

            current_fragments.append(fragment)

        self._flush_current_fragments(
            chunk_payloads=chunk_payloads,
            document_title=document_title,
            current_fragments=current_fragments,
            section_path_lookup=section_path_lookup,
        )
        return chunk_payloads

    def _split_fragment_to_chunk_payloads(
        self,
        *,
        document_title: str | None,
        fragment: ChunkFragment,
        section_path_lookup: dict[tuple[str, ...], str] | None = None,
    ) -> list[ChunkPayload]:
        windows = self.text_splitter.split(fragment.text)
        return [
            self.payload_factory.build_payload(
                document_title=document_title,
                fragments=[fragment],
                content_override=window,
                section_path_lookup=section_path_lookup,
            )
            for window in windows
            if window.strip()
        ]

    def _flush_current_fragments(
        self,
        *,
        chunk_payloads: list[ChunkPayload],
        document_title: str | None,
        current_fragments: list[ChunkFragment],
        section_path_lookup: dict[tuple[str, ...], str] | None = None,
    ) -> None:
        if not current_fragments:
            return

        chunk_payloads.append(
            self.payload_factory.build_payload(
                document_title=document_title,
                fragments=current_fragments,
                section_path_lookup=section_path_lookup,
            )
        )

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
