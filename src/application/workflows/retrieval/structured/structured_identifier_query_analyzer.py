from __future__ import annotations

import re

from src.domain.common import IdentifierType

_IDENTIFIER_INVENTORY_VERBS = (
    "list",
    "show",
    "display",
    "enumerate",
    "provide",
    "give me",
    "find all",
)
_IDENTIFIER_INVENTORY_MARKERS: dict[IdentifierType, tuple[str, ...]] = {
    IdentifierType.PART_NUMBER: ("part number", "part numbers", "part"),
    IdentifierType.SERIAL_NUMBER: ("serial number", "serial numbers", "serial"),
    IdentifierType.MODEL_NUMBER: ("model number", "model numbers", "model"),
    IdentifierType.PRODUCT_NAME: (
        "product name",
        "product names",
        "equipment name",
        "equipment names",
        "system name",
        "system names",
    ),
    IdentifierType.DRAWING_NUMBER: ("drawing number", "drawing numbers", "drawing"),
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
    IdentifierType.MANUFACTURER_NAME: ("manufacturer", "manufacturers"),
    IdentifierType.SUPPLIER_NAME: (
        "supplier",
        "suppliers",
        "vendor",
        "vendors",
        "distributor",
        "distributors",
    ),
    IdentifierType.PHONE_NUMBER: (
        "phone number",
        "phone numbers",
        "telephone number",
        "telephone numbers",
        "phone",
        "telephone",
        "tel",
    ),
    IdentifierType.FAX_NUMBER: ("fax number", "fax numbers", "fax"),
    IdentifierType.EMAIL_ADDRESS: (
        "email address",
        "email addresses",
        "email",
        "emails",
    ),
    IdentifierType.URL: (
        "url",
        "urls",
        "website",
        "websites",
        "web address",
        "web addresses",
    ),
}
_IDENTIFIER_VALUE_PATTERN = re.compile(
    r"\b([A-Z]{1,5}\d{1,6}[A-Z0-9-]*|\d{3,}[A-Z0-9-]+)\b",
    re.IGNORECASE,
)


class StructuredIdentifierQueryAnalyzer:
    def looks_like_inventory_query(self, query_text: str | None) -> bool:
        normalized = self._normalized(query_text)
        if not normalized:
            return False
        if _IDENTIFIER_VALUE_PATTERN.search(normalized):
            return False
        if not any(marker in normalized for marker in _IDENTIFIER_INVENTORY_VERBS):
            return False
        return any(
            marker in normalized
            for markers in _IDENTIFIER_INVENTORY_MARKERS.values()
            for marker in markers
        )

    def requested_identifier_types(
        self,
        query_text: str | None,
    ) -> list[IdentifierType]:
        normalized = self._normalized(query_text)
        requested: list[IdentifierType] = []
        for identifier_type, markers in _IDENTIFIER_INVENTORY_MARKERS.items():
            if any(marker in normalized for marker in markers):
                requested.append(identifier_type)
        return requested

    @staticmethod
    def contains_identifier_value(query_text: str | None) -> bool:
        return bool(_IDENTIFIER_VALUE_PATTERN.search(query_text or ""))

    @staticmethod
    def _normalized(query_text: str | None) -> str:
        return " ".join((query_text or "").strip().lower().split())
