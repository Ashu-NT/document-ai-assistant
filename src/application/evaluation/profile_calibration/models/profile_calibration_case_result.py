from dataclasses import dataclass

from src.application.evaluation.profile_calibration.models.profile_scoring_snapshot import (
    ProfileScoringSnapshot,
)


@dataclass(frozen=True, slots=True)
class ProfileCalibrationCaseResult:
    """One labeled document run through both the production (old) evidence
    formula and the candidate (new, ratio-based) one, under the SAME
    unmodified StructuralProfileDecisionPolicy -- so any divergence in
    outcome traces only to the evidence formula, not a second unvalidated
    change."""

    document_label: str
    expected_profile: str
    old: ProfileScoringSnapshot
    new: ProfileScoringSnapshot

    @property
    def old_correct(self) -> bool:
        return self.old.selected_profile == self.expected_profile

    @property
    def new_correct(self) -> bool:
        return self.new.selected_profile == self.expected_profile

    def to_dict(self) -> dict:
        return {
            "document_label": self.document_label,
            "expected_profile": self.expected_profile,
            "old": {
                "scores": self.old.scores,
                "selected_profile": self.old.selected_profile,
                "confidence": self.old.confidence,
                "top_score": self.old.top_score,
                "second_score": self.old.second_score,
                "gap": self.old.gap,
                "is_default": self.old.is_default,
            },
            "new": {
                "scores": self.new.scores,
                "selected_profile": self.new.selected_profile,
                "confidence": self.new.confidence,
                "top_score": self.new.top_score,
                "second_score": self.new.second_score,
                "gap": self.new.gap,
                "is_default": self.new.is_default,
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProfileCalibrationCaseResult":
        return cls(
            document_label=data["document_label"],
            expected_profile=data["expected_profile"],
            old=ProfileScoringSnapshot(**data["old"]),
            new=ProfileScoringSnapshot(**data["new"]),
        )
