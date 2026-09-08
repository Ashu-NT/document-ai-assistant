from collections.abc import Callable
from dataclasses import replace

from src.application.evaluation.profile_calibration.candidate.candidate_evidence_scoring import (
    candidate_evidence_score,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_document_features import (
    StructuralDocumentFeatures,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_evidence_matcher import (
    StructuralEvidenceSummary,
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

EvidenceScoreFn = Callable[[ChunkingProfile, StructuralEvidenceSummary, int], float]


def real_evidence_contribution(
    scorer: ProfileEvidenceScorer,
    features: StructuralDocumentFeatures,
) -> float:
    """Derives exactly what the real scorer added for evidence by diffing
    its score against the same features with that profile's evidence
    zeroed out -- avoids hardcoding/duplicating the production
    occurrence-count formula (which could drift out of sync). Exposed at
    module level (not just as a CandidateScoreAggregator internal) so
    invariant tests can independently reconstruct "what production would
    have scored" without depending on aggregator internals."""
    with_evidence, _ = scorer.score(features)
    zeroed_evidence = {
        **features.evidence,
        scorer.profile: StructuralEvidenceSummary(),
    }
    without_evidence, _ = scorer.score(replace(features, evidence=zeroed_evidence))
    return with_evidence - without_evidence


class CandidateScoreAggregator:
    """Reruns the REAL, unmodified production scorers (ManualScorer,
    DatasheetScorer, ...) and algebraically swaps only their evidence term
    for the ratio-based candidate one -- every non-evidence signal (table
    ratio, list ratio, text density, cross-profile penalties, ...) comes
    from the exact same production code, called read-only. This is
    deliberately NOT a duplicated/forked copy of each scorer's full logic:
    duplicating would drift silently if a scorer's non-evidence branches
    ever change. Production scorer files are imported and called, never
    modified, by this module.
    """

    def __init__(
        self,
        scorers: list[ProfileEvidenceScorer] | None = None,
        *,
        evidence_score_fn: EvidenceScoreFn | None = None,
    ) -> None:
        self.scorers: list[ProfileEvidenceScorer] = scorers or [
            ManualScorer(),
            DatasheetScorer(),
            DrawingScorer(),
            ReportScorer(),
            CertificateScorer(),
        ]
        # Injectable so invariant tests can substitute a stub that returns
        # exactly the production evidence contribution, proving the
        # evidence-swap arithmetic itself is a no-op when new == old --
        # see test_candidate_score_aggregator_scorer_parity.py.
        self.evidence_score_fn: EvidenceScoreFn = (
            evidence_score_fn or candidate_evidence_score
        )

    def aggregate(self, features: StructuralDocumentFeatures) -> ProfileScores:
        scores: dict[ChunkingProfile, float] = {profile: 0.0 for profile in ChunkingProfile}
        reasons: dict[ChunkingProfile, list[str]] = {profile: [] for profile in ChunkingProfile}

        for scorer in self.scorers:
            real_score, real_reasons = scorer.score(features)
            old_evidence_contribution = real_evidence_contribution(scorer, features)
            new_evidence_contribution = self.evidence_score_fn(
                scorer.profile,
                features.evidence[scorer.profile],
                features.section_count,
            )
            candidate_score = (
                real_score - old_evidence_contribution + new_evidence_contribution
            )
            scores[scorer.profile] = round(max(0.0, candidate_score), 3)
            reasons[scorer.profile] = list(real_reasons) + [
                "[candidate] ratio-based evidence score "
                f"{new_evidence_contribution:.2f} "
                f"(production evidence score was {old_evidence_contribution:.2f})"
            ]

        return ProfileScores(scores=scores, reasons=reasons)
