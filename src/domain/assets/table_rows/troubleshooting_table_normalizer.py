from __future__ import annotations

import re

from src.domain.assets.table_rows.normalized_table_rows import NormalizedTableRows
from src.domain.assets.table_rows.table_row_patterns import (
    looks_explicit_header_cell,
    normalize_cell,
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
        "remedies",
        "remedy",
        "solution",
    ),
    "notes": ("comment", "comments", "note", "notes", "remark", "remarks"),
}
_NUMBERING_TOKEN_PATTERN = re.compile(r"^\(?\d{1,3}[a-z]?[).]?$", re.IGNORECASE)
_ENUMERATION_PATTERN = re.compile(r"^\(?\d+[A-Za-z]?\)?[.)]?$")


class TroubleshootingTableNormalizer:
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
        for row in rows[1:]:
            parsed = self._parse_row(row=row, header_indexes=header_indexes)
            if parsed is None:
                continue
            normalized_rows.append([parsed.get(field, "") for field in ordered_fields])

        if not normalized_rows:
            return None

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
        return None

    @staticmethod
    def _contains_marker(header: str, marker: str) -> bool:
        """Word-boundary match, not plain substring containment - a bare
        substring check would let a short marker like "action" match
        inside an unrelated word like "reaction". A trailing "s?" tolerates
        the regular plural real headers commonly use ("Probable Causes",
        "Corrective Actions") - the one irregular plural in this
        vocabulary ("remedy" -> "remedies") is already listed as its own
        literal marker, so this never needs to handle it.
        """
        return re.search(rf"\b{re.escape(marker)}s?\b", header) is not None

    @staticmethod
    def _realign_numbering_columns(
        header_indexes: dict[int, str],
        *,
        data_rows: list[list[str]],
    ) -> dict[int, str]:
        """A header spanning a "1a) <text>" sub-column pair sometimes
        lands its label on the numbering sub-column only, leaving the
        actual text one column over, unlabeled (a Docling merged-header
        artifact, not a marker-matching problem). When a mapped column's
        values are consistently bare numbering tokens ("1a)", "(2)") and
        the very next column is unmapped and has real text, the mapping
        belongs on that next column instead.
        """
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

    @staticmethod
    def _parse_row(
        *,
        row: list[str],
        header_indexes: dict[int, str],
    ) -> dict[str, str] | None:
        candidates: dict[str, list[tuple[int, str]]] = {}
        extras: list[tuple[int, str]] = []
        for index, cell in enumerate(row):
            value = normalize_cell(cell)
            if not value:
                continue
            mapped_field = header_indexes.get(index)
            if mapped_field is None:
                extras.append((index, value))
                continue
            candidates.setdefault(mapped_field, []).append((index, value))

        parsed = {
            field: TroubleshootingTableNormalizer._best_field_value(values)
            for field, values in candidates.items()
        }
        used_extra_indexes = TroubleshootingTableNormalizer._promote_richer_extras(
            parsed=parsed,
            extras=extras,
            header_indexes=header_indexes,
        )

        if extras:
            existing_notes = parsed.get("notes", "")
            parsed["notes"] = " | ".join(
                part for part in (
                    existing_notes,
                    *(
                        value
                        for index, value in extras
                        if index not in used_extra_indexes
                    ),
                ) if part
            )

        signal_fields = [
            field for field in ("symptom", "cause", "remedy") if parsed.get(field)
        ]
        if not signal_fields:
            return None
        return parsed

    @staticmethod
    def _best_field_value(values: list[tuple[int, str]]) -> str:
        return max(values, key=TroubleshootingTableNormalizer._field_value_score)[1]

    @staticmethod
    def _field_value_score(item: tuple[int, str]) -> tuple[int, int]:
        value = item[1]
        normalized = value.casefold()
        score = 0 if _ENUMERATION_PATTERN.match(normalized) else 3
        score += sum(character.isalpha() for character in value)
        return score, len(value)

    @staticmethod
    def _promote_richer_extras(
        *,
        parsed: dict[str, str],
        extras: list[tuple[int, str]],
        header_indexes: dict[int, str],
    ) -> set[int]:
        used_indexes: set[int] = set()
        if not extras:
            return used_indexes
        cause_index = min(
            (index for index, field in header_indexes.items() if field == "cause"),
            default=None,
        )
        remedy_index = min(
            (index for index, field in header_indexes.items() if field == "remedy"),
            default=None,
        )
        if TroubleshootingTableNormalizer._needs_richer_value(parsed.get("cause")):
            candidate = TroubleshootingTableNormalizer._candidate_from_extras(
                extras,
                lower_bound=cause_index,
                upper_bound=remedy_index,
            )
            if candidate is not None:
                used_indexes.add(candidate[0])
                parsed["cause"] = candidate[1]
        if TroubleshootingTableNormalizer._needs_richer_value(parsed.get("remedy")):
            candidate = TroubleshootingTableNormalizer._candidate_from_extras(
                extras,
                lower_bound=remedy_index if remedy_index is not None else cause_index,
            )
            if candidate is not None:
                used_indexes.add(candidate[0])
                parsed["remedy"] = candidate[1]
        return used_indexes

    @staticmethod
    def _candidate_from_extras(
        extras: list[tuple[int, str]],
        *,
        lower_bound: int | None,
        upper_bound: int | None = None,
    ) -> tuple[int, str] | None:
        candidates = [
            (index, value)
            for index, value in extras
            if (lower_bound is None or index > lower_bound)
            and (upper_bound is None or index < upper_bound)
            and not TroubleshootingTableNormalizer._needs_richer_value(value)
        ]
        return max(candidates, key=lambda item: len(item[1])) if candidates else None

    @staticmethod
    def _needs_richer_value(value: str | None) -> bool:
        normalized = normalize_cell(value)
        return not normalized or _ENUMERATION_PATTERN.match(normalized.casefold()) is not None
