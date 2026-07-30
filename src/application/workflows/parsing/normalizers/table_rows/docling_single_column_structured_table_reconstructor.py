from __future__ import annotations

from src.application.workflows.parsing.normalizers.table_rows.docling_single_column_row_parser import (
    DoclingSingleColumnRowParser,
    SingleColumnHeaderSpec,
)


class DoclingSingleColumnStructuredTableReconstructor:
    def __init__(
        self,
        *,
        row_parser: DoclingSingleColumnRowParser | None = None,
    ) -> None:
        self.row_parser = row_parser or DoclingSingleColumnRowParser()

    def reconstruct(self, rows: list[list[str]]) -> list[list[str]]:
        if len(rows) < 2 or not self._looks_single_column(rows):
            return rows

        header_spec = self._infer_header_spec(rows[0][0])
        if header_spec is None:
            return rows
        header_spec = self.row_parser.enable_quantity_column_when_supported(
            rows[1:],
            header_spec=header_spec,
        )

        reconstructed_rows = [list(header_spec.headers)]
        successful_rows = 0
        for row in rows[1:]:
            reconstructed = self.row_parser.reconstruct_row(
                row[0],
                header_spec=header_spec,
            )
            if reconstructed is None:
                return rows
            reconstructed_rows.append(reconstructed)
            successful_rows += 1

        if successful_rows < max(2, len(rows) - 1):
            return rows
        return reconstructed_rows

    @staticmethod
    def _looks_single_column(rows: list[list[str]]) -> bool:
        return all(len(row) == 1 for row in rows)

    def _infer_header_spec(self, header_cell: str) -> SingleColumnHeaderSpec | None:
        normalized = self.row_parser.normalize_for_match(header_cell)
        if not normalized:
            return None

        lead_label = self._first_present_label(
            normalized,
            (
                ("p id pos nr", "P&ID Pos Nr."),
                ("pid pos nr", "P&ID Pos Nr."),
                ("position no", "Position No."),
                ("pos nr", "Pos Nr."),
                ("tag number", "Tag Number"),
                ("tag", "Tag"),
            ),
        )
        tail_label = self._last_present_label(
            normalized,
            (
                ("part no", "Part No."),
                ("part nr", "Part No."),
                ("part number", "Part No."),
                ("serial number", "Serial Number"),
                ("model number", "Model Number"),
                ("order code", "Order Code"),
            ),
        )
        if lead_label is None:
            return None

        middle_label = self._middle_label(
            normalized,
            lead_label=lead_label,
            tail_label=tail_label,
        )
        if tail_label is not None:
            return SingleColumnHeaderSpec(
                headers=(lead_label, middle_label, tail_label),
                expects_trailing_code=True,
            )
        return SingleColumnHeaderSpec(
            headers=(lead_label, middle_label),
            expects_trailing_code=False,
        )

    def _middle_label(
        self,
        normalized_header: str,
        *,
        lead_label: str,
        tail_label: str | None,
    ) -> str:
        normalized_lead = self.row_parser.normalize_for_match(lead_label)
        lead_index = normalized_header.find(normalized_lead)
        lead_end = lead_index + len(normalized_lead)
        tail_index = (
            normalized_header.rfind(self.row_parser.normalize_for_match(tail_label))
            if tail_label is not None
            else len(normalized_header)
        )
        middle = self.row_parser.normalize(normalized_header[lead_end:tail_index])
        return middle.title() if middle else "Description"

    def _first_present_label(
        self,
        normalized_header: str,
        labels: tuple[tuple[str, str], ...],
    ) -> str | None:
        for marker, label in labels:
            if self.row_parser.normalize_for_match(marker) in normalized_header:
                return label
        return None

    def _last_present_label(
        self,
        normalized_header: str,
        labels: tuple[tuple[str, str], ...],
    ) -> str | None:
        for marker, label in labels:
            if self.row_parser.normalize_for_match(marker) in normalized_header:
                return label
        return None
