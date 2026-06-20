from src.application.workflows.parsing.builders.chunking.chunk_fragment_builder import (
    ChunkFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.chunk_payload_factory import (
    ChunkPayloadFactory,
)
from src.application.workflows.parsing.builders.chunking.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.chunking_runtime import (
    ChunkingRuntime,
)
from src.application.workflows.parsing.builders.chunking.document_chunking_policy_resolver import (
    DocumentChunkingPolicyResolver,
)
from src.application.workflows.parsing.builders.chunking.section_chunk_skipper import (
    SectionChunkSkipper,
)
from src.application.workflows.parsing.builders.chunking.section_merge_policy import (
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
    ) -> None:
        self.policy_resolver = policy_resolver or DocumentChunkingPolicyResolver()

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
        text_splitter = ChunkTextSplitter(
            max_chunk_tokens=policy.max_chunk_tokens,
            chunk_overlap=policy.chunk_overlap,
        )
        return ChunkingRuntime(
            policy=policy,
            text_splitter=text_splitter,
            fragment_builder=ChunkFragmentBuilder(
                text_splitter=text_splitter,
            ),
            section_skipper=SectionChunkSkipper(
                text_splitter=text_splitter,
            ),
            payload_factory=ChunkPayloadFactory(),
            merge_policy=SectionMergePolicy(
                text_splitter=text_splitter,
                min_section_text_length=max(12, policy.same_topic_merge_tokens // 6),
                same_topic_merge_tokens=policy.same_topic_merge_tokens,
                intro_context_tokens=policy.intro_context_tokens,
            ),
        )
