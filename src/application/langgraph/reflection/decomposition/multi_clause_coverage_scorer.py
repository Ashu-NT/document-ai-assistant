from __future__ import annotations

from dataclasses import dataclass

from src.application.langgraph.reflection.decomposition.question_clauses import (
    QuestionClauses,
)

_MIN_TERM_LENGTH = 3


@dataclass(slots=True, frozen=True)
class ClauseCoverage:
    clause: str
    is_covered: bool


@dataclass(slots=True, frozen=True)
class MultiClauseCoverageResult:
    clauses: tuple[ClauseCoverage, ...]

    @property
    def is_fully_covered(self) -> bool:
        return all(clause.is_covered for clause in self.clauses)

    @property
    def uncovered_clauses(self) -> tuple[str, ...]:
        return tuple(clause.clause for clause in self.clauses if not clause.is_covered)


class MultiClauseCoverageScorer:
    """Checks whether an answer addresses each clause of a multi-clause
    question -- the same generic term-overlap approach
    `AnswerQualityScorer.score()` already uses for the whole question
    (shared tokens longer than 3 characters), applied per-clause instead."""

    def score(
        self, *, clauses: QuestionClauses, answer_text: str
    ) -> MultiClauseCoverageResult:
        answer_terms = set((answer_text or "").lower().split())
        coverages = tuple(
            ClauseCoverage(
                clause=clause,
                is_covered=self._is_clause_covered(clause, answer_terms),
            )
            for clause in clauses.clauses
        )
        return MultiClauseCoverageResult(clauses=coverages)

    @staticmethod
    def _is_clause_covered(clause: str, answer_terms: set[str]) -> bool:
        clause_terms = {
            token for token in clause.lower().split() if len(token) > _MIN_TERM_LENGTH
        }
        if not clause_terms:
            return True
        return bool(clause_terms & answer_terms)
