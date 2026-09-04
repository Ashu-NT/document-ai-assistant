from src.application.workflows.parsing.builders.chunking.builders.chunk_type_resolver import (
    ChunkTypeResolver,
)
from src.application.workflows.parsing.builders.chunking.builders.fragment.chunk_fragment_builder import (
    ChunkFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.builders.structured_section_fragment_builder import (
    StructuredSectionFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.builders.chunk_payload_factory import (
    ChunkPayloadFactory,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.tokenization.chunk_token_counter import (
    ChunkTokenCounter,
)
from src.application.workflows.parsing.builders.chunking.text.tokenization.chunk_token_counter_factory import (
    ChunkTokenCounterFactory,
)
from src.application.workflows.parsing.builders.chunking.text.tokenization.whitespace_chunk_token_counter import (
    WhitespaceChunkTokenCounter,
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
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.config.logging import get_logger
from src.domain.common import DocumentType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement

logger = get_logger(__name__)


_SPECIAL_TOKEN_RESERVE = 2
_WORD_TO_SUBWORD_EXPANSION_FACTOR = 3.0


def _max_safe_chunk_tokens(token_counter: ChunkTokenCounter) -> int:
    try:
        from src.config.settings import embedding_settings

        ceiling = max(1, embedding_settings.max_sequence_tokens - _SPECIAL_TOKEN_RESERVE)
    except Exception:
        ceiling = 510

    if isinstance(token_counter, WhitespaceChunkTokenCounter):
        return max(1, int(ceiling / _WORD_TO_SUBWORD_EXPANSION_FACTOR))
    return ceiling


class ChunkingRuntimeFactory:
    def __init__(
        self,
        *,
        policy_resolver: DocumentChunkingPolicyResolver | None = None,
        structured_fragment_builder: StructuredSectionFragmentBuilder | None = None,
        max_chunk_tokens_override: int | None = None,
        chunk_overlap_override: int | None = None,
        min_section_text_length_override: int | None = None,
        token_counter: ChunkTokenCounter | None = None,
        token_counter_factory: ChunkTokenCounterFactory | None = None,
    ) -> None:
        self.policy_resolver = policy_resolver or DocumentChunkingPolicyResolver()
        self.structured_fragment_builder = structured_fragment_builder
        self.max_chunk_tokens_override = max_chunk_tokens_override
        self.chunk_overlap_override = chunk_overlap_override
        self.min_section_text_length_override = min_section_text_length_override
        self.token_counter = token_counter
        self.token_counter_factory = token_counter_factory or ChunkTokenCounterFactory()

    def create(
        self,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
        chunking_profile_override: ChunkingProfile | None = None,
        page_sizes: dict[int, tuple[float, float]] | None = None,
    ) -> ChunkingRuntime:
        chunk_type_resolver = ChunkTypeResolver()
        policy = self.policy_resolver.resolve(
            document_title=document_title,
            document_type=document_type,
            chunking_profile_override=chunking_profile_override,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        )
        token_counter = self.token_counter or self.token_counter_factory.create()
        max_chunk_tokens = self.max_chunk_tokens_override or policy.max_chunk_tokens
        safe_max_chunk_tokens = _max_safe_chunk_tokens(token_counter)
        if max_chunk_tokens > safe_max_chunk_tokens:
            logger.warning(
                "chunking profile max_chunk_tokens exceeds embedding model capacity, clamping",
                extra={
                    "profile": policy.profile_name.value,
                    "configured_max_chunk_tokens": max_chunk_tokens,
                    "clamped_max_chunk_tokens": safe_max_chunk_tokens,
                },
            )
            max_chunk_tokens = safe_max_chunk_tokens
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
            token_counter=token_counter,
        )
        return ChunkingRuntime(
            policy=policy,
            text_splitter=text_splitter,
            fragment_builder=ChunkFragmentBuilder(
                text_splitter=text_splitter,
                structured_fragment_builder=self.structured_fragment_builder,
                include_picture_chunks=policy.include_picture_chunks,
                include_table_context=policy.include_table_context,
                asset_context_window=policy.asset_context_window,
                asset_context_max_tokens=policy.asset_context_max_tokens,
                page_sizes=page_sizes,
            ),
            section_skipper=SectionChunkSkipper(
                text_splitter=text_splitter,
            ),
            payload_factory=ChunkPayloadFactory(
                chunk_type_resolver=chunk_type_resolver,
            ),
            merge_policy=SectionMergePolicy(
                text_splitter=text_splitter,
                min_section_text_length=min_section_text_length,
                same_topic_merge_tokens=policy.same_topic_merge_tokens,
                intro_context_tokens=policy.intro_context_tokens,
                chunk_type_resolver=chunk_type_resolver,
            ),
        )
