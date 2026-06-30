from __future__ import annotations

from src.application.validation.common import ValidationResult, Validator


class GuardrailConfigValidator(Validator):
    def validate(self, value) -> ValidationResult:
        result = ValidationResult()
        if value is None:
            result.add_issue(
                "guardrails",
                "Guardrail configuration cannot be None.",
                "guardrails.config.required",
            )
            return result
        return result
