from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_document_features import (
    StructuralDocumentFeatures,
)


class CertificateScorer:
    profile = ChunkingProfile.CERTIFICATE

    def score(self, features: StructuralDocumentFeatures) -> tuple[float, list[str]]:
        score = 0.0
        reasons: list[str] = []

        if features.certificate_structural_evidence_hits > 0:
            score += min(5.0, features.certificate_structural_evidence_hits * 1.8)
            reasons.append(
                f"Certificate markers found in title/sections ({features.certificate_structural_evidence_hits} hits)."
            )

        if features.table_ratio >= 0.15:
            score += 1.4
            reasons.append(
                f"Tables are present (ratio {features.table_ratio:.2f}), typical for certificate data."
            )

        if features.short_text_ratio >= 0.30:
            score += 0.9
            reasons.append(
                f"Short form-like text entries found (ratio {features.short_text_ratio:.2f})."
            )

        if features.max_section_depth <= 2 and features.section_count <= 8:
            score += 0.6
            reasons.append(
                "Compact, shallow structure is consistent with a certificate document."
            )

        if features.manual_structural_evidence_hits >= 3 or features.procedure_like_section_count >= 2:
            score -= 1.8
            reasons.append(
                "Strong manual/procedure signals reduce certificate confidence."
            )

        if features.long_text_ratio >= 0.35:
            score -= 1.2
            reasons.append(
                "Narrative text is uncharacteristic for a certificate document."
            )

        return score, reasons
