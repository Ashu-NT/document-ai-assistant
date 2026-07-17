from __future__ import annotations

import re

from src.application.workflows.parsing.tables.rows.normalized_table_rows import (
    NormalizedTableRows,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    looks_explicit_header_cell,
    normalize_cell,
)
from src.domain.assets.table_cell_span import TableCellSpan
from src.application.workflows.parsing.tables.normalization.troubleshooting_row_continuation_merger import (
    TroubleshootingRowContinuationMerger,
)
from src.application.workflows.parsing.tables.normalization.troubleshooting_row_continuation_evidence_builder import (
    TroubleshootingRowContinuationEvidenceBuilder,
)
from src.application.workflows.parsing.tables.normalization.troubleshooting_row_parser import (
    TroubleshootingRowParser,
)

_FIELD_ORDER = ("symptom", "cause", "remedy", "notes")
_FIELD_LABELS = {
    "symptom": "Symptom",
    "cause": "Cause",
    "remedy": "Remedy",
    "notes": "Notes",
}
_FIELD_MARKERS = {
    "symptom": ("fault", "problem", "symptom", "trouble", "warning"),
    "cause": (
        "cause",
        "causes",
        "probable cause",
        "probable causes",
        "possible cause",
        "possible causes",
        "reason",
    ),
    "remedy": (
        "action",
        "corrective action",
        "measure",
        "possible remedies",
        "rectification",
        "remedies",
        "remedy",
        "solution",
    ),
    "notes": ("comment", "comments", "note", "notes", "remark", "remarks"),
}
_NUMBERING_TOKEN_PATTERN = re.compile(r"^\(?\d{1,3}[a-z]?[).]?$", re.IGNORECASE)
_ENUMERATION_PATTERN = re.compile(r"^\(?\d+[A-Za-z]?\)?[.)]?$")
_ROW_CONTINUATION_MERGER = TroubleshootingRowContinuationMerger()
_ROW_CONTINUATION_EVIDENCE_BUILDER = (
    TroubleshootingRowContinuationEvidenceBuilder()
)
_ROW_PARSER = TroubleshootingRowParser()


class TroubleshootingTableNormalizer:
    def normalize(
        self,
        rows: list[list[str]],
        *,
        table_category: str | None,
        chunk_type: str | None,
        cell_spans: list[TableCellSpan] | None = None,
    ) -> NormalizedTableRows | None:
        if not self._should_normalize(
            table_category=table_category,
            chunk_type=chunk_type,
        ):
            return None

        if len(rows) < 2:
            return None

        header_indexes = self._header_indexes(rows[0])
        if not header_indexes:
            return None
        header_indexes = self._realign_numbering_columns(
            header_indexes,
            data_rows=rows[1:],
        )

        ordered_fields = [
            field
            for field in _FIELD_ORDER
            if any(mapped_field == field for mapped_field in header_indexes.values())
        ]
        if len(ordered_fields) < 2:
            return None

        normalized_rows: list[list[str]] = []
        source_row_indexes: list[int] = []
        for source_row_index, row in enumerate(rows[1:], start=1):
            parsed = _ROW_PARSER.parse(row=row, header_indexes=header_indexes)
            if parsed is None:
                continue
            normalized_rows.append([parsed.get(field, "") for field in ordered_fields])
            source_row_indexes.append(source_row_index)

        if not normalized_rows:
            return None
        continuation_evidence = _ROW_CONTINUATION_EVIDENCE_BUILDER.build(
            source_row_indexes=source_row_indexes,
            header_indexes=header_indexes,
            cell_spans=cell_spans,
        )
        normalized_rows = _ROW_CONTINUATION_MERGER.merge(
            headers=[_FIELD_LABELS[field] for field in ordered_fields],
            rows=normalized_rows,
            source_row_indexes=source_row_indexes,
            continuation_evidence=continuation_evidence,
        )

        return NormalizedTableRows(
            headers=[_FIELD_LABELS[field] for field in ordered_fields],
            rows=normalized_rows,
        )

    @staticmethod
    def _should_normalize(
        *,
        table_category: str | None,
        chunk_type: str | None,
    ) -> bool:
        normalized_category = (table_category or "").strip().lower()
        if normalized_category == "troubleshooting_table":
            return True
        return (chunk_type or "").strip().lower() == "troubleshooting"

    def _header_indexes(self, header_row: list[str]) -> dict[int, str]:
        normalized_headers = [normalize_cell(cell).casefold() for cell in header_row]
        if not any(looks_explicit_header_cell(cell) for cell in normalized_headers if cell):
            return {}

        header_indexes: dict[int, str] = {}
        for index, header in enumerate(normalized_headers):
            mapped_field = self._map_header(header)
            if mapped_field is not None:
                header_indexes[index] = mapped_field
        return header_indexes

    def _map_header(self, header: str) -> str | None:
        for field in _FIELD_ORDER:
            if any(self._contains_marker(header, marker) for marker in _FIELD_MARKERS[field]):
                return field
        # "Description" is a bare, low-signal fallback for the symptom
        # column - checked only after every field's own real marker has
        # had a chance, so a genuine "Cause Description"/"Remedy
        # Description" compound header still maps to its real field
        # first instead of being swallowed as a symptom.
        if self._contains_marker(header, "description"):
            return "symptom"
        return None

    @staticmethod
    def _contains_marker(header: str, marker: str) -> bool:
        return re.search(rf"\b{re.escape(marker)}s?\b", header) is not None

    @staticmethod
    def _realign_numbering_columns(
        header_indexes: dict[int, str],
        *,
        data_rows: list[list[str]],
    ) -> dict[int, str]:
        if not data_rows:
            return header_indexes

        realigned = dict(header_indexes)
        for index, field in header_indexes.items():
            next_index = index + 1
            if next_index in header_indexes:
                continue

            inspected = 0
            numbering_like = 0
            next_column_populated = 0
            for row in data_rows:
                if index >= len(row):
                    continue
                value = normalize_cell(row[index])
                if not value:
                    continue
                inspected += 1
                if _NUMBERING_TOKEN_PATTERN.match(value):
                    numbering_like += 1
                if next_index < len(row) and normalize_cell(row[next_index]):
                    next_column_populated += 1

            if inspected == 0 or numbering_like != inspected:
                continue
            if next_column_populated < inspected:
                continue
            realigned[next_index] = field
            del realigned[index]
        return realigned
