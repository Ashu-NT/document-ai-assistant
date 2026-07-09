from __future__ import annotations

from src.domain.common import IdentifierType

# Canonical phrase markers used to decide which IdentifierType(s) a piece of
# question/query text refers to (e.g. "what's the part no?" -> PART_NUMBER).
# Previously duplicated independently in
# StructuredIdentifierQueryAnalyzer._IDENTIFIER_INVENTORY_MARKERS and
# IdentifierAnswerRenderer._QUESTION_TYPE_MARKERS, with real drift between
# the two copies (this dict's "part no"/"serial no" short-form aliases were
# only present in the renderer's copy, meaning the same question could be
# recognized as identifier-scoped by the final renderer but not by the
# earlier structured-evidence resolver). This is the union of both.
IDENTIFIER_TYPE_MARKERS: dict[IdentifierType, tuple[str, ...]] = {
    IdentifierType.PART_NUMBER: ("part number", "part numbers", "part no", "part"),
    IdentifierType.SERIAL_NUMBER: (
        "serial number",
        "serial numbers",
        "serial no",
        "serial",
    ),
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
