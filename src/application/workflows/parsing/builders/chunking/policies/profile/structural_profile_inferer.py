from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_feature_extractor import (
    StructuralFeatureExtractor,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.scoring.profile_score_aggregator import (
    ProfileScoreAggregator,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_decision_policy import (
    StructuralProfileDecisionPolicy,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.structural_profile_inference import (
    StructuralProfileInference,
)
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class StructuralProfileInferer:
    """Orchestrates the structural chunking-profile pipeline: extract
    features from the document -> score each profile's evidence -> decide
    the winner (including whether DEFAULT applies) -> assemble the final
    StructuralProfileInference."""

    def __init__(
        self,
        *,
        feature_extractor: StructuralFeatureExtractor | None = None,
        score_aggregator: ProfileScoreAggregator | None = None,
        decision_policy: StructuralProfileDecisionPolicy | None = None,
    ) -> None:
        self.feature_extractor = feature_extractor or StructuralFeatureExtractor()
        self.score_aggregator = score_aggregator or ProfileScoreAggregator()
        self.decision_policy = decision_policy or StructuralProfileDecisionPolicy()

    def infer(
        self,
        *,
        document_title: str | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
    ) -> ChunkingProfile:
        return self.infer_result(
            document_title=document_title,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        ).selected_profile

    def infer_result(
        self,
        *,
        document_title: str | None,
        sections: list[DocumentSection],
        section_elements_by_id: dict[str, list[CanonicalElement]],
    ) -> StructuralProfileInference:
        features = self.feature_extractor.build(
            document_title=document_title,
            sections=sections,
            section_elements_by_id=section_elements_by_id,
        )
        scores = self.score_aggregator.aggregate(features)
        selected_profile, confidence, final_scores = self.decision_policy.decide(
            scores=scores,
            features=features,
        )
        return StructuralProfileInference(
            selected_profile=selected_profile,
            confidence=confidence,
            scores=final_scores.scores,
            reasons=final_scores.reasons,
            features=features,
        )
