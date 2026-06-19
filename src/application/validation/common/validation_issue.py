from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ValidationIssue:
    field: str
    message: str
    code: str | None = None