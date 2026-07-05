from src.application.workflows.linking.semantic_relationship_scorer import (
    ACCEPT_THRESHOLD,
    REVIEW_THRESHOLD,
    resolve_status,
)
from src.domain.extraction import SemanticRelationshipStatus


def test_high_score_is_accepted() -> None:
    assert resolve_status(1.0) == SemanticRelationshipStatus.ACCEPTED
    assert resolve_status(ACCEPT_THRESHOLD) == SemanticRelationshipStatus.ACCEPTED


def test_mid_score_needs_review() -> None:
    midpoint = (ACCEPT_THRESHOLD + REVIEW_THRESHOLD) / 2
    assert resolve_status(midpoint) == SemanticRelationshipStatus.NEEDS_REVIEW
    assert resolve_status(REVIEW_THRESHOLD) == SemanticRelationshipStatus.NEEDS_REVIEW


def test_low_score_is_discarded() -> None:
    assert resolve_status(REVIEW_THRESHOLD - 0.01) is None
    assert resolve_status(0.0) is None
