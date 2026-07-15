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
    logical_table_family_id: str | None = None
    logical_table_family_index: int | None = None
    logical_table_family_total: int | None = None
    logical_table_continuation_role: str | None = None
    table_category: str | None = None
    table_category_confidence: float | None = None
    table_row_start: int | None = None
    table_row_end: int | None = None
    table_shape: str | None = None
    table_structure_quality: float | None = None
    header_paths: list[list[str]] = field(default_factory=list)
    axis_summary: dict[str, str] = field(default_factory=dict)

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
