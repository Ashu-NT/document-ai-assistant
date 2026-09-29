from dataclasses import dataclass

from src.application.evaluation.classification.classification_review_status import (
    ClassificationReviewStatus,
)
from src.domain.common import DocumentType


@dataclass(slots=True, frozen=True)
class ClassificationExpectationCase:
    """One document's classification golden expectation. Lives in its own
    dedicated fixture family (`TestDoc/fixtures/classification_expectations*.md`)
    - deliberately NOT inside `retrieval_truth_set.md` (retrieval-focused)
    nor the Phase 1 structural-expectations fixtures (parsing-stage-only).

    `ambiguous=True` marks a document whose single expected label is
    genuinely debatable (e.g. a multi-certificate packet, or a report that
    reads like a procedure). Such documents are never removed or silently
    excluded - they are reported in their own section with explicit
    denominators, and excluded from the primary accuracy/confusion-matrix
    denominator so a debatable label can never masquerade as a clean-cut
    accuracy failure or success.
    """

    document_alias: str
    expected_document_type: DocumentType
    ambiguous: bool = False
    review_status: ClassificationReviewStatus = ClassificationReviewStatus.CANDIDATE
    notes: str | None = None

    @property
    def is_reviewed(self) -> bool:
        return self.review_status == ClassificationReviewStatus.REVIEWED


__all__ = ["ClassificationExpectationCase"]
