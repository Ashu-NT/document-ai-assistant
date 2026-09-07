from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_document_features import (
    StructuralDocumentFeatures,
)


class ReportScorer:
    profile = ChunkingProfile.REPORT

    def score(self, features: StructuralDocumentFeatures) -> tuple[float, list[str]]:
        score = 0.0
        reasons: list[str] = []

        if features.report_structural_evidence_hits > 0:
            score += min(5.0, features.report_structural_evidence_hits * 1.7)
            reasons.append(
                f"Report markers found in title/sections ({features.report_structural_evidence_hits} hits)."
            )

        if features.long_text_ratio >= 0.35:
            score += 1.8
            reasons.append(
                f"Narrative text blocks are common (long-text ratio {features.long_text_ratio:.2f})."
            )

        if features.avg_text_tokens >= 18:
            score += 1.1
            reasons.append(
                f"Average text blocks are long ({features.avg_text_tokens:.1f} tokens)."
            )

        if features.section_count >= 4:
            score += 0.7
            reasons.append(
                f"Document has multiple narrative sections ({features.section_count})."
            )

        if features.nested_section_ratio >= 0.20:
            score += 0.6
            reasons.append(
                f"Section hierarchy supports report-style structure (nested ratio {features.nested_section_ratio:.2f})."
            )

        if features.manual_structural_evidence_hits >= 3 and features.procedure_like_section_count >= 2:
            score -= 1.4
            reasons.append(
                "Strong procedure/task structure reduces report confidence."
            )

        return score, reasons
