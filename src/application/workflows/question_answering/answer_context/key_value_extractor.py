from __future__ import annotations

import re
from typing import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
    AnswerSource,
)
from src.application.workflows.question_answering.answer_context.tables import (
    AnswerTable,
    AnswerTableProjector,
    SpecificationTableKeyValueExtractor,
)

KEY_VALUE_EXTRACTOR_RULES_VERSION = "v2"

_KEY_ALIASES: dict[str, tuple[str, ...]] = {
    "Capacity": ("capacity",),
    "Current": ("current",),
    "Date of inspection": ("date of inspection", "inspection date"),
    "Design pressure": ("design pressure",),
    "Design Temperature": ("design temperature",),
    "DN": ("dn",),
    "Material": ("material",),
    "Model": ("model", "model number"),
    "Order code": ("order code", "ordering code", "order number"),
    "Part Number": ("part number", "part no", "part no.", "part nr", "part nr."),
    "Power": ("power",),
    "Pressure": ("pressure",),
    "Quantity": ("quantity", "qty"),
    "Serial Number": ("serial number", "serial no", "serial no.", "serial nr", "serial nr."),
    "Size": ("size", "nominal size"),
    "Temperature": ("temperature",),
    "Test pressure": ("test pressure",),
    "Voltage": ("voltage",),
    "Working pressure": ("working pressure",),
}
_TABLE_ROW_PATTERN = re.compile(r"^\|(?P<cells>.+)\|$")
_KEY_VALUE_PATTERN = re.compile(
    r"^(?P<key>[A-Za-z][A-Za-z0-9 /().%-]{1,80})\s*[:=\-]\s*(?P<value>.+)$"
)
_UNIT_PATTERN = re.compile(r"\b(bar|mm|cm|m|kw|w|v|a|hz|dn|pcs|pc|c)\b", re.IGNORECASE)
_SUPPORTED_INTENTS = {
    AnswerIntent.CERTIFICATION_SUMMARY,
    AnswerIntent.IDENTIFIER_LOOKUP,
    AnswerIntent.SPECIFICATION_SUMMARY,
    AnswerIntent.TABLE_SUMMARY,
}


class KeyValueExtractor:
    def __init__(
        self,
        specification_table_extractor: SpecificationTableKeyValueExtractor | None = None,
        answer_table_projector: AnswerTableProjector | None = None,
    ) -> None:
        self.specification_table_extractor = (
            specification_table_extractor or SpecificationTableKeyValueExtractor()
        )
        self.answer_table_projector = answer_table_projector or AnswerTableProjector()

    def extract(
        self,
        sources: Sequence[AnswerSource],
        *,
        answer_intent: AnswerIntent,
        tables: Sequence[AnswerTable] | None = None,
    ) -> list[AnswerKeyValue]:
        if answer_intent not in _SUPPORTED_INTENTS:
            return []

        resolved_tables = list(tables) if tables is not None else self.answer_table_projector.build(sources)
        table_key_values = self.specification_table_extractor.extract(
            resolved_tables,
            answer_intent=answer_intent,
        )
        key_values: list[AnswerKeyValue] = list(table_key_values)
        seen: set[tuple[int, str, str]] = {
            (item.source_number, item.key.lower(), item.value.lower())
            for item in table_key_values
        }
        table_sources = {item.source_number for item in table_key_values}

        for source in sources:
            if source.source_number in table_sources:
                continue
            for raw_key, raw_value in self._candidate_pairs(source.content):
                key = self._normalize_key(raw_key)
                if key is None:
                    continue
                value = raw_value.strip().strip("|").strip()
                if not value:
                    continue
                fingerprint = (source.source_number, key.lower(), value.lower())
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                key_values.append(
                    AnswerKeyValue(
                        key=key,
                        value=value,
                        unit=self._extract_unit(value),
                        source_number=source.source_number,
                        confidence=0.9,
                        field_kind=self._field_kind(key),
                    )
                )
        return key_values

    def _candidate_pairs(self, content: str) -> list[tuple[str, str]]:
        pairs: list[tuple[str, str]] = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            table_match = _TABLE_ROW_PATTERN.match(stripped)
            if table_match is not None:
                cells = [cell.strip() for cell in table_match.group("cells").split("|")]
                if len(cells) >= 2 and cells[0] and cells[1]:
                    pairs.append((cells[0], cells[1]))
                continue

            key_value_match = _KEY_VALUE_PATTERN.match(stripped)
            if key_value_match is not None:
                pairs.append(
                    (
                        key_value_match.group("key"),
                        key_value_match.group("value"),
                    )
                )
        return pairs

    @classmethod
    def _normalize_key(cls, raw_key: str) -> str | None:
        cleaned = " ".join(str(raw_key or "").strip().split()).strip(" |:-")
        if not cleaned:
            return None
        normalized = cleaned.lower()
        for canonical, aliases in _KEY_ALIASES.items():
            if normalized == canonical.lower():
                return canonical
            if normalized in aliases:
                return canonical
        return cleaned if cls._field_kind(cleaned) != "unknown" else None

    @staticmethod
    def _field_kind(key: str) -> str:
        normalized = " ".join(str(key or "").strip().lower().split())
        if any(
            token in normalized
            for token in (
                "model",
                "order code",
                "order number",
                "part no",
                "part number",
                "serial no",
                "serial number",
            )
        ):
            return "identifier"
        if normalized:
            return "specification"
        return "unknown"

    @staticmethod
    def _extract_unit(value: str) -> str | None:
        match = _UNIT_PATTERN.search(value)
        if match is None:
            return None
        return match.group(1)
