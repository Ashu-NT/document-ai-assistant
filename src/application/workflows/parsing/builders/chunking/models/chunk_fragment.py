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
    form_ids: list[str] = field(default_factory=list)
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
    table_shape: str | None = None
    table_structure_quality: float | None = None
    header_paths: list[list[str]] = field(default_factory=list)
    axis_summary: dict[str, str] = field(default_factory=dict)
    # Shared id for consecutive LIST_ITEM-derived fragments (a numbered
    # procedure's steps), and the summed token_count across every fragment
    # in that run. Lets the packer avoid starting a new chunk partway
    # through a list when the whole list would fit in one chunk on its own
    # -- see ChunkFragmentPacker._should_flush_before_list_run.
    list_run_id: str | None = None
    list_run_total_tokens: int | None = None
