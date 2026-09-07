from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class IngestionAssertionResult:
    name: str
    expected: Any
    actual: Any
    passed: bool


@dataclass(slots=True)
class IngestionExpectationCaseResult:
    case_id: str
    assertions: list[IngestionAssertionResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(assertion.passed for assertion in self.assertions)

    @property
    def failed_assertions(self) -> list[IngestionAssertionResult]:
        return [assertion for assertion in self.assertions if not assertion.passed]


__all__ = ["IngestionAssertionResult", "IngestionExpectationCaseResult"]
