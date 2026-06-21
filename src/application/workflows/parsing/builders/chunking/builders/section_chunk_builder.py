from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.builders.chunk_fragment_builder import (
    ChunkFragmentBuilder,
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
from src.application.workflows.parsing.builders.chunking.runtime.chunking_runtime_factory import (
    ChunkingRuntimeFactory,
)
from src.application.workflows.parsing.builders.chunking.builders.section_chunk_skipper import (
    SectionChunkSkipper,
)
from src.application.workflows.parsing.builders.chunking.policies.section_merge_policy import (
    SectionMergePolicy,
)
from src.application.workflows.parsing.builders.chunking.builders.section_overview_chunk_builder import (
    SectionOverviewChunkBuilder,
)
from src.domain.common import ChunkType
from src.domain.common import DocumentType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.deduplication.chunk_payload_deduplicator import (
    ChunkPayloadDeduplicator,
)


class SectionChunkBuilder:
    def __init__(
        self,
        *,
        text_splitter: ChunkTextSplitter | None = None,
        max_chunk_tokens: int | None = None,
        chunk_overlap: int | None = None,
        min_section_text_length: int | None = None,
        runtime_factory: ChunkingRuntimeFactory | None = None,
        payload_deduplicator: ChunkPayloadDeduplicator | None = None,
    ) -> None:
        text_splitter = text_splitter or (
            ChunkTextSplitter(
                max_chunk_tokens=(
                    200 if max_chunk_tokens is None else max_chunk_tokens
                ),
                chunk_overlap=20 if chunk_overlap is None else chunk_overlap,
            )
            if max_chunk_tokens is not None or chunk_overlap is not None
            else None
        )
        self.runtime_factory = runtime_factory or ChunkingRuntimeFactory(
            max_chunk_tokens_override=(
                text_splitter.max_chunk_tokens
                if text_splitter is not None
                else max_chunk_tokens
            ),
            chunk_overlap_override=(
                text_splitter.chunk_overlap
                if text_splitter is not None
                else chunk_overlap
            ),
            min_section_text_length_override=min_section_text_length,
        )
        self.payload_deduplicator = (
            payload_deduplicator or ChunkPayloadDeduplicator()
        )
    def build_chunk_payloads(
        self,
        *,
        document_title: str | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
        document_type: DocumentType | None = None,
        chunking_profile_override: ChunkingProfile | None = None,
    ) -> list[ChunkPayload]:
        if not elements:
            return []

        runtime = self.runtime_factory.create(
            document_title=document_title,
            document_type=document_type,
            chunking_profile_override=chunking_profile_override,
            sections=[section],
            section_elements_by_id={section.section_id: elements},
        )

        if runtime.section_skipper.should_skip_section(
            document_title=document_title,
            section=section,
            elements=elements,
        ):
            return []

        fragments = runtime.fragment_builder.build_section_fragments(
            document_title=document_title,
            document_type=document_type,
            section=section,
            elements=elements,
        )
        if not fragments:
            return []

        return self._deduplicate_payloads(
            self._chunk_payloads_from_fragments(
                document_title=document_title,
                fragments=fragments,
                text_splitter=runtime.text_splitter,
                payload_factory=runtime.payload_factory,
                merge_policy=runtime.merge_policy,
            )
        )

    def build_document_chunk_payloads(
        self,
        *,
        document_title: str | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
        document_type: DocumentType | None = None,
        chunking_profile_override: ChunkingProfile | None = None,
    ) -> list[ChunkPayload]:
        runtime = self.runtime_factory.create(
            document_title=document_title,
            document_type=document_type,
            chunking_profile_override=chunking_profile_override,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        )
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

            if runtime.section_skipper.should_skip_section(
                document_title=document_title,
                section=section,
                elements=elements,
            ):
                continue

            fragments.extend(
                runtime.fragment_builder.build_section_fragments(
                    document_title=document_title,
                    document_type=document_type,
                    section=section,
                    elements=elements,
                )
            )

        if not fragments:
            base_payloads: list[ChunkPayload] = []
        else:
            base_payloads = self._chunk_payloads_from_fragments(
                document_title=document_title,
                fragments=fragments,
                section_path_lookup=section_path_lookup,
                text_splitter=runtime.text_splitter,
                payload_factory=runtime.payload_factory,
                merge_policy=runtime.merge_policy,
            )

        overview_payloads = SectionOverviewChunkBuilder(
            text_splitter=runtime.text_splitter,
            payload_factory=runtime.payload_factory,
        ).build(
            document_title=document_title,
            sections=ordered_sections,
            section_elements_by_id=section_elements_by_id,
        )
        return self._deduplicate_payloads(
            self._merge_overview_payloads(
                base_payloads=base_payloads,
                overview_payloads=overview_payloads,
            )
        )

    def _deduplicate_payloads(
        self,
        payloads: list[ChunkPayload],
    ) -> list[ChunkPayload]:
        return self.payload_deduplicator.deduplicate(payloads).payloads

    def _chunk_payloads_from_fragments(
        self,
        *,
        document_title: str | None,
        fragments: list[ChunkFragment],
        text_splitter: ChunkTextSplitter,
        payload_factory: ChunkPayloadFactory,
        merge_policy: SectionMergePolicy,
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
                    payload_factory=payload_factory,
                    section_path_lookup=section_path_lookup,
                )
                current_fragments = []
                chunk_payloads.extend(
                    self._split_fragment_to_chunk_payloads(
                        document_title=document_title,
                        fragment=fragment,
                        payload_factory=payload_factory,
                        text_splitter=text_splitter,
                        section_path_lookup=section_path_lookup,
                    )
                )
                continue

            if fragment.token_count > text_splitter.max_chunk_tokens:
                self._flush_current_fragments(
                    chunk_payloads=chunk_payloads,
                    document_title=document_title,
                    current_fragments=current_fragments,
                    section_path_lookup=section_path_lookup,
                    payload_factory=payload_factory,
                )
                current_fragments = []
                chunk_payloads.extend(
                    self._split_fragment_to_chunk_payloads(
                        document_title=document_title,
                        fragment=fragment,
                        payload_factory=payload_factory,
                        text_splitter=text_splitter,
                        section_path_lookup=section_path_lookup,
                    )
                )
                continue

            if (
                current_fragments
                and fragment.section_id != current_fragments[-1].section_id
                and merge_policy.should_flush_on_section_change(
                    current_fragments=current_fragments,
                    next_fragment=fragment,
                )
            ):
                self._flush_current_fragments(
                    chunk_payloads=chunk_payloads,
                    document_title=document_title,
                    current_fragments=current_fragments,
                    section_path_lookup=section_path_lookup,
                    payload_factory=payload_factory,
                )
                current_fragments = []

            candidate_fragments = [*current_fragments, fragment]
            if self._fragments_token_count(candidate_fragments) <= text_splitter.max_chunk_tokens:
                current_fragments = candidate_fragments
                continue

            self._flush_current_fragments(
                chunk_payloads=chunk_payloads,
                document_title=document_title,
                current_fragments=current_fragments,
                section_path_lookup=section_path_lookup,
                payload_factory=payload_factory,
            )

            current_fragments = self._overlap_fragments(
                current_fragments,
                text_splitter=text_splitter,
            )
            while (
                current_fragments
                and self._fragments_token_count([*current_fragments, fragment])
                > text_splitter.max_chunk_tokens
            ):
                current_fragments = current_fragments[1:]

            current_fragments.append(fragment)

        self._flush_current_fragments(
            chunk_payloads=chunk_payloads,
            document_title=document_title,
            current_fragments=current_fragments,
            section_path_lookup=section_path_lookup,
            payload_factory=payload_factory,
        )
        return chunk_payloads

    def _split_fragment_to_chunk_payloads(
        self,
        *,
        document_title: str | None,
        fragment: ChunkFragment,
        payload_factory: ChunkPayloadFactory,
        text_splitter: ChunkTextSplitter,
        section_path_lookup: dict[tuple[str, ...], str] | None = None,
    ) -> list[ChunkPayload]:
        windows = text_splitter.split(fragment.text)
        return [
            payload_factory.build_payload(
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
        payload_factory: ChunkPayloadFactory,
        section_path_lookup: dict[tuple[str, ...], str] | None = None,
    ) -> None:
        if not current_fragments:
            return

        chunk_payloads.append(
            payload_factory.build_payload(
                document_title=document_title,
                fragments=current_fragments,
                section_path_lookup=section_path_lookup,
            )
        )

    def _overlap_fragments(
        self,
        fragments: list[ChunkFragment],
        *,
        text_splitter: ChunkTextSplitter,
    ) -> list[ChunkFragment]:
        if text_splitter.chunk_overlap <= 0:
            return []

        overlap: list[ChunkFragment] = []
        token_total = 0

        for fragment in reversed(fragments):
            if fragment.chunk_type != ChunkType.GENERAL:
                break

            fragment_tokens = fragment.token_count
            if overlap and token_total + fragment_tokens > text_splitter.chunk_overlap:
                break

            if not overlap and fragment_tokens > text_splitter.chunk_overlap:
                break

            overlap.insert(0, fragment)
            token_total += fragment_tokens

            if token_total >= text_splitter.chunk_overlap:
                break

        return overlap

    @staticmethod
    def _merge_overview_payloads(
        *,
        base_payloads: list[ChunkPayload],
        overview_payloads: list[ChunkPayload],
    ) -> list[ChunkPayload]:
        if not overview_payloads:
            return base_payloads

        ordered_payloads: list[ChunkPayload] = []
        inserted_sections: set[str] = set()

        for payload in base_payloads:
            matching_overviews = sorted(
                (
                    overview_payload
                    for overview_payload in overview_payloads
                    if overview_payload.section_id
                    and overview_payload.section_id not in inserted_sections
                    and SectionChunkBuilder._is_path_prefix(
                        overview_payload.section_path,
                        payload.section_path,
                    )
                ),
                key=lambda overview_payload: len(overview_payload.section_path),
            )
            for overview_payload in matching_overviews:
                ordered_payloads.append(overview_payload)
                inserted_sections.add(overview_payload.section_id)
            ordered_payloads.append(payload)

        for payload in overview_payloads:
            if payload.section_id and payload.section_id in inserted_sections:
                continue
            ordered_payloads.append(payload)

        return ordered_payloads

    @staticmethod
    def _is_path_prefix(
        ancestor_path: list[str],
        descendant_path: list[str],
    ) -> bool:
        if not ancestor_path or len(ancestor_path) > len(descendant_path):
            return False
        return descendant_path[: len(ancestor_path)] == ancestor_path

    @staticmethod
    def _fragments_token_count(fragments: list[ChunkFragment]) -> int:
        return sum(fragment.token_count for fragment in fragments)
