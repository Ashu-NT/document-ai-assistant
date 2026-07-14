import inspect
from typing import Any

from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)
from src.application.workflows.parsing.normalizers.docling_table_row_grid_builder import (
    DoclingTableRowGridBuilder,
)


class DoclingTableExtractor:
    def __init__(
        self,
        *,
        row_grid_builder: DoclingTableRowGridBuilder | None = None,
    ) -> None:
        self.row_grid_builder = row_grid_builder or DoclingTableRowGridBuilder()

    def is_table_item(self, item: Any) -> bool:
        raw_ref = self._extract_raw_ref(item)
        if raw_ref.startswith("#/tables/"):
            return True

        label = self._lower_label(item)
        if label in {"table", "document_index"}:
            return True

        table_cells = self._extract_table_cells(item)
        return bool(table_cells)

    def extract_markdown(
        self,
        item: Any,
        *,
        doc: Any | None = None,
    ) -> str | None:
        for attribute_name in ("markdown", "md", "text"):
            value = self._get_value(item, attribute_name)
            cleaned = self._clean_text(value)
            if cleaned:
                return cleaned

        for method_name in ("export_to_markdown", "to_markdown"):
            method = getattr(item, method_name, None)
            if callable(method):
                try:
                    cleaned = self._clean_text(
                        self._call_markdown_method(method, doc=doc)
                    )
                except Exception:
                    cleaned = None
                if cleaned:
                    return cleaned

        rows = self._extract_rows(item)
        if not rows:
            return None

        if len(rows[0]) == 1:
            return "\n".join(f"| {row[0]} |" for row in rows)

        header = rows[0]
        separator = ["---"] * len(header)
        body = rows[1:]
        markdown_rows = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(separator) + " |",
        ]
        markdown_rows.extend("| " + " | ".join(row) + " |" for row in body)
        return "\n".join(markdown_rows)

    def extract_dimensions(self, item: Any) -> tuple[int | None, int | None]:
        table_cells = self._extract_table_cells(item)
        if not table_cells:
            return (None, None)

        row_count = max(
            (
                self._resolve_offset_end(cell, "end_row_offset_idx", "start_row_offset_idx")
                for cell in table_cells
            ),
            default=0,
        )
        column_count = max(
            (
                self._resolve_offset_end(cell, "end_col_offset_idx", "start_col_offset_idx")
                for cell in table_cells
            ),
            default=0,
        )

        return (
            row_count or None,
            column_count or None,
        )

    def _resolve_offset_end(self, cell: Any, end_key: str, start_key: str) -> int:
        # `or` would treat a legitimate offset of 0 as falsy and fall
        # through to the start-offset fallback - check for None
        # explicitly instead.
        end_value = self._coerce_int(self._get_value(cell, end_key))
        if end_value is not None:
            return end_value
        start_value = self._coerce_int(self._get_value(cell, start_key))
        return (start_value or 0) + 1

    def extract_rows(self, item: Any) -> list[list[str]]:
        return self._extract_rows(item)

    def extract_cell_spans(self, item: Any) -> list[dict[str, object]]:
        table_cells = self._extract_table_cells(item)
        spans: list[dict[str, object]] = []

        for cell in table_cells:
            row_start = self._coerce_int(self._get_value(cell, "start_row_offset_idx"))
            row_end = self._coerce_int(self._get_value(cell, "end_row_offset_idx"))
            col_start = self._coerce_int(self._get_value(cell, "start_col_offset_idx"))
            col_end = self._coerce_int(self._get_value(cell, "end_col_offset_idx"))
            text = self._clean_text(self._get_value(cell, "text"))
            if (
                row_start is None
                or row_end is None
                or col_start is None
                or col_end is None
                or not text
            ):
                continue

            raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
            spans.append(
                {
                    "row_start": row_start,
                    "row_end": max(row_start, row_end - 1),
                    "col_start": col_start,
                    "col_end": max(col_start, col_end - 1),
                    "text": text,
                    "normalized_text": " ".join(raw_lines) if raw_lines else text,
                    "raw_lines": raw_lines,
                }
            )

        return spans

    @staticmethod
    def _call_markdown_method(
        method: Any,
        *,
        doc: Any | None = None,
    ) -> Any:
        if doc is None:
            return method()

        try:
            parameters = inspect.signature(method).parameters
        except (TypeError, ValueError):
            parameters = {}

        if "doc" in parameters:
            return method(doc=doc)

        return method()

    def _extract_rows(self, item: Any) -> list[list[str]]:
        table_cells = self._extract_table_cells(item)
        if not table_cells:
            return []

        return self.row_grid_builder.build_rows(table_cells)

    def _extract_table_cells(self, item: Any) -> list[Any]:
        data = self._get_value(item, "data")
        if data is None:
            return []

        table_cells = self._get_value(data, "table_cells")
        if isinstance(table_cells, list):
            return table_cells

        return []

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

    @classmethod
    def _lower_label(cls, item: Any) -> str:
        label = cls._get_value(item, "label")
        if label is None:
            return ""

        value = cls._get_value(label, "value")
        if value is not None:
            return str(value).lower()

        return str(label).lower()

    @classmethod
    def _extract_raw_ref(cls, item: Any) -> str:
        for attribute_name in ("self_ref", "ref", "id", "uuid"):
            value = cls._get_value(item, attribute_name)
            if value is None:
                continue

            text = str(value).strip()
            if text:
                return text

        return ""

    @staticmethod
    def _get_value(value: Any, name: str) -> Any:
        if value is None:
            return None

        if isinstance(value, dict):
            return value.get(name)

        return getattr(value, name, None)
