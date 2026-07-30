from __future__ import annotations

import re

from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    normalize_cell,
)

_ENUMERATION_PATTERN = re.compile(r"^\(?\d+[A-Za-z]?\)?[.)]?$")


class TroubleshootingRowParser:
    def parse(
        self,
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
            field: self._best_field_value(values)
            for field, values in candidates.items()
        }
        used_extra_indexes = self._promote_richer_extras(
            parsed=parsed,
            extras=extras,
            header_indexes=header_indexes,
        )

        if extras:
            existing_notes = parsed.get("notes", "")
            parsed["notes"] = " | ".join(
                part
                for part in (
                    existing_notes,
                    *(value for index, value in extras if index not in used_extra_indexes),
                )
                if part
            )

        signal_fields = [
            field for field in ("symptom", "cause", "remedy") if parsed.get(field)
        ]
        if not signal_fields:
            return None
        return parsed

    def _best_field_value(self, values: list[tuple[int, str]]) -> str:
        return max(values, key=self._field_value_score)[1]

    @staticmethod
    def _field_value_score(item: tuple[int, str]) -> tuple[int, int]:
        value = item[1]
        normalized = value.casefold()
        score = 0 if _ENUMERATION_PATTERN.match(normalized) else 3
        score += sum(character.isalpha() for character in value)
        return score, len(value)

    def _promote_richer_extras(
        self,
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
        if self._needs_richer_value(parsed.get("cause")):
            candidate = self._candidate_from_extras(
                extras,
                lower_bound=cause_index,
                upper_bound=remedy_index,
            )
            if candidate is not None:
                used_indexes.add(candidate[0])
                parsed["cause"] = candidate[1]
        if self._needs_richer_value(parsed.get("remedy")):
            candidate = self._candidate_from_extras(
                extras,
                lower_bound=remedy_index if remedy_index is not None else cause_index,
            )
            if candidate is not None:
                used_indexes.add(candidate[0])
                parsed["remedy"] = candidate[1]
        return used_indexes

    def _candidate_from_extras(
        self,
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
            and not self._needs_richer_value(value)
        ]
        return max(candidates, key=lambda item: len(item[1])) if candidates else None

    @staticmethod
    def _needs_richer_value(value: str | None) -> bool:
        normalized = normalize_cell(value)
        return not normalized or _ENUMERATION_PATTERN.match(normalized.casefold()) is not None
