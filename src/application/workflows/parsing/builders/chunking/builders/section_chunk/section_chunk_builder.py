from src.application.workflows.parsing.builders.chunking.builders.section_chunk.chunk_fragment_packer import (
    ChunkFragmentPacker,
)
from src.application.workflows.parsing.builders.chunking.builders.section_chunk.overview_payload_merger import (
    merge_overview_payloads,
)
from src.application.workflows.parsing.builders.chunking.builders.section_overview_chunk_builder import (
    SectionOverviewChunkBuilder,
)
from src.application.workflows.parsing.builders.chunking.deduplication.chunk_payload_deduplicator import (
    ChunkPayloadDeduplicator,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.runtime.chunking_runtime_factory import (
    ChunkingRuntimeFactory,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.profiling import GraphBuildProfiler
from src.domain.common import DocumentType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


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
        profiler: GraphBuildProfiler | None = None,
    ) -> None:
        self.profiler = profiler or GraphBuildProfiler.disabled()
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
            token_counter=(
                text_splitter.token_counter
                if text_splitter is not None
                else None
            ),
        )
        self.payload_deduplicator = (
            payload_deduplicator or ChunkPayloadDeduplicator()
        )
        self.fragment_packer = ChunkFragmentPacker()

    def set_profiler(self, profiler: GraphBuildProfiler | None) -> None:
        self.profiler = profiler or GraphBuildProfiler.disabled()

    def build_chunk_payloads(
        self,
        *,
        document_title: str | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
        document_type: DocumentType | None = None,
        chunking_profile_override: ChunkingProfile | None = None,
        page_sizes: dict[int, tuple[float, float]] | None = None,
    ) -> list[ChunkPayload]:
        if not elements:
            return []

        with self.profiler.measure(
            name="section_chunk_builder.create_runtime",
            input_counts={"sections": 1, "elements": len(elements)},
        ) as stage:
            runtime = self.runtime_factory.create(
                document_title=document_title,
                document_type=document_type,
                chunking_profile_override=chunking_profile_override,
                sections=[section],
                section_elements_by_id={section.section_id: elements},
                page_sizes=page_sizes,
            )
            stage.output_counts["sections"] = 1

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
            self.fragment_packer.pack(
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
        page_sizes: dict[int, tuple[float, float]] | None = None,
    ) -> list[ChunkPayload]:
        with self.profiler.measure(
            name="section_chunk_builder.create_runtime",
            input_counts={"sections": len(sections)},
        ) as stage:
            runtime = self.runtime_factory.create(
                document_title=document_title,
                document_type=document_type,
                chunking_profile_override=chunking_profile_override,
                sections=sections,
                section_elements_by_id=section_elements_by_id,
                page_sizes=page_sizes,
            )
            stage.output_counts["sections"] = len(sections)
        with self.profiler.measure(
            name="section_chunk_builder.order_sections",
            input_counts={"sections": len(sections)},
        ) as stage:
            ordered_sections = sorted(
                sections,
                key=lambda value: value.sequence_number or 0,
            )
            stage.output_counts["ordered_sections"] = len(ordered_sections)
        with self.profiler.measure(
            name="section_chunk_builder.build_section_lookup",
            input_counts={"sections": len(ordered_sections)},
        ) as stage:
            section_path_lookup = {
                tuple(section.section_path): section.section_id
                for section in ordered_sections
                if section.section_path
            }
            stage.output_counts["section_paths"] = len(section_path_lookup)
        with self.profiler.measure(
            name="section_chunk_builder.combine_document_section_text",
            input_counts={"sections": len(ordered_sections)},
        ) as stage:
            document_sections_combined_text = " ".join(
                " > ".join(sec.section_path or ([sec.title] if sec.title else []))
                for sec in ordered_sections
                if sec.section_path or sec.title
            )
            stage.output_counts["combined_text_length"] = len(
                document_sections_combined_text
            )
        fragments: list[ChunkFragment] = []

        with self.profiler.measure(
            name="section_chunk_builder.build_fragments",
            input_counts={"sections": len(ordered_sections)},
        ) as stage:
            skipped_sections = 0
            for section in ordered_sections:
                elements = section_elements_by_id.get(section.section_id, [])
                if not elements:
                    continue

                if runtime.section_skipper.should_skip_section(
                    document_title=document_title,
                    section=section,
                    elements=elements,
                ):
                    skipped_sections += 1
                    continue

                fragments.extend(
                    runtime.fragment_builder.build_section_fragments(
                        document_title=document_title,
                        document_type=document_type,
                        section=section,
                        elements=elements,
                        document_sections_combined_text=document_sections_combined_text,
                    )
                )
            stage.output_counts["fragments"] = len(fragments)
            stage.operations["skipped_sections"] = skipped_sections

        if not fragments:
            base_payloads: list[ChunkPayload] = []
        else:
            with self.profiler.measure(
                name="section_chunk_builder.build_base_payloads",
                input_counts={"fragments": len(fragments)},
            ) as stage:
                base_payloads = self.fragment_packer.pack(
                    document_title=document_title,
                    fragments=fragments,
                    section_path_lookup=section_path_lookup,
                    text_splitter=runtime.text_splitter,
                    payload_factory=runtime.payload_factory,
                    merge_policy=runtime.merge_policy,
                )
                stage.output_counts["base_payloads"] = len(base_payloads)

        with self.profiler.measure(
            name="section_chunk_builder.build_overviews",
            input_counts={"sections": len(ordered_sections)},
        ) as stage:
            overview_payloads = SectionOverviewChunkBuilder(
                text_splitter=runtime.text_splitter,
                payload_factory=runtime.payload_factory,
            ).build(
                document_title=document_title,
                sections=ordered_sections,
                section_elements_by_id=section_elements_by_id,
            )
            stage.output_counts["overview_payloads"] = len(overview_payloads)
        with self.profiler.measure(
            name="section_chunk_builder.merge_overviews",
            input_counts={
                "base_payloads": len(base_payloads),
                "overview_payloads": len(overview_payloads),
            },
        ) as stage:
            merged_payloads = merge_overview_payloads(
                base_payloads=base_payloads,
                overview_payloads=overview_payloads,
            )
            stage.output_counts["merged_payloads"] = len(merged_payloads)
        with self.profiler.measure(
            name="section_chunk_builder.deduplicate_payloads",
            input_counts={"merged_payloads": len(merged_payloads)},
        ) as stage:
            deduplicated_payloads = self._deduplicate_payloads(merged_payloads)
            stage.output_counts["deduplicated_payloads"] = len(deduplicated_payloads)
        return deduplicated_payloads

    def _deduplicate_payloads(
        self,
        payloads: list[ChunkPayload],
    ) -> list[ChunkPayload]:
        return self.payload_deduplicator.deduplicate(payloads).payloads
