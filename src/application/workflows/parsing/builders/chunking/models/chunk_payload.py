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
