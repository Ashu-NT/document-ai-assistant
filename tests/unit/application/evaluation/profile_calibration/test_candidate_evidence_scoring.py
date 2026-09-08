from src.application.evaluation.profile_calibration.candidate.candidate_evidence_scoring import (
    candidate_evidence_score,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_evidence_matcher import (
    StructuralEvidenceSummary,
)


def test_zero_occurrences_scores_zero() -> None:
    summary = StructuralEvidenceSummary()

    score = candidate_evidence_score(ChunkingProfile.MANUAL, summary, section_count=50)

    assert score == 0.0


def test_same_absolute_hits_score_lower_when_diluted_across_more_sections() -> None:
    """The whole point of the ratio-based formula: raw occurrence count
    alone can't distinguish concentrated evidence from evidence diluted
    across a much larger document."""
    summary = StructuralEvidenceSummary(
        total_occurrences=8, distinct_term_count=3, matching_title_count=4,
        matched_terms=("maintenance", "procedure", "service"),
    )

    concentrated = candidate_evidence_score(
        ChunkingProfile.MANUAL, summary, section_count=10
    )
    diluted = candidate_evidence_score(
        ChunkingProfile.MANUAL, summary, section_count=400
    )

    assert concentrated > diluted


def test_score_is_capped_at_five() -> None:
    summary = StructuralEvidenceSummary(
        total_occurrences=100, distinct_term_count=9, matching_title_count=100,
        matched_terms=tuple(f"term{i}" for i in range(9)),
    )

    score = candidate_evidence_score(ChunkingProfile.MANUAL, summary, section_count=100)

    assert score == 5.0


def test_zero_section_count_does_not_raise() -> None:
    summary = StructuralEvidenceSummary(
        total_occurrences=1, distinct_term_count=1, matching_title_count=1,
        matched_terms=("maintenance",),
    )

    score = candidate_evidence_score(ChunkingProfile.MANUAL, summary, section_count=0)

    assert score >= 0.0
