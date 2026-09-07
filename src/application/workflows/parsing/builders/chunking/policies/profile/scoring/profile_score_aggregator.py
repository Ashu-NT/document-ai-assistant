from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_document_features import (
    StructuralDocumentFeatures,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.scoring.certificate_scorer import (
    CertificateScorer,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.scoring.datasheet_scorer import (
    DatasheetScorer,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.scoring.drawing_scorer import (
    DrawingScorer,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.scoring.manual_scorer import (
    ManualScorer,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.scoring.profile_evidence_scorer import (
    ProfileEvidenceScorer,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.scoring.profile_scores import (
    ProfileScores,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.scoring.report_scorer import (
    ReportScorer,
)


class ProfileScoreAggregator:
    """Runs every ProfileEvidenceScorer over one StructuralDocumentFeatures
    and merges their results into a ProfileScores. ChunkingProfile.DEFAULT
    is left at 0.0/[] here -- StructuralProfileDecisionPolicy fills it in
    from how decisive these scores turn out to be."""

    def __init__(self, scorers: list[ProfileEvidenceScorer] | None = None) -> None:
        self.scorers: list[ProfileEvidenceScorer] = scorers or [
            ManualScorer(),
            DatasheetScorer(),
            DrawingScorer(),
            ReportScorer(),
            CertificateScorer(),
        ]

    def aggregate(self, features: StructuralDocumentFeatures) -> ProfileScores:
        scores: dict[ChunkingProfile, float] = {profile: 0.0 for profile in ChunkingProfile}
        reasons: dict[ChunkingProfile, list[str]] = {profile: [] for profile in ChunkingProfile}

        for scorer in self.scorers:
            score_delta, score_reasons = scorer.score(features)
            scores[scorer.profile] += score_delta
            reasons[scorer.profile].extend(score_reasons)

        rounded_scores = {
            profile: round(max(0.0, score), 3)
            for profile, score in scores.items()
        }
        return ProfileScores(scores=rounded_scores, reasons=reasons)
