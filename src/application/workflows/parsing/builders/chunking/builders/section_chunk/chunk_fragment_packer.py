from dataclasses import replace as dataclass_replace

from src.application.workflows.parsing.builders.chunking.builders.chunk_payload_factory import (
    ChunkPayloadFactory,
)
from src.application.workflows.parsing.builders.chunking.builders.fragment.table_fragment_splitter import (
    TableFragmentSplitter,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)
from src.application.workflows.parsing.builders.chunking.policies.section_merge_policy import (
    SectionMergePolicy,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ChunkType


class ChunkFragmentPacker:
    def pack(
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
        if fragment.table_rows:
            split_fragments = TableFragmentSplitter(text_splitter=text_splitter).split(
                fragment
            )
            if len(split_fragments) > 1 or split_fragments[0] is not fragment:
                return [
                    payload_factory.build_payload(
                        document_title=document_title,
                        fragments=[split_fragment],
                        content_override=split_fragment.text,
                        section_path_lookup=section_path_lookup,
                    )
                    for split_fragment in split_fragments
                    if split_fragment.text.strip()
                ]

        windows = text_splitter.split(fragment.text)
        return [
            payload_factory.build_payload(
                document_title=document_title,
                fragments=[
                    dataclass_replace(
                        fragment,
                        table_row_start=fragment.table_row_start,
                        table_row_end=fragment.table_row_end,
                    )
                ],
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
    def _fragments_token_count(fragments: list[ChunkFragment]) -> int:
        return sum(fragment.token_count for fragment in fragments)
