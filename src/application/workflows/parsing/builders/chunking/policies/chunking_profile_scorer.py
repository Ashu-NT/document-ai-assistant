from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_inference import (
    ChunkingProfileInference,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile_statistics import (
    ChunkingProfileStatistics,
)
from src.application.workflows.parsing.builders.chunking.policies.profile_scoring import (
    score_certificate_profile,
    score_datasheet_profile,
    score_default_profile,
    score_drawing_profile,
    score_manual_profile,
    score_report_profile,
)


class ChunkingProfileScorer:
    def score(
        self,
        statistics: ChunkingProfileStatistics,
    ) -> ChunkingProfileInference:
        scores = {
            profile: 0.0
            for profile in ChunkingProfile
        }
        reasons = {
            profile: []
            for profile in ChunkingProfile
        }

        score_manual_profile(scores, reasons, statistics)
        score_datasheet_profile(scores, reasons, statistics)
        score_drawing_profile(scores, reasons, statistics)
        score_report_profile(scores, reasons, statistics)
        score_certificate_profile(scores, reasons, statistics)
        score_default_profile(scores, reasons, statistics)

        rounded_scores = {
            profile: round(max(0.0, score), 3)
            for profile, score in scores.items()
        }
        selected_profile = self._select_profile(rounded_scores)
        confidence = self._confidence(
            selected_profile=selected_profile,
            scores=rounded_scores,
        )
        return ChunkingProfileInference(
            selected_profile=selected_profile,
            confidence=confidence,
            scores=rounded_scores,
            reasons=reasons,
            statistics=statistics,
        )

    @staticmethod
    def _select_profile(
        scores: dict[ChunkingProfile, float],
    ) -> ChunkingProfile:
        ordered = sorted(
            scores.items(),
            key=lambda item: (
                item[1],
                item[0] == ChunkingProfile.DEFAULT,
            ),
            reverse=True,
        )
        return ordered[0][0]

    @staticmethod
    def _confidence(
        *,
        selected_profile: ChunkingProfile,
        scores: dict[ChunkingProfile, float],
    ) -> float:
        ordered_scores = sorted(scores.values(), reverse=True)
        top_score = ordered_scores[0] if ordered_scores else 0.0
        second_score = ordered_scores[1] if len(ordered_scores) > 1 else 0.0
        normalized_top = min(1.0, top_score / 8.0)
        gap_ratio = min(1.0, (top_score - second_score) / max(top_score, 1.0))
        confidence = 0.15 + (0.45 * normalized_top) + (0.40 * gap_ratio)

        if selected_profile == ChunkingProfile.DEFAULT:
            confidence = min(confidence, 0.6)

        return round(min(0.99, max(0.0, confidence)), 3)
