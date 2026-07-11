from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics import (
    ChunkingProfileStatistics,
)


def score_default_profile(
    scores: dict[ChunkingProfile, float],
    reasons: dict[ChunkingProfile, list[str]],
    statistics: ChunkingProfileStatistics,
) -> None:
    non_default_scores = sorted(
        (
            score
            for profile, score in scores.items()
            if profile != ChunkingProfile.DEFAULT
        ),
        reverse=True,
    )
    top_score = non_default_scores[0] if non_default_scores else 0.0
    second_score = non_default_scores[1] if len(non_default_scores) > 1 else 0.0
    gap = top_score - second_score

    if top_score < 3.0:
        scores[ChunkingProfile.DEFAULT] += 3.0
        reasons[ChunkingProfile.DEFAULT].append(
            "Structural signals are weak across all profile candidates."
        )
    elif top_score < 4.5:
        scores[ChunkingProfile.DEFAULT] += 1.3
        reasons[ChunkingProfile.DEFAULT].append(
            "No structural profile is strongly dominant."
        )

    if gap < 0.75:
        scores[ChunkingProfile.DEFAULT] += 2.5
        reasons[ChunkingProfile.DEFAULT].append(
            "Top structural profile scores are too close, so the document is ambiguous."
        )
    elif gap < 1.5:
        scores[ChunkingProfile.DEFAULT] += 0.9
        reasons[ChunkingProfile.DEFAULT].append(
            "Top structural profile scores are relatively close."
        )

    if statistics.total_marker_hits == 0:
        scores[ChunkingProfile.DEFAULT] += 0.8
        reasons[ChunkingProfile.DEFAULT].append(
            "No strong profile markers were found in the title or section headings."
        )

    if statistics.element_count < 4:
        scores[ChunkingProfile.DEFAULT] += 0.6
        reasons[ChunkingProfile.DEFAULT].append(
            "Very small documents do not provide enough structural evidence."
        )
