from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics import (
    ChunkingProfileStatistics,
)


def score_datasheet_profile(
    scores: dict[ChunkingProfile, float],
    reasons: dict[ChunkingProfile, list[str]],
    statistics: ChunkingProfileStatistics,
) -> None:
    if statistics.datasheet_marker_hits > 0:
        scores[ChunkingProfile.DATASHEET] += min(
            5.0,
            statistics.datasheet_marker_hits * 1.7,
        )
        reasons[ChunkingProfile.DATASHEET].append(
            f"Datasheet/specification markers found in title/sections ({statistics.datasheet_marker_hits} hits)."
        )

    if statistics.table_ratio >= 0.22:
        scores[ChunkingProfile.DATASHEET] += 2.5
        reasons[ChunkingProfile.DATASHEET].append(
            f"Tables are dominant (ratio {statistics.table_ratio:.2f})."
        )
    elif statistics.table_ratio >= 0.12:
        scores[ChunkingProfile.DATASHEET] += 1.2
        reasons[ChunkingProfile.DATASHEET].append(
            f"Tables are a notable structural signal (ratio {statistics.table_ratio:.2f})."
        )

    if statistics.short_text_ratio >= 0.35:
        scores[ChunkingProfile.DATASHEET] += 1.2
        reasons[ChunkingProfile.DATASHEET].append(
            f"Text blocks are short and spec-like (short-text ratio {statistics.short_text_ratio:.2f})."
        )

    if 0 < statistics.avg_text_tokens <= 14:
        scores[ChunkingProfile.DATASHEET] += 0.9
        reasons[ChunkingProfile.DATASHEET].append(
            f"Average text blocks are concise ({statistics.avg_text_tokens:.1f} tokens)."
        )

    if statistics.max_section_depth <= 2 and statistics.root_section_count >= statistics.nested_section_count:
        scores[ChunkingProfile.DATASHEET] += 0.6
        reasons[ChunkingProfile.DATASHEET].append(
            "Section structure is shallow, which fits specification-style documents."
        )

    if statistics.manual_marker_hits >= 3 or statistics.procedure_like_section_count >= 2:
        scores[ChunkingProfile.DATASHEET] -= 2.0
        reasons[ChunkingProfile.DATASHEET].append(
            "Strong manual/procedure signals reduce datasheet confidence."
        )

    if statistics.long_text_ratio >= 0.35:
        scores[ChunkingProfile.DATASHEET] -= 1.0
        reasons[ChunkingProfile.DATASHEET].append(
            "Long narrative text is less typical for a datasheet."
        )
