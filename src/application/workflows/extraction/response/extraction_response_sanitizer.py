from __future__ import annotations

import re
from typing import Any

from src.application.workflows.extraction.response.extraction_payload_contracts import (
    EXTRACTION_PAYLOAD_CONTRACTS,
    ExtractionPayloadContract,
)

KEY_PATTERN = re.compile(r"[^a-z0-9]+")
NULL_LIKE_TEXT_VALUES = {
    "",
    "null",
    "none",
    "n/a",
    "na",
    "not available",
    "not applicable",
    "-",
    "--",
}


class ExtractionResponseSanitizer:
    def sanitize(self, payload: dict[str, Any]) -> dict[str, Any]:
        sanitized = dict(payload)
        for field_name, contract in EXTRACTION_PAYLOAD_CONTRACTS.items():
            sanitized[field_name] = self._filter_items(
                payload.get(field_name, []),
                contract=contract,
            )
        return sanitized

    def _filter_items(
        self,
        items: list[dict[str, Any]],
        *,
        contract: ExtractionPayloadContract,
    ) -> list[dict[str, Any]]:
        kept: list[dict[str, Any]] = []
        for item in items:
            if not self._has_meaningful_content(item, contract.content_keys):
                continue
            if not self._has_required_fields(item, contract.required_field_groups):
                continue
            kept.append(item)
        return kept

    def _has_meaningful_content(
        self,
        payload: dict[str, Any],
        content_keys: tuple[str, ...],
    ) -> bool:
        return any(self._optional_text(payload, key) for key in content_keys)

    def _has_required_fields(
        self,
        payload: dict[str, Any],
        required_field_groups: tuple[tuple[str, ...], ...],
    ) -> bool:
        if not required_field_groups:
            return True
        return all(
            self._optional_text(payload, *field_group)
            for field_group in required_field_groups
        )

    @staticmethod
    def _pick(payload: dict[str, Any], *keys: str) -> Any:
        normalized_payload = {
            KEY_PATTERN.sub("_", key.lower()).strip("_"): value
            for key, value in payload.items()
        }
        for key in keys:
            normalized_key = KEY_PATTERN.sub("_", key.lower()).strip("_")
            if normalized_key in normalized_payload:
                return normalized_payload[normalized_key]
        return None

    @classmethod
    def _optional_text(cls, payload: dict[str, Any], *keys: str) -> str | None:
        value = cls._pick(payload, *keys)
        if value is None:
            return None

        if isinstance(value, list):
            return " ".join(str(item).strip() for item in value if str(item).strip()) or None

        text = " ".join(str(value).strip().strip('"').strip("'").split())
        text = text.rstrip(" .;:")
        if text.lower() in NULL_LIKE_TEXT_VALUES:
            return None
        return text or None
