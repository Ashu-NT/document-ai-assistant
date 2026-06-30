from __future__ import annotations

import json
from typing import Any

from src.shared.exceptions import SchemaValidationError


class ResearchJsonParser:
    def parse_object(self, payload: str, *, message_prefix: str) -> dict[str, Any]:
        normalized = self._strip_code_fences(payload)
        try:
            data = json.loads(normalized)
        except json.JSONDecodeError as exc:
            raise SchemaValidationError(
                f"Malformed {message_prefix} JSON.",
                details={"error": str(exc)},
            ) from exc
        if not isinstance(data, dict):
            raise SchemaValidationError(
                f"{message_prefix.capitalize()} must be a JSON object.",
                details={"payload_type": type(data).__name__},
            )
        return data

    @staticmethod
    def _strip_code_fences(payload: str) -> str:
        stripped = (payload or "").strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 2:
                stripped = "\n".join(lines[1:-1]).strip()
        return stripped
