from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context import (
    AnswerKeyValue,
    StructuredAnswerContext,
)
from src.application.workflows.shared.identifier_type_markers import (
    IDENTIFIER_TYPE_MARKERS,
)
from src.domain.common import IdentifierType
from src.domain.document.entities.identifier import Identifier

_IDENTIFIER_TYPE_LABELS: dict[IdentifierType, str] = {
    IdentifierType.PART_NUMBER: "Part Numbers",
    IdentifierType.SERIAL_NUMBER: "Serial Numbers",
    IdentifierType.MODEL_NUMBER: "Model Numbers",
    IdentifierType.PRODUCT_NAME: "Product Names",
    IdentifierType.DRAWING_NUMBER: "Drawing Numbers",
    IdentifierType.COMPONENT_CODE: "Order / Component Codes",
    IdentifierType.CERTIFICATE_NUMBER: "Certificate Numbers",
    IdentifierType.MANUFACTURER_NAME: "Manufacturers",
    IdentifierType.SUPPLIER_NAME: "Suppliers",
    IdentifierType.PHONE_NUMBER: "Phone Numbers",
    IdentifierType.FAX_NUMBER: "Fax Numbers",
    IdentifierType.EMAIL_ADDRESS: "Email Addresses",
    IdentifierType.URL: "Web Addresses",
}
_IDENTIFIER_KEY_TO_TYPE: dict[str, IdentifierType] = {
    "Part Number": IdentifierType.PART_NUMBER,
    "Serial Number": IdentifierType.SERIAL_NUMBER,
    "Model": IdentifierType.MODEL_NUMBER,
    "Product Name": IdentifierType.PRODUCT_NAME,
    "Order code": IdentifierType.COMPONENT_CODE,
    "Phone Number": IdentifierType.PHONE_NUMBER,
    "Fax Number": IdentifierType.FAX_NUMBER,
    "Email": IdentifierType.EMAIL_ADDRESS,
    "Email Address": IdentifierType.EMAIL_ADDRESS,
    "URL": IdentifierType.URL,
    "Website": IdentifierType.URL,
}
_TYPE_ORDER: tuple[IdentifierType, ...] = (
    IdentifierType.PART_NUMBER,
    IdentifierType.SERIAL_NUMBER,
    IdentifierType.MODEL_NUMBER,
    IdentifierType.PRODUCT_NAME,
    IdentifierType.COMPONENT_CODE,
    IdentifierType.DRAWING_NUMBER,
    IdentifierType.CERTIFICATE_NUMBER,
    IdentifierType.MANUFACTURER_NAME,
    IdentifierType.SUPPLIER_NAME,
    IdentifierType.PHONE_NUMBER,
    IdentifierType.FAX_NUMBER,
    IdentifierType.EMAIL_ADDRESS,
    IdentifierType.URL,
)


class IdentifierAnswerRenderer:
    """Prefers the typed `StructuredAnswerContext.key_values` (populated via
    `StructuredFactKeyValueBuilder.build_from_identifiers()`, the same
    typed-context model the rest of this pipeline is built on) as the
    primary source. Only falls back to the raw `resolved_identifiers`
    domain objects for identifiers not already covered by
    `structured_context` -- this is the same "prefer the richer typed
    model, fall back only for resilience" shape `SparePartsListRenderer`
    already uses (plan section 4.7/9.5). The fallback still matters: when
    no `document_lookup_service` is configured, an identifier's source
    chunk is never fetched, so it never reaches `key_values` at all (the
    same degraded-mode gap Phase 4 already accepted for
    `structured_entities`) -- without this fallback, that identifier would
    silently disappear from the deterministic answer instead of only
    losing its typed representation.
    """

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
        grouped_values: dict[IdentifierType, list[tuple[str, str | None]]] = defaultdict(list)
        seen: set[tuple[IdentifierType, str]] = set()

        if structured_context is not None:
            page_by_source_number = {
                source.source_number: self._format_page_range(source.page_start, source.page_end)
                for source in structured_context.sources
            }
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
                page_label = page_by_source_number.get(key_value.source_number)
                grouped_values[identifier_type].append((value, page_label))

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
            page_label = self._format_page_range(identifier.page_start, identifier.page_end)
            grouped_values[identifier_type].append((value, page_label))

        if not grouped_values:
            return None

        total_count = sum(len(values) for values in grouped_values.values())
        lines = [f"Requested identifiers ({total_count} found)", ""]
        ordered_types = [
            identifier_type
            for identifier_type in _TYPE_ORDER
            if grouped_values.get(identifier_type)
        ]
        for index, identifier_type in enumerate(ordered_types):
            label = _IDENTIFIER_TYPE_LABELS[identifier_type]
            lines.append(f"{label}:")
            for value, page_label in grouped_values[identifier_type]:
                suffix = f" ({page_label})" if page_label else ""
                lines.append(f"- {value}{suffix}")
            if index < len(ordered_types) - 1:
                lines.append("")
        return "\n".join(lines).strip()

    @staticmethod
    def _format_page_range(page_start: int | None, page_end: int | None) -> str | None:
        if page_start is None:
            return None
        if page_end is None or page_end == page_start:
            return f"p.{page_start}"
        return f"pp.{page_start}-{page_end}"

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
        for identifier_type, markers in IDENTIFIER_TYPE_MARKERS.items():
            if any(marker in normalized_question for marker in markers):
                requested.add(identifier_type)
        return requested
