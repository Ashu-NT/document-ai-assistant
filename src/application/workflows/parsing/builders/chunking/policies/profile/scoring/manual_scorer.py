from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_document_features import (
    StructuralDocumentFeatures,
)


class ManualScorer:
    profile = ChunkingProfile.MANUAL

    def score(self, features: StructuralDocumentFeatures) -> tuple[float, list[str]]:
        score = 0.0
        reasons: list[str] = []

        if features.manual_structural_evidence_hits > 0:
            score += min(5.0, features.manual_structural_evidence_hits * 1.6)
            reasons.append(
                f"Manual markers found in title/sections ({features.manual_structural_evidence_hits} hits)."
            )

        if features.procedure_like_section_count > 0:
            score += min(
                2.0,
                0.8 + (features.procedure_like_section_count * 0.4),
            )
            reasons.append(
                f"Procedure-like section titles are present ({features.procedure_like_section_count})."
            )

        if features.list_ratio >= 0.12:
            score += 1.3
            reasons.append(
                f"List items are common (ratio {features.list_ratio:.2f})."
            )

        if (
            features.long_text_ratio >= 0.25
            and (
                features.manual_structural_evidence_hits > 0
                or features.procedure_like_section_count > 0
            )
        ):
            score += 1.2
            reasons.append(
                f"Narrative text blocks are present (long-text ratio {features.long_text_ratio:.2f})."
            )

        if features.max_section_depth >= 3 or features.nested_section_ratio >= 0.35:
            score += 0.8
            reasons.append(
                f"Section hierarchy is task-oriented or nested (depth {features.max_section_depth})."
            )

        return score, reasons
