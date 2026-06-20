from src.application.workflows.parsing.builders.chunking.builders.chunk_fragment_builder import (
    ChunkFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.builders.chunk_payload_factory import (
    ChunkPayloadFactory,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.runtime.chunking_runtime import (
    ChunkingRuntime,
)
from src.application.workflows.parsing.builders.chunking.policies.document_chunking_policy_resolver import (
    DocumentChunkingPolicyResolver,
)
from src.application.workflows.parsing.builders.chunking.builders.section_chunk_skipper import (
    SectionChunkSkipper,
)
from src.application.workflows.parsing.builders.chunking.policies.section_merge_policy import (
    SectionMergePolicy,
)
from src.domain.common import DocumentType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class ChunkingRuntimeFactory:
    def __init__(
        self,
        *,
        policy_resolver: DocumentChunkingPolicyResolver | None = None,
        max_chunk_tokens_override: int | None = None,
        chunk_overlap_override: int | None = None,
        min_section_text_length_override: int | None = None,
    ) -> None:
        self.policy_resolver = policy_resolver or DocumentChunkingPolicyResolver()
        self.max_chunk_tokens_override = max_chunk_tokens_override
        self.chunk_overlap_override = chunk_overlap_override
        self.min_section_text_length_override = min_section_text_length_override

    def create(
        self,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
    ) -> ChunkingRuntime:
        policy = self.policy_resolver.resolve(
            document_title=document_title,
            document_type=document_type,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        )
        max_chunk_tokens = self.max_chunk_tokens_override or policy.max_chunk_tokens
        chunk_overlap = (
            self.chunk_overlap_override
            if self.chunk_overlap_override is not None
            else policy.chunk_overlap
        )
        min_section_text_length = (
            self.min_section_text_length_override
            if self.min_section_text_length_override is not None
            else max(12, policy.same_topic_merge_tokens // 6)
        )
        text_splitter = ChunkTextSplitter(
            max_chunk_tokens=max_chunk_tokens,
            chunk_overlap=chunk_overlap,
        )
        return ChunkingRuntime(
            policy=policy,
            text_splitter=text_splitter,
            fragment_builder=ChunkFragmentBuilder(
                text_splitter=text_splitter,
                include_picture_chunks=policy.include_picture_chunks,
                include_table_context=policy.include_table_context,
                asset_context_window=policy.asset_context_window,
                asset_context_max_tokens=policy.asset_context_max_tokens,
            ),
            section_skipper=SectionChunkSkipper(
                text_splitter=text_splitter,
            ),
            payload_factory=ChunkPayloadFactory(),
            merge_policy=SectionMergePolicy(
                text_splitter=text_splitter,
                min_section_text_length=min_section_text_length,
                same_topic_merge_tokens=policy.same_topic_merge_tokens,
                intro_context_tokens=policy.intro_context_tokens,
            ),
        )
