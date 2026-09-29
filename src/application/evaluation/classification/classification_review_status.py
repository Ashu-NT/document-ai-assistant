from enum import StrEnum


class ClassificationReviewStatus(StrEnum):
    """Whether a human has actually confirmed a golden classification
    label, or whether it is only a migrated candidate.

    The Phase 1 golden corpus manifest's `expected_document_type` values
    were reused verbatim from `retrieval_truth_set.md`'s human-authored
    "Expected Type" column - never independently verified by a real
    classifier run (see
    outputs/architecture/phase2_classification_extraction_evaluation_investigation.md
    section 5). Every classification expectation fixture entry MUST start
    life as CANDIDATE; only a human explicitly marking `review_status:
    reviewed` in the fixture promotes it. Authoritative accuracy/confusion
    metrics only ever count REVIEWED entries - zero reviewed labels is an
    acceptable, honest outcome, never silently promoted to look otherwise.
    """

    CANDIDATE = "candidate"
    REVIEWED = "reviewed"


__all__ = ["ClassificationReviewStatus"]
