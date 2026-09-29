from dataclasses import dataclass, field
from enum import StrEnum

from src.application.evaluation.extraction.extraction_completeness import (
    ExtractionCompleteness,
)
from src.application.evaluation.extraction.extraction_expectation_case import (
    ExtractionExpectationCase,
)
from src.application.evaluation.extraction.extraction_review_status import (
    ExtractionReviewStatus,
)


class ExtractionMatchOutcome(StrEnum):
    MATCHED = "matched"
    UNMATCHED_EXPECTED = "unmatched_expected"  # a real FN candidate
    UNMATCHED_ACTUAL = "unmatched_actual"  # a real FP candidate (EXHAUSTIVE only)


@dataclass(frozen=True, slots=True)
class ExtractionMatchResult:
    outcome: ExtractionMatchOutcome
    entity_type: str
    # Group-level (document, entity_type, scope) properties - populated for
    # EVERY result, including UNMATCHED_ACTUAL (which has no `expectation`
    # of its own to read them from, but still needs a completeness value
    # to know whether it counts as a real false positive). Derived from the
    # matched group's expectations, which are required to share one
    # completeness/review_status per (document, entity_type, scope) - see
    # match_expectations_against_actuals.
    group_completeness: ExtractionCompleteness = ExtractionCompleteness.PRESENCE_ONLY
    group_review_status: ExtractionReviewStatus = ExtractionReviewStatus.CANDIDATE
    expectation: ExtractionExpectationCase | None = None
    actual_entity_id: str | None = None
    identity_fields_used: tuple[str, ...] = ()
    differing_fields: tuple[str, ...] = ()
    normalized_expected: dict[str, str | None] = field(default_factory=dict)
    normalized_actual: dict[str, str | None] | None = None
    match_reason: str = ""
    # Deterministic - populated instead of silently picking one candidate
    # whenever more than one actual entity is equally plausible.
    ambiguous_actual_entity_ids: tuple[str, ...] = ()
    # Entity-correctness vs evidence-correctness are separate dimensions
    # (see extraction_evidence_matcher.py) - None means "not checked"
    # (e.g. UNMATCHED_EXPECTED has no actual entity to check evidence on).
    evidence_correct: bool | None = None
    evidence_detail: str | None = None


__all__ = ["ExtractionMatchOutcome", "ExtractionMatchResult"]
