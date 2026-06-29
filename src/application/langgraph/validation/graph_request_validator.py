from __future__ import annotations

import re
from typing import Any

from src.application.validation.common import ValidationResult, Validator

_SAFE_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


class GraphRequestValidator(Validator[dict[str, Any]]):
    def validate(self, value: dict[str, Any]) -> ValidationResult:
        result = ValidationResult()

        user_input = value.get("user_input")
        if not isinstance(user_input, str) or not user_input.strip():
            result.add_issue(
                "user_input",
                "user_input cannot be empty.",
                "langgraph.user_input.required",
            )

        top_k = value.get("top_k")
        if top_k is not None:
            if not isinstance(top_k, int):
                result.add_issue(
                    "top_k",
                    "top_k must be an integer when provided.",
                    "langgraph.top_k.invalid_type",
                )
            elif top_k <= 0:
                result.add_issue(
                    "top_k",
                    "top_k must be greater than zero.",
                    "langgraph.top_k.invalid_value",
                )

        document_id = value.get("document_id")
        if document_id is not None and not isinstance(document_id, str):
            result.add_issue(
                "document_id",
                "document_id must be a string when provided.",
                "langgraph.document_id.invalid_type",
            )

        session_id = value.get("session_id")
        if session_id is not None:
            if not isinstance(session_id, str):
                result.add_issue(
                    "session_id",
                    "session_id must be a string when provided.",
                    "langgraph.session_id.invalid_type",
                )
            elif not _SAFE_SESSION_ID_RE.fullmatch(session_id):
                result.add_issue(
                    "session_id",
                    "session_id may only contain letters, digits, underscore, dash, or dot.",
                    "langgraph.session_id.invalid_value",
                )

        for field_name in ("allow_answer_generation", "include_context"):
            raw_value = value.get(field_name)
            if not isinstance(raw_value, bool):
                result.add_issue(
                    field_name,
                    f"{field_name} must be a boolean.",
                    f"langgraph.{field_name}.invalid_type",
                )

        return result
