from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)


@dataclass(slots=True, frozen=True)
class DocumentChunkingPolicy:
    profile_name: ChunkingProfile
    max_chunk_tokens: int
    chunk_overlap: int
    same_topic_merge_tokens: int
    intro_context_tokens: int
    asset_context_window: int
    asset_context_max_tokens: int
    include_picture_chunks: bool = True
    include_table_context: bool = True
