from dataclasses import dataclass, field

from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.assets.table_cell_span import TableCellSpan
from src.domain.assets.table_rows.performance_curve_matrix_normalizer import (
    PerformanceCurveMatrixNormalizer,
)
from src.domain.assets.table_rows.structured_row_renderer import (
    StructuredRowRenderer,
)
from src.domain.common import AuditMetadata

_STRUCTURED_ROW_RENDERER = StructuredRowRenderer()
_PERFORMANCE_CURVE_NORMALIZER = PerformanceCurveMatrixNormalizer()


@dataclass(slots=True)
class TableAsset:
    table_id: str
    document_id: str

    markdown: str

    parent_section_id: str | None = None

    rows: list[list[str]] = field(default_factory=list)
    row_ids: list[str] = field(default_factory=list)
    cell_spans: list[TableCellSpan] = field(default_factory=list)
    row_count: int | None = None
    column_count: int | None = None
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

    def to_structured_row_text(self) -> str | None:
        return _STRUCTURED_ROW_RENDERER.render(
            self.rows,
            table_category=self.table_category,
            table_shape=self.resolved_table_shape(),
        )

    def resolved_table_shape(self) -> str | None:
        if self.table_shape:
            return self.table_shape
        if _PERFORMANCE_CURVE_NORMALIZER.normalize(self.rows) is not None:
            return "performance_curve_matrix"
        return None
