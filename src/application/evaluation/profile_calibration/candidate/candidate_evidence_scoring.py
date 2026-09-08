from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_evidence_matcher import (
    StructuralEvidenceSummary,
)

# Mirrors the term-catalog sizes in StructuralEvidenceMatcher's
# _DEFAULT_TERM_CATALOG. This is a calibration-only module (does not import
# or modify the production scorers' evidence term) -- if the real catalogs
# change size, these must be updated to match or the diversity_ratio below
# will silently drift from what the production term lists actually contain.
_CATALOG_SIZE: dict[ChunkingProfile, int] = {
    ChunkingProfile.MANUAL: 9,
    ChunkingProfile.DATASHEET: 10,
    ChunkingProfile.DRAWING: 5,
    ChunkingProfile.REPORT: 8,
    ChunkingProfile.CERTIFICATE: 6,
}

_COVERAGE_WEIGHT = 6.0
_DIVERSITY_WEIGHT = 3.0
_OCCURRENCE_FLOOR_CAP = 1.0
_OCCURRENCE_FLOOR_RATE = 0.15
_EVIDENCE_SCORE_CAP = 5.0


def candidate_evidence_score(
    profile: ChunkingProfile,
    summary: StructuralEvidenceSummary,
    section_count: int,
) -> float:
    """Ratio-based evidence score: rewards evidence that is proportionally
    widespread (matching_title_count / section_count) and diverse across
    the profile's own term catalog (distinct_term_count / catalog size),
    rather than a raw occurrence count that scales with document length
    alone and saturates its cap almost immediately on any real document
    (see project_structural_profile_calibration memory for the FWC12 and
    synthetic-length-dilution evidence this was validated against). A small
    bounded occurrence floor keeps tiny documents (near-zero section_count)
    from producing noisy, denominator-dominated ratios.
    """
    if summary.total_occurrences <= 0:
        return 0.0
    coverage_ratio = (
        summary.matching_title_count / section_count if section_count > 0 else 0.0
    )
    diversity_ratio = summary.distinct_term_count / _CATALOG_SIZE[profile]
    occurrence_floor = min(
        _OCCURRENCE_FLOOR_CAP, summary.total_occurrences * _OCCURRENCE_FLOOR_RATE
    )
    return min(
        _EVIDENCE_SCORE_CAP,
        coverage_ratio * _COVERAGE_WEIGHT
        + diversity_ratio * _DIVERSITY_WEIGHT
        + occurrence_floor,
    )
