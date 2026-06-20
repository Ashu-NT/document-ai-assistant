from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics import (
    ChunkingProfileStatistics,
)


@dataclass(slots=True, frozen=True)
class ChunkingProfileInference:
    selected_profile: ChunkingProfile
    confidence: float
    scores: dict[ChunkingProfile, float]
    reasons: dict[ChunkingProfile, list[str]]
    statistics: ChunkingProfileStatistics

    @property
    def selected_reasons(self) -> list[str]:
        return list(self.reasons.get(self.selected_profile, []))

    @property
    def score_gap(self) -> float:
        ordered_scores = sorted(self.scores.values(), reverse=True)
        if len(ordered_scores) < 2:
            return ordered_scores[0] if ordered_scores else 0.0
        return ordered_scores[0] - ordered_scores[1]

    def scores_by_name(self) -> dict[str, float]:
        return {
            profile.value: round(score, 3)
            for profile, score in self.scores.items()
        }

    def reasons_by_name(self) -> dict[str, list[str]]:
        return {
            profile.value: list(profile_reasons)
            for profile, profile_reasons in self.reasons.items()
        }
