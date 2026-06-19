from dataclasses import dataclass, field

from src.domain.common import ChunkType


@dataclass(slots=True)
class ChunkFragment:
    text: str
    chunk_type: ChunkType
    standalone: bool = False
    element_ids: list[str] = field(default_factory=list)
    table_ids: list[str] = field(default_factory=list)
    picture_ids: list[str] = field(default_factory=list)
    page_start: int | None = None
    page_end: int | None = None
    token_count: int = 0
