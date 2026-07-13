from dataclasses import dataclass, field

from src.domain.common import ChunkType


@dataclass(slots=True)
class ChunkFragment:
    text: str
    chunk_type: ChunkType
    standalone: bool = False
    order_index: int = 0
    section_id: str | None = None
    section_title: str | None = None
    section_path: list[str] = field(default_factory=list)
    section_level: int = 1
    parent_section_id: str | None = None
    element_ids: list[str] = field(default_factory=list)
    table_ids: list[str] = field(default_factory=list)
    picture_ids: list[str] = field(default_factory=list)
    page_start: int | None = None
    page_end: int | None = None
    token_count: int = 0
    table_context: str | None = None
    table_rows: list[list[str]] | None = None
    logical_table_family_id: str | None = None
    logical_table_family_index: int | None = None
    logical_table_family_total: int | None = None
    logical_table_continuation_role: str | None = None
    table_category: str | None = None
    table_category_confidence: float | None = None
    table_row_start: int | None = None
    table_row_end: int | None = None
