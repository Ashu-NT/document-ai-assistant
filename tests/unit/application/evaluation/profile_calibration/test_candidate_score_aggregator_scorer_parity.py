"""Invariant tests protecting the evidence-swap arithmetic in
CandidateScoreAggregator: for each of the 5 profile scorers, if the
candidate evidence function is made to return EXACTLY the same value as
production's own evidence contribution (derived independently via
real_evidence_contribution, not hardcoded), the aggregator's output must
equal the real scorer's output exactly.

This does not assert anything about the actual candidate_evidence_score
formula's numbers -- it protects the *substitution mechanism* itself, so it
stays correct even if a scorer's non-evidence branches change later or the
candidate formula's constants are retuned.
"""

import pytest

from src.application.evaluation.profile_calibration.candidate.candidate_score_aggregator import (
    CandidateScoreAggregator,
    real_evidence_contribution,
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
from src.application.workflows.parsing.builders.chunking.policies.profile.scoring.report_scorer import (
    ReportScorer,
)

_EMPTY_EVIDENCE = {
    profile: StructuralEvidenceSummary()
    for profile in ChunkingProfile
    if profile != ChunkingProfile.DEFAULT
}


def _features_for(profile: ChunkingProfile) -> StructuralDocumentFeatures:
    """One realistic, non-trivial feature set per profile -- non-zero
    evidence for the profile under test PLUS enough non-evidence signal to
    exercise that scorer's other branches (bonuses and cross-profile
    penalties alike), so the invariant is checked against real scorer
    behavior, not a degenerate all-zero case."""
    evidence = dict(_EMPTY_EVIDENCE)
    evidence[profile] = StructuralEvidenceSummary(
        total_occurrences=6,
        distinct_term_count=3,
        matching_title_count=5,
        matched_terms=("term_a", "term_b", "term_c"),
    )
    base = {
        ChunkingProfile.MANUAL: dict(
            procedure_like_section_count=4,
            list_ratio=0.2,
            long_text_ratio=0.3,
            max_section_depth=3,
            section_count=20,
        ),
        ChunkingProfile.DATASHEET: dict(
            table_ratio=0.25,
            short_text_ratio=0.4,
            avg_text_tokens=10.0,
            max_section_depth=2,
            root_section_count=5,
            nested_section_count=1,
            section_count=10,
        ),
        ChunkingProfile.DRAWING: dict(
            picture_ratio=0.3,
            caption_ratio=0.1,
            text_element_count=40,
            avg_text_tokens=6.0,
            long_text_ratio=0.05,
            section_count=15,
        ),
        ChunkingProfile.REPORT: dict(
            long_text_ratio=0.4,
            avg_text_tokens=20.0,
            section_count=8,
            nested_section_ratio=0.3,
        ),
        ChunkingProfile.CERTIFICATE: dict(
            table_ratio=0.2,
            short_text_ratio=0.35,
            max_section_depth=2,
            section_count=6,
        ),
    }[profile]
    return StructuralDocumentFeatures(evidence=evidence, **base)


@pytest.mark.parametrize(
    "scorer_cls, profile",
    [
        (ManualScorer, ChunkingProfile.MANUAL),
        (DatasheetScorer, ChunkingProfile.DATASHEET),
        (DrawingScorer, ChunkingProfile.DRAWING),
        (ReportScorer, ChunkingProfile.REPORT),
        (CertificateScorer, ChunkingProfile.CERTIFICATE),
    ],
)
def test_candidate_matches_production_exactly_when_evidence_functions_agree(
    scorer_cls, profile
) -> None:
    features = _features_for(profile)
    real_scorer = scorer_cls()
    real_score, _ = real_scorer.score(features)

    # A stub evidence function that always returns "whatever production's
    # own evidence contribution was" for the profile being scored --
    # derived fresh each call, never hardcoded to a specific number.
    def evidence_score_fn_matching_production(p, summary, section_count):
        return real_evidence_contribution(real_scorer, features)

    aggregator = CandidateScoreAggregator(
        scorers=[real_scorer],
        evidence_score_fn=evidence_score_fn_matching_production,
    )

    result = aggregator.aggregate(features)

    assert result.score_for(profile) == round(max(0.0, real_score), 3)
