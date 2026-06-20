from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.chunk_fragment_builder import (
    ChunkFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.chunk_payload_factory import (
    ChunkPayloadFactory,
)
from src.application.workflows.parsing.builders.chunking.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.document_chunking_policy import (
    DocumentChunkingPolicy,
)
from src.application.workflows.parsing.builders.chunking.section_chunk_skipper import (
    SectionChunkSkipper,
)
from src.application.workflows.parsing.builders.chunking.section_merge_policy import (
    SectionMergePolicy,
)


@dataclass(slots=True)
class ChunkingRuntime:
    policy: DocumentChunkingPolicy
    text_splitter: ChunkTextSplitter
    fragment_builder: ChunkFragmentBuilder
    section_skipper: SectionChunkSkipper
    payload_factory: ChunkPayloadFactory
    merge_policy: SectionMergePolicy
