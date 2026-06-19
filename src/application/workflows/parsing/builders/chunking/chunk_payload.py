from dataclasses import dataclass, field

from src.domain.common import ChunkType


@dataclass(slots=True)
class ChunkPayload:
    section_id: str
    section_path: list[str]
    content: str
    chunk_type: ChunkType
    embedding_text: str
    element_ids: list[str] = field(default_factory=list)
    table_ids: list[str] = field(default_factory=list)
    picture_ids: list[str] = field(default_factory=list)
    page_start: int | None = None
    page_end: int | None = None
