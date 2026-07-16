import pytest

from src.application.workflows.parsing.builders.chunking.builders import (
    ChunkTypeResolver,
)

from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)

from src.application.workflows.parsing.builders.chunking.policies.section_merge_policy import (
    SectionMergePolicy,
)

from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)

from src.domain.common import ChunkType

def make_fragment(
    *,
    section_id: str = "sec_001",
    section_title: str,
    section_path: list[str] | None = None,
    text: str,
    chunk_type: ChunkType = ChunkType.GENERAL,
    parent_section_id: str | None = "sec_parent",
    token_count: int = 24,
    table_ids: list[str] | None = None,
    standalone: bool = False,
) -> ChunkFragment:
    return ChunkFragment(
        text=text,
        chunk_type=chunk_type,
        section_id=section_id,
        section_title=section_title,
        section_path=section_path or ["Manual", section_title],
        section_level=2,
        parent_section_id=parent_section_id,
        token_count=token_count,
        table_ids=table_ids or [],
        standalone=standalone,
    )

__all__ = [name for name in globals() if not name.startswith("__")]
