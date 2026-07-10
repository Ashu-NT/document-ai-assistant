from __future__ import annotations

from typing import Any

from src.application.workflows.extraction.response.extraction_payload_contracts import (
    EXTRACTION_PAYLOAD_CONTRACTS,
    ExtractionPayloadContract,
)
from src.application.workflows.extraction.response.extraction_payload_field_picker import (
    optional_payload_text,
    pick_payload_value,
)


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
        return pick_payload_value(payload, *keys)

    @classmethod
    def _optional_text(cls, payload: dict[str, Any], *keys: str) -> str | None:
        return optional_payload_text(payload, *keys)
