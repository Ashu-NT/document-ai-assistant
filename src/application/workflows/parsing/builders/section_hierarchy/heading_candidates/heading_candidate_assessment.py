from dataclasses import dataclass, field

from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates.heading_candidate_role import (
    HeadingCandidateRole,
)


@dataclass(slots=True, frozen=True)
class HeadingCandidateAssessment:
    role: HeadingCandidateRole
    confidence: float
    scores: dict[HeadingCandidateRole, float] = field(default_factory=dict)
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "role": self.role.value,
            "confidence": self.confidence,
            "scores": {role.value: score for role, score in self.scores.items()},
            "reasons": list(self.reasons),
        }
