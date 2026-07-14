from __future__ import annotations

import re

from src.domain.assets.table_rows.normalized_table_rows import NormalizedTableRows
from src.domain.assets.table_rows.table_row_patterns import (
    looks_explicit_header_cell,
    normalize_cell,
)

_FIELD_ORDER = (
    "position",
    "quantity",
    "unit",
    "description",
    "part_no",
    "service_package",
)
_FIELD_LABELS = {
    "position": "Position",
    "quantity": "Quantity",
    "unit": "Unit",
    "description": "Description",
    "part_no": "Part No.",
    "service_package": "Service package",
}
_FIELD_MARKERS = {
    "position": ("position", "position no", "part pos", "pos.", "pos nr", "item no"),
    "quantity": ("qty", "quantity"),
    "unit": ("unit",),
    "description": (
        "designation",
        "denomination",
        "description",
        "size / dimension",
        "material / surface",
    ),
    "part_no": (
        "part no",
        "part number",
        "spare part no",
        "article no",
        "material no",
        "order no",
    ),
    "service_package": ("service package", "included in service package"),
}
_POSITION_WITH_DOT_PATTERN = re.compile(
    r"(?P<position>[A-Za-z]?\d{1,4}\.\d{2})\s+(?P<description>.+?)(?=(?:\s+[A-Za-z]?\d{1,4}\.\d{2}\s+)|$)"
)
_POSITION_TOKEN_PATTERN = re.compile(r"^[A-Za-z]?\d{1,6}(?:\.\d{2})?$")
_QUANTITY_PATTERN = re.compile(r"^\d{1,4}$")
_UNIT_PATTERN = re.compile(r"^[A-Za-z]{2,12}$")
_PART_CODE_PATTERN = re.compile(r"^-?[A-Za-z0-9]+(?:[./-][A-Za-z0-9]+)*$")


class SparePartsTableNormalizer:
    def normalize(
        self,
        rows: list[list[str]],
        *,
        table_category: str | None,
        chunk_type: str | None,
    ) -> NormalizedTableRows | None:
        if not self._should_normalize(
            table_category=table_category,
            chunk_type=chunk_type,
        ):
            return None

        parsed_rows: list[dict[str, str]] = []
        detected_header_fields: list[str] = []
        candidate_row_count = 0

        for row in rows:
            normalized_cells = [normalize_cell(cell) for cell in row if normalize_cell(cell)]
            if not normalized_cells:
                continue
            if self._looks_like_title_row(normalized_cells):
                continue
            header_fields = self._header_fields(normalized_cells)
            if header_fields:
                for field in header_fields:
                    if field not in detected_header_fields:
                        detected_header_fields.append(field)
                continue

            candidate_row_count += 1
            parsed_rows.extend(self._parse_row(normalized_cells))

        if not parsed_rows:
            return None
        if candidate_row_count > 1 and len(parsed_rows) < 2:
            return None

        fields = self._header_output_fields(
            detected_header_fields=detected_header_fields,
            parsed_rows=parsed_rows,
        )
        normalized_rows = [
            [row.get(field, "") for field in fields]
            for row in parsed_rows
        ]
        return NormalizedTableRows(
            headers=[_FIELD_LABELS[field] for field in fields],
            rows=normalized_rows,
        )

    @staticmethod
    def _should_normalize(
        *,
        table_category: str | None,
        chunk_type: str | None,
    ) -> bool:
        normalized_category = (table_category or "").strip().lower()
        if normalized_category == "spare_parts_table":
            return True
        return (chunk_type or "").strip().lower() == "spare_parts_table"

    @staticmethod
    def _looks_like_title_row(cells: list[str]) -> bool:
        if len(cells) != 1:
            return False
        normalized = cells[0].casefold()
        return normalized in {"spare parts list", "spare parts", "exploded views"}

    def _header_fields(self, cells: list[str]) -> list[str]:
        joined = " ".join(cells).casefold()
        if not any(looks_explicit_header_cell(cell) for cell in cells) and "spare part" not in joined:
            return []

        detected: list[str] = []
        for field in _FIELD_ORDER:
            if any(marker in joined for marker in _FIELD_MARKERS[field]):
                detected.append(field)
        return detected

    @staticmethod
    def _header_output_fields(
        *,
        detected_header_fields: list[str],
        parsed_rows: list[dict[str, str]],
    ) -> list[str]:
        detected = list(detected_header_fields)
        for field in _FIELD_ORDER:
            if field in detected:
                continue
            if any(row.get(field, "").strip() for row in parsed_rows):
                detected.append(field)
        return detected or ["description"]

    def _parse_row(self, cells: list[str]) -> list[dict[str, str]]:
        explicit_row = self._parse_explicit_row(cells)
        if explicit_row is not None:
            return [explicit_row]

        joined = " ".join(cells).strip()
        if not joined:
            return []

        position_pairs = self._parse_position_pairs(joined)
        if position_pairs:
            return position_pairs

        free_form_row = self._parse_free_form_row(joined)
        if free_form_row is not None:
            return [free_form_row]

        return []

    def _parse_explicit_row(self, cells: list[str]) -> dict[str, str] | None:
        first_cell = cells[0]
        tokens = first_cell.split()
        if len(tokens) < 2:
            return None
        if not self._looks_position_token(tokens[0]) or not _QUANTITY_PATTERN.match(tokens[1]):
            return None

        row: dict[str, str] = {
            "position": tokens[0],
            "quantity": tokens[1],
        }
        description_parts: list[str] = []

        remainder_start = 2
        if len(tokens) > 2 and _UNIT_PATTERN.match(tokens[2]):
            row["unit"] = tokens[2]
            remainder_start = 3
        if len(tokens) > remainder_start:
            description_parts.append(" ".join(tokens[remainder_start:]))

        if len(cells) >= 2 and cells[1]:
            description_parts.append(cells[1])
        description = " ".join(part.strip() for part in description_parts if part.strip()).strip()
        if description:
            row["description"] = description

        if len(cells) >= 3:
            self._apply_tail_code(row, cells[2])
        if len(cells) >= 4 and not row.get("service_package"):
            self._apply_tail_code(row, cells[3])

        if row.get("description") or row.get("part_no"):
            return row
        return None

    @staticmethod
    def _apply_tail_code(row: dict[str, str], value: str) -> None:
        normalized = normalize_cell(value)
        if not normalized:
            return
        tokens = normalized.split()
        if not tokens:
            return
        if len(tokens) >= 2 and tokens[-1].isdigit():
            row["service_package"] = tokens[-1]
            candidate = " ".join(tokens[:-1]).strip()
        else:
            candidate = normalized
        if candidate and SparePartsTableNormalizer._looks_part_code(candidate):
            row["part_no"] = candidate

    def _parse_free_form_row(self, value: str) -> dict[str, str] | None:
        tokens = value.split()
        if len(tokens) < 3:
            return None
        if not self._looks_position_token(tokens[0]) or not _QUANTITY_PATTERN.match(tokens[1]):
            return None

        row: dict[str, str] = {
            "position": tokens[0],
            "quantity": tokens[1],
        }
        description_start = 2
        if len(tokens) > 2 and _UNIT_PATTERN.match(tokens[2]):
            row["unit"] = tokens[2]
            description_start = 3
        description = " ".join(tokens[description_start:]).strip()
        if not description:
            return None
        row["description"] = description
        return row

    def _parse_position_pairs(self, value: str) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for match in _POSITION_WITH_DOT_PATTERN.finditer(value):
            description = match.group("description").strip(" ,;:-")
            if not description:
                continue
            rows.append(
                {
                    "position": match.group("position"),
                    "description": description,
                }
            )
        return rows

    @staticmethod
    def _looks_position_token(value: str) -> bool:
        return bool(_POSITION_TOKEN_PATTERN.match(value))

    @staticmethod
    def _looks_part_code(value: str) -> bool:
        if not value or not _PART_CODE_PATTERN.match(value):
            return False
        return any(character.isdigit() for character in value)
