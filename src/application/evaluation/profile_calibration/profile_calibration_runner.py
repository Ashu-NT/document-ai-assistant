from src.application.evaluation.profile_calibration.candidate.candidate_score_aggregator import (
    CandidateScoreAggregator,
)
from src.application.evaluation.profile_calibration.models.profile_calibration_case_result import (
    ProfileCalibrationCaseResult,
)
from src.application.evaluation.profile_calibration.models.profile_scoring_snapshot import (
    ProfileScoringSnapshot,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_decision_policy import (
    StructuralProfileDecisionPolicy,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_inferer import (
    StructuralProfileInferer,
)
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class ProfileCalibrationRunner:
    """Runs one labeled document through both the production evidence
    formula (via the real, unmodified StructuralProfileInferer) and the
    candidate ratio-based one (via CandidateScoreAggregator), deciding both
    through the SAME unmodified StructuralProfileDecisionPolicy -- so any
    outcome divergence between old/new traces only to the evidence formula,
    never to a second, unvalidated change to the decision thresholds.
    Neither production scorer nor decision-policy files are modified by
    this module; both are called read-only.
    """

    def __init__(
        self,
        *,
        profile_inferer: StructuralProfileInferer | None = None,
        candidate_aggregator: CandidateScoreAggregator | None = None,
        decision_policy: StructuralProfileDecisionPolicy | None = None,
    ) -> None:
        self.profile_inferer = profile_inferer or StructuralProfileInferer()
        self.candidate_aggregator = candidate_aggregator or CandidateScoreAggregator()
        self.decision_policy = decision_policy or StructuralProfileDecisionPolicy()

    def run(
        self,
        *,
        document_label: str,
        expected_profile: str,
        document_title: str | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
    ) -> ProfileCalibrationCaseResult:
        old_inference = self.profile_inferer.infer_result(
            document_title=document_title,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        )
        old_snapshot = self._snapshot(
            scores=old_inference.scores,
            selected_profile=old_inference.selected_profile,
            confidence=old_inference.confidence,
        )

        # Reuse the SAME already-extracted features for the candidate run --
        # only the evidence formula varies, never the underlying document
        # measurements, so this is a controlled, single-variable comparison.
        features = old_inference.features
        candidate_scores = self.candidate_aggregator.aggregate(features)
        new_selected_profile, new_confidence, new_final_scores = (
            self.decision_policy.decide(scores=candidate_scores, features=features)
        )
        new_snapshot = self._snapshot(
            scores=new_final_scores.scores,
            selected_profile=new_selected_profile,
            confidence=new_confidence,
        )

        return ProfileCalibrationCaseResult(
            document_label=document_label,
            expected_profile=expected_profile,
            old=old_snapshot,
            new=new_snapshot,
        )

    @staticmethod
    def _snapshot(
        *,
        scores: dict[ChunkingProfile, float],
        selected_profile: ChunkingProfile,
        confidence: float,
    ) -> ProfileScoringSnapshot:
        ordered = sorted(scores.values(), reverse=True)
        top_score = ordered[0] if ordered else 0.0
        second_score = ordered[1] if len(ordered) > 1 else 0.0
        return ProfileScoringSnapshot(
            scores={profile.value: score for profile, score in scores.items()},
            selected_profile=selected_profile.value,
            confidence=confidence,
            top_score=top_score,
            second_score=second_score,
            gap=top_score - second_score,
            is_default=selected_profile == ChunkingProfile.DEFAULT,
        )
