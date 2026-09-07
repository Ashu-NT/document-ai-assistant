from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_document_features import (
    StructuralDocumentFeatures,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.scoring.profile_scores import (
    ProfileScores,
)


class StructuralProfileDecisionPolicy:
    """Turns a ProfileScores (MANUAL/DATASHEET/DRAWING/REPORT/CERTIFICATE
    only) into a final decision: scores ChunkingProfile.DEFAULT from how
    decisive the other profiles' scores are, picks the winner, and computes
    a confidence value."""

    def decide(
        self,
        *,
        scores: ProfileScores,
        features: StructuralDocumentFeatures,
    ) -> tuple[ChunkingProfile, float, ProfileScores]:
        default_score, default_reasons = self._score_default(scores.scores, features)
        final_scores = scores.with_profile(
            ChunkingProfile.DEFAULT,
            score=round(max(0.0, default_score), 3),
            reasons=default_reasons,
        )

        selected_profile = self._select_profile(final_scores.scores)
        confidence = self._confidence(
            selected_profile=selected_profile,
            scores=final_scores.scores,
        )
        return selected_profile, confidence, final_scores

    @staticmethod
    def _score_default(
        scores: dict[ChunkingProfile, float],
        features: StructuralDocumentFeatures,
    ) -> tuple[float, list[str]]:
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

        default_score = 0.0
        reasons: list[str] = []

        if top_score < 3.0:
            default_score += 3.0
            reasons.append(
                "Structural signals are weak across all profile candidates."
            )
        elif top_score < 4.5:
            default_score += 1.3
            reasons.append("No structural profile is strongly dominant.")

        if gap < 0.75:
            default_score += 2.5
            reasons.append(
                "Top structural profile scores are too close, so the document is ambiguous."
            )
        elif gap < 1.5:
            default_score += 0.9
            reasons.append("Top structural profile scores are relatively close.")

        if features.total_structural_evidence_hits == 0:
            default_score += 0.8
            reasons.append(
                "No strong profile markers were found in the title or section headings."
            )

        if features.element_count < 4:
            default_score += 0.6
            reasons.append(
                "Very small documents do not provide enough structural evidence."
            )

        return default_score, reasons

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
