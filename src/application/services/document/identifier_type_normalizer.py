from __future__ import annotations

import re

from src.domain.common.enums import IdentifierType

_NORMALIZED_TYPE_ALIASES: dict[str, IdentifierType] = {
    "partnumber": IdentifierType.PART_NUMBER,
    "partno": IdentifierType.PART_NUMBER,
    "partnum": IdentifierType.PART_NUMBER,
    "sparepartnumber": IdentifierType.PART_NUMBER,
    "sparepartno": IdentifierType.PART_NUMBER,
    "serialnumber": IdentifierType.SERIAL_NUMBER,
    "serialno": IdentifierType.SERIAL_NUMBER,
    "serialnum": IdentifierType.SERIAL_NUMBER,
    "serial": IdentifierType.SERIAL_NUMBER,
    "sn": IdentifierType.SERIAL_NUMBER,
    "modelnumber": IdentifierType.MODEL_NUMBER,
    "modelno": IdentifierType.MODEL_NUMBER,
    "modelnum": IdentifierType.MODEL_NUMBER,
    "model": IdentifierType.MODEL_NUMBER,
    "drawingnumber": IdentifierType.DRAWING_NUMBER,
    "drawingno": IdentifierType.DRAWING_NUMBER,
    "drawingnum": IdentifierType.DRAWING_NUMBER,
    "drawing": IdentifierType.DRAWING_NUMBER,
    "dwgnumber": IdentifierType.DRAWING_NUMBER,
    "dwgno": IdentifierType.DRAWING_NUMBER,
    "drgnumber": IdentifierType.DRAWING_NUMBER,
    "drgno": IdentifierType.DRAWING_NUMBER,
    "componentcode": IdentifierType.COMPONENT_CODE,
    "componentnumber": IdentifierType.COMPONENT_CODE,
    "componentno": IdentifierType.COMPONENT_CODE,
    "ordercode": IdentifierType.COMPONENT_CODE,
    "ordernumber": IdentifierType.COMPONENT_CODE,
    "orderno": IdentifierType.COMPONENT_CODE,
    "itemnumber": IdentifierType.COMPONENT_CODE,
    "itemno": IdentifierType.COMPONENT_CODE,
    "itemcode": IdentifierType.COMPONENT_CODE,
    "tagnumber": IdentifierType.COMPONENT_CODE,
    "tagno": IdentifierType.COMPONENT_CODE,
    "tagcode": IdentifierType.COMPONENT_CODE,
    "certificatenumber": IdentifierType.CERTIFICATE_NUMBER,
    "certificateno": IdentifierType.CERTIFICATE_NUMBER,
    "certnumber": IdentifierType.CERTIFICATE_NUMBER,
    "certno": IdentifierType.CERTIFICATE_NUMBER,
    "certificate": IdentifierType.CERTIFICATE_NUMBER,
    "manufacturername": IdentifierType.MANUFACTURER_NAME,
    "manufacturer": IdentifierType.MANUFACTURER_NAME,
    "maker": IdentifierType.MANUFACTURER_NAME,
    "oem": IdentifierType.MANUFACTURER_NAME,
    "suppliername": IdentifierType.SUPPLIER_NAME,
    "supplier": IdentifierType.SUPPLIER_NAME,
    "vendor": IdentifierType.SUPPLIER_NAME,
    "distributor": IdentifierType.SUPPLIER_NAME,
    "phonenumber": IdentifierType.PHONE_NUMBER,
    "phone": IdentifierType.PHONE_NUMBER,
    "telephone": IdentifierType.PHONE_NUMBER,
    "telephonenumber": IdentifierType.PHONE_NUMBER,
    "tel": IdentifierType.PHONE_NUMBER,
    "faxnumber": IdentifierType.FAX_NUMBER,
    "fax": IdentifierType.FAX_NUMBER,
    "emailaddress": IdentifierType.EMAIL_ADDRESS,
    "email": IdentifierType.EMAIL_ADDRESS,
    "url": IdentifierType.URL,
    "website": IdentifierType.URL,
    "webaddress": IdentifierType.URL,
    "unknown": IdentifierType.UNKNOWN,
}

_IGNORED_NORMALIZED_TYPE_LABELS: frozenset[str] = frozenset(
    {
        "chunkid",
        "sourcechunkid",
        "documentid",
        "docid",
        "parametervalue",
        "menuname",
        "menu",
        "chapter",
        "chapternumber",
        "displaymessage",
        "messagedisplayedinformationmenu",
    }
)


class IdentifierTypeNormalizer:
    def normalize(self, value: str | None) -> IdentifierType | None:
        if value is None:
            return None

        stripped = value.strip()
        if not stripped:
            return None

        try:
            return IdentifierType(stripped.lower())
        except ValueError:
            normalized = self._normalize_label(stripped)
            return _NORMALIZED_TYPE_ALIASES.get(normalized)

    def should_ignore(self, value: str | None) -> bool:
        if value is None:
            return False

        stripped = value.strip()
        if not stripped:
            return False

        return self._normalize_label(stripped) in _IGNORED_NORMALIZED_TYPE_LABELS

    @staticmethod
    def _normalize_label(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.strip().lower())
