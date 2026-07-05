from src.domain.extraction import SemanticRelationshipStatus

# Threshold-based accept/review/discard classification for a candidate's
# raw evidence score (see `semantic_relationship_candidate_generator` for how
# scores are assigned per window/evidence type). Kept as clearly-named,
# easily-adjustable constants since these are proposed defaults, not
# empirically tuned values.
ACCEPT_THRESHOLD = 0.6
REVIEW_THRESHOLD = 0.3


def resolve_status(score: float) -> SemanticRelationshipStatus | None:
    """Classify a candidate's score into accepted/needs_review, or discard
    it (`None`) when the evidence is too weak to persist at all."""
    if score >= ACCEPT_THRESHOLD:
        return SemanticRelationshipStatus.ACCEPTED
    if score >= REVIEW_THRESHOLD:
        return SemanticRelationshipStatus.NEEDS_REVIEW
    return None
