from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics import (
    ChunkingProfileStatistics,
)


def score_drawing_profile(
    scores: dict[ChunkingProfile, float],
    reasons: dict[ChunkingProfile, list[str]],
    statistics: ChunkingProfileStatistics,
) -> None:
    if statistics.drawing_marker_hits > 0:
        scores[ChunkingProfile.DRAWING] += min(
            5.0,
            statistics.drawing_marker_hits * 1.7,
        )
        reasons[ChunkingProfile.DRAWING].append(
            f"Drawing/schematic markers found in title/sections ({statistics.drawing_marker_hits} hits)."
        )

    if statistics.picture_ratio >= 0.22:
        scores[ChunkingProfile.DRAWING] += 2.6
        reasons[ChunkingProfile.DRAWING].append(
            f"Pictures are dominant (ratio {statistics.picture_ratio:.2f})."
        )
    elif statistics.picture_ratio >= 0.12:
        scores[ChunkingProfile.DRAWING] += 1.1
        reasons[ChunkingProfile.DRAWING].append(
            f"Pictures are a meaningful structural signal (ratio {statistics.picture_ratio:.2f})."
        )

    if statistics.caption_ratio >= 0.08:
        scores[ChunkingProfile.DRAWING] += 0.7
        reasons[ChunkingProfile.DRAWING].append(
            f"Caption density supports figure-driven content (ratio {statistics.caption_ratio:.2f})."
        )

    if statistics.text_element_count == 0 or statistics.avg_text_tokens <= 8:
        scores[ChunkingProfile.DRAWING] += 1.4
        reasons[ChunkingProfile.DRAWING].append(
            "Text density is very low, which fits drawing-like documents."
        )

    if statistics.long_text_ratio <= 0.10 and statistics.text_element_count > 0:
        scores[ChunkingProfile.DRAWING] += 1.0
        reasons[ChunkingProfile.DRAWING].append(
            f"Long narrative text is rare (long-text ratio {statistics.long_text_ratio:.2f})."
        )

    if statistics.avg_text_tokens >= 16 or statistics.long_text_ratio >= 0.25:
        scores[ChunkingProfile.DRAWING] -= 2.4
        reasons[ChunkingProfile.DRAWING].append(
            "Text-rich structure reduces drawing confidence."
        )

    if statistics.list_ratio >= 0.12:
        scores[ChunkingProfile.DRAWING] -= 1.2
        reasons[ChunkingProfile.DRAWING].append(
            "Frequent list items are atypical for drawing-centric documents."
        )
