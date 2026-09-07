from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_document_features import (
    StructuralDocumentFeatures,
)


class DrawingScorer:
    profile = ChunkingProfile.DRAWING

    def score(self, features: StructuralDocumentFeatures) -> tuple[float, list[str]]:
        score = 0.0
        reasons: list[str] = []

        if features.drawing_structural_evidence_hits > 0:
            score += min(5.0, features.drawing_structural_evidence_hits * 1.7)
            reasons.append(
                f"Drawing/schematic markers found in title/sections ({features.drawing_structural_evidence_hits} hits)."
            )

        if features.picture_ratio >= 0.22:
            score += 2.6
            reasons.append(
                f"Pictures are dominant (ratio {features.picture_ratio:.2f})."
            )
        elif features.picture_ratio >= 0.12:
            score += 1.1
            reasons.append(
                f"Pictures are a meaningful structural signal (ratio {features.picture_ratio:.2f})."
            )

        if features.caption_ratio >= 0.08:
            score += 0.7
            reasons.append(
                f"Caption density supports figure-driven content (ratio {features.caption_ratio:.2f})."
            )

        if features.text_element_count == 0 or features.avg_text_tokens <= 8:
            score += 1.4
            reasons.append(
                "Text density is very low, which fits drawing-like documents."
            )

        if features.long_text_ratio <= 0.10 and features.text_element_count > 0:
            score += 1.0
            reasons.append(
                f"Long narrative text is rare (long-text ratio {features.long_text_ratio:.2f})."
            )

        if features.avg_text_tokens >= 16 or features.long_text_ratio >= 0.25:
            score -= 2.4
            reasons.append(
                "Text-rich structure reduces drawing confidence."
            )

        if features.list_ratio >= 0.12:
            score -= 1.2
            reasons.append(
                "Frequent list items are atypical for drawing-centric documents."
            )

        return score, reasons
