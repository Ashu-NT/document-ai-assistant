from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class QuestionClauses:
    """A question split into independent clauses, each expected to be
    separately answerable/coverable. A single-clause result (the common
    case) always contains the original question, unmodified."""

    clauses: tuple[str, ...]

    @property
    def has_multiple_clauses(self) -> bool:
        return len(self.clauses) > 1
