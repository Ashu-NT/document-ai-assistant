from enum import StrEnum


class ExtractionReviewStatus(StrEnum):
    """Mirrors `ClassificationReviewStatus` exactly (Phase 2A convention).
    Every expectation/declaration authored by an LLM/Claude starts as
    CANDIDATE and is never auto-promoted. Only REVIEWED entries contribute
    to authoritative metrics."""

    CANDIDATE = "candidate"
    REVIEWED = "reviewed"
