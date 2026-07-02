from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.structured_answer_context import (
    AnswerKeyValue,
    StructuredAnswerContext,
)
from src.domain.common import IdentifierType
from src.domain.document.entities.identifier import Identifier

_IDENTIFIER_TYPE_LABELS: dict[IdentifierType, str] = {
    IdentifierType.PART_NUMBER: "Part Numbers",
    IdentifierType.SERIAL_NUMBER: "Serial Numbers",
    IdentifierType.MODEL_NUMBER: "Model Numbers",
    IdentifierType.DRAWING_NUMBER: "Drawing Numbers",
    IdentifierType.COMPONENT_CODE: "Order / Component Codes",
    IdentifierType.CERTIFICATE_NUMBER: "Certificate Numbers",
    IdentifierType.MANUFACTURER_NAME: "Manufacturers / Suppliers",
}
_IDENTIFIER_KEY_TO_TYPE: dict[str, IdentifierType] = {
    "Part Number": IdentifierType.PART_NUMBER,
    "Serial Number": IdentifierType.SERIAL_NUMBER,
    "Model": IdentifierType.MODEL_NUMBER,
    "Order code": IdentifierType.COMPONENT_CODE,
}
_QUESTION_TYPE_MARKERS: dict[IdentifierType, tuple[str, ...]] = {
    IdentifierType.PART_NUMBER: ("part number", "part numbers", "part no", "part"),
    IdentifierType.SERIAL_NUMBER: (
        "serial number",
        "serial numbers",
        "serial no",
        "serial",
    ),
    IdentifierType.MODEL_NUMBER: ("model number", "model numbers", "model"),
    IdentifierType.DRAWING_NUMBER: (
        "drawing number",
        "drawing numbers",
        "drawing",
    ),
    IdentifierType.COMPONENT_CODE: (
        "order code",
        "order codes",
        "order number",
        "order numbers",
        "component code",
        "component codes",
        "tag",
        "tags",
    ),
    IdentifierType.CERTIFICATE_NUMBER: (
        "certificate number",
        "certificate numbers",
        "certificate",
        "approval number",
        "approval numbers",
    ),
    IdentifierType.MANUFACTURER_NAME: (
        "manufacturer",
        "manufacturers",
        "supplier",
        "suppliers",
    ),
}
_TYPE_ORDER: tuple[IdentifierType, ...] = (
    IdentifierType.PART_NUMBER,
    IdentifierType.SERIAL_NUMBER,
    IdentifierType.MODEL_NUMBER,
    IdentifierType.COMPONENT_CODE,
    IdentifierType.DRAWING_NUMBER,
    IdentifierType.CERTIFICATE_NUMBER,
    IdentifierType.MANUFACTURER_NAME,
)


class IdentifierAnswerRenderer:
    def render(
        self,
        *,
        question: str,
        answer_intent: AnswerIntent | None,
        structured_context: StructuredAnswerContext | None,
        resolved_identifiers: Sequence[Identifier],
    ) -> str | None:
        if answer_intent != AnswerIntent.IDENTIFIER_LOOKUP:
            return None

        requested_types = self._requested_identifier_types(question)
        grouped_values: dict[IdentifierType, list[str]] = defaultdict(list)
        seen: set[tuple[IdentifierType, str]] = set()

        for identifier in resolved_identifiers:
            identifier_type = self._normalized_identifier_type(identifier.identifier_type)
            if identifier_type is None:
                continue
            if requested_types and identifier_type not in requested_types:
                continue
            value = self._clean_value(identifier.raw_value)
            if value is None:
                continue
            fingerprint = (identifier_type, value.lower())
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            grouped_values[identifier_type].append(value)

        if structured_context is not None:
            for key_value in structured_context.key_values:
                identifier_type = self._identifier_type_from_key_value(key_value)
                if identifier_type is None:
                    continue
                if requested_types and identifier_type not in requested_types:
                    continue
                value = self._clean_value(key_value.value)
                if value is None:
                    continue
                fingerprint = (identifier_type, value.lower())
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                grouped_values[identifier_type].append(value)

        if not grouped_values:
            return None

        lines = ["Requested identifiers", ""]
        ordered_types = [
            identifier_type
            for identifier_type in _TYPE_ORDER
            if grouped_values.get(identifier_type)
        ]
        for index, identifier_type in enumerate(ordered_types):
            label = _IDENTIFIER_TYPE_LABELS[identifier_type]
            lines.append(f"{label}:")
            for value in grouped_values[identifier_type]:
                lines.append(f"- {value}")
            if index < len(ordered_types) - 1:
                lines.append("")
        return "\n".join(lines).strip()

    @staticmethod
    def _clean_value(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.strip().split())
        return cleaned or None

    @staticmethod
    def _normalized_identifier_type(
        identifier_type: IdentifierType,
    ) -> IdentifierType | None:
        if identifier_type == IdentifierType.UNKNOWN:
            return None
        return identifier_type

    @staticmethod
    def _identifier_type_from_key_value(
        key_value: AnswerKeyValue,
    ) -> IdentifierType | None:
        return _IDENTIFIER_KEY_TO_TYPE.get(key_value.key)

    @staticmethod
    def _requested_identifier_types(question: str) -> set[IdentifierType]:
        normalized_question = " ".join((question or "").strip().lower().split())
        requested: set[IdentifierType] = set()
        for identifier_type, markers in _QUESTION_TYPE_MARKERS.items():
            if any(marker in normalized_question for marker in markers):
                requested.add(identifier_type)
        return requested
