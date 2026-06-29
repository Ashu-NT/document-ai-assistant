from __future__ import annotations

import re
from typing import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.structured_answer_context import (
    AnswerKeyValue,
    AnswerSource,
)

_KEY_ALIASES: dict[str, tuple[str, ...]] = {
    "Design Temperature": ("design temperature",),
    "Test pressure": ("test pressure",),
    "Design pressure": ("design pressure",),
    "Working pressure": ("working pressure",),
    "Pressure": ("pressure",),
    "Temperature": ("temperature",),
    "Size": ("size", "nominal size"),
    "Quantity": ("quantity", "qty"),
    "Material": ("material",),
    "Voltage": ("voltage",),
    "Current": ("current",),
    "Power": ("power",),
    "Capacity": ("capacity",),
    "Serial Number": ("serial number",),
    "Part Number": ("part number",),
    "Model": ("model", "model number"),
    "Order code": ("order code", "ordering code", "order number"),
    "DN": ("dn",),
    "Date of inspection": ("date of inspection", "inspection date"),
}
_TABLE_ROW_PATTERN = re.compile(r"^\|(?P<cells>.+)\|$")
_KEY_VALUE_PATTERN = re.compile(
    r"^(?P<key>[A-Za-z][A-Za-z0-9 /().%-]{1,80})\s*[:\-]\s*(?P<value>.+)$"
)
_INLINE_PATTERN = re.compile(
    r"\b(?P<key>"
    r"design temperature|test pressure|design pressure|working pressure|pressure|"
    r"temperature|size|quantity|material|voltage|current|power|capacity|dn|"
    r"serial number|part number|model(?: number)?|order(?:ing)? code|"
    r"date of inspection|inspection date"
    r")\b\s*(?:is|=)?\s*(?P<value>.+)$",
    re.IGNORECASE,
)
_UNIT_PATTERN = re.compile(r"\b(bar|mm|cm|m|kw|w|v|a|hz|dn|pcs|pc|°c|c)\b", re.IGNORECASE)
_SUPPORTED_INTENTS = {
    AnswerIntent.SPECIFICATION_SUMMARY,
    AnswerIntent.CERTIFICATION_SUMMARY,
    AnswerIntent.TABLE_SUMMARY,
    AnswerIntent.IDENTIFIER_LOOKUP,
}


class KeyValueExtractor:
    def extract(
        self,
        sources: Sequence[AnswerSource],
        *,
        answer_intent: AnswerIntent,
    ) -> list[AnswerKeyValue]:
        if answer_intent not in _SUPPORTED_INTENTS:
            return []

        key_values: list[AnswerKeyValue] = []
        seen: set[tuple[int, str, str]] = set()
        for source in sources:
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
                continue

            inline_match = _INLINE_PATTERN.search(stripped)
            if inline_match is not None:
                pairs.append((inline_match.group("key"), inline_match.group("value")))
        return pairs

    @staticmethod
    def _normalize_key(raw_key: str) -> str | None:
        normalized = " ".join(raw_key.lower().split())
        for canonical, aliases in _KEY_ALIASES.items():
            if normalized == canonical.lower():
                return canonical
            if normalized in aliases:
                return canonical
        return None

    @staticmethod
    def _extract_unit(value: str) -> str | None:
        match = _UNIT_PATTERN.search(value)
        if match is None:
            return None
        return match.group(1)
