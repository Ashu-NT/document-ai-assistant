from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProfileScoringSnapshot:
    """One scoring formula's full result for one document: every profile's
    score (including DEFAULT), the winner, its confidence, and the
    top/second-place score gap that drove the DEFAULT/decisiveness
    decision."""

    scores: dict[str, float]
    selected_profile: str
    confidence: float
    top_score: float
    second_score: float
    gap: float
    is_default: bool
