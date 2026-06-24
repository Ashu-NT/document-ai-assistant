from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, ChunkType, SourceLocation
from src.domain.document.value_objects import ChunkStatistics


@dataclass(slots=True)
class DocumentChunk:
    chunk_id: str
    document_id: str
    section_id: str | None

    content: str
    chunk_type: ChunkType = ChunkType.GENERAL
    chunk_type_source: str = "deterministic"

    section_path: list[str] = field(default_factory=list)

    element_ids: list[str] = field(default_factory=list)
    table_ids: list[str] = field(default_factory=list)
    picture_ids: list[str] = field(default_factory=list)

    source: SourceLocation = field(default_factory=SourceLocation)

    sequence_number: int = 1
    chunk_index: int = 1
    chunk_total: int = 1

    embedding_text: str | None = None

    statistics: ChunkStatistics | None = None
    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def __post_init__(self) -> None:
        if self.statistics is None:
            self.statistics = ChunkStatistics.from_text(self.content)

    def has_embedding_text(self) -> bool:
        return bool(self.embedding_text)