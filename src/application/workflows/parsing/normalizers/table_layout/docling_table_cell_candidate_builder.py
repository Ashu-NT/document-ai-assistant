from __future__ import annotations

from typing import Any

from src.application.workflows.parsing.normalizers.docling_provenance_extractor import (
    DoclingProvenanceExtractor,
)
from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)
from src.domain.assets import TableCellSpan


class DoclingTableCellCandidateBuilder:
    def __init__(
        self,
        *,
        provenance_extractor: DoclingProvenanceExtractor | None = None,
    ) -> None:
        self.provenance_extractor = provenance_extractor or DoclingProvenanceExtractor()

    def build(self, table_cells: list[Any]) -> list[TableCellSpan]:
        spans: list[TableCellSpan] = []
        for cell in table_cells:
            row_start = self._coerce_int(self._get_value(cell, "start_row_offset_idx"))
            row_end = self._coerce_int(self._get_value(cell, "end_row_offset_idx"))
            col_start = self._coerce_int(self._get_value(cell, "start_col_offset_idx"))
            col_end = self._coerce_int(self._get_value(cell, "end_col_offset_idx"))
            text = self._clean_text(self._get_value(cell, "text"))
            if (
                row_start is None
                or col_start is None
                or not text
            ):
                continue

            raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
            page_start, page_end = self.provenance_extractor.extract_pages(cell)
            spans.append(
                TableCellSpan(
                    row_start=row_start,
                    row_end=max(
                        row_start,
                        (row_end - 1) if row_end is not None else row_start,
                    ),
                    col_start=col_start,
                    col_end=max(
                        col_start,
                        (col_end - 1) if col_end is not None else col_start,
                    ),
                    text=text,
                    normalized_text=" ".join(raw_lines) if raw_lines else text,
                    raw_lines=raw_lines,
                    page_number=page_start or page_end,
                    bbox=self.provenance_extractor.extract_bbox(cell),
                )
            )
        return spans

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _clean_text(value: Any) -> str | None:
        if value is None:
            return None
        text = repair_docling_text(str(value)).strip()
        return text or None

    @staticmethod
    def _get_value(value: Any, name: str) -> Any:
        if value is None:
            return None
        if isinstance(value, dict):
            return value.get(name)
        return getattr(value, name, None)
