from __future__ import annotations

from typing import Any

from src.application.workflows.common.enum_label_resolver import resolve_enum_value
from src.domain.extraction import ContactPointType, SemanticEntityType

# Contact-point/owner enum resolution, split out of extraction_workflow.py.
# Both resolvers normalize the raw payload value the same way (lower-case,
# strip, collapse spaces/hyphens to underscores) before matching it against
# `resolve_enum_value`'s alias table / allowed-member set -- see that
# function's docstring for the exact resolution order.


def _normalize_enum_label_separators(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


_CONTACT_POINT_TYPE_ALIASES: dict[str, ContactPointType] = {
    "phone": ContactPointType.PHONE_NUMBER,
    "telephone": ContactPointType.PHONE_NUMBER,
    "telephone_number": ContactPointType.PHONE_NUMBER,
    "tel": ContactPointType.PHONE_NUMBER,
    "fax": ContactPointType.FAX_NUMBER,
    "fax_number": ContactPointType.FAX_NUMBER,
    "email": ContactPointType.EMAIL_ADDRESS,
    "email_address": ContactPointType.EMAIL_ADDRESS,
    "e_mail": ContactPointType.EMAIL_ADDRESS,
    "website": ContactPointType.URL,
    "web": ContactPointType.URL,
    "web_address": ContactPointType.URL,
}

_CONTACT_OWNER_ENTITY_TYPES = frozenset(
    {SemanticEntityType.MANUFACTURER, SemanticEntityType.SUPPLIER}
)


def resolve_contact_point_type(value: Any) -> ContactPointType:
    return resolve_enum_value(
        value,
        ContactPointType,
        normalize=_normalize_enum_label_separators,
        aliases=_CONTACT_POINT_TYPE_ALIASES,
        default=ContactPointType.UNKNOWN,
    )


def resolve_contact_owner_type(value: Any) -> SemanticEntityType | None:
    return resolve_enum_value(
        value,
        SemanticEntityType,
        normalize=_normalize_enum_label_separators,
        allowed_members=_CONTACT_OWNER_ENTITY_TYPES,
        default=None,
    )
