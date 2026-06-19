from dataclasses import dataclass, field

from src.application.validation.common.validation_issue import ValidationIssue
from src.shared.exceptions import SchemaValidationError


@dataclass(slots=True)
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.issues

    def add_issue(
        self,
        field: str,
        message: str,
        code: str | None = None,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                field=field,
                message=message,
                code=code,
            )
        )

    def raise_if_invalid(self) -> None:
        if self.is_valid:
            return

        raise SchemaValidationError(
            "Validation failed.",
            details={
                "issues": [
                    {
                        "field": issue.field,
                        "message": issue.message,
                        "code": issue.code,
                    }
                    for issue in self.issues
                ]
            },
        )