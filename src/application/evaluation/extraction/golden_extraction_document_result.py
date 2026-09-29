from dataclasses import dataclass, field
from enum import StrEnum

from src.application.evaluation.extraction.extraction_evaluation_scope import (
    ExtractionEvaluationScope,
)
from src.application.evaluation.extraction.extraction_expectation_case import (
    ExtractionApplicabilityDeclaration,
)
from src.application.evaluation.extraction.matchers.extraction_match_result import (
    ExtractionMatchResult,
)


class ExtractionStageStatus(StrEnum):
    """Mirrors `ClassificationStageStatus`'s shape, scoped to one
    (document, scope) extraction execution."""

    EVALUATED = "evaluated"
    EXECUTION_FAILED = "execution_failed"
    SKIPPED_PARSING_UNAVAILABLE = "skipped_parsing_unavailable"
    NO_EXPECTATIONS = "no_expectations"


@dataclass(slots=True)
class ExtractionBatchSummary:
    """Raw-attempt vs accepted-output observability (task section 12) -
    everything the real production workflow actually exposes today.
    Sanitizer-level pre-build drops are NOT observable without a
    production change (see extraction_isolation.py's module docstring and
    the Phase 2B final report) - not fabricated here."""

    batch_count: int
    parse_success_count: int
    parse_failure_count: int
    dropped_empty_count: int
    invalid_source_chunk_id_event_count: int


@dataclass(slots=True)
class ExtractionScopeRunOutcome:
    document_alias: str
    scope: ExtractionEvaluationScope
    stage_status: ExtractionStageStatus
    execution_error: str | None = None
    batch_summary: ExtractionBatchSummary | None = None
    match_results: list[ExtractionMatchResult] = field(default_factory=list)
    applicability_declarations: list[ExtractionApplicabilityDeclaration] = field(
        default_factory=list
    )

    @property
    def was_evaluated(self) -> bool:
        return self.stage_status is ExtractionStageStatus.EVALUATED


@dataclass(slots=True)
class GoldenExtractionDocumentResult:
    alias: str
    scope_outcomes: list[ExtractionScopeRunOutcome] = field(default_factory=list)

    @property
    def was_evaluated(self) -> bool:
        return any(outcome.was_evaluated for outcome in self.scope_outcomes)

    @property
    def has_execution_failures(self) -> bool:
        return any(
            outcome.stage_status is ExtractionStageStatus.EXECUTION_FAILED
            for outcome in self.scope_outcomes
        )


__all__ = [
    "ExtractionStageStatus",
    "ExtractionBatchSummary",
    "ExtractionScopeRunOutcome",
    "GoldenExtractionDocumentResult",
]
