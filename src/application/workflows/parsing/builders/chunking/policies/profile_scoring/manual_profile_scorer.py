from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics import (
    ChunkingProfileStatistics,
)


def score_manual_profile(
    scores: dict[ChunkingProfile, float],
    reasons: dict[ChunkingProfile, list[str]],
    statistics: ChunkingProfileStatistics,
) -> None:
    if statistics.manual_marker_hits > 0:
        scores[ChunkingProfile.MANUAL] += min(
            5.0,
            statistics.manual_marker_hits * 1.6,
        )
        reasons[ChunkingProfile.MANUAL].append(
            f"Manual markers found in title/sections ({statistics.manual_marker_hits} hits)."
        )

    if statistics.procedure_like_section_count > 0:
        scores[ChunkingProfile.MANUAL] += min(
            2.0,
            0.8 + (statistics.procedure_like_section_count * 0.4),
        )
        reasons[ChunkingProfile.MANUAL].append(
            f"Procedure-like section titles are present ({statistics.procedure_like_section_count})."
        )

    if statistics.list_ratio >= 0.12:
        scores[ChunkingProfile.MANUAL] += 1.3
        reasons[ChunkingProfile.MANUAL].append(
            f"List items are common (ratio {statistics.list_ratio:.2f})."
        )

    if (
        statistics.long_text_ratio >= 0.25
        and (
            statistics.manual_marker_hits > 0
            or statistics.procedure_like_section_count > 0
        )
    ):
        scores[ChunkingProfile.MANUAL] += 1.2
        reasons[ChunkingProfile.MANUAL].append(
            f"Narrative text blocks are present (long-text ratio {statistics.long_text_ratio:.2f})."
        )

    if statistics.max_section_depth >= 3 or statistics.nested_section_ratio >= 0.35:
        scores[ChunkingProfile.MANUAL] += 0.8
        reasons[ChunkingProfile.MANUAL].append(
            f"Section hierarchy is task-oriented or nested (depth {statistics.max_section_depth})."
        )
