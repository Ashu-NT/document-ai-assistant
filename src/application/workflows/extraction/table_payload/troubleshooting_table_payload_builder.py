from __future__ import annotations

from src.application.workflows.extraction.table_payload.table_payload_support import (
    TablePayloadSupport,
)
from src.domain.assets import TableAsset
from src.application.workflows.parsing.tables.normalization.troubleshooting_table_normalizer import (
    TroubleshootingTableNormalizer,
)


class TroubleshootingTablePayloadBuilder:
    def __init__(
        self,
        *,
        troubleshooting_table_normalizer: (
            TroubleshootingTableNormalizer | None
        ) = None,
        support: TablePayloadSupport | None = None,
    ) -> None:
        self.troubleshooting_table_normalizer = (
            troubleshooting_table_normalizer or TroubleshootingTableNormalizer()
        )
        self.support = support or TablePayloadSupport()

    def build(self, table: TableAsset, *, chunk_type: str | None = None) -> str | None:
        normalized = self.troubleshooting_table_normalizer.normalize(
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
        return "Structured troubleshooting records:\n" + "\n".join(lines)
