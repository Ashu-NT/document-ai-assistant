from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics import (
    ChunkingProfileStatistics,
)


def score_certificate_profile(
    scores: dict[ChunkingProfile, float],
    reasons: dict[ChunkingProfile, list[str]],
    statistics: ChunkingProfileStatistics,
) -> None:
    if statistics.certificate_marker_hits > 0:
        scores[ChunkingProfile.CERTIFICATE] += min(
            5.0,
            statistics.certificate_marker_hits * 1.8,
        )
        reasons[ChunkingProfile.CERTIFICATE].append(
            f"Certificate markers found in title/sections ({statistics.certificate_marker_hits} hits)."
        )

    if statistics.table_ratio >= 0.15:
        scores[ChunkingProfile.CERTIFICATE] += 1.4
        reasons[ChunkingProfile.CERTIFICATE].append(
            f"Tables are present (ratio {statistics.table_ratio:.2f}), typical for certificate data."
        )

    if statistics.short_text_ratio >= 0.30:
        scores[ChunkingProfile.CERTIFICATE] += 0.9
        reasons[ChunkingProfile.CERTIFICATE].append(
            f"Short form-like text entries found (ratio {statistics.short_text_ratio:.2f})."
        )

    if statistics.max_section_depth <= 2 and statistics.section_count <= 8:
        scores[ChunkingProfile.CERTIFICATE] += 0.6
        reasons[ChunkingProfile.CERTIFICATE].append(
            "Compact, shallow structure is consistent with a certificate document."
        )

    if statistics.manual_marker_hits >= 3 or statistics.procedure_like_section_count >= 2:
        scores[ChunkingProfile.CERTIFICATE] -= 1.8
        reasons[ChunkingProfile.CERTIFICATE].append(
            "Strong manual/procedure signals reduce certificate confidence."
        )

    if statistics.long_text_ratio >= 0.35:
        scores[ChunkingProfile.CERTIFICATE] -= 1.2
        reasons[ChunkingProfile.CERTIFICATE].append(
            "Narrative text is uncharacteristic for a certificate document."
        )
