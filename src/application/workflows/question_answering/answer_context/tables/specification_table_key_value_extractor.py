from __future__ import annotations

from typing import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
)
from src.application.workflows.question_answering.answer_context.tables.table_header_semantics import (
    looks_identifier_label,
)
from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
)

_SPECIFICATION_INTENTS = {
    AnswerIntent.CERTIFICATION_SUMMARY,
    AnswerIntent.IDENTIFIER_LOOKUP,
    AnswerIntent.SPECIFICATION_SUMMARY,
    AnswerIntent.TABLE_SUMMARY,
}
_CANONICAL_LABEL_ALIASES: dict[str, str] = {
    "part no": "Part Number",
    "part no.": "Part Number",
    "part nr": "Part Number",
    "part nr.": "Part Number",
    "serial no": "Serial Number",
    "serial no.": "Serial Number",
    "serial nr": "Serial Number",
    "serial nr.": "Serial Number",
}


class SpecificationTableKeyValueExtractor:
    def extract(
        self,
        tables: Sequence[AnswerTable],
        *,
        answer_intent: AnswerIntent,
    ) -> list[AnswerKeyValue]:
        if answer_intent not in _SPECIFICATION_INTENTS:
            return []

        key_values: list[AnswerKeyValue] = []
        seen: set[tuple[int, str, str]] = set()
        for table in tables:
            for item in self._iter_key_values(table, answer_intent=answer_intent):
                fingerprint = (
                    item.source_number,
                    item.key.lower(),
                    item.value.lower(),
                )
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                key_values.append(item)
        return key_values

    def _iter_key_values(
        self,
        table: AnswerTable,
        *,
        answer_intent: AnswerIntent,
    ):
        if table.table_kind in {
            TableQueryStrategy.MAINTENANCE_SCHEDULE_TABLE,
            TableQueryStrategy.MAINTENANCE_SCHEDULE_MATRIX,
        }:
            return []

        if table.table_kind == TableQueryStrategy.KEY_VALUE_TABLE:
            return list(self._key_value_rows(table, answer_intent=answer_intent))

        if table.table_kind == TableQueryStrategy.SPECIFICATION_MATRIX:
            if self._looks_label_value_projection(table):
                return list(self._key_value_rows(table, answer_intent=answer_intent))
            return list(self._record_rows(table, answer_intent=answer_intent))

        if table.table_kind == TableQueryStrategy.RECORD_TABLE:
            return list(self._record_rows(table, answer_intent=answer_intent))

        if not table.headers and self._looks_pair_table(table):
            return list(self._pair_rows(table, answer_intent=answer_intent))

        return []

    def _key_value_rows(
        self,
        table: AnswerTable,
        *,
        answer_intent: AnswerIntent,
    ):
        label_index = self._first_column_with_role(table, "label", default=0)
        value_index = self._first_column_with_role(table, "value", default=1)
        for row in table.rows:
            if label_index >= len(row.cells) or value_index >= len(row.cells):
                continue
            label = self._clean_label(row.cells[label_index])
            value = self._clean_value(row.cells[value_index])
            key_value = self._build_key_value(
                label=label,
                value=value,
                source_number=table.source_number,
                answer_intent=answer_intent,
            )
            if key_value is not None:
                yield key_value

    def _record_rows(
        self,
        table: AnswerTable,
        *,
        answer_intent: AnswerIntent,
    ):
        for row in table.rows:
            for header, value in row.cells_by_header.items():
                key_value = self._build_key_value(
                    label=self._clean_label(header),
                    value=self._clean_value(value),
                    source_number=table.source_number,
                    answer_intent=answer_intent,
                )
                if key_value is not None:
                    yield key_value

    def _pair_rows(
        self,
        table: AnswerTable,
        *,
        answer_intent: AnswerIntent,
    ):
        for row in table.rows:
            if len(row.cells) < 2:
                continue
            key_value = self._build_key_value(
                label=self._clean_label(row.cells[0]),
                value=self._clean_value(row.cells[1]),
                source_number=table.source_number,
                answer_intent=answer_intent,
            )
            if key_value is not None:
                yield key_value

    @staticmethod
    def _first_column_with_role(
        table: AnswerTable,
        role: str,
        *,
        default: int,
    ) -> int:
        for index, column_role in table.column_roles.items():
            if column_role == role:
                return index
        return default

    @staticmethod
    def _looks_pair_table(table: AnswerTable) -> bool:
        if (table.chunk_type or "").strip().lower() not in {
            "certification_info",
            "technical_specification",
        }:
            return False
        return any(len(row.cells) >= 2 for row in table.rows)

    @staticmethod
    def _looks_label_value_projection(table: AnswerTable) -> bool:
        if len(table.headers) < 2:
            return False
        return (
            table.column_roles.get(0) == "label"
            and table.column_roles.get(1) == "value"
        )

    def _build_key_value(
        self,
        *,
        label: str | None,
        value: str | None,
        source_number: int,
        answer_intent: AnswerIntent,
    ) -> AnswerKeyValue | None:
        if not label or not value:
            return None
        field_kind = "identifier" if looks_identifier_label(label) else "specification"
        if answer_intent == AnswerIntent.SPECIFICATION_SUMMARY and field_kind == "identifier":
            return None
        if answer_intent == AnswerIntent.IDENTIFIER_LOOKUP and field_kind != "identifier":
            return None
        return AnswerKeyValue(
            key=label,
            value=value,
            unit=None,
            source_number=source_number,
            confidence=0.95,
            field_kind=field_kind,
        )

    @staticmethod
    def _clean_label(value: str | None) -> str | None:
        cleaned = " ".join(str(value or "").split()).strip(" |:-")
        if not cleaned:
            return None
        return _CANONICAL_LABEL_ALIASES.get(cleaned.lower(), cleaned)

    @staticmethod
    def _clean_value(value: str | None) -> str | None:
        cleaned = " ".join(str(value or "").split()).strip(" |")
        return cleaned or None
