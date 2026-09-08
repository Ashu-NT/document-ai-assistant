from src.application.evaluation.profile_calibration.candidate.candidate_evidence_scoring import (
    candidate_evidence_score,
)
from src.application.evaluation.profile_calibration.candidate.candidate_score_aggregator import (
    CandidateScoreAggregator,
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
from src.application.workflows.parsing.builders.chunking.policies.profile.scoring.manual_scorer import (
    ManualScorer,
)


def _features_with_manual_evidence(
    total_occurrences: int, section_count: int
) -> StructuralDocumentFeatures:
    return StructuralDocumentFeatures(
        section_count=section_count,
        list_ratio=0.2,
        long_text_ratio=0.3,
        max_section_depth=3,
        procedure_like_section_count=2,
        evidence={
            profile: StructuralEvidenceSummary()
            for profile in ChunkingProfile
            if profile != ChunkingProfile.DEFAULT
        }
        | {
            ChunkingProfile.MANUAL: StructuralEvidenceSummary(
                total_occurrences=total_occurrences,
                distinct_term_count=3,
                matching_title_count=4,
                matched_terms=("maintenance", "procedure", "service"),
            )
        },
    )


def test_candidate_score_equals_real_score_when_evidence_is_zero() -> None:
    """When a profile has zero evidence, the algebraic evidence-swap should
    be a no-op: candidate score must equal the real scorer's score exactly,
    since both the old and new evidence contributions are zero."""
    features = _features_with_manual_evidence(total_occurrences=0, section_count=50)
    real_score, _ = ManualScorer().score(features)

    aggregator = CandidateScoreAggregator()
    scores = aggregator.aggregate(features)

    assert scores.score_for(ChunkingProfile.MANUAL) == round(max(0.0, real_score), 3)


def test_candidate_score_swaps_only_the_evidence_term() -> None:
    features = _features_with_manual_evidence(total_occurrences=8, section_count=20)
    real_score, _ = ManualScorer().score(features)
    zero_evidence_features = _features_with_manual_evidence(
        total_occurrences=0, section_count=20
    )
    real_score_without_evidence, _ = ManualScorer().score(zero_evidence_features)
    real_evidence_contribution = real_score - real_score_without_evidence
    new_evidence_contribution = candidate_evidence_score(
        ChunkingProfile.MANUAL,
        features.evidence[ChunkingProfile.MANUAL],
        features.section_count,
    )
    expected_candidate_score = round(
        max(0.0, real_score - real_evidence_contribution + new_evidence_contribution),
        3,
    )

    aggregator = CandidateScoreAggregator()
    scores = aggregator.aggregate(features)

    assert scores.score_for(ChunkingProfile.MANUAL) == expected_candidate_score


def test_candidate_scores_include_every_non_default_profile() -> None:
    features = _features_with_manual_evidence(total_occurrences=8, section_count=20)

    aggregator = CandidateScoreAggregator()
    scores = aggregator.aggregate(features)

    for profile in ChunkingProfile:
        if profile == ChunkingProfile.DEFAULT:
            assert scores.score_for(profile) == 0.0
        else:
            assert profile in scores.scores
