from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)


@dataclass(slots=True, frozen=True)
class ProfileScores:
    """Per-ChunkingProfile score totals and their reasons, produced by
    ProfileScoreAggregator running each ProfileEvidenceScorer over
    StructuralDocumentFeatures. ChunkingProfile.DEFAULT is not scored here --
    see StructuralProfileDecisionPolicy, which decides DEFAULT's score from
    how decisive (or not) these other profiles' scores are."""

    scores: dict[ChunkingProfile, float]
    reasons: dict[ChunkingProfile, list[str]]

    def score_for(self, profile: ChunkingProfile) -> float:
        return self.scores.get(profile, 0.0)

    def with_profile(
        self,
        profile: ChunkingProfile,
        *,
        score: float,
        reasons: list[str],
    ) -> "ProfileScores":
        return ProfileScores(
            scores={**self.scores, profile: score},
            reasons={**self.reasons, profile: reasons},
        )
