from dataclasses import dataclass, field

from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.assets.table_cell_span import TableCellSpan
from src.domain.common import AuditMetadata


@dataclass(slots=True)
class TableAsset:
    table_id: str
    document_id: str

    markdown: str

    parent_section_id: str | None = None

    rows: list[list[str]] = field(default_factory=list)
    parallel_stream_rows: list[list[list[str]]] = field(default_factory=list)
    row_ids: list[str] = field(default_factory=list)
    cell_spans: list[TableCellSpan] = field(default_factory=list)
    row_count: int | None = None
    column_count: int | None = None
    local_reading_order: str | None = None
    logical_table_family_id: str | None = None
    family_index: int | None = None
    family_total: int | None = None
    continuation_role: str | None = None
    normalized_header_signature: str | None = None
    table_category: str | None = None
    table_category_confidence: float | None = None
    table_shape: str | None = None
    table_structure_quality: float | None = None
    header_paths: list[list[str]] = field(default_factory=list)
    axis_summary: dict[str, str] = field(default_factory=dict)
    signals: frozenset[str] = field(default_factory=frozenset)

    layout_region_id: str | None = None
    layout_region_role: str | None = None
    layout_lane_index: int | None = None
    layout_lane_count: int | None = None
    page_orientation: str | None = None

    metadata: AssetMetadata = field(default_factory=AssetMetadata)
    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def has_content(self) -> bool:
        return bool(self.markdown and self.markdown.strip())

    def has_structured_rows(self) -> bool:
        return bool(self.rows)

    def to_embedding_text(self) -> str:
        parts = []

        if self.metadata.caption:
            parts.append(f"Table Caption: {self.metadata.caption}")

        parts.append(self.markdown)

        return "\n".join(parts)
