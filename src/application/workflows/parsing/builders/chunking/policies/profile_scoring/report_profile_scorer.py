from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics import (
    ChunkingProfileStatistics,
)


def score_report_profile(
    scores: dict[ChunkingProfile, float],
    reasons: dict[ChunkingProfile, list[str]],
    statistics: ChunkingProfileStatistics,
) -> None:
    if statistics.report_marker_hits > 0:
        scores[ChunkingProfile.REPORT] += min(
            5.0,
            statistics.report_marker_hits * 1.7,
        )
        reasons[ChunkingProfile.REPORT].append(
            f"Report markers found in title/sections ({statistics.report_marker_hits} hits)."
        )

    if statistics.long_text_ratio >= 0.35:
        scores[ChunkingProfile.REPORT] += 1.8
        reasons[ChunkingProfile.REPORT].append(
            f"Narrative text blocks are common (long-text ratio {statistics.long_text_ratio:.2f})."
        )

    if statistics.avg_text_tokens >= 18:
        scores[ChunkingProfile.REPORT] += 1.1
        reasons[ChunkingProfile.REPORT].append(
            f"Average text blocks are long ({statistics.avg_text_tokens:.1f} tokens)."
        )

    if statistics.section_count >= 4:
        scores[ChunkingProfile.REPORT] += 0.7
        reasons[ChunkingProfile.REPORT].append(
            f"Document has multiple narrative sections ({statistics.section_count})."
        )

    if statistics.nested_section_ratio >= 0.20:
        scores[ChunkingProfile.REPORT] += 0.6
        reasons[ChunkingProfile.REPORT].append(
            f"Section hierarchy supports report-style structure (nested ratio {statistics.nested_section_ratio:.2f})."
        )

    if statistics.manual_marker_hits >= 3 and statistics.procedure_like_section_count >= 2:
        scores[ChunkingProfile.REPORT] -= 1.4
        reasons[ChunkingProfile.REPORT].append(
            "Strong procedure/task structure reduces report confidence."
        )
