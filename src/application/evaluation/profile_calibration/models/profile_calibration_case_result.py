from dataclasses import dataclass, field

from src.application.evaluation.profile_calibration.models.profile_evidence_diagnostics import (
    ProfileEvidenceDiagnostics,
)
from src.application.evaluation.profile_calibration.models.profile_scoring_snapshot import (
    ProfileScoringSnapshot,
)


@dataclass(frozen=True, slots=True)
class ProfileCalibrationCaseResult:
    """One labeled document run through both the production (old) evidence
    formula and the candidate (new, ratio-based) one, under the SAME
    unmodified StructuralProfileDecisionPolicy -- so any divergence in
    outcome traces only to the evidence formula, not a second unvalidated
    change.

    Identity is `document_hash` (a stable content hash), not
    `document_label` -- see ProfileCalibrationReportStore.upsert. The label
    is display metadata a human can freely rename without losing history or
    accidentally colliding with an unrelated document that happens to reuse
    the same label text.
    """

    document_label: str
    document_hash: str
    expected_profile: str
    section_count: int
    old: ProfileScoringSnapshot
    new: ProfileScoringSnapshot
    evidence_diagnostics: dict[str, ProfileEvidenceDiagnostics] = field(
        default_factory=dict
    )

    @property
    def old_correct(self) -> bool:
        return self.old.selected_profile == self.expected_profile

    @property
    def new_correct(self) -> bool:
        return self.new.selected_profile == self.expected_profile

    def to_dict(self) -> dict:
        return {
            "document_label": self.document_label,
            "document_hash": self.document_hash,
            "expected_profile": self.expected_profile,
            "section_count": self.section_count,
            "evidence_diagnostics": {
                profile: {
                    "total_occurrences": diag.total_occurrences,
                    "distinct_term_count": diag.distinct_term_count,
                    "matching_title_count": diag.matching_title_count,
                }
                for profile, diag in self.evidence_diagnostics.items()
            },
            "old": {
                "scores": self.old.scores,
                "selected_profile": self.old.selected_profile,
                "second_profile": self.old.second_profile,
                "confidence": self.old.confidence,
                "top_score": self.old.top_score,
                "second_score": self.old.second_score,
                "gap": self.old.gap,
                "is_default": self.old.is_default,
            },
            "new": {
                "scores": self.new.scores,
                "selected_profile": self.new.selected_profile,
                "second_profile": self.new.second_profile,
                "confidence": self.new.confidence,
                "top_score": self.new.top_score,
                "second_score": self.new.second_score,
                "gap": self.new.gap,
                "is_default": self.new.is_default,
            },
            # Derived, not source-of-truth -- recomputed from the fields
            # above on load. Included directly so a human or a downstream
            # analysis script reading the JSON doesn't have to reconstruct
            # the dataclass just to see them.
            "old_correct": self.old.selected_profile == self.expected_profile,
            "new_correct": self.new.selected_profile == self.expected_profile,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProfileCalibrationCaseResult":
        return cls(
            document_label=data["document_label"],
            document_hash=data["document_hash"],
            expected_profile=data["expected_profile"],
            section_count=data["section_count"],
            evidence_diagnostics={
                profile: ProfileEvidenceDiagnostics(**diag)
                for profile, diag in data.get("evidence_diagnostics", {}).items()
            },
            old=ProfileScoringSnapshot(**data["old"]),
            new=ProfileScoringSnapshot(**data["new"]),
        )
