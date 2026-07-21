from __future__ import annotations

from src.application.workflows.extraction.batching.table_payload.table_payload_support import (
    TablePayloadSupport,
)
from src.domain.assets import TableAsset
from src.application.workflows.parsing.tables.normalization.spare_parts_table_normalizer import (
    SparePartsTableNormalizer,
)


class SparePartsTablePayloadBuilder:
    def __init__(
        self,
        *,
        spare_parts_table_normalizer: SparePartsTableNormalizer | None = None,
        support: TablePayloadSupport | None = None,
    ) -> None:
        self.spare_parts_table_normalizer = (
            spare_parts_table_normalizer or SparePartsTableNormalizer()
        )
        self.support = support or TablePayloadSupport()

    def build(self, table: TableAsset, *, chunk_type: str | None = None) -> str | None:
        normalized = self.spare_parts_table_normalizer.normalize(
            self.support.cleaned_rows(table),
            table_category=table.table_category,
            chunk_type=chunk_type,
        )
        if normalized is None:
            return None

        lines: list[str] = []
        for row_index, row in enumerate(normalized.rows, start=1):
            rendered_fields = self.support.render_fields(normalized.headers, row)
            if rendered_fields:
                lines.append(f"Row {row_index}: " + " | ".join(rendered_fields))

        if not lines:
            return None
        return "Structured spare-parts records:\n" + "\n".join(lines)
