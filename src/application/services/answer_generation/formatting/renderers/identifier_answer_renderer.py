from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
import re

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
    "Part No": IdentifierType.PART_NUMBER,
    "Part No.": IdentifierType.PART_NUMBER,
    "Part Nr": IdentifierType.PART_NUMBER,
    "Part Nr.": IdentifierType.PART_NUMBER,
    "Serial Number": IdentifierType.SERIAL_NUMBER,
    "Serial No": IdentifierType.SERIAL_NUMBER,
    "Serial No.": IdentifierType.SERIAL_NUMBER,
    "Model": IdentifierType.MODEL_NUMBER,
    "Product Name": IdentifierType.PRODUCT_NAME,
    "Order code": IdentifierType.COMPONENT_CODE,
    "Order Code": IdentifierType.COMPONENT_CODE,
    "Order Number": IdentifierType.COMPONENT_CODE,
    "Phone Number": IdentifierType.PHONE_NUMBER,
    "Fax Number": IdentifierType.FAX_NUMBER,
    "Email": IdentifierType.EMAIL_ADDRESS,
    "Email Address": IdentifierType.EMAIL_ADDRESS,
    "URL": IdentifierType.URL,
    "Website": IdentifierType.URL,
}
_UNIT_LIKE_IDENTIFIER_TOKEN_PATTERN = re.compile(
    r"^\d+(?:vdc|vac|hz|bar|kg|kw|w|v|a|mm|cm|m|l|hr|hrs)$",
    re.IGNORECASE,
)
_CODE_LIKE_TOKEN_PATTERN = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9./_-]{2,}\b")
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
                page_label = page_by_source_number.get(key_value.source_number)
                for value in self._normalized_key_value_values(
                    identifier_type,
                    key_value.value,
                ):
                    fingerprint = (identifier_type, value.lower())
                    if fingerprint in seen:
                        continue
                    seen.add(fingerprint)
                    grouped_values[identifier_type].append((value, page_label))

        for identifier in resolved_identifiers:
            identifier_type = self._normalized_identifier_type(identifier.identifier_type)
            if identifier_type is None:
                continue
            if requested_types and identifier_type not in requested_types:
                continue
            page_label = self._format_page_range(identifier.page_start, identifier.page_end)
            for value in self._normalized_key_value_values(
                identifier_type,
                identifier.raw_value,
            ):
                fingerprint = (identifier_type, value.lower())
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
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
        key = " ".join(str(key_value.key or "").strip().split())
        if not key:
            return None
        if key in _IDENTIFIER_KEY_TO_TYPE:
            return _IDENTIFIER_KEY_TO_TYPE[key]

        normalized = key.lower().replace("nr.", "no.").replace("nr", "no")
        if "part no" in normalized or "part number" in normalized:
            return IdentifierType.PART_NUMBER
        if "serial no" in normalized or "serial number" in normalized:
            return IdentifierType.SERIAL_NUMBER
        if "model" in normalized:
            return IdentifierType.MODEL_NUMBER
        if "product name" in normalized:
            return IdentifierType.PRODUCT_NAME
        if "order code" in normalized or "order number" in normalized:
            return IdentifierType.COMPONENT_CODE
        if "phone" in normalized or "telephone" in normalized or "tel" == normalized:
            return IdentifierType.PHONE_NUMBER
        if "fax" in normalized:
            return IdentifierType.FAX_NUMBER
        if "email" in normalized:
            return IdentifierType.EMAIL_ADDRESS
        if "url" in normalized or "website" in normalized or "web address" in normalized:
            return IdentifierType.URL
        return None

    def _normalized_key_value_values(
        self,
        identifier_type: IdentifierType,
        raw_value: str | None,
    ) -> list[str]:
        cleaned = self._clean_value(raw_value)
        if cleaned is None:
            return []
        if identifier_type not in {
            IdentifierType.PART_NUMBER,
            IdentifierType.SERIAL_NUMBER,
            IdentifierType.MODEL_NUMBER,
            IdentifierType.DRAWING_NUMBER,
            IdentifierType.COMPONENT_CODE,
            IdentifierType.CERTIFICATE_NUMBER,
        }:
            return [cleaned]
        extracted = self._extract_identifier_tokens(cleaned)
        if not extracted:
            return [cleaned]
        if identifier_type == IdentifierType.PART_NUMBER:
            if self._looks_like_revision_suffix_value(cleaned, extracted[0]):
                return [cleaned]
            return [extracted[-1]]
        return [extracted[0]]

    def _extract_identifier_tokens(self, value: str) -> list[str]:
        compact = self._clean_value(value)
        if compact is None:
            return []
        if " " not in compact and not _UNIT_LIKE_IDENTIFIER_TOKEN_PATTERN.match(compact):
            return [compact]

        tokens: list[str] = []
        for match in _CODE_LIKE_TOKEN_PATTERN.finditer(compact):
            token = match.group(0).strip(".,;:()[]")
            if len(token) < 3:
                continue
            if _UNIT_LIKE_IDENTIFIER_TOKEN_PATTERN.match(token):
                continue
            if not any(character.isdigit() for character in token):
                continue
            if token.lower() in {"2/2-way", "g1/2", "g1/4"}:
                continue
            if token not in tokens:
                tokens.append(token)
        return tokens

    @staticmethod
    def _looks_like_revision_suffix_value(value: str, first_token: str) -> bool:
        remainder = value[len(first_token) :].strip()
        if not remainder:
            return False
        normalized = " ".join(remainder.lower().split())
        return normalized.startswith("rev ")

    @staticmethod
    def _requested_identifier_types(question: str) -> set[IdentifierType]:
        normalized_question = " ".join((question or "").strip().lower().split())
        requested: set[IdentifierType] = set()
        for identifier_type, markers in IDENTIFIER_TYPE_MARKERS.items():
            if any(marker in normalized_question for marker in markers):
                requested.add(identifier_type)
        return requested
