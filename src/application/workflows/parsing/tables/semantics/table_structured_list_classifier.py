from __future__ import annotations

import re

from src.application.workflows.parsing.tables.semantics.table_text_signal_matcher import (
    TableTextSignalMatcher,
)

_IDENTIFIER_ROW_PATTERN = re.compile(
    r"^(?:[a-z]\d+\b|\d{3,4}\b|\d+\.\d+\b|[a-z]\.\d{2}(?:\.\d{2})+\b|[a-z0-9]{1,6}(?:[./-][a-z0-9]{1,6})+\b)",
    re.IGNORECASE,
)


class TableStructuredListClassifier:
    def __init__(
        self,
        *,
        signal_matcher: TableTextSignalMatcher | None = None,
    ) -> None:
        self.signal_matcher = signal_matcher or TableTextSignalMatcher()

    def looks_like_spare_parts_table(
        self,
        *,
        headers: list[str],
        labels: list[str],
        body_rows: list[list[str]],
        direct_text: str,
        section_text: str,
    ) -> bool:
        header_text = self.signal_matcher.normalized_text(*headers)
        label_text = self.signal_matcher.normalized_text(*labels)
        primary_markers = (
            "spare part",
            "qty",
            "quantity",
            "denomination",
            "service package",
        )
        secondary_markers = (
            "part number",
            "part no",
            "part nr",
            "position",
            "position no",
            "pos nr",
        )
        spare_part_markers = primary_markers + secondary_markers
        direct_hits = self.signal_matcher.count_unique(direct_text, spare_part_markers)
        primary_hits = self.signal_matcher.count_unique(direct_text, primary_markers)
        header_hits = self.signal_matcher.count_unique(header_text, spare_part_markers)
        header_primary_hits = self.signal_matcher.count_unique(header_text, primary_markers)
        label_hits = self.signal_matcher.count_unique(
            label_text,
            ("spare part", "position", "service package"),
        )
        code_rows = self.count_identifier_like_rows(body_rows)
        return (
            primary_hits >= 1 and direct_hits >= 2 and (header_hits >= 1 or label_hits >= 1)
        ) or (
            code_rows >= 3 and header_hits >= 2 and header_primary_hits >= 1
        ) or (
            code_rows >= 3
            and (
                self.signal_matcher.contains(section_text, "spare parts")
                or self.signal_matcher.contains(section_text, "spare parts list")
            )
        )

    def looks_like_identifier_table(
        self,
        *,
        headers: list[str],
        labels: list[str],
        body_rows: list[list[str]],
        direct_text: str,
    ) -> bool:
        header_text = self.signal_matcher.normalized_text(*headers)
        label_text = self.signal_matcher.normalized_text(*labels)
        markers = (
            "serial number",
            "part number",
            "part no",
            "part nr",
            "tag",
            "tag number",
            "model",
            "code",
            "service function",
            "type",
        )
        direct_hits = self.signal_matcher.count_unique(
            self.signal_matcher.normalized_text(label_text, direct_text),
            markers,
        )
        technical_header_hits = self.signal_matcher.count_unique(
            self.signal_matcher.normalized_text(label_text, header_text),
            ("voltage", "power", "pressure", "temperature", "capacity"),
        )
        identifier_rows = self.count_identifier_like_rows(body_rows)
        header_hits = self.signal_matcher.count_unique(
            header_text,
            ("serial number", "part number", "part no", "part nr", "tag", "model", "service function", "type"),
        )
        return (
            direct_hits >= 2
            and technical_header_hits == 0
            and (
                identifier_rows >= 3
                or (
                    identifier_rows >= 2
                    and header_hits >= 2
                )
            )
        )

    def looks_like_connection_table(
        self,
        *,
        headers: list[str],
        direct_text: str,
    ) -> bool:
        header_text = self.signal_matcher.normalized_text(*headers)
        direct_markers = ("terminal", "connection", "wire", "signal", "conductor")
        direct_hits = self.signal_matcher.count_unique(direct_text, direct_markers)
        header_hits = self.signal_matcher.count_unique(
            header_text,
            direct_markers + ("pin",),
        )
        return direct_hits >= 2 and header_hits >= 1

    def looks_like_sensor_instrument_table(
        self,
        *,
        headers: list[str],
        direct_text: str,
    ) -> bool:
        header_text = self.signal_matcher.normalized_text(*headers)
        structural_markers = (
            "tag",
            "tag number",
            "service function",
            "type",
            "p id",
            "p and id",
        )
        device_markers = (
            "sensor",
            "instrument",
            "switch",
            "transmitter",
            "detector",
            "radar",
            "probe",
        )
        return (
            self.signal_matcher.count_unique(direct_text, device_markers) >= 2
            and self.signal_matcher.count_unique(
                self.signal_matcher.normalized_text(header_text, direct_text),
                structural_markers,
            ) >= 1
        )

    @staticmethod
    def count_identifier_like_rows(rows: list[list[str]]) -> int:
        count = 0
        for row in rows:
            row_text = " ".join(
                str(cell or "").strip()
                for cell in row
                if str(cell or "").strip()
            )
            if row_text and _IDENTIFIER_ROW_PATTERN.match(row_text):
                count += 1
        return count
