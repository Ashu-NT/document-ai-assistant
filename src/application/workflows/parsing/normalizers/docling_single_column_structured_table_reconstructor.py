from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class _HeaderSpec:
    headers: tuple[str, ...]
    expects_trailing_code: bool


class DoclingSingleColumnStructuredTableReconstructor:
    _LEADING_CODE_PATTERN = re.compile(
        r"^(?P<code>(?:[A-Z]\.\d{2}(?:\.\d{2})+)|(?:[A-Z]\d+(?:[./-][A-Z0-9]+)*)|(?:\d+\.\d+(?:\.\d+)*))\b",
        re.IGNORECASE,
    )
    _TRAILING_CODE_PATTERN = re.compile(
        r"(?P<code>(?:-?[A-Z0-9]+(?:[./-][A-Z0-9]+)+)|(?:[A-Z]\d{3,}[A-Z0-9-]*))$",
        re.IGNORECASE,
    )
    _WHITESPACE_PATTERN = re.compile(r"\s+")

    def reconstruct(self, rows: list[list[str]]) -> list[list[str]]:
        if len(rows) < 2 or not self._looks_single_column(rows):
            return rows

        header_spec = self._infer_header_spec(rows[0][0])
        if header_spec is None:
            return rows

        reconstructed_rows = [list(header_spec.headers)]
        successful_rows = 0
        for row in rows[1:]:
            reconstructed = self._reconstruct_row(
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

    def _infer_header_spec(self, header_cell: str) -> _HeaderSpec | None:
        normalized = self._normalize_for_match(header_cell)
        if not normalized:
            return None

        lead_label = self._first_present_label(
            normalized,
            (
                ("p&id pos nr.", "P&ID Pos Nr."),
                ("pid pos nr.", "P&ID Pos Nr."),
                ("position no.", "Position No."),
                ("pos nr.", "Pos Nr."),
                ("tag number", "Tag Number"),
                ("tag", "Tag"),
            ),
        )
        tail_label = self._last_present_label(
            normalized,
            (
                ("part no.", "Part No."),
                ("part nr.", "Part No."),
                ("part number", "Part No."),
                ("serial number", "Serial Number"),
                ("model number", "Model Number"),
                ("order code", "Order Code"),
            ),
        )
        if lead_label is not None:
            middle_label = self._middle_label(
                normalized,
                lead_label=lead_label,
                tail_label=tail_label,
            )
            if tail_label is not None:
                return _HeaderSpec(
                    headers=(lead_label, middle_label, tail_label),
                    expects_trailing_code=True,
                )
            return _HeaderSpec(
                headers=(lead_label, middle_label),
                expects_trailing_code=False,
            )

        return None

    def _reconstruct_row(
        self,
        value: str,
        *,
        header_spec: _HeaderSpec,
    ) -> list[str] | None:
        normalized = self._normalize(value)
        if not normalized:
            return None

        leading_match = self._LEADING_CODE_PATTERN.match(normalized)
        if leading_match is None:
            return None

        leading_code = self._normalize(leading_match.group("code"))
        remaining = self._normalize(normalized[leading_match.end() :])
        trailing_code = ""
        if header_spec.expects_trailing_code:
            trailing_match = self._TRAILING_CODE_PATTERN.search(remaining)
            if trailing_match is not None:
                trailing_code = self._normalize(trailing_match.group("code"))
                remaining = self._normalize(remaining[: trailing_match.start()])

        if len(header_spec.headers) == 2:
            if not remaining:
                return None
            return [leading_code, remaining]

        if not remaining:
            return None
        return [leading_code, remaining, trailing_code]

    def _middle_label(
        self,
        normalized_header: str,
        *,
        lead_label: str,
        tail_label: str | None,
    ) -> str:
        lead_index = normalized_header.find(self._normalize_for_match(lead_label))
        lead_end = lead_index + len(self._normalize_for_match(lead_label))
        tail_index = (
            normalized_header.rfind(self._normalize_for_match(tail_label))
            if tail_label is not None
            else len(normalized_header)
        )
        middle = self._normalize(normalized_header[lead_end:tail_index])
        return middle.title() if middle else "Description"

    def _first_present_label(
        self,
        normalized_header: str,
        labels: tuple[tuple[str, str], ...],
    ) -> str | None:
        for marker, label in labels:
            if self._normalize_for_match(marker) in normalized_header:
                return label
        return None

    def _last_present_label(
        self,
        normalized_header: str,
        labels: tuple[tuple[str, str], ...],
    ) -> str | None:
        for marker, label in labels:
            if self._normalize_for_match(marker) in normalized_header:
                return label
        return None

    def _normalize(self, value: str | None) -> str:
        return self._WHITESPACE_PATTERN.sub(" ", str(value or "")).strip()

    def _normalize_for_match(self, value: str | None) -> str:
        return self._normalize(value).casefold()
